"""Foglio KiCad 10 'Alimentazione' della scheda RK3568 (VIN_SYS 12 V, jack 5 V, USB-C) e pin del foglio radice."""
import os
import re, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kilib import extract, pins, PROJ, ROOT_UUID, LIBNAME, mik

PRJ = sys.argv[1]
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
    out = [f'(symbol "Scheda:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)',
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
    "Power_Protection:TPD2EUSB30A": extract("Power_Protection", "TPD2EUSB30A"),
    "Interface_USB:FUSB302BMPX": extract("Interface_USB", "FUSB302BMPX"),
    "Connector:Barrel_Jack_Switch": extract("Connector", "Barrel_Jack_Switch"),
    "Device:D_TVS": extract("Device", "D_TVS"),
    "Device:C": extract("Device", "C"),
    "Connector:TestPoint": extract("Connector", "TestPoint"),
    "Device:R": extract("Device", "R"),
    "Device:L": extract("Device", "L"),
}
# componenti specifici dalla libreria personale MIKILAB (simbolo + footprint EasyEDA, numeri dei pin = pad)
MK = {}
for part in ("TPS56637RPAR", "TPS2121RUXR", "SY6280AAC", "TYPE-C-31-M-12"):
    lid, txt, fp = mik(part)
    SYMS[lid] = txt
    MK[part] = (lid, fp)
PINS = {k: pins(v) for k, v in SYMS.items()}

GLOBAL = {"GND_D"}
HIER = {"VIN_SYS": "passive", "5V_SYS": "passive", "VCC3V3_SYS": "passive", "USB0_DP": "bidirectional",
        "USB0_DM": "bidirectional", "I2C1_SDA": "bidirectional", "I2C1_SCL": "bidirectional",
        "PD_INT_N": "output", "VBUS_SRC_EN": "input", "PWR_SRC_ST": "output", "OTG_VBUSDET": "output"}
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
        f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot}) (unit 1) (body_style 1) (exclude_from_sim no) (in_bom {"no" if lib_id == "Connector:TestPoint" else "yes"}) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}") '
        f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
        f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
        f'(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
        f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
        f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
        + " ".join(pl) + f' (instances (project "{PROJ}" (path "{PATH}" (reference "{ref}") (unit 1)))))')


def text(s, x, y):
    items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')


R0603, C0603, C0805, C1206 = "Resistor_SMD:R_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric", "Capacitor_SMD:C_1206_3216Metric"
R = lambda ref, val, x, y, a, b, **k: place("Device:R", ref, val, R0603, x, y, {"1": a, "2": b}, **k)
C = lambda ref, val, x, y, a, b, fp=None: place("Device:C", ref, val, fp or (C0603 if val.startswith(("22u", "10u", "4.7u")) else "Capacitor_SMD:C_0402_1005Metric"), x, y, {"1": a, "2": b})

