# FRC product 3D wallpapers: renders official CAD with Blender (urun3d_blender.py) and composites the layout.
# python urun3d.py preview            -> low-res still of every product (contact sheet)
# python urun3d.py still|desk|anim [names...]
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = "D:/CLAUDE/Araclar/Blender/blender.exe"
CAD = "D:/CLAUDE/Araclar/cad/"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "Yeniden Olusturulan", "3D Urun Duvar Kagitlari", "_render")

P = {
    "kraken_x60": dict(parts=["kraken_x60.step"], rot=[80, -90, 0], order="YXZ", brand="CTRE / WCP", model="KRAKEN X60",
                       sub="Fırçasız motor · dahili Talon FX", az=-35, el=14),
    "kraken_x44": dict(parts=["kraken_x44.step"], rot=[80, -90, 0], order="YXZ", brand="CTRE / WCP", model="KRAKEN X44",
                       sub="Kompakt fırçasız motor · dahili Talon FX", az=-35, el=14),
    "vortex": dict(parts=["neo_vortex_spark_flex.step"], hide=["REV-11-2159-P08", "REV-11-2159-P03"], rot=[-90, 0, 0],
                   brand="REV ROBOTICS", model="NEO VORTEX + SPARK FLEX", sub="Fırçasız motor ve takılı sürücü", az=-35, el=16),
    "neo": dict(parts=["neo_v11.step"], brand="REV ROBOTICS", model="NEO V1.1", sub="Fırçasız motor", az=-35, el=14,
                paint=dict(mode="face", default="alu", rules=[dict(mat="steel", rax="z", rmax=6.5),
                                                               dict(mat="black", rax="z", rmin=31.5)])),
    "neo550": dict(parts=["neo550.step"], rot=[0, 90, 0], brand="REV ROBOTICS", model="NEO 550", sub="Küçük fırçasız motor",
                   az=-35, el=14, paint=dict(mode="face", default="alu", rules=[dict(mat="steel", rax="x", rmax=3.2),
                                                                                  dict(mat="white", rax="x", rmin=18.6)])),
    "sparkmax": dict(parts=["spark_max.step"], brand="REV ROBOTICS", model="SPARK MAX", sub="Motor sürücü", az=-30, el=28,
                     paint=dict(mode="part", default="black", rules=[dict(mat="copper", dmax=6)])),
    "roborio": dict(parts=["roborio2.step"], brand="NI", model="roboRIO 2.0", sub="Robot ana denetleyicisi", az=-25, el=38),
    "pdh": dict(parts=["pdh.step"], rot=[90, 0, 0], brand="REV ROBOTICS", model="POWER DISTRIBUTION HUB",
                sub="Güç dağıtım kartı", az=-25, el=38, paint="PDH"),
    "ctre_sens": dict(parts=["pigeon2/Pigeon 2.STEP", "cancoder/Housing.STEP", "cancoder/PCB Assembly.STEP", "canivore/CANivore.STEP"],
                      offsets=[[0, 0, 0], [-50, 0, 0], [-50, 0, 0], [58, 0, 0]], brand="CTRE",
                      model="PIGEON 2 · CANcoder · CANivore", sub="IMU · mutlak enkoder · CAN FD", az=-25, el=34),
    "mk4i": dict(parts=["mk4i_falcon.step"], rot=[90, 0, 0], brand="SWERVE DRIVE SPECIALTIES", model="MK4i",
                 sub="Swerve modülü", az=-35, el=18),
    "battery": dict(builtin="battery", parts=["breaker120.step"], offsets=[[160, 0, 30, 90, 0, 0]], brand="MK / ANDYMARK",
                    model="12V AKÜ + 120A SİGORTA", sub="ES17-12 akü · ana devre kesici", az=-30, el=18),
    "sasi": dict(builtin="chassis", brand="ALFA ROBOTICS 8084", model="SWERVE ŞASİ", sub="4× SDS MK4i · roboRIO 2 · PDH · 8084 tamponları",
                 az=-38, el=30, pose=0.1),
    "swerve": dict(builtin="chassis", bumpers=False, brand="SDS MK4i × 4", model="SWERVE SÜRÜŞ", sub="Gerçek swerve kinematiği · yön + tekerlek",
                   az=-38, el=16, pose=0.3),
    "radio": dict(parts=["vh109.step"], brand="VIVID-HOSTING", model="VH-109", sub="FRC robot radyosu", az=-30, el=28),
    "limelight": dict(parts=["limelight4.step"], rot=[0, 180, 180], brand="LIMELIGHT", model="LIMELIGHT 4",
                      sub="Akıllı görüntü işleme kamerası", az=-30, el=14),
}


