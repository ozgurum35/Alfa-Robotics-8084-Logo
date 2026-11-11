"""Pixel-compare the original artwork area against a rebuilt file."""
import sys, json, pymupdf, numpy as np
from PIL import Image

src, new, clipf, out = sys.argv[1:5]
c = json.load(open(clipf))
Z = 6
clip = pymupdf.Rect(c["ox"], c["oy"], c["ox"] + c["W"], c["oy"] + c["H"])
a = pymupdf.open(src)[0].get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=clip)
pn = pymupdf.open(new)[0]
print("new page %.2f x %.2f | expected %.2f x %.2f" % (pn.rect.width, pn.rect.height, c["W"], c["H"]))
b = pn.get_pixmap(matrix=pymupdf.Matrix(Z, Z))
A = np.frombuffer(a.samples, np.uint8).reshape(a.h, a.w, a.n)[..., :3].astype(int)
B = np.frombuffer(b.samples, np.uint8).reshape(b.h, b.w, b.n)[..., :3].astype(int)
h, w = min(A.shape[0], B.shape[0]), min(A.shape[1], B.shape[1])
D = np.abs(A[:h, :w] - B[:h, :w]).max(axis=2)
print("sizes", A.shape, B.shape, "| pixels %d | diff>32: %d (%.4f%%) | diff>128: %d | max %d"
      % (D.size, (D > 32).sum(), 100 * (D > 32).mean(), (D > 128).sum(), D.max()))
vis = np.where(D[..., None] > 32, np.array([255, 0, 0]), (A[:h, :w] + 255) // 2).astype(np.uint8)
Image.fromarray(vis).save(out)
