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



# ===================== Foglio PMIC: AXP717 (reference Allwinner A100_A133_B3_AXP707_LPDDR3, pag. 05) =====
AXP = custom("AXP717",
             [("49", "VBUS_1", "power_in"), ("50", "VBUS_2", "power_in"), ("47", "VMID_1", "power_out"), ("48", "VMID_2", "passive"),
              ("45", "SW_1", "passive"), ("46", "SW_2", "passive"), ("43", "VSYS_1", "power_out"), ("44", "VSYS_2", "passive"),
              ("41", "BAT_1", "passive"), ("42", "BAT_2", "passive"), ("39", "TS", "input"), ("38", "CHGLED", "output"),
              ("36", "BACKUP", "passive"), ("6", "PWRON", "input"), ("1", "PWROK", "output"), ("37", "IRQ", "output"),
              ("52", "SCK", "input"), ("51", "SDA", "bidirectional"), ("3", "DP", "bidirectional"), ("2", "DM", "bidirectional"),
              ("4", "CC1", "bidirectional"), ("5", "CC2", "bidirectional"), ("40", "DCDCEN", "output"), ("7", "VREF", "passive"),
              ("35", "VRTC", "power_out")],
             [("9", "VIN1", "power_in"), ("10", "LX1_1", "passive"), ("11", "LX1_2", "passive"), ("12", "FB1", "input"),
              ("32", "VIN2", "power_in"), ("33", "LX2", "passive"), ("34", "FB2", "input"),
              ("31", "VIN3", "power_in"), ("30", "LX3", "passive"), ("29", "FB3", "input"),
              ("15", "ALDOIN", "power_in"), ("13", "ALDO1", "power_out"), ("14", "ALDO2", "power_out"), ("16", "ALDO3", "power_out"), ("17", "ALDO4", "power_out"),
              ("20", "BLDOIN", "power_in"), ("18", "BLDO1", "power_out"), ("19", "BLDO2", "power_out"), ("21", "BLDO3", "power_out"), ("22", "BLDO4", "power_out"),
              ("25", "CLDOIN", "power_in"), ("23", "CLDO1", "power_out"), ("24", "CLDO2", "power_out"), ("26", "CLDO3", "power_out"), ("27", "CLDO4", "power_out"),
              ("28", "CPUSLDO", "power_out")],
             [("8", "GND", "power_in"), ("53", "EPAD", "power_in")], w=15.24)

SYMS = {
    "A133:AXP717": AXP,
    "Regulator_Switching:TPS563201": extract("Regulator_Switching", "TPS563201"),
    "Regulator_Linear:AP2112K-3.3": extract("Regulator_Linear", "AP2112K-3.3"),
    "Device:Battery_Cell": extract("Device", "Battery_Cell"),
    "Switch:SW_Push": extract("Switch", "SW_Push"),
    "Device:C": extract("Device", "C"),
    "Device:R": extract("Device", "R"),
    "Device:L": extract("Device", "L"),
}
PINS = {k: pins(v) for k, v in SYMS.items()}

HIER_PMIC = {n: "passive" for n in [
    "5V_SYS", "VDD-CPU", "VDD-SYS", "VCC-DRAM", "VDD18-LPDDR", "VCC-PLL", "VCC-PE", "VCC-PL", "VCC-PG",
    "VCC-PC", "VCC-IO", "VCC-CARD", "VDD-CPUS", "VCC-RTC", "3V3_PERI"]}
HIER_PMIC.update({"VDD-CPUFB": "input", "VDD-SYSFB": "input", "VCC-DRAM-FB": "input", "PMU-SCK": "input",
                  "PMU-SDA": "bidirectional", "AP-NMI": "output", "AP-RESET": "output", "USB0_DP": "bidirectional",
                  "USB0_DM": "bidirectional"})
GLOBAL = {"GND_D"}
HIER = HIER_PMIC
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
    ref = f"{m.group(1)}{200 + int(m.group(2))}"  # serie 2xx: foglio PMIC
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


