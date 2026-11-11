"""Turn mk5_v8.py into mk5.py for v9: square bounding box, circle centred on the logo."""
m = open("mk5_v8.py", encoding="utf-8").read()
NL = chr(92) + "n"          # a literal backslash-n for the generated source


def rep(a, b):
    global m
    assert a in m, a
    m = m.replace(a, b)


rep('"YTIP, RTIP = 397.0, 20.0")', '"YTIP, RTIP = 393.0, 20.0")')
rep('head = rep(head, "PHI = 27.0", "PHI = 24.0")',
    'head = rep(head, "PHI = 27.0", "PHI = 28.0' + NL + 'HALF_X = 22.1        # extra half-span of the A legs: logo as wide as tall")')
rep('mid = rep(mid, "ga = 3.5 ", "ga = 4.5 ")',
    'mid = rep(mid, "ga = 3.5 ", "ga = 4.5 ")\n'
    'mid = rep(mid, "PL, PR = foot - half * dU, foot + half * dU", "half += HALF_X' + NL + 'PL, PR = foot - half * dU, foot + half * dU")\n'
    'mid = rep(mid, "def letters(Wd, gA=4.0, gLF=7.0):", "def letters(Wd, gA=5.5, gLF=9.0):")')
NEWOFF = '''NEWOFF = """_P = np.vstack([sample(J_(s_), 12) for _, its_ in groups for _, _, subs_ in its_ for s_ in subs_])
OB = V((_P[:, 0].min() + _P[:, 0].max()) / 2, (_P[:, 1].min() + _P[:, 1].max()) / 2)
RB = float(np.hypot(_P[:, 0] - OB[0], _P[:, 1] - OB[1]).max())
BW, BH = _P[:, 0].max() - _P[:, 0].min(), _P[:, 1].max() - _P[:, 1].min()
print("BBOX w %.2f h %.2f | circle B R %.2f | gaps L/R %.2f T/B %.2f" % (BW, BH, RB, RB - BW / 2, RB - BH / 2))
side = math.ceil(2 * RB * 1.03)
off = V(side / 2, side / 2) - OB"""
'''
rep('tail = seg(360, 363)', NEWOFF + 'tail = seg(360, 363)')
rep('seg(375, 462) + audit',
    'rep(rep(seg(375, 462), "side = math.ceil(2 * R * (1 + MARG))' + NL + 'off = V(side / 2, side / 2) - O", NEWOFF), '
    '\'"circle": [side / 2, side / 2, round(R, 4)]\', \'"circle": [side / 2, side / 2, round(RB, 4)]\') + audit')
open("mk5.py", "w", encoding="utf-8").write(m)
