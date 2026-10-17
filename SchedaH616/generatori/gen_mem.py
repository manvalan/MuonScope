"""Foglio KiCad 10 'Memorie' della scheda RK3568: DDR4 x16 K4AAG165WA-BCWE (singolo chip, point-to-point), eMMC 8 bit, microSD. Serie 4xx."""
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, multi_symbol, place_multi, pins_by_unit
from kilib import LIBNAME

PRJ = sys.argv[1]
RAILS = ["VCC_DDR", "VCC2V5_DDR", "VCC1V8_EMMC", "VCC_3V3", "VCC3V3_SD", "VCCIO_SD", "VCC3V3_PMU"]
m = Sheet("Memorie", "memorie.kicad_sch", 400, 6, RAILS, ("DDR_", "EMMC_", "SD_"), paper="A2")
C0402, C0603 = "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric"
R0402 = "Resistor_SMD:R_0402_1005Metric"   # rete DDR (ZQ, VREF) e serie dei clock vicino ai pin


def natkey(t):
    mm = re.match(r"([A-Z_/]+?)(\d+)(.*)$", t[1])
    return (mm.group(1), mm.group(3), int(mm.group(2))) if mm else (t[1], "", 0)


# ---------------- DDR4 x16 FBGA-96: ballout JEDEC (JESD79-4), uguale al simbolo EasyEDA di K4AAG165WA-BCWE (LCSC C2920140)
# e al simbolo "DDR4_16bit_SDP" del reference Rockchip RK3568 AIoT V1.1 pag. 28.
DDR4 = {
    "A1": "VDDQ", "A2": "VSSQ", "A3": "DQU0", "A7": "DQSU_c", "A8": "VSSQ", "A9": "VDDQ",
    "B1": "VPP", "B2": "VSS", "B3": "VDD", "B7": "DQSU_t", "B8": "DQU1", "B9": "VDD",
    "C1": "VDDQ", "C2": "DQU4", "C3": "DQU2", "C7": "DQU3", "C8": "DQU5", "C9": "VSSQ",
    "D1": "VDD", "D2": "VSSQ", "D3": "DQU6", "D7": "DQU7", "D8": "VSSQ", "D9": "VDDQ",
    "E1": "VSS", "E2": "DMU_n/DBIU_n", "E3": "VSSQ", "E7": "DML_n/DBIL_n", "E8": "VSSQ", "E9": "VSS",
    "F1": "VSSQ", "F2": "VDDQ", "F3": "DQSL_c", "F7": "DQL1", "F8": "VDDQ", "F9": "ZQ",
    "G1": "VDDQ", "G2": "DQL0", "G3": "DQSL_t", "G7": "VDD", "G8": "VSS", "G9": "VDDQ",
    "H1": "VSSQ", "H2": "DQL4", "H3": "DQL2", "H7": "DQL3", "H8": "DQL5", "H9": "VSSQ",
    "J1": "VDD", "J2": "VDDQ", "J3": "DQL6", "J7": "DQL7", "J8": "VDDQ", "J9": "VDD",
    "K1": "VSS", "K2": "CKE", "K3": "ODT", "K7": "CK_t", "K8": "CK_c", "K9": "VSS",
    "L1": "VDD", "L2": "WE_n/A14", "L3": "ACT_n", "L7": "CS_n", "L8": "RAS_n/A16", "L9": "VDD",
    "M1": "VREFCA", "M2": "BG0", "M3": "A10/AP", "M7": "A12/BC_n", "M8": "CAS_n/A15", "M9": "VSS",
    "N1": "VSS", "N2": "BA0", "N3": "A4", "N7": "A3", "N8": "BA1", "N9": "TEN",
    "P1": "RESET_n", "P2": "A6", "P3": "A0", "P7": "A1", "P8": "A5", "P9": "ALERT_n",
    "R1": "VDD", "R2": "A8", "R3": "A2", "R7": "A9", "R8": "A7", "R9": "VPP",
    "T1": "VSS", "T2": "A11", "T3": "PAR", "T7": "NC", "T8": "A13", "T9": "VDD"}