# --- AXP717 al centro --------------------------------------------------------------------------
X0, Y0 = 200, 150
text("PMIC AXP717 secondo il reference Allwinner A100_A133_B3_AXP707_LPDDR3 (pag. 05, che usa l'AXP717). Ingresso 5V_SYS dal TPS2121. Niente batteria.", 25, 25)
text("Net rinominate come nel reference. Alias: VCC-PLL = AVCC/VCC-PLL/VDD18-DRAM; VCC-PC = VCC-PC/VCC-EFUSE/CPVIN/VCC-LVDS (1.8 V, VCCQ eMMC);", 25, 30)
text("VCC-IO = VCC-IO/VCC-USB/VCC-PD/VCC-3V3 (3.3 V); VCC-CARD = VCC-CARD/VCC-NAND (microSD + VCC eMMC). LPDDR4: VDD2/VDDQ = VCC-DRAM 1.1 V, VDD1 = VDD18-LPDDR 1.8 V. Niente VPP (solo DDR4).", 25, 35)
place("A133:AXP717", "U1", "AXP717", "Package_DFN_QFN:VQFN-52-1EP_6x6mm_P0.4mm_EP4.7x4.7mm", X0, Y0, {
    "VBUS_1": "5V_SYS", "VBUS_2": "5V_SYS", "VMID_1": "VMID", "VMID_2": "VMID", "SW_1": "PMU_SW", "SW_2": "PMU_SW",
    "VSYS_1": "PS", "VSYS_2": "PS", "BAT_1": "VBAT", "BAT_2": "VBAT", "TS": "PMU_TS", "CHGLED": "NC",
    "BACKUP": "BACKUP", "PWRON": "PWRON", "PWROK": "AP-RESET", "IRQ": "AP-NMI", "SCK": "PMU-SCK", "SDA": "PMU-SDA",
    "DP": "PMU_DP", "DM": "PMU_DM", "CC1": "NC", "CC2": "NC", "DCDCEN": "DCDCEN", "VREF": "PMU_VREF", "VRTC": "VCC-RTC",
    "VIN1": "PS", "LX1_1": "LX1", "LX1_2": "LX1", "FB1": "VDD-CPUFB", "VIN2": "PS", "LX2": "LX2", "FB2": "VDD-SYSFB",
    "VIN3": "PS", "LX3": "LX3", "FB3": "VCC-DRAM-FB", "ALDOIN": "PS", "ALDO1": "ALDO1_NU", "ALDO2": "VCC-PE",
    "ALDO3": "VCC-PL", "ALDO4": "VCC-PLL", "BLDOIN": "PS", "BLDO1": "VCC-PG", "BLDO2": "VDD18-LPDDR",
    "BLDO3": "BLDO3_NU", "BLDO4": "BLDO4_NU", "CLDOIN": "PS", "CLDO1": "VCC-PC", "CLDO2": "CLDO2_NU",
    "CLDO3": "VCC-IO", "CLDO4": "CLDO4_NU", "CPUSLDO": "VDD-CPUS", "GND": "GND_D", "EPAD": "GND_D"})

# --- Ingresso, VMID, caricatore (SW -> VSYS) e BAT -----------------------------------------------
X1, Y1 = 25, 60
text("Ingresso VBUS = 5V_SYS, VMID, induttore del power-path SW -> VSYS (PS). BAT senza batteria: solo condensatori, caricatore da disabilitare in U-Boot.", X1, Y1 - 8)
C("C1", "10uF/16V", X1, Y1, "5V_SYS", "GND_D")
C("C2", "22uF/10V", X1 + 10, Y1, "VMID", "GND_D")
place("Device:L", "L1", "1.0uH/3A", "Inductor_SMD:L_1008_2520Metric", X1 + 22, Y1, {"1": "PMU_SW", "2": "PS"}, extra_props=(("MPN", "SML2520 1.0uH 3A"),))
C("C3", "22uF/10V", X1 + 34, Y1, "PS", "GND_D")
C("C4", "22uF/10V", X1 + 44, Y1, "PS", "GND_D")
C("C5", "4.7uF/10V", X1 + 54, Y1, "VBAT", "GND_D")
C("C6", "100nF", X1 + 64, Y1, "VBAT", "GND_D")
R("R1", "10k 1%", X1 + 74, Y1, "PMU_TS", "GND_D")
text("R201 su TS = NTC fittizio a 25 C, come RP45 del reference.", X1 + 70, Y1 + 12)

