#!/usr/bin/env bash
# Package and publish a GitHub release for logo version N (same layout as v10).
# Usage: kaynak/surum.sh 11 "notes.md"      -> publish
#        kaynak/surum.sh 11 "notes.md" --dry -> only build the packages and print what would be published
# Expects: "Yeniden Olusturulan/ALFA 8084 - {Amblem,Yazi Logo} vN.ai",
#          "Yeniden Olusturulan/vN disa aktarim/" (transparent) and ".../beyaz zemin/" (white background).
set -euo pipefail
N="${1:?version number, e.g. 11}"; NOTES="${2:?release notes file}"; DRY="${3:-}"
REPO="ozgurum35/Alfa-Robotics-8084-Logo"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
R="$ROOT/Yeniden Olusturulan"; E="$R/v$N disa aktarim"
for f in "$R/ALFA 8084 - Amblem v$N.ai" "$R/ALFA 8084 - Yazi Logo v$N.ai" "$E" "$E/beyaz zemin"; do
    [ -e "$f" ] || { echo "missing: $f" >&2; exit 1; }
done
[ -z "$(git -C "$ROOT" status --porcelain)" ] || { echo "working tree not clean: commit first" >&2; exit 1; }
git -C "$ROOT" fetch -q
[ "$(git -C "$ROOT" rev-parse HEAD)" = "$(git -C "$ROOT" rev-parse origin/main)" ] || { echo "HEAD is not pushed to origin/main" >&2; exit 1; }

OUT="$(mktemp -d)"; NOTES="$(cd "$(dirname "$NOTES")" && pwd)/$(basename "$NOTES")"
python - "$OUT" "$N" "$R" "$E" <<'EOF'
import sys, os, glob, zipfile, hashlib
out, n, r, e = sys.argv[1:]
packs = {
    f"ALFA-8084-Logo-v{n}-saydam.zip": [f for f in glob.glob(os.path.join(e, "*")) if os.path.isfile(f)],
    f"ALFA-8084-Logo-v{n}-beyaz-zemin.zip": glob.glob(os.path.join(e, "beyaz zemin", "*")),
    f"ALFA-8084-Logo-v{n}-illustrator.zip": [os.path.join(r, f"ALFA 8084 - {k} v{n}.ai") for k in ("Amblem", "Yazi Logo")],
}
sums = []
for z, files in packs.items():
    p = os.path.join(out, z)
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as f:
        for x in sorted(files):
            f.write(x, os.path.basename(x))
    print(f"{z}: {len(files)} files, {os.path.getsize(p) // 1024} KB")
    sums.append(hashlib.sha256(open(p, "rb").read()).hexdigest() + "  " + z)
open(os.path.join(out, "SHA256SUMS.txt"), "w", newline="\n").write("\n".join(sums) + "\n")
EOF
cd "$OUT"
if [ "$DRY" = "--dry" ]; then
    echo "dry run: would publish v$N at $(git -C "$ROOT" rev-parse HEAD) from $OUT"; cat SHA256SUMS.txt; exit 0
fi
gh release create "v$N" -R "$REPO" --target "$(git -C "$ROOT" rev-parse HEAD)" \
    --title "ALFA Robotics 8084 Logo v$N" --notes-file "$NOTES" --latest \
    ALFA-8084-Logo-v"$N"-*.zip SHA256SUMS.txt
# verify: download again and check checksums
mkdir check && cd check && gh release download "v$N" -R "$REPO" && sha256sum -c SHA256SUMS.txt
