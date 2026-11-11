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
RC, WF = 18.0, 14.0                # top corner radius, frame width
YT, RT = 56.0, 490.0               # top arc apex and radius
YTIP, RTIP = 397.0, 20.0           # sharp-tip position before rounding, tip radius
NOSE0, RN0 = (280.0, 55.27097877), 24.0   # nose arc of the navy silhouette (checked in the report)


def _corner_gap(hw):
    cy = YT + RT - math.sqrt((RT - RC) ** 2 - (hw - RC) ** 2)
    rs = (hw ** 2 + (YTIP - cy) ** 2) / (2 * hw)
    tip = cy + math.sqrt((rs - RTIP) ** 2 - (rs - hw) ** 2) + RTIP
    lo, hi = 100.0, 300.0
    for _ in range(60):
        yo = (lo + hi) / 2
        if math.hypot(NOSE0[0] - X0, NOSE0[1] - yo) + RN0 > tip - yo:
            hi = yo
        else:
            lo = yo
    return (tip - yo) - (math.hypot(hw - RC, cy - yo) + RC)


_lo, _hi = 154.0, 175.0
for _ in range(60):
    HW = (_lo + _hi) / 2
    if _corner_gap(HW) > 0:
        _lo = HW
    else:
        _hi = HW
HW = round(HW, 3)     # shield half width: top corners touch the circle through nose and tip
GP = 6.5              # every white channel (perpendicular)
TL = 21.0             # the two long outer legs of the As
LW = 8.0              # navy strip between the lower cut and the 8084 panel = strip under the wolf
T = 18.0              # stroke weight of every ALFA stroke (perpendicular)
CAPH, BANDH = 62.0, 23.0           # ALFA cap height, ROBOTICS band height (vertical measure)
PHI = 24.0            # A legs: +-PHI from vertical
YU = 209.0            # upper cut line at the axis
RCUT = 3.0            # rounding of the cut corners
WO = WF               # outline width around the head = frame width
NAVY, SKY, ICE = [0, 58, 111], [71, 185, 239], [208, 233, 232]

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
up_out = (clip(sh0, PU, nUp))
up_in = (clip(shI, PU + WF * nUp, nUp))
lo_out = (clip(sh0, PL_, -nUp))
lo_in = (clip(shI, PL_ - LW * nUp, -nUp))
TIPY = F[1] + RTIP

# ------------------------------------------------------------------ wolf (v5)
# One navy silhouette; sky and ice patches lie on it, nothing navy overlaps navy.
# The head is built from lines and arcs, so the navy outline is its exact offset.
W = {}
for it in next(g for g in src["groups"] if g["name"] == "Kurt")["items"]:
    key = {"Kurt govde": "G", "Burun": "B", "Dil": "D", "Yele 1": "Y", "Yele 2": "Z", "Bas ve boyun": "H"}[it["name"]]
    W[key] = [{"p": V(*a["p"]), "i": None if a["i"] == a["p"] else V(*a["i"]), "o": None if a["o"] == a["p"] else V(*a["o"])}
              for a in it["subs"][0]]
FG, FZ = fair(W["G"]), fair(W["Z"])
PIN = PU + LW * nUp                    # navy strip under the wolf = strip above the 8084 panel (LW)
cosd, sind = (lambda a: math.cos(rad(a))), (lambda a: math.sin(rad(a)))


def bow(a, b, k):
    """handles of a single even bow from a to b; sagitta = k * chord, positive = left of travel"""
    a, b = V(*a), V(*b)
    ch = b - a
    off = V(ch[1], -ch[0]) * (4 / 3) * k
    return a + ch / 3 + off, b - ch / 3 + off