# --- Disaccoppiamento ingressi DCDC/LDO e riferimenti ---------------------------------------------
X2, Y2 = 25, 95
text("Condensatori degli ingressi VIN1-3 / ALDOIN / BLDOIN / CLDOIN vicini al PMIC, VREF, VRTC, CPUSLDO", X2, Y2 - 8)
for i, (ref, val, net) in enumerate([("C7", "1uF/10V", "PS"), ("C8", "1uF/10V", "PS"), ("C9", "1uF/10V", "PS"),
                                     ("C10", "1uF/10V", "PS"), ("C11", "1uF/10V", "PS"), ("C12", "1uF/10V", "PS"),
                                     ("C13", "1uF/10V", "PMU_VREF"), ("C14", "1uF/10V", "VCC-RTC"), ("C15", "2.2uF/6.3V", "VDD-CPUS")]):
    C(ref, val, X2 + 10 * i, Y2, net, "GND_D")

# --- DCDC1/2/3 --------------------------------------------------------------------------------
X3, Y3 = 25, 130
text("DCDC1 VDD-CPU 0.9-1.18 V 4 A, DCDC2 VDD-SYS/VDD-USB 0.95 V, DCDC3 VCC-DRAM 1.1 V (LPDDR4). FB con sense remoto: FB1/FB2 dalle sfere del SoC, FB3 vicino alla DRAM.", X3, Y3 - 8)
place("Device:L", "L2", "1.0uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", X3, Y3, {"1": "LX1", "2": "VDD-CPU"}, extra_props=(("MPN", "NR3020 1.0uH 4A"),))
C("C16", "22uF/10V", X3 + 10, Y3, "VDD-CPU", "GND_D")
C("C17", "22uF/10V", X3 + 20, Y3, "VDD-CPU", "GND_D")
place("Device:L", "L3", "1.0uH/3A", "Inductor_SMD:L_1008_2520Metric", X3 + 32, Y3, {"1": "LX2", "2": "VDD-SYS"}, extra_props=(("MPN", "SML2520 1.0uH 3A"),))
C("C18", "22uF/10V", X3 + 42, Y3, "VDD-SYS", "GND_D")
C("C19", "22uF/10V", X3 + 52, Y3, "VDD-SYS", "GND_D")
place("Device:L", "L4", "1.0uH/3A", "Inductor_SMD:L_1008_2520Metric", X3 + 64, Y3, {"1": "LX3", "2": "VCC-DRAM"}, extra_props=(("MPN", "SML2520 1.0uH 3A"),))
C("C20", "22uF/10V", X3 + 74, Y3, "VCC-DRAM", "GND_D")
C("C21", "22uF/10V", X3 + 84, Y3, "VCC-DRAM", "GND_D")

# --- Uscite LDO -------------------------------------------------------------------------------
X4, Y4 = 25, 170
text("LDO: ALDO2 VCC-PE 1.8 V, ALDO3 VCC-PL 3.3 V, ALDO4 VCC-PLL 1.8 V, BLDO1 VCC-PG 3.3 V (VCCIO-WIFI), BLDO2 VDD18-LPDDR 1.8 V, CLDO1 VCC-PC 1.8 V, CLDO3 VCC-IO 3.3 V.", X4, Y4 - 8)
text("Non usati (camera, LCD, touch, motore): ALDO1, BLDO3, BLDO4, CLDO2, CLDO4. Condensatore montato, uscita spenta da software.", X4, Y4 - 4)
for i, net in enumerate(["ALDO1_NU", "VCC-PE", "VCC-PL", "VCC-PLL", "VCC-PG", "VDD18-LPDDR", "BLDO3_NU", "BLDO4_NU",
                         "VCC-PC", "CLDO2_NU", "VCC-IO", "CLDO4_NU"]):
    C(f"C{22 + i}", "2.2uF/6.3V", X4 + 10 * i, Y4 + 5, net, "GND_D")

