# ALFA Robotics 8084 animated phone wallpapers, set 2: 16 original designs, each a seamless 10 s loop,
# 1080 x 2340 (19.5:9), 30 fps, H.264 MP4. Frames are rendered in parallel (multiprocessing) and piped to ffmpeg.
# Usage: python hareketli2.py [names ...]          render videos (no name = all)
#        python hareketli2.py --test name f1,f2..   save single frames (frame numbers 0-299) for checking
import math, os, subprocess, sys, time
from multiprocessing import Pool
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, T = 1080, 2340, 30, 10.0
N = int(FPS * T)
NAVY, SKY, ICE, NEON, WHITE = (0, 58, 111), (99, 196, 242), (208, 233, 232), (40, 140, 255), (255, 255, 255)
ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/"
import guncel_logo
EMD = guncel_logo.pdf("Amblem", "Koyu zemin")
OUT = ROOT + "Hareketli Duvar Kagitlari/"
CX, CY = W / 2, round(0.535 * H)
TAU = 2 * math.pi
PAD = 200
BICUBIC, BILINEAR = Image.BICUBIC, Image.BILINEAR
_YY = _XX = None
def grid():
    global _YY, _XX
    if _YY is None: _YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
    return _YY, _XX


# ---------- general helpers ----------
def smooth(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
def bump(x, c, w):  # 0..1..0 around c, half width w
    return max(0.0, 1 - abs(x - c) / w) ** 2
def mix(c0, c1, t):
    t = np.clip(t, 0, 1)[..., None]; return np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
def arr_img(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
def rgba(rgb, a): return Image.fromarray(np.dstack([np.broadcast_to(np.clip(rgb, 0, 255), a.shape + (3,)), np.clip(a * 255, 0, 255)]).astype(np.uint8), "RGBA")
def solid(A, color, k=1.0):
    im = Image.new("RGBA", A.size, color + (255,)); im.putalpha(A.point(lambda v: int(min(255, v * k)))); return im
def fade(im, k):
    if k >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * max(0.0, k)))); return im
def blur(im, r): return im.filter(ImageFilter.GaussianBlur(r))
def paste(im, layer, x, y):
    """alpha_composite with clipping (PIL refuses negative destinations)."""
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(im.width, x + layer.width), min(im.height, y + layer.height)
    if x1 <= x0 or y1 <= y0: return
    im.alpha_composite(layer.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))
def put(im, layer, cx, cy, ang=0.0, k=1.0, sx=1.0, sy=None):
    sy = abs(sx) if sy is None else sy
    if abs(sx - 1) > 1e-3 or abs(sy - 1) > 1e-3:
        layer = layer.resize((max(1, round(layer.width * abs(sx))), max(1, round(layer.height * sy))), BILINEAR)
        if sx < 0: layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
    if abs(ang) > 1e-3: layer = layer.rotate(ang, resample=BICUBIC)
    layer = fade(layer, k)
    paste(im, layer, cx - layer.width / 2, cy - layer.height / 2)
def pad(im, p=PAD):
    c = Image.new(im.mode, (im.width + 2 * p, im.height + 2 * p), 0 if im.mode == "L" else (0, 0, 0, 0)); c.paste(im, (p, p)); return c
def dilate(A, n):
    for _ in range(n): A = A.filter(ImageFilter.MaxFilter(9))
    return A
def pnoise(w, h, cells, seed):
    """Noise that tiles in x and y (so it can scroll seamlessly). cells = ((cx, cy, amp), ...)."""
    r = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32)
    for cx_, cy_, amp in cells:
        s = r.random((cy_, cx_)).astype(np.float32)
        big = Image.fromarray(np.tile(s, (3, 3)), "F").resize((3 * w, 3 * h), BICUBIC)
        acc += amp * np.asarray(big)[h:2 * h, w:2 * w]
    acc -= acc.min(); return acc / acc.max()
def periodic_ridge(width, base, amps, seed):
    """Mountain line that repeats every `width` pixels (integer harmonics)."""
    r = np.random.default_rng(seed); xs = np.arange(width + 1)
    y = np.full(width + 1, float(base))
    for k, a in amps: y -= a * (0.6 + 0.4 * np.sin(TAU * k * xs / width + r.uniform(0, TAU)))
    return [(float(x), float(v)) for x, v in zip(xs[::6], y[::6])] + [(float(width), float(y[-1]))]

_LOGO = {}
def logo(width, path=EMD):
    key = (width, path)
    if key not in _LOGO:
        _LOGO[key] = guncel_logo.render(path, width)
    return _LOGO[key]
def neon(width, col=NEON, rim=(90, 200, 255), rimpx=2):
    L = logo(width); A = L.getchannel("A"); AP = pad(A)
    ring = dilate(AP, rimpx)
    return dict(L=L, LP=pad(L), AP=AP, RIM=solid(ring, rim), RIMG=blur(solid(ring, col), 24),
                BIG=blur(solid(AP, col), 100), SH=blur(solid(AP, (0, 0, 0), 0.85), 26))
def draw_logo(im, N_, cx, cy, ang=0.0, pulse=0.5, k=1.0, big=0.5, rim=True, sx=1.0, body=None):
    put(im, N_["BIG"], cx, cy, ang, k * (big * (0.6 + 0.6 * pulse)), sx)
    put(im, N_["SH"], cx, cy + 22, ang, k, sx)
    if rim:
        put(im, N_["RIMG"], cx, cy, ang, k * (0.5 + 0.5 * pulse), sx)
        put(im, N_["RIM"], cx, cy, ang, k * (0.7 + 0.3 * pulse), sx)
    put(im, N_["LP"] if body is None else body, cx, cy, ang, k, sx)
def icy_mask(L):
    a = np.asarray(L).astype(np.float32) / 255
    m = np.clip(1 - np.abs(a[..., :3] - np.array(ICE) / 255).sum(-1) / 0.25, 0, 1) * a[..., 3]
    return Image.fromarray((m * 255).astype(np.uint8), "L")

_FONT = {}
def font(size, var="SemiBold", mono=False):
    key = (size, var, mono)
    if key not in _FONT:
        if mono: _FONT[key] = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size)
        else:
            f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", size); f.set_variation_by_name(var); _FONT[key] = f
    return _FONT[key]
