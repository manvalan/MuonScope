import os
import re, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kilib import extract
D = sys.argv[1]
U = lambda: str(uuid.uuid4())
ROOT = "ca22b936-6f4a-45ef-aa0b-04959bbbf7ee"
root = open(f"{D}/SchedaH616.kicad_sch").read()
def sheet_uuid(fname):
    i = root.find(f'"Sheetfile" "{fname}"'); j = root.rfind("(sheet ", 0, i)
    return re.search(r'\(uuid "([0-9a-f-]+)"\)', root[j:i]).group(1)
FLAG = extract("power", "PWR_FLAG")
WANT = {"gnss.kicad_sch": ["GNSS_V_BCKP"], "alimentazione.kicad_sch": ["VIN_SYS", "5V_EXT", "3V3_SYS", "GND_D"],
        "pmic.kicad_sch": ["3V3_PERI", "VCC-IO", "VCC-1V8", "VCC-DRAM", "VDD-CPU", "VDD-SYS"]}
n = 0
for fname, nets in WANT.items():
    t = open(f"{D}/{fname}").read()
    if '"power:PWR_FLAG"' not in t:
        t = t.replace("(lib_symbols ", "(lib_symbols " + FLAG + " ", 1)
    path = f"/{ROOT}/{sheet_uuid(fname)}"
    out = []
    for k, net in enumerate(nets):
        n += 1
        x, y = 20.32 + 20.32 * k, 280.67
        lab = (f'(global_label "{net}" (shape passive) (at {x:.2f} {y + 5.08:.2f} 270) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{U()}"))'
               if net == "GND_D" or net.startswith("GNSS_") else f'(label "{net}" (at {x:.2f} {y + 5.08:.2f} 270) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid "{U()}"))')
        out.append(f'(wire (pts (xy {x:.2f} {y:.2f}) (xy {x:.2f} {y + 5.08:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        out.append(lab)
        out.append(f'(symbol (lib_id "power:PWR_FLAG") (at {x:.2f} {y:.2f} 0) (unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (uuid "{U()}") '
                   f'(property "Reference" "#FLG0{n:02d}" (at {x:.2f} {y - 1.9:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
                   f'(property "Value" "PWR_FLAG" (at {x:.2f} {y - 3.81:.2f} 0) (effects (font (size 1.27 1.27)))) '
                   f'(property "Footprint" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
                   f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
                   f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
                   f'(pin "1" (uuid "{U()}")) (instances (project "SchedaH616" (path "{path}" (reference "#FLG0{n:02d}") (unit 1)))))')
    t = t.rstrip()
    t = t[:t.rfind("(embedded_fonts no)")] + " ".join(out) + " (embedded_fonts no))"
    open(f"{D}/{fname}", "w").write(t)
print("flag:", n)
# BUS_3V3: etichetta gerarchica senza utilizzatori -> etichetta locale, tolti pin e etichetta nel foglio radice
b = open(f"{D}/bus-mikilab.kicad_sch").read()
b = re.sub(r'\(hierarchical_label "BUS_3V3" \(shape [a-z]+\)', '(label "BUS_3V3"', b)
open(f"{D}/bus-mikilab.kicad_sch", "w").write(b)
r = root
r = re.sub(r'\s*\(pin "BUS_3V3" [a-z]+\s*\(at [^)]*\)\s*(\(uuid "[^"]+"\))?\s*\(effects\s*\(font\s*\(size [^)]*\)\s*\)\s*(\(justify [a-z ]+\))?\s*\)\s*(\(uuid "[^"]+"\))?\s*\)', "", r)
m = re.search(r'\(label "BUS_3V3" \(at ([\d.]+) ([\d.]+) 180\)', r)
if m:
    x, y = float(m.group(1)), float(m.group(2))
    r = re.sub(r'\(label "BUS_3V3" \(at [^\n]*?\(uuid "[^"]+"\)\)', "", r)
    r = re.sub(r'\(wire \(pts \(xy %.2f %.2f\) \(xy %.2f %.2f\)\)[^\n]*?\(uuid "[^"]+"\)\)' % (x + 5.08, y, x, y), "", r)
open(f"{D}/SchedaH616.kicad_sch", "w").write(r)
print("BUS_3V3 pin root:", r.count('"BUS_3V3"'))
