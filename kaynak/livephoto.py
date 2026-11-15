# Writes an Apple Live Photo pair (JPEG + MOV) without macOS tools.
# The pair is linked by one ContentIdentifier (UUID):
#   JPEG: Apple MakerNote tag 0x0011 (Make = Apple so ImageIO parses the maker note)
#   MOV : moov/meta mdta key com.apple.quicktime.content.identifier (written by ffmpeg)
#         + a timed metadata track ('mebx') with com.apple.quicktime.still-image-time = -1 at t = 0,
#         which marks the still image's place in the movie (here: the first frame).
# Usage as module: make_pair(frames_iter, w, h, fps, still_img, out_base, vw, vh)
import struct, subprocess, uuid
from PIL import Image

STILL_KEY = b"com.apple.quicktime.still-image-time"


def box(t, payload): return struct.pack(">I", 8 + len(payload)) + t + payload
def fbox(t, ver, flags, payload): return box(t, struct.pack(">I", (ver << 24) | flags) + payload)


def boxes(b, start=0, end=None):
    """Yield (type, payload_start, box_end) of the boxes in b[start:end]."""
    i, end = start, len(b) if end is None else end
    while i + 8 <= end:
        size, t = struct.unpack(">I4s", b[i:i + 8]); hdr = 8
        if size == 1: size = struct.unpack(">Q", b[i + 8:i + 16])[0]; hdr = 16
        elif size == 0: size = end - i
        yield t, i + hdr, i + size
        i += size


# ---------------- JPEG ----------------
def apple_makernote(cid):
    s = cid.encode() + b"\x00"
    n = 2; ifd = 14; data = ifd + 2 + 12 * n + 4
    out = b"Apple iOS\x00" + b"\x00\x01" + b"MM" + struct.pack(">H", n)
    out += struct.pack(">HHII", 0x0001, 9, 1, 14)                 # MakerNoteVersion, SLONG
    out += struct.pack(">HHII", 0x0011, 2, len(s), data)          # ContentIdentifier, ASCII
    return out + b"\x00\x00\x00\x00" + s


def write_jpeg(img, path, cid, quality=95):
    ex = Image.Exif()
    ex[0x010F] = "Apple"; ex[0x0131] = "ALFA 8084 Live Photo"
    ex.get_ifd(0x8769)[0x927C] = apple_makernote(cid)
    img.convert("RGB").save(path, "JPEG", quality=quality, exif=ex.tobytes(), subsampling=0)


def read_jpeg_cid(path):
    ex = Image.open(path).getexif().get_ifd(0x8769); mn = ex.get(0x927C)
    if not mn or not mn.startswith(b"Apple iOS\x00"): return None
    n = struct.unpack(">H", mn[14:16])[0]
    for k in range(n):
        tag, typ, cnt, val = struct.unpack(">HHII", mn[16 + 12 * k:28 + 12 * k])
        if tag == 0x0011: return mn[val:val + cnt].rstrip(b"\x00").decode()


# ---------------- MOV ----------------
def still_track(track_id, mts, offset, movie_dur):
    """Timed metadata track holding one still-image-time sample (int8 -1) at media time 0."""
    sdur = 1
    ident = struct.pack(">9I", 0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000)
    tkhd = fbox(b"tkhd", 0, 1, struct.pack(">IIIII", 0, 0, track_id, 0, movie_dur) + b"\0" * 8
                + struct.pack(">hhhh", 0, 0, 0, 0) + ident + struct.pack(">II", 0, 0))
    mdhd = fbox(b"mdhd", 0, 0, struct.pack(">IIIIHH", 0, 0, mts, sdur, 0x55C4, 0))
    hdlr = fbox(b"hdlr", 0, 0, b"mhlr" + b"meta" + b"\0" * 12 + b"\0")
    gmhd = box(b"gmhd", fbox(b"gmin", 0, 0, struct.pack(">HHHHhH", 0x40, 0x8000, 0x8000, 0x8000, 0, 0)))
    dinf = box(b"dinf", fbox(b"dref", 0, 0, struct.pack(">I", 1) + fbox(b"alis", 0, 1, b"")))
    key = box(struct.pack(">I", 1), box(b"keyd", b"mdta" + STILL_KEY) + box(b"dtyp", struct.pack(">II", 0, 65)))
    mebx = box(b"mebx", b"\0" * 6 + struct.pack(">H", 1) + box(b"keys", key))
    stbl = box(b"stbl", fbox(b"stsd", 0, 0, struct.pack(">I", 1) + mebx)
               + fbox(b"stts", 0, 0, struct.pack(">III", 1, 1, sdur))
               + fbox(b"stsc", 0, 0, struct.pack(">IIII", 1, 1, 1, 1))
               + fbox(b"stsz", 0, 0, struct.pack(">II", 9, 1))
               + fbox(b"stco", 0, 0, struct.pack(">II", 1, offset)))
    return box(b"trak", tkhd + box(b"mdia", mdhd + hdlr + box(b"minf", gmhd + dinf + stbl)))


