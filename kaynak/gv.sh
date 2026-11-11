#!/bin/sh
# usage: gv.sh x0 y0 x1 y1 zoom name   (grid view of the current emblem_check.pdf)
S="${ALFA_TMP:-tmp}"; mkdir -p "$S"
OFF=$(python -c "import json;a=json.load(open('emblem.json'));print(a['width']/2-188.5)")
OY=$(grep -o "centre ([0-9.]*, [0-9.]*)" $S/log.txt | sed 's/.*, //;s/)//')
OYY=$(python -c "import json;a=json.load(open('emblem.json'));print(a['width']/2-$OY)")
python gridview.py emblem_check.pdf $OFF $OYY $1 $2 $3 $4 $5 $S/$6.png
