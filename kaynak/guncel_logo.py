# The current logo version, in one place. Everything that draws the logo (wallpapers, animations, orbit scenes)
# reads its files from here, so a new logo version only needs VER changed and the sets rendered again.
VER = "v11.1"
ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/"
AILE = ROOT + VER + " surum ailesi/"


def pdf(folder, variant):
    """e.g. pdf("Amblem", "Koyu zemin") -> the RGB PDF of that family member"""
    return f"{AILE}{folder}/{variant}/ALFA 8084 - {folder} {VER} - {variant}.pdf"


def render(path, width):
    """Logo as an RGBA image whose artwork is `width` px wide. The emblem is padded with transparent pixels so that
    the image centre is the shield axis (the centre of its square artboard), not the centre of its bounding box:
    wherever it is placed by its centre, the shield sits symmetrically."""
    import pymupdf
    from PIL import Image
    page = pymupdf.open(path)[0]
    z = width * 1.35 / page.rect.width
    p = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True)
    im = Image.frombytes("RGBa", (p.width, p.height), p.samples).convert("RGBA")
    l, t, r, b = im.getchannel("A").getbbox()
    f = width / (r - l)
    out = im.crop((l, t, r, b)).resize((width, round((b - t) * f)), Image.LANCZOS)
    if "/Amblem/" in path:
        left, right = round((p.width / 2 - l) * f), round((r - p.width / 2) * f)
        half = max(left, right)
        c = Image.new("RGBA", (2 * half, out.height), (0, 0, 0, 0))
        c.alpha_composite(out, (half - left, 0))
        out = c
    return out