_FOOT = {}
def footer(im, color=ICE, y=None, label="FRC TEAM 8084"):
    key = (color, label)
    if key not in _FOOT:
        f = font(36); lay = Image.new("RGBA", (W, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        s = "   ".join(" ".join(w) for w in label.split()); tw = d.textlength(s, font=f)
        d.text((W / 2, 50), s, font=f, fill=color + (220,), anchor="mm")
        for sg in (-1, 1):
            x0 = W / 2 + sg * (tw / 2 + 36); d.line((x0, 50, x0 + sg * 170, 50), fill=color + (120,), width=3)
        _FOOT[key] = lay
    paste(im, _FOOT[key], 0, (round(0.845 * H) if y is None else y) - 50)
def stars(n, seed, y0=0, y1=H, rmax=3.0):
    r = np.random.default_rng(seed)
    return [(r.uniform(0, W), r.uniform(y0, y1), r.uniform(0.8, rmax), r.uniform(0, TAU), int(r.integers(1, 4))) for _ in range(n)]
def draw_stars(im, S, t, color=WHITE, k=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, r, ph, f in S:
        a = k * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(TAU * f * t + ph)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(255 * a),))
    im.alpha_composite(lay)
def bolt(p0, p1, disp, depth, r, out, branch=True):
    if depth == 0: out.append((p0, p1)); return
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
    m = (mx - dy / L * r.normal(0, disp), my + dx / L * r.normal(0, disp))
    bolt(p0, m, disp / 2, depth - 1, r, out, branch); bolt(m, p1, disp / 2, depth - 1, r, out, branch)
    if branch and depth > 3 and r.random() < 0.4:
        a = math.atan2(dy, dx) + r.choice((-1, 1)) * r.uniform(0.35, 0.8)
        bolt(m, (m[0] + math.cos(a) * L * 0.45, m[1] + math.sin(a) * L * 0.45), disp / 2, depth - 2, r, out, False)
def draw_bolts(segs, col=NEON, core=(230, 245, 255), w=10, cw=3):
    wide = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dw = ImageDraw.Draw(wide)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(c)
    for p, q in segs: dw.line((p, q), fill=col + (255,), width=w); dc.line((p, q), fill=core + (255,), width=cw)
    out = blur(wide, 30); out.alpha_composite(blur(wide, 7)); out.alpha_composite(c); return out


# ===================================================================================================
# designs: setup() -> state dict, frame(S, t) -> RGB image
# ===================================================================================================
D = {}
def design(name):
    def reg(cls): D[name] = cls; return cls
    return reg


# ---------- 01 howl: sound-wave rings pour out of the howling wolf's muzzle in the logo, equalizer answers ----------
@design("01 Uluma Dalgasi")
class Uluma:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((8, 30, 76), (0, 3, 12), np.clip(np.hypot(XX - CX, YY - CY) / 1400, 0, 1)))
        self.st = stars(150, 21, 0, H, 2.2)
        self.N = neon(620); L = self.N["L"]
        self.M = (CX - L.width / 2 + 0.80 * L.width, CY - L.height / 2 + 0.07 * L.height)   # muzzle tip
        self.nb = 27
    def frame(self, t):
        im = self.base.copy(); draw_stars(im, self.st, t)
        mx, my = self.M
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        lvl = 0.0
        for j in range(6):                                   # two howls per loop, 6 rings each
            u = (t * 2 + j / 6) % 1.0; r = 40 + 1500 * u; a = (1 - u) ** 1.5
            lvl += a / 6
            d.arc((mx - r, my - r, mx + r, my + r), 195, 345, fill=(170, 230, 255, int(255 * a)), width=max(4, int(22 * (1 - u))))
        im.alpha_composite(blur(lay, 18)); im.alpha_composite(blur(lay, 6)); im.alpha_composite(lay)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 4 * t), big=0.6 + 0.6 * lvl)
        eq = Image.new("RGBA", (W, H), (0, 0, 0, 0)); de = ImageDraw.Draw(eq)
        y0 = round(0.78 * H); bw = W / self.nb
        for i in range(self.nb):
            c = abs(i - self.nb // 2) / (self.nb // 2)
            h = 30 + 260 * (1 - 0.6 * c) * (0.5 + 0.5 * math.sin(TAU * (2 * t) - c * 5 + i * 0.7)) * (0.6 + 0.4 * math.sin(TAU * 3 * t + i))
            x = i * bw + bw * 0.18
            for k in range(int(h // 22)):
                yy = y0 - k * 22; f = k * 22 / 290
                col = (int(60 + 180 * f), int(160 + 80 * f), 255)
                de.rectangle((x, yy - 16, x + bw * 0.64, yy), fill=col + (230,))
        im.alpha_composite(blur(eq, 12)); im.alpha_composite(eq)
        footer(im, y=round(0.84 * H))
        return im


# ---------- 02 neon tunnel: hexagon rings rush towards the viewer around the logo ----------
@design("02 Neon Tunel")
class Tunel:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((10, 20, 60), (0, 1, 8), np.clip(np.hypot(XX - CX, YY - CY) / 900, 0, 1) ** 0.6))
        self.N = neon(560)
        self.n = 16
    def frame(self, t):
        im = self.base.copy()
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for j in range(self.n):
            z = (j + 1 - (t * 4) % 1.0) / self.n * 4.0 + 0.12      # 4 rings pass per second-ish, loop-exact
            s = 330 / z
            if s > 2400: continue
            rot = math.radians(30 * math.sin(TAU * t) + 6 * z)
            a = min(1.0, (4.1 - z) / 1.2) * min(1.0, s / 300)
            hue = 0.5 + 0.5 * math.sin(2.2 * z)
            col = (int(60 + 180 * hue), int(120 + 60 * (1 - hue)), 255)
            pts = [(CX + s * math.cos(rot + k * TAU / 6), CY + s * 1.15 * math.sin(rot + k * TAU / 6)) for k in range(7)]
            d.line(pts, fill=col + (int(255 * a),), width=max(2, int(s / 45)))
            for k in range(6):
                x, y = pts[k]; r = max(3, s / 40); d.ellipse((x - r, y - r, x + r, y + r), fill=(230, 245, 255, int(255 * a)))
        im.alpha_composite(blur(lay, 16)); im.alpha_composite(lay)
        draw_logo(im, self.N, CX, CY, ang=3 * math.sin(TAU * t), pulse=0.5 + 0.5 * math.sin(TAU * 4 * t), big=0.9)
        footer(im)
        return im



# ---------- 03 hyperspace: star streaks rush past, the logo shakes with speed ----------
@design("03 Hiper Hiz")
class Hiper:
    def setup(self):
        YY, XX = grid(); d = np.hypot(XX - CX, YY - CY)
        self.base = arr_img(mix((10, 24, 70), (0, 2, 10), np.clip(d / 1300, 0, 1) ** 0.7))
        r = np.random.default_rng(3); n = 650
        self.S = list(zip(r.uniform(0, TAU, n), r.uniform(0, 1, n), r.integers(1, 3, n), r.random(n) < 0.3))
        self.N = neon(600)
    def frame(self, t):
        im = self.base.copy()
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for th, z0, k, blue in self.S:
            z = (z0 - k * t) % 1.0; D0 = 0.04 + z; D1 = D0 + 0.05 * k
            r0, r1 = 90 / D0, 90 / D1
            if r1 > 1500: continue
            c, s = math.cos(th), math.sin(th); a = min(1, (1 - z) * 1.3)
            col = (120, 190, 255) if blue else (225, 240, 255)
            d.line((CX + c * r1, CY + s * r1, CX + c * min(r0, 2600), CY + s * min(r0, 2600)), fill=col + (int(255 * a),), width=max(1, int(1 + 4 * (1 - z))))
        im.alpha_composite(blur(lay, 6)); im.alpha_composite(lay)
        rr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(rr)
        for j in range(3):
            u = (t * 3 + j / 3) % 1; R = 300 + 1100 * u
            dr.ellipse((CX - R, CY - R, CX + R, CY + R), outline=SKY + (int(150 * (1 - u)),), width=6)
        im.alpha_composite(blur(rr, 8))
        sh = 5 * math.sin(TAU * 17 * t), 4 * math.sin(TAU * 23 * t + 1)
        draw_logo(im, self.N, CX + sh[0], CY + sh[1], pulse=0.5 + 0.5 * math.sin(TAU * 4 * t), big=0.9)
        footer(im)
        return im


# ---------- 04 circuit energy: light pulses race along traces into the logo ----------
@design("04 Devre Enerjisi")
class Devre:
    def setup(self):
        YY, XX = grid(); d = np.hypot(XX - CX, YY - CY)
        self.base = arr_img(mix((0, 34, 70), (0, 6, 18), np.clip(d / 1500, 0, 1)))
        r = np.random.default_rng(4); self.tr = []
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
        for i in range(44):
            th = TAU * i / 44 + r.uniform(-0.05, 0.05); E = (CX + 440 * math.cos(th), CY + 470 * math.sin(th))
            far = 2600; S = (CX + far * math.cos(th), CY + far * math.sin(th))
            S = (min(max(S[0], -20), W + 20), min(max(S[1], -20), H + 20))
            if abs(S[0] - E[0]) > abs(S[1] - E[1]):
                c = abs(S[1] - E[1]); mid = (E[0] + math.copysign(c, S[0] - E[0]), S[1])
            else:
                c = abs(S[0] - E[0]); mid = (S[0], E[1] + math.copysign(c, S[1] - E[1]))
            pts = [S, mid, E]; L = [0]
            for a, b in zip(pts, pts[1:]): L.append(L[-1] + math.dist(a, b))
            self.tr.append((pts, L, int(r.integers(1, 4)), r.uniform(0, 1)))
            dg.line(pts, fill=(40, 110, 200, 150), width=5); dg.ellipse((E[0] - 9, E[1] - 9, E[0] + 9, E[1] + 9), fill=(10, 30, 60, 255), outline=(80, 170, 255, 220), width=3)
        self.base.alpha_composite(blur(g, 6)); self.base.alpha_composite(g)
        self.N = neon(600)
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ring)
        for k in range(36):
            a = TAU * k / 36; x, y = CX + 520 * math.cos(a), CY + 520 * math.sin(a); dr.ellipse((x - 7, y - 7, x + 7, y + 7), fill=SKY + (200,))
        dr.ellipse((CX - 440, CY - 470, CX + 440, CY + 470), outline=(80, 170, 255, 160), width=4)
        self.ring = ring
    def pos(self, pts, L, u):
        s = u * L[-1]
        for i in range(len(pts) - 1):
            if s <= L[i + 1]:
                f = (s - L[i]) / max(1e-6, L[i + 1] - L[i]); return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
        return pts[-1]
    def frame(self, t):
        im = self.base.copy()
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); hits = 0
        for pts, L, k, ph in self.tr:
            u = (t * k + ph) % 1.0
            hits += math.exp(-((1 - u) * 18)) if u > 0.9 else 0
            q = [self.pos(pts, L, max(0, u - j * 0.012)) for j in range(10)]
            d.line(q, fill=(120, 210, 255, 255), width=6)
            x, y = q[0]; d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(235, 248, 255, 255))
        im.alpha_composite(blur(lay, 14)); im.alpha_composite(lay)
        put(im, self.ring, CX, CY, ang=30 * t, k=0.9)
        draw_logo(im, self.N, CX, CY, pulse=min(1, 0.4 + hits * 0.25))
        footer(im)
        return im


