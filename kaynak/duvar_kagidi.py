# ALFA Robotics 8084 phone wallpapers: 2160 x 4680 px (19.5:9, fits iPhone and Android), 10 designs.
# Vector art is written as SVG and rasterised with PyMuPDF; gradients, glows and text with numpy / PIL.
# Usage: python duvar_kagidi.py [design numbers ...]   (no argument = all), then a preview sheet is made.
# Windows desktop set (3840 x 2160): set ALFA_DESK=1 (same for duvar_kagidi2.py); output in 'Masaustu Duvar Kagitlari/'.
import math, os, sys
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DESK = os.environ.get("ALFA_DESK") == "1"   # Windows desktop: 3840 x 2160 (4K UHD, 16:9)
W, H = (3840, 2160) if DESK else (2160, 4680)
K = 0.78 if DESK else 1.0                  # scale of the central composition (logo, rings) on the desktop
NAVY, SKY, ICE, WHITE = (0, 58, 111), (99, 196, 242), (208, 233, 232), (255, 255, 255)
ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/"
EM = ROOT + "v10 surum ailesi/Amblem/Koyu zemin/ALFA 8084 - Amblem v10 - Koyu zemin.pdf"
OUT = ROOT + ("Masaustu Duvar Kagitlari/" if DESK else "Duvar Kagitlari/")
PREFIX = "ALFA 8084 - Masaustu " if DESK else "ALFA 8084 - Duvar Kagidi "
BAHN, MONO = "C:/Windows/Fonts/bahnschrift.ttf", "C:/Windows/Fonts/consola.ttf"
CX, CY = W / 2, round((0.48 if DESK else 0.535) * H)   # logo centre; phone: the lock-screen clock sits in ~6-24 % of the height
FOOT_Y = H - 170 if DESK else round(0.845 * H)          # above the taskbar / the lock-screen buttons and the home bar
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------- SVG layer ----------
def hx(c): return "#%02x%02x%02x" % tuple(int(v) for v in c)
def path(p, close=False): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p) + (" Z" if close else "")
def line(p, c, w, o=1.0, close=False):
    return (f'<path d="{path(p, close)}" fill="none" stroke="{hx(c)}" stroke-width="{w}" stroke-opacity="{o}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')
def shape(d, fill=None, fo=1.0, stroke=None, w=0, so=1.0, rule="nonzero"):
    f = f'fill="{hx(fill)}" fill-opacity="{fo}"' if fill else 'fill="none"'
    s = f' stroke="{hx(stroke)}" stroke-width="{w}" stroke-opacity="{so}" stroke-linejoin="round"' if stroke else ""
    return f'<path d="{d}" {f}{s} fill-rule="{rule}"/>'
def poly(p, **k): return shape(path(p, True), **k)
def circ_path(x, y, r):
    n = int(min(180, max(24, r / 2)))
    return path([(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n)) for i in range(n)], True)
def circle(x, y, r, **k): return shape(circ_path(x, y, r), **k)
def rot(p, a, c=(0, 0)):
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in p]
def kk(v): return v * K
def kp(x, y): return (CX + (x - CX) * K, CY + (y - CY) * K)
def kg(body, k=K, cx=CX, cy=CY):   # scale a group of SVG elements about the logo centre
    return body if k == 1 else [f'<g transform="translate({cx} {cy}) scale({k}) translate({-cx} {-cy})">'] + body + ["</g>"]
def svg(body):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{"".join(body)}</svg>'
    p = pymupdf.open(stream=s.encode(), filetype="svg")[0].get_pixmap(alpha=True)
    assert (p.width, p.height) == (W, H), (p.width, p.height)
    return Image.frombytes("RGBa", (W, H), p.samples).convert("RGBA")   # MuPDF alpha is premultiplied


# ---------- raster helpers ----------
def arr_img(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
def mix(c0, c1, t):
    t = np.clip(t, 0, 1)[..., None]
    return np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
def dist(cx=CX, cy=CY): return np.hypot(XX - cx, YY - cy)
def alpha_mul(layer, m):
    a = np.asarray(layer).copy()
    a[..., 3] = (a[..., 3] * np.clip(m, 0, 1)).astype(np.uint8)
    return Image.fromarray(a, "RGBA")
def clear_zone(r0, r1, cx=CX, cy=CY): return np.clip((dist(cx, cy) - kk(r0)) / (kk(r1) - kk(r0)), 0, 1)
def clock_dim(k=0.45):  # quieter art behind the lock-screen clock
    if DESK: return np.ones_like(YY)
    t = np.clip(1 - np.abs(YY / H - 0.145) / 0.13, 0, 1)
    return 1 - (1 - k) * np.clip(t * 1.6, 0, 1)
def scale_alpha(im, k):
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: min(255, int(v * k)))); return im
def glow(base, layer, r, k=1.0):
    base.alpha_composite(scale_alpha(layer.filter(ImageFilter.GaussianBlur(r)), k))
def add(base, layer, mask=None, glows=()):
    if mask is not None: layer = alpha_mul(layer, mask)
    for r, k in glows: glow(base, layer, r, k)
    base.alpha_composite(layer)


def logo(width):
    page = pymupdf.open(EM)[0]
    z = width * 1.35 / page.rect.width
    p = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True)
    im = Image.frombytes("RGBa", (p.width, p.height), p.samples).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def place_logo(base, width=1320, cy=CY, cx=CX, glow_c=SKY, glow_k=0.55, shadow_k=0.6, mass=False, k=K):
    L = logo(round(width * k))
    A = L.getchannel("A")
    if mass:   # centre the visual weight (alpha centroid), not the bounding box
        a = np.asarray(A, np.float32); ys, xs = np.mgrid[0:L.height, 0:L.width]
        ox, oy = (a * xs).sum() / a.sum(), (a * ys).sum() / a.sum()
    else: ox, oy = L.width / 2, L.height / 2
    x, y = round(cx - ox), round(cy - oy)
    for color, blur, k, dy in ((glow_c, 130, glow_k, 0), ((0, 0, 0), 40, shadow_k, 30)):
        if k <= 0: continue
        pad = blur * 3
        g = Image.new("RGBA", (L.width + 2 * pad, L.height + 2 * pad), color + (0,))
        sh = Image.new("RGBA", L.size, color + (255,)); sh.putalpha(A.point(lambda v: int(v * k)))
        g.paste(sh, (pad, pad + dy))
        base.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)), (x - pad, y - pad))
    base.alpha_composite(L, (x, y))
    return x, y, x + L.width, y + L.height


def font(size, var="Bold", mono=False):
    if mono: return ImageFont.truetype(MONO, size)
    f = ImageFont.truetype(BAHN, size); f.set_variation_by_name(var); return f


