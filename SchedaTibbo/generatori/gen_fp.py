"""Footprint di progetto: LQFP-176 20x20 passo 0.4 della libreria KiCad con pad esposto 177 (GND) per l'SP7021-IF.

Uso: python3 gen_fp.py progetto-kicad
La dimensione del pad esposto non e' nel datasheet pubblico SP7021: 10 x 10 mm provvisori, da verificare sul disegno
del package Sunplus/Tibbo prima della produzione. Pasta a 3 x 3 finestre (circa 50 %).
"""
import os
import sys
from kilib import FPLIB

PRJ = sys.argv[1]
EP = 10.0
src = open(f"{FPLIB}/Package_QFP.pretty/LQFP-176_20x20mm_P0.4mm.kicad_mod").read()
name = f"LQFP-176-1EP_20x20mm_P0.4mm_EP{EP:g}x{EP:g}mm"
t = src.replace('(footprint "LQFP-176_20x20mm_P0.4mm"', f'(footprint "{name}"', 1)
t = t.replace('(descr "LQFP, 176 Pin', '(descr "LQFP, 176 Pin + EP %gx%g mm (SP7021, EP da verificare)' % (EP, EP), 1)
pad = f'\t(pad "177" smd rect\n\t\t(at 0 0)\n\t\t(size {EP:g} {EP:g})\n\t\t(property pad_prop_heatsink)\n\t\t(layers "F.Cu" "F.Mask")\n\t\t(zone_connect 2)\n\t)\n'
step = EP / 3
for i in range(3):
    for j in range(3):
        pad += (f'\t(pad "" smd roundrect\n\t\t(at {(i - 1) * step:.4f} {(j - 1) * step:.4f})\n\t\t(size {step * 0.7:.4f} {step * 0.7:.4f})\n'
                f'\t\t(layers "F.Paste")\n\t\t(roundrect_rratio 0.15)\n\t)\n')
t = t.replace("\t(embedded_fonts no)", pad + "\t(embedded_fonts no)", 1)
os.makedirs(os.path.join(PRJ, "Scheda.pretty"), exist_ok=True)
open(os.path.join(PRJ, "Scheda.pretty", f"{name}.kicad_mod"), "w").write(t)
print("footprint:", name)
