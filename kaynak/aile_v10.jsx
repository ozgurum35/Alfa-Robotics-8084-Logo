// v10 logo family: colour (white ROBOTICS), dark-background (white sticker edge), one-colour navy / white.
// Each variant also gets a CMYK print PDF (Coated FOGRA39 values, see CMYK below).
// Opens the v10 .ai files (unchanged), builds each variant with Pathfinder, saves .ai + PDF + SVG.
// Artboard = artwork bounds + equal margin (10% of the longer side). PNGs are rendered from the PDFs afterwards (aile_png.py).
var SRC = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/";
var VER = "v11.1";         // logo version: source .ai names, output folder and file names
var OUT = SRC + VER + " surum ailesi/";
var STICKER = 8;          // white edge for the dark-background version, pt
var MARGIN_RATIO = 0.10;
// sRGB -> Coated FOGRA39, relative colorimetric (kaynak/renk.py); Pantone matches are in the guide
var CMYK = { "ALFA Lacivert": [100, 82, 36, 23], "ALFA Açık Mavi": [58, 4, 1, 0], "ALFA Buz": [22, 2, 12, 0] };
var ONLY = (typeof ONLY_VARIANT != "undefined") ? ONLY_VARIANT : null;
var log = [];
var GUIDE = null;

function sw(d, name) { for (var i = 0; i < d.swatches.length; i++) if (d.swatches[i].name == name) return d.swatches[i].color; return null; }
function white() { var c = new RGBColor(); c.red = c.green = c.blue = 255; return c; }
function openAi(name) {
    var d = app.open(new File(SRC + name + ".ai"));
    for (var k = d.layers.length - 1; k >= 0; k--) {
        var L = d.layers[k]; L.locked = false; L.visible = true;
        if (L.name.indexOf("K\u0131lavuz") === 0 || L.name.indexOf("Kilavuz") === 0) {
            // frame circle of the emblem (centre + radius RF), read before the guide layer is dropped
            if (L.pathItems.length) { var gb = L.pathItems[0].geometricBounds; GUIDE = { cx: (gb[0] + gb[2]) / 2, cy: (gb[1] + gb[3]) / 2, r: (gb[2] - gb[0]) / 2 }; }
            L.remove();
        }
    }
    return d;
}
function find(d, name) { // first page item with this name (any depth)
    for (var i = 0; i < d.pageItems.length; i++) if (d.pageItems[i].name == name) return d.pageItems[i];
    return null;
}
function allArt(d) { var a = []; for (var k = 0; k < d.layers.length; k++) for (var i = 0; i < d.layers[k].pageItems.length; i++) a.push(d.layers[k].pageItems[i]); return a; }
function runOn(d, items, cmds) {
    d.selection = null;
    for (var i = 0; i < items.length; i++) items[i].selected = true;
    // Live Pathfinder works on a group; on loose items it is applied to each item separately
    if (cmds[0].indexOf("Live Pathfinder") === 0) app.executeMenuCommand("group");
    for (var c = 0; c < cmds.length; c++) app.executeMenuCommand(cmds[c]);
    return d.selection[0];
}
function area(p) { var b = p.geometricBounds; return (b[2] - b[0]) * (b[1] - b[3]); }
function inside(a, b) { var x = a.geometricBounds, y = b.geometricBounds; return x[0] >= y[0] - 0.01 && x[1] <= y[1] + 0.01 && x[2] <= y[2] + 0.01 && x[3] >= y[3] - 0.01 && area(a) < area(b); }
// turn any group / compound result into one compound path with only the outer contours (holes removed)
function solid(d, item, layer) {
    var paths = [];
    function collect(it) {
        if (it.typename == "PathItem") paths.push(it);
        else if (it.typename == "CompoundPathItem") for (var i = 0; i < it.pathItems.length; i++) paths.push(it.pathItems[i]);
        else if (it.typename == "GroupItem") for (var j = 0; j < it.pageItems.length; j++) collect(it.pageItems[j]);
    }
    collect(item);
    var cp = layer.compoundPathItems.add();
    for (var i = 0; i < paths.length; i++) {
        var hole = false;
        for (var j = 0; j < paths.length && !hole; j++) if (i != j && inside(paths[i], paths[j])) hole = true;
        if (!hole) paths[i].duplicate(cp, ElementPlacement.PLACEATEND);
    }
    item.remove();
    return cp;
}
function fill(item, color) {
    if (item.typename == "CompoundPathItem") { for (var i = 0; i < item.pathItems.length; i++) fill(item.pathItems[i], color); return; }
    if (item.typename == "GroupItem") { for (var j = 0; j < item.pageItems.length; j++) fill(item.pageItems[j], color); return; }
    item.filled = true; item.stroked = false; item.fillColor = color;
}
function backLayer(d, name) { var L = d.layers.add(); L.name = name; L.zOrder(ZOrderMethod.SENDTOBACK); return L; }
function dupAll(d, layer) { var a = allArt(d), out = []; for (var i = 0; i < a.length; i++) out.push(a[i].duplicate(layer, ElementPlacement.PLACEATEND)); return out; }