def text(base, s, x, y, size, color=ICE, a=1.0, var="Bold", track=0.0, anchor="m", mono=False, angle=0):
    """Draw tracked text centred (anchor m), left (l) or right (r) on (x, y); returns its width."""
    f = font(size, var, mono)
    ws = [f.getlength(ch) for ch in s]
    tw = sum(ws) + track * size * (len(s) - 1)
    im = Image.new("RGBA", (int(tw) + 4 * size, 3 * size), color + (0,))
    d = ImageDraw.Draw(im); cx = 2 * size
    for ch, w in zip(s, ws):
        d.text((cx, 1.5 * size), ch, font=f, fill=color + (int(255 * a),), anchor="lm"); cx += w + track * size
    if angle: im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    ox = {"m": tw / 2, "l": 0, "r": tw}[anchor] if not angle else None
    if angle: px, py = x - im.width / 2, y - im.height / 2
    else: px, py = x - 2 * size - ox, y - 1.5 * size
    base.alpha_composite(im, (round(px), round(py)))
    return tw


def hline(base, x0, x1, y, color, a, w=4):
    ov = Image.new("RGBA", base.size, color + (0,)); ImageDraw.Draw(ov).line((x0, y, x1, y), fill=color + (int(255 * a),), width=w)
    base.alpha_composite(ov)


def footer(base, label="FRC TEAM 8084", y=FOOT_Y, color=ICE):
    tw = text(base, label, CX, y, 62, color, 0.9, "SemiBold", track=0.42)
    for s in (-1, 1):
        x0 = CX + s * (tw / 2 + 70)
        hline(base, min(x0, x0 + s * 240), max(x0, x0 + s * 240), y, color, 0.45)


def finish(base, name):
    a = np.asarray(base.convert("RGB")).astype(np.float32)
    a += np.random.default_rng(7).normal(0, 1.4, (H, W, 1)).astype(np.float32)   # grain: no banding in gradients
    os.makedirs(OUT, exist_ok=True)
    f = OUT + f"{PREFIX}{name}.jpg"
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f, quality=95, subsampling=0)
    print(f)
    return f


# ---------- 1. technical drawing ----------
def d_blueprint():
    base = arr_img(mix((12, 66, 124), (3, 30, 66), YY / H) + 26 * np.clip(1 - dist() / 1900, 0, 1)[..., None])
    b = []
    for k in range(-80, 81):
        x = CX + 54 * k
        if 0 <= x <= W: b.append(line([(x, 0), (x, H)], ICE, 3 if k % 5 == 0 else 1.5, 0.16 if k % 5 == 0 else 0.07))
    for k in range(-80, 81):
        y = CY + 54 * k
        if 0 <= y <= H: b.append(line([(0, y), (W, y)], ICE, 3 if k % 5 == 0 else 1.5, 0.16 if k % 5 == 0 else 0.07))
    add(base, svg(b), clock_dim(0.6))

    S = 1760; x0, y0, x1, y1 = CX - S / 2, CY - S / 2, CX + S / 2, CY + S / 2
    d = []
    def rect(xa, ya, xb, yb, w=5, o=0.55, c=ICE): d.append(line([(xa, ya), (xb, ya), (xb, yb), (xa, yb)], c, w, o, True))
    rect(x0, y0, x1, y1, 6, 0.7); rect(x0 + 70, y0 + 70, x1 - 70, y1 - 70, 3, 0.35)
    m = 330
    for mx, my in ((x0, y0), (x1 - m, y0), (x0, y1 - m), (x1 - m, y1 - m)):
        rect(mx + 20, my + 20, mx + m - 20, my + m - 20, 4, 0.6)
        c = (mx + m / 2, my + m / 2)
        d.append(circle(*c, 120, stroke=ICE, w=4, so=0.6)); d.append(circle(*c, 72, stroke=SKY, w=4, so=0.8))
        d.append(line(rot([(-40, -105), (40, -105), (40, 105), (-40, 105)], math.radians(30), c), SKY, 4, 0.9, True))
        for bx, by in ((40, 40), (m - 40, 40), (40, m - 40), (m - 40, m - 40)): d.append(circle(mx + bx, my + by, 9, stroke=ICE, w=3, so=0.6))
    rect(x0 + m, CY - 35, x1 - m, CY + 35, 3, 0.4); rect(CX - 35, y0 + m, CX + 35, y1 - m, 3, 0.4)
    def dashdot(p0, p1):
        L = math.dist(p0, p1); ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L; t = 0
        while t < L:
            for a, b_ in ((t, min(t + 70, L)), (t + 88, min(t + 96, L))):
                if a < L: d.append(line([(p0[0] + ux * a, p0[1] + uy * a), (p0[0] + ux * b_, p0[1] + uy * b_)], SKY, 3, 0.55))
            t += 114
    dashdot((x0 - 140, CY), (x1 + 140, CY)); dashdot((CX, y0 - 140), (CX, y1 + 140))
    yd = y0 - 190
    for x in (x0, x1): d.append(line([(x, y0 - 20), (x, yd - 40)], ICE, 2, 0.5))
    d.append(line([(x0, yd), (x1, yd)], ICE, 3, 0.75))
    d.append(poly([(x0, yd), (x0 + 50, yd - 15), (x0 + 50, yd + 15)], fill=ICE, fo=0.8))
    d.append(poly([(x1, yd), (x1 - 50, yd - 15), (x1 - 50, yd + 15)], fill=ICE, fo=0.8))
    xd = x0 - 110
    for y in (y0, y1): d.append(line([(x0 - 20, y), (xd - 40, y)], ICE, 2, 0.5))
    d.append(line([(xd, y0), (xd, y1)], ICE, 3, 0.75))
    d.append(poly([(xd, y0), (xd - 15, y0 + 50), (xd + 15, y0 + 50)], fill=ICE, fo=0.8))
    d.append(poly([(xd, y1), (xd - 15, y1 - 50), (xd + 15, y1 - 50)], fill=ICE, fo=0.8))
    balloons = [((x0 + 165, y1 - 165), (x0 + 60, y1 + 200), "1"), ((CX + 300, CY + 35), (x1 - 60, y1 + 200), "2")]
    for (ax, ay), (bx, by), _ in balloons:
        d.append(line([(ax, ay), (bx, by - 42)], ICE, 2, 0.6)); d.append(circle(ax, ay, 8, fill=ICE, fo=0.8))
        d.append(circle(bx, by, 42, stroke=ICE, w=3, so=0.8))
    d = kg(d)
    # title block: under the drawing (phone), bottom-right corner of the sheet (desktop)
    tb = (W - 1100, H - 150 - 320, W - 120, H - 150) if DESK else (x0, y1 + 320, x1, y1 + 640)
    dv = tb[0] + 730 if DESK else CX + 300
    t1, t2 = (46, 30) if DESK else (60, 38)
    rect(*tb, 4, 0.75)
    d.append(line([(tb[0], tb[1] + 130), (tb[2], tb[1] + 130)], ICE, 3, 0.6))
    d.append(line([(tb[0], tb[1] + 230), (tb[2], tb[1] + 230)], ICE, 2, 0.5))
    d.append(line([(dv, tb[1] + 130), (dv, tb[3])], ICE, 2, 0.5))
    add(base, svg(d), glows=((10, 0.5),))
    place_logo(base, 1320, glow_c=WHITE, glow_k=0.3)
    text(base, "27.0 in  ·  686 mm", *kp(CX, yd - 52), round(kk(46)), ICE, 0.85, mono=True)
    text(base, "27.0 in  ·  686 mm", *kp(xd - 52, CY), round(kk(46)), ICE, 0.85, mono=True, angle=90)
    for _, (bx, by), n in balloons: text(base, n, *kp(bx, by), round(kk(44)), ICE, 0.95, mono=True)
    text(base, "ALFA ROBOTICS  ·  FRC TEAM 8084", tb[0] + 50, tb[1] + 68, t1, ICE, 0.95, "SemiBold", 0.12, "l")
    text(base, "1  SWERVE MODÜLÜ ×4   2  ŞASİ 27×27" if DESK else "1  SWERVE MODÜLÜ ×4      2  ŞASİ 27×27", tb[0] + 50, tb[1] + 182, t2, ICE, 0.8, mono=True, anchor="l")
    text(base, "ÇİZEN: 8084", dv + 40, tb[1] + 182, t2, ICE, 0.8, mono=True, anchor="l")
    text(base, "ÖLÇEK 1:5   ·   REV v10", tb[0] + 50, tb[1] + 276, t2, ICE, 0.8, mono=True, anchor="l")
    text(base, "SAYFA 1/1", dv + 40, tb[1] + 276, t2, ICE, 0.8, mono=True, anchor="l")
    return base


