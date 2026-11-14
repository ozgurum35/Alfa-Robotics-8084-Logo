# Interactive logo picker: one self-contained HTML page next to the logo family. Three clicks (which logo, which
# background, where it is used) and the matching files are listed. Links are relative, so the page works offline
# inside the unzipped package and on any web host. usage: python secici.py
import json, os
import guncel_logo as g

VER, ROOT = g.VER, g.AILE
OUT = ROOT + "ALFA 8084 - Logo Secici.html"

LOGOS = [  # id, folder, title, hint, variants (id -> folder variant)
    ("amblem", "Amblem", "Amblem", "Ana logo. Kararsızsanız bunu seçin.",
     {"acik": "Renkli", "koyu": "Koyu zemin", "tek-l": "Tek renk lacivert", "tek-b": "Tek renk beyaz"}),
    ("yatay", "Yatay Logo", "Yatay Logo", "Geniş ve alçak yerler: site başlığı, e-posta imzası, pankart.",
     {"acik": "Renkli", "koyu": "Koyu zemin", "tek-l": "Tek renk lacivert", "tek-b": "Tek renk beyaz"}),
    ("yazi", "Yazi Logo", "Yazı Logo", "Kalkanın sığmadığı dar yerler.",
     {"acik": "Renkli", "koyu": "Tek renk beyaz", "tek-l": "Tek renk lacivert", "tek-b": "Tek renk beyaz"}),
]
GROUNDS = [  # id, title, hint, dark preview?
    ("acik", "Açık zemin", "Beyaz kâğıt, açık renk kumaş, açık renkli sayfa.", False),
    ("koyu", "Koyu zemin", "Lacivert, siyah, koyu fotoğraf.", True),
    ("tek-l", "Tek renk, açık zemine", "Tek mürekkeple baskı, damga, nakış, kesim. Logo lacivert.", False),
    ("tek-b", "Tek renk, koyu zemine", "Koyu kumaşa ya da cama tek renk. Logo beyaz.", True),
]
USES = [  # id, title, hint, files: (suffix, label, note)
    ("ekran", "Ekranda", "Telefon, sunum, sosyal medya, web sitesi.",
     [(" 1024px.png", "Resim, orta boy", "Sunum, Word, Canva, web (1024 piksel)"),
      (" 2048px.png", "Resim, büyük boy", "Sosyal medya gönderisi, video (2048 piksel)"),
      (" 4096px.png", "Resim, en büyük boy", "Banner, kapak görseli (4096 piksel)"),
      (" 512px.png", "Resim, küçük boy", "E-posta imzası, küçük simge (512 piksel)")]),
    ("baski", "Baskıda", "Matbaa, forma, tişört, çıkartma, antetli kâğıt.",
     [(" - Baski CMYK.pdf", "Baskı dosyası", "Matbaaya ve tekstil baskıcısına bunu gönderin")]),
    ("kesim", "Kesim, nakış, tasarım", "Lazer, folyo kesim, nakışçı, tasarımcı.",
     [(".svg", "Çizgi dosyası (SVG)", "Lazer kesim, folyo kesim, CNC, web sitesi"),
      (".ai", "Kaynak dosya (AI)", "Nakışçıya ve tasarımcıya; Adobe Illustrator ile açılır"),
      (".pdf", "PDF (ekran renkleri)", "Dijital belge, ofis yazıcısı")]),
]
SHAPES = [("", "Zeminsiz", "Arkası saydam; kendi zemininize koyarsınız."), (" Kare", "Kare içinde", "Dolu kare zemin."),
          (" Daire", "Daire içinde", "Dolu daire zemin; çıkartma, rozet, yuvarlak alan.")]


def path(folder, variant, suffix):
    return f"{folder}/{variant}/ALFA 8084 - {folder} {VER} - {variant}{suffix}"


# every file the page can offer must exist
missing = [path(f + sh, v, suf) for _, f, _, _, vs in LOGOS for v in set(vs.values()) for sh, _, _ in SHAPES
           for _, _, _, files in USES for suf, _, _ in files if not os.path.exists(ROOT + path(f + sh, v, suf))]
assert not missing, missing[:5]
profiles = [f"Profil/ALFA 8084 - Profil {c} {s}px.png" for c in ("beyaz", "lacivert") for s in (1080, 4096)]
assert all(os.path.exists(ROOT + p) for p in profiles)

DATA = dict(ver=VER, logos=[dict(id=i, folder=f, title=t, hint=h, variants=v) for i, f, t, h, v in LOGOS],
            grounds=[dict(id=i, title=t, hint=h, dark=d) for i, t, h, d in GROUNDS],
            uses=[dict(id=i, title=t, hint=h, files=[dict(suffix=s, label=l, note=n) for s, l, n in fs]) for i, t, h, fs in USES],
            shapes=[dict(suffix=s, title=t, hint=h) for s, t, h in SHAPES])

