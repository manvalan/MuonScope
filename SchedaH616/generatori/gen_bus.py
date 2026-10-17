"""Genera il foglio KiCad 10 'Bus MIKILAB' per la scheda RK3568 e lo aggancia al foglio radice."""
import os, re, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kilib import LIB, PROJ, ROOT_UUID, mik

PRJ = sys.argv[1]
SHEET_UUID = str(uuid.uuid4())
PATH = f"/{ROOT_UUID}/{SHEET_UUID}"
U = lambda: str(uuid.uuid4())


def extract(lib, name):
    t = open(f"{LIB}/{lib}.kicad_sym").read()
    i = t.find(f'(symbol "{name}"')
    d = 0
    for j in range(i, len(t)):
        if t[j] == "(":
            d += 1
        elif t[j] == ")":
            d -= 1
            if d == 0:
                s = t[i:j + 1]
                return s.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)


def pins_of(symtext):
    return {n: (float(x), float(y)) for x, y, n in
            re.findall(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) [\d.]+\).*?\(number "([^"]+)"', symtext, re.S)}


# connettori dalla libreria personale MIKILAB (simbolo e footprint EasyEDA con i pad di montaggio come pin 31/32 e 29/30)
FH12_ID, C22, FH12_FP = mik("FH12-30S-0.5SH")
FPC_ID, C28, FPC_FP = mik("FPC-05F-28PH20")
RES = extract("Device", "R")

FONT = "(effects (font (size 1.27 1.27)) (justify {j}))"
items = []
hier = []  # (nome, direzione)


def prop(name, val, x, y, hide=False, ang=0):
    h = " (hide yes)" if hide else ""
    return f'(property "{name}" "{val}" (at {x:.2f} {y:.2f} {ang}){h} (effects (font (size 1.27 1.27))))'


def symbol(lib_id, ref, val, fp, x, y, pins, extra=""):
    pl = " ".join(f'(pin "{p}" (uuid "{U()}"))' for p in pins)
    items.append(
        f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1) (body_style 1) (exclude_from_sim no) '
        f'(in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (uuid "{U()}") '
        f'{prop("Reference", ref, x + 3.81, y - 1.27)} {prop("Value", val, x + 3.81, y + 1.27, ang=90 if ref.startswith("J") else 0)} '
        f'{prop("Footprint", fp, x, y, True)} {prop("Datasheet", "", x, y, True)} {prop("Description", "", x, y, True)} {extra} '
        f'{pl} (instances (project "{PROJ}" (path "{PATH}" (reference "{ref}") (unit 1)))))')


def wire(x1, y1, x2, y2):
    items.append(f'(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')


GLOBAL = {"GND_D", "GND_A"}


def label(name, x, y, ang, direction="bidirectional"):
    j = "right" if ang == 180 else "left"
    if name in GLOBAL:
        items.append(f'(global_label "{name}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) '
                     f'{FONT.format(j=j)} (uuid "{U()}"))')
    elif name.startswith(("MAIN_", "PWR_")) or name in HIER_EXTRA:
        items.append(f'(hierarchical_label "{name}" (shape {direction}) (at {x:.2f} {y:.2f} {ang}) '
                     f'{FONT.format(j=j)} (uuid "{U()}"))')
        if name not in [h[0] for h in hier]:
            hier.append((name, direction))
    else:
        items.append(f'(label "{name}" (at {x:.2f} {y:.2f} {ang}) {FONT.format(j=j + " bottom")} (uuid "{U()}"))')


def text(s, x, y):
    s = s.replace('"', "'")
    items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) {FONT.format(j="left bottom")} (uuid "{U()}"))')


HIER_EXTRA = {"VREF_ENABLE", "VBIAS_ENABLE", "DAC61402_FAULT", "BUS_3V3", "VIN_SYS"}
OUT, IN = "output", "input"
DIR = {"MAIN_SPI_MISO": OUT, "MAIN_SPI_ALERT_N": OUT, "PWR_SPI_MISO": OUT, "DAC61402_FAULT": OUT,
       "MAIN_I2C_SDA": "bidirectional", "MAIN_I2C_SCL": "bidirectional", "BUS_3V3": "passive", "VIN_SYS": "passive"}

