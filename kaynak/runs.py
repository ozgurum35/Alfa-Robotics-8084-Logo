"""Colour runs along a vertical line: runs.py file.pdf x y0 y1 [offx offy]"""
import sys, pymupdf, numpy as np
f, x, y0, y1 = sys.argv[1], *map(float, sys.argv[2:5]); ox, oy = (map(float, sys.argv[5:7]) if len(sys.argv) > 6 else (0, 0))
z = 20; pm = pymupdf.open(f)[0].get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x + ox, y0 + oy, x + ox + 0.1, y1 + oy), alpha=False)
col = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, 3)[:, 0]
nm = lambda c: "navy" if c[2] < 140 else ("white" if c.min() > 245 else ("ice" if c[0] > 180 else "sky"))
cur, st = None, 0
for i, c in enumerate(col):
    k = nm(c)
    if k != cur:
        if cur: print("%-5s %7.2f .. %7.2f  (%.2f)" % (cur, y0 + st / z, y0 + i / z, (i - st) / z))
        cur, st = k, i
print("%-5s %7.2f .. %7.2f  (%.2f)" % (cur, y0 + st / z, y0 + len(col) / z, (len(col) - st) / z))
