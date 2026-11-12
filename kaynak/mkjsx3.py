"""Illustrator build script (v10, professional file structure):
- one layer per part (Kalkan / Kurt / Yazi), guide circle on its own locked, hidden, non-printing layer
- global process colour swatches only (Illustrator default swatches removed)
- smooth anchor points marked SMOOTH, corners CORNER (so editing keeps tangency)
- Turkish names, named artboard
usage: mkjsx3.py out.jsx json1 target1.ai "Artboard name 1" [json2 target2.ai "name 2" ...]"""
import sys, json, math
out = sys.argv[1]; a = sys.argv[2:]
NAMES = {"Kalkan ust": "Kalkan üst", "Kalkan alt": "Kalkan alt", "Kurt": "Kurt", "ALFA": "ALFA", "ROBOTICS": "ROBOTICS", "8084": "8084",
         "Lacivert siluet": "Lacivert siluet", "Gok sol": "Gök sol", "Gok sag": "Gök sağ", "Gok centik": "Gök çentik",
         "Cerceve": "Çerçeve", "Zemin (8084 bosluklu)": "Zemin (8084 boşluklu)",
         "Bas ve boyun (kapali goz bosluklu)": "Baş ve boyun (kapalı göz boşluklu)", "Goz ve kulak": "Göz ve kulak",
         "Yele 1": "Yele 1", "Yele 2": "Yele 2", "A sol": "A sol", "L": "L", "F": "F", "A sag": "A sağ",
         "Bant + ROBOTICS": "Bant + ROBOTICS"}
LAYER = {"Kalkan ust": "Kalkan", "Kalkan alt": "Kalkan", "Kurt": "Kurt", "ALFA": "Yazı", "ROBOTICS": "Yazı", "8084": "Yazı"}
SWATCH = {"Lacivert": "ALFA Lacivert", "Acik Mavi": "ALFA Açık Mavi", "Buz": "ALFA Buz"}


def smooth_flags(sub):
    fl = []
    for k, n in enumerate(sub):
        p, i, o = n["p"], n["i"], n["o"]
        vi, vo = (p[0] - i[0], p[1] - i[1]), (o[0] - p[0], o[1] - p[1])
        li, lo = math.hypot(*vi), math.hypot(*vo)
        ok = li > 1e-6 and lo > 1e-6 and (vi[0] * vo[0] + vi[1] * vo[1]) / li / lo > math.cos(math.radians(0.5))
        fl.append(1 if ok else 0)
    return fl


jobs = []
for k in range(0, len(a), 3):
    art = json.load(open(a[k]))
    for g in art["groups"]:
        g["layer"] = LAYER[g["name"]]; g["name"] = NAMES.get(g["name"], g["name"])
        for it in g["items"]:
            it["name"] = NAMES.get(it["name"], it["name"]); it["swatch"] = SWATCH[it["color"]]
            it["smooth"] = [smooth_flags(s) for s in it["subs"]]
    jobs.append({"target": a[k + 1].replace("\\", "/"), "artboard": a[k + 2], "art": art})
