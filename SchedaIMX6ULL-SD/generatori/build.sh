#!/bin/sh
# Rigenera lo schema della scheda i.MX 6ULL con sola microSD in ../progetto-kicad (i file vengono sovrascritti), esegue l'ERC, esporta PDF e mappa dei pin.
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
export LC_ALL=C LANG=C
[ -d "$HOME/Develop/kicad-libs/usr/share/kicad" ] && export KICAD10_SYMBOL_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/symbols" KICAD10_FOOTPRINT_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/footprints"
[ -z "$MIKILAB" ] && [ -d "$HOME/Develop/mikilab-kicad-library" ] && export MIKILAB="$HOME/Develop/mikilab-kicad-library"
K=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
PRJ=SchedaIMX6ULL-SD
mkdir -p "$P"
python3 "$G/gen_fp.py" "$P/Scheda.pretty"
python3 "$G/gen_sch.py" "$P"
printf '(sym_lib_table (version 7) (lib (name "Scheda") (type "KiCad") (uri "${KIPRJMOD}/Scheda.kicad_sym") (options "") (descr "Simboli della scheda i.MX 6ULL")))' > "$P/sym-lib-table"
printf '(fp_lib_table (version 7) (lib (name "Scheda") (type "KiCad") (uri "${KIPRJMOD}/Scheda.pretty") (options "") (descr "Footprint della scheda i.MX 6ULL")))' > "$P/fp-lib-table"
"$K" sch erc --severity-error --severity-warning -o "$P/erc.rpt" "$P/$PRJ.kicad_sch" 2>/dev/null | grep -i violations || true
"$K" sch export pdf -o "$G/../schema-imx6ull-sd.pdf" "$P/$PRJ.kicad_sch" 2>/dev/null | tail -1
python3 "$G/gen_pinmap.py"
