#!/bin/sh
# Rigenera da zero il progetto KiCad della SchedaH616 in ../progetto-kicad, esegue l'ERC ed esporta il PDF.
# Servono python3 e KiCad 10 (kicad-cli e librerie standard in /Applications/KiCad).
set -e
G="$(cd "$(dirname "$0")" && pwd)"
P="$G/../progetto-kicad"
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
mkdir -p "$P"
rm -f "$P"/*.kicad_sch "$P/H616.kicad_sym"
cat > "$P/SchedaH616.kicad_sch" <<'SCH'
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
"$K" sch erc --severity-error --severity-warning -o "$P/erc.rpt" "$P/SchedaH616.kicad_sch" 2>/dev/null | grep -i violations
"$K" sch export pdf -o "$G/../schema-h616.pdf" "$P/SchedaH616.kicad_sch" 2>/dev/null | tail -1
"$K" sch export netlist --format kicadxml -o "$P/netlist.xml" "$P/SchedaH616.kicad_sch" 2>/dev/null | tail -1
python3 "$G/gen_pinmap.py" "$P/netlist.xml"
rm -f "$P/netlist.xml"
