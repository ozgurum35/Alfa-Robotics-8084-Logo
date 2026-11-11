"""Render a region of a check PDF with a labelled design-coordinate grid.
usage: gridview.py pdf offx offy x0 y0 x1 y1 zoom out.png"""
import sys, pymupdf
pdf, ox, oy, x0, y0, x1, y1, z, out = sys.argv[1], *map(float, sys.argv[2:9]), sys.argv[9]
doc = pymupdf.open(pdf); pg = doc[0]
x = x0 - x0 % 10
while x <= x1:
    big = x % 50 == 0
    pg.draw_line((x + ox, y0 + oy), (x + ox, y1 + oy), color=(1, 0, 0), width=0.25 if big else 0.08)
    if x % 20 == 0: pg.insert_text((x + ox + 0.5, y0 + oy + 4), "%d" % x, fontsize=3.5, color=(1, 0, 0))
    x += 10
y = y0 - y0 % 10
while y <= y1:
    big = y % 50 == 0
    pg.draw_line((x0 + ox, y + oy), (x1 + ox, y + oy), color=(1, 0, 0), width=0.25 if big else 0.08)
    if y % 20 == 0: pg.insert_text((x0 + ox + 0.5, y + oy - 0.5), "%d" % y, fontsize=3.5, color=(1, 0, 0))
    y += 10
pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0 + ox, y0 + oy, x1 + ox, y1 + oy)).save(out)