# ---------- 05 meshing gears turning around the logo ----------
def gear_poly(R, N_, dep, ph, cx, cy):
    p = TAU / N_; q = []
    for k in range(N_):
        a0 = ph + k * p
        for f, r in ((0, R - dep), (0.2, R - dep), (0.4, R - dep), (0.5, R), (0.7, R), (0.9, R)):
            q.append((cx + r * math.cos(a0 + f * p), cy + r * math.sin(a0 + f * p)))
    return q
@design("05 Disli Mekanizma")
class Disli:
    def setup(self):
        YY, XX = grid(); d = np.hypot(XX - CX, YY - CY)
        self.base = arr_img(mix((4, 40, 84), (0, 8, 22), np.clip(d / 1600, 0, 1)))
        pitch = TAU * 560 / 36
        def gear(N_, holes, ph, col):
            R = N_ * pitch / TAU; s = int(2 * R + 40); c = s / 2
            m = Image.new("L", (2 * s, 2 * s), 0); dm = ImageDraw.Draw(m)
            dm.polygon([(x * 2, y * 2) for x, y in gear_poly(R, N_, 70, ph, c, c)], fill=255)
            dm.ellipse(((c - R * 0.16) * 2, (c - R * 0.16) * 2, (c + R * 0.16) * 2, (c + R * 0.16) * 2), fill=0)
            for j in range(holes):
                a = ph + j * TAU / holes; hx, hy, hr = c + 0.56 * R * math.cos(a), c + 0.56 * R * math.sin(a), R * 0.17
                dm.ellipse(((hx - hr) * 2, (hy - hr) * 2, (hx + hr) * 2, (hy + hr) * 2), fill=0)
            m = m.resize((s, s), Image.LANCZOS)
            body = solid(m, tuple(int(c * 0.8) for c in col), 1.0); edge = solid(Image.fromarray(np.clip(np.asarray(dilate(m, 1), np.int16) - np.asarray(m.filter(ImageFilter.MinFilter(5)), np.int16), 0, 255).astype(np.uint8)), (110, 190, 255))
            body.alpha_composite(edge); return body
        self.G = [(gear(36, 6, 0.0, (14, 52, 104)), CX, CY, 1.0)]
        ph1 = 0.0
        for th, N_ in ((math.radians(-120), 18), (math.radians(-35), 12), (math.radians(60), 24), (math.radians(140), 18), (math.radians(100), 12)):
            R = N_ * pitch / TAU; dd = 560 + R - 70
            f1 = ((th - ph1) / (TAU / 36)) % 1; f2 = 0.7 - (f1 - 0.2); ph = th + math.pi - f2 * TAU / N_
            if N_ == 12 and th > 1.5: dd = 560 + 24 * pitch / TAU * 2 - 140 + R - 70 + 0; continue
            self.G.append((gear(N_, 6 if N_ != 24 else 4, ph, (10, 40, 86) if N_ % 12 == 0 else (18, 60, 116)), CX + dd * math.cos(th), CY + dd * math.sin(th), -36 / N_))
        self.N = neon(600)
    def frame(self, t):
        im = self.base.copy()
        for g, x, y, ratio in self.G:
            put(im, g, x, y, ang=-60 * t * ratio)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 2 * t))
        footer(im)
        return im


