"""ALFA Robotics 8084 - emblem redrawn from construction. Writes emblem.json + preview."""
import sys, json, math
import numpy as np
import pymupdf
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment
from geo import *

SP, FONT = sys.argv[1], sys.argv[2]
src = json.load(open(SP + "/logo1.json"))
rad = math.radians

# ------------------------------------------------------------------ parameters
X0 = 188.5            # shield axis
TH = 15.0             # lettering angle = italic angle of Classic Robot -> stems come out vertical
HW, RC, WF = 154.0, 18.0, 14.0     # shield half width, top corner radius, frame width
YT, RT = 56.0, 490.0               # top arc apex and radius
YTIP, RTIP = 392.0, 20.0           # sharp-tip position before rounding, tip radius
GP = 6.5              # every white channel (perpendicular)
T = 18.0              # stroke weight of every ALFA stroke (perpendicular)
CAPH, BANDH = 57.0, 21.0           # ALFA cap height, ROBOTICS band height (vertical measure)
PHI = 27.0            # A legs: +-PHI from vertical
YU = 213.0            # upper cut line at the axis
RCUT = 3.0            # rounding of the cut corners
WO = WF               # outline width around the head = frame width
NAVY, SKY, ICE = [0, 58, 111], [71, 185, 239], [235, 247, 252]

dU = V(math.cos(rad(TH)), -math.sin(rad(TH)))      # along the lettering, rising to the right
nUp = V(-math.sin(rad(TH)), -math.cos(rad(TH)))    # perpendicular, pointing up
tanT, cosT = math.tan(rad(TH)), math.cos(rad(TH))
CY = YT + RT - math.sqrt((RT - RC) ** 2 - (HW - RC) ** 2)
RS = (HW ** 2 + (YTIP - CY) ** 2) / (2 * HW)
CT = V(X0, YT + RT)


def shield(d=0.0):
    CR, CL = V(X0 + HW - RC, CY), V(X0 - HW + RC, CY)
    SR, SL = V(X0 + HW - RS, CY), V(X0 - HW + RS, CY)
    T2, T1 = CT + (RT - d) * unit(CR - CT), CT + (RT - d) * unit(CL - CT)
    R1, L1 = V(X0 + HW - d, CY), V(X0 - HW + d, CY)
    F = V(X0, CY + math.sqrt((RS - RTIP) ** 2 - (RS - HW) ** 2))
    A, B = SR + (RS - d) * unit(F - SR), SL + (RS - d) * unit(F - SL)
    return [Ar(CT, T1, T2), Ar(CR, T2, R1), Ar(SR, R1, A), Ar(F, A, B), Ar(SL, B, L1), Ar(CL, L1, T1)], F


def lvl(y_axis):
    return lambda x: y_axis - (x - X0) * tanT


e = GP / cosT
yC = YU + e
yB = yC + CAPH
yT = yB + e
yBB = yT + BANDH
yLW = yBB + e
cap, base, btop, bbot = lvl(yC), lvl(yB), lvl(yT), lvl(yBB)
PU, PL_ = V(X0, YU), V(X0, yLW)

sh0, F = shield(0)
shI, _ = shield(WF)
up_out = fillet(clip(sh0, PU, nUp), RCUT)
up_in = fillet(clip(shI, PU + WF * nUp, nUp), RCUT)
lo_out = fillet(clip(sh0, PL_, -nUp), RCUT)
lo_in = fillet(clip(shI, PL_ - WF * nUp, -nUp), RCUT)
TIPY = F[1] + RTIP

# ------------------------------------------------------------------ wolf
W = {}
for it in next(g for g in src["groups"] if g["name"] == "Kurt")["items"]:
    key = {"Kurt govde": "G", "Burun": "B", "Dil": "D", "Yele 1": "Y", "Yele 2": "Z", "Bas ve boyun": "H"}[it["name"]]
    W[key] = [{"p": V(*a["p"]), "i": None if a["i"] == a["p"] else V(*a["i"]), "o": None if a["o"] == a["p"] else V(*a["o"])}
              for a in it["subs"][0]]


def turn(path, idx, deg, c):
    for k in idx:
        for key in ("p", "i", "o"):
            if path[k][key] is not None:
                path[k][key] = rot(path[k][key], deg, c)


