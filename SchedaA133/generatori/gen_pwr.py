"""Foglio KiCad 10 'Alimentazione' della scheda A133 (VIN_SYS 12 V, jack 5 V, USB-C) e pin del foglio radice."""
import os
import re, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kilib import extract, pins

PRJ = sys.argv[1]
PROJ = "SchedaA133"
ROOT_UUID = "96743135-20e0-42f1-ba20-b9a0710e1ba3"
SHEET_UUID = str(uuid.uuid4())
PATH = f"/{ROOT_UUID}/{SHEET_UUID}"
U = lambda: str(uuid.uuid4())
F = "(effects (font (size 1.27 1.27)) (justify {j}))"
G = lambda v: round(v / 1.27) * 1.27


def custom(name, left, right, bottom, w=10.16):
    """Simbolo rettangolare: left/right = [(num, nome, tipo)], bottom = [(num, nome, tipo)]."""
    n = max(len(left), len(right))
    h = 2.54 * (n + 1)
    top = h / 2
    out = [f'(symbol "A133:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)',
           f'(property "Reference" "U" (at 0 {top + 1.27:.2f} 0) {F.format(j="left")})',
           f'(property "Value" "{name}" (at 0 {-top - 3.81:.2f} 0) {F.format(j="left")})',
           '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '(property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '(property "Description" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           f'(symbol "{name}_0_1" (rectangle (start {-w:.2f} {top:.2f}) (end {w:.2f} {-top:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))',
           f'(symbol "{name}_1_1"']
    pin = lambda t, x, y, a, nm, num: f'(pin {t} line (at {x:.2f} {y:.2f} {a}) (length 2.54) (name "{nm}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))'
    for i, (num, nm, t) in enumerate(left):
        out.append(pin(t, -w - 2.54, top - 2.54 * (i + 1), 0, nm, num))
    for i, (num, nm, t) in enumerate(right):
        out.append(pin(t, w + 2.54, top - 2.54 * (i + 1), 180, nm, num))
    for i, (num, nm, t) in enumerate(bottom):
        out.append(pin(t, 2.54 * i, -top - 2.54, 90, nm, num))
    out.append(") (embedded_fonts no))")
    return " ".join(out)


SYMS = {
    "A133:TPS56637": custom("TPS56637", [("8", "VIN", "power_in"), ("1", "EN", "input"), ("10", "MODE", "input"), ("5", "NC", "passive")],
                            [("6", "SW", "passive"), ("7", "BOOT", "passive"), ("2", "FB", "input"), ("4", "PG", "output")],
                            [("3", "AGND", "power_in"), ("9", "PGND", "power_in")]),
    "Power_Management:LM74700": extract("Power_Management", "LM74700"),
    "Transistor_FET:CSD17551Q5A": extract("Transistor_FET", "CSD17551Q5A"),
    "Interface_USB:FUSB302BMPX": extract("Interface_USB", "FUSB302BMPX"),
    "Connector:USB_C_Receptacle_USB2.0_16P": extract("Connector", "USB_C_Receptacle_USB2.0_16P"),
    "Connector:Barrel_Jack_Switch": extract("Connector", "Barrel_Jack_Switch"),
    "Device:Polyfuse": extract("Device", "Polyfuse"),
    "Device:D_TVS": extract("Device", "D_TVS"),
    "Device:C": extract("Device", "C"),
    "Device:R": extract("Device", "R"),
    "Device:L": extract("Device", "L"),
    "A133:TPS2121": custom("TPS2121",
                           [("7", "IN1", "power_in"), ("6", "PR1", "input"), ("5", "OV1", "input"),
                            ("2", "IN2", "power_in"), ("4", "OV2", "input"), ("3", "CP2", "input")],
                           [("1", "OUT", "power_out"), ("8", "OUT", "passive"), ("9", "ST", "output"),
                            ("10", "ILM", "passive"), ("11", "SS", "passive")],
                           [("12", "GND", "power_in")]),
    "A133:SY6280AAC": custom("SY6280AAC",
                             [("5", "IN", "power_in"), ("4", "EN", "input"), ("3", "ISET", "passive")],
                             [("1", "OUT", "power_out")], [("2", "GND", "power_in")], w=7.62),
}
PINS = {k: pins(v) for k, v in SYMS.items()}

GLOBAL = {"GND_D"}
HIER = {"VIN_SYS": "passive", "5V_SYS": "passive", "3V3_SYS": "passive", "USB0_DP": "bidirectional",
        "USB0_DM": "bidirectional", "PD_I2C_SDA": "bidirectional", "PD_I2C_SCL": "bidirectional",
        "PD_INT_N": "output", "VBUS_SRC_EN": "input", "PWR_SRC_ST": "output"}
items, hier = [], []


def label(net, x, y, ang):
    j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
    if net in GLOBAL:
        items.append(f'(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) {F.format(j=j)} (uuid "{U()}"))')
    elif net in HIER:
        items.append(f'(hierarchical_label "{net}" (shape {HIER[net]}) (at {x:.2f} {y:.2f} {ang}) {F.format(j=j)} (uuid "{U()}"))')
        if net not in hier:
            hier.append(net)
    else:
        items.append(f'(label "{net}" (at {x:.2f} {y:.2f} {ang}) {F.format(j=j + " bottom")} (uuid "{U()}"))')


def place(lib_id, ref, val, fp, x, y, nets, rot=0, dnp=False, extra_props=()):
    m = re.match(r"([A-Z]+)(\d+)$", ref)
    ref = f"{m.group(1)}{100 + int(m.group(2))}"  # serie 1xx: foglio Alimentazione
    x, y = G(x), G(y)
    seen = set()
    pl = []
    for num, nm, px, py, a, typ in PINS[lib_id]:
        pl.append(f'(pin "{num}" (uuid "{U()}"))')
        if rot == 90:  # rotazione antioraria di 90 gradi (componenti a due pin orizzontali)
            px, py, a = -py, px, (a + 90) % 360
        ax, ay = round(x + px, 2), round(y - py, 2)
        if (ax, ay) in seen:
            continue
        seen.add((ax, ay))
        net = nets.get(num, nets.get(nm, "NC"))
        dx, dy, la = {0: (-1, 0, 180), 180: (1, 0, 0), 90: (0, 1, 270), 270: (0, -1, 90)}[a]
        if net == "NC":
            items.append(f'(no_connect (at {ax:.2f} {ay:.2f}) (uuid "{U()}"))')
            continue
        ex, ey = ax + dx * 2.54, ay + dy * 2.54
        items.append(f'(wire (pts (xy {ax:.2f} {ay:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        label(net, ex, ey, la)
    big = not lib_id.startswith("Device:")
    maxpy = max(p[3] for p in PINS[lib_id])
    fx, fy = (x - 7.62, y - maxpy - 5.08) if big else (x + 2.54, y + 1.27)
    props = "".join(f' (property "{k}" "{v}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))' for k, v in extra_props)
    items.append(
        f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot}) (unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}") '
        f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
        f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
        f'(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
        f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
        f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
        + " ".join(pl) + f' (instances (project "{PROJ}" (path "{PATH}" (reference "{ref}") (unit 1)))))')


def text(s, x, y):
    items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')


R0603, C0603, C0805, C1206 = "Resistor_SMD:R_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric", "Capacitor_SMD:C_1206_3216Metric"
R = lambda ref, val, x, y, a, b, **k: place("Device:R", ref, val, R0603, x, y, {"1": a, "2": b}, **k)
C = lambda ref, val, x, y, a, b, fp=C0603: place("Device:C", ref, val, fp, x, y, {"1": a, "2": b})

# --- 1. VIN_SYS 12 V -> fusibile -> TPS56637 6 A -> LM74700 + N-MOSFET -> 5V_EXT ----------------------
X, Y = 30, 70
text("1) VIN_SYS 12 V dal BUS_POWER (pin 24-26) -> F101 2.5 A -> buck TPS56637 12 -> 5 V / 6 A -> ideal diode LM74700 + CSD17551Q5A -> 5V_EXT", X, Y - 15)
place("Device:Polyfuse", "F1", "2.5A/24V", "Fuse:Fuse_1812_4532Metric", X, Y, {"1": "VIN_SYS", "2": "VIN_12V"})
C("C1", "10uF/25V", X + 12.7, Y, "VIN_12V", "GND_D", C1206)
C("C2", "10uF/25V", X + 22.86, Y, "VIN_12V", "GND_D", C1206)
C("C25", "100nF/50V", X + 33.02, Y, "VIN_12V", "GND_D")
R("R1", "169k 1%", X + 43.18, Y - 7.62, "VIN_12V", "BUCK_EN")
R("R2", "36.1k 1%", X + 43.18, Y + 7.62, "BUCK_EN", "GND_D")
place("A133:TPS56637", "U1", "TPS56637RPAR", "A133:Texas_RPA0010A_VQFN-HR-10_3x3mm", X + 75, Y,
      {"8": "VIN_12V", "1": "BUCK_EN", "2": "BUCK_FB", "10": "BUCK_MODE", "4": "BUCK_PG", "5": "NC", "7": "BUCK_BST",
       "6": "BUCK_SW", "3": "GND_D", "9": "GND_D"}, extra_props=(("MPN", "TPS56637RPAR"),))
R("R14", "10k", X + 60, Y + 25, "BUCK_MODE", "GND_D", dnp=True)
R("R15", "100k", X + 72, Y + 25, "5V_BUCK", "BUCK_PG")
C("C3", "100nF", X + 100, Y - 12, "BUCK_BST", "BUCK_SW")
place("Device:L", "L1", "3.3uH/8A", "Inductor_SMD:L_Coilcraft_XAL6030-XXX", X + 112, Y - 12, {"1": "BUCK_SW", "2": "5V_BUCK"}, extra_props=(("MPN", "XAL6030-332"),))
R("R3", "73.2k 1%", X + 124, Y - 5, "5V_BUCK", "BUCK_FB")
R("R4", "10k 1%", X + 124, Y + 12, "BUCK_FB", "GND_D")
R("R16", "20k", X + 134, Y - 12, "5V_BUCK", "BUCK_FF")
C("C26", "100pF", X + 134, Y + 2, "BUCK_FF", "BUCK_FB")
for i, ref in enumerate(["C4", "C5", "C27", "C28"]):
    C(ref, "22uF/10V", X + 144 + 10 * i, Y, "5V_BUCK", "GND_D", C1206)
place("Power_Management:LM74700", "U2", "LM74700-Q1", "Package_TO_SOT_SMD:SOT-23-6", X + 200, Y,
      {"ANODE": "5V_BUCK", "CATHODE": "5V_EXT", "GATE": "IDEAL_GATE", "VCAP": "IDEAL_VCAP", "EN": "5V_BUCK", "GND": "GND_D"}, extra_props=(("MPN", "LM74700QDBVRQ1"),))
C("C29", "100nF", X + 190, Y + 22, "IDEAL_VCAP", "5V_BUCK")
place("Transistor_FET:CSD17551Q5A", "Q1", "CSD17577Q5A", "Package_TO_SOT_SMD:TDSON-8-1", X + 220, Y - 22,
      {"S": "5V_BUCK", "G": "IDEAL_GATE", "D": "5V_EXT"}, extra_props=(("MPN", "CSD17577Q5A"),))
text("TPS56637 (tabella 4 del datasheet, Vout 5 V): Vfb 0.6 V, R103/R104 73.2k/10k = 4.99 V, L 3.3 uH, Cout 4x22 uF, feed-forward R116 20k + C126 100 pF.", X, Y + 38)
text("EN: 169k/36.1k (schema tipico TI). MODE libero = FCCM, R114 DNP per Eco-mode. Q101 N-MOSFET 30 V, Vgs +-20 V (il LM74700 pilota fino a 13 V).", X, Y + 43)

# --- 2. Jack DC 5 V sul nodo 5V_EXT ---------------------------------------------------------
X2, Y2 = 30, 120
text("2) Jack DC 5 V (DC-005-5A-2.0) sullo stesso nodo 5V_EXT, a valle dell'ideal diode", X2, Y2 - 12)
place("Connector:Barrel_Jack_Switch", "J3", "DC-005-5A-2.0", "Connector_BarrelJack:BarrelJack_Horizontal", X2, Y2,
      {"1": "5V_JACK", "2": "GND_D", "3": "GND_D"})
place("Device:Polyfuse", "F2", "4A/16V", "Fuse:Fuse_2920_7451Metric", X2 + 20, Y2, {"1": "5V_JACK", "2": "5V_EXT"})
place("Device:D_TVS", "D1", "SMBJ6.0CA", "Diode_SMD:D_SMB", X2 + 35, Y2, {"1": "5V_EXT", "2": "GND_D"}, rot=90)
C("C6", "22uF/10V", X2 + 47, Y2, "5V_EXT", "GND_D", C0805)

# --- 3. USB-C con FUSB302B, fusibile e TVS su VBUS ------------------------------------------
X3, Y3 = 30, 175
text("3) USB-C (HRO TYPE-C-31-M-12): solo USB 2.0, FUSB302B per CC/PD, fusibile 3 A e TVS su VBUS", X3, Y3 - 28)
place("Connector:USB_C_Receptacle_USB2.0_16P", "J4", "TYPE-C-31-M-12", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", X3, Y3,
      {"VBUS": "VBUS_CONN", "CC1": "USBC_CC1", "CC2": "USBC_CC2", "D+": "USB0_DP", "D-": "USB0_DM",
       "SBU1": "NC", "SBU2": "NC", "GND": "GND_D", "SHIELD": "GND_D"})
place("Device:D_TVS", "D2", "SMBJ6.0CA", "Diode_SMD:D_SMB", X3 + 30, Y3 - 10, {"1": "VBUS_CONN", "2": "GND_D"}, rot=90)
place("Device:Polyfuse", "F3", "3A/16V", "Fuse:Fuse_1812_4532Metric", X3 + 42, Y3 - 10, {"1": "VBUS_CONN", "2": "VBUS"}, extra_props=(("MPN", "1812L300/16"),))
C("C7", "4.7uF/10V", X3 + 54, Y3 - 10, "VBUS", "GND_D")
place("Interface_USB:FUSB302BMPX", "U4", "FUSB302BMPX", "Package_DFN_QFN:WQFN-14-1EP_2.5x2.5mm_P0.5mm_EP1.45x1.45mm", X3 + 90, Y3,
      {"CC1": "USBC_CC1", "CC2": "USBC_CC2", "VBUS": "VBUS", "VDD": "3V3_SYS", "VCONN": "NC", "INT_N": "PD_INT_N",
       "SCL": "PD_I2C_SCL", "SDA": "PD_I2C_SDA", "GND": "GND_D"})
C("C8", "1uF", X3 + 112, Y3 - 12, "3V3_SYS", "GND_D")
C("C9", "100nF", X3 + 122, Y3 - 12, "3V3_SYS", "GND_D")
text("FUSB302B: pull-up I2C 2.2k e INT_N 10k sul foglio CPU (I2C condivisa). VCONN non usato: verificare sul datasheet se lasciarlo libero.", X3, Y3 + 32)

# --- 4. TPS2121: IN1 = 5V_EXT (priorita), IN2 = VBUS -> 5V_SYS verso AXP707 ------------------
X4, Y4 = 215, 70
text("4) Power mux TPS2121: IN1 5V_EXT (jack o VIN_SYS) con priorita, IN2 VBUS USB-C. Uscita 5V_SYS verso AXP707 (VBUS/ACIN)", X4 - 10, Y4 - 25)
place("A133:TPS2121", "U3", "TPS2121RUXR", "Package_DFN_QFN:Texas_VQFN-HR-12_2x2.5mm_P0.5mm", X4 + 45, Y4,
      {"7": "5V_EXT", "6": "MUX_PR1", "5": "MUX_OV1", "2": "VBUS", "4": "MUX_OV2", "3": "GND_D",
       "1": "5V_SYS", "8": "5V_SYS", "9": "PWR_SRC_ST", "10": "MUX_ILM", "11": "MUX_SS", "12": "GND_D"})
R("R5", "32.4k 1%", X4, Y4 - 10, "5V_EXT", "MUX_PR1")
R("R6", "10k 1%", X4, Y4 + 5, "MUX_PR1", "GND_D")
R("R7", "46.4k 1%", X4 + 10, Y4 - 10, "5V_EXT", "MUX_OV1")
R("R8", "10k 1%", X4 + 10, Y4 + 5, "MUX_OV1", "GND_D")
R("R9", "46.4k 1%", X4 + 20, Y4 - 10, "VBUS", "MUX_OV2")
R("R10", "10k 1%", X4 + 20, Y4 + 5, "MUX_OV2", "GND_D")
R("R11", "22.1k 1%", X4 + 72, Y4 + 15, "MUX_ILM", "GND_D")
C("C10", "100nF", X4 + 82, Y4 + 15, "MUX_SS", "GND_D")
C("C11", "1uF/10V", X4 + 5, Y4 + 25, "5V_EXT", "GND_D")
C("C12", "1uF/10V", X4 + 15, Y4 + 25, "VBUS", "GND_D")
C("C13", "22uF/10V", X4 + 92, Y4 + 15, "5V_SYS", "GND_D", C0805)
C("C14", "1uF/10V", X4 + 102, Y4 + 15, "5V_SYS", "GND_D")
text("PR1: IN1 sotto 4.49 V -> passa a IN2. OV1/OV2: canale escluso sopra 5.98 V. CP2 a GND (modo VREF). ILM 22.1k -> 4-5 A. SS 100 nF.", X4 - 10, Y4 + 38)

# --- 5. SY6280AAC: VBUS in uscita (modo source), solo con alimentazione esterna -------------
X5, Y5 = 215, 145
text("5) SY6280AAC: VBUS in uscita verso una periferica (source, ~1 A). Ingresso da 5V_EXT: si accende solo con jack o VIN_SYS presenti", X5 - 10, Y5 - 15)
place("A133:SY6280AAC", "U5", "SY6280AAC", "Package_TO_SOT_SMD:SOT-23-5", X5 + 30, Y5,
      {"5": "5V_EXT", "4": "VBUS_SRC_EN", "3": "SRC_ISET", "1": "VBUS", "2": "GND_D"})
R("R12", "6.8k 1%", X5 + 10, Y5 + 12, "SRC_ISET", "GND_D")
R("R13", "100k", X5, Y5 + 12, "VBUS_SRC_EN", "GND_D")
C("C15", "10uF/10V", X5 + 50, Y5 + 5, "5V_EXT", "GND_D", C0805)
text("Ilim = 6800 / R112 = 1 A. R113: uscita spenta finche Linux non abilita VBUS_SRC_EN (comandato da tcpm).", X5 - 10, Y5 + 28)

lib = "(kicad_symbol_lib (version 20251024) (generator \"kicad_symbol_editor\") (generator_version \"10.0\") " + " ".join(
    v.replace(f'(symbol "{k}"', f'(symbol "{k.split(":")[1]}"', 1) for k, v in SYMS.items() if k.startswith("A133:")) + ")"
open(f"{PRJ}/A133.kicad_sym", "w").write(lib)
open(f"{PRJ}/sym-lib-table", "w").write('(sym_lib_table (version 7) (lib (name "A133") (type "KiCad") (uri "${KIPRJMOD}/A133.kicad_sym") (options "") (descr "Simboli della scheda A133")))')
libsyms = "(lib_symbols " + " ".join(SYMS.values()) + ")"
open(f"{PRJ}/alimentazione.kicad_sch", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{SHEET_UUID}") (paper "A3") '
    + libsyms + " " + " ".join(items) + " (embedded_fonts no))")

# Foglio radice: blocco del foglio, pin con etichette locali (cosi VIN_SYS si unisce al foglio Bus)
root_path = f"{PRJ}/{PROJ}.kicad_sch"
root = open(root_path).read()
sx, sy, w = 38.1, 101.6, 50.8
h = 5.08 + 2.54 * len(hier)
pinlist, extra = [], []
for k, n in enumerate(hier):
    py = sy + 2.54 * (k + 1)
    pinlist.append(f'(pin "{n}" {HIER[n]} (at {sx + w:.2f} {py:.2f} 0) (uuid "{U()}") {F.format(j="right")})')
    extra.append(f'(wire (pts (xy {sx + w:.2f} {py:.2f}) (xy {sx + w + 5.08:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
    extra.append(f'(label "{n}" (at {sx + w + 5.08:.2f} {py:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')
sheet = (f'(sheet (at {sx} {sy}) (size {w} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
         f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{SHEET_UUID}") '
         f'(property "Sheetname" "Alimentazione" (at {sx} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
         f'(property "Sheetfile" "alimentazione.kicad_sch" (at {sx} {sy + h + 0.58:.2f} 0) {F.format(j="left top")}) '
         + " ".join(pinlist) + f' (instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "4")))))')
i = root.rfind("\t(sheet_instances")
root = root[:i] + "\t" + sheet + "\n\t" + "\n\t".join(extra) + "\n" + root[i:]
open(root_path, "w").write(root)
print("hier:", hier)
