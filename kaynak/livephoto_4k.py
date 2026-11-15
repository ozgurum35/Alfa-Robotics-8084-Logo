# iPhone Live Photo versions of the 17 animated phone wallpapers, drawn natively at 2160 x 4680 (Z = 2).
# Each pair: JPEG still 2160 x 4680 (first frame of the clip) + HEVC MOV 3 s (90 frames of the 10 s loop, see START), linked by a
# ContentIdentifier (see livephoto.py). The video is 2016 x 4368 (same 19.5:9 shape): that keeps it inside HEVC
# level 5.1, the level every 4K-recording iPhone decodes; 2160 x 4680 itself would need level 6.
# Usage: python livephoto_4k.py [NN ...]     (no number = all 17; 17 = storm design from hareketli.py)
import os, sys, time
os.environ["ALFA_Z"] = "2"
from multiprocessing import Pool
import imageio_ffmpeg
import hareketli2 as h2
import livephoto as lp

OUT = h2.ROOT + "Live Photo 4K/"
FRAMES = 90                     # 3 s at 30 fps
VW, VH = 2016, 4368
STORM = "17 Firtina"
# Clip start frame. The still is the first clip frame, so it must show the logo, and the clip must move:
# 12's particle burst starts at 3.3 s; 16's logo appears only at 3.3 s (frame 130 = full logo, then the light sweep).
START = {"12 Parcacik Logo": 100, "16 Isik Cizimi": 130}


def _storm(i):
    import hareketli as h1
    return h1.frame(i).tobytes()


def build(name, workers=8):
    t0 = time.time()
    if name == STORM:
        pool = Pool(workers)
        frames = pool.imap(_storm, range(FRAMES), chunksize=2)
    else:
        pool = Pool(workers, initializer=h2._init, initargs=(name,))
        s0 = START.get(name, 0); frames = pool.imap(h2._work, range(s0, s0 + FRAMES), chunksize=2)
    with pool:
        base = OUT + f"ALFA 8084 - Live Photo {name}"
        cid = lp.make_pair(frames, h2.W, h2.H, h2.FPS, base, VW, VH, imageio_ffmpeg.get_ffmpeg_exe())
    m = lp.read_mov(base + ".MOV"); j = lp.read_jpeg_cid(base + ".JPG")
    assert m["cid"] == cid == j and m["still"] and m["val"] == (9, 1, -1), (name, m, j)
    print(f"{name}: {os.path.getsize(base + '.MOV') // 1024} KB mov, {os.path.getsize(base + '.JPG') // 1024} KB jpg, "
          f"{time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    assert (h2.W, h2.H) == (2160, 4680)
    os.makedirs(OUT, exist_ok=True)
    names = list(h2.D) + [STORM]
    a = sys.argv[1:]
    for n in names:
        if not a or n[:2] in a: build(n)