def tang(a, b):  # unit tangent leaving a towards b's control structure
    return unit((a["o"] if a["o"] is not None else (b["i"] if b["i"] is not None else b["p"])) - a["p"])


G8, G9 = W["G"][8]["p"].copy(), W["G"][9]["p"].copy()
H4dir = unit(W["H"][5]["i"] - W["H"][4]["p"])
H12dir = unit(W["H"][12]["p"] - W["H"][12]["i"])
G2dir = unit(W["G"][3]["i"] - W["G"][2]["p"])
H16dir = unit(W["H"][17]["i"] - W["H"][16]["p"])
W["B"][14]["o"] = V(100.0, 116.3)      # ear top: one clean sweep instead of a stepped joint
del W["B"][15]
H3dir = unit(W["H"][4]["p"] - W["H"][3]["p"])
FG, FH, FB, FD, FY, FZ = (fair(W[k]) for k in "GHBDYZ")

# lower jaw: straight lip, round tip, taut throat line; the ice inlay is its parallel inset
JA = 20.0
ja = V(math.cos(rad(JA)), -math.sin(rad(JA)))
jn = perp(ja)
JLEN, JR, JW = 32.0, 9.0, 6.0
P1 = G9 + JLEN * ja
CJ = P1 + JR * jn
P2 = CJ + JR * jn
jaw_n = anchors([Ln(G9, P1), Ar(CJ, P1, P2)], closed=False)[1:]
I0, I1, I2 = G9 + JW * jn + 2.0 * ja, P1 + JW * jn, CJ + (JR - JW) * jn
jaw_i = anchors([Ln(I0, I1), Ar(CJ, I1, I2)], closed=False)

# snout: two straight edges and one round nose, the navy outline is its exact offset
A33 = 33.0
d33 = V(math.cos(rad(A33)), -math.sin(rad(A33)))
n33 = V(-math.sin(rad(A33)), -math.cos(rad(A33)))
XF, RN = 290.0, 10.0                           # muzzle front (ice), nose radius (ice)
Qi = V(267.6, 51.4)
Ki = lineX(Qi, d33, V(XF, 0), V(0, 1))
M = Qi + ((250.0 - Qi[0]) / d33[0]) * d33
H11 = V(XF, 82.2)
ice_snout = fillet([Ln(M, Ki), Ln(Ki, H11)], RN, closed=False)
NOSE_C = ice_snout[1]["c"]
Qn = Qi + WO * n33
Kn = lineX(Qn, d33, V(XF + WO, 0), V(0, 1))
topA = sh0[0]
X1 = min(hits(topA, Qn, d33), key=lambda p: abs(p[0] - 232))
X2 = hits(topA, V(XF + WO, 0), V(0, 1))[0]
nav = fillet([Ar(CT, topA["a"], X1), Ln(X1, Kn), Ln(Kn, X2), Ar(CT, X2, topA["b"])], 0, closed=False,
             only={0: 6.0, 1: RN + WO, 2: 6.0})
nav_an = anchors(nav[1:6], closed=False)


def A_(p, i=None, o=None):
    return {"p": V(*p), "i": i, "o": o}


J = A_(Qn + ((205.0 - Qn[0]) / d33[0]) * d33)
Jf = A_(Qn + ((216.0 - Qn[0]) / d33[0]) * d33)
E1 = A_((XF + WO, 80.0))
g2, g9 = dict(FG[2]), dict(FG[9])
join(g2, J, G2dir, d33)
join(E1, g9, V(0, 1), unit(G9 - G8))
g9["o"] = None
d2, d0 = dict(FD[2]), dict(FD[0])
d2["i"], d0["o"], d0["i"] = None, None, None
g0 = dict(FG[0])
g0["i"] = None
g13 = dict(FG[13])
jaw_n[-1]["o"] = P2 - 30.0 * ja
g13["i"] = V(250.0, 168.0)
body = [g0, FG[1], g2, J, Jf] + nav_an + [E1, g9] + jaw_n + [g13] + FG[14:17] + [d2, FD[3], FD[4], d0]
body = clip_bez(body, PU + (WF / 2) * nUp, nUp)

