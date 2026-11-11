"""ROBOTICS fit check: rob_olc.py emblem_check.pdf -> top margin, gaps at the band's top corners (pt)."""
import sys, pymupdf, numpy as np
pg = pymupdf.open(sys.argv[1])[0]
d = next(d for d in pg.get_drawings() if d['rect'].y0 > 200 and d['rect'].y1 < 380 and d['rect'].width > 150)
P = np.array([(p.x, p.y) for it in d['items'] for p in it[1:] if isinstance(p, pymupdf.Point)])
band = np.unique(np.round(P[:8], 3), axis=0); L = P[8:]
c = band.mean(0); u = np.linalg.svd(band - c)[2][0]; u = u if u[0] > 0 else -u; n = np.array([u[1], -u[0]])  # n points up
bu, bn = (band - c) @ u, (band - c) @ n
o = np.argsort(bu); lft, rgt = o[:2], o[2:]
TL_, BL_ = (lft if bn[lft[0]] > bn[lft[1]] else lft[::-1]); TR_, BR_ = (rgt if bn[rgt[0]] > bn[rgt[1]] else rgt[::-1])
u = (band[TR_] - band[TL_]) + (band[BR_] - band[BL_]); u = u / np.hypot(*u); n = np.array([u[1], -u[0]])
bu, bn = (band - c) @ u, (band - c) @ n; lu, ln = (L - c) @ u, (L - c) @ n
TLi, TRi, BLi, BRi = TL_, TR_, BL_, BR_; top = np.isin(np.arange(4), [TL_, TR_])
cap = ln.max(); sel = ln > cap - 0.4
def end_u(a, b, nn):
    t = (nn - bn[a]) / (bn[b] - bn[a]); return bu[a] + t * (bu[b] - bu[a])
gl = lu[sel].min() - end_u(BLi, TLi, cap); gr = end_u(BRi, TRi, cap) - lu[sel].max()
bot = ln.min(); sb = ln < bot + 0.4
glb = lu[sb].min() - end_u(BLi, TLi, bot); grb = end_u(BRi, TRi, bot) - lu[sb].max()
print("baseline gaps %.2f / %.2f" % (glb, grb))
print("top margin %.2f | bottom margin %.2f | gap at top-left corner %.2f | top-right %.2f" % (bn[top].mean() - cap, ln.min() - bn[~top].mean(), gl, gr))