# ---------- 06 radar sweep ----------
@design("06 Radar")
class Radar:
    def setup(self):
        YY, XX = grid(); d = np.hypot(XX - CX, YY - CY); self.R = R = 500
        self.base = arr_img(mix((0, 30, 40), (0, 6, 12), np.clip(d / 1400, 0, 1)))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g); C = (60, 230, 200)
        for r in (R * 0.25, R * 0.5, R * 0.75, R): dg.ellipse((CX - r, CY - r, CX + r, CY + r), outline=C + (110,), width=3)
        dg.line((CX - R, CY, CX + R, CY), fill=C + (70,), width=2); dg.line((CX, CY - R, CX, CY + R), fill=C + (70,), width=2)
        for k in range(72):
            a = TAU * k / 72; L = 26 if k % 6 == 0 else 12
            dg.line((CX + R * math.cos(a), CY + R * math.sin(a), CX + (R + L) * math.cos(a), CY + (R + L) * math.sin(a)), fill=C + (160,), width=3)
        for x in range(0, W, 90): dg.line((x, 0, x, H), fill=C + (14,), width=1)
        for y in range(0, H, 90): dg.line((0, y, W, y), fill=C + (14,), width=1)
        self.base.alpha_composite(blur(g, 4)); self.base.alpha_composite(g)
        s = 2 * R; yy, xx = np.mgrid[0:s, 0:s].astype(np.float32) - R
        ang = (np.degrees(np.arctan2(yy, xx)) % 360); rr = np.hypot(xx, yy)
        wedge = np.clip(1 - ang / 100, 0, 1) ** 2.2 * (rr < R) * 0.55 + (ang > 357) * (rr < R) * 0.9
        self.W_ = rgba(np.array(C, np.float32), wedge)
        r = np.random.default_rng(6); self.B = [(r.uniform(0.35, 0.95) * R, r.uniform(0, 360)) for _ in range(14)]
        self.N = neon(520, col=(40, 200, 180), rim=(120, 255, 220)); self.C = C
    def frame(self, t):
        im = self.base.copy(); sw = (720 * t) % 360
        put(im, self.W_, CX, CY, ang=-sw)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for r, a in self.B:
            since = (sw - a) % 360; k = math.exp(-since / 110)
            x, y = CX + r * math.cos(math.radians(a)), CY + r * math.sin(math.radians(a)); s = 10 + 8 * k
            d.ellipse((x - s, y - s, x + s, y + s), fill=(160, 255, 220, int(255 * k)))
        im.alpha_composite(blur(lay, 10)); im.alpha_composite(lay)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 2 * t), big=0.4)
        f = font(30, mono=True); d2 = ImageDraw.Draw(im)
        d2.text((70, CY + 640), f"AZİMUT {sw:05.1f}°", font=f, fill=self.C + (220,))
        d2.text((W - 70, CY + 640), "HEDEF: 8084", font=f, fill=self.C + (220,), anchor="ra")
        footer(im, color=(170, 255, 230))
        return im


# ---------- 07 code rain ----------
@design("07 Kod Yagmuru")
class Kod:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((0, 10, 26), (0, 2, 8), YY / H))
        self.cell = 40; self.cols = W // 36
        chars = "01ALF8048ABCDEF"
        f = font(36, mono=True)
        self.G = {}
        for ch in set(chars):
            for lvl in range(8):
                a = (lvl + 1) / 8; im = Image.new("RGBA", (40, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                col = (230, 250, 255) if lvl == 7 else (60, int(140 + 100 * a), 255)
                d.text((20, 23), ch, font=f, fill=col + (int(255 * a),), anchor="mm"); self.G[(ch, lvl)] = im
        r = np.random.default_rng(7)
        self.C = [(r.uniform(0, 1), int(r.integers(1, 4)), int(r.integers(12, 30))) for _ in range(self.cols)]
        self.chars = chars; self.rows = H // self.cell + 1
        self.grid_ch = r.integers(0, len(chars), (self.cols, self.rows + 40))
        self.N = neon(600)
    def frame(self, t):
        im = self.base.copy(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fi = int(t * N)
        span = self.rows + 30
        for c, (ph, k, L) in enumerate(self.C):
            head = ((ph + k * t) % 1.0) * span
            for j in range(L):
                row = int(head) - j
                if row < 0 or row >= self.rows: continue
                lvl = 7 if j == 0 else max(0, int(6 * (1 - j / L)))
                idx = self.grid_ch[c, row] if (row * 7 + c + fi // 4) % 11 else (self.grid_ch[c, row] + fi // 4) % len(self.chars)
                lay.alpha_composite(self.G[(self.chars[idx], lvl)], (c * 36 + 2, row * self.cell))
        im.alpha_composite(blur(lay, 5)); im.alpha_composite(lay)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 2 * t), big=0.9)
        footer(im)
        return im


# ---------- 08 plasma globe: arcs crackle from the logo to the glass ----------
@design("08 Plazma Kure")
class Plazma:
    def setup(self):
        YY, XX = grid(); d = np.hypot(XX - CX, YY - CY); self.R = R = 560
        a = mix((40, 10, 90), (2, 0, 12), np.clip(d / 1300, 0, 1) ** 0.8)
        a += (np.exp(-((d - R) / 18) ** 2) * 70)[..., None] * np.array((0.6, 0.6, 1.0))
        a += (np.clip(1 - d / R, 0, 1) ** 0.5 * 25)[..., None] * np.array((0.5, 0.3, 1.0))
        self.base = arr_img(a)
        hl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(hl).arc((CX - R + 50, CY - R + 50, CX + R - 50, CY + R - 50), 200, 250, fill=(255, 255, 255, 120), width=26)
        self.base.alpha_composite(blur(hl, 14))
        r = np.random.default_rng(8); self.A = [(r.uniform(0, TAU), r.uniform(0, TAU), int(r.integers(1, 3))) for _ in range(9)]
        self.N = neon(560, col=(160, 80, 255), rim=(220, 180, 255))
    def frame(self, t):
        im = self.base.copy(); fi = int(t * N)
        segs = []; spots = []
        for i, (a0, ph, k) in enumerate(self.A):
            a = a0 + 0.7 * math.sin(TAU * k * t + ph)
            p0 = (CX + 300 * math.cos(a), CY + 320 * math.sin(a)); p1 = (CX + (self.R - 8) * math.cos(a + 0.15), CY + (self.R - 8) * math.sin(a + 0.15))
            bolt(p0, p1, 60, 6, np.random.default_rng(i * 1000 + fi // 2), segs); spots.append(p1)
        b = draw_bolts(segs, col=(180, 110, 255), core=(245, 235, 255), w=14, cw=4); im.alpha_composite(b); im.alpha_composite(blur(b, 20))
        sp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sp)
        for x, y in spots: ds.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(230, 200, 255, 220))
        im.alpha_composite(blur(sp, 16))
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 3 * t), big=0.8)
        footer(im, color=(220, 200, 255))
        return im


