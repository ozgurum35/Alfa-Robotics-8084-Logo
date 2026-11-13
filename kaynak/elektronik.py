# ALFA Robotics 8084 wallpapers, FRC electronics theme: 8 designs (brushless motor, motor controller, CAN bus,
# controller board, power distribution, encoder, planetary gearbox, pneumatics). Generic drawings, no brand names.
# Each design is drawn resolution-independently and exported three ways:
#   phone still 2160x4680 JPG, desktop (Windows) 3840x2160 JPG, phone animated 1080x2340 MP4 (10 s seamless loop).
# Usage: python elektronik.py [still|desk|anim|all] [design-number-prefixes ...]
#        python elektronik.py --test <prefix> <mode> t1,t2,...   (t in 0..1, saves check images)
import math, os, subprocess, sys, time
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw
from hareketli2 import (smooth, mix, solid, fade, blur, paste, neon, draw_logo, font, gear_poly,
                        ICE, SKY, NEON, WHITE, ROOT)

TAU = 2 * math.pi
FPS, NF = 30, 300
OUT = ROOT + "Elektronik Duvar Kagitlari/"
RED, BLK, YEL, GRN, AMB, CU = (235, 60, 60), (70, 76, 92), (250, 205, 50), (70, 200, 110), (255, 160, 40), (200, 120, 60)
DARK, PANEL, MID = (6, 24, 50), (14, 40, 78), (30, 72, 128)


class Ctx:
    def __init__(self, mode):
        self.mode = mode
        if mode == "desk":
            W, H = 3840, 2160; self.k = 2
            self.logo = (0.25 * W, 0.45 * H, 1000); self.box = (1700, 110, 3790, 2050); self.foot = (0.25 * W, 1720)
        else:
            W, H = (1080, 2340) if mode == "anim" else (2160, 4680); self.k = W / 1080
            self.logo = (W / 2, 0.345 * H, 430 * self.k); self.box = (0, 0.47 * H, W, 0.865 * H); self.foot = (W / 2, 0.925 * H)
        self.W, self.H = W, H
        bx0, by0, bx1, by1 = self.box
        self.bs = min(bx1 - bx0, by1 - by0) / 1000


class Pen:
    """Draws in a 1000 x 1000 unit square centred in ctx.box, 2x supersampled; two layers: flat and glowing."""
    def __init__(self, ctx, ss=2):
        bx0, by0, bx1, by1 = ctx.box; self.c, self.ss, self.bs = ctx, ss, ctx.bs
        self.w, self.h = round(bx1 - bx0), round(by1 - by0)
        self.ox, self.oy = (self.w - 1000 * self.bs) / 2, (self.h - 1000 * self.bs) / 2
        self.f = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0)); self.g = self.f.copy()
        self.df, self.dg = ImageDraw.Draw(self.f), ImageDraw.Draw(self.g)
    def p(self, x, y): return ((self.ox + x * self.bs) * self.ss, (self.oy + y * self.bs) * self.ss)
    def L(self, v): return v * self.bs * self.ss
    def _d(self, glow): return self.dg if glow else self.df
    @staticmethod
    def _c(c, a=255): return None if c is None else (tuple(c) + (a,) if len(c) == 3 else tuple(c))
    def line(self, pts, col, w=3, glow=False, a=255):
        self._d(glow).line([self.p(*q) for q in pts], fill=self._c(col, a), width=max(1, round(self.L(w))), joint="curve")
    def circle(self, x, y, r, fill=None, outline=None, w=3, glow=False, a=255):
        x0, y0 = self.p(x - r, y - r); x1, y1 = self.p(x + r, y + r); wd = max(1, round(self.L(w)))
        if glow and outline is not None:   # glowing outline, flat fill (keeps details drawn later on top)
            if fill is not None: self.df.ellipse((x0, y0, x1, y1), fill=self._c(fill, a))
            self.dg.ellipse((x0, y0, x1, y1), outline=self._c(outline, a), width=wd); return
        self._d(glow).ellipse((x0, y0, x1, y1), fill=self._c(fill, a), outline=self._c(outline, a), width=wd)
    def poly(self, pts, fill=None, outline=None, w=3, glow=False, a=255):
        q = [self.p(*z) for z in pts]; d = self._d(glow)
        if fill is not None: (self.df if glow and outline is not None else d).polygon(q, fill=self._c(fill, a))
        if outline is not None: d.line(q + [q[0]], fill=self._c(outline, a), width=max(1, round(self.L(w))), joint="curve")
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=3, r=0, glow=False, a=255):
        p0, p1 = self.p(x0, y0), self.p(x1, y1)
        if glow and outline is not None:
            if fill is not None: self.df.rounded_rectangle((p0, p1), radius=self.L(r), fill=self._c(fill, a))
            self.dg.rounded_rectangle((p0, p1), radius=self.L(r), outline=self._c(outline, a), width=max(1, round(self.L(w)))); return
        self._d(glow).rounded_rectangle((p0, p1), radius=self.L(r), fill=self._c(fill, a), outline=self._c(outline, a), width=max(1, round(self.L(w))) if outline else 0)
    def text(self, s, x, y, size, col=ICE, anchor="mm", glow=False, mono=False, var="SemiBold", a=255):
        self._d(glow).text(self.p(x, y), s, font=font(max(6, round(self.L(size))), var, mono), fill=self._c(col, a), anchor=anchor)
    def out(self, im, glow_r=10):
        f = self.f.resize((self.w, self.h), Image.LANCZOS); g = self.g.resize((self.w, self.h), Image.LANCZOS)
        x, y = round(self.c.box[0]), round(self.c.box[1]); r = glow_r * self.bs
        gb = blur(g, r * 2.5); paste(im, gb, x, y); paste(im, blur(g, r * 0.8), x, y)
        paste(im, f, x, y); paste(im, g, x, y)