# ---------- 2. circuit board ----------
def offset(p, dd):
    p = [np.array(q, float) for q in p]; out = []
    for i in range(len(p)):
        segs = ([p[i] - p[i - 1]] if i > 0 else []) + ([p[i + 1] - p[i]] if i < len(p) - 1 else [])
        ns = [np.array((-s[1], s[0])) / np.linalg.norm(s) for s in segs]
        m = sum(ns); m = m / np.linalg.norm(m)
        out.append(p[i] + m * dd / max(0.3, float(np.dot(m, ns[0]))))
    return [tuple(q) for q in out]


def d_circuit():
    rng = np.random.default_rng(2)
    base = arr_img(mix((0, 46, 90), (0, 10, 26), dist() / 2700))
    d, ends = [], []
    def bundle(start, d0, d1, L, n, o):
        p0 = np.array(start, float); d0 = np.array(d0, float); d1 = np.array(d1, float) / math.sqrt(2)
        a = p0 + d0 * L[0]; b = a + d1 * L[1]; c = b + d0 * L[2]
        for i in range(n):
            q = offset([p0, a, b, c], (i - (n - 1) / 2) * 34)
            cut = rng.uniform(0, 160); last = np.array(q[-1]) - d0 * cut; q[-1] = tuple(last)
            d.append(line(q, SKY, 6, o)); ends.append((q, o))
    for side in (1, -1):
        for y in (np.arange(140, H, 300) if DESK else np.arange(330, 4500, 400)):
            n = int(rng.integers(3, 7)); sgn = 1 if y < CY else -1
            x0 = -20 if side == 1 else W + 20
            bundle((x0, y), (side, 0), (side, sgn), (rng.uniform(80, 520), rng.uniform(140, 300), rng.uniform(150, 600)), n, rng.uniform(0.35, 0.85))
    for x, sg in (((420, 1), (1300, 1), (2540, -1), (3420, -1)) if DESK else ((420, 1), (1740, -1))):
        bundle((x, H + 20), (0, -1), (sg, -1), (rng.uniform(150, 300), 260, 400), 5, 0.7)
        bundle((x, -20), (0, 1), (sg, 1), (rng.uniform(100, 200), 200, 300), 4, 0.45)
    for q, o in ends:
        d.append(circle(*q[-1], 13, fill=(0, 22, 46), stroke=SKY, w=5, so=o))
    L = svg(d)
    m = clear_zone(700, 1000) * clock_dim(0.5)
    add(base, L, m, ((14, 1.0), (50, 0.8)))
    p = []
    for q, o in [ends[i] for i in rng.choice(len(ends), 16, replace=False)]:
        t = rng.uniform(0.25, 0.85); seg = rng.integers(0, len(q) - 1)
        x = q[seg][0] + (q[seg + 1][0] - q[seg][0]) * t; y = q[seg][1] + (q[seg + 1][1] - q[seg][1]) * t
        p.append(circle(x, y, 11, fill=ICE, fo=1)); p.append(circle(x, y, 26, fill=SKY, fo=0.25))
    add(base, svg(p), m, ((20, 1.2),))
    place_logo(base, 1320, glow_k=0.75)
    footer(base)
    return base


# ---------- 3. gears ----------
def gear_path(cx, cy, R, N, dep, ph, holes=6):
    p = 2 * math.pi / N; q = []
    for k in range(N):
        a0 = ph + k * p
        for f, r in ((0, R - dep), (0.2, R - dep), (0.4, R - dep), (0.5, R), (0.7, R), (0.9, R)):
            q.append((cx + r * math.cos(a0 + f * p), cy + r * math.sin(a0 + f * p)))
    d = path(q, True) + " " + circ_path(cx, cy, R * 0.16)
    for j in range(holes):
        a = ph + j * 2 * math.pi / holes
        d += " " + circ_path(cx + 0.56 * R * math.cos(a), cy + 0.56 * R * math.sin(a), R * 0.17)
    return d


