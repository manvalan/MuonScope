"""Foglio KiCad 10 'Memorie' della scheda A133: LPDDR4 MT53E512M32D1ZW-046, eMMC Kingston EMMC256-IY29-5B101, microSD."""
import os
import json, re, sys, uuid
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kilib import extract, pins

PRJ = sys.argv[1]
PROJ = "SchedaA133"
ROOT_UUID = "96743135-20e0-42f1-ba20-b9a0710e1ba3"
SHEET_UUID = str(uuid.uuid4())
PATH = f"/{ROOT_UUID}/{SHEET_UUID}"
U = lambda: str(uuid.uuid4())
F = "(effects (font (size 1.27 1.27)) (justify {j}))"
G = lambda v: round(v / 1.27) * 1.27


def multi_symbol(libname, name, units_pins, desc, w=20.32):
    """units_pins: lista di unità, ognuna lista di (numero, nome); metà a sinistra, metà a destra."""
    sub, PINMAP = [], {}
    for uu, lst in enumerate(units_pins, start=1):
        half = (len(lst) + 1) // 2
        top = G(2.54 * (half + 1) / 2)
        body = [f'(symbol "{name}_{uu}_1" (rectangle (start {-w:.2f} {top:.2f}) (end {w:.2f} {-top - 2.54:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))']
        PINMAP[uu] = []
        for side, group in ((0, lst[:half]), (180, lst[half:])):
            for i, (num, nm) in enumerate(group):
                x = -w - 2.54 if side == 0 else w + 2.54
                y = top - 2.54 * (i + 1)
                body.append(f'(pin passive line (at {x:.2f} {y:.2f} {side}) (length 2.54) (name "{nm}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))')
                PINMAP[uu].append((num, nm, x, y, side))
        body.append(")")
        sub.append(" ".join(body))
    sym = (f'(symbol "{libname}:{name}" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no) '
           f'(property "Reference" "U" (at 0 2.54 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 0 0) (effects (font (size 1.27 1.27)))) '
           '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) (property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) '
           f'(property "Description" "{desc}" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) ' + " ".join(sub) + " (embedded_fonts no))")
    return sym, PINMAP


def natkey(t):
    m = re.match(r"([A-Z_]+?)(\d+)(.*)$", t[1])
    return (m.group(1), m.group(3), int(m.group(2))) if m else (t[1], "", 0)


# ---------------- LPDDR4 FBGA-200 (ball map dal reference Allwinner, pag. 08) ----------------------------
LB = json.load(open(f"{SC}/lpddr4_balls.json"))
sig = sorted([(b, n) for b, n in LB.items() if not re.match(r"(VDD|VSS|NC)", n)], key=natkey)
pwr = sorted([(b, n) for b, n in LB.items() if re.match(r"(VDD|VSS|NC)", n)], key=natkey)
LP_SYM, LP_PINS = multi_symbol("A133", "LPDDR4_FBGA200", [sig, pwr], "LPDDR4 x32 200 ball (JEDEC), es. Micron MT53E512M32D1ZW-046 IT:B")

# rimappatura del reference: CA/CS sul chip <- ball del SoC (net del reference -> porta DRAM_ del foglio CPU)
REFNET2PORT = {"SA0": "DRAM_A5", "SA1": "DRAM_A0", "SA2": "DRAM_A2", "SA3": "DRAM_A1", "SA4": "DRAM_CS0", "SA5": "DRAM_CS1",
               "SCS0": "DRAM_A4", "SCS1": "DRAM_A3", "SCKE0": "DRAM_CKE0", "SCKE1": "DRAM_CKE1", "SCKP": "DRAM_CKP",
               "SCKN": "DRAM_CKN", "SRST": "DRAM_RST"}
CHIP2REF = {}
for ch in "AB":
    for i in range(6):
        CHIP2REF[f"CA{i}_{ch}"] = f"SA{i}"
    CHIP2REF.update({f"CKE0_{ch}": "SCKE0", f"CKE1_{ch}": "SCKE1", f"CK_T_{ch}": "SCKP", f"CK_C_{ch}": "SCKN",
                     f"CS0_{ch}": "SCS0", f"CS1_{ch}": "SCS1"})
CHIP2REF["RESET-N"] = "SRST"
DQMAP = {"A": [14, 10, 15, 8, 9, 13, 12, 11, 7, 4, 2, 1, 0, 3, 5, 6], "B": [18, 19, 17, 16, 21, 20, 22, 23, 28, 30, 27, 25, 26, 31, 29, 24]}
STROBE = {("A", 0): 1, ("A", 1): 0, ("B", 0): 2, ("B", 1): 3}


