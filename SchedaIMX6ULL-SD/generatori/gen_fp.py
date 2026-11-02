"""Footprint di progetto: LB-LINK BL-M8723DS1, LGA-44 12x12 mm (datasheet V1.0.1.3, par. 6.2 Recommend PCB Layout Footprint).
Passo 0.9, pad 0.5 x 1.5 che escono 0.5 oltre il modulo. Pin 1 in alto a sinistra, 1-11 a sinistra, 12-22 in basso, 23-33 a destra dal basso, 34-44 in alto da destra.
Uso: python3 gen_fp.py ../progetto-kicad/Scheda.pretty"""
import os
import re
import sys
import uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kilib import block, mik_fp_dir

OUT = sys.argv[1]
U = lambda: str(uuid.uuid4())
NAME = "LB-LINK_BL-M8723DS1_LGA-44_12x12mm"
P, W, L, CENTER = 0.9, 0.5, 1.5, 5.75  # passo, larghezza, lunghezza, centro del pad dal centro del modulo
h = 6.0


def line(x1, y1, x2, y2, layer, w):
    return f'\t(fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{U()}"))'


def prop(name, val, x, y, layer, hide=False):
    hd = " (hide yes)" if hide else ""
    return f'\t(property "{name}" "{val}" (at {x} {y} 0) (layer "{layer}"){hd} (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))'


items = [f'(footprint "{NAME}"', '\t(version 20260206)', '\t(generator "pcbnew")', '\t(generator_version "10.0")', '\t(layer "F.Cu")',
         prop("Reference", "REF**", 0, -h - 1.8, "F.SilkS"), prop("Value", NAME, 0, h + 1.8, "F.Fab"), prop("Datasheet", "", 0, 0, "F.Fab", True), prop("Description", "", 0, 0, "F.Fab", True),
         '\t(attr smd)', '\t(duplicate_pad_numbers_are_jumpers no)']
items += [line(-h, -h, h, -h, "F.Fab", 0.1), line(h, -h, h, h, "F.Fab", 0.1), line(h, h, -h, h, "F.Fab", 0.1), line(-h, h, -h, -h, "F.Fab", 0.1)]
c = h + 0.75
items += [line(-c, -c, c, -c, "F.CrtYd", 0.05), line(c, -c, c, c, "F.CrtYd", 0.05), line(c, c, -c, c, "F.CrtYd", 0.05), line(-c, c, -c, -c, "F.CrtYd", 0.05)]
s = h + 0.15
items += [line(-s, -s, -s + 1, -s, "F.SilkS", 0.12), line(s, -s, s - 1, -s, "F.SilkS", 0.12), line(s, s, s - 1, s, "F.SilkS", 0.12), line(-s, s, -s + 1, s, "F.SilkS", 0.12),
          f'\t(fp_circle (center {-c - 0.3:.3f} {-4.5:.3f}) (end {-c - 0.05:.3f} {-4.5:.3f}) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))']
pads = []
off = [-4.5 + P * i for i in range(11)]
for i, o in enumerate(off):
    pads.append((1 + i, -CENTER, o, L, W))             # 1-11 sinistra, dall'alto
    pads.append((12 + i, o, CENTER, W, L))              # 12-22 basso, da sinistra
    pads.append((23 + i, CENTER, -o, L, W))             # 23-33 destra, dal basso
    pads.append((34 + i, -o, -CENTER, W, L))            # 34-44 alto, da destra
for n, x, y, sx, sy in sorted(pads):
    items.append(f'\t(pad "{n}" smd roundrect (at {x:.3f} {y:.3f}) (size {sx} {sy}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15) (uuid "{U()}"))')
items += ["\t(embedded_fonts no)", ")"]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".kicad_mod"), "w").write("\n".join(items) + "\n")
assert len(pads) == 44


# Copie di progetto di due footprint EasyEDA della libreria MIKILAB, con le correzioni per questa scheda:
# SMA: tolti bordo scheda e serigrafia del footprint (la scheda ha il suo bordo); quarzo 32.768 kHz: tolta la serigrafia sul pad.
def local_copy(nick, name, drop_layers=(), npth=False):
    txt = open(os.path.join(mik_fp_dir(nick), name + ".kicad_mod")).read()
    for m in reversed(list(re.finditer(r"\(fp_(?:line|arc|circle|rect|poly)\b", txt))):
        b = block(txt, m.start())
        if any(f'(layer "{L}")' in b or f"(layer {L})" in b for L in drop_layers):
            txt = txt[:m.start()] + txt[m.start() + len(b):]
    if npth:
        txt = re.sub(r'\(pad ""\s+thru_hole', '(pad "" np_thru_hole', txt)
    open(os.path.join(OUT, name + ".kicad_mod"), "w").write(txt)


local_copy("MIKILAB_BWSMA_KE_P001", "SMA-SMD_BWSMA-KE-P001", ("Edge.Cuts", "F.SilkS"))
local_copy("MIKILAB_Q13FC1350000400", "FC-135R_L3.2-W1.5", ("F.SilkS",))