def bows(nodes, last=None):
    """[(point, k)] -> corner anchors joined by bows; closes on `last` (or on itself)"""
    out = [{"p": V(*p), "i": None, "o": None} for p, _ in nodes]
    for j, (p, k) in enumerate(nodes):
        nxt = out[j + 1] if j + 1 < len(nodes) else (last if last is not None else out[0])
        if k:
            out[j]["o"], nxt["i"] = bow(p, nxt["p"], k)
    return out


def rev(pr):
    q = dict(pr)
    q["a"], q["b"] = pr["b"], pr["a"]
    if pr["t"] == "A":
        q["s"] = -pr["s"]
    return q


def arc_y(pr, y, sgn):
    return V(pr["c"][0] + sgn * math.sqrt(pr["r"] ** 2 - (y - pr["c"][1]) ** 2), y)


def arc_x(pr, x):
    return V(x, pr["c"][1] - math.sqrt(pr["r"] ** 2 - (x - pr["c"][0]) ** 2))


def left_arc(p, t, r, deg):
    c = p - r * perp(t)
    return Ar(c, p, rot(p, -deg, c), -1), rot(p, -deg, c), rot(t, -deg)


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


WJT, WJF, WJU = 8.0, 8.0, 8.0        # navy around the jaw: lip side, front, underside and throat
WM, RX = 9.0, 3.0                      # outline inside the shield (lip, jaw, throat); small outer roundings
A33 = 33.0
d33, n33 = V(cosd(A33), -sind(A33)), V(-sind(A33), -cosd(A33))
XF, RN = 290.0, 10.0
LIPR = 5.0                             # nose front -> upper lip
Qi = V(267.6, 51.4)
inA, topA = shI[0], sh0[0]
xo = XF + WO

# --- ice head, right side: forehead flush with the frame, snout, nose, lip, jaw, throat
Pfa = arc_x(inA, 228.0)
Pfb = min(hits(inA, Qi, d33), key=lambda p: abs(p[0] - 237))
Ki = lineX(Qi, d33, V(XF, 0), V(0, 1))
H11 = V(XF, 82.0)
# mouth as in the original drawing: hollow lip line, two fur ticks at the corner, rising jaw with a blunt front
Cm, JS = V(260.7, 116.9), V(260.5, 133.4)
ch_ = Cm - H11
rl_ = (ch_ @ ch_ / 4 + 2.6 ** 2) / (2 * 2.6)
cl = (H11 + Cm) / 2 - (rl_ - 2.6) * perp(unit(ch_))
JA, JF = 13.5, 105.0
RJT, RJB = 5.0, 10.0                    # outer (navy) radii of the jaw corners; ice = outer - outline, sharp if negative
ja = V(cosd(JA), -sind(JA))
jn = perp(ja)
JT = V(305.3, 122.2)
tf, tu = V(cosd(JF), sind(JF)), V(cosd(157.0), sind(157.0))
JB1 = JT + 16.0 * tf
JB2 = JB1 + 6.0 * tu
# throat: two arcs from the jaw corner that end exactly on the tip of the neck blade (node 20 of the original),
# so the ice tongue between throat and blade closes there as in the original drawing
BS = 4.0 * V(0.9659, -0.2588)                       # neck blade (original nodes 20-23) shift
TT = 0.2                               # throat end: fraction of the way up the blade's right edge (0 = blade tip node 20)
N20 = V(*W["H"][20]["p"]) + BS + TT * (V(*W["H"][21]["p"]) - V(*W["H"][20]["p"]))
_a = left_arc(V(0.0, 0.0), tu, 1.0, 6.0)
_b = left_arc(V(0.0, 0.0), _a[2], 1.0, 30.0)
R9, R10 = np.linalg.solve(np.column_stack([_a[1], _b[1]]), N20 - JB2)
print("throat arcs r %.1f / %.1f" % (R9, R10))
a9, P4, t4 = left_arc(JB2, tu, R9, 6.0)
a10, P5, t5 = left_arc(P4, t4, R10, 30.0)
E = P5 + 22 * t5
# back of the head exactly as in the original drawing (nodes 33-35, 0, 3-6 of the old head path);
# only the closed eye no longer opens into this line, it is a separate shape below it
ice_r = fillet([Ln(Qi, Ki), Ln(Ki, H11), Ar(cl, H11, Cm, -1)], 0, closed=False, only={0: RN, 1: LIPR})
NOSE_C = next(q["c"] for q in ice_r if q["t"] == "A" and abs(q["r"] - RN) < 1e-6)
JIN = {k_: max(v_, 1.0) for k_, v_ in ((0, RJT - (WJT + WJF) / 2), (1, RJB - (WJF + WJU) / 2))}   # concentric, or 1 pt if the outline is too thick
jaw = fillet([Ln(JS, JT), Ln(JT, JB1), Ln(JB1, JB2)], 0, closed=False, only=JIN) + [a9, a10]
chain = ice_r + jaw
ticks = [{"p": V(263.9, 116.4), "i": None, "o": None}, {"p": V(259.8, 126.3), "i": V(260.6, 121.1), "o": None},
         {"p": V(266.4, 127.5), "i": None, "o": None}]
