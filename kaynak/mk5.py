"""Assemble design5.py from design.py (lettering, text, output) + wolf5_block.py (new wolf)."""
L = open("design.py", encoding="utf-8").read().split("\n")


def seg(a, b):
    return "\n".join(L[a - 1:b])


def rep(s, a, b):
    assert a in s, a
    return s.replace(a, b)


head = seg(1, 66)
head = rep(head, "CAPH, BANDH = 57.0, 21.0", "CAPH, BANDH = 62.0, 23.0")
head = rep(head, "PHI = 27.0", "PHI = 24.0")
head = rep(head, "YU = 213.0", "YU = 209.0")
head = rep(head, "YTIP, RTIP = 392.0, 20.0", "YTIP, RTIP = 397.0, 20.0")
head = rep(head, "T = 18.0 ", "TL = 21.0             # the two long outer legs of the As\nLW = 8.0              # navy strip between the lower cut and the 8084 panel = strip under the wolf\nT = 18.0 ")
head = rep(head, "clip(shI, PL_ - WF * nUp, -nUp)", "clip(shI, PL_ - LW * nUp, -nUp)")
# v10: sharp cut corners, old ice tone, shield widened until its top corners touch the circle (6 contact points)
for nm_ in ("up_out", "up_in", "lo_out", "lo_in"):
    head = rep(head, nm_ + " = fillet(clip(", nm_ + " = (clip(")
head = head.replace(", RCUT)" + chr(10), ")" + chr(10))
head = rep(head, "[235, 247, 252]", "[208, 233, 232]")
head = rep(head, "[71, 185, 239]", "[99, 196, 242]")      # SKY (Acik Mavi)
head = rep(head, "HW, RC, WF = 154.0, 18.0, 14.0     # shield half width, top corner radius, frame width",
           "RC, WF = 18.0, 14.0                # top corner radius, frame width")
head = rep(head, "GP = 6.5 ", '''NOSE0, RN0 = (280.0, 55.27097877), 24.0   # nose arc of the navy silhouette (checked in the report)


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
GP = 6.5 ''')
mid = seg(183, 358)
old_A = seg(215, 231)
new_A = '''def letter_A(p_outer, long_left):
    """p_outer: end of the long leg on the band-bottom line (left A) or of the short leg on the baseline (right A)"""
    WL = TL / math.cos(rad(PHI))
    wl, wr_ = (WL, WH) if long_left else (WH, WL)
    aL = toline(p_outer, dl, cap)
    aR = aL + ((WL + WH) / 2 / dU[0]) * dU
    fl, fr = (bbot, base) if long_left else (base, bbot)
    ro, ri = toline(aR, dr, fr), toline(aR - wr_ * hx, dr, fr)
    notch = lineX(aL + wl * hx, dl, aR - wr_ * hx, dr)
    li = toline(aL + wl * hx, dl, fl)
    return [aL, aR, ro, ri, notch, li, p_outer], aL, aR'''
mid = rep(mid, old_A, new_A)
mid = rep(mid, "rn = RN + WO\n", "")
mid = rep(mid, "ga = 3.5 ", "ga = 4.5 ")
mid = rep(mid, "ym = yC + (CAPH - TB) / 2 + 1.0 ", "ym = yC + TB + e    ")
mid = rep(mid, "- 2 * 26.0)", "- 2 * ROB_M)")
mid = rep(mid, "ROB_CAP = 12.0", """ROB_CAP, ROB_SX = 13.5, 1.17      # horizontal scale of the ROBOTICS glyphs, as in the original drawing (measured)
ROB_M, ROB_DU = 6.385, 0.505       # ROBOTICS ends: inset from the band ends, shift along the band


def _rob_tc(s_, tr_):
    return [[{k: (None if a[k] is None else V(a[k][0] * ROB_SX, a[k][1])) for k in ("p", "i", "o")} for a in c]
            for c in text_contours(s_, tr_)]


def fit_rob(s_, centre, cap_perp, length):
    w0 = place(_rob_tc(s_, 0), centre, cap_perp)[1]
    w1 = place(_rob_tc(s_, 100), centre, cap_perp)[1]
    tr_ = (length - w0) / (w1 - w0) * 100
    return place(_rob_tc(s_, tr_), centre, cap_perp)[0], tr_""")
