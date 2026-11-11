// Export v10 .ai files to PDF, SVG and PNG (guide layer removed in the exported copies; the .ai files stay unchanged)
var SRC = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/";
var OUT = SRC + "v10 disa aktarim/";
var names = ["ALFA 8084 - Amblem v10", "ALFA 8084 - Yazi Logo v10"];
var log = [];
function dropGuides(d) {
    for (var k = d.layers.length - 1; k >= 0; k--) {
        var L = d.layers[k];
        if (L.name.indexOf("Kilavuz") === 0 || !L.visible) { L.locked = false; L.visible = true; L.remove(); }
    }
}
for (var i = 0; i < names.length; i++) {
    // PNG + SVG
    var d = app.open(new File(SRC + names[i] + ".ai"));
    dropGuides(d);
    var ab = d.artboards[0].artboardRect, w = ab[2] - ab[0];
    var widths = [4096, 2048, 1024, 512];
    for (var j = 0; j < widths.length; j++) {
        var p = new ExportOptionsPNG24();
        p.antiAliasing = true; p.transparency = true; p.artBoardClipping = true;
        p.horizontalScale = p.verticalScale = Math.min(776, widths[j] / w * 100);
        d.exportFile(new File(OUT + names[i] + " " + widths[j] + "px.png"), ExportType.PNG24, p);
    }
    var s = new ExportOptionsSVG();
    s.embedRasterImages = true; s.fontType = SVGFontType.OUTLINEFONT; s.coordinatePrecision = 3;
    s.cssProperties = SVGCSSPropertyLocation.PRESENTATIONATTRIBUTES; s.documentEncoding = SVGDocumentEncoding.UTF8;
    d.exportFile(new File(OUT + names[i] + ".svg"), ExportType.SVG, s);
    // PDF (print)
    var o = new PDFSaveOptions();
    o.compatibility = PDFCompatibility.ACROBAT7; o.preserveEditability = false; o.generateThumbnails = true;
    o.viewAfterSaving = false;
    d.saveAs(new File(OUT + names[i] + ".pdf"), o);
    d.close(SaveOptions.DONOTSAVECHANGES);
    log.push(names[i] + " ok");
}
log.join("\n");
