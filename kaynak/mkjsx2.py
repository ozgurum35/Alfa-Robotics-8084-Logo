import sys, json
out = sys.argv[1]; jobs = sys.argv[2:]   # pairs: json, target .ai
data = [{"target": jobs[i+1].replace("\\", "/"), "art": json.load(open(jobs[i]))} for i in range(0, len(jobs), 2)]
JS = r"""
var JOBS = __DATA__;
var LOG = [];
function rgb(c) { var k = new RGBColor(); k.red = c[0]; k.green = c[1]; k.blue = c[2]; return k; }
function fillPath(pi, sub, ox, oy, color) {
    var pts = [], i;
    for (i = 0; i < sub.length; i++) pts.push([ox + sub[i].p[0], oy - sub[i].p[1]]);
    pi.setEntirePath(pts);
    for (i = 0; i < sub.length; i++) {
        var pp = pi.pathPoints[i], a = sub[i];
        pp.leftDirection = [ox + a.i[0], oy - a.i[1]];
        pp.rightDirection = [ox + a.o[0], oy - a.o[1]];
        pp.pointType = PointType.CORNER;
    }
    pi.closed = true; pi.stroked = false; pi.filled = true; pi.fillColor = color; pi.evenodd = true;
}
function build(job) {
    var art = job.art;
    var doc = app.documents.add(DocumentColorSpace.RGB, art.width, art.height);
    var ab = doc.artboards[0].artboardRect, ox = ab[0], oy = ab[1];
    doc.artboards[0].name = "Logo";
    var layer = doc.layers[0]; layer.name = "ALFA Robotics 8084";
    var sw = {}, n = 0, g, i, j, s;
    for (g = 0; g < art.groups.length; g++) {
        var grp = layer.groupItems.add(); grp.name = art.groups[g].name;
        var items = art.groups[g].items;
        for (i = 0; i < items.length; i++) {
            var it = items[i];
            if (!sw[it.color]) {
                var sp = doc.spots.add(); sp.name = "ALFA " + it.color; sp.colorType = ColorModel.PROCESS; sp.color = rgb(it.rgb);
                var sc = new SpotColor(); sc.spot = sp; sc.tint = 100; sw[it.color] = sc;
            }
            if (it.subs.length == 1) {
                var p = grp.pathItems.add(); p.name = it.name; fillPath(p, it.subs[0], ox, oy, sw[it.color]); n++;
            } else {
                var cp = grp.compoundPathItems.add(); cp.name = it.name;
                for (s = 0; s < it.subs.length; s++) { fillPath(cp.pathItems.add(), it.subs[s], ox, oy, sw[it.color]); n++; }
            }
        }
    }
    if (art.circle) {
        var gl = doc.layers.add(); gl.name = "Kilavuz daire (yazdirilmaz)";
        var r = art.circle[2];
        var c = gl.pathItems.ellipse(oy - art.circle[1] + r, ox + art.circle[0] - r, 2 * r, 2 * r);
        c.filled = false; c.stroked = true; c.strokeWidth = 0.5; c.strokeColor = rgb([230, 0, 120]); c.name = "Cevreleyen daire";
        gl.printable = false; gl.visible = false;
        doc.activeLayer = layer;
    }
    var o = new IllustratorSaveOptions();
    o.pdfCompatible = true; o.embedICCProfile = true; o.compressed = true;
    doc.saveAs(new File(job.target), o);
    LOG.push(job.target + " | paths " + n + " | artboard " + (ab[2]-ab[0]) + "x" + (ab[1]-ab[3]));
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var lvl = app.userInteractionLevel;
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
try { for (var k = 0; k < JOBS.length; k++) build(JOBS[k]); }
catch (e) { LOG.push("ERROR line " + e.line + ": " + e.message); }
app.userInteractionLevel = lvl;
LOG.join("\n");
"""
open(out, "w", encoding="ascii").write(JS.replace("__DATA__", json.dumps(data)))