# --- LDO esterno 3.3 V per VCC-CARD / VCC-NAND (CLDO3 > 400 mA) ---------------------------------
X5, Y5 = 25, 215
text("LDO esterno 3.3 V per microSD ed eMMC (come U19 TCS2155-E33 del reference, qui AP2112K-3.3 stesso pinout SOT-23-5). EN da VCC-IO: parte dopo CLDO3.", X5, Y5 - 10)
place("Regulator_Linear:AP2112K-3.3", "U2", "AP2112K-3.3", "Package_TO_SOT_SMD:SOT-23-5", X5 + 30, Y5,
      {"VIN": "PS", "GND": "GND_D", "EN": "VCC-IO", "NC": "NC", "VOUT": "VCC-CARD"})
C("C34", "1uF/10V", X5, Y5, "PS", "GND_D")
C("C35", "1uF/10V", X5 + 55, Y5, "VCC-CARD", "GND_D")
C("C36", "10uF/10V", X5 + 65, Y5, "VCC-CARD", "GND_D", C0805)

# --- Controllo: PWRON, PWROK, IRQ, RSB, BC1.2, RTC ----------------------------------------------
X6, Y6 = 270, 60
text("Controllo verso l'A133: PMU-SCK/PMU-SDA = bus RSB (S_RSB), AP-NMI = NMI, AP-RESET = PWROK verso RESET del SoC, PWRON = tasto di accensione.", X6 - 10, Y6 - 12)
place("Switch:SW_Push", "SW1", "PWRON", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X6, Y6, {"1": "PWRON", "2": "GND_D"})
C("C37", "100nF", X6 + 15, Y6, "PWRON", "GND_D")
R("R2", "10k 1%", X6 + 25, Y6, "VCC-RTC", "AP-RESET")
R("R3", "10k 1%", X6 + 35, Y6, "VCC-RTC", "AP-NMI")
R("R4", "2k", X6 + 45, Y6, "VCC-PL", "PMU-SCK", dnp=True)
R("R5", "2k", X6 + 55, Y6, "VCC-PL", "PMU-SDA", dnp=True)
R("R6", "470R 1%", X6 + 70, Y6, "PMU_DP", "USB0_DP", dnp=True)
R("R7", "470R 1%", X6 + 80, Y6, "PMU_DM", "USB0_DM", dnp=True)
text("R204/R205 DNP: RSB non vuole pull-up (NC anche nel reference). R206/R207 DNP: rilevamento BC1.2 sul USB0, inutile con il FUSB302B.", X6 - 10, Y6 + 14)
place("Device:Battery_Cell", "BT1", "CR1220 (opz.)", "Battery:Battery_Panasonic_CR1220-VCN_Vertical_CircularHoles", X6 + 10, Y6 + 40, {"+": "RTC_BAT", "-": "GND_D", "1": "RTC_BAT", "2": "GND_D"}, dnp=True)
R("R8", "0R", X6 + 25, Y6 + 40, "RTC_BAT", "BACKUP", dnp=True)
C("C38", "100nF", X6 + 35, Y6 + 40, "BACKUP", "GND_D")
text("RTC: pila CR1220 opzionale DNP su BACKUP. Senza pila l'ora va presa dal GNSS/NTP.", X6 - 10, Y6 + 54)