# ---------- 09 hologram: the logo turns in the light of a projector ----------
@design("09 Hologram")
class Holo:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((0, 16, 30), (0, 3, 8), np.clip(np.hypot(XX - CX, YY - CY) / 1400, 0, 1)))
        self.BY = BY = round(0.80 * H)
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
        for k in range(-12, 13): dg.line((CX + k * 30, BY + 40, CX + k * 160, H), fill=(40, 200, 255, 50), width=2)
        for j in range(12): y = BY + 40 + j * j * 7; dg.line((0, y, W, y), fill=(40, 200, 255, 40), width=2)
        dg.ellipse((CX - 300, BY - 40, CX + 300, BY + 70), fill=(10, 40, 70, 255), outline=(80, 220, 255, 255), width=6)
        dg.ellipse((CX - 200, BY - 20, CX + 200, BY + 40), fill=(60, 200, 255, 160))
        self.base.alpha_composite(blur(g, 6)); self.base.alpha_composite(g)
        cone = np.zeros((H, W), np.float32); yy, xx = grid()
        top, bot = CY - 300, BY
        u = np.clip((yy - top) / (bot - top), 0, 1); half = 330 * (1 - u) + 200 * u
        cone = (np.abs(xx - CX) < half) * ((yy > top) & (yy < bot)) * (0.10 + 0.25 * u)
        self.cone = blur(rgba(np.array((80, 210, 255), np.float32), cone), 20)
        L = logo(600); a = np.asarray(L).astype(np.float32); lum = (a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11) / 255
        rgb = np.array((40, 150, 255), np.float32) * (1 - lum[..., None]) + np.array((200, 250, 255), np.float32) * lum[..., None]
        al = a[..., 3] / 255 * 0.85 * (1 - 0.4 * ((np.arange(L.height)[:, None] % 6) < 2))
        self.HL = pad(rgba(rgb, al)); self.HG = blur(solid(pad(L.getchannel("A")), (60, 200, 255)), 30)
    def frame(self, t):
        im = self.base.copy(); im.alpha_composite(fade(self.cone, 0.85 + 0.15 * math.sin(TAU * 6 * t)))
        sx = math.cos(math.radians(55 * math.sin(TAU * t))); body = self.HL
        k = 0.82 + 0.12 * math.sin(TAU * 13 * t) + 0.06 * math.sin(TAU * 29 * t)
        g = bump(t, 0.25, 0.015) + bump(t, 0.76, 0.015)
        if g > 0.05:
            arr = np.asarray(body).copy(); r = np.random.default_rng(int(t * N))
            for _ in range(6):
                y0 = int(r.integers(0, arr.shape[0] - 40)); arr[y0:y0 + 30] = np.roll(arr[y0:y0 + 30], int(r.integers(-40, 40)), axis=1)
            body = Image.fromarray(arr, "RGBA")
        cy = CY - 40 + 12 * math.sin(TAU * 2 * t)
        put(im, self.HG, CX, cy, k=0.7 * k, sx=sx, sy=1.0)
        put(im, body, CX, cy, k=k, sx=sx, sy=1.0)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for j, (ry, rx, sp) in enumerate(((cy - 330, 380, 1), (cy + 20, 470, -1), (cy + 360, 400, 2))):
            d.ellipse((CX - rx, ry - rx * 0.16, CX + rx, ry + rx * 0.16), outline=(80, 220, 255, 90), width=3)
            for q in range(10):
                a = TAU * (q / 10 + sp * t); d.ellipse((CX + rx * math.cos(a) - 6, ry + rx * 0.16 * math.sin(a) - 6, CX + rx * math.cos(a) + 6, ry + rx * 0.16 * math.sin(a) + 6), fill=(160, 240, 255, int(140 + 100 * math.sin(a))))
        im.alpha_composite(blur(lay, 4)); im.alpha_composite(lay)
        footer(im, color=(150, 230, 255), y=round(0.90 * H))
        return im


# ---------- 10 aurora that flows ----------
@design("10 Kutup Isiklari")
class Aurora:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((1, 4, 18), (4, 26, 52), YY / H))
        self.st = stars(200, 10, 0, 0.75 * H, 2.4)
        self.h, self.w = H // 2, W // 2
        self.yy, self.xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        r = np.random.default_rng(10); self.rays = np.asarray(Image.fromarray(np.tile(r.random((1, 90)).astype(np.float32), (1, 3)), "F").resize((3 * self.w, self.h), BICUBIC))
        mt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(mt)
        for base_y, amps, seed, col, edge in ((0.78 * H, ((1, 120), (3, 60), (7, 20)), 1, (6, 16, 34), (60, 255, 150)), (0.86 * H, ((2, 80), (5, 25)), 2, (2, 8, 20), (0, 200, 255))):
            R = periodic_ridge(W, base_y, amps, seed); d.polygon(R + [(W, H), (0, H)], fill=col + (255,)); d.line(R, fill=edge + (130,), width=3)
        self.mt = mt; self.N = neon(600, col=(40, 220, 160), rim=(150, 255, 210))
    def frame(self, t):
        im = self.base.copy(); draw_stars(im, self.st, t)
        a = np.zeros((self.h, self.w, 3), np.float32); xx, yy = self.xx, self.yy
        for k, (y0, A1, A2, L, f1, f2, ph) in enumerate(((0.30, 70, 30, 380, 1, 2, 0.3), (0.40, 90, 40, 460, 2, 1, 2.1), (0.50, 60, 25, 300, 1, 3, 4.0))):
            by = y0 * self.h + A1 * np.sin(TAU * (xx / self.w * 1.5) + ph + TAU * f1 * t) + A2 * np.sin(TAU * (xx / self.w * 4) + ph * 2 - TAU * f2 * t)
            dd = yy - by
            off = int((t * (k + 1)) * self.w) % self.w
            rays = 0.35 + 0.65 * self.rays[:, off:off + self.w]
            I = np.where(dd < 0, np.exp(dd / L), np.exp(-(dd / 14) ** 2)) * rays * (0.9 - 0.15 * k)
            a += I[..., None] * mix((60, 255, 150), (170, 70, 255), np.clip(-dd / (1.3 * L), 0, 1)) * 0.85
        au = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").resize((W, H), BICUBIC)
        im = Image.fromarray(np.clip(np.asarray(im.convert("RGB"), np.int16) + np.asarray(au, np.int16), 0, 255).astype(np.uint8)).convert("RGBA")
        im.alpha_composite(self.mt)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 2 * t))
        footer(im, color=(170, 255, 215), y=round(0.92 * H))
        return im


