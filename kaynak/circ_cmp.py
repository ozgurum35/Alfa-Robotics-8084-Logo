"""Side-by-side: A = circle on the shield axis (touches 4 points), B = circle centred on the logo's bounding box."""
import json, pymupdf, numpy as np
art = json.load(open("emblem.json")); cx, cy, R = art["circle"]; S = art["width"]
P = []
for g in art["groups"]:
    for it in g["items"]:
        for s in it["subs"]:
            n = len(s)
            for k in range(n):
                a, b = s[k], s[(k + 1) % n]
                for t in np.linspace(0, 1, 20, endpoint=False):
                    P.append([(1 - t) ** 3 * a["p"][i] + 3 * (1 - t) ** 2 * t * a["o"][i] + 3 * (1 - t) * t * t * b["i"][i] + t ** 3 * b["p"][i] for i in (0, 1)])
P = np.array(P)
x0, x1, y0, y1 = P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()
bx, by = (x0 + x1) / 2, (y0 + y1) / 2
RB = float(np.hypot(P[:, 0] - bx, P[:, 1] - by).max())
src = pymupdf.open("D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/ALFA 8084 - Amblem v8.ai")
M, W = 40, 2 * RB + 80
doc = pymupdf.open(); pg = doc.new_page(width=2 * W, height=W + 50)
PINK, GREY = (0.9, 0, 0.47), (0.35, 0.35, 0.35)
for j, (title, ccx, ccy, rr) in enumerate((("A  (simdiki): daire kalkan ekseninde, logo 4 noktada degiyor", cx, cy, R),
                                           ("B: daire logonun tam ortasinda, sag-sol ve ust-alt bosluk esit", bx, by, RB))):
    ox, oy = j * W + W / 2 - ccx, 50 + W / 2 - ccy
    pg.show_pdf_page(pymupdf.Rect(ox, oy, ox + S, oy + S), src, 0)
    c = (ccx + ox, ccy + oy)
    pg.draw_circle(c, rr, color=PINK, width=1.2)
    pg.draw_line((c[0] - 6, c[1]), (c[0] + 6, c[1]), color=PINK, width=0.8); pg.draw_line((c[0], c[1] - 6), (c[0], c[1] + 6), color=PINK, width=0.8)
    pg.insert_text((j * W + 20, 30), title, fontsize=13, color=(0, 0, 0))
    gaps = {"sol": (x0 - (ccx - rr)), "sag": ((ccx + rr) - x1), "ust": (y0 - (ccy - rr)), "alt": ((ccy + rr) - y1)}
    # gap bars along the horizontal / vertical through the circle centre
    for nm, (pa, pb) in {"sol": ((c[0] - rr, c[1]), (x0 + ox, c[1])), "sag": ((x1 + ox, c[1]), (c[0] + rr, c[1])),
                         "ust": ((c[0], c[1] - rr), (c[0], y0 + oy)), "alt": ((c[0], y1 + oy), (c[0], c[1] + rr))}.items():
        if gaps[nm] > 0.5:
            pg.draw_line(pa, pb, color=(0.85, 0.1, 0.1), width=2.2)
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        dx, dy = {"sol": (-4, -6), "sag": (-22, -6), "ust": (6, 4), "alt": (6, -2)}[nm]
        pg.insert_text((mx + dx, my + dy), "%s %.0f" % (nm, gaps[nm]), fontsize=11, color=(0.75, 0, 0))
    print(title[:1], "R %.1f" % rr, {k: round(v, 1) for k, v in gaps.items()})
    # dashed bounding box of the logo
    pg.draw_rect(pymupdf.Rect(x0 + ox, y0 + oy, x1 + ox, y1 + oy), color=GREY, width=0.5, dashes="[3 3]")
pg.get_pixmap(matrix=pymupdf.Matrix(2, 2)).save("D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/ALFA 8084 - Daire secenekleri A-B.png")
print("bbox centre shift from axis circle: dx %.1f dy %.1f" % (bx - cx, by - cy))
