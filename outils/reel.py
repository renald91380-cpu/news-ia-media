"""Transforme un carrousel News IA en Reel vertical 1080x1920 (H.264 + AAC).

Usage : python3 reel.py <dossier_carrousel> <sortie.mp4>

Mode plein écran (par défaut si <dossier>/reel/manifest.json existe, produit par carrousel.py) :
  - images 1080x1920 plein cadre, le texte apparaît bloc par bloc (fondu 0,25 s) ;
  - léger zoom avant continu sur chaque page (mouvement dès la 1re image) ;
  - fondu de 0,3 s entre les pages, barre de progression fine en haut ;
  - musique originale générée par le script (pas de droits à gérer).
Mode secours (anciens dossiers sans manifest) : pages 1080x1350 centrées sur fond flouté.
"""
import glob, json, math, os, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
STAGE_FADE, PAGE_FADE, ZOOM = 0.25, 0.3, 0.045


# ---------- musique originale (synthèse simple, 100 BPM) ----------
def music(path, dur, sr=44100):
    n = int(dur * sr); t = np.arange(n) / sr
    beat = 60 / 100; bar = 4 * beat
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    pad = np.zeros(n); bass = np.zeros(n)
    for b in range(int(dur / bar) + 1):
        s, e = int(b * bar * sr), min(n, int((b + 1) * bar * sr))
        if s >= n: break
        tt = t[s:e] - b * bar
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.4)
        ch = chords[b % 4]
        for m in ch:
            f = hz(m + 12)
            pad[s:e] += env * (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt + 0.5)) / len(ch)
        for k in range(4):
            bs = int((b * bar + k * beat) * sr); be = min(n, bs + int(beat * sr))
            if bs >= n: break
            u = t[bs:be] - (b * bar + k * beat)
            bass[bs:be] += np.sin(2*np.pi*hz(ch[0] - 12)*u) * np.exp(-u * 3)
    kick = np.zeros(n); hat = np.zeros(n); rng = np.random.default_rng(7)
    for k in range(int(dur / beat) + 1):
        s = int(k * beat * sr)
        if s >= n: break
        L = min(n - s, int(0.35 * sr)); u = np.arange(L) / sr
        kick[s:s+L] += np.sin(2*np.pi*(45 + 90*np.exp(-u*30))*u) * np.exp(-u*9)
        hs = int((k + 0.5) * beat * sr); HL = min(n - hs, int(0.05 * sr))
        if HL > 0:
            noise = np.diff(rng.standard_normal(HL + 1))
            hat[hs:hs+HL] += noise * np.exp(-np.arange(HL) / sr * 80)
    mix = 0.30*pad + 0.32*bass + 0.45*kick + 0.04*hat
    mix *= np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 1.2)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.5
    st = np.stack([mix, np.roll(mix, int(0.012 * sr)) * 0.95], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def encode(frames, total, out):
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "music.wav")
    music(wav, total + 0.1)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg a échoué")
    print(out)


# ---------- mode plein écran ----------
def zoomed(img, z):
    """Zoom centré sub-pixel (pas de saccade)."""
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def fullscreen(src, out):
    rd = os.path.join(src, "reel")
    man = json.load(open(os.path.join(rd, "manifest.json")))
    acc = tuple(man["accent"])
    pages = []
    for stages in man["pages"]:
        ims = [Image.open(os.path.join(rd, s["file"])).convert("RGB") for s in stages]
        pages.append((ims, [s["dur"] for s in stages]))
    total = sum(sum(d) for _, d in pages)

    def page_frame(ims, durs, t):
        """Image de la page à l'instant t (depuis le début de la page)."""
        acc_t, k = 0.0, 0
        while k < len(durs) - 1 and t >= acc_t + durs[k]:
            acc_t += durs[k]; k += 1
        im = ims[k]
        if k > 0 and t - acc_t < STAGE_FADE:
            im = Image.blend(ims[k - 1], ims[k], (t - acc_t) / STAGE_FADE)
        pd = sum(durs)
        return zoomed(im, 1 + ZOOM * min(1, t / pd))

    def frames():
        start = 0.0
        for i, (ims, durs) in enumerate(pages):
            pd = sum(durs)
            for f in range(int(round(pd * FPS))):
                t = f / FPS
                im = page_frame(ims, durs, t)
                if i + 1 < len(pages) and t > pd - PAGE_FADE:
                    nxt = page_frame(*pages[i + 1], 0.0)
                    im = Image.blend(im, nxt, (t - (pd - PAGE_FADE)) / PAGE_FADE)
                d = ImageDraw.Draw(im)   # barre de progression
                x = int(W * min(1, (start + t) / total))
                d.rectangle((0, 0, W, 7), fill=(30, 36, 54)); d.rectangle((0, 0, x, 7), fill=acc)
                yield im
            start += pd
    encode(frames(), total, out)


# ---------- mode secours (ancien format) ----------
def legacy(src, out, COVER=3.5, PAGE=3.0):
    pages = sorted(glob.glob(os.path.join(src, "[0-9][0-9].png")))
    if len(pages) < 2:
        raise SystemExit("Il faut au moins 2 images NN.png")
    def frame(p):
        im = Image.open(p).convert("RGB")
        bg = im.resize((W, int(im.height * W / im.width * 1.45)))
        bg = bg.crop((0, (bg.height - H) // 2, W, (bg.height - H) // 2 + H)) if bg.height >= H else bg.resize((W, H))
        bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.35)
        fg = im.resize((W, int(im.height * W / im.width)))
        bg.paste(fg, (0, (H - fg.height) // 2)); return bg
    ims = [frame(p) for p in pages]
    durs = [COVER] + [PAGE] * (len(ims) - 1); durs[-1] += 0.5
    def frames():
        for i, (im, d) in enumerate(zip(ims, durs)):
            for f in range(int(d * FPS)):
                t = f / FPS; z = zoomed(im, 1 + ZOOM * t / d)
                if i + 1 < len(ims) and t > d - PAGE_FADE:
                    z = Image.blend(z, ims[i + 1], (t - (d - PAGE_FADE)) / PAGE_FADE)
                yield z
    encode(frames(), sum(durs), out)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    if os.path.exists(os.path.join(src, "reel", "manifest.json")):
        fullscreen(src, out)
    else:
        legacy(src, out)