h4, h12 = dict(FH[4]), dict(FH[12])
m_an = anchors(ice_snout, closed=False)
join(h4, m_an[0], H3dir, d33)
join(m_an[-1], h12, V(0, 1), H12dir)
h16, h20 = dict(FH[16]), dict(FH[20])
join(h16, jaw_i[0], H16dir, ja)
jaw_i[-1]["o"] = I2 - 26.0 * ja
h20["i"] = V(247.0, 162.0)
head = FH[:4] + [h4] + m_an + [h12] + FH[13:16] + [h16] + jaw_i + [h20] + FH[21:]
PIN = PU + WF * nUp
head = clip_bez(head, PIN, nUp)


def tidy(an):
    out = []
    carry = None
    for k, a in enumerate(an):
        a = dict(a)
        if carry is not None:
            a["i"], carry = carry[0], None
        if math.hypot(*(an[(k + 1) % len(an)]["p"] - a["p"])) > 0.2:
            out.append(a)
        else:
            carry = (a["i"],)
    if carry is not None:
        out[0]["i"] = carry[0]
    return out


ear, fur1, fur2 = FB, tidy(clip_bez(FY, PIN, nUp)), tidy(clip_bez(FZ, PIN, nUp))
head, body = tidy(head), tidy(body)

# ------------------------------------------------------------------ enclosing circle (axis-centred)
# touches the nose and the shield tip; the A legs are then made to end exactly on it
rn = RN + WO
yO = (TIPY ** 2 - rn ** 2 - 2 * TIPY * rn + 0) if False else None
lo, hi = 100.0, 300.0
for _ in range(60):
    yO = (lo + hi) / 2
    if math.hypot(NOSE_C[0] - X0, NOSE_C[1] - yO) + rn > TIPY - yO:
        hi = yO
    else:
        lo = yO
O = V(X0, yO)
R = TIPY - yO
foot = O + ((V(X0, yBB) - O) @ -nUp) * -nUp
half = math.sqrt(R ** 2 - ((V(X0, yBB) - O) @ -nUp) ** 2)
PL, PR = foot - half * dU, foot + half * dU

# ------------------------------------------------------------------ ALFA
dl, dr = V(-math.sin(rad(PHI)), math.cos(rad(PHI))), V(math.sin(rad(PHI)), math.cos(rad(PHI)))  # leg directions, downwards
WH = T / math.cos(rad(PHI))          # horizontal width of a leg
TB = T / cosT                        # vertical height of a bar
hx = V(1, 0)


def on(f, x):
    return V(x, f(x))


def toline(p, d, f):                 # where the line (p, d) meets level line f
    return lineX(p, d, V(X0, f(X0)), dU)


def letter_A(p_outer, long_left):
    """p_outer: end of the long leg on the band-bottom line (left A) or of the short leg on the baseline (right A)"""
    if long_left:
        aL = toline(p_outer, dl, cap)
        aR = aL + (WH / dU[0]) * dU
        ro = toline(aR, dr, base)                      # right (short) leg, outer
        ri = toline(aR - WH * hx, dr, base)
        notch = lineX(aL + WH * hx, dl, aR - WH * hx, dr)
        li = toline(aL + WH * hx, dl, bbot)
        return [aL, aR, ro, ri, notch, li, p_outer], aL, aR
    aL = toline(p_outer, dl, cap)
    aR = aL + (WH / dU[0]) * dU
    ro = toline(aR, dr, bbot)                          # right (long) leg, outer
    ri = toline(aR - WH * hx, dr, bbot)
    notch = lineX(aL + WH * hx, dl, aR - WH * hx, dr)
    li = toline(aL + WH * hx, dl, base)
    return [aL, aR, ro, ri, notch, li, p_outer], aL, aR


def letters(Wd, gA=4.0, gLF=7.0):
    A1, a1L, a1R = letter_A(PL, True)
    xL = A1[2][0] + gA
    Lp = [on(cap, xL), on(cap, xL + T), on(lvl(yB - TB), xL + T), on(lvl(yB - TB), xL + Wd), on(base, xL + Wd), on(base, xL)]
    xF = xL + Wd + gLF
    ga = 3.5                                           # stem-arm separation of the F
    Fs = [on(cap, xF), on(cap, xF + T), on(base, xF + T), on(base, xF)]
    F1 = [on(cap, xF + T + ga), on(cap, xF + Wd), on(lvl(yC + TB), xF + Wd), on(lvl(yC + TB), xF + T + ga)]
    ym = yC + (CAPH - TB) / 2 + 1.0                     # middle arm, optically a touch below centre
    wm = Wd - 6.0
    F2 = [on(lvl(ym), xF + T + ga), on(lvl(ym), xF + wm), on(lvl(ym + TB), xF + wm), on(lvl(ym + TB), xF + T + ga)]
    A2, a2L, a2R = letter_A(on(base, xF + Wd + gA), False)
    return {"A1": A1, "L": Lp, "F": Fs, "F1": F1, "F2": F2, "A2": A2}