# --- 1. VIN_SYS 12 V -> TPS56637 6 A -> 5V_BUCK (eFuse tolto su richiesta di Michele) ------------------
X, Y = 30, 70
text("1) VIN_SYS 12 V dal BUS_POWER (pin 24-26) -> buck TPS56637 12 -> 5 V / 6 A -> 5V_BUCK -> TPS2121 U108 (IN1, priorita). Niente eFuse e niente fusibile.", X, Y - 22)
X = X + 45
C("C1", "10uF/25V", X + 12.7, Y, "VIN_SYS", "GND_D", C1206)
C("C2", "10uF/25V", X + 22.86, Y, "VIN_SYS", "GND_D", C1206)
C("C25", "100nF/50V", X + 33.02, Y, "VIN_SYS", "GND_D")
R("R1", "169k 1%", X + 43.18, Y - 7.62, "VIN_SYS", "BUCK_EN")
R("R2", "36.1k 1%", X + 43.18, Y + 7.62, "BUCK_EN", "GND_D")
place(*MK["TPS56637RPAR"][:1], "U1", "TPS56637RPAR", MK["TPS56637RPAR"][1], X + 75, Y,
      {"8": "VIN_SYS", "1": "BUCK_EN", "2": "BUCK_FB", "10": "BUCK_MODE", "4": "BUCK_PG", "5": "NC", "7": "BUCK_BST",
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
text("TPS56637 (tabella 4 del datasheet, Vout 5 V): Vfb 0.6 V, R103/R104 73.2k/10k = 4.99 V, L 3.3 uH, Cout 4x22 uF, feed-forward R116 20k + C126 100 pF.", X - 45, Y + 38)
text("EN: 169k/36.1k (schema tipico TI). MODE libero = FCCM (R114 DNP): frequenza fissa, ripple basso vicino al GNSS. Il jack e' separato dal TPS2121 U108, niente corrente inversa nel buck.", X - 45, Y + 43)
text("Senza eFuse il buck vede direttamente il BUS_POWER: niente limite di corrente, UVLO/OVLO e blocco inverso sui 12 V (protezione a carico del modulo Power).", X - 45, Y + 48)

# --- 2. Jack DC 5 V e secondo TPS2121 (U108): IN1 = 5V_BUCK con priorita, IN2 = jack -> 5V_EXT ---------
X2, Y2 = 30, 130
text("2) Jack DC 5 V (DC-005-5A-2.0) su 5V_JACK, TVS D101, nessun fusibile. TPS2121 U108: IN1 = 5V_BUCK (bus 12 V) con priorita, IN2 = jack. Uscita 5V_EXT -> IN1 di U103.", X2, Y2 - 12)
place("Connector:Barrel_Jack_Switch", "J3", "DC-005-5A-2.0", "Connector_BarrelJack:BarrelJack_Horizontal", X2, Y2,
      {"1": "5V_JACK", "2": "GND_D", "3": "GND_D"})
place("Device:D_TVS", "D1", "SMF5.0A", "Diode_SMD:D_SMF", X2 + 20, Y2, {"1": "5V_JACK", "2": "GND_D"}, rot=90)
C("C6", "22uF/10V", X2 + 32, Y2, "5V_JACK", "GND_D", C0805)
place(MK["TPS2121RUXR"][0], "U8", "TPS2121RUXR", MK["TPS2121RUXR"][1], X2 + 95, Y2 + 5,
      {"7": "5V_BUCK", "6": "MUX2_PR1", "5": "MUX2_OV1", "2": "5V_JACK", "4": "MUX2_OV2", "3": "GND_D",
       "1": "5V_EXT", "8": "5V_EXT", "9": "MUX2_ST", "10": "MUX2_ILM", "11": "MUX2_SS", "12": "GND_D"}, extra_props=(("MPN", "TPS2121RUXR"),))
R("R21", "32.4k 1%", X2 + 45, Y2 - 5, "5V_BUCK", "MUX2_PR1")
R("R22", "10k 1%", X2 + 45, Y2 + 10, "MUX2_PR1", "GND_D")
R("R23", "46.4k 1%", X2 + 55, Y2 - 5, "5V_BUCK", "MUX2_OV1")
R("R24", "10k 1%", X2 + 55, Y2 + 10, "MUX2_OV1", "GND_D")
R("R25", "46.4k 1%", X2 + 65, Y2 - 5, "5V_JACK", "MUX2_OV2")
R("R26", "10k 1%", X2 + 65, Y2 + 10, "MUX2_OV2", "GND_D")
R("R27", "22.1k 1%", X2 + 125, Y2 + 15, "MUX2_ILM", "GND_D")
C("C32", "100nF", X2 + 135, Y2 + 15, "MUX2_SS", "GND_D")
C("C33", "1uF/10V", X2 + 50, Y2 + 25, "5V_BUCK", "GND_D")
C("C34", "1uF/10V", X2 + 60, Y2 + 25, "5V_JACK", "GND_D")
C("C35", "10uF/10V", X2 + 145, Y2 + 15, "5V_EXT", "GND_D", C0805)
R("R28", "100k", X2 + 155, Y2 + 15, "5V_EXT", "MUX2_ST")
place("Connector:TestPoint", "TP1", "MUX2_ST", "TestPoint:TestPoint_Pad_D1.0mm", X2 + 165, Y2 + 5, {"1": "MUX2_ST"})
text("U108 (datasheet TPS2121 SLVSEA3F): PR1 = 1.06 V x (32.4k+10k)/10k = 4.49 V -> sotto passa al jack; CP2 a GND = priorita fissa su IN1; OV 5.98 V; ILM 22.1k = 4-5 A; ST (basso = uscita dal jack, IN2) con 100k e test point TP101.", X2, Y2 + 38)
text("Priorita: bus 12 V (buck) > jack > USB-C. Il bus e' l'alimentazione di esercizio, il jack serve al banco, l'USB-C e' l'ultima risorsa (1.5-3 A).", X2, Y2 + 43)

# --- 3. USB-C con FUSB302B, fusibile e TVS su VBUS ------------------------------------------
X3, Y3 = 30, 175
text("3) USB-C (HRO TYPE-C-31-M-12): solo USB 2.0, FUSB302B per CC/PD, TVS SMF5.0A su VBUS (nessun fusibile), ESD TPD2EUSB30A su CC1/CC2", X3, Y3 - 28)
place(MK["TYPE-C-31-M-12"][0], "J4", "TYPE-C-31-M-12", MK["TYPE-C-31-M-12"][1], X3, Y3,
      {"VBUS": "VBUS", "CC1": "USBC_CC1", "CC2": "USBC_CC2", "DP1": "USB0_DP", "DP2": "USB0_DP", "DN1": "USB0_DM", "DN2": "USB0_DM",
       "SBU1": "NC", "SBU2": "NC", "GND": "GND_D", "EH": "GND_D"})
place("Device:D_TVS", "D2", "SMF5.0A", "Diode_SMD:D_SMF", X3 + 30, Y3 - 10, {"1": "VBUS", "2": "GND_D"}, rot=90)
place("Power_Protection:TPD2EUSB30A", "U7", "TPD2EUSB30ADRTR", "Package_TO_SOT_SMD:Texas_DRT-3", X3 + 45, Y3 + 20, {"D+": "USBC_CC1", "D-": "USBC_CC2", "GND": "GND_D"}, extra_props=(("MPN", "TPD2EUSB30ADRTR"),))
C("C7", "4.7uF/10V", X3 + 54, Y3 - 10, "VBUS", "GND_D")
place("Interface_USB:FUSB302BMPX", "U4", "FUSB302BMPX", "Package_DFN_QFN:WQFN-14-1EP_2.5x2.5mm_P0.5mm_EP1.45x1.45mm", X3 + 90, Y3,
      {"CC1": "USBC_CC1", "CC2": "USBC_CC2", "VBUS": "VBUS", "VDD": "VCC3V3_SYS", "VCONN": "NC", "INT_N": "PD_INT_N",
       "SCL": "I2C1_SCL", "SDA": "I2C1_SDA", "GND": "GND_D"})
C("C8", "1uF", X3 + 112, Y3 - 12, "VCC3V3_SYS", "GND_D")
C("C9", "100nF", X3 + 122, Y3 - 12, "VCC3V3_SYS", "GND_D")
R("R29", "10k 1%", X3 + 140, Y3 - 12, "VBUS", "OTG_VBUSDET")
R("R30", "15k 1%", X3 + 140, Y3 + 3, "OTG_VBUSDET", "GND_D")
C("C36", "100nF", X3 + 150, Y3 + 3, "OTG_VBUSDET", "GND_D")
text("USB3_OTG0_VBUSDET (M24): VBUS x 15k/(10k+15k) = 3.0 V con 100 nF (Hardware Design Guide RK3568: 2.7-3.3 V, tip. 3.0 V). Serve al flash con rkdeveloptool (modo device).", X3, Y3 + 37)
text("FUSB302B (0x22): VDD da VCC3V3_SYS, I2C1 dell'RK3568 (GPIO0_B3/B4, PMUIO2 3.3 V) con pull-up 2.2k a VCC3V3_PMU e INT_N 10k a VCC_3V3 sul foglio CPU.", X3, Y3 + 32)

# --- 4. TPS2121: IN1 = 5V_EXT (priorita), IN2 = VBUS -> 5V_SYS verso AXP313A ------------------
X4, Y4 = 215, 70
text("4) Power mux TPS2121 U103: IN1 5V_EXT (uscita di U108: bus o jack) con priorita, IN2 VBUS USB-C. Uscita 5V_SYS verso TPS563201 (VCC3V3_SYS), TCS4525 (VDD_CPU) e TPS2553", X4 - 10, Y4 - 25)
place(MK["TPS2121RUXR"][0], "U3", "TPS2121RUXR", MK["TPS2121RUXR"][1], X4 + 45, Y4,
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
place(MK["SY6280AAC"][0], "U5", "SY6280AAC", MK["SY6280AAC"][1], X5 + 30, Y5,
      {"5": "5V_EXT", "4": "VBUS_SRC_EN", "3": "SRC_ISET", "1": "VBUS", "2": "GND_D"})
R("R12", "6.8k 1%", X5 + 10, Y5 + 12, "SRC_ISET", "GND_D")
R("R13", "100k", X5, Y5 + 12, "VBUS_SRC_EN", "GND_D")
C("C15", "10uF/10V", X5 + 50, Y5 + 5, "5V_EXT", "GND_D", C0805)
text("Ilim = 6800 / R112 = 1 A. R113: uscita spenta finche Linux non abilita VBUS_SRC_EN (GPIO0_A5, comandato da tcpm).", X5 - 10, Y5 + 28)

lib = "(kicad_symbol_lib (version 20251024) (generator \"kicad_symbol_editor\") (generator_version \"10.0\") " + " ".join(
    v.replace(f'(symbol "{k}"', f'(symbol "{k.split(":")[1]}"', 1) for k, v in SYMS.items() if k.startswith("Scheda:")) + ")"
open(f"{PRJ}/{LIBNAME}.kicad_sym", "w").write(lib)
open(f"{PRJ}/sym-lib-table", "w").write('(sym_lib_table (version 7) (lib (name "Scheda") (type "KiCad") (uri "${KIPRJMOD}/Scheda.kicad_sym") (options "") (descr "Simboli della scheda RK3568")))')
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
