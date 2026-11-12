// Export v10 .ai files with a white background and equal margins on all four sides.
// Artboard = artwork bounds + MARGIN on every side; a white rectangle fills the artboard.
// The .ai files stay unchanged. PNGs (512-4096 px) are rendered from the PDF with PyMuPDF afterwards:
// Illustrator's PNG export rounds the size (1023 px instead of 1024) and caps the scale at 776%.
var SRC = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/";
var OUT = SRC + "v10 disa aktarim/beyaz zemin/";
var names = ["ALFA 8084 - Amblem v10", "ALFA 8084 - Yazi Logo v10"];
var MARGIN_RATIO = 0.10; // margin = 10% of the artwork's longer side
var log = [];
new Folder(OUT).create();
function dropGuides(d) {
    for (var k = d.layers.length - 1; k >= 0; k--) {
        var L = d.layers[k];
        if (L.name.indexOf("Kilavuz") === 0 || L.name.indexOf("K\u0131lavuz") === 0 || !L.visible) {
            L.locked = false; L.visible = true; L.remove();
        }
    }
}
function white(d) {
    if (d.documentColorSpace == DocumentColorSpace.CMYK) {
        var c = new CMYKColor(); c.cyan = c.magenta = c.yellow = c.black = 0; return c;
    }
    var r = new RGBColor(); r.red = r.green = r.blue = 255; return r;
}
for (var i = 0; i < names.length; i++) {
    var d = app.open(new File(SRC + names[i] + ".ai"));
    dropGuides(d);
    for (var k = 0; k < d.layers.length; k++) d.layers[k].locked = false;
    var b = d.visibleBounds; // [left, top, right, bottom], y up
    var w = b[2] - b[0], h = b[1] - b[3];
    var m = Math.max(w, h) * MARGIN_RATIO;
    var ab = [b[0] - m, b[1] + m, b[2] + m, b[3] - m];
    d.artboards[0].artboardRect = ab;
    var bg = d.layers.add(); bg.name = "Zemin"; bg.zOrder(ZOrderMethod.SENDTOBACK);
    var r = bg.pathItems.rectangle(ab[1], ab[0], ab[2] - ab[0], ab[1] - ab[3]);
    r.stroked = false; r.filled = true; r.fillColor = white(d); r.name = "Beyaz zemin";
    var base = OUT + names[i] + " beyaz zemin";
    var s = new ExportOptionsSVG();
    s.embedRasterImages = true; s.fontType = SVGFontType.OUTLINEFONT; s.coordinatePrecision = 3;
    s.cssProperties = SVGCSSPropertyLocation.PRESENTATIONATTRIBUTES; s.documentEncoding = SVGDocumentEncoding.UTF8;
    d.exportFile(new File(base + ".svg"), ExportType.SVG, s);
    var o = new PDFSaveOptions();
    o.compatibility = PDFCompatibility.ACROBAT7; o.preserveEditability = false; o.generateThumbnails = true;
    o.viewAfterSaving = false;
    d.saveAs(new File(base + ".pdf"), o);
    d.close(SaveOptions.DONOTSAVECHANGES);
    log.push(names[i] + ": art " + w.toFixed(2) + " x " + h.toFixed(2) + " pt, margin " + m.toFixed(2) + " pt");
}
log.join("\n");