hj_ = anchors(jaw, closed=False)
hj_[0]["i"] = V(263.0, 129.6)
def _hn(k, s=V(0.0, 0.0)):
    a = W["H"][k]
    return {"p": a["p"] + s, "i": None if a["i"] is None else a["i"] + s, "o": None if a["o"] is None else a["o"] + s}
top_ = [_hn(33), _hn(34), _hn(35), dict(_hn(0), o=None), dict(_hn(3), i=None), _hn(4), _hn(5), dict(_hn(6), o=None)]
hr = top_ + anchors(ice_r, closed=False) + ticks + hj_
# left side: mane lobes separated by dark blades, neck notch at the cut
HK = V(0.0, -8.0)                       # the hook under the second blade, lifted clear of the (higher) cut
left = [_hn(21, BS), _hn(22, BS), _hn(23, BS), _hn(24), _hn(25, HK), _hn(26, HK), _hn(27, HK), _hn(28), _hn(29), _hn(30), _hn(31)]
left += [dict(_hn(32), o=None)]
head = tidy(clip_bez(hr + left, PIN, nUp))

# --- navy/sky boundary on the right = offset of the ice chain
gq, gd = V(304.8, 71.2), V(cosd(115.5), sind(115.5))  # upper lip edge of the sky, as drawn originally
Xa = min(hits(inA, gq, gd), key=lambda p: abs(p[0] - xo))


def off_out(pr, w):
    if pr["t"] == "L":
        n_ = -perp(unit(pr["b"] - pr["a"]))
        return Ln(pr["a"] + w * n_, pr["b"] + w * n_)
    k_ = (pr["r"] + pr["s"] * w) / pr["r"]
    return Ar(pr["c"], pr["c"] + k_ * (pr["a"] - pr["c"]), pr["c"] + k_ * (pr["b"] - pr["c"]), pr["s"])


o_t, o_f, o_u = off_out(Ln(JS, JT), WJT), off_out(Ln(JT, JB1), WJF), off_out(Ln(JB1, JB2), WJU)
Wc = lineX(gq, gd, o_t["a"], ja)
c1_, c2_ = lineX(o_t["a"], ja, o_f["a"], tf), lineX(o_f["a"], tf, o_u["a"], tu)
wr = [Ln(Xa, Wc)] + fillet([Ln(Wc, c1_), Ln(c1_, c2_), Ln(c2_, o_u["b"])], 0, closed=False,
                           only={0: RJT, 1: RJB})
wr += [off_out(a9, WJU), off_out(a10, WJU), Ln(off_out(a10, WJU)["b"], off_out(a10, WJU)["b"] + 22 * t5)]
for j in (len(wr) - 2, len(wr) - 1):
    h = hits(wr[j], PIN, dU)
    if h:
        wr = wr[:j] + [dict(wr[j], b=h[0])]
        break