# MAIN 28 pin, BPS-MIKILAB-2026-REV5.1 (pin 28 = HIT#; scheda RK3568 = J_OUT, testa della catena)
MAIN = {1: "GND_D", 2: "BUS_5V", 3: "BUS_3V3", 4: "GND_D", 5: "BUS_2V5_REF", 6: "BUS_1V25_REF", 7: "GND_A",
        8: "BUS_VBIAS_1", 9: "BUS_VBIAS_2", 10: "GND_D", 11: "MAIN_SPI_SCLK", 12: "MAIN_SPI_MOSI",
        13: "MAIN_SPI_MISO", 14: "MAIN_I2C_SDA", 15: "MAIN_I2C_SCL", 16: "GND_D", 17: "MAIN_SPI_CS_MASTER",
        18: "MAIN_SPI_ADDR_0", 19: "MAIN_SPI_ADDR_1", 20: "MAIN_SPI_ADDR_2", 21: "MAIN_SPI_PREFIX_0",
        22: "MAIN_SPI_PREFIX_1", 23: "MAIN_SPI_PREFIX_2", 24: "MAIN_SPI_ALERT_N", 25: "SPI_ID_0",
        26: "SPI_ID_1", 27: "SPI_ID_2", 28: "MAIN_HIT_N", "MP": "GND_D"}
# BUS_POWER_MIKILAB 22 pin (pinout di Michele)
PWR = {1: "GND_A", 2: "BUS_VBIAS_1", 3: "BUS_VBIAS_2", 4: "GND_A", 5: "BUS_2V5_REF", 6: "BUS_1V25_REF",
       7: "GND_A", 8: "BUS_5V", 9: "BUS_3V3", 10: "GND_D", 11: "PWR_SPI_SCLK", 12: "PWR_SPI_MOSI",
       13: "PWR_SPI_MISO", 14: "GND_D", 15: "PWR_SPI_INA239A_CS", 16: "PWR_SPI_INA239B_CS",
       17: "PWR_SPI_DAC_CS", 18: "VREF_ENABLE", 19: "VBIAS_ENABLE", 20: "DAC61402_FAULT", 21: "GND_D",
       22: "GND_D", 23: "GND_D", 24: "VIN_SYS", 25: "VIN_SYS", 26: "VIN_SYS", 27: "GND_D", 28: "GND_D",
       29: "BUS_3V3", 30: "GND_D", "MP": "GND_D"}


def place_conn(lib_id, symtext, ref, val, fp, x, y, netmap, npin):
    p = pins_of(symtext)
    symbol(lib_id, ref, val, fp, x, y, list(p))
    for n, (px, py) in p.items():
        ax, ay = x + px, y - py
        n = "MP" if n == "MP" or int(n) > npin else n   # pin oltre npin = pad di montaggio
        net = netmap[int(n) if n != "MP" else n]
        if n == "MP":                                # pad di montaggio: filo verso l'esterno del simbolo
            d = -7.62 if py > 0 else 7.62
            wire(ax, ay, ax, ay + d)
            label(net, ax, ay + d, 90 if d > 0 else 270)
        else:
            L = 20.32 if net in GLOBAL else 7.62
            wire(ax, ay, ax - L, ay)
            label(net, ax - L, ay, 180, DIR.get(net, IN))


place_conn(FH12_ID, C22, "J1", "BUS_POWER_MIKILAB", FH12_FP, 86.36, 86.36, PWR, 30)
place_conn(FPC_ID, C28, "J2", "BUS_MIKILAB_MAIN", FPC_FP, 182.88, 86.36, MAIN, 28)