JS = r"""
var JOBS = __DATA__;
var LOG = [];
function rgb(c) { var k = new RGBColor(); k.red = c[0]; k.green = c[1]; k.blue = c[2]; return k; }
function fillPath(pi, sub, sm, ox, oy, color) {
    var pts = [], i;
    for (i = 0; i < sub.length; i++) pts.push([ox + sub[i].p[0], oy - sub[i].p[1]]);
    pi.setEntirePath(pts);
    for (i = 0; i < sub.length; i++) {
        var pp = pi.pathPoints[i], q = sub[i];
        pp.leftDirection = [ox + q.i[0], oy - q.i[1]];
        pp.rightDirection = [ox + q.o[0], oy - q.o[1]];
        pp.pointType = sm[i] ? PointType.SMOOTH : PointType.CORNER;
    }
    pi.closed = true; pi.stroked = false; pi.filled = true; pi.fillColor = color; pi.evenodd = true;
}
function build(job) {
    var art = job.art;
    var doc = app.documents.add(DocumentColorSpace.RGB, art.width, art.height);
    var ab = doc.artboards[0].artboardRect, ox = ab[0], oy = ab[1];
    doc.artboards[0].name = job.artboard;
    // swatches: drop every default swatch / group, keep [None] and [Registration]
    for (var s0 = doc.swatchGroups.length - 1; s0 > 0; s0--) { try { doc.swatchGroups[s0].remove(); } catch (e) {} }
    for (var s1 = doc.swatches.length - 1; s1 >= 0; s1--) {
        var sw0 = doc.swatches[s1], t = sw0.color.typename;
        if (t == "NoColor" || (t == "SpotColor" && sw0.color.spot.colorType == ColorModel.REGISTRATION)) continue;
        try { sw0.remove(); } catch (e) {}
    }
    for (var s2 = doc.spots.length - 1; s2 >= 0; s2--) { try { if (doc.spots[s2].colorType != ColorModel.REGISTRATION) doc.spots[s2].remove(); } catch (e) {} }
    var sw = {}, layers = {}, n = 0, g, i, s;
    var base = doc.layers[0];
    // layers bottom -> top in the order they first appear
    var order = [];
    for (g = 0; g < art.groups.length; g++) {
        var ln = art.groups[g].layer, seen = false;
        for (var q = 0; q < order.length; q++) if (order[q] == ln) seen = true;
        if (!seen) order.push(ln);
    }
    for (var L = 0; L < order.length; L++) {
        var ly = (L == 0) ? base : doc.layers.add();
        ly.name = order[L]; layers[order[L]] = ly;
    }
    for (g = 0; g < art.groups.length; g++) {
        var grp = layers[art.groups[g].layer].groupItems.add(); grp.name = art.groups[g].name;
        var items = art.groups[g].items;
        for (i = 0; i < items.length; i++) {
            var it = items[i];
            if (!sw[it.swatch]) {
                var sp = doc.spots.add(); sp.name = it.swatch; sp.colorType = ColorModel.PROCESS; sp.color = rgb(it.rgb);
                var sc = new SpotColor(); sc.spot = sp; sc.tint = 100; sw[it.swatch] = sc;
            }
            if (it.subs.length == 1) {
                var p = grp.pathItems.add(); p.name = it.name; fillPath(p, it.subs[0], it.smooth[0], ox, oy, sw[it.swatch]); n++;
            } else {
                var cp = grp.compoundPathItems.add(); cp.name = it.name;
                for (s = 0; s < it.subs.length; s++) { fillPath(cp.pathItems.add(), it.subs[s], it.smooth[s], ox, oy, sw[it.swatch]); n++; }
            }
        }
    }
    if (art.circle) {
        var gl = doc.layers.add(); gl.name = "Kılavuz daire (yazdırılmaz)";
        var r = art.circle[2];
        var c = gl.pathItems.ellipse(oy - art.circle[1] + r, ox + art.circle[0] - r, 2 * r, 2 * r);
        c.filled = false; c.stroked = true; c.strokeWidth = 0.5; c.strokeColor = rgb([230, 0, 120]); c.name = "Çevreleyen daire";
        gl.printable = false; gl.visible = false; gl.locked = true;
    }
    doc.activeLayer = layers[order[order.length - 1]];
    var o = new IllustratorSaveOptions();
    o.pdfCompatible = true; o.embedICCProfile = true; o.compressed = true;
    doc.saveAs(new File(job.target), o);
    LOG.push(job.target + " | paths " + n + " | layers " + doc.layers.length + " | swatches " + doc.swatches.length);
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var lvl = app.userInteractionLevel;
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
try { for (var k = 0; k < JOBS.length; k++) build(JOBS[k]); }
catch (e) { LOG.push("ERROR line " + e.line + ": " + e.message); }
app.userInteractionLevel = lvl;
LOG.join("\n");
"""
open(out, "w", encoding="utf-8-sig").write(JS.replace("__DATA__", json.dumps(jobs)))
