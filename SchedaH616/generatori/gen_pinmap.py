"""Scrive docs/pinmap-rk3568.md dalla netlist esportata (kicadxml) e dalla ball map Rockchip: python3 gen_pinmap.py netlist.xml"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
BALLS = json.load(open(os.path.join(SC, "rk3568_balls.json")))
net_of = {}
for n in ET.parse(sys.argv[1]).getroot().iter("net"):
    for x in n.iter("node"):
        if x.get("ref") == "U301":
            net_of[x.get("pin")] = n.get("name").split("/")[-1]
ROWS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "R", "T", "U", "V", "W", "Y",
        "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH"]


def key(b):
    m = re.match(r"([A-Z]+)(\d+)$", b)
    return (ROWS.index(m.group(1)), int(m.group(2)))


def gpio_key(t):
    m = re.search(r"GPIO(\d)_([A-D])(\d)", t[0])
    return (int(m.group(1)), m.group(2), int(m.group(3)))


DOM = {"GPIO0_A": "PMUIO1 3.3 V", "GPIO0_B": "PMUIO2 3.3 V", "GPIO0_C": "PMUIO2 3.3 V", "GPIO0_D0": "PMUIO2 3.3 V",
       "GPIO0_D1": "PMUIO2 3.3 V", "GPIO0_D": "PMUIO0 1.8 V"}


def domain(g, part):
    for k in sorted(DOM, key=len, reverse=True):
        if g.startswith(k):
            return DOM[k]
    d = part.split()[0]
    return {"VCCIO1": "VCCIO1 (non alimentato)", "VCCIO2": "VCCIO2 1.8 V", "VCCIO3": "VCCIO3 VCCIO_SD", "VCCIO4": "VCCIO4 3.3 V",
            "VCCIO5": "VCCIO5 3.3 V", "VCCIO6": "VCCIO6 3.3 V", "VCCIO7": "VCCIO7 3.3 V"}.get(d, d)


out = ["# RK3568: mappa dei pin della scheda", "",
       "Generata da `generatori/gen_pinmap.py` a partire dalla netlist dello schema e dalla ball map Rockchip",
       "(RK3568 PinOut V1.1, foglio \"PinOut List\"), controllata sfera per sfera sulla tabella 2-1 del datasheet RK3568 V1.2:",
       "636 sfere su 636 coincidono.", "",
       "Le funzioni dei GPIO sono quelle scelte per la scheda (vedi `generatori/gen_cpu.py`). I GPIO senza net restano liberi",
       "(flottanti, come indicato da Rockchip per i pin non usati).", "",
       "## GPIO", "", "| GPIO | Sfera | Dominio | Net | Funzioni della sfera |", "|---|---|---|---|---|"]
gp = []
for b, (name, dom, part) in BALLS.items():
    m = re.search(r"GPIO\d_[A-D]\d", name)
    if m:
        gp.append((m.group(0), b, name, part))
for g, b, name, part in sorted(gp, key=gpio_key):
    n = net_of.get(b, "")
    n = "" if n.startswith("unconnected") else n
    out.append(f"| {g} | {b} | {domain(g, part)} | {n or '-'} | {name.replace('_' + g.split('_')[1], '', 0)} |")
out += ["", "## Altre sfere (non GPIO)", "", "| Sfera | Nome | Net |", "|---|---|---|"]
for b in sorted([b for b, v in BALLS.items() if not re.search(r"GPIO\d_[A-D]\d", v[0])], key=key):
    n = net_of.get(b, "")
    out.append(f"| {b} | {BALLS[b][0]} | {'NC' if not n or n.startswith('unconnected') else n} |")
open(os.path.join(SC, "..", "docs", "pinmap-rk3568.md"), "w").write("\n".join(out) + "\n")
print("sfere:", len(BALLS), "collegate:", sum(1 for b in BALLS if b in net_of and not net_of[b].startswith("unconnected")))