def d_gears():
    base = arr_img(mix((0, 52, 100), (0, 12, 30), dist() / 2600))
    pitch = 2 * math.pi * 1000 / 36
    G = [(CX, CY, 1000, 36, 0.0)]
    ph1 = 0.0; d = []
    def mesh(theta, R):
        N = round(2 * math.pi * R / pitch); R = N * pitch / (2 * math.pi)
        dd = 1000 + R - 70
        f1 = ((theta - ph1) / (2 * math.pi / 36)) % 1
        f2 = 0.7 - (f1 - 0.2)
        ph = theta + math.pi - f2 * 2 * math.pi / N
        return (CX + dd * math.cos(theta), CY + dd * math.sin(theta), R, N, ph)
    G += [mesh(math.radians(-125), 560), mesh(math.radians(-40), 300), mesh(math.radians(50), 700), mesh(math.radians(140), 380)]
    for i, (x, y, R, N, ph) in enumerate(G):
        fo = 0.13 if i == 0 else 0.09 + 0.02 * (i % 2)
        d.append(shape(gear_path(x, y, R, N, 70, ph, 6 if R > 400 else 5), fill=SKY, fo=fo, stroke=SKY, w=5, so=0.5, rule="evenodd"))
        d.append(circle(x, y, R - 120, stroke=ICE, w=3, so=0.18)); d.append(circle(x, y, R * 0.16 + 26, stroke=ICE, w=4, so=0.35))
        for j in range(6):
            a = ph + math.pi / 6 + j * math.pi / 3
            d.append(circle(x + 0.3 * R * math.cos(a), y + 0.3 * R * math.sin(a), 12, fill=ICE, fo=0.35))
    d = kg(d)
    if DESK:   # two extra gears fill the wide sides
        for x, y, R, ph in ((430, 1720, 520, 0.1), (3450, 380, 460, 0.4)):
            d.append(shape(gear_path(x, y, R, round(2 * math.pi * R / pitch), 70, ph, 5), fill=SKY, fo=0.08, stroke=SKY, w=5, so=0.4, rule="evenodd"))
            d.append(circle(x, y, R - 120, stroke=ICE, w=3, so=0.15))
    add(base, svg(d), clock_dim(0.55), ((18, 0.7),))
    place_logo(base, 1320, glow_k=0.6)
    footer(base)
    return base


# ---------- 4. hex HUD ----------
def d_hexhud():
    rng = np.random.default_rng(4)
    base = arr_img(mix((0, 44, 86), (0, 8, 22), dist() / 2600))
    s = 78; w = math.sqrt(3) * s
    seeds = ([(rng.uniform(0, W), rng.uniform(0, H)) for _ in range(7)] + [(300, H - 200), (W - 300, 300)] if DESK else
             [(rng.uniform(0, W), rng.uniform(1300, H)) for _ in range(6)] + [(150, 4400), (2000, 1500)])
    d = []
    for row in range(int(H / (1.5 * s)) + 2):
        for col in range(int(W / w) + 2):
            x = col * w + (row % 2) * w / 2; y = row * 1.5 * s
            cl = max(math.exp(-((x - a) ** 2 + (y - b) ** 2) / (2 * 380 ** 2)) for a, b in seeds)
            hexp = [(x + (s - 4) * math.cos(math.radians(60 * i + 30)), y + (s - 4) * math.sin(math.radians(60 * i + 30))) for i in range(6)]
            lit = rng.random() < 0.04 + 0.35 * cl
            d.append(poly(hexp, fill=SKY if lit else None, fo=rng.uniform(0.08, 0.32) * (0.4 + cl), stroke=ICE, w=2, so=0.07 + 0.22 * cl))
    add(base, svg(d), clear_zone(650, 1000) * clock_dim(0.5), ((12, 0.6),))
    h = []
    sweep = 60
    for i in range(sweep):
        a0 = math.radians(-90 - 55 + 55 * i / sweep); a1 = math.radians(-90 - 55 + 55 * (i + 1) / sweep)
        h.append(poly([(CX, CY), (CX + 1000 * math.cos(a0), CY + 1000 * math.sin(a0)), (CX + 1000 * math.cos(a1), CY + 1000 * math.sin(a1))], fill=SKY, fo=0.004 * i))
    h.append(circle(CX, CY, 820, stroke=SKY, w=4, so=0.55))
    for k in range(120):
        a = math.radians(3 * k); L = 45 if k % 5 == 0 else 20
        h.append(line([(CX + 870 * math.cos(a), CY + 870 * math.sin(a)), (CX + (870 + L) * math.cos(a), CY + (870 + L) * math.sin(a))], ICE, 3, 0.55))
    for a0 in (20, 110, 200, 290):
        q = [(CX + 975 * math.cos(math.radians(a)), CY + 975 * math.sin(math.radians(a))) for a in range(a0, a0 + 51, 2)]
        h.append(line(q, SKY, 14, 0.7))
    for a in (0, 90, 180, 270):
        r = math.radians(a); c = (CX + 1030 * math.cos(r), CY + 1030 * math.sin(r))
        h.append(poly(rot([(-28, -22), (-28, 22), (8, 0)], r + math.pi, c), fill=ICE, fo=0.8))
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = CX + sx * 1010, CY + sy * 1060
            h.append(line([(x - sx * 110, y), (x, y), (x, y - sy * 110)], SKY, 6, 0.65))
    add(base, svg(kg(h)), glows=((10, 0.8),))
    place_logo(base, 1260, glow_k=0.65)
    ty = H - 420 if DESK else CY + 1150
    for i, s_ in enumerate(("SYS  ONLINE", "MOD  TELEOP", "CAN  100%")):
        text(base, s_, 90, ty + 62 * i, 42, SKY if i == 0 else ICE, 0.85, mono=True, anchor="l")
    for i, s_ in enumerate(("BAT 12.8 V", "LAT  18 ms", "TEAM  8084")):
        text(base, s_, W - 90, ty + 62 * i, 42, ICE, 0.85, mono=True, anchor="r")
    footer(base)
    return base