Xd = wr[-1]["b"]
QR = hits(shI[2], PIN, dU)[0]
loopR = [Ar(CT, Xa, inA["b"]), shI[1], dict(shI[2], b=QR), Ln(QR, Xd)] + [rev(p) for p in reversed(wr)]
nR = len(loopR)
skyR = anchors(fillet(loopR, 0, only={3: 1.0, nR - 2: 1.5, nR - 1: RX}))

# --- sky, upper left: frame edge + the line of the back
GL, Xtip = arc_y(shI[4], 119.9, -1), arc_x(inA, 205.0)
g0 = {"p": GL, "i": None, "o": FG[0]["o"] + (GL - FG[0]["p"])}
back = [g0, FG[1], dict(FG[2], o=None), {"p": Xtip, "i": V(146.0, 74.0), "o": None}]
BACK1 = True                           # back line from its corner to the frame as ONE even curve (the frame moved out
if BACK1:                              # with the wider shield, so the original short end piece made a kink)
    _p2 = FG[2]["p"]
    _L = math.hypot(*(GL - _p2)) / 3
    _t2 = unit(V(98.3, 109.4) - _p2)                     # original tangent leaving the corner (node 2 of W["G"])
    _t0 = unit(V(52.0, 118.1) - V(48.1, 119.9))          # original tangent at the frame (node 0)
    g0 = {"p": GL, "i": None, "o": GL + _L * _t0}
    back = [g0, dict(FG[2], i=_p2 + _L * _t2, o=None), {"p": Xtip, "i": V(146.0, 74.0), "o": None}]
SKY_EAR = False                        # sky edge above the ear = the ear's top line offset by WE (constant navy)
WE = 8.0
if SKY_EAR:
    _e = [V(*W["B"][14]["p"]), V(100.0, 116.3), V(*W["B"][0]["i"]), V(*W["B"][0]["p"])]   # ear top (see eye below)
    _bz = lambda t: (1 - t) ** 3 * _e[0] + 3 * (1 - t) ** 2 * t * _e[1] + 3 * (1 - t) * t * t * _e[2] + t ** 3 * _e[3]
    def _sub(t0, t1):                   # sub-curve of the ear top by de Casteljau
        def split(P, t):
            a, b, c = P[0] + t * (P[1] - P[0]), P[1] + t * (P[2] - P[1]), P[2] + t * (P[3] - P[2])
            d, e = a + t * (b - a), b + t * (c - b)
            f = d + t * (e - d)
            return [P[0], a, d, f], [f, e, c, P[3]]
        R_ = split(_e, t0)[1]
        return split(R_, (t1 - t0) / (1 - t0))[0]
    def _off(P, w):                     # Tiller-Hanson offset of a cubic towards the sky (left of travel = up)
        ln = [(P[k] + w * V((P[k + 1] - P[k])[1], -(P[k + 1] - P[k])[0]) / math.hypot(*(P[k + 1] - P[k])),
               unit(P[k + 1] - P[k])) for k in range(3)]
        return [ln[0][0], lineX(ln[0][0], ln[0][1], ln[1][0], ln[1][1]), lineX(ln[1][0], ln[1][1], ln[2][0], ln[2][1]),
                ln[2][0] + math.hypot(*(P[3] - P[2])) * ln[2][1]]
    _bd = unit(V(146.0, 74.0) - FG[2]["p"])            # back line leaving its corner towards the snout
    _ts = np.linspace(0.0, 0.97, 400)
    _q = [_off(_sub(max(t_ - 0.01, 0.0), t_ + 0.01), -WE)[1] for t_ in _ts[1:]]
    _sd = [((q_ - FG[2]["p"]) @ V(_bd[1], -_bd[0])) for q_ in _q]
    t_r = next(_ts[1:][k] for k in range(1, len(_q)) if _sd[k - 1] * _sd[k] <= 0)
    t_l = 0.85                          # left of this the ear top turns down into its tip: go straight to the frame
    _o = _off(_sub(t_r, t_l), -WE)
    _dl = unit(_o[3] - _o[2])
    GL = min(hits(shI[4], _o[3], _dl), key=lambda q: math.hypot(*(q - _o[3])))
    g0 = {"p": GL, "i": None, "o": None}
    back = [g0, {"p": _o[3], "i": None, "o": _o[2]}, {"p": _o[0], "i": _o[1], "o": None},
            {"p": Xtip, "i": V(146.0, 74.0), "o": None}]
    print("sky over ear: corner", np.round(_o[0], 2), "frame", np.round(GL, 2), "t %.3f" % t_r)
    skyTL = anchors([dict(shI[4], a=GL), shI[5], dict(inA, b=Xtip)], closed=False)
    skyTL[-1]["o"] = back[3]["i"]
    skyTL += [{"p": a_["p"], "i": a_["o"], "o": a_["i"]} for a_ in (back[2], back[1])]