def cid_meta(cid):
    """moov/meta (QuickTime style, no version field): hdlr mdta + keys + ilst with the content identifier."""
    k = b"com.apple.quicktime.content.identifier"
    hdlr = fbox(b"hdlr", 0, 0, b"\0" * 4 + b"mdta" + b"\0" * 12 + b"\0")
    keys = fbox(b"keys", 0, 0, struct.pack(">I", 1) + box(b"mdta", k))
    ilst = box(b"ilst", box(struct.pack(">I", 1), box(b"data", struct.pack(">II", 1, 0) + cid.encode())))
    return box(b"meta", hdlr + keys + ilst)


def add_still_track(path, cid):
    b = open(path, "rb").read()
    top = list(boxes(b))
    mv = [x for x in top if x[0] == b"moov"]; assert len(mv) == 1 and mv[0][2] == len(b), "moov must be last (no faststart)"
    _, ms, me = mv[0]; moov_start = ms - 8
    kids = list(boxes(b, ms, me))
    mvhd = next(x for x in kids if x[0] == b"mvhd"); p = mvhd[1]
    assert b[p] == 0, "mvhd v0 expected"
    mts, mdur = struct.unpack(">II", b[p + 12:p + 20]); next_id = struct.unpack(">I", b[mvhd[2] - 4:mvhd[2]])[0]
    sample = struct.pack(">II", 9, 1) + b"\xff"                 # [size][local key id 1][int8 -1]
    mdat = box(b"mdat", sample); offset = moov_start + 8
    trak = still_track(next_id, mts, offset, 1)
    body = b""
    for t, s, e in kids:
        if t in (b"udta", b"meta"): continue                      # ffmpeg tags; replaced by our moov/meta
        chunk = b[s - 8:e]
        if t == b"mvhd": chunk = chunk[:-4] + struct.pack(">I", next_id + 1)
        body += chunk
    new_moov = box(b"moov", body + trak + cid_meta(cid))
    open(path, "wb").write(b[:moov_start] + mdat + new_moov)


def read_mov(path):
    """Return (content identifier, has still-image-time track, sample value) for checking."""
    b = open(path, "rb").read(); out = {"cid": None, "still": False, "val": None}
    def walk(s, e, depth):
        for t, ps, pe in boxes(b, s, e):
            if t == b"meta" and depth == 1:
                kk = list(boxes(b, ps, pe))
                keys = next((x for x in kk if x[0] == b"keys"), None); ilst = next((x for x in kk if x[0] == b"ilst"), None)
                names = []; k = keys[1] + 8
                for _ in range(struct.unpack(">I", b[keys[1] + 4:keys[1] + 8])[0]):
                    sz = struct.unpack(">I", b[k:k + 4])[0]; names.append(b[k + 8:k + sz]); k += sz
                for it, ips, ipe in boxes(b, ilst[1], ilst[2]):
                    i = struct.unpack(">I", it)[0]
                    for dt, dps, dpe in boxes(b, ips, ipe):
                        if dt == b"data" and names[i - 1] == b"com.apple.quicktime.content.identifier": out["cid"] = b[dps + 8:dpe].decode()
            if t in (b"moov", b"trak", b"mdia", b"minf", b"stbl"): walk(ps, pe, depth + 1)
            if t == b"stsd" and STILL_KEY in b[ps:pe]: out["still"] = True
            if t == b"stco" and out["still"] and out["val"] is None:
                off = struct.unpack(">I", b[ps + 8:ps + 12])[0]; out["val"] = struct.unpack(">IIb", b[off:off + 9])
    walk(0, len(b), 0)
    return out


def make_pair(frames, w, h, fps, out_base, vw, vh, ffmpeg, crf=20):
    """frames: iterable of RGB bytes (w x h). First frame becomes the still. Writes out_base + .JPG/.MOV"""
    cid = str(uuid.uuid4()).upper()
    mov = out_base + ".MOV"
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
           "-vf", f"scale={vw}:{vh}:flags=lanczos", "-c:v", "libx265", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-tag:v", "hvc1", "-x265-params", "log-level=error", "-f", "mov", mov]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); first = None
    for fr in frames:
        if first is None: first = fr
        p.stdin.write(fr)
    p.stdin.close(); assert p.wait() == 0, "ffmpeg failed"
    add_still_track(mov, cid)
    write_jpeg(Image.frombytes("RGB", (w, h), first), out_base + ".JPG", cid)
    return cid