assert len(DDR4) == 96
sig = sorted([(b, n) for b, n in DDR4.items() if not re.match(r"(VDD|VSS|VPP|NC$)", n)], key=natkey)
pwr = sorted([(b, n) for b, n in DDR4.items() if re.match(r"(VDD|VSS|VPP|NC$)", n)], key=natkey)
# simbolo e footprint dalla libreria personale MIKILAB (EasyEDA C2920140): nomi delle sfere controllati sul DDR4 qui sopra
D4_ID, D4_FP = m.mik("K4AAG165WA-BCWE")
assert {n: nm for n, nm, *_ in __import__("kilib").pins(m.syms[D4_ID])}.keys() == DDR4.keys()
for k in ["Device:R", "Device:C", "Power_Protection:TPD4E05U06DQA"]:
    m.std(k)

D4NET = {"DQSU_c": "DDR_DQSU_N", "DQSU_t": "DDR_DQSU_P", "DQSL_c": "DDR_DQSL_N", "DQSL_t": "DDR_DQSL_P", "DMU_n/DBIU_n": "DDR_DMU",
         "DML_n/DBIL_n": "DDR_DML", "CKE": "DDR_CKE", "ODT": "DDR_ODT", "CK_t": "DDR_CK_P", "CK_c": "DDR_CK_N",
         "WE_n/A14": "DDR_A14_WE_N", "ACT_n": "DDR_ACT_N", "CS_n": "DDR_CS_N", "RAS_n/A16": "DDR_A16_RAS_N", "A10/AP": "DDR_A10",
         "A12/BC_n": "DDR_A12", "CAS_n/A15": "DDR_A15_CAS_N", "BG0": "DDR_BG0", "BA0": "DDR_BA0", "BA1": "DDR_BA1",
         "RESET_n": "DDR_RESET_N", "VREFCA": "VREF_DDR4_CA", "ZQ": "DDR4_ZQ", "TEN": "GND_D", "PAR": "GND_D", "ALERT_n": "NC",
         "NC": "NC", "VPP": "VCC2V5_DDR"}


def d4_net(num, n):
    if n in D4NET:
        return D4NET[n]
    if re.match(r"DQ[LU]\d$", n) or re.match(r"A\d+$", n):
        return "DDR_" + n
    if n.startswith(("VDDQ", "VDD")):
        return "VCC_DDR"
    if n.startswith("VSS"):
        return "GND_D"
    raise SystemExit("DDR4: sfera senza net " + num + " " + n)


m.text("MEMORIE: DDR4 x16 (1 chip, point-to-point, niente VTT), eMMC 8 bit su EMMC (VCCIO2 1.8 V), microSD su SDMMC0 (VCCIO3). Serie 4xx.", 20, 15)
m.text("U401 Samsung K4AAG165WA-BCWE (LCSC C2920140, 16 Gbit = 2 GB, x16, DDR4-3200): VDD/VDDQ = VCC_DDR 1.2 V (BUCK3), VPP = VCC2V5_DDR (AP2112K-2.5). Collegata al canale A del PHY dell'RK3568.", 20, 22)
m.text("DQ/DM/DQS secondo il pinout Rockchip (DDR_DQx_A -> DDR4_DQL/DQU_A): l'ordine dei bit nel byte e' quello del template Rockchip, i CA non si possono scambiare (Hardware Design Guide 2.1.7).", 20, 27)
m.place(D4_ID, "U1", "K4AAG165WA-BCWE", D4_FP, 100, 150, {b: d4_net(b, n) for b, n in DDR4.items()}, mpn="K4AAG165WA-BCWE", lcsc="C2920140")
X, Y = 260, 55
m.text("ZQ 240R 1% a GND, TEN e PAR a GND, ALERT_n libero, T7 (NC/A17) libero (reference Rockchip DDR4 16bit SDP). RESET_n con 1 nF DNP (anti-ESD, Hardware Design Guide).", X - 10, Y - 12)
m.R("R1", "240R 1%", X, Y, "DDR4_ZQ", "GND_D", fp=R0402)
m.C("C1", "1nF", X + 10, Y, "DDR_RESET_N", "GND_D", dnp=True)
X, Y = 260, 85
m.text("VREFCA da DDR_VREFOUT del SoC (P8, 0.6 V di default) con 0R; 2x 1 nF vicino alla DDR4 (valore da non cambiare, Hardware Design Guide). Partitore 1k/1k DNP come alternativa.", X - 10, Y - 12)
m.R("R2", "0R", X, Y, "DDR_VREFOUT", "VREF_DDR4_CA", fp=R0402)
m.C("C2", "1nF", X + 10, Y, "VREF_DDR4_CA", "GND_D", C0402)
m.C("C3", "1nF", X + 20, Y, "VREF_DDR4_CA", "GND_D", C0402)
m.R("R3", "1k 1%", X + 30, Y, "VCC_DDR", "VREF_DDR4_CA", fp=R0402, dnp=True)
m.R("R4", "1k 1%", X + 40, Y, "VREF_DDR4_CA", "GND_D", fp=R0402, dnp=True)
X, Y = 260, 115
m.text("Disaccoppiamento DDR4 (reference, ridotto a un chip): VCC_DDR 2x 10 uF + 1 uF + 10x 100 nF; VPP 1 uF + 100 nF vicino alle sfere B1/R9.", X - 10, Y - 12)
dl = [("C4", "10uF", "VCC_DDR", C0603), ("C5", "10uF", "VCC_DDR", C0603), ("C6", "1uF", "VCC_DDR", C0402)] + \
     [(f"C{7 + i}", "100nF", "VCC_DDR", C0402) for i in range(10)] + [("C17", "1uF", "VCC2V5_DDR", C0402), ("C18", "100nF", "VCC2V5_DDR", C0402)]