# ID iniziale 000 su J_OUT: SPI_ID_0..2 a massa tramite 0 ohm; ponte GND_A-GND_D apribile
for i, (ref, top, bot) in enumerate([("R1", "SPI_ID_0", "GND_D"), ("R2", "SPI_ID_1", "GND_D"),
                                     ("R3", "SPI_ID_2", "GND_D"), ("R4", "GND_A", "GND_D")]):
    x, y = 228.6 + i * 12.7, 76.2
    symbol("Device:R", ref, "0R", "Resistor_SMD:R_0603_1608Metric", x, y, ["1", "2"])
    wire(x, y - 3.81, x, y - 8.89); label(top, x, y - 8.89, 90 if top not in GLOBAL else 270)
    wire(x, y + 3.81, x, y + 8.89); label(bot, x, y + 8.89, 90)

text("J1 BUS_POWER 30 pin (Hirose FH12-30S): pin 1-22 come J3 del modulo Power, 24-26 VIN_SYS 12 V, 29 secondo 3V3. Rail BUS_* passanti verso J2, non collegati ai rail della scheda.", 25.4, 25.4)
text("VIN_SYS -> buck TPS56637 12->5 V (foglio Alimentazione), senza eFuse. BUS_5V va solo a J2 pin 2.", 25.4, 30.48)
text("J2 MAIN 28 pin secondo BPS-MIKILAB-2026-REV5.1 (pin 28 = HIT#) (XUNPU FPC-05F-28PH20, LCSC C2856807; simbolo e footprint dalla libreria MIKILAB).", 25.4, 35.56)
text("Sul foglio CPU: BUS_POWER su SPI3_M1 e MAIN su SPI2_M1 (due controller separati) con 33R serie, 100R su ADDR/PREFIX, pull-up 4.7k su ALERT#/HIT#, 2.2k su I2C, 10k sui CS, ESD TPD4E05U06.", 25.4, 40.64)
text("R4 0R: ponte GND_A-GND_D, DNP di default (sul modulo Power GND_A e GND_D sono gia la stessa net). R1-R3: ID iniziale 000 (scheda = J_OUT, testa della catena).", 25.4, 45.72)

libsyms = "(lib_symbols " + C22 + C28 + RES + ")"
sch = (f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{SHEET_UUID}") '
       f'(paper "A3") {libsyms} ' + " ".join(items) + " (embedded_fonts no))")
open(f"{PRJ}/bus-mikilab.kicad_sch", "w").write(sch)

# Foglio radice: aggiunge il sotto-foglio con i pin gerarchici
root_path = f"{PRJ}/{PROJ}.kicad_sch"
root = open(root_path).read()
h = 5.08 + 2.54 * len(hier)
sx, sy, w = 152.4, 38.1, 50.8
pins = " ".join(
    f'(pin "{n}" {d} '
    f'(at {sx:.2f} {sy + 2.54 * (k + 1):.2f} 180) (uuid "{U()}") {FONT.format(j="left")})'
    for k, (n, d) in enumerate(hier))
extra = []
for k, (n, d) in enumerate(hier):
    py = sy + 2.54 * (k + 1)
    extra.append(f'(wire (pts (xy {sx:.2f} {py:.2f}) (xy {sx - 5.08:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
    extra.append(f'(label "{n}" (at {sx - 5.08:.2f} {py:.2f} 180) {FONT.format(j="right bottom")} (uuid "{U()}"))')
sheet = (f'(sheet (at {sx} {sy}) (size {w} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) '
         f'(fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{SHEET_UUID}") '
         f'(property "Sheetname" "Bus MIKILAB" (at {sx} {sy - 0.71:.2f} 0) {FONT.format(j="left bottom")}) '
         f'(property "Sheetfile" "bus-mikilab.kicad_sch" (at {sx} {sy + h + 0.58:.2f} 0) {FONT.format(j="left top")}) '
         f'{pins} (instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "3")))))')
i = root.rfind("\t(sheet_instances")
root = root[:i] + "\t" + sheet + "\n\t" + "\n\t".join(extra) + "\n" + root[i:]
open(root_path, "w").write(root)
print("hier:", len(hier), [n for n, _ in hier])