lo, hi = 30.0, 70.0
for _ in range(60):
    WD = (lo + hi) / 2
    if letters(WD)["A2"][2][0] < PR[0]:
        lo = WD
    else:
        hi = WD
LT = letters(WD)
# band: ends parallel to the long legs, one channel away
bl_p = LT["A1"][5] + (GP / math.cos(rad(PHI))) * hx
br_p = LT["A2"][3] - (GP / math.cos(rad(PHI))) * hx
band = [toline(bl_p, dl, btop), toline(br_p, dr, btop), toline(br_p, dr, bbot), toline(bl_p, dl, bbot)]

# ------------------------------------------------------------------ Classic Robot text (undistorted)
font = TTFont(FONT)
gset, cmap = font.getGlyphSet(), font.getBestCmap()
ITAL = math.tan(rad(-font["post"].italicAngle))


def text_contours(s, tracking):
    cs, x = [], 0.0
    for ch in s:
        g = gset[cmap[ord(ch)]]
        pen = RecordingPen()
        g.draw(pen)
        cur = None
        for op, a in pen.value:
            if op == "moveTo":
                cur = [{"p": V(a[0][0] + x, a[0][1]), "i": None, "o": None}]
                cs.append(cur)
            elif op == "lineTo":
                cur.append({"p": V(a[0][0] + x, a[0][1]), "i": None, "o": None})
            elif op == "curveTo":
                cur[-1]["o"] = V(a[0][0] + x, a[0][1])
                cur.append({"p": V(a[2][0] + x, a[2][1]), "i": V(a[1][0] + x, a[1][1]), "o": None})
            elif op == "qCurveTo":                      # TrueType quadratics -> exact cubics
                for q, p1 in decomposeQuadraticSegment(a):
                    p0, q, p1 = cur[-1]["p"], V(q[0] + x, q[1]), V(p1[0] + x, p1[1])
                    cur[-1]["o"] = p0 + (q - p0) * 2 / 3
                    cur.append({"p": p1, "i": p1 + (q - p1) * 2 / 3, "o": None})
        x += g.width + tracking
    for c in cs:
        if math.hypot(*(c[-1]["p"] - c[0]["p"])) < 1e-6:
            c[0]["i"] = c[-1]["i"]
            c.pop()
    return cs


def text_box(cs):
    P = np.vstack([sample(c, 8) for c in cs])
    xs = P[:, 0] - P[:, 1] * ITAL                       # un-slanted extent
    return xs.min(), xs.max(), P[:, 1].min(), P[:, 1].max()


def place(cs, centre, cap_perp):
    x0, x1, y0, y1 = text_box(cs)
    s = cap_perp / (y1 - y0)
    yc = (y0 + y1) / 2
    fc = V((x0 + x1) / 2 + yc * ITAL, yc)
    out = []
    for c in cs:
        out.append([{k: (None if a[k] is None else centre + s * ((a[k][0] - fc[0]) * dU + (a[k][1] - fc[1]) * nUp)) for k in ("p", "i", "o")} for a in c])
    return out, s * (x1 - x0)


def fit_text(s, centre, cap_perp, length):
    w0 = place(text_contours(s, 0), centre, cap_perp)[1]
    w1 = place(text_contours(s, 100), centre, cap_perp)[1]
    tr = (length - w0) / (w1 - w0) * 100
    return place(text_contours(s, tr), centre, cap_perp)[0], tr


ymid = (yT + yBB) / 2
bL, bR = toline(bl_p, dl, lvl(ymid)), toline(br_p, dr, lvl(ymid))
ROB_CAP = 12.0
robotics, rob_tr = fit_text("ROBOTICS", (bL + bR) / 2, ROB_CAP, math.hypot(*(bR - bL)) - 2 * 26.0)

