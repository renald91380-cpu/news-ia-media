"""Transforme un carrousel News IA en Reel vertical 1080x1920 (H.264 + AAC).

Usage : python3 reel.py <dossier_carrousel> <sortie.mp4> [--court]
  --court : version courte (~15 s) : accroche, titre + 1re phrase de chaque actu, récap.

Mode plein écran (par défaut si <dossier>/reel/manifest.json existe, produit par carrousel.py) :
  - ouverture « punch » : l'accroche arrive en zoom rapide avec un impact sonore ;
  - le texte apparaît bloc par bloc en glissant vers le haut ;
  - léger zoom avant continu, transition « push » rapide entre les pages avec whoosh ;
  - barre de progression segmentée (une case par page) ;
  - musique originale 118 BPM générée par le script (pas de droits à gérer).
Mode secours (anciens dossiers sans manifest) : pages 1080x1350 centrées sur fond flouté.
"""
import glob, json, math, os, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
STAGE_FADE, PAGE_FADE, ZOOM = 0.25, 0.3, 0.045


# ---------- musique originale (synthèse, 118 BPM, plus percutante) + effets ----------
BPM = 118

def music(path, dur, hits=(), sr=44100):
    """Musique originale : kick à chaque temps, clap sur 2 et 4, basse, nappe « pompée ».
    hits = instants (s) des changements de page : un « whoosh » y est ajouté.
    Un impact grave marque le tout début (accroche)."""
    n = int(dur * sr); t = np.arange(n) / sr
    beat = 60 / BPM; bar = 4 * beat
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    rng = np.random.default_rng(7)
    pad = np.zeros(n); bass = np.zeros(n); kick = np.zeros(n); clap = np.zeros(n); hat = np.zeros(n)
    for b in range(int(dur / bar) + 1):
        s, e = int(b * bar * sr), min(n, int((b + 1) * bar * sr))
        if s >= n: break
        tt = t[s:e] - b * bar; ch = chords[b % 4]
        for m in ch:
            f = hz(m + 12)
            pad[s:e] += (np.sin(2*np.pi*f*tt) + 0.35*np.sin(2*np.pi*2*f*tt + 0.5)) / len(ch)
        for k in range(8):                                   # basse en croches
            bs = int((b * bar + k * beat / 2) * sr); be = min(n, bs + int(beat / 2 * sr))
            if bs >= n: break
            u = t[bs:be] - (b * bar + k * beat / 2)
            note = ch[0] - 12 + (12 if k % 4 == 3 else 0)
            bass[bs:be] += np.tanh(2.2 * np.sin(2*np.pi*hz(note)*u)) * np.exp(-u * 5)
    pump = np.ones(n)                                         # effet « sidechain »
    for k in range(int(dur / beat) + 1):
        s = int(k * beat * sr)
        if s >= n: break
        L = min(n - s, int(0.3 * sr)); u = np.arange(L) / sr
        kick[s:s+L] += np.sin(2*np.pi*(48 + 110*np.exp(-u*35))*u) * np.exp(-u*10)
        P = min(n - s, int(beat * sr)); up = np.arange(P) / sr
        pump[s:s+P] = 0.35 + 0.65 * np.minimum(1, up / (beat * 0.6))
        if k % 2 == 1:                                        # clap sur 2 et 4
            CL = min(n - s, int(0.18 * sr))
            nz = rng.standard_normal(CL); nz = nz - np.convolve(nz, np.ones(6) / 6, "same")
            clap[s:s+CL] += nz * np.exp(-np.arange(CL) / sr * 22)
        for h in (0.25, 0.5, 0.75):                           # charleston en doubles
            hs = int((k + h) * beat * sr); HL = min(n - hs, int(0.04 * sr))
            if HL > 0:
                hat[hs:hs+HL] += np.diff(rng.standard_normal(HL + 1)) * np.exp(-np.arange(HL) / sr * 90) * (1 if h == 0.5 else 0.5)
    fx = np.zeros(n)
    L = min(n, int(0.9 * sr)); u = np.arange(L) / sr           # impact d'ouverture
    fx[:L] += np.sin(2*np.pi*(38 + 140*np.exp(-u*12))*u) * np.exp(-u*4) * 1.3
    fx[:L] += rng.standard_normal(L) * np.exp(-u*14) * 0.35
    for h in hits:                                            # whoosh centré sur chaque transition
        c = int(h * sr); W2 = int(0.45 * sr); s = max(0, c - W2); e = min(n, c + int(0.15 * sr))
        if e <= s: continue
        nz = rng.standard_normal(e - s); u = np.arange(e - s) / sr
        k = int(sr * 0.002); nz = np.convolve(nz, np.ones(k) / k, "same")
        env = np.where(np.arange(s, e) < c, ((np.arange(s, e) - s) / max(1, c - s)) ** 2.5,
                       np.exp(-(np.arange(s, e) - c) / sr * 30))
        fx[s:e] += nz * env * 5.0
    mix = 0.22*pad*pump + 0.30*bass*pump + 0.55*kick + 0.16*clap + 0.05*hat + 0.35*fx
    mix *= np.minimum(1, (dur - t) / 1.0)
    mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.6) * 0.62
    st = np.stack([mix, np.roll(mix, int(0.010 * sr)) * 0.95], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def encode(frames, total, out, hits=()):
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "music.wav")
    music(wav, total + 0.1, hits)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(np.ascontiguousarray(f, dtype=np.uint8).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg a échoué")
    print(out, "(%.1f s)" % total)


# ---------- mode plein écran ----------
ease_out = lambda x: 1 - (1 - min(1, max(0, x))) ** 3
ease_io = lambda x: (lambda x: 4*x**3 if x < 0.5 else 1 - (-2*x + 2)**3 / 2)(min(1, max(0, x)))
REVEAL, SLIDE, PUSH, SLAM = 0.24, 46, 0.28, 0.4   # durées (s) et glissement (px)


def zoomed(img, z):
    """Zoom centré sub-pixel (pas de saccade)."""
    if not isinstance(img, Image.Image): img = Image.fromarray(img)
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    return np.asarray(img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)))


