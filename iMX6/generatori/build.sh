#!/bin/sh
# Rigenera la scheda iMX6 da nanoberry: schema (ERC), PCB aggiornato (DRC con parita'), render PDF/PNG.
# Servono KiCad 10 (kicad-cli, Python con pcbnew), le librerie standard e la libreria MIKILAB.
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
O="$G/../nanoberry-originale"
export LC_ALL=C LANG=C
[ -d "$HOME/Develop/kicad-libs/usr/share/kicad" ] && export KICAD10_SYMBOL_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/symbols" KICAD10_FOOTPRINT_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/footprints"
[ -z "$MIKILAB" ] && [ -d "$HOME/Develop/mikilab-kicad-library" ] && export MIKILAB="$HOME/Develop/mikilab-kicad-library"
K=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
T=$(mktemp -d)
# simboli di nanoberry: cache KiCad 5 convertita
"$K" sym upgrade --force -o "$T/nano-cache.kicad_sym" "$O/nano-cache.lib" > /dev/null 2>&1
python3 "$G/converti.py" "$T" "$P"
"$K" sch erc --severity-error --severity-warning -o "$P/erc.rpt" "$P/iMX6.kicad_sch" | grep -i violations || true
"$K" sch export pdf -o "$G/../schema-imx6.pdf" "$P/iMX6.kicad_sch" > /dev/null 2>&1
"$K" sch export netlist --format kicadsexpr -o "$T/net.net" "$P/iMX6.kicad_sch" > /dev/null 2>&1
# PCB: si riparte sempre dal PCB originale di nanoberry convertito
cp "$O/nano.kicad_pcb" "$P/iMX6.kicad_pcb"
"$K" pcb upgrade "$P/iMX6.kicad_pcb" > /dev/null 2>&1
python3 "$G/aggiorna_pcb.py" "$T/net.net" "$P" 2>&1 | grep -v "^$\|assert\|memory leak\|PROPERTY_ENUM\|Debug:\|Warning:\|Zone fills" || true
# zone: il riempimento di kicad-cli a volte si blocca su questa macchina; si riprova con un tempo limite
for i in 1 2 3; do
	timeout 300 "$K" pcb drc --refill-zones --save-board --schematic-parity --severity-error --severity-warning -o "$P/drc.rpt" "$P/iMX6.kicad_pcb" > /dev/null 2>&1 && break || true
done
grep -E "^\*\* Found" "$P/drc.rpt" || true
"$K" pcb export pdf --layers "Edge.Cuts,F.Fab,F.CrtYd,F.Silkscreen,F.Cu" --mode-single -o "$T/top.pdf" "$P/iMX6.kicad_pcb" > /dev/null 2>&1
"$K" pcb export pdf --layers "Edge.Cuts,B.Fab,B.CrtYd,B.Silkscreen,B.Cu" --mode-single --mirror -o "$T/bot.pdf" "$P/iMX6.kicad_pcb" > /dev/null 2>&1
pdfunite "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-imx6.pdf"
python3 "$G/png_placement.py" "$T/top.pdf" "$T/bot.pdf" "$G/../pcb-imx6.png"
rm -rf "$T"
