from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import os, datetime

# ====== CONTENU DU JOUR (seule partie à modifier) ======
DATE = "Lundi 5 octobre"
ACCROCHE = "Google, OpenAI et un robot : 3 actus IA à connaître"
ACCROCHE_EN = "Google, OpenAI and a robot: 3 AI news to know"  # traduction affichée sous l'accroche ("" pour aucune)
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
TOP, BOT, SCALE = 0, 0, 1.0   # marges de sécurité et échelle (modifiées pour la version Reel 9:16)

def font(bold, size):
    size = int(round(size * SCALE))
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
    ph = int(92 * SCALE)
    d.rounded_rectangle((M, M + TOP, M + bw + 76, M + TOP + ph), radius=ph // 2, fill=ACC)
    spaced(d, M + 38, M + TOP + int(20 * SCALE), "NEWS IA", f, DARK, 6)
    return img, d

def footer(d, left, right):
    f = font(False, 30)
    y = H - BOT - 146
    d.line((M, y, W - M, y), fill=(52, 60, 82), width=2)
    d.text((M, y + 24), fix(left), font=f, fill=MUTED)
    d.text((W - M - d.textlength(right, font=f), y + 24), right, font=f, fill=MUTED)

def block(d, parts, upto=None):
    """parts = liste de (lignes, police, couleur, interligne, espace_apres, puce).
    upto : ne dessine que les `upto` premiers éléments (même mise en page)."""
    top, bottom = M + TOP + int(132 * SCALE), H - BOT - 186
    h = sum(len(l) * lh + gap for l, f, c, lh, gap, b in parts) - parts[-1][4]
    assert h <= bottom - top, f"Texte trop long ({h}px pour {bottom-top}px) : raccourcir"
    y = top + (bottom - top - h) // 2
    for k, (lines, f, col, lh, gap, bullet) in enumerate(parts):
        draw = upto is None or k < upto
        if bullet and draw:
            o = int(17 * SCALE); s = int(20 * SCALE)
            d.rounded_rectangle((M, y + o, M + s, y + o + s), radius=5, fill=ACC)
        for ln in lines:
            assert d.textlength(ln, font=f) <= W - 2*M, ln
            if draw:
                d.text((M + (int(54 * SCALE) if bullet else 0), y), ln, font=f, fill=col)
            y += lh
        y += gap

def sc(v):
    return int(round(v * SCALE))

def pages_spec():
    """Renvoie la liste des pages : (dessin_du_fond, parts, footer, étapes de révélation)."""
    specs = []
    mw = W - 2*M
    # --- couverture
    def cover_bg(d):
        fd = font(False, 40); d.text((W - M - d.textlength(DATE, font=fd), M + TOP + sc(24)), DATE, font=fd, fill=SOFT)
    img, d = page()
    EN = globals().get("ACCROCHE_EN", "").strip()
    ft = font(True, 104); lines = wrap(d, ACCROCHE, ft, mw)
    if len(lines) > (4 if EN else 5): ft = font(True, 88); lines = wrap(d, ACCROCHE, ft, mw)
    cover = [(lines, ft, WHITE, int(ft.size*1.08), 0, False)]
    if EN:
        fe = font(False, 52)
        cover[0] = cover[0][:4] + (sc(48), False)
        cover.append((wrap(d, "EN · " + EN, fe, mw), fe, ACC, sc(66), 0, False))
    specs.append((cover_bg, cover, ("L’actu IA en 1 minute", "Fais défiler  →"),
                  [1, 2] if EN else [1]))
    # --- actus
    for i, n in enumerate(NEWS, 1):
        num = f"{i}/{len(NEWS)}"
        def bg(d, num=num):
            fn = font(True, 40); d.text((W - M - d.textlength(num, font=fn), M + TOP + sc(24)), num, font=fn, fill=SOFT)
        ftag, ft, fb = font(True, 34), font(True, 84), font(False, 44)
        tl = wrap(d, n["titre"], ft, mw)
        if len(tl) > 3: ft = font(True, 72); tl = wrap(d, n["titre"], ft, mw)
        parts = [([" ".join(n["tag"].upper())], ftag, ACC, sc(34), sc(28), False),
                 (tl, ft, WHITE, int(ft.size*1.08), sc(60), False)]
        parts += [(wrap(d, p, fb, mw - sc(54)), fb, SOFT, sc(62), sc(34), True) for p in n["points"]]
        specs.append((bg, parts, ("Source : " + n["source"], "→"), list(range(2, len(parts) + 1))))
    # --- récap + appel à l'action
    fh, fl, fc = font(True, 34), font(True, 50), font(True, 62)
    parts = [([" ".join("À RETENIR")], fh, ACC, sc(34), sc(40), False)]
    parts += [(wrap(d, n["titre"], fl, mw - sc(54)), fl, WHITE, sc(60), sc(26), True) for n in NEWS]
    parts[-1] = parts[-1][:4] + (sc(80), True)
    parts += [(wrap(d, "Enregistre ce post pour suivre l'actu IA chaque matin.", fc, mw), fc, ACC, sc(70), 0, False)]
    specs.append((lambda d: None, parts, ("Abonne-toi pour la suite", "#NewsIA"), [len(parts) - 1, len(parts)]))
    return specs

def render(spec, upto=None):
    bg, parts, foot, _ = spec
    img, d = page(); bg(d); block(d, parts, upto); footer(d, *foot)
    return img

# --- 1) carrousel 1080 x 1350 (images fixes, solution de repli)
os.makedirs(OUT, exist_ok=True)
for k, spec in enumerate(pages_spec(), 1):
    p = os.path.join(OUT, f"{k:02d}.png"); render(spec).save(p, optimize=True); print(p)

# --- 2) étapes plein écran 1080 x 1920 pour le Reel (texte révélé progressivement)
# Zones de sécurité : interface Instagram/TikTok en haut (~200 px) et en bas (~380 px).
import json
H, TOP, BOT, SCALE = 1920, 150, 300, 1.18
RD = os.path.join(OUT, "reel"); os.makedirs(RD, exist_ok=True)
manifest = []
for k, spec in enumerate(pages_spec(), 1):
    stages, prev_words = [], 0
    for s, upto in enumerate(spec[3], 1):
        p = os.path.join(RD, f"{k:02d}_{s}.png"); render(spec, upto).save(p)
        words = sum(len(" ".join(l).split()) for l, *_ in spec[1][:upto])
        new = words - prev_words; prev_words = words
        dur = 1.4 if (k == 1 and s == 1) else min(2.6, max(1.0, 0.4 + 0.13 * new))
        stages.append({"file": os.path.basename(p), "dur": round(dur, 2)})
    if k == len(NEWS) + 2: stages[-1]["dur"] += 0.8   # laisser lire l'appel à l'action
    manifest.append(stages)
json.dump({"accent": list(ACC), "pages": manifest}, open(os.path.join(RD, "manifest.json"), "w"), indent=1)
print(RD, "(%d pages, %.1f s)" % (len(manifest), sum(s["dur"] for p in manifest for s in p)))