HTML = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ALFA Robotics 8084 – Logo Seçici</title>
<style>
:root { --navy: #003A6F; --sky: #63C4F2; --ice: #D0E9E8; --ink: #1d2733; --mut: #5b6775; --line: #d5dce4; --bg: #f3f6f9; --card: #ffffff; --link: #0a5fa0; }
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.5 "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif; color: var(--ink); background: var(--bg); }
header { background: var(--navy); color: #fff; padding: 18px 16px; border-bottom: 4px solid var(--sky); }
header .in, main { max-width: 980px; margin: 0 auto; }
header h1 { margin: 0; font-size: 1.5rem; }
header p { margin: 4px 0 0; color: #cfe9f8; }
main { padding: 16px; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; margin-bottom: 14px; }
section[aria-disabled="true"] { opacity: .45; }
h2 { margin: 0 0 10px; font-size: 1.15rem; color: var(--navy); display: flex; align-items: center; gap: 10px; }
.no { flex: none; width: 30px; height: 30px; border-radius: 50%; background: var(--navy); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 1rem; }
.opts { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }
button.opt { font: inherit; text-align: left; color: inherit; background: #fff; border: 2px solid var(--line); border-radius: 10px; padding: 10px; cursor: pointer; min-height: 44px; }
button.opt:hover { border-color: var(--sky); }
button.opt:focus-visible, a:focus-visible, button.reset:focus-visible { outline: 3px solid #f2a900; outline-offset: 2px; }
button.opt[aria-pressed="true"] { border-color: var(--navy); background: #eaf5fc; box-shadow: inset 0 0 0 1px var(--navy); }
button.opt:disabled { cursor: not-allowed; }
button.opt .pic { display: block; height: 110px; border-radius: 6px; margin-bottom: 8px; background: #fff center / contain no-repeat; border: 1px solid var(--line); }
button.opt .pic.dark { background-color: var(--navy); border-color: var(--navy); }
button.opt b { display: block; }
button.opt span.h { display: block; color: var(--mut); font-size: .9rem; }
#result .top { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; }
#preview { flex: none; width: 220px; height: 220px; border-radius: 10px; border: 1px solid var(--line); background: #fff center / 86% no-repeat; }
#preview.dark { background-color: var(--navy); }
#result .txt { flex: 1 1 260px; }
#picked { font-weight: 600; color: var(--navy); margin: 0 0 6px; }
ul.files { list-style: none; margin: 10px 0 0; padding: 0; }
ul.files li { border-top: 1px solid var(--line); padding: 10px 0; display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center; justify-content: space-between; }
ul.files .n { color: var(--mut); font-size: .92rem; display: block; }
a.dl { flex: none; display: inline-block; background: var(--navy); color: #fff; text-decoration: none; font-weight: 600; padding: 10px 16px; border-radius: 8px; min-height: 44px; }
a.dl:hover { background: #0a5fa0; }
a.plain { color: var(--link); font-weight: 600; }
button.reset { font: inherit; background: none; border: 1px solid var(--line); border-radius: 8px; padding: 8px 14px; cursor: pointer; color: var(--navy); min-height: 44px; }
.shape { margin-top: 12px; }
.shape .opts { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
footer { max-width: 980px; margin: 0 auto; padding: 0 16px 24px; color: var(--mut); font-size: .9rem; }
.empty { color: var(--mut); margin: 0; }
@media (prefers-reduced-motion: no-preference) { button.opt, a.dl { transition: border-color .15s, background-color .15s; } }
</style>
</head>
<body>
<header><div class="in">
<h1>ALFA Robotics 8084 – Logo Seçici</h1>
<p>Üç soruyu sırayla yanıtlayın; size uygun dosyalar altta çıkar.</p>
</div></header>
<main>
<section id="s1"><h2><span class="no">1</span>Hangi logo?</h2><div class="opts" id="o1"></div></section>
<section id="s2" aria-disabled="true"><h2><span class="no">2</span>Zemin ne renk?</h2><div class="opts" id="o2"></div></section>
<section id="s3" aria-disabled="true"><h2><span class="no">3</span>Nerede kullanılacak?</h2><div class="opts" id="o3"></div></section>
<section id="result" aria-live="polite"><h2><span class="no">✓</span>Dosyalarınız</h2>
<p class="empty" id="empty">Yukarıdaki üç soruyu yanıtlayınca dosyalar burada görünür.</p>
<div id="out" hidden>
  <div class="top"><div id="preview" role="img" aria-label="Seçilen logonun önizlemesi"></div>
  <div class="txt"><p id="picked"></p>
    <div class="shape"><b>Zemin şekli</b><div class="opts" id="o4"></div></div>
  </div></div>
  <ul class="files" id="files"></ul>
  <p><button class="reset" id="reset" type="button">Baştan başla</button></p>
</div></section>
<section><h2><span class="no">★</span>Sık arananlar</h2>
<p style="margin:0">Profil fotoğrafı (Instagram, WhatsApp, YouTube):
<a class="plain" href="__P0__" download>Beyaz zeminli</a> · <a class="plain" href="__P2__" download>Lacivert zeminli</a> ·
daha büyük: <a class="plain" href="__P1__" download>Beyaz 4096</a> · <a class="plain" href="__P3__" download>Lacivert 4096</a></p>
<p style="margin:8px 0 0">Ayrıntılı kurallar, renk kodları ve yapılmaması gerekenler: <a class="plain" href="ALFA%208084%20-%20Logo%20Kullanim%20Kilavuzu.pdf">Logo Kullanım Kılavuzu (PDF)</a></p>
</section>
</main>
<footer>ALFA Robotics 8084 · Logo __VER__ · Bu sayfa, logo klasörünün içinde durduğu sürece internetsiz de çalışır.</footer>
<script>
const D = __DATA__;
const st = { logo: null, ground: null, use: null, shape: "" };
const $ = id => document.getElementById(id);
const enc = p => p.split("/").map(encodeURIComponent).join("/");
const file = (folder, variant, suffix) => enc(`${folder}/${variant}/ALFA 8084 - ${folder} ${D.ver} - ${variant}${suffix}`);
function opt(parent, title, hint, pressed, onClick, pic, dark, disabled) {
  const b = document.createElement("button"); b.type = "button"; b.className = "opt"; b.setAttribute("aria-pressed", pressed); b.disabled = !!disabled;
  if (pic) { const s = document.createElement("span"); s.className = "pic" + (dark ? " dark" : ""); s.style.backgroundImage = `url("${pic}")`; b.appendChild(s); }
  const t = document.createElement("b"); t.textContent = title; b.appendChild(t);
  const h = document.createElement("span"); h.className = "h"; h.textContent = hint; b.appendChild(h);
  b.addEventListener("click", onClick); parent.appendChild(b);
}
function render() {
  const L = D.logos.find(l => l.id === st.logo), G = D.grounds.find(g => g.id === st.ground), U = D.uses.find(u => u.id === st.use);
  $("o1").replaceChildren(); $("o2").replaceChildren(); $("o3").replaceChildren(); $("o4").replaceChildren();
  D.logos.forEach(l => opt($("o1"), l.title, l.hint, st.logo === l.id, () => { st.logo = l.id; render(); focusStep(2); }, file(l.folder, "Renkli", " 512px.png")));
  const base = L || D.logos[0];
  D.grounds.forEach(g => opt($("o2"), g.title, g.hint, st.ground === g.id, () => { st.ground = g.id; render(); focusStep(3); },
    file(base.folder, base.variants[g.id], " 512px.png"), g.dark, !L));
  D.uses.forEach(u => opt($("o3"), u.title, u.hint, st.use === u.id, () => { st.use = u.id; render(); $("result").scrollIntoView({ behavior: "smooth", block: "start" }); }, null, false, !(L && G)));
  $("s2").setAttribute("aria-disabled", !L); $("s3").setAttribute("aria-disabled", !(L && G));
  const done = L && G && U; $("out").hidden = !done; $("empty").hidden = !!done;
  if (!done) return;
  const variant = L.variants[G.id], folder = L.folder + st.shape;
  D.shapes.forEach(s => opt($("o4"), s.title, s.hint, st.shape === s.suffix, () => { st.shape = s.suffix; render(); }));
  const pv = $("preview"); pv.style.backgroundImage = `url("${file(folder, variant, " 1024px.png")}")`;
  pv.className = (G.dark && !st.shape) ? "dark" : ""; pv.style.backgroundSize = st.shape ? "100%" : "86%";
  const sh = D.shapes.find(s => s.suffix === st.shape);
  $("picked").textContent = `${L.title} · ${variant} · ${sh.title} · ${U.title}`;
  $("files").replaceChildren();
  U.files.forEach(f => {
    const li = document.createElement("li"), d = document.createElement("div"), b = document.createElement("b"), n = document.createElement("span"), a = document.createElement("a");
    b.textContent = f.label; n.className = "n"; n.textContent = f.note; d.append(b, n);
    a.className = "dl"; a.href = file(folder, variant, f.suffix); a.setAttribute("download", ""); a.textContent = "İndir";
    a.setAttribute("aria-label", `${f.label} dosyasını indir`); li.append(d, a); $("files").appendChild(li);
  });
}
function focusStep(n) { const b = document.querySelector(`#o${n} button:not(:disabled)`); if (b) { $("s" + n).scrollIntoView({ behavior: "smooth", block: "nearest" }); b.focus({ preventScroll: true }); } }
$("reset").addEventListener("click", () => { st.logo = st.ground = st.use = null; st.shape = ""; render(); window.scrollTo({ top: 0, behavior: "smooth" }); });
render();
</script>
</body>
</html>
"""
from urllib.parse import quote
html = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)).replace("__VER__", VER)
for i, p in enumerate(profiles):
    html = html.replace(f"__P{i}__", quote(p))
open(OUT, "w", encoding="utf-8", newline="\n").write(html)
print(OUT, len(html) // 1024, "KB")