# 8084: largest size that keeps a clear margin inside the lower panel
lo_in_an = anchors(lo_in)
panel = sample(lo_in_an, 40)


def inside(P, poly_):
    x, y = P[:, 0][:, None], P[:, 1][:, None]
    x1, y1 = poly_[:, 0][None], poly_[:, 1][None]
    x2, y2 = np.roll(poly_[:, 0], -1)[None], np.roll(poly_[:, 1], -1)[None]
    cond = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-300) + x1)
    return cond.sum(axis=1) % 2 == 1


def clearance(cs):
    P = np.vstack([sample(c, 6) for c in cs])
    if not inside(P, panel).all():
        return -1.0
    return float(np.hypot(P[:, None, 0] - panel[None, :, 0], P[:, None, 1] - panel[None, :, 1]).min())


NUM_TR, NUM_CLEAR = 0.0, 4.0
cen0 = panel.mean(axis=0)
best = None
for capn in np.arange(22.0, 9.0, -0.25):
    for du in np.arange(-10, 10.01, 1.0):
        for dn in np.arange(-8, 8.01, 1.0):
            cs = place(text_contours("8084", NUM_TR), cen0 + du * dU + dn * nUp, capn)[0]
            c = clearance(cs)
            if c >= NUM_CLEAR and (best is None or c > best[0]):
                best = (c, capn, cs)
    if best:
        break
num, NUM_CAP = best[2], best[1]

# ------------------------------------------------------------------ assemble
def J_(an):
    return [{"p": a["p"], "i": a["i"] if a.get("i") is not None else a["p"], "o": a["o"] if a.get("o") is not None else a["p"]} for a in an]


groups = [
    ("Kalkan ust", [("Cerceve", "Lacivert", [anchors(up_out)]), ("Zemin", "Acik Mavi", [anchors(up_in)])]),
    ("Kalkan alt", [("Cerceve", "Lacivert", [anchors(lo_out)]), ("Zemin", "Acik Mavi", [lo_in_an])]),
    ("Kurt", [("Govde ve dis hat", "Lacivert", [body]), ("Kulak", "Buz", [ear]), ("Yele 1", "Buz", [fur1]),
              ("Yele 2", "Buz", [fur2]), ("Bas ve boyun", "Buz", [head])]),
    ("ALFA", [("A sol", "Lacivert", [poly(LT["A1"])]), ("L", "Lacivert", [poly(LT["L"])]),
              ("F", "Lacivert", [poly(LT["F"]), poly(LT["F1"]), poly(LT["F2"])]), ("A sag", "Lacivert", [poly(LT["A2"])])]),
    ("ROBOTICS", [("Bant + ROBOTICS", "Lacivert", [poly(band)] + robotics)]),
    ("8084", [("8084", "Lacivert", num)]),
]
PAL = {"Lacivert": NAVY, "Acik Mavi": SKY, "Buz": ICE}
MARG = 0.07
side = math.ceil(2 * R * (1 + MARG))
off = V(side / 2, side / 2) - O
out = {"width": side, "height": side, "circle": [side / 2, side / 2, round(R, 4)], "groups": []}
allpts = []
for gname, items in groups:
    jg = {"name": gname, "items": []}
    for name, col, subs in items:
        js = []
        for s in subs:
            s = J_(s)
            allpts.append(sample(s, 12))
            js.append([{k: [round(float(a[k][0] + off[0]), 4), round(float(a[k][1] + off[1]), 4)] for k in ("p", "i", "o")} for a in s])
        jg["items"].append({"name": name, "color": col, "rgb": PAL[col], "subs": js})
    out["groups"].append(jg)
json.dump(out, open(SP + "/emblem.json", "w"))

# ------------------------------------------------------------------ report
P = np.vstack(allpts)
d = np.hypot(P[:, 0] - O[0], P[:, 1] - O[1])
print("circle: centre (%.2f, %.2f) R %.2f | farthest point %.2f | artboard %d" % (O[0], O[1], R, d.max(), side))
for nm, m in (("left", P[:, 0].min() - (O[0] - R)), ("right", (O[0] + R) - P[:, 0].max()), ("top", P[:, 1].min() - (O[1] - R)), ("bottom", (O[1] + R) - P[:, 1].max())):
    print("   gap bbox-circle %-6s %.2f" % (nm, m))
