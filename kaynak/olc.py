"""Concentricity report for v10: inner/outer radii, their difference vs. the outline width, centre offset.
Rule (user): inner radius = outer radius - outline; if that is not possible the inner corner gets 1 pt."""
import math, sys
src_ = open("design5.py", encoding="utf-8").read().split("# ------------------------------------------------------------------ enclosing circle")[0]
sys.argv = ["x", ".", ""]
exec(src_)
bad = []


def rpt(nm, outer, inner, w):
    dc = math.hypot(*(outer["c"] - inner["c"]))
    ok = abs(abs(outer["r"] - inner["r"]) - w) < 0.01 and dc < 0.01
    bad.extend([] if ok else [nm])
    print("%-30s dis r %7.2f | ic r %7.2f | fark %5.2f (kontur %5.2f) | merkez kaymasi %.3f | %s"
          % (nm, outer["r"], inner["r"], abs(outer["r"] - inner["r"]), w, dc, "OK" if ok else "HATA"))


for k, nm in ((1, "kalkan sag ust kose"), (5, "kalkan sol ust kose"), (3, "kalkan alt uc"), (0, "ust yay"), (2, "sag yan"), (4, "sol yan")):
    rpt(nm, sh0[k], shI[k], WF)
arcs = lambda ch, r: [q for q in ch if q["t"] == "A" and abs(q["r"] - r) < 1e-6]
rpt("burun ucu", arcs(nav, RN + WO)[0], arcs(ice_r, RN)[0], WO)
rpt("bogaz yayi 1", off_out(a9, WJU), a9, WJU)
rpt("bogaz yayi 2", off_out(a10, WJU), a10, WJU)
for k_, nm, ro, w in ((0, "cene on ust ucu", RJT, (WJT + WJF) / 2), (1, "cene alt kosesi", RJB, (WJF + WJU) / 2)):
    ri = JIN[k_]
    want = ro - w
    ok = abs(ri - want) < 0.01 if want >= 1.0 else abs(ri - 1.0) < 0.01
    bad.extend([] if ok else [nm])
    print("%-30s dis r %7.2f | ic r %7.2f | kontur %5.2f -> %s | %s"
          % (nm, ro, ri, w, "es merkez" if want >= 1.0 else "kontur kalin: 1 pt kurali", "OK" if ok else "HATA"))
print("yele 1 sol kenar = cerceve ic kenari shI[4] (ayni yay, yapi geregi)")
print("SONUC:", "tum kontroller gecti" if not bad else "HATALI: " + ", ".join(bad))