# --- Buck 3V3_PERI per AP6256, RTL8211F e GNSS --------------------------------------------------
X7, Y7 = 270, 150
text("3V3_PERI: TPS563201 da 5V_SYS, 3.3 V / 3 A per AP6256 (VBAT), RTL8211F e NEO-F10T. Separato dalla 3V3 del bus. EN da DCDCEN del PMIC (stessa sequenza di CLDO2).", X7 - 10, Y7 - 22)
C("C39", "10uF/16V", X7 - 5, Y7, "5V_SYS", "GND_D", C0805)
C("C40", "100nF", X7 + 5, Y7, "5V_SYS", "GND_D")
place("Regulator_Switching:TPS563201", "U3", "TPS563201", "Package_TO_SOT_SMD:SOT-23-6", X7 + 30, Y7,
      {"VIN": "5V_SYS", "EN": "PERI_EN", "GND": "GND_D", "SW": "PERI_SW", "VBST": "PERI_BST", "VFB": "PERI_FB"})
R("R9", "0R", X7 + 15, Y7 + 15, "DCDCEN", "PERI_EN")
R("R10", "100k", X7 + 5, Y7 + 15, "5V_SYS", "PERI_EN", dnp=True)
C("C41", "100nF", X7 + 52, Y7 - 10, "PERI_BST", "PERI_SW")
place("Device:L", "L5", "2.2uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", X7 + 65, Y7 - 10, {"1": "PERI_SW", "2": "3V3_PERI"}, extra_props=(("MPN", "XAL4020-222"),))
R("R11", "33.2k 1%", X7 + 78, Y7 - 5, "3V3_PERI", "PERI_FB")
R("R12", "10k 1%", X7 + 78, Y7 + 10, "PERI_FB", "GND_D")
C("C42", "22uF/10V", X7 + 90, Y7, "3V3_PERI", "GND_D", C0805)
C("C43", "22uF/10V", X7 + 100, Y7, "3V3_PERI", "GND_D", C0805)
text("Vout = 0.768 V x (1 + R211/R212) = 3.32 V. R210 DNP: alternativa per accenderlo sempre da 5V_SYS se DCDCEN non va bene.", X7 - 10, Y7 + 30)

# --- Libreria di progetto: aggiunge AXP717 ------------------------------------------------------
libp = f"{PRJ}/A133.kicad_sym"
lib = open(libp).read()
if '(symbol "AXP717"' not in lib:
    lib = lib.rstrip()[:-1] + " " + AXP.replace('(symbol "A133:AXP717"', '(symbol "AXP717"', 1) + ")"
    open(libp, "w").write(lib)

libsyms = "(lib_symbols " + " ".join(SYMS.values()) + ")"
open(f"{PRJ}/pmic.kicad_sch", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{SHEET_UUID}") (paper "A3") '
    + libsyms + " " + " ".join(items) + " (embedded_fonts no))")

# --- Foglio radice: blocco PMIC con i pin a sinistra e etichette locali ---------------------------
root_path = f"{PRJ}/{PROJ}.kicad_sch"
root = open(root_path).read().replace('(paper "A4")', '(paper "A3")', 1)
sx, sy, w = 254.0, 38.1, 50.8
h = 5.08 + 2.54 * len(hier)
pinlist, extra = [], []
for k, n in enumerate(hier):
    py = sy + 2.54 * (k + 1)
    pinlist.append(f'(pin "{n}" {HIER[n]} (at {sx:.2f} {py:.2f} 180) (uuid "{U()}") {F.format(j="left")})')
    extra.append(f'(wire (pts (xy {sx:.2f} {py:.2f}) (xy {sx - 5.08:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
    extra.append(f'(label "{n}" (at {sx - 5.08:.2f} {py:.2f} 180) {F.format(j="right bottom")} (uuid "{U()}"))')
sheet = (f'(sheet (at {sx} {sy}) (size {w} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
         f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{SHEET_UUID}") '
         f'(property "Sheetname" "PMIC" (at {sx} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
         f'(property "Sheetfile" "pmic.kicad_sch" (at {sx} {sy + h + 0.58:.2f} 0) {F.format(j="left top")}) '
         + " ".join(pinlist) + f' (instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "5")))))')
i = root.rfind("\t(sheet_instances")
root = root[:i] + "\t" + sheet + "\n\t" + "\n\t".join(extra) + "\n" + root[i:]
open(root_path, "w").write(root)
print("hier:", len(hier), hier)
