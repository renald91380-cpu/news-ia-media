"""Transforme un carrousel News IA (images 1080x1350) en Reel vertical 1080x1920.

Usage : python3 reel.py <dossier_images> <sortie.mp4>
Chaque page reste ~3 s (couverture 3,5 s), avec un fondu de 0,4 s entre les pages.
Le fond reprend l'image floutée et assombrie, l'image nette est centrée.
Une piste audio silencieuse est ajoutée (certaines plateformes l'exigent).
"""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageFilter, ImageEnhance

W, H = 1080, 1920
COVER, PAGE, FADE = 3.5, 3.0, 0.4


def frame(src, dst):
    im = Image.open(src).convert("RGB")
    bg = im.resize((W, int(im.height * W / im.width * 1.45)))
    bg = bg.crop((0, (bg.height - H) // 2, W, (bg.height - H) // 2 + H)) if bg.height >= H else bg.resize((W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.35)
    fg = im.resize((W, int(im.height * W / im.width)))
    bg.paste(fg, (0, (H - fg.height) // 2))
    bg.save(dst)


def main(src_dir, out):
    pages = sorted(glob.glob(os.path.join(src_dir, "[0-9][0-9].png")))
    if len(pages) < 2:
        raise SystemExit("Il faut au moins 2 images NN.png")
    tmp = tempfile.mkdtemp()
    frames = []
    for i, p in enumerate(pages):
        f = os.path.join(tmp, f"f{i:02d}.png"); frame(p, f); frames.append(f)
    durs = [COVER] + [PAGE] * (len(frames) - 1)
    durs[-1] += 0.5  # laisser le temps de lire la dernière page
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for f, d in zip(frames, durs):
        cmd += ["-loop", "1", "-t", f"{d + FADE:.2f}", "-i", f]
    total = sum(durs) + FADE
    cmd += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
    parts, last, offset = [], "[0:v]", 0.0
    for i in range(1, len(frames)):
        offset += durs[i - 1]
        tag = f"[v{i}]"
        parts.append(f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={offset:.2f}{tag}")
        last = tag
    parts.append(f"{last}format=yuv420p,fps=30[vout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", f"{len(frames)}:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "96k",
            "-movflags", "+faststart", "-shortest", out]
    subprocess.run(cmd, check=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