def rot_pts(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a); return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]
def arc_pts(cx, cy, r0, r1, a0, a1, n=10):
    o = [(cx + r1 * math.cos(a0 + (a1 - a0) * i / n), cy + r1 * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    return o + [(cx + r0 * math.cos(a1 - (a1 - a0) * i / n), cy + r0 * math.sin(a1 - (a1 - a0) * i / n)) for i in range(n + 1)]
def along(pts, s):
    """point at distance s along a polyline"""
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if s <= L: f = s / max(L, 1e-6); return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        s -= L
    return pts[-1]
def plen(pts): return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
def flow(pen, pts, t, col, n, speed=1, r=7, rev=False):
    L = plen(pts)
    for j in range(n):
        u = (j / n + (-1 if rev else 1) * speed * t) % 1.0; x, y = along(pts, u * L)
        pen.circle(x, y, r, fill=col, glow=True)
def ease_cycle(u, a0, a1, b0, b1):   # 0 -> 1 between a0..a1, 1 -> 0 between b0..b1
    return smooth(a0, a1, u) * (1 - smooth(b0, b1, u))


def background(ctx, c0=(6, 34, 76), c1=(0, 4, 14)):
    W, H, k = ctx.W, ctx.H, ctx.k
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bx0, by0, bx1, by1 = ctx.box; cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    d = np.hypot(xx - cx, (yy - cy) * 0.8) / (0.75 * max(W, H))
    a = mix(c0, c1, np.clip(d, 0, 1) ** 0.8)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g); s = round(40 * k)
    for i, x in enumerate(range(0, W, s)): dg.line((x, 0, x, H), fill=(110, 180, 255, 26 if i % 5 == 0 else 10), width=max(1, round(k)))
    for i, y in enumerate(range(0, H, s)): dg.line((0, y, W, y), fill=(110, 180, 255, 26 if i % 5 == 0 else 10), width=max(1, round(k)))
    im.alpha_composite(g)
    return im

def footer(im, ctx, color=ICE):
    k = ctx.k; f = font(round(36 * k)); x, y = ctx.foot
    lay = Image.new("RGBA", (ctx.W, round(100 * k)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); my = 50 * k
    s = "   ".join(" ".join(w) for w in "FRC TEAM 8084".split()); tw = d.textlength(s, font=f)
    d.text((x, my), s, font=f, fill=color + (220,), anchor="mm")
    for sg in (-1, 1):
        x0 = x + sg * (tw / 2 + 36 * k); d.line((x0, my, x0 + sg * 170 * k, my), fill=color + (120,), width=max(1, round(3 * k)))
    paste(im, lay, 0, y - my)


# ===================================================================================================
D = {}
def design(name, still_t=0.1):
    def reg(cls): cls.still_t = still_t; D[name] = cls; return cls
    return reg

class Base:
    bg = ((6, 34, 76), (0, 4, 14))
    def __init__(self, ctx):
        self.ctx = ctx; self.BG = background(ctx, *self.bg); self.N = neon(round(ctx.logo[2]))
        self.setup()
    def setup(self): pass
    def frame(self, t, still=False):
        im = self.BG.copy(); pen = Pen(self.ctx)
        self.draw(pen, t); pen.out(im)
        lx, ly, lw = self.ctx.logo
        draw_logo(im, self.N, lx, ly, pulse=0.5 if still else 0.5 + 0.5 * math.sin(TAU * 2 * t), big=0.5)
        footer(im, self.ctx)
        return im


# ---------- 01 brushless motor cross-section: rotor spins, the three phases switch round ----------
@design("01 Fircasiz Motor", 0.04)
class Motor(Base):
    def draw(self, p, t):
        cx, cy = 500, 470; th = -TAU * 3 * t; el = 7 * th
        p.circle(cx, cy, 470, fill=(8, 26, 52), outline=SKY, w=5, glow=True)
        for i in range(48):
            a = TAU * i / 48; p.line([(cx + 470 * math.cos(a), cy + 470 * math.sin(a)), (cx + 492 * math.cos(a), cy + 492 * math.sin(a))], (60, 130, 210), 6)
        p.circle(cx, cy, 448, fill=(22, 54, 98)); p.circle(cx, cy, 372, fill=(0, 0, 0, 0))
        for i in range(12):
            a = TAU * i / 12 - math.pi / 2; ph = i % 3
            I = max(0.0, math.cos(el - ph * TAU / 3 + (math.pi if (i // 3) % 2 else 0)))
            col = tuple(int(v) for v in np.array(CU) * (1 - I) + np.array((255, 215, 140)) * I)
            coil = rot_pts([(255, -40), (365, -40), (365, 40), (255, 40)], cx, cy, a)
            p.poly(coil, fill=col, glow=I > 0.15, a=255)
            for j in range(1, 6):
                r = 255 + j * 18; p.line(rot_pts([(r, -40), (r, 40)], cx, cy, a), (110, 60, 25), 2)
            p.poly(rot_pts([(240, -24), (380, -24), (380, 24), (240, 24)], cx, cy, a), fill=(36, 82, 140))
            p.poly(arc_pts(cx, cy, 228, 248, a - 0.2, a + 0.2, 6), fill=(36, 82, 140))
            p.text("ABC"[ph], *rot_pts([(410, 0)], cx, cy, a)[0], 26, col if I > 0.3 else ICE, glow=I > 0.3, var="Bold")
        p.circle(cx, cy, 218, fill=(14, 36, 70), outline=(70, 140, 220), w=3)
        for m in range(14):
            a0 = th + TAU * m / 14
            p.poly(arc_pts(cx, cy, 178, 214, a0 - 0.18, a0 + 0.18, 6), fill=(210, 70, 80) if m % 2 else (60, 120, 220))
            p.text("SN"[m % 2], cx + 196 * math.cos(a0), cy + 196 * math.sin(a0), 18, WHITE, var="Bold")
        for h in range(6):
            a0 = th + TAU * h / 6 + 0.26; p.circle(cx + 112 * math.cos(a0), cy + 112 * math.sin(a0), 26, fill=(6, 20, 42))
        p.circle(cx, cy, 52, fill=(175, 190, 205), outline=WHITE, w=2)
        p.poly(rot_pts([(30, -10), (54, -10), (54, 10), (30, 10)], cx, cy, th), fill=(60, 70, 85))
        p.text("FIRÇASIZ DC MOTOR", 20, 960, 26, ICE, "lm", var="Bold")
        p.text("12 OLUK · 14 KUTUP · 3 FAZ", 980, 960, 22, (140, 200, 240), "rm", mono=True)


# ---------- 02 motor controller with a scope: three phase currents and the PWM that makes them ----------
@design("02 Motor Surucu", 0.1)
class Surucu(Base):
    def draw(self, p, t):
        on = 0.5 + 0.5 * math.sin(TAU * 20 * t) > 0.5
        for xx, col in ((215, RED), (285, BLK)):
            pts = [(xx, 160), (xx, 50 + (xx - 215)), (-120, 50 + (xx - 215))]; p.line(pts, col, 12)
        flow(p, [(-120, 50), (215, 50), (215, 160)], t, (255, 140, 120), 6, 3, 5)
        for yy, col in ((400, YEL), (440, GRN)): p.line([(110, yy), (-120, yy)], col, 9)
        flow(p, [(110, 400), (-120, 400)], t, (255, 240, 160), 3, 4, 4)
        outs = [(190, SKY), (250, ICE), (310, NEON)]
        for i, (xx, col) in enumerate(outs):
            q = [(xx, 790), (xx, 830), (250 + (xx - 250) * 0.5, 862)]
            p.line(q, col, 10); flow(p, q, t, WHITE, 2, 6 + i, 4)
        p.circle(250, 915, 58, fill=PANEL, outline=SKY, w=4, glow=True)
        for s_ in range(4):
            a = TAU * (10 * t) + s_ * TAU / 4; p.line([(250, 915), (250 + 46 * math.cos(a), 915 + 46 * math.sin(a))], (150, 200, 240), 6)
        p.circle(250, 915, 14, fill=(200, 210, 220))
        p.rect(110, 160, 390, 790, fill=(18, 46, 88), outline=SKY, w=4, r=30, glow=True)
        for y in range(250, 701, 30): p.rect(140, y, 360, y + 14, fill=(30, 70, 124), r=5)
        p.text("MOTOR SÜRÜCÜ", 250, 202, 26, ICE, var="Bold")
        p.circle(250, 745, 18, fill=(80, 255, 160) if on else (20, 70, 50), glow=on)
        p.text("CAN", 125, 370, 18, YEL, "lm", var="Bold")
        # scope
        X0, X1, Y0, Y1 = 470, 990, 120, 880
        p.rect(X0, Y0, X1, Y1, fill=(3, 14, 30), outline=(70, 150, 230), w=4, r=22, glow=True)
        for i in range(1, 10): p.line([(X0 + i * (X1 - X0) / 10, Y0 + 10), (X0 + i * (X1 - X0) / 10, Y1 - 10)], (40, 90, 150), 1)
        for i in range(1, 8): p.line([(X0 + 10, Y0 + i * (Y1 - Y0) / 8), (X1 - 10, Y0 + i * (Y1 - Y0) / 8)], (40, 90, 150), 1)
        xs = np.linspace(X0 + 14, X1 - 14, 160); per = (X1 - X0) / 2
        for k, col in enumerate((SKY, ICE, (255, 120, 200))):
            ys = 330 - 150 * np.sin(TAU * (xs / per - 3 * t) + k * TAU / 3)
            p.line(list(zip(xs, ys)), col, 5, glow=True)
        pts = []; pw = 26; x = X0 + 14
        while x < X1 - 14:
            duty = 0.5 + 0.42 * math.sin(TAU * (x / per - 3 * t))
            x1 = min(X1 - 14, x + pw * duty); x2 = min(X1 - 14, x + pw)
            pts += [(x, 820), (x, 640), (x1, 640), (x1, 820), (x2, 820)]; x = x2
        p.line(pts, (255, 190, 80), 3, glow=True)
        p.text("FAZ A · B · C", X0 + 24, Y0 + 30, 20, ICE, "lm", mono=True)
        p.text("PWM", X0 + 24, 600, 20, (255, 190, 80), "lm", mono=True)


# ---------- 03 CAN bus: packets run down the twisted pair from device to device ----------
@design("03 CAN Veri Yolu", 0.3)
class CAN(Base):
    def setup(self):
        self.dev = [(150, 160, "KONTROLCÜ"), (500, 160, "GÜÇ DAĞITIM"), (850, 160, "SÜRÜCÜ 1"), (850, 480, "SÜRÜCÜ 2"),
                    (500, 480, "SÜRÜCÜ 3"), (150, 480, "SÜRÜCÜ 4"), (150, 800, "JİROSKOP"), (500, 800, "SENSÖR")]
        self.path = [(x, y) for x, y, _ in self.dev] + [(800, 800)]
        self.L = plen(self.path); self.ids = ["0x0A1", "0x1F4", "0x204", "0x3E8", "0x7C2"]
    def draw(self, p, t):
        n = 5; pk = [((t * 2 + j / n) % 1.0) * self.L for j in range(n)]
        for a, b in zip(self.path, self.path[1:]):
            L = math.dist(a, b); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            for sg, col in ((1, YEL), (-1, GRN)):
                q = [(a[0] + ux * s - uy * sg * 9 * math.sin(s / 22), a[1] + uy * s + ux * sg * 9 * math.sin(s / 22)) for s in np.linspace(0, L, int(L / 6))]
                p.line(q, col, 7)
        x, y = self.path[-1]; p.rect(x - 10, y - 40, x + 110, y + 40, fill=(30, 30, 40), outline=(200, 200, 210), w=3, r=10)
        p.text("120 Ω", x + 50, y, 22, ICE, var="Bold")
        s0 = 0
        for i, (x, y, name) in enumerate(self.dev):
            hit = max(math.exp(-((s0 - s) / 45) ** 2) for s in pk)
            p.rect(x - 120, y - 70, x + 120, y + 70, fill=(14, 40, 78), outline=tuple(int(c) for c in np.array((60, 130, 210)) * (1 - hit) + np.array((200, 240, 255)) * hit), w=4, r=16, glow=True)
            p.text(name, x, y - 18, 24, ICE, var="Bold")
            p.text(f"ID {i + 1:02d}", x, y + 22, 18, (130, 190, 240), mono=True)
            p.circle(x + 95, y - 45, 10, fill=(80, 255, 160) if hit > 0.3 else (20, 70, 50), glow=hit > 0.3)
            if i < len(self.dev) - 1: s0 += math.dist(self.path[i], self.path[i + 1])
        for j, s in enumerate(pk):
            x, y = along(self.path, s)
            if any(abs(x - dx) < 150 and abs(y - dy) < 85 for dx, dy, _ in self.dev): continue
            p.rect(x - 34, y - 16, x + 34, y + 16, fill=(220, 245, 255), r=8, glow=True)
            p.text(self.ids[j], x, y, 15, (10, 40, 80), mono=True, glow=True)
        p.text("CAN VERİ YOLU · 1 Mbit/s", 500, 960, 26, ICE, var="Bold")


# ---------- 04 controller board: data pulses on the traces, status LEDs blink ----------
@design("04 Kontrol Karti", 0.2)
class Kart(Base):
    def setup(self):
        r = np.random.default_rng(4); self.tr = []
        hx = [130 + i * 82 for i in range(10)]
        for i, x in enumerate(hx):
            x0 = 410 + i * 20; yl = 620 + abs(i - 4.5) * -10 + 60
            self.tr.append([(x0, 560), (x0, yl), (x, yl + abs(x - x0) * 0), (x, 820)])
        for (a, b) in (((440, 340), (250, 290)), ((560, 340), (760, 310)), ((390, 450), (310, 640)), ((610, 450), (740, 650)),
                       ((500, 340), (500, 130)), ((610, 400), (880, 400))):
            mid = (a[0], b[1]) if abs(b[1] - a[1]) > abs(b[0] - a[0]) else (b[0], a[1])
            self.tr.append([a, (a[0], (a[1] + b[1]) / 2), (b[0], (a[1] + b[1]) / 2), b])
        self.ph = r.uniform(0, 1, len(self.tr)); self.sp = r.integers(1, 4, len(self.tr)); self.hx = hx
    def draw(self, p, t):
        p.rect(40, 80, 960, 920, fill=(5, 28, 58), outline=(80, 160, 240), w=5, r=40, glow=True)
        for x, y in ((90, 130), (910, 130), (90, 870), (910, 870)): p.circle(x, y, 22, fill=(0, 0, 0, 0), outline=(170, 185, 200), w=6)
        for q in self.tr: p.line(q, (40, 110, 190), 6)
        for q, ph, sp in zip(self.tr, self.ph, self.sp):
            L = plen(q); u = (t * sp + ph) % 1.0
            for j in range(6):
                x, y = along(q, max(0, u - j * 0.02) * L); p.circle(x, y, 7 - j, fill=(200, 240, 255), glow=True)
        # chips
        for x0, y0, x1, y1, lab in ((190, 250, 310, 330, "BELLEK"), (690, 260, 830, 360, "AĞ"), (250, 640, 370, 740, "GÜÇ"), (630, 650, 760, 720, "IMU")):
            p.rect(x0, y0, x1, y1, fill=(16, 22, 32), outline=(90, 110, 140), w=2, r=6)
            for i in range(5):
                xx = x0 + (i + 0.5) * (x1 - x0) / 5; p.line([(xx, y0 - 10), (xx, y0)], (180, 190, 200), 6); p.line([(xx, y1), (xx, y1 + 10)], (180, 190, 200), 6)
            p.text(lab, (x0 + x1) / 2, (y0 + y1) / 2, 18, (150, 170, 200), mono=True)
        g = 0.5 + 0.5 * math.sin(TAU * 4 * t)
        p.rect(380, 330, 620, 570, fill=(12, 18, 28), outline=tuple(int(v) for v in np.array((80, 160, 240)) * (0.6 + 0.4 * g)), w=4, r=10, glow=True)
        for i in range(14):
            s = 395 + i * 15.5
            for a, b in (((s, 316), (s, 330)), ((s, 570), (s, 584)), ((366, s - 15 + 20), (380, s - 15 + 20)), ((620, s - 15 + 20), (634, s - 15 + 20))):
                p.line([a, b], (190, 200, 210), 6)
        p.text("8084", 500, 430, 54, ICE, var="Bold", glow=True, a=int(150 + 100 * g))
        p.text("ALFA · CPU", 500, 490, 20, (130, 170, 220), mono=True)
        for i, x in enumerate(self.hx):
            p.rect(x - 22, 820, x + 22, 890, fill=(20, 20, 26), r=4)
            for j, c in enumerate(((60, 60, 60), RED, WHITE)): p.rect(x - 7, 828 + j * 20, x + 7, 842 + j * 20, fill=(200, 170, 70))
            p.text(str(i), x, 805, 16, (150, 190, 230), mono=True)
        p.text("PWM", 70, 805, 18, ICE, "lm", var="Bold")
        leds = (("GÜÇ", (80, 255, 160), 1.0), ("DURUM", SKY, 0.5 + 0.5 * math.sin(TAU * 5 * t)), ("RSL", AMB, 1.0 if (t * 15) % 1 < 0.5 else 0.0),
                ("İLETİŞİM", (120, 200, 255), 1.0 if (t * 37) % 1 < 0.3 else 0.1))
        for i, (lab, col, k) in enumerate(leds):
            y = 430 + i * 62; p.circle(880, y, 16, fill=tuple(int(c * (0.25 + 0.75 * k)) for c in col), glow=k > 0.5)
            p.text(lab, 850, y, 18, ICE, "rm", var="Bold")
        p.rect(400, 50, 600, 110, fill=(170, 180, 195), r=8); p.text("USB · ETHERNET", 500, 80, 18, (20, 30, 50), var="Bold")
        p.text("ALFA ROBOTICS 8084 · ROBOT KONTROL KARTI", 90, 175, 18, (130, 180, 230), "lm", mono=True)


# ---------- 05 power distribution: current flows from the battery through the breakers to the motors ----------
@design("05 Guc Dagitimi", 0.15)
class Guc(Base):
    def draw(self, p, t):
        mot = [160, 390, 620, 850]; spd = [5, 4, 6, 3]
        # wires
        rp = [(130, 140), (130, 90), (420, 90), (420, 200)]; rp2 = [(540, 200), (540, 300), (560, 300), (560, 420)]
        bp = [(230, 140), (230, 110), (300, 110), (300, 330), (480, 330), (480, 420)]
        p.line(rp, RED, 14); p.line(rp2, RED, 14); p.line(bp, BLK, 14)
        flow(p, rp + rp2[1:], t, (255, 170, 150), 10, 2, 6); flow(p, bp, t, (190, 200, 220), 8, 2, 5, rev=True)
        for i, x in enumerate(mot):
            sx = 440 + i * 140
            for dx, col, rev in ((-12, RED, False), (12, BLK, True)):
                q = [(sx + dx, 640), (sx + dx, 720), (x + dx, 760), (x + dx, 790)]; p.line(q, col, 9)
                flow(p, q, t, (255, 170, 150) if not rev else (190, 200, 220), 4, spd[i] * 0.5, 4, rev)
        # battery
        p.rect(40, 140, 320, 380, fill=(22, 26, 36), outline=(150, 160, 175), w=4, r=18)
        p.rect(100, 125, 160, 145, fill=RED, r=4); p.rect(200, 125, 260, 145, fill=BLK, r=4)
        p.text("12V", 180, 245, 74, ICE, var="Bold"); p.text("AKÜ · 18 Ah", 180, 320, 22, (150, 170, 200), mono=True)
        # main breaker
        p.circle(480, 200, 72, fill=(30, 34, 44), outline=(200, 205, 215), w=4)
        p.circle(480, 200, 26, fill=RED, glow=True); p.text("120A", 480, 255, 20, ICE, var="Bold")
        p.text("ANA SİGORTA", 568, 150, 18, (150, 190, 230), "lm", var="Bold")
        # PDH
        p.rect(380, 420, 960, 640, fill=(16, 42, 82), outline=SKY, w=4, r=20, glow=True)
        p.text("GÜÇ DAĞITIM PANELİ", 670, 455, 24, ICE, var="Bold")
        for i in range(8):
            x = 410 + i * 68; on = 0.5 + 0.5 * math.sin(TAU * (2 * t + i / 8))
            p.rect(x, 490, x + 52, 600, fill=(8, 22, 44), outline=(70, 140, 220), w=2, r=6)
            p.text(f"{[40, 40, 40, 40, 30, 20, 20, 10][i]}A", x + 26, 520, 16, ICE, mono=True)
            p.circle(x + 26, 575, 9, fill=(80, 255, 160) if on > 0.2 else (20, 70, 50), glow=on > 0.2)
        # motors
        for i, x in enumerate(mot):
            p.circle(x, 865, 75, fill=PANEL, outline=SKY, w=4, glow=True)
            for s_ in range(3):
                a = TAU * spd[i] * t * 2 + s_ * TAU / 3; p.line([(x, 865), (x + 58 * math.cos(a), 865 + 58 * math.sin(a))], (150, 200, 240), 8)
            p.circle(x, 865, 16, fill=(200, 210, 220)); p.text(f"M{i + 1}", x + 52, 800, 20, ICE, var="Bold")
        # readout
        I = 86 + 30 * math.sin(TAU * 2 * t) + 10 * math.sin(TAU * 5 * t); V = 12.6 - I * 0.008
        p.rect(40, 440, 320, 640, fill=(3, 14, 30), outline=(70, 150, 230), w=3, r=14)
        p.text(f"{V:.2f} V", 180, 500, 44, (120, 255, 190), mono=True, glow=True)
        p.text(f"{I:5.1f} A", 180, 585, 44, (255, 200, 110), mono=True, glow=True)


# ---------- 06 quadrature encoder: slotted disc, optical head, A/B square waves ----------
@design("06 Enkoder", 0.12)
class Enkoder(Base):
    Z = 48
    def ang(self, t): return TAU * 2 * t
    def draw(self, p, t):
        cx, cy, Z = 500, 400, self.Z; th = self.ang(t)
        p.circle(cx, cy, 345, fill=(14, 40, 80), outline=SKY, w=4, glow=True)
        for i in range(Z):
            a = th + TAU * i / Z; p.poly(arc_pts(cx, cy, 282, 330, a, a + TAU / Z / 2, 3), fill=(0, 0, 0, 0))
        a = th + 0.05; p.poly(arc_pts(cx, cy, 236, 256, a, a + TAU / Z / 2, 3), fill=(0, 0, 0, 0))
        for i in range(8): b = th + TAU * i / 8; p.line([(cx + 70 * math.cos(b), cy + 70 * math.sin(b)), (cx + 220 * math.cos(b), cy + 220 * math.sin(b))], (30, 70, 130), 4)
        p.circle(cx, cy, 70, fill=(170, 185, 200), outline=WHITE, w=2); p.circle(cx, cy, 24, fill=(40, 50, 64))
        # read head at the top; light passes when a slot sits under it (slot = first half of each pitch)
        f = ((-math.pi / 2 - th) / (TAU / Z)) % 1.0; lit = f < 0.5
        p.rect(455, 0, 545, 150, fill=(26, 32, 44), outline=(150, 165, 185), w=3, r=10)
        p.rect(465, 60, 535, 130, fill=(0, 0, 0, 0))
        p.line([(500, 20), (500, 140)], (255, 90, 90), 10 if lit else 4, glow=lit, a=255 if lit else 120)
        p.circle(500, 22, 10, fill=(255, 90, 90), glow=True)
        p.text("OPTİK OKUYUCU", 570, 40, 20, ICE, "lm", var="Bold")
        # A / B traces (history window 0.05 of the loop, newest on the right)
        X0, X1 = 60, 940
        p.rect(X0 - 20, 770, X1 + 20, 985, fill=(3, 14, 30), outline=(70, 150, 230), w=3, r=14)
        xs = np.linspace(X0 + 30, X1, 400)
        for k_, (yc, col, lab) in enumerate(((820, SKY, "A"), (930, (255, 190, 80), "B"))):
            tau = t - (X1 - xs) / (X1 - X0) * 0.05
            v = np.cos(Z * self.ang(tau) + k_ * math.pi / 2) > 0
            ys = np.where(v, yc - 30, yc + 30); pts = []
            for x, y in zip(xs, ys):
                if pts and pts[-1][1] != y: pts.append((x, pts[-1][1]))
                pts.append((x, y))
            p.line(pts, col, 4, glow=True); p.text(lab, X0, yc, 24, col, var="Bold")
        deg = (math.degrees(th)) % 360
        p.text(f"θ = {deg:05.1f}°", 980, 720, 24, ICE, "rm", mono=True)
        p.text("KUADRATÜR ENKODER · 48 YARIK", 20, 720, 22, ICE, "lm", var="Bold")


# ---------- 07 planetary gearbox 5:1: sun drives, ring fixed, carrier turns slowly ----------
@design("07 Planet Disli", 0.05)
class Planet(Base):
    Zs, Zp, Zr, m = 12, 18, 48, 14
    def setup(self):
        self.ps, self.pp, self.pr = TAU / self.Zs, TAU / self.Zp, TAU / self.Zr
        th0 = self.phases(0)[1][0]
        a0 = 0.0; ph_p = th0; f_p = ((a0 - ph_p) / self.pp) % 1.0
        self.ph_r = a0 - f_p * self.pr
    def phases(self, t):
        ths = -TAU * 5 * t; thc = ths * self.Zs / (self.Zs + self.Zr); out = []
        for i in range(3):
            a = thc + i * TAU / 3; f_s = ((a - ths) / self.ps) % 1.0; f_p = (0.9 - f_s) % 1.0
            out.append(a + math.pi - f_p * self.pp)
        return ths, out, thc
    def draw(self, p, t):
        cx, cy, m = 500, 460, self.m; ths, php, thc = self.phases(t)
        rs, rp, rr = m * self.Zs / 2, m * self.Zp / 2, m * self.Zr / 2; cd = rs + rp
        p.circle(cx, cy, rr + 70, fill=(18, 50, 96), outline=SKY, w=5, glow=True)
        for i in range(24):
            a = TAU * i / 24; p.circle(cx + (rr + 42) * math.cos(a), cy + (rr + 42) * math.sin(a), 7, fill=(8, 26, 52))
        ring = gear_poly(rr + 1.25 * m, self.Zr, 2.25 * m, self.ph_r, cx, cy)
        p.poly(ring, fill=(0, 0, 0, 0)); p.poly(ring, outline=(90, 170, 240), w=3, glow=True)
        for i in range(3):
            a = thc + i * TAU / 3; x, y = cx + cd * math.cos(a), cy + cd * math.sin(a)
            g = gear_poly(rp + m, self.Zp, 2.25 * m, php[i], x, y)
            p.poly(g, fill=(30, 78, 138), outline=(120, 200, 255), w=3)
            for h in range(5):
                b = php[i] + TAU * h / 5; p.circle(x + 70 * math.cos(b), y + 70 * math.sin(b), 15, fill=(16, 44, 86))
        sg = gear_poly(rs + m, self.Zs, 2.25 * m, ths, cx, cy)
        p.poly(sg, fill=(44, 110, 180), outline=(170, 225, 255), w=3, glow=True)
        p.circle(cx, cy, 30, fill=(180, 195, 210)); p.poly(rot_pts([(18, -8), (32, -8), (32, 8), (18, 8)], cx, cy, ths), fill=(60, 70, 85))
        pts = [(cx + cd * math.cos(thc + i * TAU / 3), cy + cd * math.sin(thc + i * TAU / 3)) for i in range(3)]
        p.poly(pts, outline=(255, 190, 80), w=8, glow=True)
        for x, y in pts: p.circle(x, y, 22, fill=(255, 190, 80), glow=True)
        p.text("PLANET DİŞLİ KUTUSU · 5:1", 500, 935, 28, ICE, var="Bold")
        p.text(f"GÜNEŞ {self.Zs}T  ·  PLANET {self.Zp}T  ·  HALKA {self.Zr}T", 500, 980, 20, (140, 200, 240), mono=True)


# ---------- 08 pneumatics: compressor fills the tank, the valve fires, the piston strokes ----------
@design("08 Pnomatik", 0.12)
class Pnomatik(Base):
    def draw(self, p, t):
        u = (2 * t) % 1.0; e = ease_cycle(u, 0.05, 0.18, 0.55, 0.68); ext = 0.05 < u < 0.55
        AIR = (170, 230, 255)
        tube = lambda q, c=(80, 150, 220): p.line(q, c, 12)
        main = [(250, 200), (330, 200)]; m2 = [(620, 200), (800, 200)]; m3 = [(850, 235), (850, 400)]
        A = [(810, 500), (810, 570), (150, 570), (150, 640)]; B = [(890, 500), (890, 600), (680, 600), (680, 640)]
        for q in (main, m2, m3, A, B): tube(q)
        flow(p, main, t, AIR, 3, 6, 6); flow(p, m2, t, AIR, 4, 4, 6); flow(p, m3, t, AIR, 4, 4, 6)
        flow(p, A if ext else B, t, AIR, 8, 6, 7); flow(p, B if ext else A, t, (90, 140, 190), 6, 6, 5, rev=True)
        # compressor
        p.rect(40, 130, 250, 270, fill=PANEL, outline=SKY, w=4, r=16, glow=True)
        p.circle(110, 200, 48, fill=(8, 26, 52), outline=(120, 190, 250), w=3)
        for s_ in range(5):
            a = TAU * 15 * t + s_ * TAU / 5; p.poly(rot_pts([(8, -6), (42, -16), (42, 16), (8, 6)], 110, 200, a), fill=(150, 200, 240))
        for y in range(160, 250, 18): p.line([(180, y), (235, y)], (60, 120, 190), 6)
        p.text("KOMPRESÖR", 145, 300, 20, ICE, var="Bold")
        # tank + gauge
        p.rect(330, 140, 620, 260, fill=(20, 54, 100), outline=SKY, w=4, r=60, glow=True)
        p.text("HAVA TANKI", 475, 200, 24, ICE, var="Bold")
        P = 116 + 3 * math.sin(TAU * 3 * t)
        p.circle(700, 95, 62, fill=(225, 232, 240), outline=(150, 165, 185), w=4); p.line([(700, 157), (700, 200)], (80, 150, 220), 10)
        for i in range(7):
            a = math.radians(135 + i * 45); p.line([(700 + 46 * math.cos(a), 95 + 46 * math.sin(a)), (700 + 56 * math.cos(a), 95 + 56 * math.sin(a))], (40, 50, 70), 3)
        a = math.radians(135 + P / 150 * 270); p.line([(700, 95), (700 + 46 * math.cos(a), 95 + 46 * math.sin(a))], RED, 5)
        p.circle(700, 95, 7, fill=(40, 50, 70)); p.text(f"{P:.0f} psi", 780, 95, 20, ICE, "lm", mono=True)
        # regulator
        p.rect(800, 165, 900, 235, fill=(30, 40, 56), outline=(160, 175, 195), w=3, r=8); p.text("REG", 850, 200, 18, ICE, var="Bold")
        # solenoid valve
        p.rect(760, 400, 940, 500, fill=(26, 34, 50), outline=(160, 175, 195), w=3, r=10)
        p.rect(940, 415, 990, 485, fill=(30, 90, 170) if ext else (24, 50, 90), r=6, glow=ext)
        p.circle(785, 425, 9, fill=(80, 255, 160) if ext else (20, 70, 50), glow=ext)
        p.text("SOLENOİD VALF", 850, 470, 18, ICE, var="Bold")
        # cylinder
        xp = 200 + 380 * e
        p.rect(xp + 30, 680, xp + 420, 720, fill=(190, 200, 215), outline=WHITE, w=2, r=8)
        p.rect(xp + 400, 650, xp + 440, 750, fill=(150, 160, 175), r=8)
        p.rect(110, 640, 720, 760, fill=(14, 40, 78), outline=SKY, w=5, r=18, glow=True)
        p.rect(130, 655, xp, 745, fill=(60, 140, 220) if ext else (24, 60, 110), r=10, a=110)
        p.rect(xp, 650, xp + 34, 750, fill=(200, 210, 222), r=6)
        p.text("PİSTON", 300, 800, 22, ICE, var="Bold")
        p.text("PNÖMATİK SİSTEM", 500, 930, 28, ICE, var="Bold")


# ===================================================================================================
_S = None
def _init(name, mode):
    global _S
    _S = D[name](Ctx(mode))
def _work(i): return _S.frame(i / NF).convert("RGB").tobytes()

def fname(name, mode):
    sub, pre = {"still": ("Telefon/", "ALFA 8084 - Elektronik "), "desk": ("Masaustu/", "ALFA 8084 - Elektronik Masaustu "),
                "anim": ("Hareketli/", "ALFA 8084 - Elektronik Hareketli ")}[mode]
    os.makedirs(OUT + sub, exist_ok=True); return OUT + sub + pre + name

def still(args):
    name, mode = args; t0 = time.time()
    S = D[name](Ctx(mode)); S.frame(S.still_t, still=True).convert("RGB").save(fname(name, mode) + ".jpg", quality=93)
    return f"{name} [{mode}] {time.time() - t0:.0f} s"

def anim(name, workers=12):
    import imageio_ffmpeg
    out = fname(name, "anim"); c = Ctx("anim")
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{c.W}x{c.H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", "-movflags", "+faststart", "-an", out + ".mp4"]
    t0 = time.time(); pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers, initializer=_init, initargs=(name, "anim")) as pool:
        for i, b in enumerate(pool.imap(_work, range(NF), chunksize=2)):
            pr.stdin.write(b)
            if i == 0: Image.frombytes("RGB", (c.W, c.H), b).save(out + " (kapak).jpg", quality=92)
    pr.stdin.close(); pr.wait()
    print(f"{name} [anim] {os.path.getsize(out + '.mp4') // 1024} KB, {time.time() - t0:.0f} s, rc={pr.returncode}", flush=True)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--test":
        name = next(n for n in D if n.startswith(a[1])); mode = a[2]; os.makedirs(OUT + "_test", exist_ok=True)
        S = D[name](Ctx(mode))
        for tt in map(float, a[3].split(",")):
            t0 = time.time(); S.frame(tt).convert("RGB").save(OUT + f"_test/{name[:2]}_{mode}_{tt:.2f}.jpg", quality=85); print(tt, f"{time.time() - t0:.2f}s")
        sys.exit()
    what = a[0] if a else "all"; names = [n for n in D if len(a) < 2 or any(n.startswith(x) for x in a[1:])]
    if what in ("still", "desk", "all"):
        jobs = [(n, m) for n in names for m in (("still", "desk") if what == "all" else (what,))]
        with Pool(8) as pool:
            for r in pool.imap_unordered(still, jobs): print(r, flush=True)
    if what in ("anim", "all"):
        for n in names: anim(n)
