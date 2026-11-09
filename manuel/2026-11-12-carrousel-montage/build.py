"""Carrousel « 5 IA pour monter plus vite » : HTML -> 9 images 1080x1350 (Playwright)."""
import os
from playwright.sync_api import sync_playwright

ACC = "#ff6384"
HANDLE = "@renald91150"
N = 9

TOOLS = [
    ("MONTER", "Edits, gratuit sur Mac",
     "Montage multipiste et export 4K sans filigrane. Il faut un Mac M1 minimum, et tes Reels partent en direct.",
     "Instagram"),
    ("TRIER", "Resolve 21.1.2 trouve le bon plan",
     "La recherche IA va jusqu’à 14 fois plus vite sur Mac M6, selon Blackmagic. Mise à jour gratuite.",
     "Blackmagic Design"),
    ("NETTOYER", "Topaz Wonder 4 répare tes images",
     "Agrandissement, débruitage, netteté et visages restaurés en un seul passage.",
     "Topaz Labs"),
    ("SONORISER", "ElevenLabs SFX v3",
     "Tu décris le bruitage en une phrase, l’IA le génère pour ton montage.",
     "ElevenLabs"),
    ("MUSIQUE", "Suno depuis ton chatbot",
     "Une chanson créée dans Claude, ChatGPT ou Gemini, à partir d’un mémo vocal. En bêta.",
     "Suno"),
]

def frame(i, body, cls=""):
    num = f'<div class="num">{i}/{N}</div>'
    return f'''<section class="{cls}">
  <div class="glow1"></div><div class="glow2"></div>
  <div class="top"><div class="pill">NEWS IA</div>{num}</div>
  <div class="body">{body}</div>
  <div class="foot"><span>{HANDLE}</span><span>{"Fais défiler  →" if i < N else "Spécial montage"}</span></div>
</section>'''

slides = []
slides.append(frame(1, '''
  <div class="kick">SPÉCIAL MONTAGE</div>
  <h1 class="cover"><b>5</b> IA pour monter plus vite</h1>
  <p class="promise">Sorties ces 15 derniers jours. Garde-les sous la main.</p>''', "c"))
slides.append(frame(2, '''
  <div class="kick">POURQUOI</div>
  <h2>Trier, monter, sonoriser, nettoyer.</h2>
  <p class="lead">Ce sont les 4 étapes qui te prennent le plus de temps.</p>
  <p class="lead acc">Chacune a reçu une mise à jour IA ce mois-ci.</p>'''))
for k, (tag, title, text, src) in enumerate(TOOLS, 3):
    slides.append(frame(k, f'''
  <div class="kick">{tag}</div>
  <h2>{title}</h2>
  <p class="lead">{text}</p>
  <p class="src">Source : {src}</p>'''))
rows = "".join(f'<li><span class="k">{t[0].capitalize()}</span><span>{t[1].split(",")[0] if t[0]=="MONTER" else t[1]}</span></li>'
               for t in [TOOLS[1], TOOLS[0], TOOLS[2], TOOLS[3], TOOLS[4]])
slides.append(frame(8, f'''
  <div class="kick">À RETENIR</div>
  <ul class="recap">
    <li><span class="k">Trier</span><span>Resolve 21.1.2</span></li>
    <li><span class="k">Monter</span><span>Edits sur Mac</span></li>
    <li><span class="k">Nettoyer</span><span>Topaz Wonder 4</span></li>
    <li><span class="k">Sonoriser</span><span>ElevenLabs SFX v3</span></li>
    <li><span class="k">Musique</span><span>Suno MCP (bêta)</span></li>
  </ul>'''))
slides.append(frame(9, '''
  <div class="kick">ET MAINTENANT</div>
  <h2 class="cta">Enregistre ce post pour ton prochain montage.</h2>
  <p class="lead">Une actu IA pour créateurs, chaque matin à 10h.</p>'''))

CSS = f'''
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#000; }}
section {{ width:1080px; height:1350px; position:relative; overflow:hidden;
  background:linear-gradient(180deg,#090c16 0%,#0f1124 100%); color:#f5f7fc;
  font-family:"Inter", sans-serif; padding:120px 120px 0 120px; }}
.glow1 {{ position:absolute; right:-300px; top:-380px; width:900px; height:820px; border-radius:50%;
  background:{ACC}; opacity:.42; filter:blur(170px); }}
.glow2 {{ position:absolute; left:-380px; bottom:-420px; width:760px; height:680px; border-radius:50%;
  background:{ACC}; opacity:.2; filter:blur(170px); }}
.top {{ position:relative; display:flex; justify-content:space-between; align-items:center; }}
.pill {{ background:{ACC}; color:#090c16; font-family:"Inter Display"; font-weight:800; font-size:40px;
  letter-spacing:6px; padding:18px 38px 16px; border-radius:60px; }}
.num {{ font-family:"Inter Display"; font-weight:800; font-size:40px; color:#d6dce9; }}
.body {{ position:absolute; left:120px; right:120px; top:290px; bottom:230px; display:flex;
  flex-direction:column; justify-content:center; }}
.kick {{ color:{ACC}; font-family:"Inter Display"; font-weight:800; font-size:36px; letter-spacing:8px; margin-bottom:34px; }}
h1.cover {{ font-family:"Inter Display"; font-weight:800; font-size:132px; line-height:1.0; letter-spacing:-2px; }}
h1.cover b {{ color:{ACC}; font-size:168px; }}
.promise {{ margin-top:48px; font-size:44px; line-height:1.35; color:#d6dce9; }}
h2 {{ font-family:"Inter Display"; font-weight:800; font-size:84px; line-height:1.06; letter-spacing:-1px; }}
h2.cta {{ color:{ACC}; font-size:88px; }}
.lead {{ margin-top:44px; font-size:46px; line-height:1.4; color:#d6dce9; }}
.lead.acc {{ color:{ACC}; margin-top:28px; font-weight:600; }}
.src {{ margin-top:48px; font-size:32px; color:#8a94aa; }}
ul.recap {{ list-style:none; }}
ul.recap li {{ display:flex; gap:32px; align-items:baseline; padding:26px 0; border-bottom:2px solid #2a3150; }}
ul.recap li:last-child {{ border-bottom:none; }}
ul.recap .k {{ color:{ACC}; font-family:"Inter Display"; font-weight:800; font-size:44px; width:280px; flex:none; }}
ul.recap span:last-child {{ font-family:"Inter Display"; font-weight:800; font-size:52px; }}
.foot {{ position:absolute; left:120px; right:120px; bottom:110px; display:flex; justify-content:space-between;
  border-top:2px solid #343c52; padding-top:26px; font-size:32px; color:#8a94aa; }}
'''
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(slides)}</body></html>'
open("carrousel.html", "w").write(html)

os.makedirs("png", exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
    pg.goto("file://" + os.path.abspath("carrousel.html"))
    pg.wait_for_timeout(300)
    for i, s in enumerate(pg.query_selector_all("section"), 1):
        s.screenshot(path=f"png/{i:02d}.png")
    b.close()
print("ok")
