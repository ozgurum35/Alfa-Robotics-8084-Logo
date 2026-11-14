// v10 horizontal lockup: emblem + wordmark side by side, built from the v10 family .ai files (aile_v10.jsx).
// Wordmark height = 72% of the emblem height, gap = 16%, vertically centred on the emblem.
// Margin = 10% of the lockup height (same clear space as the emblem). PNGs: aile_png.py.
var ONLY_VARIANT = "__none__";   // load aile_v10.jsx helpers without running its jobs
var MARGIN_SHORT = true;
#include "aile_v10.jsx"
var FAM = OUT, RATIO = 0.72, GAP = 0.16;
var ylog = [];
function famDoc(folder, variant) {
    var label = folder;
    return app.open(new File(FAM + folder + "/" + variant + "/ALFA 8084 - " + label + " " + VER + " - " + variant + ".ai"));
}
function boundsOf(items) {
    var r = null;
    for (var i = 0; i < items.length; i++) {
        var b = items[i].visibleBounds;
        if (!r) r = b.slice(0); else { r[0] = Math.min(r[0], b[0]); r[1] = Math.max(r[1], b[1]); r[2] = Math.max(r[2], b[2]); r[3] = Math.min(r[3], b[3]); }
    }
    return r;
}
// emblem art without the white sticker edge: identical geometry in every emblem variant
var ref = famDoc("Amblem", "Renkli");
var E = ref.visibleBounds; ref.close(SaveOptions.DONOTSAVECHANGES);
var Eh = E[1] - E[3], Ecy = (E[1] + E[3]) / 2;

var yjobs = [["Renkli", "Renkli", "Renkli"], ["Koyu zemin", "Koyu zemin", "Tek renk beyaz"],
             ["Tek renk lacivert", "Tek renk lacivert", "Tek renk lacivert"], ["Tek renk beyaz", "Tek renk beyaz", "Tek renk beyaz"]];
// each lockup three times: plain (artboard = bounds + margin), on a filled square and on a filled circle
var shapes = (typeof YATAY_SHAPES != "undefined" && YATAY_SHAPES) ? YATAY_SHAPES : [null, "Kare", "Daire"];
var darkBg = { "Koyu zemin": true, "Tek renk beyaz": true };
for (var j = 0; j < yjobs.length; j++) for (var q = 0; q < shapes.length; q++) {
    var d = famDoc("Amblem", yjobs[j][1]);
    var w = famDoc("Yazi Logo", yjobs[j][2]);
    var L = d.layers.add(); L.name = "Yazı Logo"; L.zOrder(ZOrderMethod.BRINGTOFRONT);
    var g = L.groupItems.add(); g.name = "Yazi Logo";
    var src = allArt(w);
    // cross-document duplicate works only into a layer; then move into the group (order kept)
    for (var i = 0; i < src.length; i++) src[i].duplicate(L, ElementPlacement.PLACEATEND).move(g, ElementPlacement.PLACEATEND);
    w.close(SaveOptions.DONOTSAVECHANGES);
    // scale by geometric height of the wordmark art
    var gb = g.geometricBounds, s = 100 * RATIO * Eh / (gb[1] - gb[3]);
    g.resize(s, s, true, true, true, true, s, Transformation.TOPLEFT);
    gb = g.geometricBounds;
    g.translate(E[2] + GAP * Eh - gb[0], Ecy - (gb[1] + gb[3]) / 2);
    d.activate();
    var folder = "Yatay Logo" + (shapes[q] ? " " + shapes[q] : "");
    if (shapes[q]) backdropFit(d, shapes[q], darkBg[yjobs[j][0]] ? navy(d) : white());
    fitAndSave(d, FAM + folder + "/" + yjobs[j][0] + "/ALFA 8084 - " + folder + " " + VER + " - " + yjobs[j][0], !!shapes[q]);
}
log.join("\n");
