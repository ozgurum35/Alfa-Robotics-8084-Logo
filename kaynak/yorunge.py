# ALFA 8084 orbit wallpapers: real FRC parts (official CAD) or the swerve robot circling the neon logo.
# python yorunge.py still|desk|anim|all [parcalar|robot]      (preview: python yorunge.py test <name> <mode>)
import json, math, os, subprocess, sys, time
from PIL import Image
from urun3d import P, BL, HERE, ROOT

OUT = os.path.join(ROOT, "Yeniden Olusturulan", "3D Yorunge Duvar Kagitlari")
WORK = os.path.join(OUT, "_render")
FPS, NF = 30, 300
MIX = ["kraken_x60", "pdh", "vortex", "roborio", "sparkmax", "mk4i", "limelight"]
KEEP = ("parts", "builtin", "rot", "order", "hide", "offsets", "paint", "az", "el")
FACE = {"kraken_x60": dict(az=135, el=12), "limelight": dict(az=0, el=6), "pdh": dict(az=-20, el=50)}   # logo side to the camera (six-view check)      # orbit-only view tweaks so the brand side faces the camera

SCENES = {
    "parcalar": dict(name="01 FRC Parcalari", kind="parts", items=[dict({k: v for k, v in P[n].items() if k in KEEP}, **FACE.get(n, {})) for n in MIX],
                     size=0.56, R=1.15, logo_h=1.0, el=12,
                     phone=dict(ring=[68, 0, 18], lens=85, R=1.35, size=0.8, logo_h=1.5, stretch=1.45), desk=dict(ring=[13, -9, 0], R=1.55)),
    "robot": dict(name="02 Swerve Robot", kind="robot", ride=0.85, bumpers=True, path_r=1.3, tha=0.0, floor=-0.98, R=1.3, size=0.9, rob_scale=1.5,
                  el=26, tz=-0.3, ring=[0, 0, 0], pose=0.86, lens=70, logo_h=1.2, phone=dict(lens=85, path_r=0.95, el=35, logo_h=1.4), desk=dict()),
}


class Ctx:
    def __init__(self, mode):
        self.mode = mode
        if mode == "desk":
            self.W, self.H = 3840, 2160; self.k = 2; self.box = (0, 30, 3840, 1960); self.foot = (1920, 2040)
        else:
            self.W, self.H = (1080, 2340) if mode == "anim" else (2160, 4680); self.k = self.W / 1080
            self.box = (0, round(0.21 * self.H), self.W, round(0.885 * self.H)); self.foot = (self.W / 2, 0.93 * self.H)
        self.logo = (self.W / 2, self.H / 2, 0)


def logo_mask():
    p = os.path.join(WORK, "logo_mask.png")
    if not os.path.exists(p):
        from hareketli2 import neon
        os.makedirs(WORK, exist_ok=True); neon(1600)["L"].save(p)
    return p


def render(scene, mode, out, samples, frames=None):
    c = Ctx(mode); sp = dict(SCENES[scene]); sp.update(sp.pop("desk" if mode == "desk" else "phone")); sp.pop("phone", None); sp.pop("desk", None)
    sp.update(w=round(c.box[2] - c.box[0]), h=round(c.box[3] - c.box[1]), samples=samples, frames=frames, out=out, logo=logo_mask())
    f = os.path.join(WORK, f"{scene}_{mode}_spec.json"); json.dump(sp, open(f, "w", encoding="utf-8"))
    r = subprocess.run([BL, "-b", "--python", os.path.join(HERE, "yorunge_blender.py"), "--", f], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if "DONE" not in r.stdout: print(r.stdout[-3000:], r.stderr[-2000:]); raise SystemExit("render failed")


class Comp:
    def __init__(self, scene, mode, meta):
        from elektronik import background
        from hareketli2 import neon
        self.c = c = Ctx(mode); m = json.load(open(meta))
        self.lw = m["x1"] - m["x0"]; self.lc = (c.box[0] + (m["x0"] + m["x1"]) / 2, c.box[1] + (m["y0"] + m["y1"]) / 2)
        self.BG = background(c, (8, 40, 88), (0, 4, 14)); self.N = neon(round(self.lw))

    def frame(self, prod, pulse=0.5, rect=None):
        """rect: the logo as Blender posed it this frame (centre, width, angle) - neon drawn exactly over its holdout"""
        from hareketli2 import draw_logo
        from elektronik import footer
        im = self.BG.copy(); lc, sx, ang = self.lc, 1.0, 0.0
        if rect: lc, sx, ang = (self.c.box[0] + rect["cx"], self.c.box[1] + rect["cy"]), rect["lw"] / self.lw, rect["ang"]
        draw_logo(im, self.N, *lc, ang=ang, pulse=pulse, big=0.85, sx=sx)
        im.alpha_composite(prod, (round(self.c.box[0]), round(self.c.box[1])))
        footer(im, self.c)
        return im.convert("RGB")


def fname(scene, mode):
    sub = {"still": "Telefon", "desk": "Masaustu", "anim": "Hareketli"}[mode]
    d = os.path.join(OUT, sub); os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"ALFA 8084 - Yorunge {'Masaustu ' if mode == 'desk' else 'Hareketli ' if mode == 'anim' else ''}{SCENES[scene]['name']}")


def make_still(scene, mode, samples=128, out=None):
    png = os.path.join(WORK, f"{scene}_{mode}.png"); render(scene, mode, png, samples)
    rect = json.load(open(png + ".logo.json"))
    Comp(scene, mode, png + ".json").frame(Image.open(png).convert("RGBA"), rect=rect).save(out or fname(scene, mode) + ".jpg", quality=93)


def make_anim(scene, samples=24, chunk=100):
    import imageio_ffmpeg
    c = Ctx("anim"); fd = os.path.join(WORK, f"{scene}_frames")
    for a in range(0, NF, chunk):
        if not all(os.path.exists(os.path.join(fd, f"{i:03d}.png")) for i in range(a, min(NF, a + chunk))):
            render(scene, "anim", fd, samples, frames=[a, min(NF, a + chunk)])
    cp = Comp(scene, "anim", fd + ".json"); out = fname(scene, "anim")
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{c.W}x{c.H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", "-movflags", "+faststart", "-an", out + ".mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NF):
        rect = json.load(open(os.path.join(fd, f"{i:03d}.json")))
        f = cp.frame(Image.open(os.path.join(fd, f"{i:03d}.png")).convert("RGBA"), 0.5 + 0.5 * math.sin(2 * math.pi * 3 * i / NF), rect)
        if i == 0: f.save(out + " (kapak).jpg", quality=92)
        pr.stdin.write(f.tobytes())
    pr.stdin.close(); pr.wait(); print(scene, "anim", os.path.getsize(out + ".mp4") // 1024, "KB", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "test":
        os.makedirs(WORK, exist_ok=True); make_still(a[1], a[2], samples=32, out=os.path.join(WORK, f"test_{a[1]}_{a[2]}.jpg")); sys.exit()
    names = a[1:] or list(SCENES)
    for n in names:
        for m in (("still", "desk", "anim") if a[0] == "all" else (a[0],)):
            t0 = time.time(); make_anim(n) if m == "anim" else make_still(n, m); print(n, m, f"{time.time() - t0:.0f} s", flush=True)
