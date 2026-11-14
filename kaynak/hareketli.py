# ALFA Robotics 8084 animated phone wallpaper (storm theme): seamless 10 s loop, 1080 x 2340 (19.5:9), 30 fps, H.264 MP4.
# Dark storm clouds drift, lightning flickers at both sides, a large ghost wolf glows behind, the logo sways with a
# pulsing neon-blue rim; blue diagonal bars in the corners, wet reflective floor at the bottom.
# Every motion repeats a whole number of times per loop, so the video loops without a jump.
# Usage: python hareketli.py        (needs imageio-ffmpeg); output: Yeniden Olusturulan/Hareketli Duvar Kagidi/
import math, os, subprocess, sys
import numpy as np
import pymupdf
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, T = 1080, 2340, 30, 10.0
N = int(FPS * T)
SKY, ICE, NEON = (99, 196, 242), (208, 233, 232), (40, 140, 255)
ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/"
import guncel_logo
EM = guncel_logo.pdf("Amblem", "Koyu zemin")
OUT = ROOT + "Hareketli Duvar Kagidi/"
CX, CY = W / 2, round(0.555 * H)
LW = 640
FLOOR = round(0.885 * H)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
TAU = 2 * math.pi
rng = np.random.default_rng(8084)


def render(width):
    return guncel_logo.render(EM, width)
def solid(A, color, k=1.0):
    im = Image.new("RGBA", A.size, color + (255,)); im.putalpha(A.point(lambda v: int(min(255, v * k)))); return im
def fade(im, k):
    if k >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * max(0.0, k)))); return im
def to_img(rgb, a):
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), "RGBA")
def noise(w, h, octaves, seed):
    r = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32)
    for n, amp in octaves:
        small = r.random((max(2, round(n * h / w)), n)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray(small, "F").resize((w, h), Image.BICUBIC))
    acc -= acc.min(); return acc / acc.max()


# ---------- background: near-black navy, lighter behind the logo ----------
d = np.hypot((XX - CX) * 1.1, YY - CY * 0.9)
bg = np.array((2, 6, 16), np.float32) + (np.array((6, 26, 62), np.float32) * np.clip(1 - d / 1300, 0, 1)[..., None] ** 1.4)
BG = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

# ---------- storm clouds (wider than the screen; drift back and forth once per loop) ----------
CW = W + 240
n1 = noise(CW, H, ((4, 1.0), (8, 0.55), (16, 0.3), (32, 0.16), (64, 0.08)), 1)
n2 = noise(CW, H, ((6, 1.0), (12, 0.5), (24, 0.25), (48, 0.12)), 2)
cy_, cx_ = np.mgrid[0:H, 0:CW].astype(np.float32)
side = np.clip(np.abs(cx_ - CW / 2) / (W * 0.5), 0, 1) ** 0.8               # thicker at the sides
vert = np.exp(-((cy_ / H - 0.62) / 0.28) ** 2) + 0.55 * np.exp(-((cy_ / H - 0.22) / 0.2) ** 2)
dens = np.clip((n1 - 0.36) / 0.45, 0, 1) ** 1.1 * (0.45 + 0.55 * side) * vert
edge = np.clip((n2 - 0.5) / 0.35, 0, 1) * dens
crgb = np.array((18, 42, 86), np.float32) * dens[..., None] + np.array((70, 140, 240), np.float32) * edge[..., None] * 1.2
CLOUD = to_img(crgb / np.maximum(dens, 0.05)[..., None], np.clip(dens * 0.95, 0, 1))
CLOUD_LIT = to_img(np.array((90, 150, 255), np.float32) * np.ones_like(dens)[..., None], np.clip(edge * 0.8 + dens * 0.25, 0, 1))

# ---------- ghost wolf: upper part of the emblem, large and faint ----------
big = render(1500)
gw = big.crop((0, 0, big.width, round(big.height * 0.56)))
ga = np.asarray(gw).astype(np.float32) / 255
icy = np.clip(1 - np.abs(ga[..., :3] - np.array((208, 233, 232)) / 255).sum(-1) / 0.25, 0, 1)   # the ice-white wolf only
gal = icy * ga[..., 3]
gal *= np.clip(1 - (np.arange(gw.height)[:, None] / gw.height - 0.55) / 0.45, 0, 1)   # fade out downwards
GHOST = to_img(np.array((150, 190, 235), np.float32) * np.ones_like(gal)[..., None], gal * 0.30).filter(ImageFilter.GaussianBlur(2))
GHOST_POS = (round(CX - gw.width / 2 - 40), round(0.06 * H))
GHOST_GLOW = solid(GHOST.getchannel("A"), NEON, 1.4).filter(ImageFilter.GaussianBlur(30))