print("   touch: nose %.3f tip %.3f A-left %.3f A-right %.3f shield corner %.2f" % (
    R - (math.hypot(*(NOSE_C - O)) + rn), R - (TIPY - yO), R - math.hypot(*(PL - O)), R - math.hypot(*(LT["A2"][2] - O)),
    R - np.hypot(sample(anchors(sh0), 30)[:, 0] - O[0], sample(anchors(sh0), 30)[:, 1] - O[1]).max()))
print("letters: L=F width %.2f | stroke %.1f | channel %.1f | ROBOTICS cap %.1f tracking %.0f/1000em-ish | 8084 cap %.2f clearance %.2f" % (WD, T, GP, ROB_CAP, rob_tr, NUM_CAP, best[0]))
print("levels at axis: U %.1f cap %.1f base %.1f band %.1f-%.1f lower cut %.1f tip %.1f (orig lower cut 328.9)" % (YU, yC, yB, yT, yBB, yLW, TIPY))
print("shield: CY %.2f RS %.2f | A legs" % (CY, RS), [np.round(p, 1).tolist() for p in LT["A1"][:2]], [np.round(p, 1).tolist() for p in LT["A2"][:3]])

# preview
Z = 2.6
doc = pymupdf.open()
pg = doc.new_page(width=side, height=side)
for g in out["groups"]:
    for it in g["items"]:
        sh = pg.new_shape()
        for s in it["subs"]:
            n = len(s)
            for k in range(n):
                a, b = s[k], s[(k + 1) % n]
                if a["o"] == a["p"] and b["i"] == b["p"]:
                    sh.draw_line(pymupdf.Point(a["p"]), pymupdf.Point(b["p"]))
                else:
                    sh.draw_bezier(pymupdf.Point(a["p"]), pymupdf.Point(a["o"]), pymupdf.Point(b["i"]), pymupdf.Point(b["p"]))
        sh.finish(fill=[c / 255 for c in it["rgb"]], color=None, even_odd=True, closePath=True)
        sh.commit()
doc.save(SP + "/emblem_check.pdf")
if "--circle" in sys.argv:
    pg.draw_circle(pymupdf.Point(side / 2, side / 2), R, color=(1, 0, 0), width=0.4)
pg.get_pixmap(matrix=pymupdf.Matrix(Z, Z)).save(SP + "/emblem.png")
c0 = V(30, 20) + off
pg.get_pixmap(matrix=pymupdf.Matrix(3.6, 3.6), clip=pymupdf.Rect(c0[0], c0[1], c0[0] + 320, c0[1] + 215)).save(SP + "/wolf.png")
c0 = V(60, 225) + off
pg.get_pixmap(matrix=pymupdf.Matrix(3.6, 3.6), clip=pymupdf.Rect(c0[0], c0[1], c0[0] + 320, c0[1] + 170)).save(SP + "/text.png")


# ------------------------------------------------------------------ geometric audit
S0 = sample(anchors(sh0), 40)
mir = np.column_stack([2 * X0 - S0[:, 0], S0[:, 1]])
sym = max(np.hypot(S0[:, 0] - q[0], S0[:, 1] - q[1]).min() for q in mir)
SI = sample(anchors(shI), 40)
S0f = sample(anchors(sh0), 400)
dd = np.array([np.hypot(S0f[:, 0] - q[0], S0f[:, 1] - q[1]).min() for q in SI])
print("audit shield: mirror deviation %.4f pt | frame width min %.3f max %.3f" % (sym, dd.min(), dd.max()))
angs = set()
for nm in ("A1", "L", "F", "F1", "F2", "A2"):
    pp = LT[nm]
    for k in range(len(pp)):
        v = pp[(k + 1) % len(pp)] - pp[k]
        angs.add(round(math.degrees(math.atan2(-v[1], v[0])) % 180, 3))
print("audit ALFA edge angles:", sorted(angs))


def kinks(an):
    c = segs(an)
    n, bad, tiny = len(c), 0, 0
    for k in range(n):
        a, b = c[k - 1], c[k]
        ti = next(unit(a[3] - h) for h in (a[2], a[1], a[0]) if math.hypot(*(a[3] - h)) > 1e-6)
        to = next(unit(h - b[0]) for h in (b[1], b[2], b[3]) if math.hypot(*(h - b[0])) > 1e-6)
        dv = math.degrees(math.acos(max(-1, min(1, ti @ to))))
        bad += 0.05 < dv < 38
        tiny += math.hypot(*(b[3] - b[0])) < 0.5
    return n, bad, tiny