for i, (ref, val, net, fp) in enumerate(dl):
    m.C(ref, val, X + 10 * (i % 8), Y + 18 * (i // 8), net, "GND_D", fp)

# ---------------- eMMC FBGA-153 (pinout JEDEC eMMC 5.1) ----------------------------------------------------------------------
EMMC_BALLS = [("A3", "DAT0"), ("A4", "DAT1"), ("A5", "DAT2"), ("B2", "DAT3"), ("B3", "DAT4"), ("B4", "DAT5"), ("B5", "DAT6"),
              ("B6", "DAT7"), ("M5", "CMD"), ("M6", "CLK"), ("K5", "RST_n"), ("H5", "DS"), ("C2", "VDDI"),
              ("E6", "VCC"), ("F5", "VCC"), ("J10", "VCC"), ("K9", "VCC"), ("C6", "VCCQ"), ("M4", "VCCQ"), ("N4", "VCCQ"),
              ("P3", "VCCQ"), ("P5", "VCCQ"), ("E7", "VSS"), ("G5", "VSS"), ("H10", "VSS"), ("K8", "VSS"), ("A6", "VSS"), ("J5", "VSS"), ("C4", "VSSQ"),
              ("N2", "VSSQ"), ("N5", "VSSQ"), ("P4", "VSSQ"), ("P6", "VSSQ")]
# simbolo (2 unita) e footprint dalla libreria MIKILAB (EasyEDA C49284704); le sfere non elencate qui sopra sono NC/RFU/VSF
EM_ID, EM_FP = m.mik("FEMDNN064G-C9A61")
EM_PINS = pins_by_unit(m.syms[EM_ID])
EMB = dict(EMMC_BALLS)
EMN = {"DAT0": "EMMC_D0", "DAT1": "EMMC_D1", "DAT2": "EMMC_D2", "DAT3": "EMMC_D3", "DAT4": "EMMC_D4", "DAT5": "EMMC_D5",
       "DAT6": "EMMC_D6", "DAT7": "EMMC_D7", "CMD": "EMMC_CMD", "CLK": "EMMC_CLK", "RST_n": "EMMC_RST", "DS": "EMMC_DS",
       "VDDI": "EMMC_VDDI", "VCC": "VCC_3V3", "VCCQ": "VCC1V8_EMMC", "VSS": "GND_D", "VSSQ": "GND_D"}
X, Y = 280, 220
m.text("U402 eMMC FORESEE FEMDNN064G-C9A61 (64 GB, eMMC 5.1 HS400, LCSC C49284704): VCC = VCC_3V3, VCCQ = VCC1V8_EMMC (AP2112K-1.8, = VCCIO2: HS200/HS400). CLK 22R serie vicino al SoC (reference), pull-up 10k su CMD/DAT0-7/RST_n.", X - 30, Y - 35)
place_multi(m, EM_ID, "U2", "FEMDNN064G-C9A61", EM_FP, EM_PINS, lambda num, n: EMN[EMB[num]] if num in EMB else "NC",
            {1: (170, 300), 2: (75, 300)}, mpn="FEMDNN064G-C9A61", lcsc="C49284704")
m.R("R5", "22R", X + 45, Y - 30, "EMMC_CLK_S", "EMMC_CLK", fp=R0402)
for i, net in enumerate(["EMMC_CMD", "EMMC_D0", "EMMC_D1", "EMMC_D2", "EMMC_D3", "EMMC_D4", "EMMC_D5", "EMMC_D6", "EMMC_D7", "EMMC_RST"]):
    m.R(f"R{6 + i}", "10k", X + 40 + 10 * i, Y + 40, "VCC1V8_EMMC", net)
m.C("C19", "1uF/10V", X + 40, Y + 65, "EMMC_VDDI", "GND_D")
for i, (ref, val, net) in enumerate([("C20", "2.2uF/10V", "VCC_3V3"), ("C21", "0.1uF", "VCC_3V3"), ("C22", "0.1uF", "VCC_3V3"),
                                     ("C23", "2.2uF/10V", "VCC1V8_EMMC"), ("C24", "0.1uF", "VCC1V8_EMMC"), ("C25", "0.1uF", "VCC1V8_EMMC")]):
    m.C(ref, val, X + 50 + 10 * i, Y + 65, net, "GND_D")

# ---------------- microSD ---------------------------------------------------------------------------------------------------
X, Y = 280, 340
m.text("J401 microSD (Hirose DM3AT) su SDMMC0: VDD = VCC3V3_SD (SWOUT2 dell'RK809-5), segnali a VCCIO_SD (LDO5, 3.3 V, 1.8 V per UHS). CLK 22R serie, pull-up 47k a VCCIO_SD.", X - 30, Y - 30)
m.text("SD_DET su SDMMC0_DET (GPIO0_A4, PMUIO1) con 10k a VCC3V3_PMU: basso con la scheda inserita = SDMMC0 (alto = JTAG sui pin SDMMC0, Hardware Design Guide).", X - 30, Y - 25)
SD_ID, SD_FP = m.mik("DM3AT-SF-PEJM5")
m.place(SD_ID, "J1", "DM3AT-SF-PEJM5", SD_FP, X, Y,
        {"1": "SD_D2", "2": "SD_D3", "3": "SD_CMD", "4": "VCC3V3_SD", "5": "SD_CLK", "6": "GND_D", "7": "SD_D0", "8": "SD_D1",
         "9": "SD_DET", "11": "GND_D", "10": "GND_D", "12": "GND_D", "13": "GND_D", "14": "GND_D"}, mpn="DM3AT-SF-PEJM5")
m.R("R16", "22R", X + 30, Y - 15, "SD_CLK_S", "SD_CLK", fp=R0402)
for i, net in enumerate(["SD_CMD", "SD_D0", "SD_D1", "SD_D2", "SD_D3"]):
    m.R(f"R{17 + i}", "47k", X + 45 + 10 * i, Y - 15, "VCCIO_SD", net)
m.R("R22", "10k", X + 100, Y - 15, "VCC3V3_PMU", "SD_DET")
m.C("C26", "10uF/10V", X + 45, Y + 10, "VCC3V3_SD", "GND_D", C0603)
m.C("C27", "0.1uF", X + 55, Y + 10, "VCC3V3_SD", "GND_D")
m.text("ESD TPD4E05U06DQA vicino allo slot: CLK (lato slot), CMD, DAT0-3, DET.", X + 40, Y + 25)
m.place("Power_Protection:TPD4E05U06DQA", "U3", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 50, Y + 45,
        {"1": "SD_CLK", "2": "SD_CMD", "4": "SD_D0", "5": "SD_D1", "3": "GND_D", "8": "GND_D"})
m.place("Power_Protection:TPD4E05U06DQA", "U4", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 95, Y + 45,
        {"1": "SD_D2", "2": "SD_D3", "4": "SD_DET", "5": "NC", "3": "GND_D", "8": "GND_D"})
print("porte:", m.write(PRJ, 431.8, 38.1, f"{PRJ}/{LIBNAME}.kicad_sym"))
