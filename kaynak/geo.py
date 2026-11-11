"""Small 2D kit: line/arc outlines (exact offsets, clipping, fillets) and cubic-bezier paths.
Coordinates are y-down; 'clockwise' means clockwise on screen (angle increasing)."""
import math
import numpy as np


def V(x, y):
    return np.array([x, y], float)


def unit(v):
    return v / math.hypot(v[0], v[1])


def perp(v):  # interior side normal for clockwise travel
    return V(-v[1], v[0])


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def rot(v, deg, c=(0, 0)):
    a = math.radians(deg)
    x, y = v[0] - c[0], v[1] - c[1]
    return V(c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def lineX(p, d, q, e):
    den = cross(d, e)
    t = cross(q - p, e) / den
    return p + t * d


# ---------------- primitives ----------------
def Ln(a, b):
    return {"t": "L", "a": V(*a), "b": V(*b)}


def Ar(c, a, b, s=1):
    c = V(*c)
    return {"t": "A", "c": c, "r": math.hypot(*(V(*a) - c)), "a": V(*a), "b": V(*b), "s": s}


def tan_at(pr, end):
    if pr["t"] == "L":
        return unit(pr["b"] - pr["a"])
    p = pr["b"] if end else pr["a"]
    return pr["s"] * perp(unit(p - pr["c"]))


def sweep(pr, p=None):
    a0 = math.atan2(*(pr["a"] - pr["c"])[::-1])
    a1 = math.atan2(*((pr["b"] if p is None else p) - pr["c"])[::-1])
    return ((a1 - a0) * pr["s"]) % (2 * math.pi)


def on_arc(pr, p):
    return 1e-9 < sweep(pr, p) < sweep(pr) - 1e-9


def hits(pr, q, d):
    """parameters-free intersections of prim with infinite line (q, d), strictly inside the prim"""
    out = []
    if pr["t"] == "L":
        e = pr["b"] - pr["a"]
        den = cross(e, d)
        if abs(den) > 1e-12:
            t = cross(q - pr["a"], d) / den
            if 1e-9 < t < 1 - 1e-9:
                out.append(pr["a"] + t * e)
    else:
        d = unit(d)
        f = q - pr["c"]
        b = f @ d
        disc = b * b - (f @ f - pr["r"] ** 2)
        if disc > 0:
            for t in (-b - math.sqrt(disc), -b + math.sqrt(disc)):
                p = q + t * d
                if on_arc(pr, p):
                    out.append(p)
        out.sort(key=lambda p: sweep(pr, p))
    return out


def split(pr, ps):
    out, cur = [], pr["a"]
    for p in list(ps) + [pr["b"]]:
        n = dict(pr)
        n["a"], n["b"] = cur, p
        out.append(n)
        cur = p
    return out


def mid(pr):
    if pr["t"] == "L":
        return (pr["a"] + pr["b"]) / 2
    a0 = math.atan2(*(pr["a"] - pr["c"])[::-1]) + pr["s"] * sweep(pr) / 2
    return pr["c"] + pr["r"] * V(math.cos(a0), math.sin(a0))


def clip(prims, q, n):
    """keep the part of a closed outline where (p-q).n >= 0; the cut is closed with a straight line"""
    d = perp(n)
    pieces = [x for pr in prims for x in split(pr, hits(pr, q, d))]
    keep = [(mid(x) - q) @ n >= 0 for x in pieces]
    if all(keep):
        return pieces
    k = next(i for i in range(len(pieces)) if keep[i] and not keep[i - 1])
    pieces, keep = pieces[k:] + pieces[:k], keep[k:] + keep[:k]
    out = [x for x, kp in zip(pieces, keep) if kp]
    out.append(Ln(out[-1]["b"], out[0]["a"]))
    return out


def _off(pr, e):
    """locus of fillet centres for prim: ('L', point, dir) or ('C', centre, radius)"""
    if pr["t"] == "L":
        d = unit(pr["b"] - pr["a"])
        return ("L", pr["a"] + e * perp(d), d)
    return ("C", pr["c"], pr["r"] - pr["s"] * e)


def _locus_x(A, B, near):
    if A[0] == "L" and B[0] == "L":
        return [lineX(A[1], A[2], B[1], B[2])]
    if A[0] == "C" and B[0] == "L":
        A, B = B, A
    if A[0] == "L":
        f = A[1] - B[1]
        b = f @ A[2]
        disc = b * b - (f @ f - B[2] ** 2)
        return [A[1] + t * A[2] for t in (-b - math.sqrt(disc), -b + math.sqrt(disc))]
    dv = B[1] - A[1]
    dist = math.hypot(*dv)
    a = (A[2] ** 2 - B[2] ** 2 + dist ** 2) / (2 * dist)
    h = math.sqrt(max(A[2] ** 2 - a * a, 0))
    m = A[1] + a * dv / dist
    return [m + h * perp(dv / dist), m - h * perp(dv / dist)]


def fillet(prims, r, closed=True, only=None):
    """round every tangent-discontinuous corner (or those listed in `only`) with radius r"""
    prims = [dict(p) for p in prims]
    n = len(prims)
    arcs = {}
    for j in range(n if closed else n - 1):
        A, B = prims[j], prims[(j + 1) % n]
        if only is not None and j not in only:
            continue
        rr = only[j] if isinstance(only, dict) else r
        ta, tb = tan_at(A, True), tan_at(B, False)
        cr = cross(ta, tb)
        if abs(cr) < 0.02:
            continue
        e = rr if cr > 0 else -rr
        corner = A["b"]
        c = min(_locus_x(_off(A, e), _off(B, e), corner), key=lambda p: math.hypot(*(p - corner)))

        def foot(pr):
            if pr["t"] == "L":
                d = unit(pr["b"] - pr["a"])
                return c - e * perp(d)
            return pr["c"] + pr["r"] * unit(c - pr["c"]) * (1 if pr["r"] - pr["s"] * e > 0 else -1)
        pa, pb = foot(A), foot(B)
        A["b"], B["a"] = pa, pb
        arcs[j] = Ar(c, pa, pb, 1 if cr > 0 else -1)
    out = []
    for j in range(n):
        out.append(prims[j])
        if j in arcs:
            out.append(arcs[j])
    return out


def anchors(prims, closed=True):
    """prims -> list of bezier anchors {p, i, o}"""
    pts = []

    def add(p, i=None, o=None):
        if pts and math.hypot(*(pts[-1]["p"] - p)) < 1e-7:
            if i is not None:
                pts[-1]["i"] = i
            if o is not None:
                pts[-1]["o"] = o
        else:
            pts.append({"p": p, "i": i, "o": o})
    for pr in prims:
        if math.hypot(*(pr["b"] - pr["a"])) < 1e-7:
            continue
        if pr["t"] == "L":
            add(pr["a"])
            add(pr["b"])
            continue
        sw = sweep(pr)
        k = max(1, math.ceil(sw / (math.pi / 4) - 1e-9))
        a0 = math.atan2(*(pr["a"] - pr["c"])[::-1])
        h = 4 / 3 * math.tan(sw / k / 4) * pr["r"]
        for m in range(k):
            a, b = a0 + pr["s"] * sw * m / k, a0 + pr["s"] * sw * (m + 1) / k
            pa = pr["c"] + pr["r"] * V(math.cos(a), math.sin(a))
            pb = pr["c"] + pr["r"] * V(math.cos(b), math.sin(b))
            add(pa, o=pa + h * pr["s"] * V(-math.sin(a), math.cos(a)))
            add(pb, i=pb - h * pr["s"] * V(-math.sin(b), math.cos(b)))
    if closed and len(pts) > 1 and math.hypot(*(pts[-1]["p"] - pts[0]["p"])) < 1e-7:
        if pts[-1]["i"] is not None:
            pts[0]["i"] = pts[-1]["i"]
        pts.pop()
    return pts


def poly(points):
    return [{"p": V(*p), "i": None, "o": None} for p in points]


# ---------------- bezier paths (anchor lists) ----------------
def segs(an):
    """closed anchor list -> list of cubic control quadruples"""
    n = len(an)
    out = []
    for k in range(n):
        a, b = an[k], an[(k + 1) % n]
        out.append([a["p"], a["o"] if a["o"] is not None else a["p"], b["i"] if b["i"] is not None else b["p"], b["p"]])
    return out


def bez(c, t):
    t = np.atleast_1d(t)[:, None]
    return (1 - t) ** 3 * c[0] + 3 * (1 - t) ** 2 * t * c[1] + 3 * (1 - t) * t ** 2 * c[2] + t ** 3 * c[3]


def bsplit(c, t):
    p01, p12, p23 = c[0] + (c[1] - c[0]) * t, c[1] + (c[2] - c[1]) * t, c[2] + (c[3] - c[2]) * t
    p012, p123 = p01 + (p12 - p01) * t, p12 + (p23 - p12) * t
    m = p012 + (p123 - p012) * t
    return [c[0], p01, p012, m], [m, p123, p23, c[3]]


def from_segs(sg):
    """list of consecutive cubic quadruples (closed) -> anchors; straight pieces lose their handles"""
    n = len(sg)
    out = []
    for k in range(n):
        c, prv = sg[k], sg[k - 1]

        def straight(q):
            L = math.hypot(*(q[3] - q[0]))
            return L < 1e-9 or all(abs(cross(q[3] - q[0], h - q[0])) / L < 1e-6 for h in (q[1], q[2]))
        out.append({"p": c[0], "i": None if straight(prv) else prv[2], "o": None if straight(c) else c[1]})
    return out


def clip_bez(an, q, n):
    """keep the part of a closed bezier path where (p-q).n >= 0"""
    pieces = []
    for c in segs(an):
        d = [(p - q) @ n for p in c]
        co = [-d[0] + 3 * d[1] - 3 * d[2] + d[3], 3 * d[0] - 6 * d[1] + 3 * d[2], -3 * d[0] + 3 * d[1], d[0]]
        ts = sorted(float(r.real) for r in np.roots(co) if abs(r.imag) < 1e-9 and 1e-6 < r.real < 1 - 1e-6) if any(abs(x) > 1e-12 for x in co[:3]) else []
        rest, t0 = c, 0.0
        for t in ts:
            a, rest = bsplit(rest, (t - t0) / (1 - t0))
            pieces.append(a)
            t0 = t
        pieces.append(rest)
    keep = [(bez(c, 0.5)[0] - q) @ n >= 0 for c in pieces]
    if all(keep):
        return an
    k = next(i for i in range(len(pieces)) if keep[i] and not keep[i - 1])
    pieces, keep = pieces[k:] + pieces[:k], keep[k:] + keep[:k]
    out = []
    for c, kp in zip(pieces, keep):
        if kp:
            if out and math.hypot(*(out[-1][3] - c[0])) > 1e-6:
                out.append([out[-1][3], out[-1][3], c[0], c[0]])
            out.append(c)
    if math.hypot(*(out[-1][3] - out[0][0])) > 1e-6:
        out.append([out[-1][3], out[-1][3], out[0][0], out[0][0]])
    return from_segs(out)


def sample(an, m=24):
    ts = np.linspace(0, 1, m, endpoint=False)
    return np.vstack([bez(c, ts) for c in segs(an)])


def fair(an, smooth_deg=38.0, keep_corner=()):
    """G1-fair a closed path: near-smooth joints become truly smooth, every curve gets two balanced
    handles refitted to the original shape. Corners sharper than smooth_deg stay corners."""
    sg = segs(an)
    n = len(sg)

    def is_line(c):
        L = math.hypot(*(c[3] - c[0]))
        return all(abs(cross(c[3] - c[0], h - c[0])) / L < 0.02 for h in (c[1], c[2]))

    def t_start(c):
        for h in (c[1], c[2], c[3]):
            if math.hypot(*(h - c[0])) > 1e-6:
                return unit(h - c[0])

    def t_end(c):
        for h in (c[2], c[1], c[0]):
            if math.hypot(*(c[3] - h)) > 1e-6:
                return unit(c[3] - h)
    tin = [t_end(sg[k - 1]) for k in range(n)]
    tout = [t_start(sg[k]) for k in range(n)]
    lines = [is_line(c) for c in sg]
    for k in range(n):
        dev = math.degrees(math.acos(max(-1, min(1, tin[k] @ tout[k]))))
        if k in keep_corner or dev >= smooth_deg or dev < 1e-6:
            continue
        if lines[k - 1] and not lines[k]:
            tout[k] = tin[k]
        elif lines[k] and not lines[k - 1]:
            tin[k] = tout[k]
        elif not lines[k] and not lines[k - 1]:
            tin[k] = tout[k] = unit(tin[k] + tout[k])
    new = []
    ts = np.linspace(0, 1, 25)
    for k in range(n):
        c = sg[k]
        if lines[k]:
            new.append([c[0], c[0], c[3], c[3]])
            continue
        ta, tb = tout[k], tin[(k + 1) % n]
        ch = math.hypot(*(c[3] - c[0]))
        ref = bez(c, ts)
        best = None
        ga = gb = np.linspace(0.14, 0.86, 13)
        step = ga[1] - ga[0]
        for _ in range(3):
            for la in ga:
                for lb in gb:
                    if la < 0.12 or lb < 0.12:
                        continue
                    q = bez([c[0], c[0] + ta * la * ch, c[3] - tb * lb * ch, c[3]], ts)
                    dmat = np.hypot(q[:, None, 0] - ref[None, :, 0], q[:, None, 1] - ref[None, :, 1])
                    err = dmat.min(axis=0).sum() + dmat.min(axis=1).sum()
                    if best is None or err < best[0]:
                        best = (err, la, lb)
            ga = np.linspace(best[1] - step, best[1] + step, 7)
            gb = np.linspace(best[2] - step, best[2] + step, 7)
            step /= 3
        new.append([c[0], c[0] + ta * best[1] * ch, c[3] - tb * best[2] * ch, c[3]])
    return from_segs(new)


def join(a, b, ta, tb, k=1.0):
    """set a smooth cubic from anchor a to anchor b with unit tangents ta (leaving a) and tb (arriving b)"""
    ch = b["p"] - a["p"]
    L = math.hypot(*ch)
    ca = max(0.3, (unit(ch) @ ta + unit(ch) @ tb) / 2)
    h = k * (2 / 3) * L / (1 + ca)
    a["o"] = a["p"] + ta * h
    b["i"] = b["p"] - tb * h


def min_circle(P, it=4000):
    c = P.mean(axis=0)
    for i in range(it):
        d = np.hypot(P[:, 0] - c[0], P[:, 1] - c[1])
        c = c + (P[d.argmax()] - c) / (i + 2)
    return c, float(np.hypot(P[:, 0] - c[0], P[:, 1] - c[1]).max())
