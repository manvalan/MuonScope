"""Genera il footprint Rockchip_FCBGA-636_19x19mm_P0.65mm in Scheda.pretty: python3 gen_fp.py ../progetto-kicad/Scheda.pretty

Package FCBGA636L 19x19 mm, griglia 28x28 passo 0.65 mm (righe A-AH senza I, O, Q, S, X, Z), 636 sfere da 0.35 mm.
Sfere dalla ball map Rockchip (rk3568_balls.json), vista dall'alto con A1 in alto a sinistra. Pad NSMD da 0.30 mm
(via-in-pad 0.25/0.15 con piste da 5 mil tra le sfere). Il footprint EasyEDA di LCSC C2938930 ha le stesse 636 sfere,
ruotate di 90 gradi (A1 in basso a sinistra): stessa geometria, nessun ribaltamento.
"""
import json
import os
import sys
import uuid

SC = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
BALLS = json.load(open(os.path.join(SC, "rk3568_balls.json")))
ROWS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "R", "T", "U", "V", "W", "Y",
        "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH"]
P, BODY, PAD = 0.65, 19.0, 0.30
U = lambda: str(uuid.uuid4())
NAME = "Rockchip_FCBGA-636_19x19mm_P0.65mm"


def line(x1, y1, x2, y2, layer, w):
    return (f'\t(fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) '
            f'(layer "{layer}") (uuid "{U()}"))')


def text_prop(name, val, x, y, layer, hide=False, size=1.0):
    h = " (hide yes)" if hide else ""
    return (f'\t(property "{name}" "{val}" (at {x} {y} 0) (layer "{layer}"){h} (uuid "{U()}") '
            f'(effects (font (size {size} {size}) (thickness 0.15))))')


h = BODY / 2
items = [f'(footprint "{NAME}"', '\t(version 20260206)', '\t(generator "pcbnew")', '\t(generator_version "10.0")', '\t(layer "F.Cu")',
         text_prop("Reference", "REF**", 0, -h - 1.2, "F.SilkS"),
         text_prop("Value", NAME, 0, h + 1.2, "F.Fab"),
         text_prop("Datasheet", "", 0, 0, "F.Fab", hide=True, size=1.27),
         text_prop("Description", "", 0, 0, "F.Fab", hide=True, size=1.27),
         text_prop("LCSC", "C2938930", 0, 0, "F.Fab", hide=True, size=1.27),
         '\t(attr smd)', '\t(duplicate_pad_numbers_are_jumpers no)']
# corpo (Fab) con smusso su A1, serigrafia agli angoli e segno di A1, courtyard 0.5 mm oltre il corpo
c = 1.0
items += [line(-h + c, -h, h, -h, "F.Fab", 0.1), line(h, -h, h, h, "F.Fab", 0.1), line(h, h, -h, h, "F.Fab", 0.1),
          line(-h, h, -h, -h + c, "F.Fab", 0.1), line(-h, -h + c, -h + c, -h, "F.Fab", 0.1)]
s, k = h + 0.11, 1.5
for sx in (-1, 1):
    for sy in (-1, 1):
        if sx == -1 and sy == -1:
            continue
        items += [line(sx * s, sy * s, sx * (s - k), sy * s, "F.SilkS", 0.12), line(sx * s, sy * s, sx * s, sy * (s - k), "F.SilkS", 0.12)]
items += [line(-s, -s + k, -s, -s, "F.SilkS", 0.12), line(-s, -s, -s + k, -s, "F.SilkS", 0.12),
          f'\t(fp_circle (center {-s - 0.6:.3f} {-s - 0.6:.3f}) (end {-s - 0.35:.3f} {-s - 0.6:.3f}) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))']
cy = h + 0.5
items += [line(-cy, -cy, cy, -cy, "F.CrtYd", 0.05), line(cy, -cy, cy, cy, "F.CrtYd", 0.05), line(cy, cy, -cy, cy, "F.CrtYd", 0.05),
          line(-cy, cy, -cy, -cy, "F.CrtYd", 0.05)]
items.append(f'\t(fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))')
n = 0
for ball in sorted(BALLS, key=lambda b: (ROWS.index(b.rstrip("0123456789")), int(b[len(b.rstrip("0123456789")):]))):
    r = ROWS.index(ball.rstrip("0123456789"))
    col = int(ball[len(ball.rstrip("0123456789")):])
    x, y = (col - 14.5) * P, (r - 13.5) * P
    items.append(f'\t(pad "{ball}" smd circle (at {x:.4f} {y:.4f}) (size {PAD} {PAD}) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{U()}"))')
    n += 1
assert n == 636
items.append("\t(embedded_fonts no)")
items.append(")")
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".kicad_mod"), "w").write("\n".join(items) + "\n")
print("pad:", n)
