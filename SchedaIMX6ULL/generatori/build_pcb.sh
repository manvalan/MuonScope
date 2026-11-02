#!/bin/sh
# Rigenera il PCB della scheda i.MX 6ULL (solo placement) dallo schema, esegue il DRC con la parita' schema/PCB
# ed esporta il placement in PDF e PNG. Va eseguito dopo build.sh. Funziona su Linux e macOS.
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
PRJ=SchedaIMX6ULL
export LC_ALL=C LANG=C
[ -d "$HOME/Develop/kicad-libs/usr/share/kicad" ] && export KICAD10_SYMBOL_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/symbols" KICAD10_FOOTPRINT_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/footprints"
[ -z "$MIKILAB" ] && [ -d "$HOME/Develop/mikilab-kicad-library" ] && export MIKILAB="$HOME/Develop/mikilab-kicad-library"
K=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
if python3 -c "import pcbnew" > /dev/null 2>&1; then PY=python3; else PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3; fi
T=$(mktemp -d)
"$K" sch export netlist --format kicadsexpr -o "$T/net.net" "$P/$PRJ.kicad_sch" > /dev/null 2>&1
"$PY" "$G/gen_pcb.py" "$T/net.net" "$P" 2>&1 | grep -v "^$\|assert\|GetSize\|memory leak\|PROPERTY_ENUM" || true
"$K" pcb drc --schematic-parity --severity-error --severity-warning -o "$P/drc.rpt" "$P/$PRJ.kicad_pcb" 2>/dev/null | grep -i found || true
grep -E "^\[" "$P/drc.rpt" | sed 's/\]:.*/]/' | sort | uniq -c
"$K" pcb export pdf --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single -o "$T/top.pdf" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
"$K" pcb export pdf --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --mirror -o "$T/bot.pdf" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
pdfunite "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-placement-imx6ull.pdf"
python3 "$G/png_placement.py" "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-placement-imx6ull.png"