def render(name, out, w, h, samples, frames=None, fill=0.82):
    p = P[name]
    spec = {k: v for k, v in p.items() if k in ("builtin", "rot", "order", "pose", "path_r", "rail_bottom", "bumpers", "hide", "az", "el", "lens", "offsets", "paint")}
    spec.update(parts=[CAD + x for x in p.get("parts", [])], w=w, h=h, samples=samples, frames=frames, out=out, fill=fill)
    os.makedirs(WORK, exist_ok=True)
    sp = os.path.join(WORK, f"{name}_spec.json"); json.dump(spec, open(sp, "w", encoding="utf-8"))
    r = subprocess.run([BL, "-b", "--python", os.path.join(HERE, "urun3d_blender.py"), "--", sp],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "DONE" not in r.stdout:
        print(r.stdout[-3000:], r.stderr[-2000:]); raise SystemExit(f"render failed: {name}")


def preview(names):
    from PIL import Image, ImageDraw
    s = 420; d = os.path.join(WORK, "preview"); os.makedirs(d, exist_ok=True)
    for n in names:
        render(n, os.path.join(d, n + ".png"), s, s, 24); print("ok", n, flush=True)
    cols = 5; rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * s, rows * s), (14, 22, 40)); dr = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        im = Image.open(os.path.join(d, n + ".png")).convert("RGBA")
        sheet.paste(im, ((i % cols) * s, (i // cols) * s), im); dr.text(((i % cols) * s + 6, (i // cols) * s + 6), n, fill="yellow")
    sheet.save(os.path.join(d, "sheet.jpg"), quality=88)


# ---------------------------------------------------------------------------------------------- layout
OUT = os.path.join(ROOT, "Yeniden Olusturulan", "3D Urun Duvar Kagitlari")
NUM = {n: i + 1 for i, n in enumerate(P)}
FPS, NF = 30, 300


def lay(mode):
    """product box, caption anchor and logo/footer positions per format"""
    from elektronik import Ctx
    c = Ctx(mode)
    if mode == "desk":
        c.box = (1640, 60, 3800, 1680); c.cap = (2720, 1715); c.logo = (0.235 * c.W, 0.45 * c.H, 1000); c.foot = (0.235 * c.W, 1720)
    else:
        W, H = c.W, c.H; c.box = (0, round(0.455 * H), W, round(0.815 * H)); c.cap = (W / 2, 0.828 * H)
    return c


def caption(im, c, p):
    from PIL import Image, ImageDraw
    from hareketli2 import font, ICE, paste, blur
    k = c.k; x, y = c.cap
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    fb, fm, fs = font(round(30 * k), "SemiBold"), font(round(66 * k), "Bold"), font(round(30 * k), "SemiBold")
    mf = fm
    while d.textlength(p["model"], font=mf) > (c.box[2] - c.box[0]) * 0.9: mf = font(round(mf.size * 0.92), "Bold")
    brand = "  ".join(" ".join(w) for w in p["brand"].split())
    d.text((x, y), brand, font=fb, fill=(120, 190, 255, 235), anchor="mt")
    y2 = y + 52 * k; d.text((x, y2), p["model"], font=mf, fill=(255, 255, 255, 255), anchor="mt")
    y3 = y2 + mf.size * 1.12 + 14 * k
    tw = d.textlength(p["sub"], font=fs); d.text((x, y3), p["sub"], font=fs, fill=ICE + (200,), anchor="mt")
    for sg in (-1, 1):
        x0 = x + sg * (tw / 2 + 28 * k); d.line((x0, y3 + 17 * k, x0 + sg * 120 * k, y3 + 17 * k), fill=(120, 190, 255, 130), width=max(1, round(2 * k)))
    g = blur(L, 10 * k); im.alpha_composite(g); im.alpha_composite(L)


class Scene:
    def __init__(self, name, mode):
        from elektronik import background
        from hareketli2 import neon
        from PIL import Image, ImageDraw
        self.n, self.p, self.c = name, P[name], lay(mode)
        bg = background(self.c, (8, 40, 88), (0, 4, 14))
        bx0, by0, bx1, by1 = self.c.box; cx, cy = (bx0 + bx1) / 2, by0 + (by1 - by0) * 0.6
        sp = Image.new("RGBA", bg.size, (0, 0, 0, 0)); ImageDraw.Draw(sp).ellipse(
            (cx - (bx1 - bx0) * 0.38, cy - (by1 - by0) * 0.33, cx + (bx1 - bx0) * 0.38, cy + (by1 - by0) * 0.33), fill=(40, 120, 255, 70))
        from hareketli2 import blur
        bg.alpha_composite(blur(sp, (bx1 - bx0) * 0.12)); caption(bg, self.c, self.p)
        self.BG = bg; self.N = neon(round(self.c.logo[2]))

    def frame(self, prod, pulse=0.5):
        from elektronik import footer
        from hareketli2 import draw_logo
        if not hasattr(self, "M") or self.M.size != prod.size:   # soft edges so the floor shadow never ends in a hard line
            import numpy as np
            from PIL import Image
            w, h = prod.size; f = 0.1
            ex = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / (f * w), 0, 1)
            ey = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / (f * h), 0, 1)
            self.M = Image.fromarray((np.outer(ey ** 1.5, ex ** 1.5) * 255).astype(np.uint8), "L")
        from PIL import ImageChops
        prod = prod.copy(); prod.putalpha(ImageChops.multiply(prod.getchannel("A"), self.M))
        im = self.BG.copy(); im.alpha_composite(prod, (round(self.c.box[0]), round(self.c.box[1])))
        lx, ly, _ = self.c.logo; draw_logo(im, self.N, lx, ly, pulse=pulse, big=0.5); footer(im, self.c)
        return im.convert("RGB")


def fname(name, mode):
    sub, pre = {"still": ("Telefon", "ALFA 8084 - 3D "), "desk": ("Masaustu", "ALFA 8084 - 3D Masaustu "),
                "anim": ("Hareketli", "ALFA 8084 - 3D Hareketli ")}[mode]
    d = os.path.join(OUT, sub); os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{pre}{NUM[name]:02d} {P[name]['model'].replace('/', '-').replace('·', '-')}")


def make_still(name, mode, samples=160):
    from PIL import Image
    c = lay(mode); bw, bh = round(c.box[2] - c.box[0]), round(c.box[3] - c.box[1])
    png = os.path.join(WORK, f"{name}_{mode}.png"); render(name, png, bw, bh, samples)
    Scene(name, mode).frame(Image.open(png).convert("RGBA")).save(fname(name, mode) + ".jpg", quality=93)


def make_anim(name, samples=24, chunk=50):
    import math, imageio_ffmpeg
    from PIL import Image
    c = lay("anim"); bw, bh = round(c.box[2] - c.box[0]), round(c.box[3] - c.box[1]); fd = os.path.join(WORK, name + "_frames")
    todo = [a for a in range(0, NF, chunk) if not all(os.path.exists(os.path.join(fd, f"{i:03d}.png")) for i in range(a, min(NF, a + chunk)))]
    for a in todo: render(name, fd, bw, bh, samples, frames=[a, min(NF, a + chunk)], fill=0.8)
    sc = Scene(name, "anim"); out = fname(name, "anim")
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{c.W}x{c.H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", "-movflags", "+faststart", "-an", out + ".mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NF):
        f = sc.frame(Image.open(os.path.join(fd, f"{i:03d}.png")).convert("RGBA"), 0.5 + 0.5 * math.sin(2 * math.pi * 2 * i / NF))
        if i == 0: f.save(out + " (kapak).jpg", quality=92)
        pr.stdin.write(f.tobytes())
    pr.stdin.close(); pr.wait(); print(name, "anim", os.path.getsize(out + ".mp4") // 1024, "KB", flush=True)


if __name__ == "__main__":
    import time
    mode, names = sys.argv[1], sys.argv[2:] or list(P)
    if mode == "preview": preview(names); sys.exit()
    for n in names:
        t0 = time.time()
        for m in (("still", "desk", "anim") if mode == "all" else (mode,)):
            make_anim(n) if m == "anim" else make_still(n, m)
            print(n, m, f"{time.time() - t0:.0f} s", flush=True)