else:
    skyTL = anchors([dict(shI[4], a=GL), shI[5], dict(inA, b=Xtip)], closed=False)
    skyTL[-1]["o"] = back[-1]["i"]
    skyTL += [{"p": a["p"], "i": a["o"], "o": a["i"]} for a in reversed(back[1:-1])]
skyTL[0]["i"] = g0["o"]

# --- sky notch on the left edge
DA, DB, D4 = arc_y(shI[4], 130.0, -1), arc_y(shI[4], 159.0, -1), V(74.1, 145.8)
def arc3(a, b, k):
    """arc from a to b with sagitta k * chord (positive = bulging left of travel, like bow)"""
    ch = b - a
    L = math.hypot(*ch)
    sg = abs(k) * L
    r = (L * L / 4 + sg * sg) / (2 * sg)
    nl = V(ch[1], -ch[0]) / L * (1 if k > 0 else -1)
    c = (a + b) / 2 + (sg - r) * nl
    return min((Ar(c, a, b, 1), Ar(c, a, b, -1)), key=lambda q: math.hypot(*(mid(q) - ((a + b) / 2 + sg * nl))))


notchA = arc3(D4, DB, 0.14)             # lower edge of the notch: a true arc, so the mane below is its exact offset
skyD = anchors([dict(shI[4], a=DB, b=DA), Ln(DA, D4), notchA])

# --- navy silhouette: shield + snout in one path
Qn = Qi + WO * n33
Kn = lineX(Qn, d33, V(xo, 0), V(0, 1))
X1 = min(hits(topA, Qn, d33), key=lambda p: abs(p[0] - 232))
X2 = hits(topA, V(xo, 0), V(0, 1))[0]
nav = fillet([Ar(CT, topA["a"], X1), Ln(X1, Kn), Ln(Kn, X2), Ar(CT, X2, topA["b"])], 0, closed=False,
             only={0: RX, 1: RN + WO, 2: RX})
up_navy = clip(nav + sh0[1:], PU, nUp)

# --- ice details: eye + ear, mane blades; navy details: closed eye, iris
W["B"][14]["o"] = V(100.0, 116.3)      # ear top: one clean sweep instead of a stepped joint
del W["B"][15]
eye = [dict(a_) for a_ in W["B"]]      # ear/eye: original nodes in place (user); only the top is one clean sweep (above)
_s = V(5.0, 4.5)
_h = [W["H"][k] for k in range(4)]
lid = [{"p": _h[0]["p"] + _s, "i": None, "o": None}, {"p": _h[1]["p"] + _s, "i": _h[1]["i"] + _s, "o": None},
       {"p": _h[2]["p"] + _s, "i": _h[2]["i"] + _s, "o": _h[2]["o"] + _s}, {"p": _h[3]["p"] + _s, "i": None, "o": None}]
