#!/bin/sh
# Rigenera il PCB della SchedaH616 (solo placement) dallo schema, esegue il DRC
# ed esporta il placement in PDF e PNG. Va eseguito dopo build.sh.
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
T=$(mktemp -d)
"$K" sch export netlist --format kicadsexpr -o "$T/net.net" "$P/SchedaH616.kicad_sch" > /dev/null 2>&1
"$PY" "$G/gen_pcb.py" "$T/net.net" "$P" 2>&1 | grep -v "^$\|assert\|GetSize\|memory leak" || true
"$K" pcb drc --severity-error --severity-warning -o "$P/drc.rpt" "$P/SchedaH616.kicad_pcb" 2>/dev/null | grep -i found
grep -E "^\[" "$P/drc.rpt" | sed 's/\]:.*/]/' | sort | uniq -c
"$K" pcb export pdf --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single -o "$T/top.pdf" "$P/SchedaH616.kicad_pcb" > /dev/null 2>&1
"$K" pcb export pdf --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --mirror -o "$T/bot.pdf" "$P/SchedaH616.kicad_pcb" > /dev/null 2>&1
pdfunite "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-placement-h616.pdf"
"$K" pcb export svg --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single --fit-page-to-board -o "$T/top.svg" "$P/SchedaH616.kicad_pcb" > /dev/null 2>&1
"$K" pcb export svg --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --fit-page-to-board --mirror -o "$T/bot.svg" "$P/SchedaH616.kicad_pcb" > /dev/null 2>&1
rsvg-convert -b white -w 1000 "$T/top.svg" -o "$T/top.png"
rsvg-convert -b white -w 1000 "$T/bot.svg" -o "$T/bot.png"
magick "$T/top.png" "$T/bot.png" -bordercolor white -border 20 +append "$G/../pcb-placement-h616.png"
rm -rf "$T"
