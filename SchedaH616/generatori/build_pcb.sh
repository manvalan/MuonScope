#!/bin/sh
# Rigenera il PCB della scheda RK3568 (solo placement) dallo schema, esegue il DRC con la parita' schema/PCB
# ed esporta il placement in PDF e PNG. Va eseguito dopo build.sh. Funziona su Linux e macOS.
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
PRJ=SchedaRK3568
export LC_ALL=C LANG=C
[ -d "$HOME/Develop/kicad-libs/usr/share/kicad" ] && export KICAD10_SYMBOL_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/symbols" KICAD10_FOOTPRINT_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/footprints"
K=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
if python3 -c "import pcbnew" > /dev/null 2>&1; then PY=python3; else PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3; fi
T=$(mktemp -d)
"$K" sch export netlist --format kicadsexpr -o "$T/net.net" "$P/$PRJ.kicad_sch" > /dev/null 2>&1
"$PY" "$G/gen_pcb.py" "$T/net.net" "$P" 2>&1 | grep -v "^$\|assert\|GetSize\|memory leak\|PROPERTY_ENUM" || true
"$K" pcb drc --schematic-parity --severity-error --severity-warning -o "$P/drc.rpt" "$P/$PRJ.kicad_pcb" 2>/dev/null | grep -i found || true
grep -E "^\[" "$P/drc.rpt" | sed 's/\]:.*/]/' | sort | uniq -c
"$K" pcb export pdf --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single -o "$T/top.pdf" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
"$K" pcb export pdf --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --mirror -o "$T/bot.pdf" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
pdfunite "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-placement-rk3568.pdf"
"$K" pcb export svg --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single --fit-page-to-board -o "$T/top.svg" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
"$K" pcb export svg --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --fit-page-to-board --mirror -o "$T/bot.svg" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
if command -v rsvg-convert > /dev/null && command -v magick > /dev/null; then
	rsvg-convert -b white -w 1000 "$T/top.svg" -o "$T/top.png"
	rsvg-convert -b white -w 1000 "$T/bot.svg" -o "$T/bot.png"
	magick "$T/top.png" "$T/bot.png" -bordercolor white -border 20 +append "$G/../pcb-placement-rk3568.png"
else
	# senza rsvg/ImageMagick: pdftoppm sulle due pagine, ritaglio sulla scheda e affiancamento con Pillow
	python3 "$G/png_placement.py" "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-placement-rk3568.png"
fi
rm -rf "$T"
