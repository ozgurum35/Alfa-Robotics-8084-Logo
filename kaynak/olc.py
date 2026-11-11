"""Concentricity report for v10: prints inner/outer radii and the distance between their centres."""
import math, sys
src_ = open("design5.py", encoding="utf-8").read().split("# ------------------------------------------------------------------ enclosing circle")[0]
sys.argv = ["x", ".", ""]
exec(src_)
def rpt(nm, outer, inner, w):
    dc = math.hypot(*(outer["c"] - inner["c"]))
    print("%-28s dis r %7.2f | ic r %7.2f | fark %5.2f (kontur %s) | merkez kaymasi %.3f" % (nm, outer["r"], inner["r"], abs(outer["r"] - inner["r"]), w, dc))
for k, nm in ((1, "kalkan sag ust kose"), (5, "kalkan sol ust kose"), (3, "kalkan alt uc"), (0, "ust yay"), (2, "sag yan"), (4, "sol yan")):
    rpt(nm, sh0[k], shI[k], WF)
arcs = lambda ch, r: [q for q in ch if q["t"] == "A" and abs(q["r"] - r) < 1e-6]
rpt("burun", arcs(nav, RN + WO)[0], arcs(ice_r, RN)[0], WO)
rpt("alin-burun birlesimi (ic bukey)", arcs(ice_r, WO + RX)[0], arcs(nav, RX)[0], WO)
rpt("bogaz yayi 1", off_out(a9, WJU), a9, WJU)
rpt("bogaz yayi 2", off_out(a10, WJU), a10, WJU)
rpt("centik alti / yele ustu", topF, notchA, WM)
rpt("yele sol kenar / cerceve ic", shI[4], shY, GP)
print("cene on ust ucu: dis r %.1f, kontur %.1f/%.1f -> ic kose sivri" % (RJT, WJT, WJF))
print("cene alt kosesi: dis r %.1f, kontur %.1f/%.1f -> ic kose sivri" % (RJB, WJF, WJU))