# ---------- 5. robot vision ----------
def d_vision():
    rng = np.random.default_rng(5)
    base = arr_img(mix((0, 40, 78), (0, 8, 20), dist(CX, 0.45 * H) / 2700))
    vy = (0.50 if DESK else 0.40) * H; f = []; fz = 1.03 * (H - vy) if DESK else 2900
    for x in np.arange(-4000, W + 4001, 330): f.append(line([(CX, vy), (x, H + 600)], ICE, 3, 0.16))
    z = 1.0
    while True:
        y = vy + fz / z
        if y > H: z += 0.4; continue
        if y - vy < 40: break
        f.append(line([(0, y), (W, y)], ICE, 3, 0.16)); z += 0.45
    add(base, svg(f), np.clip((YY - vy) / (500 if DESK else 1400), 0, 1) * clear_zone(500, 900))
    o = []
    tags = (((560, 520, 300, -9, 4), (3300, 480, 260, 7, 7), (600, 1480, 380, 12, 12), (3260, 1500, 400, -10, 15)) if DESK else
            ((330, 1520, 330, -9, 4), (1830, 1440, 280, 7, 7), (310, 3560, 420, 12, 12), (1850, 3470, 460, -10, 15)))
    for tx, ty, size, ang, tid in tags:
        g = np.ones((10, 10)); g[1:9, 1:9] = 0; g[2:8, 2:8] = rng.random((6, 6)) > 0.5
        rgb_ = np.where(g[..., None] > 0, np.array((226, 236, 240)), np.array((8, 14, 22))).astype(np.uint8)
        im = Image.fromarray(rgb_, "RGB").resize((size, size), Image.NEAREST).convert("RGBA")
        im = scale_alpha(im.rotate(-ang, expand=True, resample=Image.BICUBIC), 0.92)
        base.alpha_composite(im, (round(tx - im.width / 2), round(ty - im.height / 2)))
        a = math.radians(ang); hs = size * 0.4
        q = rot([(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)], a, (tx, ty))
        o.append(line(q, SKY, 6, 0.95, True))
        for c in q: o.append(circle(*c, 11, fill=SKY))
        ax = rot([(0, 0), (size * 0.45, 0)], a, (tx, ty)); ay = rot([(0, 0), (0, -size * 0.45)], a, (tx, ty))
        o.append(line(ax, (255, 90, 90), 8, 0.95)); o.append(line(ay, (90, 225, 130), 8, 0.95))
        o.append(line([(tx, ty), (tx + size * 0.22, ty + size * 0.3)], SKY, 8, 0.95))
        lx, ly = min(c[0] for c in q), min(c[1] for c in q) - 34
        o.append(("t", f"ID {tid}  ·  {rng.uniform(1.5, 5.5):.2f} m", lx, ly))
    add(base, svg([e for e in o if isinstance(e, str)]), glows=((8, 0.7),))
    bb = place_logo(base, 1260, glow_k=0.55)
    k = []
    x0, y0, x1, y1 = bb[0] - 50, bb[1] - 50, bb[2] + 50, bb[3] + 50
    for (cx_, cy_, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        k.append(line([(cx_, cy_ + sy * 120), (cx_, cy_), (cx_ + sx * 120, cy_)], SKY, 9, 0.95))
    k.append(poly([(x0, y0 - 80), (x0 + 560, y0 - 80), (x0 + 560, y0 - 10), (x0, y0 - 10)], fill=SKY, fo=0.9))
    for sx, sy in (((70, 90), (W - 70, 90), (70, H - 120), (W - 70, H - 120)) if DESK else ((70, 1290), (W - 70, 1290), (70, 4180), (W - 70, 4180))):
        dx, dy = (1 if sx < CX else -1), (1 if sy < CY else -1)
        k.append(line([(sx, sy + dy * 130), (sx, sy), (sx + dx * 130, sy)], ICE, 6, 0.5))
    add(base, svg(k), glows=((8, 0.6),))
    text(base, "ALFA 8084  ·  %99,8", x0 + 22, y0 - 45, 44, (0, 22, 46), 1, mono=True, anchor="l")
    for e in o:
        if not isinstance(e, str): text(base, e[1], e[2], e[3], 38, SKY, 0.95, mono=True, anchor="l")
    text(base, "CAM 0  ·  1280×800  ·  90 FPS  ·  12 ms", CX, H - 270 if DESK else round(0.805 * H), 40, ICE, 0.7, mono=True)
    footer(base)
    return base


# ---------- 6. swerve / speed ----------
def d_swerve():
    rng = np.random.default_rng(6)
    base = arr_img(mix((0, 52, 104), (0, 10, 28), (XX / W * 0.35 + YY / H * 0.65)))
    a = math.radians(-60); u = (math.cos(a), math.sin(a)); n = (-u[1], u[0])
    s = []
    for _ in range(230):
        x, y = rng.uniform(-200, W + 400), rng.uniform(0, H + 600)
        L, w = rng.uniform(250, 1500), rng.uniform(3, 16)
        tail = (x - u[0] * L, y - u[1] * L)
        s.append(poly([(x + n[0] * w / 2, y + n[1] * w / 2), (x - n[0] * w / 2, y - n[1] * w / 2), tail],
                      fill=SKY if rng.random() < 0.6 else ICE, fo=rng.uniform(0.08, 0.45)))
    add(base, svg(s), clear_zone(650, 980) * clock_dim(0.5), ((8, 0.7),))
    m = []
    for mx, my in ((CX - 800, CY - 800), (CX + 800, CY - 800), (CX - 800, CY + 800), (CX + 800, CY + 800)):
        for i in range(1, 9):
            m.append(circle(mx - u[0] * 70 * i, my - u[1] * 70 * i, 100 - 9 * i, fill=SKY, fo=0.16 - 0.017 * i))
        m.append(circle(mx, my, 125, fill=(0, 30, 60), fo=0.85, stroke=ICE, w=6, so=0.8))
        m.append(circle(mx, my, 98, stroke=SKY, w=3, so=0.45))
        m.append(poly(rot([(-85, -32), (85, -32), (85, 32), (-85, 32)], a, (mx, my)), fill=ICE, fo=0.9))
        tip = (mx + u[0] * 260, my + u[1] * 260)
        m.append(line([(mx + u[0] * 140, my + u[1] * 140), tip], SKY, 9, 0.95))
        m.append(poly(rot([(0, 0), (-50, -26), (-50, 26)], a, tip), fill=SKY))
    add(base, svg(kg(m)), glows=((14, 0.8),))
    place_logo(base, 1300, glow_k=0.65)
    footer(base)
    return base


# ---------- 7. competition field (top view) ----------
def robot_top(cx, cy, ang, color, d):
    r = math.radians(ang)
    d.append(poly(rot([(-95, -95), (95, -95), (95, 95), (-95, 95)], r, (cx, cy)), fill=color, fo=0.95))
    d.append(poly(rot([(-66, -66), (66, -66), (66, 66), (-66, 66)], r, (cx, cy)), fill=(38, 44, 54), fo=1))
    for sx, sy in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
        c = rot([(sx, sy)], r, (cx, cy))[0]; d.append(circle(*c, 16, stroke=ICE, w=3, so=0.6))
    d.append(poly(rot([(-60, -78), (60, -78), (60, -64), (-60, -64)], r, (cx, cy)), fill=(255, 150, 40), fo=0.9))


def d_field():
    global CX, CY, W
    rng = np.random.default_rng(7)
    dCX, dCY, dW = CX, CY, W
    if DESK: CX, CY, W = 1080, 2504, 2160          # build in phone field coordinates
    FS = 0.86                                         # desktop: field scale after the turn
    a = mix((30, 40, 54), (14, 20, 30), dist() / 2800) + rng.normal(0, 5, (H, dW, 1)).astype(np.float32)
    a += (np.sin(YY / 3.0) * 2.5)[..., None]
    base = arr_img(a)
    x0, x1, y0, y1, ch = 70, W - 70, CY - 2190, CY + 2140, 170
    per = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch), (x0, y0 + ch)]
    RED, BLUE = (215, 45, 55), (30, 105, 235)
    d = [poly([(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y0 + 560), (x0, y0 + 560), (x0, y0 + ch)], fill=RED, fo=0.15),
         poly([(x0, y1 - 560), (x1, y1 - 560), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch)], fill=BLUE, fo=0.17)]
    d.append(line(per, (140, 150, 165), 30, 0.9, True))
    d.append(line([(x0 + ch, y0), (x1 - ch, y0)], RED, 34, 0.9)); d.append(line([(x0 + ch, y1), (x1 - ch, y1)], BLUE, 34, 0.9))
    for i in range(3):
        xs = x0 + ch + 140 + i * 560
        d.append(poly([(xs, y0 - 15), (xs + 300, y0 - 15), (xs + 300, y0 + 15), (xs, y0 + 15)], fill=(20, 24, 30), stroke=RED, w=4, so=0.9))
        d.append(poly([(xs, y1 - 15), (xs + 300, y1 - 15), (xs + 300, y1 + 15), (xs, y1 - 15 + 30)], fill=(20, 24, 30), stroke=BLUE, w=4, so=0.9))
    T = (240, 244, 248)
    d.append(line([(x0 + 20, CY), (x1 - 20, CY)], T, 12, 0.55))
    for y in (CY - 1350, CY + 1350): d.append(line([(x0 + 20, y), (x1 - 20, y)], T, 10, 0.45))
    d.append(line([(x0 + 20, y0 + 560), (x1 - 20, y0 + 560)], RED, 10, 0.65)); d.append(line([(x0 + 20, y1 - 560), (x1 - 20, y1 - 560)], BLUE, 10, 0.65))
    d.append(circle(CX, CY, 820, stroke=T, w=10, so=0.4))
    for tx, ty in ((x0, CY - 700), (x1, CY - 700), (x0, CY + 700), (x1, CY + 700)):
        d.append(poly([(tx - 32, ty - 32), (tx + 32, ty - 32), (tx + 32, ty + 32), (tx - 32, ty + 32)], fill=(230, 236, 240), stroke=(0, 0, 0), w=6))
    robots = [(400, 1420, 15, RED), (1760, 1380, -20, RED), (1080, 1300, 5, RED), (460, 3700, 10, BLUE), (1680, 3820, -15, BLUE), (1560, 3330, 25, BLUE)]
    for x, y, an, c in robots: robot_top(x, y, an, c, d)
    if DESK:
        d = [f'<g transform="translate({dCX} {H / 2}) rotate(-90) scale({FS}) translate({-CX} {-CY})">'] + d + ["</g>"]
        rx, ry = dCX + (3700 - CY) * FS, H / 2 - (460 - CX) * FS   # the 8084 robot after the turn
        CX, CY, W = dCX, dCY, dW
        add(base, svg(d), glows=((10, 0.4),))
        place_logo(base, round(1060 * FS), cy=H / 2, glow_k=0.45, k=1)
        text(base, "8084", rx, ry - 150, 46, ICE, 0.95, mono=True)
        return base
    add(base, svg(d), glows=((10, 0.4),))
    place_logo(base, 1060, glow_k=0.45)
    text(base, "8084", 460, 3700 - 150, 46, ICE, 0.95, mono=True)
    footer(base, y=FOOT_Y + 40)
    return base