for nm, an in (("body", body), ("head", head), ("ear", ear), ("fur1", fur1), ("fur2", fur2)):
    print("audit wolf %-5s nodes %2d | unintended kinks %d | tiny segments %d" % ((nm,) + kinks(an)))
print("original wolf: nodes %d | kinks %d" % (sum(len(W0) for W0 in W.values()), sum(kinks(W[k])[1] for k in W)))

# ------------------------------------------------------------------ wordmark (same lettering, laid flat)
wl = 2 * half
x0_, x1_, y0_, y1_ = text_box(text_contours("8084", 0))
big_cap = wl * (y1_ - y0_) / (x1_ - x0_)
GAPW = 2 * GP
big, _ = place(text_contours("8084", 0), foot - nUp * (GAPW + big_cap / 2), big_cap)
wgroups = [groups[3], groups[4], ("8084", [("8084", "Lacivert", big)])]
pts = []
wj = []
for gname, items in wgroups:
    jg = {"name": gname, "items": []}
    for name, col, subs in items:
        js = []
        for sb in subs:
            sb = [{k: rot(a[k], TH, foot) for k in ("p", "i", "o")} for a in J_(sb)]
            pts.append(sample(sb, 10))
            js.append(sb)
        jg["items"].append({"name": name, "color": col, "rgb": PAL[col], "subs": js})
    wj.append(jg)
Pw = np.vstack(pts)
mg = 0.08 * (Pw[:, 0].max() - Pw[:, 0].min())
ow = V(Pw[:, 0].min() - mg, Pw[:, 1].min() - mg)
Ww, Hw = math.ceil(Pw[:, 0].max() + mg - ow[0]), math.ceil(Pw[:, 1].max() + mg - ow[1])
ow = V((Pw[:, 0].min() + Pw[:, 0].max()) / 2 - Ww / 2, (Pw[:, 1].min() + Pw[:, 1].max()) / 2 - Hw / 2)
for jg in wj:
    for it in jg["items"]:
        it["subs"] = [[{k: [round(float(a[k][0] - ow[0]), 4), round(float(a[k][1] - ow[1]), 4)] for k in ("p", "i", "o")} for a in sb] for sb in it["subs"]]
json.dump({"width": Ww, "height": Hw, "groups": wj}, open(SP + "/wordmark.json", "w"))
print("wordmark: artboard %d x %d | 8084 cap %.1f" % (Ww, Hw, big_cap))
doc = pymupdf.open()
pg = doc.new_page(width=Ww, height=Hw)
for g in wj:
    for it in g["items"]:
        sh = pg.new_shape()
        for sb in it["subs"]:
            n = len(sb)
            for k in range(n):
                a, b = sb[k], sb[(k + 1) % n]
                if a["o"] == a["p"] and b["i"] == b["p"]:
                    sh.draw_line(pymupdf.Point(a["p"]), pymupdf.Point(b["p"]))
                else:
                    sh.draw_bezier(pymupdf.Point(a["p"]), pymupdf.Point(a["o"]), pymupdf.Point(b["i"]), pymupdf.Point(b["p"]))
        sh.finish(fill=[c / 255 for c in it["rgb"]], color=None, even_odd=True, closePath=True)
        sh.commit()
doc.save(SP + "/wordmark_check.pdf")
pg.get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6)).save(SP + "/wordmark.png")

for nm, an in (("body", body), ("head", head), ("fur2", fur2)):
    c = segs(an)
    for k in range(len(c)):
        a, b = c[k - 1], c[k]
        ti = next(unit(a[3] - h) for h in (a[2], a[1], a[0]) if math.hypot(*(a[3] - h)) > 1e-6)
        to = next(unit(h - b[0]) for h in (b[1], b[2], b[3]) if math.hypot(*(h - b[0])) > 1e-6)
        dv = math.degrees(math.acos(max(-1, min(1, ti @ to))))
        if 0.05 < dv < 38 or math.hypot(*(b[3] - b[0])) < 0.5:
            print("  ", nm, k, np.round(b[0], 1), "dev %.2f" % dv, "len %.2f" % math.hypot(*(b[3] - b[0])))