// white fill under the ROBOTICS letters: outer contour of the band, behind the band
function whiteRobotics(d) {
    var band = find(d, "Bant + ROBOTICS"); if (!band) return;
    var outer = null;
    for (var i = 0; i < band.pathItems.length; i++) if (!outer || area(band.pathItems[i]) > area(outer)) outer = band.pathItems[i];
    var b = outer.duplicate(band.parent, ElementPlacement.PLACEATEND); // behind everything in the group
    b.name = "ROBOTICS beyaz dolgu"; b.filled = true; b.stroked = false; b.fillColor = white();
    b.move(band, ElementPlacement.PLACEAFTER);
}
// one-colour: navy minus (sky + ice), plus letters; returns the compound shape on a new layer
function oneColour(d, color, name) {
    var navy = [], cut = [], a = d.pageItems, i;
    var navyColor = sw(d, "ALFA Lacivert");
    var L = d.layers.add(); L.name = name;
    for (i = 0; i < a.length; i++) {
        var it = a[i]; if (it.typename == "GroupItem" || it.parent.typename == "CompoundPathItem") continue;
        var f = (it.typename == "CompoundPathItem") ? it.pathItems[0].fillColor : it.fillColor;
        var isNavy = f && f.typename == "SpotColor" && f.spot.name == "ALFA Lacivert";
        (isNavy ? navy : cut).push(it);
    }
    var N = [], C = [];
    for (i = 0; i < navy.length; i++) N.push(navy[i].duplicate(L, ElementPlacement.PLACEATEND));
    for (i = 0; i < cut.length; i++) C.push(cut[i].duplicate(L, ElementPlacement.PLACEATEND));
    var res;
    if (C.length) {
        // letters (ALFA, band) sit on top of everything: keep them out of the subtraction, add afterwards
        var base = [], top = [];
        for (i = 0; i < N.length; i++) (/^(A sol|L|F|A sa\u011f|Bant \+ ROBOTICS)$/.test(N[i].name) ? top : base).push(N[i]);
        // Minus Front cuts only the backmost object: make the navy base one compound path first
        var nb = runOn(d, base, ["Live Pathfinder Add", "expandStyle", "ungroup", "compoundPath"]);
        var cu = runOn(d, C, ["Live Pathfinder Add", "expandStyle"]);
        cu.zOrder(ZOrderMethod.BRINGTOFRONT);
        var sub = runOn(d, [nb, cu], ["Live Pathfinder Subtract", "expandStyle"]);
        top.push(sub);
        res = runOn(d, top, ["Live Pathfinder Add", "expandStyle"]);
    } else {
        res = runOn(d, N, ["Live Pathfinder Add", "expandStyle"]);
    }
    fill(res, color); res.name = name;
    // drop every other layer
    for (var k = d.layers.length - 1; k >= 0; k--) if (d.layers[k] != L) d.layers[k].remove();
    return res;
}
function sticker(d, layerName) {
    var L = backLayer(d, layerName);
    var u = runOn(d, dupAll(d, L).slice(0), ["Live Pathfinder Add", "expandStyle"]);
    u = solid(d, u, L);
    u.applyEffect('<LiveEffect name="Adobe Offset Path"><Dict data="R mlim 4 R ofst ' + STICKER + ' I jntp 0 "/></LiveEffect>');
    var o = runOn(d, [u], ["expandStyle"]);
    o = runOn(d, [o], ["Live Pathfinder Add", "expandStyle"]);
    o = solid(d, o, L); fill(o, white()); o.name = "Beyaz kenar " + STICKER + " pt";
    return o;
}
// keep = leave the source artboard as it is (v11 emblem: square frame centred on the shield axis and midway
// between nose top and shield tip); otherwise artboard = artwork bounds + margin
// emblem on a filled square or circle (profile pictures, stickers, badges):
// square = the emblem's own artboard (shield corners / nose top and shield tip equally far from the edges);
// circle = the profile circle (frame circle / 0.92: nose top and shield tip vertically, both A tips horizontally equally far)
function backdrop(d, shape, color) {
    var L = backLayer(d, shape == "Daire" ? "Daire zemin" : "Kare zemin"), it, ab = d.artboards[0].artboardRect;
    if (shape == "Daire") {
        var r = GUIDE.r / 0.92;
        it = L.pathItems.ellipse(GUIDE.cy + r, GUIDE.cx - r, 2 * r, 2 * r);
        d.artboards[0].artboardRect = [GUIDE.cx - r, GUIDE.cy + r, GUIDE.cx + r, GUIDE.cy - r];
    } else it = L.pathItems.rectangle(ab[1], ab[0], ab[2] - ab[0], ab[1] - ab[3]);
    it.name = L.name; it.filled = true; it.stroked = false; it.fillColor = color;
}
// wordmark / horizontal logo on a filled square or circle: centred on the artwork bounds;
// square side = longer side + 10% margin each side, circle = circle through the bounds' corners / 0.92
function navy(d) { var c = sw(d, "ALFA Lacivert"); if (!c) { c = new RGBColor(); c.red = 0; c.green = 58; c.blue = 111; } return c; }
function backdropFit(d, shape, color) {
    d.selection = null;
    var b = d.visibleBounds, w = b[2] - b[0], h = b[1] - b[3], cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2, it;
    var L = backLayer(d, shape == "Daire" ? "Daire zemin" : "Kare zemin");
    var r = (shape == "Daire") ? Math.sqrt(w * w + h * h) / 2 / 0.92 : Math.max(w, h) * (1 + 2 * MARGIN_RATIO) / 2;
    if (shape == "Daire") it = L.pathItems.ellipse(cy + r, cx - r, 2 * r, 2 * r);
    else it = L.pathItems.rectangle(cy + r, cx - r, 2 * r, 2 * r);
    it.name = L.name; it.filled = true; it.stroked = false; it.fillColor = color;
    d.artboards[0].artboardRect = [cx - r, cy + r, cx + r, cy - r];
}
function fitAndSave(d, base, keep) {
    d.selection = null;
    var b = d.visibleBounds, w = b[2] - b[0], h = b[1] - b[3], m = (typeof MARGIN_SHORT != "undefined" ? Math.min(w, h) : Math.max(w, h)) * MARGIN_RATIO;
    if (!keep) d.artboards[0].artboardRect = [b[0] - m, b[1] + m, b[2] + m, b[3] - m];
    new Folder(base.substring(0, base.lastIndexOf("/"))).create();
    var ai = new IllustratorSaveOptions(); ai.pdfCompatible = true; ai.compatibility = Compatibility.ILLUSTRATOR24;
    d.saveAs(new File(base + ".ai"), ai);
    var s = new ExportOptionsSVG();
    s.embedRasterImages = true; s.fontType = SVGFontType.OUTLINEFONT; s.coordinatePrecision = 3;
    s.cssProperties = SVGCSSPropertyLocation.PRESENTATIONATTRIBUTES; s.documentEncoding = SVGDocumentEncoding.UTF8;
    d.exportFile(new File(base + ".svg"), ExportType.SVG, s);
    var o = new PDFSaveOptions(); o.compatibility = PDFCompatibility.ACROBAT7; o.preserveEditability = false; o.generateThumbnails = true; o.viewAfterSaving = false;
    d.saveAs(new File(base + ".pdf"), o);
    // print PDF: document to CMYK, brand swatches set to their CMYK values (white becomes 0/0/0/0)
    app.executeMenuCommand("doc-color-cmyk");
    for (var k = 0; k < d.spots.length; k++) {
        var v = CMYK[d.spots[k].name]; if (!v) continue;
        var c = new CMYKColor(); c.cyan = v[0]; c.magenta = v[1]; c.yellow = v[2]; c.black = v[3];
        d.spots[k].color = c;
    }
    d.saveAs(new File(base + " - Baski CMYK.pdf"), o);
    d.close(SaveOptions.DONOTSAVECHANGES);
    log.push(base.substring(OUT.length) + "  " + w.toFixed(1) + " x " + h.toFixed(1) + " pt");
}

