#!/usr/bin/env bash
# Publish the logo picker on GitHub Pages: gh-pages branch = current logo family folder + index.html (the picker).
# usage: kaynak/pages.sh   (run after secici.py; needs push access)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="$(cd "$ROOT/kaynak" && python -c "import guncel_logo; print(guncel_logo.VER)")"
SRC="$ROOT/Yeniden Olusturulan/$VER surum ailesi"
TMP="$(mktemp -d)"
cp -r "$SRC/." "$TMP/"
cp "$SRC/ALFA 8084 - Logo Secici.html" "$TMP/index.html"
touch "$TMP/.nojekyll"
cd "$TMP"
git init -q -b gh-pages
git add -A
git -c user.name=ozgurum35 -c user.email=ozgurum35@users.noreply.github.com commit -q -m "Logo Secici $VER"
git push -q --force "$(git -C "$ROOT" remote get-url origin)" gh-pages
echo "gh-pages <- $VER ($(git ls-files | wc -l) dosya)"
