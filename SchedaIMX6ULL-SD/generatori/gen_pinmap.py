"""Scrive docs/pinmap-imx6ull.md: sfera, dominio, nome e net di ogni sfera (dalle tabelle usate da gen_sch.py)."""
import json
import os
SC = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(SC, "imx6ull_balls.json")))
N = json.load(open(os.path.join(SC, "imx6ull_net.json")))
out = ["# i.MX 6ULL: mappa delle sfere della scheda", "",
       "Generata da `generatori/gen_pinmap.py`. Sfere: datasheet NXP IMX6ULLCEC Rev 1.2, tabelle 90 e 91 (14x14 mm), confrontate con la netlist di una scheda KiCad aperta col 6ULL (289/289).",
       "Le ALT dei pad usati sono in `docs/scelte-progetto.md`. Le sfere con net `-` restano libere.", "", "| Sfera | Nome | Dominio | Net |", "|---|---|---|---|"]
for b, v in B.items():
    net = N.get(v["name"], "-")
    out.append(f"| {b} | {v['name']} | {v['dominio']} | {'-' if net == 'NC' else net} |")
open(os.path.join(SC, "..", "docs", "pinmap-imx6ull.md"), "w").write("\n".join(out) + "\n")
print("sfere:", len(B), "con net:", sum(1 for v in B.values() if N.get(v["name"], "NC") != "NC"))
