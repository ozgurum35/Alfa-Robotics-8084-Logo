#!/bin/sh
# usage: run.sh x0 y0 x1 y1 zoom name
S="${ALFA_TMP:-tmp}"; mkdir -p "$S"
python mk5.py && python design5.py . "${ALFA_FONT:-E:/2026 masaüstü/Classic Robot/Classic Robot Bold Italic.otf}" > $S/log.txt 2>&1 || { tail -20 $S/log.txt; exit 1; }