# ---------- 11 synthwave drive: the grid rushes towards you ----------
@design("11 Synthwave Yolu")
class Synth:
    def setup(self):
        YY, XX = grid(); self.HZ = HZ = round(0.66 * H)
        tt = np.clip(YY / HZ, 0, 1)
        a = np.where((tt < 0.55)[..., None], mix((18, 4, 48), (110, 18, 120), tt / 0.55), mix((110, 18, 120), (255, 96, 110), (tt - 0.55) / 0.45))
        a = np.where((YY > HZ)[..., None], mix((40, 6, 70), (8, 2, 24), (YY - HZ) / (H - HZ)), a)
        self.base = arr_img(a); self.st = stars(120, 11, 0, HZ - 600, 2.2)
        self.sc, self.sr = (CX, 0.50 * H), 520
        d = np.hypot(XX - self.sc[0], YY - self.sc[1]); st = (YY - (self.sc[1] - self.sr)) / (2 * self.sr)
        self.sun = rgba(mix((255, 236, 90), (255, 40, 150), st * 1.15), ((d < self.sr) & (YY < HZ)).astype(np.float32))
        self.sung = blur(solid(self.sun.getchannel("A"), (255, 80, 160)), 60)
        R = [(x, y + (HZ - y) * (1 - min(1, abs(x - CX) / 560) ** 2) * 0.95) for x, y in periodic_ridge(W, HZ, ((1, 160), (3, 90), (6, 40)), 5)]
        mt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dm = ImageDraw.Draw(mt)
        dm.polygon(R + [(W, HZ + 2), (0, HZ + 2)], fill=(30, 6, 60, 255)); dm.line(R, fill=(0, 240, 255, 230), width=4)
        self.mt = mt; self.N = neon(560, col=(255, 60, 200), rim=(255, 170, 240))
    def frame(self, t):
        im = self.base.copy(); draw_stars(im, self.st, t); HZ = self.HZ
        sun = self.sun.copy(); a = np.asarray(sun.getchannel("A")).copy()
        yy = np.arange(H)[:, None]; yb = yy - (self.sc[1] + 20); sh = (yb - 80 * t * 2) % 80
        gap = 4 + 36 * np.clip(yb / (0.9 * self.sr), 0, 1)
        a[((yb > 0) & (sh < gap))[:, 0]] = 0; sun.putalpha(Image.fromarray(a))
        im.alpha_composite(fade(self.sung, 0.8)); im.alpha_composite(sun); im.alpha_composite(self.mt)
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g); C = (255, 60, 220, 230)
        for k in range(-16, 17): d.line((CX + k * 14, HZ, CX + k * 300, H + 20), fill=C, width=4)
        for j in range(40):
            z = j + 1 - (t * 6) % 1.0
            y = HZ + 1500 / (z + 0.4)
            if HZ < y < H + 10: d.line((0, y, W, y), fill=C, width=max(2, int(6 * (y - HZ) / (H - HZ))))
        im.alpha_composite(blur(g, 10)); im.alpha_composite(g)
        draw_logo(im, self.N, CX, round(0.40 * H), pulse=0.5 + 0.5 * math.sin(TAU * 2 * t), big=0.8)
        footer(im, color=(0, 240, 255), y=round(0.92 * H))
        return im


# ---------- 12 particle logo: falls apart into a swirl and assembles again ----------
@design("12 Parcacik Logo")
class Parca:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((8, 20, 60), (0, 3, 12), np.clip(np.hypot(XX - CX, YY - CY) / 1400, 0, 1)))
        self.N = neon(620); L = self.N["L"]; a = np.asarray(L)
        ys, xs = np.nonzero(a[::3, ::3, 3] > 200); ys, xs = ys * 3, xs * 3
        self.col = a[ys, xs, :3].astype(np.float32)
        self.hx = CX - L.width / 2 + xs; self.hy = CY - L.height / 2 + ys
        r = np.random.default_rng(12); n = len(xs)
        ang = np.arctan2(self.hy - CY, self.hx - CX) + r.normal(0, 0.5, n); self.ang = ang
        self.rad = r.uniform(60, 420, n); self.sp = r.uniform(0.6, 1.6, n); self.ph = r.uniform(0, TAU, n)
    def frame(self, t):
        im = self.base.copy()
        e = smooth(0.36, 0.55, t) * (1 - smooth(0.70, 0.90, t))
        lk = 1 - smooth(0.34, 0.40, t) + smooth(0.88, 0.94, t)
        pulse = 0.5 + 0.5 * math.sin(TAU * 2 * t)
        if e > 0.001 or (0.3 < t < 0.95):
            sw = e * 2.2 * self.sp
            dx, dy = self.hx - CX, self.hy - CY
            r0 = np.hypot(dx, dy) + e * self.rad; a0 = np.arctan2(dy, dx) + sw
            x = CX + r0 * np.cos(a0) + e * 40 * np.sin(TAU * 2 * t + self.ph); y = CY + r0 * np.sin(a0) + e * 40 * np.cos(TAU * 2 * t + self.ph)
            ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
            acc = np.zeros((H, W, 3), np.float32)
            col = self.col * (1 - e * 0.5) + np.array(SKY, np.float32) * e * 0.5
            xi, yi = x[ok].astype(int), y[ok].astype(int)
            for ox, oy in ((0, 0), (1, 0), (0, 1), (1, 1)): np.add.at(acc, (yi + oy, xi + ox), col[ok])
            pa = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), "RGB")
            glow = pa.filter(ImageFilter.GaussianBlur(8))
            base = np.asarray(im.convert("RGB"), np.int16)
            pk = 1 - lk * 0.85
            out = base + (np.asarray(pa, np.int16) * pk + np.asarray(glow, np.int16) * 1.2 * pk).astype(np.int16)
            im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        if lk > 0.01: draw_logo(im, self.N, CX, CY, pulse=pulse, k=min(1, lk))
        footer(im)
        return im