# ---------- lightning: three bolt sets, each flickers at its own time ----------
def bolt(p0, p1, disp, depth, r, out, branch=True):
    if depth == 0: out.append((p0, p1)); return
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
    m = (mx - dy / L * r.normal(0, disp), my + dx / L * r.normal(0, disp))
    bolt(p0, m, disp / 2, depth - 1, r, out, branch); bolt(m, p1, disp / 2, depth - 1, r, out, branch)
    if branch and depth > 3 and r.random() < 0.45:
        a = math.atan2(dy, dx) + r.choice((-1, 1)) * r.uniform(0.35, 0.8)
        e = (m[0] + math.cos(a) * L * 0.45, m[1] + math.sin(a) * L * 0.45); sub = []
        bolt(m, e, disp / 2, depth - 2, r, sub, False); out.extend((s[0], s[1], 1) for s in sub)
def bolt_layer(paths, seed):
    r = np.random.default_rng(seed); segs = []
    for p0, p1 in paths: bolt(p0, p1, 120, 8, r, segs)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(core)
    wide = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dw = ImageDraw.Draw(wide)
    for s in segs:
        thin = len(s) == 3; p, q = s[0], s[1]
        dw.line((p, q), fill=NEON + (255,), width=7 if thin else 16)
        dc.line((p, q), fill=(225, 240, 255, 255), width=2 if thin else 5)
    out = wide.filter(ImageFilter.GaussianBlur(45)); out.alpha_composite(wide.filter(ImageFilter.GaussianBlur(45)))
    out.alpha_composite(wide.filter(ImageFilter.GaussianBlur(8)))
    out.alpha_composite(core)
    return out
BOLTS = [bolt_layer([((-20, 0.30 * H), (CX - 280, 0.47 * H)), ((-20, 0.47 * H), (0.30 * W, 0.40 * H))], 11),
         bolt_layer([((W + 20, 0.27 * H), (CX + 300, 0.43 * H)), ((W + 20, 0.42 * H), (0.62 * W, 0.62 * H))], 12),
         bolt_layer([((W + 20, 0.55 * H), (0.62 * W, 0.70 * H)), ((-20, 0.62 * H), (0.22 * W, 0.70 * H))], 13)]
# (start as loop fraction, bolt set); each strike: flash, short dip, second flash, decay; a faint afterglow stays
STRIKES = [(0.06, 0), (0.30, 1), (0.34, 2), (0.58, 0), (0.62, 1), (0.84, 2)]
def strike(t, t0):
    u = ((t - t0) % 1.0) * T                               # seconds since the strike
    if u > 1.2: return 0.0
    f = math.exp(-u / 0.25)
    if 0.06 < u < 0.12: f *= 0.15                          # flicker
    return f

# ---------- corner bars, wet floor, fog ----------
fr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dfr = ImageDraw.Draw(fr)
def bars(x0, y0, sgn):
    for i, (off, w, a, col) in enumerate(((0, 26, 0.9, (30, 90, 255)), (60, 10, 0.7, (60, 140, 255)), (110, 46, 0.35, (20, 50, 140)),
                                           (190, 8, 0.6, (80, 170, 255)), (240, 70, 0.22, (14, 30, 80)))):
        L = 820; dx, dy = 0.55, -0.835                     # about 57 degrees
        ox, oy = x0 + sgn * off, y0 + sgn * off * 0.6
        p = [(ox, oy), (ox + dx * L * sgn, oy + dy * L * sgn), (ox + dx * L * sgn + sgn * w, oy + dy * L * sgn + sgn * w * 0.6), (ox + sgn * w, oy + sgn * w * 0.6)]
        dfr.polygon(p, fill=col + (int(255 * a),))
bars(-260, 560, 1); bars(W + 260, H - 560, -1)
BARS = fr.filter(ImageFilter.GaussianBlur(14)); BARS.alpha_composite(fr)
fl = np.zeros((H, W), np.float32); fy = (YY - FLOOR) / (H - FLOOR)
floor_rgb = np.array((4, 10, 22), np.float32) + np.array((10, 40, 90), np.float32) * np.exp(-((XX - CX) / 420) ** 2)[..., None] * np.clip(1 - fy, 0, 1)[..., None]
sr = np.random.default_rng(5).random((160, 6)).astype(np.float32)
streak = np.asarray(Image.fromarray(sr, "F").resize((W, H), Image.BICUBIC))
floor_rgb += (np.clip((streak - 0.5) / 0.45, 0, 1) * 70 * np.exp(-((XX - CX) / 520) ** 2))[..., None] * np.array((0.45, 0.75, 1.0), np.float32)
FLOOR_IMG = to_img(floor_rgb, (YY >= FLOOR).astype(np.float32) * 0.97)
FLOOR_LINE = to_img(np.array((60, 140, 255), np.float32) * np.ones((H, W, 1), np.float32), np.exp(-((YY - FLOOR) / 4) ** 2) * 0.7)
fog_n = noise(W + 300, H, ((5, 1.0), (10, 0.5), (20, 0.25)), 6)
FOG = to_img(np.array((70, 110, 170), np.float32) * np.ones((H, W + 300, 1), np.float32),
             np.exp(-(((np.mgrid[0:H, 0:W + 300][0] - FLOOR + 60) / 110) ** 2)) * (0.25 + 0.5 * fog_n) * 0.55)
