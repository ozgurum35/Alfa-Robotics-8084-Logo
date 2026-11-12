"""Drawing audit for emblem.json / wordmark.json: duplicate / tiny segments, self-intersections,
navy-on-navy overlaps, colour areas outside the navy silhouette, hairline gaps."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
art = json.load(open(sys.argv[1])); Z = 8
W, H = int(art["width"] * Z), int(art["height"] * Z)

def flat(sub, n=24):
    pts = []
    for k in range(len(sub)):
        a, b = sub[k], sub[(k + 1) % len(sub)]
        P0, P1, P2, P3 = map(np.array, (a["p"], a["o"], b["i"], b["p"]))
        for t in np.linspace(0, 1, n, endpoint=False):
            pts.append((1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t * t * P2 + t ** 3 * P3)
    return np.array(pts)

def seg_x(p, q, r, s):
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-12: return False
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    return 1e-6 < t < 1 - 1e-6 and 1e-6 < u < 1 - 1e-6

masks, issues = {}, []
for g in art["groups"]:
    for it in g["items"]:
        nm = g["name"] + " / " + it["name"]
        im = Image.new("1", (W, H), 0); dr = ImageDraw.Draw(im)
        for si, sub in enumerate(it["subs"]):
            # tiny / duplicate segments
            for k in range(len(sub)):
                a, b = np.array(sub[k]["p"]), np.array(sub[(k + 1) % len(sub)]["p"])
                L = np.hypot(*(b - a))
                if L < 0.3: issues.append("%s: alt yol %d, %d. dugum: cok kisa parca %.3f pt %s" % (nm, si, k, L, np.round(a, 2)))
            # tangency: in/out directions at every node; small breaks (0.3-30 deg) are unintended kinks
            for k in range(len(sub)):
                a = sub[k]; pv = sub[k - 1]; nx = sub[(k + 1) % len(sub)]
                p_ = np.array(a["p"])
                tin = next((p_ - np.array(h) for h in (a["i"], pv["o"], pv["p"]) if np.hypot(*(p_ - np.array(h))) > 1e-6), None)
                tout = next((np.array(h) - p_ for h in (a["o"], nx["i"], nx["p"]) if np.hypot(*(np.array(h) - p_)) > 1e-6), None)
                if tin is None or tout is None: continue
                c = np.clip(tin @ tout / np.hypot(*tin) / np.hypot(*tout), -1, 1)
                ang = np.degrees(np.arccos(c))
                if 0.3 < ang < 30: issues.append("%s: alt yol %d, %d. dugumde teget kirigi %.1f derece %s" % (nm, si, k, ang, np.round(p_, 2)))
            # bumps: a curve segment whose handles point to opposite sides (S-bend) between two smooth joints
            for k in range(len(sub)):
                a, b = sub[k], sub[(k + 1) % len(sub)]
                P0, P1, P2, P3 = map(np.array, (a["p"], a["o"], b["i"], b["p"]))
                ch = P3 - P0
                if np.hypot(*ch) < 1e-6: continue
                cr = lambda v: ch[0] * v[1] - ch[1] * v[0]
                s1, s2 = cr(P1 - P0), cr(P2 - P0)
                if s1 * s2 < 0 and min(abs(s1), abs(s2)) / np.hypot(*ch) > 0.15:
                    issues.append("%s: alt yol %d, %d. parca S-kivrim (girinti/cikinti olabilir) %s" % (nm, si, k, np.round(P0, 2)))
            P = flat(sub)
            n = len(P)
            hits = 0
            for i in range(n):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1: continue
                    if seg_x(P[i], P[(i + 1) % n], P[j], P[(j + 1) % n]): hits += 1
            if hits: issues.append("%s: alt yol %d kendini kesiyor (%d nokta)" % (nm, si, hits))
            dr.polygon([tuple(q * Z) for q in P], fill=1)  # even-odd per sub handled below
        masks[nm] = (it["color"], np.array(im, bool))
# overlaps / outside checks
navy = [k for k, (c, m) in masks.items() if c == "Lacivert"]
U = np.zeros((H, W), bool)
for k in navy: U |= masks[k][1]
for i, a in enumerate(navy):
    for b in navy[i + 1:]:
        ov = (masks[a][1] & masks[b][1]).sum() / Z / Z
        if ov > 0.5: issues.append("lacivert ust uste: %s + %s = %.1f pt2" % (a, b, ov))
for k, (c, m) in masks.items():
    if c != "Lacivert":
        out = (m & ~U).sum() / Z / Z
        if out > 0.5: issues.append("%s (%s) lacivert disina tasiyor: %.1f pt2" % (k, c, out))
print("\n".join(issues) if issues else "sorun yok")
