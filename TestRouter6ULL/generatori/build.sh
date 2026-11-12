#!/bin/sh
# Rigenera TestRouter6ULL in ../progetto (i file vengono sovrascritti): schema, ERC, PDF dello schema, PCB solo placement, DRC con parita' schema/PCB, PNG del placement.
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto"
PRJ=TestRouter6ULL
export LC_ALL=C LANG=C
[ -d "$HOME/Develop/kicad-libs/usr/share/kicad" ] && export KICAD10_SYMBOL_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/symbols" KICAD10_FOOTPRINT_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/footprints"
[ -z "$MIKILAB" ] && [ -d "$HOME/Develop/mikilab-kicad-library" ] && export MIKILAB="$HOME/Develop/mikilab-kicad-library"
K=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
if python3 -c "import pcbnew" > /dev/null 2>&1; then PY=python3; else PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3; fi
mkdir -p "$P"
cp "$G/template.kicad_pro" "$P/$PRJ.kicad_pro"
python3 "$G/gen_fp.py" "$P/Scheda.pretty"
python3 "$G/gen_sch.py" "$P"
printf '(sym_lib_table (version 7) (lib (name "Scheda") (type "KiCad") (uri "${KIPRJMOD}/Scheda.kicad_sym") (options "") (descr "Simboli di TestRouter6ULL")))' > "$P/sym-lib-table"
printf '(fp_lib_table (version 7) (lib (name "Scheda") (type "KiCad") (uri "${KIPRJMOD}/Scheda.pretty") (options "") (descr "Footprint di TestRouter6ULL")))' > "$P/fp-lib-table"
"$K" sch erc --severity-error --severity-warning -o "$P/erc.rpt" "$P/$PRJ.kicad_sch" 2>/dev/null | grep -i violations || true
"$K" sch export pdf -o "$G/../schema-testrouter6ull.pdf" "$P/$PRJ.kicad_sch" > /dev/null 2>&1
T=$(mktemp -d)
"$K" sch export netlist --format kicadsexpr -o "$T/net.net" "$P/$PRJ.kicad_sch" > /dev/null 2>&1
"$PY" "$G/gen_pcb.py" "$T/net.net" "$P" 2>&1 | grep -v "^$\|assert\|GetSize\|memory leak\|PROPERTY_ENUM" || true
"$K" pcb drc --schematic-parity --severity-error --severity-warning -o "$P/drc.rpt" "$P/$PRJ.kicad_pcb" 2>/dev/null | grep -i found || true
grep -E "^\[" "$P/drc.rpt" | sed 's/\]:.*/]/' | sort | uniq -c
"$K" pcb export pdf --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single -o "$T/top.pdf" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
"$K" pcb export pdf --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --mirror -o "$T/bot.pdf" "$P/$PRJ.kicad_pcb" > /dev/null 2>&1
python3 "$G/png_placement.py" "$T/top.pdf" "$T/bot.pdf" "$G/../placement-testrouter6ull.png"
rm -rf "$T"