lid[3]["o"], lid[0]["i"] = bow(lid[3]["p"], lid[0]["p"], -0.08)
shY = shield(WF + GP)[0][4]
FPX, FZD, FK = 76.0, 7.0, -0.15         # mane 1: x of the upper tuft, depth of the bottom tip in the frame strip, valley between the tufts
# mane 1: top edge concentric with the notch (WM navy between), left edge parallel to the frame,
# bottom tip pushed through the inner frame corner into the frame band
rF = notchA["r"] + WM
cN = notchA["c"]
dcc = math.hypot(*(shY["c"] - cN))
a_ = (rF ** 2 - shY["r"] ** 2 + dcc ** 2) / (2 * dcc)
h_ = math.sqrt(rF ** 2 - a_ ** 2)
u_ = unit(shY["c"] - cN)
YA = max((cN + a_ * u_ + sg_ * h_ * V(-u_[1], u_[0]) for sg_ in (1, -1)), key=lambda p: p[1])
YP = V(FPX, cN[1] + math.sqrt(rF ** 2 - (FPX - cN[0]) ** 2))      # upper tuft: end of the concentric edge
Y4 = V(96.7, 179.5)                                                # lower tuft, as before
YZ = next(p for p in (arc_y(shY, y_, -1) for y_ in np.arange(215.0, 250.0, 0.02)) if (p - PIN) @ -nUp >= FZD)
topF = min((Ar(cN, YA, YP, 1), Ar(cN, YA, YP, -1)), key=lambda q: abs(sweep(q)))
fur1 = anchors([dict(shY, a=YZ, b=YA), topF], closed=False) + [{"p": Y4, "i": None, "o": None}]
fur1[-2]["o"], fur1[-1]["i"] = bow(YP, Y4, FK)
fur1[-1]["o"], fur1[0]["i"] = bow(Y4, YZ, -0.07)
FUR_ORIG = True                        # mane 1 exactly as in the original drawing (nodes of W["Y"])
TIPK = -0.08
FUP = 8.0                              # mane 1 slid this far up along the inner frame edge
TIPD = 6.0                             # mane 1: bottom tip carried this far further down along the inner frame edge
if FUR_ORIG:
    # the original mane, moved out until its left edge lies on the line of the sky notch's left edge, i.e. the inner
    # frame edge shI[4] continued (concentric with the outer contour); that edge is now exactly this arc (user, item 10)
    _C, _R = shI[4]["c"], shI[4]["r"]
    _c1 = V(*W["Y"][1]["p"])
    FSH = (_R - math.hypot(*(_c1 - _C))) * unit(_c1 - _C)
    _f = [{k: (None if a[k] is None else a[k] + FSH) for k in ("p", "i", "o")} for a in W["Y"]]
    if FUP:                                 # whole mane slid up along the arc (left edge stays on it)
        _ang = min((s_ * math.degrees(FUP / _R) for s_ in (1, -1)), key=lambda g: rot(_c1 + FSH, g, _C)[1])
        _f = [{k: (None if a[k] is None else rot(a[k], _ang, _C)) for k in ("p", "i", "o")} for a in _f]
    _on = lambda q: _C + _R * unit(q - _C)
    P0, P2 = _on(_f[0]["p"]), _on(_f[2]["p"])
    if TIPD:
        P2 = max((rot(P2, s_ * math.degrees(TIPD / _R), _C) for s_ in (1, -1)), key=lambda q: q[1])
    fur1 = anchors([dict(shI[4], a=P2, b=P0)], closed=False)
    fur1[-1]["o"] = _f[0]["i"] + (P0 - _f[0]["p"])
    fur1 += [{"p": _f[k]["p"], "i": _f[k]["o"], "o": _f[k]["i"]} for k in (5, 4, 3)]
    fur1[0]["i"] = _f[2]["o"] + (_on(_f[2]["p"]) - _f[2]["p"])
    if TIPD:                                # longer tip: right edge as one even bow from the upper tip (node 4)
        del fur1[-1]
        fur1[-1]["o"], fur1[0]["i"] = bow(_f[4]["p"], P2, TIPK)
    fur1 = tidy(clip_bez(fur1, PIN if TIPD == 0 else PU, nUp))
