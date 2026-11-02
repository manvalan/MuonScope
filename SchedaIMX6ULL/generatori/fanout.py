"""Stima del fanout di U1 (MAPBGA-289 passo 0.8) dalla netlist: quante sfere di segnale per lato e per anello, contro i canali disponibili.
Non e' uno sbroglio. Modello: pad 0.32, via dogbone 0.45/0.2, pista 0.127 + 2 x 0.1 di distanza = 0.327 mm per canale.
Canale tra due pad 0.48 mm, tra due via 0.35 mm: una sola pista per canale. Top: anelli 0-1. Anelli >= 2 su bottom e In2.Cu, circa 15 canali per lato e per strato.
Uso: python3 fanout.py imx6ull_balls.json imx6ull_net.json"""
import json
import sys
B = json.load(open(sys.argv[1]))
N = json.load(open(sys.argv[2]))
ROWS = "ABCDEFGHJKLMNPRTU"
PLANE = {"GND_D", "3V3", "V1P35", "V1P4", "VDD_SOC_CAP", "VDD_ARM_CAP", "VDD_HIGH_CAP", "NC", "5V_SYS"}
sides = {s: {} for s in "TBLR"}
sig = 0
deep = []
for b, v in B.items():
    net = N.get(v["name"], "NC")
    if net in PLANE:
        continue
    sig += 1
    r, c = ROWS.index(b[0]), int(b[1:]) - 1
    d = {"T": r, "B": 16 - r, "L": c, "R": 16 - c}
    s = min(d, key=d.get)
    sides[s][d[s]] = sides[s].get(d[s], 0) + 1
    if d[s] >= 4:
        deep.append((b, net))
print("sfere di segnale:", sig)
for s, m in sides.items():
    top = m.get(0, 0) + m.get(1, 0)
    bot = sum(k for a, k in m.items() if a >= 2)
    print(f"lato {s}: anelli {dict(sorted(m.items()))}  top {top}/33  bottom + In2 {bot}/30")
print("segnali oltre il quarto anello:", deep)