mid = rep(mid, 'robotics, rob_tr = fit_text("ROBOTICS", (bL + bR) / 2,', 'robotics, rob_tr = fit_rob("ROBOTICS", (bL + bR) / 2 + ROB_DU * dU,')
mid = rep(mid, "NUM_TR, NUM_CLEAR = 0.0, 4.0", "NUM_TR, NUM_CLEAR = 0.0, 1.0")   # min. gap 8084 - panel edge
# 8084: coarse scan over a wide area of the panel, then a narrow fine scan around the best spot (largest size first)
mid = rep(mid, seg(348, 358), """NUM_CAPFIX = 18.5                     # 8084 size chosen by the user (pt); None = largest that fits NUM_CLEAR
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
num, NUM_CAP = best[2], best[1]""")
groups = '''groups = [
    ("Kalkan ust", [("Lacivert siluet", "Lacivert", [anchors(up_navy)]), ("Gok sol", "Acik Mavi", [skyTL]),
                    ("Gok sag", "Acik Mavi", [skyR]), ("Gok centik", "Acik Mavi", [skyD])]),
    ("Kalkan alt", [("Cerceve", "Lacivert", [anchors(lo_out)]),
                    ("Zemin (8084 bosluklu)", "Acik Mavi", [lo_in_an] + [smooth_joins(drop_tiny(c_), 20.0) for c_ in num])]),
    ("Kurt", [("Bas ve boyun (kapali goz bosluklu)", "Buz", [head, lid]), ("Goz ve kulak", "Buz", [eye]), ("Yele 1", "Buz", [fur1]),
              ("Yele 2", "Buz", [fur2])]),
    ("ALFA", [("A sol", "Lacivert", [poly(LT["A1"])]), ("L", "Lacivert", [poly(LT["L"])]),
              ("F", "Lacivert", [poly(LT["F"]), poly(LT["F1"]), poly(LT["F2"])]), ("A sag", "Lacivert", [poly(LT["A2"])])]),
    ("ROBOTICS", [("Bant + ROBOTICS", "Lacivert", [poly(band)] + [smooth_joins(drop_tiny(c_), 20.0) for c_ in robotics])]),
]'''
audit = '''
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
'''
tail = seg(360, 363) + "\n\n" + groups + "\n" + seg(375, 462) + audit + "\n" + seg(467, 512) + "\n"
tail = rep(tail, '("8084", [("8084", "Lacivert", big)])', '("8084", [("8084", "Lacivert", [smooth_joins(drop_tiny(c_), 20.0) for c_ in big])])')
src_ = head + "\n\n" + open("wolf5_block.py", encoding="utf-8").read() + "\n" + mid + "\n\n" + tail
# v11: ALFA + ROBOTICS band slid along the lettering line so that, with the emblem framed symmetrically (shield axis /
# midway between nose top and shield tip), both outer A tips are the same horizontal distance from the frame circle
# (circle radius = farthest point / 0.92, as in the profile picture). Sizes unchanged.
src_ = rep(src_, "def letters(Wd, gA=4.0, gLF=7.0):\n    A1, a1L, a1R = letter_A(PL, True)",
           "ALFA_SHIFT = float(__import__('os').environ.get('ALFA_SHIFT', '-4.369323'))   # pt along the lettering line (negative = left)\n\n\ndef letters(Wd, gA=4.0, gLF=7.0, sh=0.0):\n    A1, a1L, a1R = letter_A(PL + sh * dU, True)")