fur2 = tidy(clip_bez(FZ, PIN, nUp))
rn = RN + WO

# ------------------------------------------------------------------ enclosing circle (axis-centred)
# touches the nose and the shield tip; the A legs are then made to end exactly on it
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
    WL = TL / math.cos(rad(PHI))
    wl, wr_ = (WL, WH) if long_left else (WH, WL)
    aL = toline(p_outer, dl, cap)
    aR = aL + ((WL + WH) / 2 / dU[0]) * dU
    fl, fr = (bbot, base) if long_left else (base, bbot)
    ro, ri = toline(aR, dr, fr), toline(aR - wr_ * hx, dr, fr)
    notch = lineX(aL + wl * hx, dl, aR - wr_ * hx, dr)
    li = toline(aL + wl * hx, dl, fl)
    return [aL, aR, ro, ri, notch, li, p_outer], aL, aR


def letters(Wd, gA=4.0, gLF=7.0):
    A1, a1L, a1R = letter_A(PL, True)
    xL = A1[2][0] + gA
    Lp = [on(cap, xL), on(cap, xL + T), on(lvl(yB - TB), xL + T), on(lvl(yB - TB), xL + Wd), on(base, xL + Wd), on(base, xL)]
    xF = xL + Wd + gLF
    ga = 4.5                                           # stem-arm separation of the F
    Fs = [on(cap, xF), on(cap, xF + T), on(base, xF + T), on(base, xF)]
    F1 = [on(cap, xF + T + ga), on(cap, xF + Wd), on(lvl(yC + TB), xF + Wd), on(lvl(yC + TB), xF + T + ga)]
    ym = yC + TB + e                        # middle arm, optically a touch below centre
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
ROB_CAP, ROB_SX = 13.5, 1.17      # horizontal scale of the ROBOTICS glyphs, as in the original drawing (measured)
ROB_M, ROB_DU = 6.385, 0.505       # ROBOTICS ends: inset from the band ends, shift along the band


def _rob_tc(s_, tr_):
    return [[{k: (None if a[k] is None else V(a[k][0] * ROB_SX, a[k][1])) for k in ("p", "i", "o")} for a in c]
            for c in text_contours(s_, tr_)]


def fit_rob(s_, centre, cap_perp, length):
    w0 = place(_rob_tc(s_, 0), centre, cap_perp)[1]
    w1 = place(_rob_tc(s_, 100), centre, cap_perp)[1]
    tr_ = (length - w0) / (w1 - w0) * 100
    return place(_rob_tc(s_, tr_), centre, cap_perp)[0], tr_
robotics, rob_tr = fit_rob("ROBOTICS", (bL + bR) / 2 + ROB_DU * dU, ROB_CAP, math.hypot(*(bR - bL)) - 2 * ROB_M)

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


NUM_TR, NUM_CLEAR = 0.0, 1.0
cen0 = panel.mean(axis=0)
NUM_CAPFIX = 18.5                     # 8084 size chosen by the user (pt); None = largest that fits NUM_CLEAR
best = None
for capn in np.arange(26.0, 9.0, -0.5):
    for du in np.arange(-12, 12.01, 2.0):
        for dn in np.arange(-18, 14.01, 2.0):
            cs = place(text_contours("8084", NUM_TR), cen0 + du * dU + dn * nUp, capn)[0]
            c = clearance(cs)
            if c >= NUM_CLEAR and (best is None or c > best[0]):
                best = (c, capn, cs, du, dn)
    if best:
        break