# ---------- 13 blue flames ----------
@design("13 Mavi Alev")
class Alev:
    def setup(self):
        self.h, self.w = H // 2, W // 2
        self.n1 = pnoise(self.w, self.h, ((10, 6, 1.0), (20, 12, 0.5), (40, 24, 0.25), (80, 48, 0.12)), 1)
        self.n2 = pnoise(self.w, self.h, ((14, 8, 1.0), (28, 16, 0.5), (56, 32, 0.25)), 2)
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        sh = np.clip((yy / self.h - 0.30) / 0.55, 0, 1) ** 0.7 * 1.05
        L = logo(600); LA = pad(L.getchannel("A"), 120); A = np.asarray(blur(dilate(LA, 3), 30).resize((LA.width // 2, LA.height // 2)), np.float32) / 255
        m = np.zeros((self.h, self.w), np.float32); y0 = int(CY / 2 - A.shape[0] / 2) - 30; x0 = int(CX / 2 - A.shape[1] / 2)
        m[y0:y0 + A.shape[0], x0:x0 + A.shape[1]] = A
        for k in range(1, 14): m = np.maximum(m, np.roll(m, -14, axis=0) * 0.93)
        self.shape = np.clip(sh + m * 1.3, 0, 1.4)
        lut = np.zeros((256, 3), np.float32); stops = [(0, (0, 0, 0)), (0.25, (0, 20, 90)), (0.5, (20, 90, 230)), (0.72, (80, 190, 255)), (0.9, (200, 240, 255)), (1, (255, 255, 255))]
        for i in range(256):
            v = i / 255
            for (a, ca), (b, cb) in zip(stops, stops[1:]):
                if a <= v <= b: f = (v - a) / (b - a); lut[i] = np.array(ca) * (1 - f) + np.array(cb) * f
        self.lut = lut.astype(np.uint8)
        self.N = neon(600)
        b = Image.new("L", (W + 200, 260), 0); ImageDraw.Draw(b).ellipse((100, 70, W + 100, 190), fill=255)
        self.band = solid(blur(b, 40), (0, 4, 16), 0.85)
        r = np.random.default_rng(13); self.E = [(r.uniform(0, W), r.uniform(0, 1), int(r.integers(1, 3)), r.uniform(2, 5), r.uniform(0, TAU)) for _ in range(90)]
    def frame(self, t):
        a = np.roll(self.n1, int(-t * 2 * self.h), axis=0) * 0.65 + np.roll(self.n2, int(-t * 3 * self.h), axis=0) * 0.35
        I = np.clip((a * self.shape - 0.32) / 0.55, 0, 1)
        rgb = self.lut[(I * 255).astype(np.uint8)]
        im = Image.fromarray(rgb, "RGB").resize((W, H), BICUBIC).convert("RGBA")
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for x, y0, k, r, ph in self.E:
            y = H - ((y0 + k * t) % 1.0) * H * 1.05; xx = x + 30 * math.sin(TAU * 2 * t + ph)
            d.ellipse((xx - r, y - r, xx + r, y + r), fill=(170, 225, 255, int(255 * min(1, y / H * 1.5))))
        im.alpha_composite(blur(lay, 4)); im.alpha_composite(lay)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 4 * t), big=0.6)
        put(im, self.band, CX, round(0.93 * H)); footer(im, color=(220, 240, 255), y=round(0.93 * H))
        return im


# ---------- 14 the logo over rippling water, rain ----------
@design("14 Su Yansimasi")
class Su:
    def setup(self):
        YY, XX = grid(); self.WY = WY = round(0.62 * H); self.LY = round(0.38 * H)
        self.sky = arr_img(mix((2, 8, 26), (12, 44, 92), np.clip(YY / WY, 0, 1) ** 1.3)); self.st = stars(110, 14, 0, WY - 300, 2.2)
        self.N = neon(560)
        r = np.random.default_rng(14); self.drops = [(r.uniform(0, W), r.uniform(WY + 40, H - 60), r.uniform(0, 1)) for _ in range(26)]
        self.rain = [(r.uniform(0, W), r.uniform(0, 1), r.uniform(60, 120)) for _ in range(110)]
        self.rows = np.arange(WY, H)
    def frame(self, t):
        up = self.sky.copy(); draw_stars(up, self.st, t)
        draw_logo(up, self.N, CX, self.LY + 10 * math.sin(TAU * t), pulse=0.5 + 0.5 * math.sin(TAU * 2 * t))
        U = np.asarray(up.convert("RGB")); WY = self.WY
        y = self.rows; depth = (y - WY) / (H - WY)
        src = np.clip(WY - 1 - (y - WY) * 0.95, 0, WY - 1).astype(int)
        dx = (3 + 14 * depth) * np.sin(TAU * (y / 40 - 3 * t)) + 3 * np.sin(TAU * (y / 13 + 5 * t))
        cols = np.clip(np.arange(W)[None, :] + dx[:, None], 0, W - 1).astype(int)
        refl = U[src[:, None], cols].astype(np.float32) * (0.55 - 0.25 * depth[:, None, None]) + np.array((2, 10, 26), np.float32) * 0.5
        out = U.copy(); out[WY:] = np.clip(refl, 0, 255).astype(np.uint8)
        im = Image.fromarray(out).convert("RGBA")
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.line((0, WY, W, WY), fill=(90, 170, 255, 180), width=3)
        for x, yy, ph in self.drops:
            u = (t * 2 + ph) % 1.0; persp = 0.35 + 0.65 * (yy - WY) / (H - WY); r = 10 + 120 * u * persp
            d.ellipse((x - r, yy - r * 0.28, x + r, yy + r * 0.28), outline=(150, 210, 255, int(200 * (1 - u))), width=3)
        for x, ph, L in self.rain:
            yy = ((ph + 4 * t) % 1.0) * (H + 200) - 100; d.line((x, yy, x - 8, yy + L), fill=(170, 210, 255, 90), width=2)
        im.alpha_composite(lay)
        footer(im, y=round(0.93 * H))
        return im


# ---------- 15 swerve robot drives laps around the logo, spinning while it drives ----------
@design("15 Swerve Robot")
class Swerve:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((24, 30, 40), (8, 10, 16), np.clip(np.hypot(XX - CX, YY - CY) / 1500, 0, 1)) + np.random.default_rng(15).normal(0, 4, (H, W, 1)))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
        for x in range(30, W, 120): d.line((x, 0, x, H), fill=(255, 255, 255, 14), width=2)
        for y in range(30, H, 120): d.line((0, y, W, y), fill=(255, 255, 255, 14), width=2)
        d.rounded_rectangle((60, 300, W - 60, H - 300), 60, outline=(255, 255, 255, 70), width=8)
        self.base.alpha_composite(g)
        self.a, self.b = 400, 760; self.N = neon(560)
        f = font(44, "Bold")
        rb = Image.new("RGBA", (240, 240), (0, 0, 0, 0)); dr = ImageDraw.Draw(rb)
        dr.rounded_rectangle((8, 8, 232, 232), 18, fill=(30, 100, 230, 255))
        dr.rectangle((34, 34, 206, 206), fill=(40, 46, 56, 255))
        dr.rectangle((80, 60, 160, 180), fill=(20, 22, 28, 255)); dr.rectangle((92, 82, 148, 100), fill=SKY + (255,))
        for txt, ang, pos in (("8084", 0, (120, 21)), ("8084", 180, (120, 219))):
            ti = Image.new("RGBA", (180, 40), (0, 0, 0, 0)); ImageDraw.Draw(ti).text((90, 20), txt, font=font(28, "Bold"), fill=WHITE, anchor="mm")
            ti = ti.rotate(ang); rb.alpha_composite(ti, (pos[0] - 90, pos[1] - 20))
        self.rb = rb
    def P(self, t):
        return CX + self.a * math.cos(TAU * t), CY + self.b * math.sin(TAU * t)
    def frame(self, t):
        im = self.base.copy()
        tr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tr)
        pts = [self.P(t - j * 0.004) for j in range(60)]
        for j in range(59): d.line((pts[j], pts[j + 1]), fill=(80, 180, 255, int(230 * (1 - j / 60))), width=int(24 * (1 - j / 60)) + 2)
        im.alpha_composite(blur(tr, 14)); im.alpha_composite(tr)
        draw_logo(im, self.N, CX, CY, pulse=0.5 + 0.5 * math.sin(TAU * 2 * t))
        x, y = self.P(t); vx, vy = -self.a * math.sin(TAU * t), self.b * math.cos(TAU * t)
        psi = 360 * 2 * t                           # chassis spins twice per lap
        heading = math.degrees(math.atan2(vy, vx))
        r = self.rb.copy(); dr = ImageDraw.Draw(r)
        wa = math.radians(-heading - psi)            # wheel direction in the robot frame
        for mx, my in ((62, 62), (178, 62), (62, 178), (178, 178)):
            dr.ellipse((mx - 24, my - 24, mx + 24, my + 24), fill=(150, 156, 166, 255))
            c, s = math.cos(wa), math.sin(wa)
            q = [(mx + c * u - s * v, my + s * u + c * v) for u, v in ((-18, -8), (18, -8), (18, 8), (-18, 8))]
            dr.polygon(q, fill=(20, 20, 24, 255))
        gl = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((40, 40, 380, 380), fill=NEON + (120,))
        put(im, blur(gl, 40), x, y)
        put(im, blur(solid(r.getchannel("A"), (0, 0, 0), 0.7), 14), x + 10, y + 16, ang=psi)
        put(im, r, x, y, ang=psi)
        footer(im, y=round(0.93 * H))
        return im