def lp_net(n):
    if n in CHIP2REF:
        return REFNET2PORT[CHIP2REF[n]]
    m = re.match(r"DQ(\d+)_([AB])$", n)
    if m:
        return f"DRAM_DQ{DQMAP[m.group(2)][int(m.group(1))]}"
    m = re.match(r"DQS(\d)([PN])_([AB])$", n)
    if m:
        return f"DRAM_DQS{STROBE[(m.group(3), int(m.group(1)))]}{m.group(2)}"
    m = re.match(r"DM(\d)_([AB])$", n)
    if m:
        return f"DRAM_DQM{STROBE[(m.group(2), int(m.group(1)))]}"
    if n.startswith("VDD1"):
        return "VDD18-LPDDR"
    if n.startswith(("VDD2", "VDDQ")):
        return "VCC-DRAM"
    if n.startswith("VSS"):
        return "GND_D"
    if n.startswith("ODT_CA"):
        return "LP_ODT_" + n[-1]
    if n.startswith("ZQ"):
        return "LP_" + n
    return "NC"


# ---------------- eMMC FBGA-153 (pinout JEDEC eMMC 5.1) ---------------------------------------------------------
EMMC_BALLS = [("A3", "DAT0"), ("A4", "DAT1"), ("A5", "DAT2"), ("B2", "DAT3"), ("B3", "DAT4"), ("B4", "DAT5"), ("B5", "DAT6"),
              ("B6", "DAT7"), ("M5", "CMD"), ("M6", "CLK"), ("K5", "RST_n"), ("H5", "DS"), ("C2", "VDDI"),
              ("E6", "VCC"), ("F5", "VCC"), ("J10", "VCC"), ("K9", "VCC"), ("C6", "VCCQ"), ("M4", "VCCQ"), ("N4", "VCCQ"),
              ("P3", "VCCQ"), ("P5", "VCCQ"), ("E7", "VSS"), ("G5", "VSS"), ("H10", "VSS"), ("K8", "VSS"), ("C4", "VSSQ"),
              ("N2", "VSSQ"), ("N5", "VSSQ"), ("P4", "VSSQ"), ("P6", "VSSQ")]
EM_SYM, EM_PINS = multi_symbol("A133", "eMMC_FBGA153", [EMMC_BALLS], "eMMC 5.1 FBGA-153 (JEDEC), es. Kingston EMMC256-IY29-5B101", w=12.7)

SYMS = {"A133:LPDDR4_FBGA200": LP_SYM, "A133:eMMC_FBGA153": EM_SYM,
        "Connector:Micro_SD_Card_Det_Hirose_DM3AT": extract("Connector", "Micro_SD_Card_Det_Hirose_DM3AT"),
        "Power_Protection:TPD4E05U06DQA": extract("Power_Protection", "TPD4E05U06DQA"),
        "Device:C": extract("Device", "C"), "Device:R": extract("Device", "R")}
PINS = {k: pins(v) for k, v in SYMS.items() if not k.startswith("A133:")}

GLOBAL = {"GND_D"}
GLOBAL_PREFIX = ("DRAM_", "EMMC_", "SD_")
HIER = ["VCC-DRAM", "VDD18-LPDDR", "VCC-CARD", "VCC-PC", "VCC-IO", "VCC-DRAM-FB"]
items, hier = [], []


def label(net, x, y, ang):
    j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
    if net in GLOBAL or net.startswith(GLOBAL_PREFIX):
        items.append(f'(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) {F.format(j=j)} (uuid "{U()}"))')
    elif net in HIER:
        items.append(f'(hierarchical_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) {F.format(j=j)} (uuid "{U()}"))')
        if net not in hier:
            hier.append(net)
    else:
        items.append(f'(label "{net}" (at {x:.2f} {y:.2f} {ang}) {F.format(j=j + " bottom")} (uuid "{U()}"))')