def load_pages(rd, man, court):
    """Liste de pages [(images numpy, durées, masques)] ; version courte si court=True."""
    spec = man["pages"]
    if court:   # accroche complète, puis titre + 1re phrase de chaque actu, puis récap
        sel = [[(spec[0][-1]["file"], 2.4)]]
        for pg in spec[1:-1]:
            sel.append([(pg[0]["file"], 0.75), (pg[min(1, len(pg) - 1)]["file"], 2.9)])
        sel.append([(spec[-1][-1]["file"], 2.6)])
    else:
        sel = [[(s["file"], s["dur"]) for s in pg] for pg in spec]
    pages = []
    for pg in sel:
        ims = [np.asarray(Image.open(os.path.join(rd, f)).convert("RGB")).astype(np.float32) for f, _ in pg]
        masks = [None]
        for a, b in zip(ims, ims[1:]):   # zone du nouveau texte, légèrement élargie
            m = Image.fromarray(((np.abs(b - a).max(2) > 10) * 255).astype(np.uint8))
            m = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
            masks.append(np.asarray(m, dtype=np.float32)[..., None] / 255)
        pages.append((ims, [d for _, d in pg], masks))
    return pages


def fullscreen(src, out, court=False):
    rd = os.path.join(src, "reel")
    man = json.load(open(os.path.join(rd, "manifest.json")))
    acc = tuple(man["accent"])
    pages = load_pages(rd, man, court)
    plen = [sum(d) for _, d, _ in pages]
    total = sum(plen)
    starts = [sum(plen[:i]) for i in range(len(plen))]

    def page_frame(i, t):
        ims, durs, masks = pages[i]
        acc_t, k = 0.0, 0
        while k < len(durs) - 1 and t >= acc_t + durs[k]:
            acc_t += durs[k]; k += 1
        if k > 0 and t - acc_t < REVEAL:   # le nouveau texte glisse vers le haut en apparaissant
            x = ease_out((t - acc_t) / REVEAL); dy = int(round(SLIDE * (1 - x)))
            m = np.roll(masks[k], dy, 0) * x; new = np.roll(ims[k], dy, 0)
            im = ims[k - 1] * (1 - m) + new * m
        else:
            im = ims[k]
        z = 1 + ZOOM * min(1, t / plen[i])
        if i == 0 and t < SLAM:            # « punch » d'ouverture : l'accroche claque à l'écran
            z += 0.14 * (1 - ease_out(t / SLAM))
        return zoomed(np.clip(im, 0, 255).astype(np.uint8), z)

    def bar(fr, tg):   # barre de progression segmentée (une case par page), plus visible
        y0, y1, gap = 14, 24, 10
        sw = (W - 2 * 40 - gap * (len(pages) - 1)) / len(pages)
        for i in range(len(pages)):
            x0 = int(40 + i * (sw + gap)); x1 = int(40 + i * (sw + gap) + sw)
            fr[y0:y1, x0:x1] = fr[y0:y1, x0:x1] * 0.45 + 255 * 0.25
            p = min(1, max(0, (tg - starts[i]) / plen[i]))
            if p > 0:
                fr[y0:y1, x0:x0 + max(1, int((x1 - x0) * p))] = acc
        return fr

    def frames():
        for i in range(len(pages)):
            for f in range(int(round(plen[i] * FPS))):
                t = f / FPS
                fr = page_frame(i, t)
                if i + 1 < len(pages) and t > plen[i] - PUSH:   # transition « push » vers la gauche
                    x = ease_io((t - (plen[i] - PUSH)) / PUSH); off = int(W * x)
                    nxt = page_frame(i + 1, 0.0)
                    fr = np.concatenate([fr[:, off:], nxt[:, :off]], 1) if off else fr
                yield bar(fr.copy(), starts[i] + t)
    hits = [s for s in starts[1:]]
    encode(frames(), total, out, hits)


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
                    a = (t - (d - PAGE_FADE)) / PAGE_FADE
                    z = (z * (1 - a) + np.asarray(ims[i + 1]) * a).astype(np.uint8)
                yield z
    encode(frames(), sum(durs), out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    court = "--court" in sys.argv
    src, out = args[0], args[1]
    if os.path.exists(os.path.join(src, "reel", "manifest.json")):
        fullscreen(src, out, court)
    else:
        legacy(src, out)
