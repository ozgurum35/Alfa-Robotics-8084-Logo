# ALFA Robotics 8084 phone wallpapers, set 2 (11-20): vivid colours and logo effects. Same canvas as set 1.
# Usage: python duvar_kagidi2.py [design numbers 11-20 ...]   (no argument = all), then a preview sheet.
import colorsys, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from duvar_kagidi import (W, H, CX, CY, FOOT_Y, YY, XX, SKY, ICE, WHITE, OUT, svg, line, poly, shape, circle, rot,
                          path, arr_img, mix, dist, alpha_mul, clear_zone, clock_dim, scale_alpha, glow, add, logo,
                          font, text, footer, finish, preview, DESK, K, kk, kg)


# ---------- helpers ----------
def fbm(seed, octaves=((5, 1.0), (10, 0.5), (20, 0.25), (40, 0.12))):
    rng = np.random.default_rng(seed); acc = np.zeros((H, W), np.float32)
    for n, amp in octaves:
        small = rng.random((max(2, round(n * H / W)), n)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray(small, "F").resize((W, H), Image.BICUBIC))
    acc -= acc.min(); return acc / acc.max()
def light(a, inten, color): a += inten[..., None] * np.array(color, np.float32)
def dilate(A, px):
    for _ in range(max(1, px // 4)): A = A.filter(ImageFilter.MaxFilter(9))
    return A
def solid(A, color, k=1.0):
    im = Image.new("RGBA", A.size, color + (255,)); im.putalpha(A.point(lambda v: int(v * k))); return im
def paste_blur(base, im, x, y, blur):
    pad = blur * 3 + 4
    g = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); g.paste(im, (pad, pad))
    base.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)) if blur else g, (x - pad, y - pad))