def stub(ax, ay, a, net, L=2.54):
    dx, dy, la = {0: (-1, 0, 180), 180: (1, 0, 0), 90: (0, 1, 270), 270: (0, -1, 90)}[a]
    if net == "NC":
        items.append(f'(no_connect (at {ax:.2f} {ay:.2f}) (uuid "{U()}"))')
        return
    ex, ey = ax + dx * L, ay + dy * L
    items.append(f'(wire (pts (xy {ax:.2f} {ay:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
    label(net, ex, ey, la)


def sym_instance(lib_id, ref, val, fp, x, y, pinnums, unit=1, dnp=False, extra_props=(), fx=None, fy=None):
    fx = x + 2.54 if fx is None else fx
    fy = y + 1.27 if fy is None else fy
    props = "".join(f' (property "{k}" "{v}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))' for k, v in extra_props)
    pl = " ".join(f'(pin "{p}" (uuid "{U()}"))' for p in pinnums)
    items.append(
        f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit {unit}) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}") '
        f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
        f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
        f'(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
        f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
        f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
        + pl + f' (instances (project "{PROJ}" (path "{PATH}" (reference "{ref}") (unit {unit})))))')


def sref(ref):
    m = re.match(r"([A-Z]+)(\d+)$", ref)
    return f"{m.group(1)}{400 + int(m.group(2))}"  # serie 4xx: foglio Memorie


def place(lib_id, ref, val, fp, x, y, nets, dnp=False, extra_props=()):
    ref = sref(ref)
    x, y = G(x), G(y)
    seen = set()
    for num, nm, px, py, a, typ in PINS[lib_id]:
        ax, ay = round(x + px, 2), round(y - py, 2)
        if (ax, ay) in seen:
            continue
        seen.add((ax, ay))
        stub(ax, ay, a, nets.get(num, nets.get(nm, "NC")))
    big = not lib_id.startswith("Device:")
    maxpy = max(p[3] for p in PINS[lib_id])
    sym_instance(lib_id, ref, val, fp, x, y, [p[0] for p in PINS[lib_id]], dnp=dnp, extra_props=extra_props,
                 fx=(x - 5.08 if big else None), fy=(y - maxpy - 3.81 if big else None))


