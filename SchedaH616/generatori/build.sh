#!/bin/sh
# Rigenera da zero il progetto KiCad della scheda RK3568 in ../progetto-kicad, esegue l'ERC ed esporta il PDF.
# Servono python3 e KiCad 10 (kicad-cli e librerie standard: vedi kilib.py per i percorsi cercati, Linux o macOS).
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
export LC_ALL=C LANG=C
[ -d "$HOME/Develop/kicad-libs/usr/share/kicad" ] && export KICAD10_SYMBOL_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/symbols" KICAD10_FOOTPRINT_DIR="$HOME/Develop/kicad-libs/usr/share/kicad/footprints"
K=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
PRJ=SchedaRK3568
mkdir -p "$P"
rm -f "$P"/*.kicad_sch "$P/Scheda.kicad_sym"
python3 "$G/gen_fp.py" "$P/Scheda.pretty"
cat > "$P/$PRJ.kicad_sch" <<'SCH'
(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "ca22b936-6f4a-45ef-aa0b-04959bbbf7ee")
	(paper "A1")
	(lib_symbols)
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)
SCH
for s in gen_bus gen_pwr gen_pmic gen_cpu gen_mem gen_comm gen_usb; do
	python3 "$G/$s.py" "$P" > /dev/null
done
python3 "$G/add_flags.py" "$P" > /dev/null
"$K" sch erc --severity-error --severity-warning -o "$P/erc.rpt" "$P/$PRJ.kicad_sch" 2>/dev/null | grep -i violations
"$K" sch export pdf -o "$G/../schema-rk3568.pdf" "$P/$PRJ.kicad_sch" 2>/dev/null | tail -1
"$K" sch export netlist --format kicadxml -o "$P/netlist.xml" "$P/$PRJ.kicad_sch" 2>/dev/null | tail -1
python3 "$G/gen_pinmap.py" "$P/netlist.xml"
rm -f "$P/netlist.xml"
