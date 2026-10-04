from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import os, datetime

# ====== CONTENU DU JOUR (seule partie à modifier) ======
DATE = "Lundi 5 octobre"
ACCROCHE = "Google, OpenAI et un robot : 3 actus IA à connaître"
NEWS = [
    dict(tag="GOOGLE", titre="Gemini 4 Argon débarque",
         points=["Le nouveau modèle de Google est d'abord réservé aux experts en cybersécurité.",
                 "Il sait repérer et corriger des failles dans les logiciels."],
         source="Google, 9to5Google"),
    dict(tag="OPENAI", titre="GPT-6.1 Sol : cinq fois moins cher",
         points=["Selon OpenAI, il approche les performances de son modèle haut de gamme.",
                 "Pour les développeurs, il coûte un cinquième du prix."],
         source="OpenAI, The Next Web"),
    dict(tag="ROBOTIQUE", titre="Le robot Atlas change de mains",
         points=["Sa nouvelle main compte quatre doigts et 13 degrés de liberté.",
                 "Elle peut porter plus de 45 kg et manier des outils."],
         source="Boston Dynamics"),
]
OUT = "carrousel"
# =======================================================

W, H, M = 1080, 1350, 84
ACCENTS = [(86, 156, 255), (46, 211, 162), (255, 168, 60), (255, 99, 132),
           (180, 140, 255), (255, 214, 64), (64, 210, 235)]   # lundi -> dimanche
ACC = ACCENTS[datetime.date.today().weekday()]
WHITE, SOFT, MUTED, DARK = (245, 247, 252), (214, 220, 233), (138, 148, 170), (9, 12, 22)
FD = "/usr/share/fonts/opentype/inter/"
def font(bold, size):
    for p in ([FD + ("InterDisplay-ExtraBold.otf" if bold else "Inter-Regular.otf")] +
              ["/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf"]):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("Aucune police trouvée")

def fix(t):  # apostrophes typographiques + espaces insécables avant : ? ! »
    t = t.replace("'", "’")
    for c in ":?!»":
        t = t.replace(" " + c, chr(160) + c)
    return t.replace("« ", "«" + chr(160))

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in fix(text).split(" "):
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) <= maxw: cur = test
        else: lines.append(cur); cur = w
    return lines + [cur]

def spaced(d, x, y, text, f, fill, sp):
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + sp
    return x

def page():
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=(int(9 + 6*t), int(12 + 5*t), int(22 + 14*t)))
    glow = Image.new("RGB", (W, H)); g = ImageDraw.Draw(glow)
    g.ellipse((W-480, -300, W+360, 480), fill=tuple(int(c*0.55) for c in ACC))
    g.ellipse((-420, H-480, 320, H+200), fill=tuple(int(c*0.28) for c in ACC))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(210)))
    d = ImageDraw.Draw(img)
    f = font(True, 44); bw = sum(d.textlength(c, font=f) + 6 for c in "NEWS IA") - 6
    d.rounded_rectangle((M, M, M + bw + 76, M + 92), radius=46, fill=ACC)
    spaced(d, M + 38, M + 20, "NEWS IA", f, DARK, 6)
    return img, d

def footer(d, left, right):
    f = font(False, 30)
    d.line((M, H - 146, W - M, H - 146), fill=(52, 60, 82), width=2)
    d.text((M, H - 122), fix(left), font=f, fill=MUTED)
    d.text((W - M - d.textlength(right, font=f), H - 122), right, font=f, fill=MUTED)

def block(d, parts, top=M + 132, bottom=H - 186):
    """parts = liste de (lignes, police, couleur, interligne, espace_apres, puce)"""
    h = sum(len(l) * lh + gap for l, f, c, lh, gap, b in parts) - parts[-1][4]
    assert h <= bottom - top, f"Texte trop long ({h}px pour {bottom-top}px) : raccourcir"
    y = top + (bottom - top - h) // 2
    for lines, f, col, lh, gap, bullet in parts:
        if bullet:
            d.rounded_rectangle((M, y + 17, M + 20, y + 37), radius=5, fill=ACC)
        for ln in lines:
            assert d.textlength(ln, font=f) <= W - 2*M, ln
            d.text((M + (54 if bullet else 0), y), ln, font=f, fill=col); y += lh
        y += gap

def save(img, n):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{n:02d}.png"); img.save(p, optimize=True); print(p)

mw = W - 2*M
total = len(NEWS) + 2
# --- page 1 : couverture
img, d = page()
fd = font(False, 40); d.text((W - M - d.textlength(DATE, font=fd), M + 24), DATE, font=fd, fill=SOFT)
ft = font(True, 104); lines = wrap(d, ACCROCHE, ft, mw)
if len(lines) > 5: ft = font(True, 88); lines = wrap(d, ACCROCHE, ft, mw)
block(d, [(lines, ft, WHITE, int(ft.size*1.08), 0, False)])
footer(d, "L’actu IA en 1 minute", "Fais défiler  →")
save(img, 1)
# --- pages actus
for i, n in enumerate(NEWS, 1):
    img, d = page()
    fn = font(True, 40); num = f"{i}/{len(NEWS)}"
    d.text((W - M - d.textlength(num, font=fn), M + 24), num, font=fn, fill=SOFT)
    ftag, ft, fb = font(True, 34), font(True, 84), font(False, 44)
    tl = wrap(d, n["titre"], ft, mw)
    if len(tl) > 3: ft = font(True, 72); tl = wrap(d, n["titre"], ft, mw)
    parts = [([" ".join(n["tag"].upper())], ftag, ACC, 34, 28, False),
             (tl, ft, WHITE, int(ft.size*1.08), 60, False)]
    parts += [(wrap(d, p, fb, mw - 54), fb, SOFT, 62, 34, True) for p in n["points"]]
    block(d, parts)
    footer(d, "Source : " + n["source"], "→")
    save(img, i + 1)
# --- dernière page : récap + appel à l'action
img, d = page()
fh, fl, fc = font(True, 34), font(True, 50), font(True, 62)
parts = [([" ".join("À RETENIR")], fh, ACC, 34, 40, False)]
parts += [(wrap(d, n["titre"], fl, mw - 54), fl, WHITE, 60, 26, True) for n in NEWS]
parts[-1] = parts[-1][:4] + (80, True)
parts += [(wrap(d, "Enregistre ce post pour suivre l'actu IA chaque matin.", fc, mw), fc, ACC, 70, 0, False)]
block(d, parts)
footer(d, "Abonne-toi pour la suite", "#NewsIA")
save(img, total)