def fx_logo(base, width=1320, cy=CY, cx=CX, fx=(), shadow=0.55, k=K):
    """Logo with effects. fx items: ('neon', color, px, blur, k) outer neon rim; ('extrude', c0, c1, steps, dx, dy);
    ('split', c1, c2, d) RGB split; ('holo', k) rainbow sheen on light areas; ('pixel', block); ('hard', color, dx, dy)
    hard offset shadow; ('outline', color, px) solid outline; ('slices', n, d) glitch slices; ('glow', color, blur, k)."""
    L = logo(round(width * k))
    x, y = round(cx - L.width / 2), round(cy - L.height / 2)
    A = L.getchannel("A")
    if shadow: paste_blur(base, solid(A, (0, 0, 0), shadow), x, y + 35, 40)
    for f in fx:
        if f[0] == "glow": paste_blur(base, solid(A, f[1], f[3]), x, y, f[2])
        elif f[0] == "neon":
            pad = f[2] + 4
            R = Image.new("L", (L.width + 2 * pad, L.height + 2 * pad), 0); R.paste(A, (pad, pad)); R = dilate(R, f[2])
            paste_blur(base, solid(R, f[1], f[4]), x - pad, y - pad, f[3]); paste_blur(base, solid(R, f[1], 1.0), x - pad, y - pad, 2)
        elif f[0] == "outline":
            pad = f[2] + 4
            R = Image.new("L", (L.width + 2 * pad, L.height + 2 * pad), 0); R.paste(A, (pad, pad))
            base.alpha_composite(solid(dilate(R, f[2]), f[1]), (x - pad, y - pad))
        elif f[0] == "extrude":
            _, c0, c1, steps, dx, dy = f
            for i in range(steps, 0, -1):
                t = i / steps; c = tuple(int(c0[j] * (1 - t) + c1[j] * t) for j in range(3))
                base.alpha_composite(solid(A, c), (x + round(dx * i), y + round(dy * i)))
        elif f[0] == "hard": base.alpha_composite(solid(A, f[1]), (x + f[2], y + f[3]))
        elif f[0] == "split":
            base.alpha_composite(solid(A, f[1], 0.85), (x - f[3], y)); base.alpha_composite(solid(A, f[2], 0.85), (x + f[3], y))
    for f in fx:
        if f[0] == "holo":
            a = np.asarray(L).astype(np.float32)
            lum = (a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11) / 255
            yy, xx = np.mgrid[0:L.height, 0:L.width]
            hue = ((xx + yy) / (L.width + L.height) * 1.6) % 1
            rainbow = np.stack(np.vectorize(colorsys.hsv_to_rgb)(hue, 0.55, 1.0), -1) * 255
            m = (np.clip((lum - 0.55) / 0.35, 0, 1) * f[1])[..., None]
            a[..., :3] = a[..., :3] * (1 - m) + rainbow * m
            L = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
        elif f[0] == "pixel":
            b = f[1]; L = L.resize((L.width // b, L.height // b), Image.BILINEAR)
            al = L.getchannel("A").point(lambda v: 255 if v > 110 else 0); L.putalpha(al)
            L = L.resize((L.width * b, L.height * b), Image.NEAREST)
        elif f[0] == "slices":
            rng = np.random.default_rng(3); out = L.copy(); out.paste((0, 0, 0, 0), (0, 0, L.width, L.height))
            cuts = sorted(rng.choice(range(80, L.height - 80), f[1] * 2, replace=False))
            prev = 0; shifts = []
            for i, c in enumerate(cuts + [L.height]):
                sh = int(rng.choice((-1, 1)) * f[2]) if i % 2 == 1 else 0
                out.alpha_composite(L.crop((0, prev, L.width, c)), (max(0, sh), prev) if sh >= 0 else (0, prev), (max(0, -sh), 0) if sh < 0 else (0, 0))
                prev = c
            L = out
    base.alpha_composite(L, (x, y))
    return x, y, x + L.width, y + L.height


def stars(rng, n, y0=0, y1=H, rmax=6, color=WHITE, flare=0.0):
    s = []
    for _ in range(n):
        x, y, r = rng.uniform(0, W), rng.uniform(y0, y1), rng.uniform(1.5, rmax)
        s.append(circle(x, y, r, fill=color, fo=rng.uniform(0.4, 1)))
        if rng.random() < flare:
            L = r * 9; s.append(line([(x - L, y), (x + L, y)], color, 2, 0.6)); s.append(line([(x, y - L), (x, y + L)], color, 2, 0.6))
    return svg(s)


def ridge(rng, y0, amp, n=16):
    xs = np.linspace(-100, W + 100, n)
    return [(x, y0 - amp * rng.uniform(0.2, 1.0) * (0.6 + 0.4 * math.sin(x / 400 + rng.uniform(0, 6)))) for x in xs]


# ---------- 11. synthwave ----------
def d_synthwave():
    rng = np.random.default_rng(11); hz = (0.72 if DESK else 0.68) * H
    t = np.clip(YY / hz, 0, 1)
    a = np.where((t < 0.55)[..., None], mix((18, 4, 48), (110, 18, 120), t / 0.55), mix((110, 18, 120), (255, 96, 110), (t - 0.55) / 0.45))
    a = np.where((YY > hz)[..., None], mix((40, 6, 70), (8, 2, 24), (YY - hz) / (H - hz)), a)
    sc, r = ((CX, CY), kk(900)) if DESK else ((CX, 0.50 * H), 900)
    ds = dist(*sc); inside = (ds < r) & (YY < hz)
    st = (YY - (sc[1] - r)) / (2 * r)
    yb = YY - (sc[1] + 0.05 * r)
    gap = 6 + 46 * np.clip(yb / (0.9 * r), 0, 1)
    cut = (yb > 0) & ((yb % 90) < gap)
    sun = mix((255, 236, 90), (255, 40, 150), st * 1.15)
    a = np.where((inside & ~cut)[..., None], sun, a)
    light(a, np.clip(1 - ds / kk(1700), 0, 1) ** 2 * (YY < hz), (120, 30, 70))
    base = arr_img(a)
    base.alpha_composite(alpha_mul(stars(rng, 160, 0, hz - (150 if DESK else 500), 4), clock_dim(0.7) * (dist(*sc) > r + 40)))
    g = []
    for k in (range(-24, 25) if DESK else range(-14, 15)):
        g.append(line([(CX, hz), (CX + k * 330, H + 20)], (255, 60, 220), 5, 0.9))
    z = 1.0
    while True:
        y = hz + (0.75 * (H - hz) if DESK else 260 * 6) / z
        if y > H: z += 0.35; continue
        if y - hz < 12: break
        g.append(line([(0, y), (W, y)], (255, 60, 220), 5, 0.9)); z += 0.55
    add(base, svg(g), np.clip((YY - hz) / (120 if DESK else 250), 0, 1), ((10, 1.2), (30, 0.8)))
    m = []
    R = [(x, y + (hz - y) * (1 - min(1, abs(x - CX) / kk(900)) ** 2) * 0.95) for x, y in ridge(rng, hz, 300 if DESK else 380, 20 if DESK else 12)]  # mountains at the sides only
    m.append(poly(R + [(W + 100, hz + 2), (-100, hz + 2)], fill=(30, 6, 60), fo=1)); m.append(line(R, (0, 240, 255), 5, 0.95))
    add(base, svg(m), glows=((12, 1.0),))
    fx_logo(base, 1300, cy=round(sc[1]), fx=(("extrude", (40, 0, 80), (255, 50, 170), 26, 2.2, 2.2), ("neon", (255, 80, 220), 22, 40, 0.9)))
    footer(base, color=(0, 240, 255))
    return base


# ---------- 12. glitch ----------
def d_glitch():
    rng = np.random.default_rng(12)
    a = mix((26, 12, 58), (4, 2, 12), dist() / 2600)
    a *= (1 - 0.18 * ((YY % 8) < 3))[..., None]
    base = arr_img(a)
    g = []
    COLS = [(0, 255, 240), (255, 0, 170), (255, 230, 0), (120, 80, 255)]
    for band in range(18 if DESK else 14):
        yc = rng.uniform(0.02 * H if DESK else 0.25 * H, 0.98 * H)
        for _ in range(rng.integers(3, 9)):
            y = yc + rng.normal(0, 70); h = rng.uniform(6, 60); x = rng.uniform(-200, W); w = rng.uniform(80, 1200)
            g.append(poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill=COLS[rng.integers(4)], fo=rng.uniform(0.15, 0.7)))
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(0 if DESK else 0.25 * H, H); s = rng.uniform(10, 40)
        g.append(poly([(x, y), (x + s, y), (x + s, y + s), (x, y + s)], fill=COLS[rng.integers(4)], fo=0.8))
    add(base, svg(g), clear_zone(600, 900), ((10, 0.8),))
    fx_logo(base, 1320, fx=(("split", (0, 255, 240), (255, 0, 170), 26), ("slices", 3, 46)), shadow=0.3)
    ty = 150 if DESK else round(0.775 * H)
    text(base, "SYSTEM://ALFA_8084", 110, ty, 50, (0, 255, 240), 0.95, mono=True, anchor="l")
    text(base, "> BOOT OK_  ROBOT ONLINE", 110, ty + 70, 42, (255, 0, 170), 0.9, mono=True, anchor="l")
    footer(base, color=(255, 230, 0))
    return base


# ---------- 13. aurora ----------
def d_aurora():
    rng = np.random.default_rng(13)
    a = mix((2, 6, 26), (4, 30, 60), YY / H)
    rays = np.asarray(Image.fromarray(rng.random((1, 260)).astype(np.float32), "F").resize((W, H), Image.BICUBIC))
    rays = 0.35 + 0.65 * rays
    curt = (((0.38, 110, 50, 520, 0.3), (0.55, 150, 60, 620, 2.1), (0.66, 100, 40, 420, 4.0)) if DESK else
            ((0.36, 160, 70, 900, 0.3), (0.50, 220, 90, 1100, 2.1), (0.60, 140, 60, 700, 4.0)))
    for k, (y0, A1, A2, L, ph) in enumerate(curt):
        base_y = y0 * H + A1 * np.sin(XX / 700 + ph) + A2 * np.sin(XX / 260 + ph * 2)
        d = YY - base_y
        I = np.where(d < 0, np.exp(d / L), np.exp(-(d / 30) ** 2)) * rays * (0.9 - 0.15 * k)
        col = mix((60, 255, 150), (170, 70, 255), np.clip(-d / (1.3 * L), 0, 1))
        a += I[..., None] * col * 0.85
    a *= (0.55 + 0.45 * clock_dim(0.6))[..., None] ** 0.5
    base = arr_img(a)
    base.alpha_composite(alpha_mul(stars(rng, 260, 0, 0.75 * H, 4, flare=0.03), clock_dim(0.7)))
    rd = ((0.80 * H, 300), (0.89 * H, 220)) if DESK else ((0.76 * H, 520), (0.84 * H, 380))
    for (y0, amp), col, edge in zip(rd, ((6, 16, 34), (2, 8, 20)), ((60, 255, 150), (0, 200, 255))):
        R = ridge(rng, y0, amp, 24 if DESK else 15)
        add(base, svg([poly(R + [(W + 100, H + 10), (-100, H + 10)], fill=col, fo=1), line(R, edge, 4, 0.5)]), glows=((8, 0.6),))
    fx_logo(base, 1320, fx=(("neon", (60, 255, 170), 16, 50, 0.8),))
    footer(base, color=(160, 255, 210))
    return base


# ---------- 14. liquid gradient + glass ----------
def d_liquid():
    n1, n2 = fbm(141), fbm(142)
    X, Y = XX + 700 * (n1 - 0.5), YY + 700 * (n2 - 0.5)
    blobs = [((0.15, 0.10), (40, 90, 255)), ((0.85, 0.22), (160, 60, 255)), ((0.20, 0.50), (0, 210, 255)), ((0.90, 0.60), (255, 60, 170)),
             ((0.30, 0.88), (255, 150, 60)), ((0.80, 0.95), (90, 40, 230)), ((0.55, 0.40), (60, 120, 255))]
    num = np.zeros((H, W, 3), np.float32); den = np.zeros((H, W), np.float32)
    for (bx, by), c in blobs:
        w_ = np.exp(-((X - bx * W) ** 2 + (Y - by * H) ** 2) / (2 * 900 ** 2)) + 1e-4
        num += w_[..., None] * np.array(c, np.float32); den += w_
    base = arr_img(num / den[..., None])
    rng = np.random.default_rng(14); g = []
    for cx_, cy_, r in (((520, 430, 230), (3280, 1640, 300), (3450, 420, 120), (760, 1720, 150), (2620, 1960, 90)) if DESK else
                        ((350, 1500, 230), (1850, 3600, 300), (1750, 1350, 120), (300, 3900, 150), (1080, 4250, 90))):
        g.append(circle(cx_, cy_, r, fill=WHITE, fo=0.14, stroke=WHITE, w=4, so=0.55))
    for cx_, cy_, s_, an in (((3130, 980, 260, 18), (660, 1060, 220, -14)) if DESK else ((1880, 2100, 260, 18), (260, 2950, 220, -14))):
        g.append(poly(rot([(-s_, -s_ * 0.6), (s_, -s_ * 0.6), (s_, s_ * 0.6), (-s_, s_ * 0.6)], math.radians(an), (cx_, cy_)), fill=WHITE, fo=0.12, stroke=WHITE, w=4, so=0.5))
    add(base, svg(g), clock_dim(0.6))
    fx_logo(base, 1320, fx=(("glow", WHITE, 90, 0.45), ("holo", 0.55)), shadow=0.45)
    footer(base, color=WHITE)
    return base


# ---------- 15. pop art / comic ----------
def burst(cx, cy, r0, r1, n, rng, ph=0.0):
    return [(cx + (r1 if i % 2 == 0 else r0) * rng.uniform(0.88, 1.08) * math.cos(ph + math.pi * i / n),
             cy + (r1 if i % 2 == 0 else r0) * rng.uniform(0.88, 1.08) * math.sin(ph + math.pi * i / n)) for i in range(2 * n)]


def d_popart():
    rng = np.random.default_rng(15)
    ang = (np.arctan2(YY - CY, XX - CX) + math.pi) / (2 * math.pi) * 28
    a = np.where((ang.astype(int) % 2 == 0)[..., None], np.array((255, 205, 0), np.float32), np.array((255, 150, 0), np.float32))
    base = arr_img(a)
    dots = []
    for y in range(0, H + 60, 46):
        for x in range(0 if (y // 46) % 2 else 23, W + 46, 46):
            r = 3 + 17 * min(1, max(0, (math.hypot(x - CX, y - CY) - kk(700)) / 1900))
            if r > 3.5: dots.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#e8172d" fill-opacity="0.85"/>')
    add(base, svg(dots), clock_dim(0.35))
    b = [poly(burst(CX + 20, CY + 30, 760, 980, 18, rng), fill=(0, 0, 0)), poly(burst(CX, CY, 740, 950, 18, np.random.default_rng(15)), fill=WHITE, stroke=(0, 0, 0), w=18),
         poly(burst(CX, CY, 600, 760, 14, rng, 0.2), fill=(0, 160, 255), stroke=(0, 0, 0), w=12)]
    add(base, svg(kg(b)))
    fx_logo(base, 1180, fx=(("outline", (0, 0, 0), 18), ("hard", (0, 0, 0), 34, 34)), shadow=0)
    def comic(s, x, y, size, fill, angle):
        f = font(size, "Bold Condensed")
        bb = f.getbbox(s, stroke_width=size // 9)
        im = Image.new("RGBA", (bb[2] - bb[0] + 60, bb[3] - bb[1] + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((30 - bb[0] + 14, 30 - bb[1] + 14), s, font=f, fill=(0, 0, 0), stroke_width=size // 9, stroke_fill=(0, 0, 0))
        d.text((30 - bb[0], 30 - bb[1]), s, font=f, fill=fill, stroke_width=size // 9, stroke_fill=(0, 0, 0))
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
        base.alpha_composite(im, (round(x - im.width / 2), round(y - im.height / 2)))
    if DESK:
        comic("GO 8084!", 3080, 1720, 260, (255, 230, 0), 6)
        comic("ZAP!", 520, 420, 170, WHITE, 12)
        comic("BOOM!", 640, 1700, 150, (0, 200, 255), -10)
        return base
    comic("GO 8084!", CX, round(0.815 * H), 300, (255, 230, 0), 6)
    comic("ZAP!", 330, round(0.30 * H), 150, WHITE, 12)
    comic("BOOM!", 1800, round(0.715 * H), 130, (0, 200, 255), -10)
    return base


# ---------- 16. galaxy ----------
def d_galaxy():
    rng = np.random.default_rng(16)
    n1, n2, n3 = fbm(161), fbm(162), fbm(163, ((12, 1.0), (24, 0.5), (48, 0.3), (96, 0.15)))
    band = np.exp(-(((XX - CX) * 0.55 - (YY - CY) * 0.35) / 900) ** 2)
    c1 = np.clip((n1 - 0.4) / 0.6, 0, 1) ** 2 * band; c2 = np.clip((n2 - 0.45) / 0.55, 0, 1) ** 2 * band
    a = mix((6, 2, 22), (2, 2, 10), dist() / 2800)
    light(a, c1 * (0.6 + 0.6 * n3), (190, 50, 230)); light(a, c2 * (0.6 + 0.6 * n3), (40, 140, 255)); light(a, (c1 * c2) * 2.5, (255, 90, 170))
    base = arr_img(a)
    base.alpha_composite(alpha_mul(stars(rng, 600 if DESK else 520, 0, H, 4.5, flare=0.04), clock_dim(0.7)))
    pc = (3150, 560) if DESK else (1700, 1530)
    ring = [(pc[0] + 430 * math.cos(t_), pc[1] + 120 * math.sin(t_)) for t_ in np.linspace(0, 2 * math.pi, 181)]
    ringL = svg([line(rot([(x - pc[0], y - pc[1]) for x, y in ring], math.radians(-18), pc), (255, 200, 120), 22, 0.75, True)])
    sa = np.zeros((H, W, 4), np.uint8)
    lx = np.clip(((XX - pc[0]) * -0.6 + (YY - pc[1]) * -0.6) / 250 + 0.5, 0, 1)
    col = mix((60, 20, 110), (255, 120, 90), lx)
    sa[..., :3] = np.clip(col, 0, 255).astype(np.uint8); sa[..., 3] = ((dist(*pc) < 250) * 255).astype(np.uint8)
    back = alpha_mul(ringL, (YY < pc[1] - 0.3 * (XX - pc[0]) * 0.32).astype(np.float32))
    front = alpha_mul(ringL, (YY >= pc[1] - 0.3 * (XX - pc[0]) * 0.32).astype(np.float32))
    base.alpha_composite(back); base.alpha_composite(Image.fromarray(sa, "RGBA")); base.alpha_composite(front)
    fx_logo(base, 1320, fx=(("neon", (190, 90, 255), 14, 60, 0.9),))
    footer(base, color=(220, 180, 255))
    return base


# ---------- 17. electric ----------
def bolt(p0, p1, disp, depth, rng, out, branch=True):
    if depth == 0: out.append((p0, p1)); return
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
    m = (mx - dy / L * rng.normal(0, disp), my + dx / L * rng.normal(0, disp))
    bolt(p0, m, disp / 2, depth - 1, rng, out, branch); bolt(m, p1, disp / 2, depth - 1, rng, out, branch)
    if branch and depth > 3 and rng.random() < 0.35:
        a = math.atan2(dy, dx) + rng.choice((-1, 1)) * rng.uniform(0.3, 0.7)
        e = (m[0] + math.cos(a) * L * 0.5, m[1] + math.sin(a) * L * 0.5); sub = []
        bolt(m, e, disp / 2, depth - 2, rng, sub, False); out.extend(sub)


def d_electric():
    rng = np.random.default_rng(17)
    a = mix((60, 20, 170), (6, 2, 30), dist() / 2400)
    base = arr_img(a)
    segs = []
    for ang in np.linspace(0, 2 * math.pi, 9)[:-1] + 0.3:
        p0 = (CX + kk(640) * math.cos(ang), CY + kk(700) * math.sin(ang))
        p1 = (CX + 2600 * math.cos(ang + rng.uniform(-0.2, 0.2)), CY + 2600 * math.sin(ang + rng.uniform(-0.2, 0.2)))
        bolt(p0, p1, 260, 8, rng, segs)
    wide = svg([line([p, q], (0, 230, 255), 16, 0.9) for p, q in segs])
    core = svg([line([p, q], WHITE, 5, 1.0) for p, q in segs])
    m = clock_dim(0.5)
    add(base, wide, m, ((30, 1.4), (90, 1.0))); add(base, core, m, ((6, 1.0),))
    ring = svg([circle(CX, CY, 760, stroke=(140, 220, 255), w=10, so=0.9), circle(CX, CY, 820, stroke=(190, 120, 255), w=5, so=0.7)])
    if DESK: ring = svg(kg([circle(CX, CY, 760, stroke=(140, 220, 255), w=10, so=0.9), circle(CX, CY, 820, stroke=(190, 120, 255), w=5, so=0.7)]))
    add(base, ring, glows=((25, 1.5),))
    sp = [circle(rng.uniform(0, W), rng.uniform(0 if DESK else 0.25 * H, H), rng.uniform(3, 8), fill=(200, 250, 255)) for _ in range(90)]
    add(base, svg(sp), clear_zone(800, 900), ((10, 1.5),))
    fx_logo(base, 1300, fx=(("neon", (0, 230, 255), 12, 45, 1.0), ("neon", (255, 255, 255), 4, 10, 0.8)))
    footer(base, color=(160, 240, 255))
    return base


# ---------- 18. pixel arcade ----------
def d_pixel():
    P = 12; w, h = W // P, H // P
    im = Image.new("RGB", (w, h)); px = im.load()
    sky = [(40, 16, 90), (70, 24, 120), (120, 40, 150), (190, 60, 150), (250, 100, 120), (255, 160, 90)]
    rng = np.random.default_rng(18)
    hz = int(h * (0.76 if DESK else 0.70))
    for y in range(h):
        for x in range(w):
            t = y / hz * (len(sky) - 1)
            i = int(t); f = t - i
            c = sky[min(i + (1 if f > [0.2, 0.7, 0.45, 0.95][(x + 2 * y) % 4] else 0), len(sky) - 1)] if y < hz else ((40, 170, 70) if y < hz + 3 else ((150, 90, 50) if (x // 4 + y // 3) % 2 else (130, 76, 42)))
            px[x, y] = c
    d = ImageDraw.Draw(im)
    for x0, y0, wd in (((40, 34, 26), (250, 44, 30), (14, 80, 22), (282, 92, 18)) if DESK else ((6, 142, 26), (128, 158, 30), (40, 196, 22), (150, 222, 18))):
        for dx, dy, ww in ((0, 2, wd), (4, 0, wd - 8), (2, 4, wd - 4)):
            d.rectangle((x0 + dx, y0 + dy, x0 + dx + ww, y0 + dy + 3), fill=(255, 240, 250))
    for _ in range(40):
        x, y = rng.integers(0, w), rng.integers(0, int(h * 0.35)); d.point((x, y), fill=(255, 255, 200))
    for i in range(0, w + 40, 26):
        hh = rng.integers(16, 34); d.polygon([(i - 20, hz), (i, hz - hh), (i + 20, hz)], fill=(60, 30, 110))
    ROBOT = ["..XXXX..", "..XOOX..", "XXXXXXXX", "XBBBBBBX", "XB8BB8BX", "XBBBBBBX", "XXXXXXXX", ".X....X."]
    def sprite(x0, y0, body):
        for j, row in enumerate(ROBOT):
            for i, ch in enumerate(row):
                if ch == "X": d.point((x0 + i, y0 + j), fill=(30, 30, 40))
                elif ch == "O": d.point((x0 + i, y0 + j), fill=(0, 230, 255))
                elif ch in "B8": d.point((x0 + i, y0 + j), fill=body if ch == "B" else WHITE)
    for x0, c in (((30, (30, 100, 230)), (90, (230, 50, 60)), (226, (30, 100, 230)), (282, (230, 50, 60))) if DESK else
                  ((22, (30, 100, 230)), (80, (230, 50, 60)), (140, (30, 100, 230)))): sprite(x0, hz - 8, c)
    for x0 in range(40, w - 20, 22):
        d.rectangle((x0, hz - 22, x0 + 2, hz - 19), fill=(255, 210, 0)); d.point((x0 + 1, hz - 21), fill=(255, 250, 160))
    d.fontmode = "1"
    f = font(11, "Bold"); f2 = font(9, "Bold")
    ty = 5 if DESK else int(h * 0.275)
    d.text((8, ty), "1UP 8084", font=f, fill=WHITE)
    d.text((w - 8, ty), "HI 808400", font=f, fill=(255, 220, 0), anchor="ra")
    for i in range(3):
        hx_ = 8 + i * 10; hy = 19 if DESK else int(h * 0.31)
        for j, row in enumerate(["X.X.", "XXX.", ".X.."]):
            for k, ch in enumerate(row):
                if ch == "X": d.rectangle((hx_ + k * 2, hy + j * 2, hx_ + k * 2 + 1, hy + j * 2 + 1), fill=(255, 50, 80))
    d.text((w // 2, hz + 12 if DESK else int(h * 0.815)), "PRESS START", font=f, fill=WHITE, anchor="mm")
    d.text((w // 2, hz + 24 if DESK else int(h * 0.845)), "FRC TEAM 8084", font=f2, fill=(255, 220, 0), anchor="mm")
    base = im.resize((W, H), Image.NEAREST).convert("RGBA")
    fx_logo(base, 1320, cy=round(0.44 * H) if DESK else CY, fx=(("hard", (20, 10, 40), 36, 36), ("pixel", 12)), shadow=0)
    return base


# ---------- 19. stadium night ----------
def d_stadium():
    rng = np.random.default_rng(19)
    a = mix((14, 10, 40), (2, 2, 10), YY / H)
    def beam(ox, oy, ang, spread, color, k):
        dx, dy = XX - ox, YY - oy; r = np.hypot(dx, dy) + 1
        th = np.arctan2(dy, dx) - ang; th = (th + math.pi) % (2 * math.pi) - math.pi
        I = np.exp(-(th / spread) ** 2) * np.clip(1 - r / 5200, 0, 1) * k
        light(a, I, color)
    for ox, oy, ang, col in ((-100, 0.30 * H, math.radians(30), (0, 200, 255)), (W + 100, 0.30 * H, math.radians(150), (255, 60, 200)),
                             (300, H + 100, math.radians(-75), (255, 210, 0)), (W - 300, H + 100, math.radians(-105), (90, 255, 150)),
                             (CX, -100, math.radians(90), (180, 120, 255))):
        beam(ox, oy, ang, 0.09, col, 0.85)
    base = arr_img(a)
    cf = []; COLS = [(255, 60, 120), (255, 210, 0), (0, 210, 255), (120, 255, 120), (190, 110, 255), WHITE]
    for _ in range(420):
        x, y = rng.uniform(0, W), rng.uniform(0, H); s = rng.uniform(14, 34); an = rng.uniform(0, math.pi)
        cf.append(poly(rot([(-s, -s * 0.4), (s, -s * 0.4), (s, s * 0.4), (-s, s * 0.4)], an, (x, y)), fill=COLS[rng.integers(len(COLS))], fo=rng.uniform(0.6, 1)))
    add(base, svg(cf), clear_zone(650, 900) * clock_dim(0.35))
    crowd = []
    for row, (yb, rr, col) in enumerate((((0.92 if DESK else 0.905) * H, 70, (14, 10, 30)), ((0.97 if DESK else 0.95) * H, 85, (6, 4, 16)))):
        for x in np.arange(-40, W + 80, rr * 1.5):
            x += rng.uniform(-20, 20); hy = yb + rng.uniform(-20, 20)
            crowd.append(circle(x, hy - rr * 1.1, rr * 0.55, fill=col)); crowd.append(poly([(x - rr, hy), (x + rr, hy), (x + rr, H + 10), (x - rr, H + 10)], fill=col))
    lights = [circle(rng.uniform(0, W), rng.uniform((0.90 if DESK else 0.88) * H, 0.96 * H), rng.uniform(5, 9), fill=(255, 250, 220)) for _ in range(60 if DESK else 40)]
    base.alpha_composite(svg(crowd)); add(base, svg(lights), glows=((12, 1.5),))
    fx_logo(base, 1320, fx=(("glow", (255, 255, 255), 120, 0.5), ("neon", (255, 210, 0), 10, 40, 0.8)))
    footer(base, "ALFA ROBOTICS  ·  8084", y=CY + 660 if DESK else round(0.82 * H), color=(255, 230, 120))
    return base


# ---------- 20. memphis ----------
def d_memphis():
    rng = np.random.default_rng(20)
    base = arr_img(mix((30, 50, 190), (60, 20, 160), YY / H))
    COLS = [(255, 214, 0), (255, 90, 150), (0, 220, 200), (255, 140, 40), WHITE]
    s = []
    for _ in range(32 if DESK else 26):
        x, y = rng.uniform(0, W), rng.uniform(0, H); c = COLS[rng.integers(len(COLS))]; k = rng.integers(5); sz = rng.uniform(70, 170)
        if k == 0: s.append(poly(rot([(0, -sz), (sz * 0.87, sz * 0.5), (-sz * 0.87, sz * 0.5)], rng.uniform(0, 6), (x, y)), fill=c))
        elif k == 1: s.append(circle(x, y, sz * 0.6, fill=c))
        elif k == 2: s.append(circle(x, y, sz * 0.6, stroke=c, w=18))
        elif k == 3:
            q = [(x + i * 22, y + 40 * math.sin(i * 0.9)) for i in range(16)]
            s.append(line(rot([(px_ - x, py - y) for px_, py in q], rng.uniform(0, 6), (x, y)), c, 16))
        else:
            q = [(x + i * 40, y + (35 if i % 2 else -35)) for i in range(9)]
            s.append(line(rot([(px_ - x, py - y) for px_, py in q], rng.uniform(0, 6), (x, y)), c, 14))
    for gx, gy in (((200, 260), (3330, 1560)) if DESK else ((140, 1500), (1700, 3300))):
        for i in range(6):
            for j in range(6): s.append(circle(gx + i * 50, gy + j * 50, 9, fill=WHITE, fo=0.8))
    add(base, svg(s), clear_zone(720, 760) * clock_dim(0.12))
    fx_logo(base, 1300, fx=(("outline", (20, 20, 40), 14), ("hard", (255, 214, 0), 40, 40)), shadow=0)
    footer(base, color=WHITE)
    return base


DESIGNS2 = [("11 Synthwave", d_synthwave), ("12 Glitch", d_glitch), ("13 Kutup Isiklari", d_aurora), ("14 Sivi Renkler", d_liquid),
            ("15 Pop Art", d_popart), ("16 Galaksi", d_galaxy), ("17 Elektrik", d_electric), ("18 Piksel Oyun", d_pixel),
            ("19 Stadyum", d_stadium), ("20 Memphis", d_memphis)]

if __name__ == "__main__":
    pick = [int(a) for a in sys.argv[1:] if a.isdigit()] or range(11, 21)
    for i in pick:
        name, fn = DESIGNS2[i - 11]
        finish(fn(), name)
    if DESK: sys.exit()
    files = [OUT + f"ALFA 8084 - Duvar Kagidi {n}.jpg" for n, _ in DESIGNS2]
    if all(os.path.exists(f) for f in files):
        preview(files, OUT + "../duvar_onizleme_2.jpg")
