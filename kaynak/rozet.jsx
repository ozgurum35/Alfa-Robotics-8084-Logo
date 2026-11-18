// Badge print sheet: A4 portrait, 6 badges (2 x 3). Cut circle 70 mm, emblem 52 mm (outer edge of the artwork,
// measured on the emblem's frame circle; on navy the 8 pt white sticker edge is included in the 52 mm).
// Two sheets: white background (colour emblem) and ALFA navy background (dark-background emblem, 2 mm bleed past the cut).
// Saves .ai, RGB .pdf, .svg, CMYK print PDF and CMYK .eps. PNGs are rendered from the PDF afterwards (rozet_png.py).
var VER = "v11.1";                 // logo version (keep equal to kaynak/guncel_logo.py VER)
var SRC = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/" + VER + " surum ailesi/Amblem/";
var OUT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/Rozet " + VER + "/";
var MM = 72 / 25.4;
var CUT = 70 * MM, LOGO = 52 * MM, BLEED = 2 * MM;
// cut circles spread evenly: in each direction the gaps between circles equal the page margins
// (horizontal (210 - 2*70) / 3 = 23.33 mm, vertical (297 - 3*70) / 4 = 21.75 mm)
var COLS = 2, ROWS = 3, GX = (210 * MM - COLS * CUT) / (COLS + 1), GY = (297 * MM - ROWS * CUT) / (ROWS + 1);
var CY_FROM_TOP = 209.7129;        // frame circle centre in the 440 pt emblem artboard (kaynak/emblem.json "circle")
// enclosing radius of the artwork about the frame circle centre, pt (measured on the 4096 px renders)
var REACH = { "Renkli": 196.652, "Koyu zemin": 204.693 };
var CMYK = { "ALFA Lacivert": [100, 82, 36, 23], "ALFA Açık Mavi": [58, 4, 1, 0], "ALFA Buz": [22, 2, 12, 0] };
var log = [];

function sw(d, name) { for (var i = 0; i < d.swatches.length; i++) if (d.swatches[i].name == name) return d.swatches[i].color; return null; }
function rgb(r, g, b) { var c = new RGBColor(); c.red = r; c.green = g; c.blue = b; return c; }

function sheet(variant, dark) {
    var src = app.open(new File(SRC + variant + "/ALFA 8084 - Amblem " + VER + " - " + variant + ".ai"));
    var ab = src.artboards[0].artboardRect, cx = (ab[0] + ab[2]) / 2, cy = ab[1] - CY_FROM_TOP;
    var items = [];
    for (var k = 0; k < src.layers.length; k++) { var L = src.layers[k]; L.locked = false; L.visible = true; for (var i = 0; i < L.pageItems.length; i++) items.push(L.pageItems[i]); }
    var tmp = src.layers[0].groupItems.add();
    for (var i = items.length - 1; i >= 0; i--) items[i].move(tmp, ElementPlacement.PLACEATBEGINNING);
    var dx = tmp.left - cx, dy = tmp.top - cy, s = (LOGO / 2) / REACH[variant];

    var d = app.documents.add(DocumentColorSpace.RGB, 210 * MM, 297 * MM);
    var r = d.artboards[0].artboardRect;
    var zemin = d.layers[0]; zemin.name = "Zemin";
    var logoL = d.layers.add(); logoL.name = "Logo";
    var kesim = d.layers.add(); kesim.name = "Kesim çizgisi 70 mm";
    var proto = tmp.duplicate(logoL, ElementPlacement.PLACEATEND);
    src.close(SaveOptions.DONOTSAVECHANGES);
    proto.resize(s * 100, s * 100, true, true, true, true, s * 100, Transformation.TOPLEFT);
    var bg = dark ? sw(d, "ALFA Lacivert") : rgb(255, 255, 255);
    var grey = rgb(150, 150, 150);
    for (var row = 0; row < ROWS; row++) for (var col = 0; col < COLS; col++) {
        var x = r[0] + GX + CUT / 2 + col * (GX + CUT), y = r[1] - (GY + CUT / 2 + row * (GY + CUT));
        var rb = dark ? CUT / 2 + BLEED : CUT / 2;
        var disc = zemin.pathItems.ellipse(y + rb, x - rb, 2 * rb, 2 * rb);
        disc.name = dark ? "Lacivert zemin (2 mm taşma)" : "Beyaz zemin"; disc.filled = true; disc.fillColor = bg; disc.stroked = false;
        var g = proto.duplicate(logoL, ElementPlacement.PLACEATEND);
        g.left = x + dx * s; g.top = y + dy * s; g.name = "Amblem 50 mm";
        var ring = kesim.pathItems.ellipse(y + CUT / 2, x - CUT / 2, CUT, CUT);
        ring.name = "Kesim 70 mm"; ring.filled = false; ring.stroked = true; ring.strokeWidth = 0.25; ring.strokeColor = grey;
    }
    proto.remove();
    kesim.locked = true;

    var name = dark ? "Lacivert zemin" : "Beyaz zemin";
    var base = OUT + "ALFA 8084 - Rozet A4 70 mm " + VER + " - " + name;
    new Folder(OUT).create();
    var ai = new IllustratorSaveOptions(); ai.pdfCompatible = true; ai.compatibility = Compatibility.ILLUSTRATOR24;
    d.saveAs(new File(base + ".ai"), ai);
    var o = new PDFSaveOptions(); o.compatibility = PDFCompatibility.ACROBAT7; o.preserveEditability = false; o.generateThumbnails = true; o.viewAfterSaving = false;
    var sv = new ExportOptionsSVG();
    sv.fontType = SVGFontType.OUTLINEFONT; sv.coordinatePrecision = 3;
    sv.cssProperties = SVGCSSPropertyLocation.PRESENTATIONATTRIBUTES; sv.documentEncoding = SVGDocumentEncoding.UTF8;
    d.exportFile(new File(base + ".svg"), ExportType.SVG, sv);
    d.saveAs(new File(base + ".pdf"), o);
    app.executeMenuCommand("doc-color-cmyk");
    for (var k = 0; k < d.spots.length; k++) {
        var v = CMYK[d.spots[k].name]; if (!v) continue;
        var c = new CMYKColor(); c.cyan = v[0]; c.magenta = v[1]; c.yellow = v[2]; c.black = v[3];
        d.spots[k].color = c;
    }
    kesim.locked = false;   // cut line: plain K 40 instead of a converted four-colour grey
    var k40 = new CMYKColor(); k40.cyan = k40.magenta = k40.yellow = 0; k40.black = 40;
    for (var i = 0; i < kesim.pathItems.length; i++) kesim.pathItems[i].strokeColor = k40;
    kesim.locked = true;
    d.saveAs(new File(base + " - Baski CMYK.pdf"), o);
    var e = new EPSSaveOptions(); e.cmykPostScript = true; e.embedAllFonts = false; e.preview = EPSPreview.TRANSPARENTCOLORTIFF;
    d.saveAs(new File(base + " - Baski CMYK.eps"), e);
    d.close(SaveOptions.DONOTSAVECHANGES);
    log.push(name + ": scale " + (s * 100).toFixed(3) + "%");
}

app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
try { sheet("Renkli", false); sheet("Koyu zemin", true); } catch (err) { log.push("HATA: " + err + " line " + err.line); }
log.join("\n");
