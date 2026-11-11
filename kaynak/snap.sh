#!/bin/sh
# usage: snap.sh out.pdf   (copy the current emblem_check.pdf + its circle centre for soru.py)
L="${ALFA_TMP:-tmp}/log.txt"
cp emblem_check.pdf "$1" && grep -o "centre ([0-9.]*, [0-9.]*)" $L | head -1 | sed 's/centre (//;s/)//;s/,//' > "$1.off"