var EM = "ALFA 8084 - Amblem " + VER, WM = "ALFA 8084 - Yazi Logo " + VER;
var jobs = [
    ["Amblem/Renkli",            EM, function (d) { whiteRobotics(d); }],
    ["Amblem/Koyu zemin",        EM, function (d) { whiteRobotics(d); sticker(d, "Beyaz kenar"); }],
    ["Amblem/Tek renk lacivert", EM, function (d) { oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); }],
    ["Amblem/Tek renk beyaz",    EM, function (d) { oneColour(d, white(), "Tek renk"); }],
    ["Amblem Kare/Renkli",            EM, function (d) { whiteRobotics(d); backdrop(d, "Kare", white()); }],
    ["Amblem Kare/Koyu zemin",        EM, function (d) { whiteRobotics(d); sticker(d, "Beyaz kenar"); backdrop(d, "Kare", sw(d, "ALFA Lacivert")); }],
    ["Amblem Kare/Tek renk lacivert", EM, function (d) { var c = sw(d, "ALFA Lacivert"); oneColour(d, c, "Tek renk"); backdrop(d, "Kare", white()); }],
    ["Amblem Kare/Tek renk beyaz",    EM, function (d) { var c = sw(d, "ALFA Lacivert"); oneColour(d, white(), "Tek renk"); backdrop(d, "Kare", c); }],
    ["Amblem Daire/Renkli",            EM, function (d) { whiteRobotics(d); backdrop(d, "Daire", white()); }],
    ["Amblem Daire/Koyu zemin",        EM, function (d) { whiteRobotics(d); sticker(d, "Beyaz kenar"); backdrop(d, "Daire", sw(d, "ALFA Lacivert")); }],
    ["Amblem Daire/Tek renk lacivert", EM, function (d) { var c = sw(d, "ALFA Lacivert"); oneColour(d, c, "Tek renk"); backdrop(d, "Daire", white()); }],
    ["Amblem Daire/Tek renk beyaz",    EM, function (d) { var c = sw(d, "ALFA Lacivert"); oneColour(d, white(), "Tek renk"); backdrop(d, "Daire", c); }],
    ["Yazi Logo/Renkli",            WM, function (d) { whiteRobotics(d); }],
    ["Yazi Logo/Tek renk lacivert", WM, function (d) { oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); }],
    ["Yazi Logo/Tek renk beyaz",    WM, function (d) { oneColour(d, white(), "Tek renk"); }],
    ["Yazi Logo Kare/Renkli",             WM, function (d) { whiteRobotics(d); backdropFit(d, "Kare", white()); }],
    ["Yazi Logo Kare/Tek renk lacivert",  WM, function (d) { oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); backdropFit(d, "Kare", white()); }],
    ["Yazi Logo Kare/Tek renk beyaz",     WM, function (d) { var c = navy(d); oneColour(d, white(), "Tek renk"); backdropFit(d, "Kare", c); }],
    ["Yazi Logo Daire/Renkli",            WM, function (d) { whiteRobotics(d); backdropFit(d, "Daire", white()); }],
    ["Yazi Logo Daire/Tek renk lacivert", WM, function (d) { oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); backdropFit(d, "Daire", white()); }],
    ["Yazi Logo Daire/Tek renk beyaz",    WM, function (d) { var c = navy(d); oneColour(d, white(), "Tek renk"); backdropFit(d, "Daire", c); }]
];
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
for (var j = 0; j < jobs.length; j++) {
    if (ONLY && jobs[j][0] != ONLY) continue;
    if (typeof ONLY_PREFIX != "undefined" && ONLY_PREFIX && jobs[j][0].indexOf(ONLY_PREFIX) !== 0) continue;
    var parts = jobs[j][0].split("/");
    var d = openAi(jobs[j][1]);
    try { jobs[j][2](d); }
    catch (e) { log.push(jobs[j][0] + " HATA: " + e + " line " + e.line); d.close(SaveOptions.DONOTSAVECHANGES); continue; }
    var label = parts[0];
    fitAndSave(d, OUT + parts[0] + "/" + parts[1] + "/ALFA 8084 - " + label + " " + VER + " - " + parts[1], parts[0].indexOf("Amblem") === 0 || / (Kare|Daire)$/.test(parts[0]));
}
log.join("\n");