FLOOR_GLOW = to_img(np.array(NEON, np.float32) * np.ones((H, W, 1), np.float32),
                    (YY >= FLOOR) * np.exp(-((XX - CX) / 260) ** 2) * np.clip(1 - fy * 1.3, 0, 1) * 0.5)

# ---------- logo with neon rim ----------
L = render(LW); A = L.getchannel("A")
PAD = 200
def padded(im):
    c = Image.new(im.mode, (im.width + 2 * PAD, im.height + 2 * PAD), 0 if im.mode == "L" else (0, 0, 0, 0)); c.paste(im, (PAD, PAD)); return c
AP = padded(A)
ring = AP
for _ in range(2): ring = ring.filter(ImageFilter.MaxFilter(9))
RIM = solid(ring, (90, 200, 255))
RIM_GLOW = solid(ring, NEON).filter(ImageFilter.GaussianBlur(26))
BIG_GLOW = solid(AP, NEON).filter(ImageFilter.GaussianBlur(110))
SHADOW = solid(AP, (0, 0, 0), 0.8).filter(ImageFilter.GaussianBlur(28))
LP = padded(L)
REFL = fade(L.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(10)), 0.22)

f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 40); f.set_variation_by_name("SemiBold")
FOOT = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); fd = ImageDraw.Draw(FOOT)
label = "F R C   T E A M   8 0 8 4"; tw = fd.textlength(label, font=f)
fd.text((W / 2, 60), label, font=f, fill=(170, 185, 200, 230), anchor="mm")
for s in (-1, 1):
    x0 = W / 2 + s * (tw / 2 + 36); fd.line((x0, 60, x0 + s * 200, 60), fill=(140, 155, 170, 160), width=3)
FOOT_Y = round(0.835 * H) - 60


def frame(i):
    t = i / N
    im = BG.copy()
    fl = [strike(t, t0) for t0, _ in STRIKES]
    flash = min(1.0, max(fl))
    ox = round(-120 + 90 * math.sin(TAU * t))                     # cloud drift
    im.alpha_composite(CLOUD.crop((-ox, 0, -ox + W, H)))
    if flash > 0.02: im.alpha_composite(fade(CLOUD_LIT.crop((-ox, 0, -ox + W, H)), flash))
    gk = 0.75 + 0.25 * math.sin(TAU * 2 * t) + 0.6 * flash
    im.alpha_composite(fade(GHOST_GLOW, 0.35 * gk), GHOST_POS); im.alpha_composite(fade(GHOST, min(1, gk)), GHOST_POS)
    for (t0, b), k in zip(STRIKES, fl):
        if k > 0.01: im.alpha_composite(fade(BOLTS[b], k))
    for b in range(3):                                            # faint afterglow so the sky never looks empty
        im.alpha_composite(fade(BOLTS[b], 0.30 + 0.12 * math.sin(TAU * (b + 1) * t + b)))
    im.alpha_composite(BARS)
    # floor, reflection and fog (fog drifts the other way)
    im.alpha_composite(FLOOR_IMG)
    pulse = 0.5 + 0.5 * math.sin(TAU * 2 * t - 1.0)
    im.alpha_composite(fade(FLOOR_GLOW, 0.6 + 0.4 * pulse + 0.8 * flash))
    im.alpha_composite(fade(FLOOR_LINE, 0.6 + 0.4 * flash))
    fx = round(-150 - 120 * math.sin(TAU * t))
    im.alpha_composite(FOG.crop((-fx, 0, -fx + W, H)))
    # logo: sway +-3 deg once per loop, float up and down twice per loop, neon pulse twice per loop
    a = 3.0 * math.sin(TAU * t)
    bob = 16 * math.sin(TAU * 2 * t + 0.5)
    x0, y0 = round(CX - LP.width / 2), round(CY - LP.height / 2 + bob)
    def put(layer, k, dy=0):
        r = layer.rotate(a, resample=Image.BICUBIC)
        im.alpha_composite(fade(r, k), (x0, y0 + dy))
    put(BIG_GLOW, 0.35 + 0.35 * pulse + 0.3 * flash)
    put(SHADOW, 1.0, 24)
    put(RIM_GLOW, 0.55 + 0.45 * pulse)
    put(RIM, 0.75 + 0.25 * pulse)
    put(LP, 1.0)
    rf = REFL.crop((0, 0, REFL.width, min(REFL.height, H - FLOOR)))
    im.alpha_composite(fade(rf, 0.8 + 0.4 * flash if flash else 0.8), (round(CX - REFL.width / 2), FLOOR + 6))
    im.alpha_composite(FOOT, (0, FOOT_Y))
    return im.convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    if only:                                                     # quick check: save single frames
        for i in only: frame(i).save(OUT + f"_kare{i}.jpg", quality=90)
        sys.exit()
    out = OUT + "ALFA 8084 - Hareketli Duvar Kagidi.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
           "-movflags", "+faststart", "-an", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(N):
        fr = frame(i)
        if i == 0: fr.save(OUT + "ALFA 8084 - Hareketli Duvar Kagidi (kapak).jpg", quality=95)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    print(out, p.returncode, os.path.getsize(out) // 1024, "KB")