_b0 = best
if NUM_CAPFIX:                                # fixed size: place it where the margin to the panel edge is largest
    best = None
    for du in np.arange(-12, 12.01, 1.0):
        for dn in np.arange(-18, 26.01, 1.0):
            cs = place(text_contours("8084", NUM_TR), cen0 + du * dU + dn * nUp, NUM_CAPFIX)[0]
            c = clearance(cs)
            if best is None or c > best[0]:
                best = (c, NUM_CAPFIX, cs, du, dn)
    _b1 = best
    for du in np.arange(_b1[3] - 1, _b1[3] + 1.01, 0.25):
        for dn in np.arange(_b1[4] - 1, _b1[4] + 1.01, 0.25):
            cs = place(text_contours("8084", NUM_TR), cen0 + du * dU + dn * nUp, NUM_CAPFIX)[0]
            c = clearance(cs)
            if c > best[0]:
                best = (c, NUM_CAPFIX, cs, du, dn)
    _b0 = best
for capn in ([] if NUM_CAPFIX else np.arange(_b0[1] + 3.0, _b0[1] - 0.01, -0.25)):
    for du in np.arange(_b0[3] - 3, _b0[3] + 3.01, 0.5):
        for dn in np.arange(_b0[4] - 3, _b0[4] + 9.01, 0.5):
            cs = place(text_contours("8084", NUM_TR), cen0 + du * dU + dn * nUp, capn)[0]
            c = clearance(cs)
            if c >= NUM_CLEAR and (best is None or capn > best[1] or (capn == best[1] and c > best[0])):
                best = (c, capn, cs, du, dn)
    if best[1] > _b0[1] or capn <= _b0[1]:
        break
print("8084 scan: coarse cap %.2f at (%.0f, %.0f) -> fine cap %.2f at (%.1f, %.1f)" % (_b0[1], _b0[3], _b0[4], best[1], best[3], best[4]))
num, NUM_CAP = best[2], best[1]

# ------------------------------------------------------------------ assemble
def J_(an):
    return [{"p": a["p"], "i": a["i"] if a.get("i") is not None else a["p"], "o": a["o"] if a.get("o") is not None else a["p"]} for a in an]


groups = [
    ("Kalkan ust", [("Lacivert siluet", "Lacivert", [anchors(up_navy)]), ("Gok sol", "Acik Mavi", [skyTL]),
                    ("Gok sag", "Acik Mavi", [skyR]), ("Gok centik", "Acik Mavi", [skyD])]),
    ("Kalkan alt", [("Cerceve", "Lacivert", [anchors(lo_out)]), ("Zemin", "Acik Mavi", [lo_in_an])]),
    ("Kurt", [("Bas ve boyun", "Buz", [head]), ("Goz ve kulak", "Buz", [eye]), ("Yele 1", "Buz", [fur1]),
              ("Yele 2", "Buz", [fur2]), ("Kapali goz", "Lacivert", [lid])]),
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


# KINKDBG
c_ = segs(head)
for k_ in range(len(c_)):
    a_, b_ = c_[k_ - 1], c_[k_]
    ti_ = next(unit(a_[3] - h) for h in (a_[2], a_[1], a_[0]) if math.hypot(*(a_[3] - h)) > 1e-6)
    to_ = next(unit(h - b_[0]) for h in (b_[1], b_[2], b_[3]) if math.hypot(*(h - b_[0])) > 1e-6)
    dv_ = math.degrees(math.acos(max(-1, min(1, ti_ @ to_))))
    if 0.05 < dv_ < 38: print('  head kink at', np.round(b_[0], 1), 'dev %.2f' % dv_)

for nm, an in (("head", head), ("eye", eye), ("fur1", fur1), ("fur2", fur2), ("skyR", skyR), ("skyTL", skyTL)):
    print("audit wolf %-5s nodes %2d | unintended kinks %d | tiny segments %d" % ((nm,) + kinks(an)))

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