# ---------- 16 a light tracer draws the logo outline, it lights up, shines, fades ----------
@design("16 Isik Cizimi")
class Cizim:
    def setup(self):
        YY, XX = grid(); self.base = arr_img(mix((6, 22, 56), (0, 3, 12), np.clip(np.hypot(XX - CX, YY - CY) / 1400, 0, 1)))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
        s = 60; w = math.sqrt(3) * s
        for row in range(int(H / (1.5 * s)) + 2):
            for col in range(int(W / w) + 2):
                x = col * w + (row % 2) * w / 2; y = row * 1.5 * s
                d.polygon([(x + (s - 3) * math.cos(math.radians(60 * i + 30)), y + (s - 3) * math.sin(math.radians(60 * i + 30))) for i in range(6)], outline=(80, 160, 255, 22))
        self.base.alpha_composite(g)
        self.N = neon(620); AP = self.N["AP"]
        outer = dilate(AP, 1); ring = np.clip(np.asarray(outer, np.int16) - np.asarray(AP.filter(ImageFilter.MinFilter(3)), np.int16) * 0, 0, 255)
        ring = np.clip(np.asarray(dilate(AP, 1), np.int16) - np.asarray(AP, np.int16), 0, 255).astype(np.float32) / 255
        ring = np.maximum(ring, np.clip(np.asarray(AP, np.int16) - np.asarray(AP.filter(ImageFilter.MinFilter(7)), np.int16), 0, 255) / 255)
        h, w = ring.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        self.ang = (np.arctan2(yy - h / 2, xx - w / 2) + math.pi / 2) % TAU      # 0 at the top, clockwise
        self.ring = ring; self.shape = (w, h)
        # tracer position for each angle: outermost ring pixel
        self.tip = []
        rr = np.hypot(xx - w / 2, yy - h / 2)
        for k in range(360):
            a0 = TAU * k / 360; m = (np.abs(((self.ang - a0 + math.pi) % TAU) - math.pi) < 0.02) & (ring > 0.5)
            if m.any(): i = np.argmax(np.where(m, rr, -1)); self.tip.append((xx.flat[i] - w / 2, yy.flat[i] - h / 2))
            else: self.tip.append(self.tip[-1] if self.tip else (0, -h / 2))
        L = self.N["LP"]; self.la = np.asarray(L.getchannel("A"), np.float32) / 255
        self.ly, self.lx = yy, xx
    def frame(self, t):
        im = self.base.copy()
        draw_k = smooth(0.03, 0.33, t)
        out_k = 1 - smooth(0.84, 0.97, t)
        fill_k = smooth(0.33, 0.43, t) * out_k
        phi = draw_k * TAU
        m = self.ring * (self.ang <= phi) * out_k if draw_k < 1 else self.ring * out_k
        R = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L")
        rl = solid(R, (150, 220, 255)); put(im, blur(solid(R, NEON, 2.0), 14), CX, CY); put(im, rl, CX, CY)
        if fill_k > 0:
            fl = 0.4 * bump(t, 0.40, 0.05)
            draw_logo(im, self.N, CX, CY, k=fill_k, pulse=0.5 + 0.5 * math.sin(TAU * 2 * t), big=0.6 + fl * 3)
            s = (t - 0.52) / 0.22
            if 0 < s < 1:
                pos = -0.3 + 1.6 * s; u = (self.lx / self.shape[0] * 0.75 + self.ly / self.shape[1] * 0.45) / 1.2
                band = np.exp(-((u - pos) / 0.05) ** 2) * self.la * 0.8 * fill_k
                put(im, rgba(np.array((255, 255, 255), np.float32), band), CX, CY)
        if 0.02 < t < 0.34:
            tx, ty = self.tip[int(phi / TAU * 359) % 360]
            g = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((70, 70, 130, 130), fill=(230, 245, 255, 255))
            put(im, blur(g, 22), CX + tx, CY + ty); put(im, blur(g, 6), CX + tx, CY + ty)
        footer(im, color=ICE)
        return im


# ===================================================================================================
_S = None
def _init(name):
    global _S
    _S = D[name](); _S.setup()
def _work(i):
    return _S.frame(i / N).convert("RGB").tobytes()

def render(name, workers=12):
    import imageio_ffmpeg
    os.makedirs(OUT, exist_ok=True)
    out = OUT + f"ALFA 8084 - Hareketli {name}.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
           "-movflags", "+faststart", "-an", out]
    t0 = time.time(); p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    with Pool(workers, initializer=_init, initargs=(name,)) as pool:
        for i, b in enumerate(pool.imap(_work, range(N), chunksize=2)):
            p.stdin.write(b)
            if i == 0: Image.frombytes("RGB", (W, H), b).save(OUT + f"ALFA 8084 - Hareketli {name} (kapak).jpg", quality=92)
    p.stdin.close(); p.wait()
    print(f"{name}: {os.path.getsize(out) // 1024} KB, {time.time() - t0:.0f} s, rc={p.returncode}", flush=True)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--test":
        os.makedirs(OUT + "_test", exist_ok=True)
        S = D[a[1]](); S.setup()
        for f in map(int, a[2].split(",")):
            t0 = time.time(); S.frame(f / N).convert("RGB").save(OUT + f"_test/{a[1][:2]}_{f:03d}.jpg", quality=88); print(f, f"{time.time() - t0:.2f}s")
        sys.exit()
    names = [n for n in D if not a or any(n.startswith(x) for x in a)]
    for n in names: render(n)
