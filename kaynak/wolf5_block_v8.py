# ------------------------------------------------------------------ wolf (v5)
# One navy silhouette; sky and ice patches lie on it, nothing navy overlaps navy.
# The head is built from lines and arcs, so the navy outline is its exact offset.
W = {}
for it in next(g for g in src["groups"] if g["name"] == "Kurt")["items"]:
    key = {"Kurt govde": "G", "Burun": "B", "Dil": "D", "Yele 1": "Y", "Yele 2": "Z", "Bas ve boyun": "H"}[it["name"]]
    W[key] = [{"p": V(*a["p"]), "i": None if a["i"] == a["p"] else V(*a["i"]), "o": None if a["o"] == a["p"] else V(*a["o"])}
              for a in it["subs"][0]]
FG, FZ = fair(W["G"]), fair(W["Z"])
PIN = PU + WF * nUp
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


WM, RX = 9.0, 3.0                      # outline inside the shield (lip, jaw, throat); small outer roundings
A33 = 33.0
d33, n33 = V(cosd(A33), -sind(A33)), V(-sind(A33), -cosd(A33))
XF, RN = 290.0, 10.0
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
JA = 13.5
ja = V(cosd(JA), -sind(JA))
jn = perp(ja)
JT = V(305.3, 122.2)
tf, tu = V(cosd(110.0), sind(110.0)), V(cosd(157.0), sind(157.0))
JB1 = JT + 16.0 * tf
JB2 = JB1 + 6.0 * tu
a9, P4, t4 = left_arc(JB2, tu, 110.0, 6.0)
a10, P5, t5 = left_arc(P4, t4, 110.0, 30.0)
E = P5 + 22 * t5
T1 = V(178.0, 110.5)                                  # back of the head: one arc up to the frame
ch_ = Pfa - T1
sg_ = 0.10 * math.hypot(*ch_)
rb_ = (ch_ @ ch_ / 4 + sg_ ** 2) / (2 * sg_)
cb_ = (T1 + Pfa) / 2 + (rb_ - sg_) * perp(unit(ch_))
ice_r = fillet([Ar(cb_, T1, Pfa), Ar(CT, Pfa, Pfb), Ln(Pfb, Ki), Ln(Ki, H11), Ar(cl, H11, Cm, -1)], 0, closed=False,
               only={0: 4.0, 1: WO + RX, 2: RN, 3: 2.0})
NOSE_C = next(q["c"] for q in ice_r if q["t"] == "A" and abs(q["r"] - RN) < 1e-6)
jaw = fillet([Ln(JS, JT), Ln(JT, JB1), Ln(JB1, JB2)], 0, closed=False, only={0: 2.5, 1: 7.0}) + [a9, a10, Ln(P5, E)]
chain = ice_r + jaw
ticks = [{"p": V(263.9, 116.4), "i": None, "o": None}, {"p": V(259.8, 126.3), "i": V(260.6, 121.1), "o": None},
         {"p": V(266.4, 127.5), "i": None, "o": None}]
hj_ = anchors(jaw, closed=False)
hj_[0]["i"] = V(263.0, 129.6)
hr = anchors(ice_r, closed=False) + ticks + hj_
# left side: mane lobes separated by dark blades, neck notch at the cut
left = [((224.0, 197.0), 0.07), ((229.0, 152.0), -0.03), ((211.0, 205.0), 0), ((186.2, 224.0), 0.045),
        ((184.5, 156.5), -0.12), ((180.0, 171.5), 0.2), ((190.4, 129.4), -0.15), ((171.5, 147.0), 0.2),
        ((204.4, 103.1), -0.05)]
head = tidy(clip_bez(hr + bows(left, hr[0]), PIN, nUp))

# --- navy/sky boundary on the right = offset of the ice chain
WJT, WJF, WJU = 7.0, 10.0, 12.0                       # navy around the jaw: lip side, front, underside and throat
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
                           only={0: 2.5 + (WJT + WJF) / 2, 1: 7.0 + (WJF + WJU) / 2})
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
skyR = anchors(fillet(loopR, 0, only={2: RCUT, 3: RCUT, nR - 2: 2.5, nR - 1: RX}))

# --- sky, upper left: frame edge + the line of the back
GL, Xtip = arc_y(shI[4], 119.9, -1), arc_x(inA, 205.0)
g0 = {"p": GL, "i": None, "o": FG[0]["o"] + (GL - FG[0]["p"])}
back = [g0, FG[1], dict(FG[2], o=None), {"p": Xtip, "i": V(146.0, 74.0), "o": None}]
skyTL = anchors([dict(shI[4], a=GL), shI[5], dict(inA, b=Xtip)], closed=False)
skyTL[-1]["o"] = back[3]["i"]
skyTL += [{"p": a["p"], "i": a["o"], "o": a["i"]} for a in (back[2], back[1])]
skyTL[0]["i"] = g0["o"]

# --- sky notch on the left edge
DA, DB, D4 = arc_y(shI[4], 130.0, -1), arc_y(shI[4], 159.0, -1), V(74.1, 145.8)
skyD = anchors([dict(shI[4], a=DB, b=DA)], closed=False) + [{"p": D4, "i": None, "o": None}]
skyD[-1]["o"], skyD[0]["i"] = bow(D4, DB, 0.14)

# --- navy silhouette: shield + snout in one path
Qn = Qi + WO * n33
Kn = lineX(Qn, d33, V(xo, 0), V(0, 1))
X1 = min(hits(topA, Qn, d33), key=lambda p: abs(p[0] - 232))
X2 = hits(topA, V(xo, 0), V(0, 1))[0]
nav = fillet([Ar(CT, topA["a"], X1), Ln(X1, Kn), Ln(Kn, X2), Ar(CT, X2, topA["b"])], 0, closed=False,
             only={0: RX, 1: RN + WO, 2: RX})
up_navy = fillet(clip(nav + sh0[1:], PU, nUp), RCUT)

# --- ice details: eye + ear, mane blades; navy details: closed eye, iris
W["B"][14]["o"] = V(100.0, 116.3)      # ear top: one clean sweep instead of a stepped joint
del W["B"][15]
eye = [{k: (None if a_[k] is None else a_[k] + V(0.0, 5.0)) for k in ("p", "i", "o")} for a_ in fair(W["B"])]
_s = V(3.0, 6.0)
_h = [W["H"][k] for k in range(4)]
lid = [{"p": _h[0]["p"] + _s, "i": None, "o": None}, {"p": _h[1]["p"] + _s, "i": _h[1]["i"] + _s, "o": None},
       {"p": _h[2]["p"] + _s, "i": _h[2]["i"] + _s, "o": _h[2]["o"] + _s}, {"p": _h[3]["p"] + _s, "i": None, "o": None}]
lid[3]["o"], lid[0]["i"] = bow(lid[3]["p"], lid[0]["p"], -0.15)
shY = shield(WF + GP)[0][4]
YA, YB, Y4 = arc_y(shY, 187.5, -1), arc_y(shY, 224.0, -1), V(96.7, 179.5)
fur1 = anchors([dict(shY, a=YB, b=YA)], closed=False) + [{"p": Y4, "i": None, "o": None}]
fur1[-2]["o"], fur1[-1]["i"] = bow(YA, Y4, -0.04)
fur1[-1]["o"], fur1[0]["i"] = bow(Y4, YB, -0.07)
fur1, fur2 = tidy(clip_bez(fur1, PIN, nUp)), tidy(clip_bez(FZ, PIN, nUp))
rn = RN + WO