# ---------- 8. 8084 robot on the field (isometric) ----------
def d_robot():
    s, T = (19, (0.69 * W, 0.66 * H)) if DESK else (26, (CX, 0.648 * H))
    o = (T[0], T[1] - 27 * 0.5 * s + 18 * s)
    def P(x, y, z): return (o[0] + (x - y) * 0.866 * s, o[1] + (x + y) * 0.5 * s - z * s)
    base = arr_img(mix((0, 48, 96), (0, 8, 20), dist(T[0], 0.62 * H) / 2400))
    g = []
    for k in range(-150, 181, 12):
        g.append(line([P(k, -150, 0), P(k, 180, 0)], ICE, 2, 0.1)); g.append(line([P(-150, k, 0), P(180, k, 0)], ICE, 2, 0.1))
    g.append(poly([P(-150, 50, 0), P(180, 50, 0), P(180, 52, 0), P(-150, 52, 0)], fill=WHITE, fo=0.4))
    g.append(poly([P(-38, -150, 0), P(-36, -150, 0), P(-36, 180, 0), P(-38, 180, 0)], fill=WHITE, fo=0.3))
    add(base, svg(g), np.clip(1 - dist(*T) / 1700, 0, 1) * np.clip((YY - (0.40 if DESK else 0.42) * H) / 500, 0, 1))
    sh = svg([poly([P(-6, -6, 0), P(36, -6, 0), P(36, 36, 0), P(-6, 36, 0)], fill=(0, 0, 0), fo=0.65)])
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
    def shade(c, k): return tuple(min(255, int(v * k)) for v in c)
    def box(x, y, z, dx, dy, dz, c, out, e=0.3):
        top = [P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
        fx = [P(x + dx, y, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x + dx, y, z + dz)]
        fy = [P(x, y + dy, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
        for f, k in ((fy, 0.62), (fx, 0.84), (top, 1.12)):
            out.append(poly(f, fill=shade(c, k), stroke=(0, 0, 0), w=1.5, so=e))
    BL, ALU, DK = (24, 92, 205), (176, 184, 194), (52, 58, 68)
    r = []
    box(-3.5, -3.5, 1.5, 3.5, 34, 5, BL, r); box(0, -3.5, 1.5, 27, 3.5, 5, BL, r)
    box(0, 0, 1.2, 27, 27, 2.6, DK, r)
    for mx, my in ((1, 1), (21, 1), (1, 21), (21, 21)):
        box(mx, my, 3.8, 5, 5, 4.5, (150, 156, 166), r); box(mx + 1, my + 1, 8.3, 3, 3, 1.2, NAVY, r)
    box(9, 9, 3.8, 6, 4, 1.2, (210, 212, 216), r); box(16, 3, 3.8, 4.5, 4, 1.6, (70, 74, 82), r); box(10, 17, 3.8, 7, 3.5, 6.5, (28, 28, 32), r)
    for yy in (4, 22):
        box(4, yy, 3.8, 2, 1, 42, ALU, r); box(5.2, yy + (1.2 if yy == 4 else -1.2), 12, 1.4, 1, 38, (140, 148, 160), r)
    box(4, 4, 45.8, 2, 19, 2, ALU, r)
    box(6.6, 7, 26, 9, 13, 9, NAVY, r)
    box(6.6, 6.4, 33.2, 9, 0.6, 0.7, SKY, r, 0)
    for zz in (27.2, 31.2): box(15.6, 7.5, zz, 2.2, 12, 2.2, (255, 140, 40), r)
    box(-3.5, 27, 1.5, 30.5, 3.5, 5, BL, r); box(27, -3.5, 1.5, 3.5, 34, 5, BL, r)
    R = svg(r)
    rim = Image.new("RGBA", (W, H), SKY + (0,)); rim.putalpha(R.getchannel("A").point(lambda v: int(v * 0.8)))
    base.alpha_composite(rim.filter(ImageFilter.GaussianBlur(55)))
    base.alpha_composite(R)
    led = svg([poly([P(6.6, 6.4, 33.9), P(15.6, 6.4, 33.9), P(15.6, 7, 33.9), P(6.6, 7, 33.9)], fill=SKY)])
    glow(base, led, 25, 2.5)
    f = font(400, "Bold SemiCondensed")
    def face_text(p_tl, p_tr, p_bl, txt):
        im = Image.new("RGBA", (1, 1)); bbox = ImageDraw.Draw(im).textbbox((0, 0), txt, font=f)
        ti = Image.new("RGBA", (bbox[2] - bbox[0] + 20, bbox[3] - bbox[1] + 20), (255, 255, 255, 0))
        ImageDraw.Draw(ti).text((10 - bbox[0], 10 - bbox[1]), txt, font=f, fill=(255, 255, 255, 245))
        O = np.array(p_tl); U = (np.array(p_tr) - O) / ti.width; V = (np.array(p_bl) - O) / ti.height
        Mi = np.linalg.inv(np.array([[U[0], V[0]], [U[1], V[1]]]))
        data = (Mi[0, 0], Mi[0, 1], -(Mi[0] @ O), Mi[1, 0], Mi[1, 1], -(Mi[1] @ O))
        base.alpha_composite(ti.transform((W, H), Image.AFFINE, data, Image.BICUBIC))
    zt, zb = 5.9, 2.1
    hw = 7.5
    face_text(P(30.5, 13.5 + hw, zt), P(30.5, 13.5 - hw, zt), P(30.5, 13.5 + hw, zb), "8084")
    face_text(P(13.5 - hw, 30.5, zt), P(13.5 + hw, 30.5, zt), P(13.5 - hw, 30.5, zb), "8084")
    if DESK:
        bb = place_logo(base, 1000, cx=0.29 * W, cy=CY, glow_k=0.6, k=1)
        text(base, "FRC TEAM 8084", 0.29 * W, bb[3] + 130, 50, ICE, 0.85, "SemiBold", 0.42)
        return base
    place_logo(base, 820, cy=round(0.335 * H), glow_k=0.6)
    text(base, "FRC TEAM 8084", CX, round(0.885 * H) - 30, 50, ICE, 0.85, "SemiBold", 0.42)
    return base


# ---------- 9. 2027 season: FIRST Canopy / BIOCORE (biodiversity) ----------
def leaf(b, ang, L, wdt, fill, fo, d, veins=True):
    u = (math.cos(ang), math.sin(ang)); n = (-u[1], u[0])
    t = (b[0] + u[0] * L, b[1] + u[1] * L)
    lc = (b[0] + u[0] * L * 0.45 + n[0] * wdt, b[1] + u[1] * L * 0.45 + n[1] * wdt)
    rc = (b[0] + u[0] * L * 0.45 - n[0] * wdt, b[1] + u[1] * L * 0.45 - n[1] * wdt)
    dd = f"M{b[0]:.1f} {b[1]:.1f} Q{lc[0]:.1f} {lc[1]:.1f} {t[0]:.1f} {t[1]:.1f} Q{rc[0]:.1f} {rc[1]:.1f} {b[0]:.1f} {b[1]:.1f} Z"
    d.append(shape(dd, fill=fill, fo=fo, stroke=SKY, w=3, so=0.28))
    if not veins: return
    d.append(line([b, (b[0] + u[0] * L * 0.9, b[1] + u[1] * L * 0.9)], SKY, 4, 0.55))
    for k in range(1, 5):
        tk = k / 5.5; p = (b[0] + u[0] * L * tk, b[1] + u[1] * L * tk)
        for sg in (1, -1):
            ln = wdt * 0.55 * (1 - tk * 0.5)
            e = (p[0] + (u[0] * 0.6 + sg * n[0]) * ln, p[1] + (u[1] * 0.6 + sg * n[1]) * ln)
            d.append(line([p, e], SKY, 3, 0.45)); d.append(circle(*e, 6, fill=SKY, fo=0.7))


def d_canopy():
    rng = np.random.default_rng(9)
    t = YY / H
    a = np.where((t < 0.5)[..., None], mix((2, 42, 58), (0, 50, 92), t / 0.5), mix((0, 50, 92), (0, 16, 34), (t - 0.5) / 0.5))
    base = arr_img(a + 18 * np.clip(1 - dist() / 1500, 0, 1)[..., None])
    GREENS = [(8, 78, 78), (14, 96, 88), (0, 72, 100), (20, 110, 96), (6, 60, 70)]
    for layer, (k0, fo) in enumerate(((0.75, 0.55), (1.0, 0.85))):
        d = []
        for (ox, oy, a0, a1) in ((-80, -80, 15, 85), (W + 80, -80, 95, 165), (-80, H + 80, -80, -15), (W + 80, H + 80, -165, -100),
                                 (-60, 0.42 * H, -35, 35), (W + 60, 0.62 * H, 145, 215)):
            cnt = 9 if oy < 0 or oy > H else 5
            for _ in range(cnt):
                ang = math.radians(rng.uniform(a0, a1)); L = rng.uniform(450, 1150) * k0
                b = (ox + rng.uniform(-120, 120), oy + rng.uniform(-120, 120))
                leaf(b, ang, L, L * rng.uniform(0.2, 0.3), GREENS[rng.integers(len(GREENS))], fo, d, veins=layer == 1)
        add(base, svg(d), clear_zone(720, 1000) * (clock_dim(0.75) if layer else 1), ((10, 0.5),) if layer else ())
    c = []
    for i in range(48):
        a = 2 * math.pi * i / 48; r = 860 + 30 * math.sin(6 * a)
        c.append(circle(CX + r * math.cos(a), CY + r * math.sin(a), 14 if i % 4 else 22, fill=SKY, fo=0.55 if i % 4 else 0.85))
    c.append(line([(CX + (930 + 40 * math.sin(5 * a)) * math.cos(a), CY + (930 + 40 * math.sin(5 * a)) * math.sin(a))
                   for a in np.linspace(0, 2 * math.pi, 361)], ICE, 4, 0.35, True))
    c.append(line([(CX + (790 + 25 * math.sin(7 * a + 1)) * math.cos(a), CY + (790 + 25 * math.sin(7 * a + 1)) * math.sin(a))
                   for a in np.linspace(0, 2 * math.pi, 361)], SKY, 3, 0.3, True))
    add(base, svg(kg(c)), glows=((14, 0.9),))
    fl = []
    for _ in range(80):
        x, y = rng.uniform(0, W), rng.uniform((0.04 if DESK else 0.25) * H, 0.95 * H)
        if math.hypot(x - CX, y - CY) < kk(1000): continue
        fl.append(circle(x, y, rng.uniform(4, 10), fill=(205, 255, 170) if rng.random() < 0.5 else ICE, fo=rng.uniform(0.6, 1)))
    add(base, svg(fl), glows=((16, 1.6), (40, 0.8)))
    place_logo(base, 1260, glow_k=0.6)
    text(base, "2027  ·  BIOCORE", CX, CY + 820 if DESK else round(0.795 * H), 52, (205, 255, 170), 0.9, "SemiBold", 0.35)
    footer(base, y=FOOT_Y + (0 if DESK else 20))
    return base


# ---------- 10. wolf night: moon, low-poly mountains, network stars ----------
def d_night():
    rng = np.random.default_rng(10)
    t = YY / H
    base = arr_img(mix((2, 18, 44), (0, 50, 96), np.clip(t / 0.75, 0, 1)))
    mc = (CX, CY - 120) if DESK else (CX, 0.43 * H)
    moon = np.clip(1 - dist(*mc) / kk(1500), 0, 1) ** 2
    m = svg([circle(*mc, kk(560), fill=(228, 240, 240), fo=1)])
    a_ = np.asarray(base).astype(np.float32); a_[..., :3] += (moon * 70)[..., None] * np.array((0.6, 0.85, 1.0)); base = Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8), "RGBA")
    glow(base, m, 90, 0.8); base.alpha_composite(m)
    cr = [circle(mc[0] + kk(rng.uniform(-380, 380)), mc[1] + kk(rng.uniform(-380, 380)), kk(rng.uniform(25, 90)), fill=(180, 200, 210), fo=0.25) for _ in range(9)]
    base.alpha_composite(alpha_mul(svg(cr), (dist(*mc) < kk(540)).astype(np.float32)))
    pts_ = []
    while len(pts_) < 130:
        x, y = rng.uniform(0, W), rng.uniform(0.02 * H, 0.66 * H)
        if DESK:
            if math.hypot(x - mc[0], y - mc[1]) > kk(680): pts_.append((x, y))
        elif math.hypot(x - mc[0], y - mc[1]) > 680 and not (0.06 * H < y < 0.24 * H and rng.random() < 0.6): pts_.append((x, y))
    P = np.array(pts_); s = []
    for i, p in enumerate(P):
        dd = np.hypot(*(P - p).T); nb = np.argsort(dd)[1:3]
        for j in nb:
            if dd[j] < 380: s.append(line([tuple(p), tuple(P[j])], ICE, 2, 0.16))
    for p in P:
        s.append(circle(*p, rng.uniform(3, 8), fill=SKY if rng.random() < 0.3 else ICE, fo=rng.uniform(0.6, 1)))
    add(base, svg(s), clock_dim(0.6), ((10, 1.0),))
    mts = (((0.70 * H, 320, 1), (0.80 * H, 230, 2)) if DESK else ((0.66 * H, 420, 1), (0.74 * H, 300, 2)))
    for (y0, amp, seed), cols in zip(mts, (((0, 44, 84), (0, 36, 72), (0, 52, 96)), ((0, 24, 52), (0, 18, 42), (0, 30, 60)))):
        r2 = np.random.default_rng(seed)
        xs = np.linspace(-100, W + 100, 24 if DESK else 14)
        ridge = [(x, y0 - amp * abs(math.sin(x / 520 + seed)) * r2.uniform(0.5, 1.1)) for x in xs]
        low = [(x + r2.uniform(-60, 60), y + r2.uniform(300, 600) * (0.6 if DESK else 1)) for x, y in ridge]
        d = []
        for i in range(len(xs) - 1):
            for tri in ((ridge[i], ridge[i + 1], low[i]), (ridge[i + 1], low[i + 1], low[i])):
                d.append(poly(tri, fill=cols[r2.integers(3)], fo=1, stroke=cols[0], w=2, so=1))
            d.append(line([ridge[i], ridge[i + 1]], SKY, 3, 0.35))
        d.append(poly(low + [(W + 100, H + 10), (-100, H + 10)], fill=cols[1], fo=1))
        base.alpha_composite(svg(d))
    place_logo(base, 1320, glow_k=0.5)
    footer(base)
    return base


DESIGNS = [("01 Teknik Cizim", d_blueprint), ("02 Devre Karti", d_circuit), ("03 Disliler", d_gears), ("04 Altigen HUD", d_hexhud),
           ("05 Robot Gorusu", d_vision), ("06 Swerve Hiz", d_swerve), ("07 Yarisma Sahasi", d_field), ("08 Robot 8084", d_robot),
           ("09 Sezon 2027 BIOCORE", d_canopy), ("10 Kurt Gecesi", d_night)]


def preview(files, out):
    tw, th = 432, 936
    sheet = Image.new("RGB", (5 * tw + 6 * 30, 2 * (th + 70) + 30), (24, 28, 34))
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGBA").resize((tw, th), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.text((tw / 2, 0.085 * th), "Perşembe 12 Kasım", font=font(22, "SemiBold"), fill=(255, 255, 255, 230), anchor="mm")
        d.text((tw / 2, 0.165 * th), "09:41", font=font(120, "SemiBold"), fill=(255, 255, 255, 235), anchor="mm")
        x, y = 30 + (i % 5) * (tw + 30), 30 + (i // 5) * (th + 70)
        sheet.paste(im.convert("RGB"), (x, y))
        ImageDraw.Draw(sheet).text((x + tw / 2, y + th + 32), os.path.basename(f)[25:-4], font=font(30, "SemiBold"), fill=(230, 236, 240), anchor="mm")
    sheet.save(out, quality=92)
    print(out)


def preview_desk(files, out, cols=4):
    tw, th = 640, 360
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 24, rows * (th + 60) + 24), (24, 28, 34))
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 24 + (i % cols) * (tw + 24), 24 + (i // cols) * (th + 60)
        sheet.paste(im, (x, y))
        ImageDraw.Draw(sheet).text((x + tw / 2, y + th + 24), os.path.basename(f)[len(PREFIX):-4], font=font(26, "SemiBold"), fill=(230, 236, 240), anchor="mm")
    sheet.save(out, quality=92)
    print(out)


if __name__ == "__main__":
    pick = [int(a) for a in sys.argv[1:] if a.isdigit()] or range(1, 11)
    for i in pick:
        name, fn = DESIGNS[i - 1]
        finish(fn(), name)
    files = [OUT + f"ALFA 8084 - Duvar Kagidi {n}.jpg" for n, _ in DESIGNS]
    if all(os.path.exists(f) for f in files):
        preview(files, OUT + "../duvar_onizleme.jpg")
