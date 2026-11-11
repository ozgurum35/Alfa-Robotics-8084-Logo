#!/bin/sh
# usage: var.sh out.pdf file 's/old/new/' ...   (build a variant into out.pdf, then restore the sources)
OUT=$1; F=$2; shift 2
cp "$F" "$F.bak"
for e in "$@"; do sed -i "$e" "$F"; done
sh run.sh; R=$?
[ $R -eq 0 ] && sh snap.sh "$OUT" && grep "8084 cap" ${ALFA_TMP:-tmp}/log.txt | head -1 > "$OUT.log"
mv "$F.bak" "$F"; sh run.sh
exit $R