def place_multi(lib_id, ref, val, fp, PM, netfn, pos, extra_props=()):
    for uu, (x0, y0) in pos.items():
        x0, y0 = G(x0), G(y0)
        seen = set()
        for num, nm, px, py, side in PM[uu]:
            ax, ay = round(x0 + px, 2), round(y0 - py, 2)
            if (ax, ay) in seen:
                continue
            seen.add((ax, ay))
            net = netfn(nm)
            stub(ax, ay, side, net, L=5.08 if net != "NC" else 2.54)
        n = len(PM[uu])
        sym_instance(lib_id, ref, val, fp, x0, y0, [p[0] for p in PM[uu]], unit=uu, extra_props=extra_props,
                     fx=x0 - 15, fy=y0 - G(2.54 * ((n + 1) // 2 + 1) / 2) - 4)


def text(s, x, y):
    items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')


R0402, C0402, C0603 = "Resistor_SMD:R_0402_1005Metric", "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric"
R = lambda ref, val, x, y, a, b, **k: place("Device:R", ref, val, R0402, x, y, {"1": a, "2": b}, **k)
C = lambda ref, val, x, y, a, b, fp=C0402, **k: place("Device:C", ref, val, fp, x, y, {"1": a, "2": b}, **k)

text("MEMORIE: LPDDR4 2 GB x32, eMMC 256 GB su SMHC2 (PC), microSD su SMHC0 (PF). Serie componenti 4xx.", 20, 15)
text("Le net DRAM_*, EMMC_*, SD_* sono etichette globali condivise con il foglio CPU (porte tolte dal blocco CPU).", 20, 20)

# ---------------- LPDDR4 ----------------------------------------------------------------------------------
text("U401 LPDDR4 MT53E512M32D1ZW-046 IT:B (2 GB, 1 die, 2 canali x16). Collegamento come nel reference Allwinner A100_A133 (pag. 08, colonna LPDDR4):", 20, 30)
text("CA0-5 <- SA5,SA0,SA2,SA1,SCS0,SCS1 del SoC; CS0/CS1 <- SA4/SA3; byte scambiati (canale A = DQ8-15 e DQ0-7, canale B = DQ16-23 e DQ24-31) come nel reference.", 20, 35)
place_multi("A133:LPDDR4_FBGA200", "U401", "MT53E512M32D1ZW-046 IT:B", "Package_BGA:BGA-200_10x14.5mm_Layout12x22_P0.8x0.65mm",
            LP_PINS, lp_net, {1: (75, 150), 2: (190, 170)}, extra_props=(("MPN", "MT53E512M32D1ZW-046 IT:B"),))
X, Y = 260, 60
text("ODT_CA_A/B a VDD2 con 100k, ZQ0/ZQ1 240R 1% a VDDQ (VCC-DRAM), come nel reference. CS1/CKE1 vanno su ball NC del chip a singolo rank: innocui.", X - 10, Y - 12)
R("R1", "100k 1%", X, Y, "VCC-DRAM", "LP_ODT_A")
R("R2", "100k 1%", X + 10, Y, "VCC-DRAM", "LP_ODT_B")
R("R3", "240R 1%", X + 20, Y, "VCC-DRAM", "LP_ZQ0")
R("R4", "240R 1%", X + 30, Y, "VCC-DRAM", "LP_ZQ1")
X, Y = 260, 95
text("Disaccoppiamento vicino alla LPDDR4: VDD2/VDDQ 4x1uF + 6x0.1uF, VDD1 2x1uF + 2x0.1uF (reference + margine; da rifinire con la PDN Micron).", X - 10, Y - 12)
dl = [("C1", "1uF/10V", "VCC-DRAM"), ("C2", "1uF/10V", "VCC-DRAM"), ("C3", "1uF/10V", "VCC-DRAM"), ("C4", "1uF/10V", "VCC-DRAM"),
      ("C5", "0.1uF", "VCC-DRAM"), ("C6", "0.1uF", "VCC-DRAM"), ("C7", "0.1uF", "VCC-DRAM"), ("C8", "0.1uF", "VCC-DRAM"),
      ("C9", "0.1uF", "VCC-DRAM"), ("C10", "0.1uF", "VCC-DRAM"), ("C11", "1uF/10V", "VDD18-LPDDR"), ("C12", "1uF/10V", "VDD18-LPDDR"),
      ("C13", "0.1uF", "VDD18-LPDDR"), ("C14", "0.1uF", "VDD18-LPDDR")]
for i, (ref, val, net) in enumerate(dl):
    C(ref, val, X + 10 * (i % 7), Y + 18 * (i // 7), net, "GND_D")
C("C15", "1uF/10V", X + 80, Y, "VCC-DRAM", "GND_D")
text("C415 vicino al SoC (CD11 del reference).", X + 75, Y + 12)
R("R23", "0R", X + 95, Y, "VCC-DRAM", "VCC-DRAM-FB")
text("R423: punto di sense FB3 del PMIC preso sulle sfere VDD2 della LPDDR4 (nota del reference).", X + 75, Y + 22)

# ---------------- eMMC -------------------------------------------------------------------------------------
X, Y = 280, 200
text("U402 eMMC Kingston EMMC256-IY29-5B101 (HS200): VCC = VCC-CARD 3.3 V, VCCQ = VCC-PC 1.8 V. CLK 33R serie vicino al SoC, pull-up 10k su CMD e DAT0-7 a VCCQ, RST_n 10k.", X - 30, Y - 35)
place_multi("A133:eMMC_FBGA153", "U402", "EMMC256-IY29-5B101", "Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm",
            EM_PINS, lambda n: {"DAT0": "EMMC_D0", "DAT1": "EMMC_D1", "DAT2": "EMMC_D2", "DAT3": "EMMC_D3", "DAT4": "EMMC_D4",
                                "DAT5": "EMMC_D5", "DAT6": "EMMC_D6", "DAT7": "EMMC_D7", "CMD": "EMMC_CMD", "CLK": "EMMC_CLK_M",
                                "RST_n": "EMMC_RST", "DS": "EMMC_DS", "VDDI": "EMMC_VDDI", "VCC": "VCC-CARD", "VCCQ": "VCC-PC",
                                "VSS": "GND_D", "VSSQ": "GND_D"}[n], {1: (X, Y)}, extra_props=(("MPN", "EMMC256-IY29-5B101"),))
R("R5", "33R", X + 45, Y - 30, "EMMC_CLK", "EMMC_CLK_M")
for i, net in enumerate(["EMMC_CMD", "EMMC_D0", "EMMC_D1", "EMMC_D2", "EMMC_D3", "EMMC_D4", "EMMC_D5", "EMMC_D6", "EMMC_D7", "EMMC_RST"]):
    R(f"R{6 + i}", "10k", X + 40 + 10 * i, Y + 40, "VCC-PC", net)
C("C16", "1uF/10V", X + 40, Y + 65, "EMMC_VDDI", "GND_D")
for i, (ref, val, net) in enumerate([("C17", "2.2uF/10V", "VCC-CARD"), ("C18", "0.1uF", "VCC-CARD"), ("C19", "0.1uF", "VCC-CARD"),
                                     ("C20", "2.2uF/10V", "VCC-PC"), ("C21", "0.1uF", "VCC-PC"), ("C22", "0.1uF", "VCC-PC")]):
    C(ref, val, X + 50 + 10 * i, Y + 65, net, "GND_D")

# ---------------- microSD -----------------------------------------------------------------------------------
X, Y = 280, 330
text("J401 microSD (Hirose DM3AT con switch di rilevamento) su SMHC0: VDD = VCC-CARD, CLK 33R serie, pull-up 47k su CMD/DAT a VCC-CARD, SD_DET su PF6 (10k a VCC-IO).", X - 30, Y - 30)
place("Connector:Micro_SD_Card_Det_Hirose_DM3AT", "J1", "microSD DM3AT", "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5", X, Y,
      {"DAT2": "SD_D2", "DAT3/CD": "SD_D3", "CMD": "SD_CMD", "VDD": "VCC-CARD", "CLK": "SD_CLK_S", "VSS": "GND_D", "DAT0": "SD_D0",
       "DAT1": "SD_D1", "DET_B": "SD_DET", "DET_A": "GND_D", "SHIELD": "GND_D"})
R("R16", "33R", X + 30, Y - 15, "SD_CLK", "SD_CLK_S")
for i, net in enumerate(["SD_CMD", "SD_D0", "SD_D1", "SD_D2", "SD_D3"]):
    R(f"R{17 + i}", "47k", X + 45 + 10 * i, Y - 15, "VCC-CARD", net)
R("R22", "10k", X + 100, Y - 15, "VCC-IO", "SD_DET")
C("C23", "10uF/10V", X + 45, Y + 10, "VCC-CARD", "GND_D", C0603)
C("C24", "0.1uF", X + 55, Y + 10, "VCC-CARD", "GND_D")
text("ESD TPD4E05U06DQA vicino allo slot: CLK (lato slot), CMD, DAT0-3, DET.", X + 40, Y + 25)
place("Power_Protection:TPD4E05U06DQA", "U3", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 50, Y + 45,
      {"1": "SD_CLK_S", "2": "SD_CMD", "4": "SD_D0", "5": "SD_D1", "3": "GND_D", "8": "GND_D"})
place("Power_Protection:TPD4E05U06DQA", "U4", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 95, Y + 45,
      {"1": "SD_D2", "2": "SD_D3", "4": "SD_DET", "5": "NC", "3": "GND_D", "8": "GND_D"})

# ---------------- uscita -------------------------------------------------------------------------------------
libp = f"{PRJ}/A133.kicad_sym"
lib = open(libp).read()
for k, v in SYMS.items():
    if k.startswith("A133:") and f'(symbol "{k[5:]}"' not in lib:
        lib = lib.rstrip()[:-1] + " " + v.replace(f'(symbol "{k}"', f'(symbol "{k[5:]}"', 1) + ")"
open(libp, "w").write(lib)
open(f"{PRJ}/memorie.kicad_sch", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{SHEET_UUID}") (paper "A2") '
    + "(lib_symbols " + " ".join(SYMS.values()) + ") " + " ".join(items) + " (embedded_fonts no))")

root_path = f"{PRJ}/{PROJ}.kicad_sch"
root = open(root_path).read()
sx, sy, w = 431.8, 38.1, 50.8
h = 5.08 + 2.54 * len(hier)
pinlist, extra = [], []
for k, n in enumerate(hier):
    py = sy + 2.54 * (k + 1)
    pinlist.append(f'(pin "{n}" passive (at {sx:.2f} {py:.2f} 180) (uuid "{U()}") {F.format(j="left")})')
    extra.append(f'(wire (pts (xy {sx:.2f} {py:.2f}) (xy {sx - 5.08:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
    extra.append(f'(label "{n}" (at {sx - 5.08:.2f} {py:.2f} 180) {F.format(j="right bottom")} (uuid "{U()}"))')
sheet = (f'(sheet (at {sx} {sy}) (size {w} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
         f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{SHEET_UUID}") '
         f'(property "Sheetname" "Memorie" (at {sx} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
         f'(property "Sheetfile" "memorie.kicad_sch" (at {sx} {sy + h + 0.58:.2f} 0) {F.format(j="left top")}) '
         + " ".join(pinlist) + f' (instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "6")))))')
k = root.rfind("\t(sheet_instances")
root = root[:k] + "\t" + sheet + "\n\t" + "\n\t".join(extra) + "\n" + root[k:]
open(root_path, "w").write(root)
print("porte:", hier)