src_ = rep(src_, "LT = letters(WD)\n", "LT = letters(WD, sh=ALFA_SHIFT)\n")
src_ = rep(src_, "side = math.ceil(2 * R * (1 + MARG))\noff = V(side / 2, side / 2) - O\n",
           """# v11 frame circle: centred on the shield axis; its height is chosen so that the vertical distance from the nose top up
# to the profile circle equals the one from the shield tip down to it (profile circle = frame circle / 0.92)
_raw = np.vstack([sample(J_(s_), 12) for _, items_ in groups for _, _, subs_ in items_ for s_ in subs_])
_nt, _tp = V(NOSE_C[0], NOSE_C[1] - rn), V(X0, TIPY)          # nose top, shield tip
def _frame(cy_):
    rf_ = float(np.hypot(_raw[:, 0] - X0, _raw[:, 1] - cy_).max()); rp_ = rf_ / 0.92
    return rf_, rp_, _nt[1] - (cy_ - math.sqrt(rp_ ** 2 - (_nt[0] - X0) ** 2)), (cy_ + rp_) - _tp[1]
_lo, _hi = _nt[1], _tp[1]
for _ in range(80):
    _cy = (_lo + _hi) / 2
    _, _, _gt, _gb = _frame(_cy)
    if _gt > _gb: _lo = _cy
    else: _hi = _cy
CEN = V(X0, _cy)
RF, _Rp, _gt, _gb = _frame(_cy)                                # frame circle through the farthest point
# square artboard: centred on the shield axis and midway between the nose top and the shield tip, so the shield
# corners are equally far from the left / right edges and nose top / shield tip from the top / bottom edges
SQ = V(X0, (_nt[1] + _tp[1]) / 2)
side = math.ceil(2 * float(np.hypot(_raw[:, 0] - SQ[0], _raw[:, 1] - SQ[1]).max()) * (1 + MARG))
off = V(side / 2, side / 2) - SQ
def _gaps(s_):
    l_, r_ = LT["A1"][6] + s_ * dU, LT["A2"][2] + s_ * dU
    return l_[0] - (X0 - math.sqrt(_Rp ** 2 - (l_[1] - _cy) ** 2)), (X0 + math.sqrt(_Rp ** 2 - (r_[1] - _cy) ** 2)) - r_[0]
_lo, _hi = -20.0, 20.0
for _ in range(80):
    _m = (_lo + _hi) / 2
    _a, _b = _gaps(_m)
    if _a > _b: _hi = _m
    else: _lo = _m
print("frame: centre (%.4f, %.4f) RF %.4f Rp %.4f | nose top (%.3f, %.3f) raw top %.3f" % (CEN[0], CEN[1], RF, _Rp, _nt[0], _nt[1], _raw[:, 1].min()))
print("PTS " + " ".join("%.4f" % v_ for v_ in (_nt[0], _nt[1], _tp[0], _tp[1], LT["A1"][6][0], LT["A1"][6][1], LT["A2"][2][0], LT["A2"][2][1], CEN[0], CEN[1], _Rp, side, SQ[1], _raw[:, 0].min(), _raw[:, 0].max())))
print("SQUARE side %d centre y %.4f | edge gaps: nose top %.4f shield tip %.4f | art left %.4f right %.4f | circle centre is %.4f pt above the square centre" % (
    side, SQ[1], _nt[1] - (SQ[1] - side / 2), (SQ[1] + side / 2) - _tp[1], _raw[:, 0].min() - (X0 - side / 2), (X0 + side / 2) - _raw[:, 0].max(), SQ[1] - CEN[1]))
print("GAPS vertical: top %.6f bottom %.6f | horizontal: left %.6f right %.6f | next ALFA_SHIFT %.6f" % ((_gt, _gb) + _gaps(0) + (ALFA_SHIFT + _m,)))
""")
src_ = rep(src_, '"circle": [side / 2, side / 2, round(R, 4)]', '"circle": [side / 2, round(float(side / 2 + CEN[1] - SQ[1]), 4), round(RF, 4)]')
# the wordmark keeps its v10 layout: its 8084 follows the shifted lettering
src_ = rep(src_, 'place(text_contours("8084", 0), foot - nUp * (GAPW + big_cap / 2), big_cap)',
           'place(text_contours("8084", 0), foot + ALFA_SHIFT * dU - nUp * (GAPW + big_cap / 2), big_cap)')
open("design5.py", "w", encoding="utf-8").write(src_)
