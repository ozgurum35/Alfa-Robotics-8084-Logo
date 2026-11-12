// v10 logo family: colour (white ROBOTICS), dark-background (white sticker edge), one-colour navy / white, icon.
// Opens the v10 .ai files (unchanged), builds each variant with Pathfinder, saves .ai + PDF + SVG.
// Artboard = artwork bounds + equal margin (10% of the longer side). PNGs are rendered from the PDFs afterwards (aile_png.py).
var SRC = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/";
var OUT = SRC + "v10 surum ailesi/";
var STICKER = 8;          // white edge for the dark-background version, pt
var MARGIN_RATIO = 0.10;
var ONLY = (typeof ONLY_VARIANT != "undefined") ? ONLY_VARIANT : null;
var log = [];

function sw(d, name) { for (var i = 0; i < d.swatches.length; i++) if (d.swatches[i].name == name) return d.swatches[i].color; return null; }
function white() { var c = new RGBColor(); c.red = c.green = c.blue = 255; return c; }
function openAi(name) {
    var d = app.open(new File(SRC + name + ".ai"));
    for (var k = d.layers.length - 1; k >= 0; k--) {
        var L = d.layers[k]; L.locked = false; L.visible = true;
        if (L.name.indexOf("K\u0131lavuz") === 0 || L.name.indexOf("Kilavuz") === 0) L.remove();
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
function icon(d) { // shield top + wolf only
    var keep = { "Kalkan \u00fcst": 1, "Kurt": 1 };
    var a = d.layers;
    for (var k = 0; k < a.length; k++) for (var i = a[k].groupItems.length - 1; i >= 0; i--) if (!keep[a[k].groupItems[i].name]) a[k].groupItems[i].remove();
    for (var m = d.layers.length - 1; m >= 0; m--) if (d.layers[m].pageItems.length == 0) d.layers[m].remove();
}
function fitAndSave(d, base) {
    d.selection = null;
    var b = d.visibleBounds, w = b[2] - b[0], h = b[1] - b[3], m = Math.max(w, h) * MARGIN_RATIO;
    d.artboards[0].artboardRect = [b[0] - m, b[1] + m, b[2] + m, b[3] - m];
    new Folder(base.substring(0, base.lastIndexOf("/"))).create();
    var ai = new IllustratorSaveOptions(); ai.pdfCompatible = true; ai.compatibility = Compatibility.ILLUSTRATOR24;
    d.saveAs(new File(base + ".ai"), ai);
    var s = new ExportOptionsSVG();
    s.embedRasterImages = true; s.fontType = SVGFontType.OUTLINEFONT; s.coordinatePrecision = 3;
    s.cssProperties = SVGCSSPropertyLocation.PRESENTATIONATTRIBUTES; s.documentEncoding = SVGDocumentEncoding.UTF8;
    d.exportFile(new File(base + ".svg"), ExportType.SVG, s);
    var o = new PDFSaveOptions(); o.compatibility = PDFCompatibility.ACROBAT7; o.preserveEditability = false; o.generateThumbnails = true; o.viewAfterSaving = false;
    d.saveAs(new File(base + ".pdf"), o);
    d.close(SaveOptions.DONOTSAVECHANGES);
    log.push(base.substring(OUT.length) + "  " + w.toFixed(1) + " x " + h.toFixed(1) + " pt");
}

var EM = "ALFA 8084 - Amblem v10", WM = "ALFA 8084 - Yazi Logo v10";
var jobs = [
    ["Amblem/Renkli",            EM, function (d) { whiteRobotics(d); }],
    ["Amblem/Koyu zemin",        EM, function (d) { whiteRobotics(d); sticker(d, "Beyaz kenar"); }],
    ["Amblem/Tek renk lacivert", EM, function (d) { oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); }],
    ["Amblem/Tek renk beyaz",    EM, function (d) { oneColour(d, white(), "Tek renk"); }],
    ["Yazi Logo/Renkli",            WM, function (d) { whiteRobotics(d); }],
    ["Yazi Logo/Tek renk lacivert", WM, function (d) { oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); }],
    ["Yazi Logo/Tek renk beyaz",    WM, function (d) { oneColour(d, white(), "Tek renk"); }],
    ["Simge/Renkli",            EM, function (d) { icon(d); }],
    ["Simge/Koyu zemin",        EM, function (d) { icon(d); sticker(d, "Beyaz kenar"); }],
    ["Simge/Tek renk lacivert", EM, function (d) { icon(d); oneColour(d, sw(d, "ALFA Lacivert"), "Tek renk"); }],
    ["Simge/Tek renk beyaz",    EM, function (d) { icon(d); oneColour(d, white(), "Tek renk"); }]
];
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
for (var j = 0; j < jobs.length; j++) {
    if (ONLY && jobs[j][0] != ONLY) continue;
    var parts = jobs[j][0].split("/");
    var d = openAi(jobs[j][1]);
    try { jobs[j][2](d); }
    catch (e) { log.push(jobs[j][0] + " HATA: " + e + " line " + e.line); d.close(SaveOptions.DONOTSAVECHANGES); continue; }
    var label = (parts[0] == "Yazi Logo" ? "Yazi Logo" : parts[0]);
    fitAndSave(d, OUT + parts[0] + "/" + parts[1] + "/ALFA 8084 - " + label + " v10 - " + parts[1]);
}
log.join("\n");
