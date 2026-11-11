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
