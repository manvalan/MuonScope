"""Foglio KiCad 10 'Memorie' della scheda H616: LPDDR4 MT53E512M32D1ZW (come Orange Pi Zero3), eMMC 8 bit, microSD. Serie 4xx."""
import json
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, multi_symbol, place_multi

PRJ = sys.argv[1]
RAILS = ["VCC-DRAM", "VCC-1V8", "VCC-1V8-EMMC", "3V3_PERI", "VCC-IO", "VCC-DRAM-FB"]
m = Sheet("Memorie", "memorie.kicad_sch", 400, 6, RAILS, ("DRAM_", "EMMC_", "SD_"), paper="A2")
C0603 = "Capacitor_SMD:C_0603_1608Metric"


def natkey(t):
    mm = re.match(r"([A-Z_]+?)(\d+)(.*)$", t[1])
    return (mm.group(1), mm.group(3), int(mm.group(2))) if mm else (t[1], "", 0)


# ---------------- LPDDR4 FBGA-200 (ball map JEDEC dal progetto A133, stesso chip) ----------------------------------------
LB = json.load(open(os.path.join(SC, "lpddr4_balls.json")))
sig = sorted([(b, n) for b, n in LB.items() if not re.match(r"(VDD|VSS|NC)", n)], key=natkey)
pwr = sorted([(b, n) for b, n in LB.items() if re.match(r"(VDD|VSS|NC)", n)], key=natkey)
LP_SYM, LP_PINS = multi_symbol("H616", "LPDDR4_FBGA200", [sig, pwr], "LPDDR4 x32 200 ball (JEDEC), es. Micron MT53E512M32D1ZW-046 IT:B")
m.add_sym("H616:LPDDR4_FBGA200", LP_SYM)
for k in ["Device:R", "Device:C", "Connector:Micro_SD_Card_Det_Hirose_DM3AT", "Power_Protection:TPD4E05U06DQA"]:
    m.std(k)

# CA/CS: ricavati dalla tabella phy_init LPDDR4 (PHY_ADDR_MAP_0, usata da H313/H616/H618/A133) di U-Boot
# arch/arm/mach-sunxi/dram_sun50i_h616.c, interpretata con lo stesso schema che riproduce il reference A133.
# NON VERIFICATO sullo schema Orange Pi Zero3 (non scaricabile): vedi docs/memorie-lpddr4.md.
CHIP2SOC = {"CA0": "DRAM_A1", "CA1": "DRAM_CS0", "CA2": "DRAM_A0", "CA3": "DRAM_CS1", "CA4": "DRAM_A4", "CA5": "DRAM_A3",
            "CS0": "DRAM_A2", "CS1": "DRAM_A5", "CKE0": "DRAM_CKE0", "CKE1": "DRAM_CKE1", "CK_T": "DRAM_CKP", "CK_C": "DRAM_CKN"}


def lp_net(num, n):
    base = re.sub(r"_[AB]$", "", n)
    ch = n[-1] if re.search(r"_[AB]$", n) else None
    if base in CHIP2SOC:
        return CHIP2SOC[base]
    if n == "RESET-N":
        return "DRAM_RST"
    mm = re.match(r"DQ(\d+)_([AB])$", n)
    if mm:  # canale A = byte 0-1 del SoC, canale B = byte 2-3, bit dritti
        return f"DRAM_DQ{int(mm.group(1)) + (16 if ch == 'B' else 0)}"
    mm = re.match(r"DQS(\d)([PN])_([AB])$", n)
    if mm:
        return f"DRAM_DQS{int(mm.group(1)) + (2 if ch == 'B' else 0)}{mm.group(2)}"
    mm = re.match(r"DM(\d)_([AB])$", n)
    if mm:
        return f"DRAM_DQM{int(mm.group(1)) + (2 if ch == 'B' else 0)}"
    if n.startswith("VDD1"):
        return "VCC-1V8"
    if n.startswith(("VDD2", "VDDQ")):
        return "VCC-DRAM"
    if n.startswith("VSS"):
        return "GND_D"
    if n.startswith("ODT_CA"):
        return "LP_ODT_" + n[-1]
    if n.startswith("ZQ"):
        return "LP_" + n
    return "NC"


m.text("MEMORIE: LPDDR4 2 GB x32 (1 chip, come Orange Pi Zero3), eMMC 8 bit su SMHC2 (PC, 1.8 V), microSD su SMHC0 (PF, 3.3 V). Serie 4xx.", 20, 15)
m.text("U401 MT53E512M32D1ZW-046 IT:B: 1 die, 2 canali x16, CA comuni ai due canali. VDD1 = VCC-1V8 (ALDO1), VDD2/VDDQ = VCC-DRAM 1.1 V (DCDC3). Niente VTT/VREF/VPP.", 20, 22)
m.text("CA0 <- SA1, CA1 <- SCS0, CA2 <- SA0, CA3 <- SCS1, CA4 <- SA4, CA5 <- SA3, CS0 <- SA2, CS1 <- SA5 (da phy_init U-Boot, NON VERIFICATO). DQ dritti: canale A = byte 0-1, canale B = byte 2-3.", 20, 27)
place_multi(m, "H616:LPDDR4_FBGA200", "U1", "MT53E512M32D1ZW-046 IT:B", "Package_BGA:BGA-200_10x14.5mm_Layout12x22_P0.8x0.65mm",
            LP_PINS, lp_net, {1: (75, 150), 2: (190, 170)}, mpn="MT53E512M32D1ZW-046 IT:B")
X, Y = 260, 60
m.text("ODT_CA_A/B a VDD2 con 100k, ZQ0/ZQ1 240R 1% a VDDQ (come il reference Allwinner). CS1/CKE1 su sfere NC del chip a singolo rank.", X - 10, Y - 12)
m.R("R1", "100k 1%", X, Y, "VCC-DRAM", "LP_ODT_A")
m.R("R2", "100k 1%", X + 10, Y, "VCC-DRAM", "LP_ODT_B")
m.R("R3", "240R 1%", X + 20, Y, "VCC-DRAM", "LP_ZQ0")
m.R("R4", "240R 1%", X + 30, Y, "VCC-DRAM", "LP_ZQ1")
X, Y = 260, 95
m.text("Disaccoppiamento LPDDR4: VDD2/VDDQ 4x1uF + 6x0.1uF, VDD1 2x1uF + 2x0.1uF (da rifinire con la PDN Micron).", X - 10, Y - 12)
dl = [("C1", "1uF/10V", "VCC-DRAM"), ("C2", "1uF/10V", "VCC-DRAM"), ("C3", "1uF/10V", "VCC-DRAM"), ("C4", "1uF/10V", "VCC-DRAM"),
      ("C5", "0.1uF", "VCC-DRAM"), ("C6", "0.1uF", "VCC-DRAM"), ("C7", "0.1uF", "VCC-DRAM"), ("C8", "0.1uF", "VCC-DRAM"),
      ("C9", "0.1uF", "VCC-DRAM"), ("C10", "0.1uF", "VCC-DRAM"), ("C11", "1uF/10V", "VCC-1V8"), ("C12", "1uF/10V", "VCC-1V8"),
      ("C13", "0.1uF", "VCC-1V8"), ("C14", "0.1uF", "VCC-1V8")]
for i, (ref, val, net) in enumerate(dl):
    m.C(ref, val, X + 10 * (i % 7), Y + 18 * (i // 7), net, "GND_D")
m.R("R5", "0R", X + 80, Y, "VCC-DRAM", "VCC-DRAM-FB")
m.text("R405: sense del DCDC3 dell'AXP313A preso sulle sfere VDD2 della LPDDR4.", X + 75, Y + 12)

# ---------------- eMMC FBGA-153 (pinout JEDEC eMMC 5.1) ----------------------------------------------------------------------
EMMC_BALLS = [("A3", "DAT0"), ("A4", "DAT1"), ("A5", "DAT2"), ("B2", "DAT3"), ("B3", "DAT4"), ("B4", "DAT5"), ("B5", "DAT6"),
              ("B6", "DAT7"), ("M5", "CMD"), ("M6", "CLK"), ("K5", "RST_n"), ("H5", "DS"), ("C2", "VDDI"),
              ("E6", "VCC"), ("F5", "VCC"), ("J10", "VCC"), ("K9", "VCC"), ("C6", "VCCQ"), ("M4", "VCCQ"), ("N4", "VCCQ"),
              ("P3", "VCCQ"), ("P5", "VCCQ"), ("E7", "VSS"), ("G5", "VSS"), ("H10", "VSS"), ("K8", "VSS"), ("C4", "VSSQ"),
              ("N2", "VSSQ"), ("N5", "VSSQ"), ("P4", "VSSQ"), ("P6", "VSSQ")]
EM_SYM, EM_PINS = multi_symbol("H616", "eMMC_FBGA153", [EMMC_BALLS], "eMMC 5.1 FBGA-153 (JEDEC), 64 GB", w=12.7)
m.add_sym("H616:eMMC_FBGA153", EM_SYM)
EMN = {"DAT0": "EMMC_D0", "DAT1": "EMMC_D1", "DAT2": "EMMC_D2", "DAT3": "EMMC_D3", "DAT4": "EMMC_D4", "DAT5": "EMMC_D5",
       "DAT6": "EMMC_D6", "DAT7": "EMMC_D7", "CMD": "EMMC_CMD", "CLK": "EMMC_CLK_M", "RST_n": "EMMC_RST", "DS": "EMMC_DS",
       "VDDI": "EMMC_VDDI", "VCC": "3V3_PERI", "VCCQ": "VCC-1V8-EMMC", "VSS": "GND_D", "VSSQ": "GND_D"}
X, Y = 280, 200
m.text("U402 eMMC 64 GB FBGA-153 (modello da scegliere): VCC = 3V3_PERI, VCCQ = VCC-1V8-EMMC (LDO dedicato, = VCC_PC: HS200, DS per HS400). CLK 33R serie, pull-up 10k su CMD/DAT0-7/RST_n a VCCQ.", X - 30, Y - 35)
place_multi(m, "H616:eMMC_FBGA153", "U2", "eMMC 64GB", "Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm",
            EM_PINS, lambda num, n: EMN[n], {1: (X, Y)})
m.R("R6", "33R", X + 45, Y - 30, "EMMC_CLK", "EMMC_CLK_M")
for i, net in enumerate(["EMMC_CMD", "EMMC_D0", "EMMC_D1", "EMMC_D2", "EMMC_D3", "EMMC_D4", "EMMC_D5", "EMMC_D6", "EMMC_D7", "EMMC_RST"]):
    m.R(f"R{7 + i}", "10k", X + 40 + 10 * i, Y + 40, "VCC-1V8-EMMC", net)
m.C("C15", "1uF/10V", X + 40, Y + 65, "EMMC_VDDI", "GND_D")
for i, (ref, val, net) in enumerate([("C16", "2.2uF/10V", "3V3_PERI"), ("C17", "0.1uF", "3V3_PERI"), ("C18", "0.1uF", "3V3_PERI"),
                                     ("C19", "2.2uF/10V", "VCC-1V8-EMMC"), ("C20", "0.1uF", "VCC-1V8-EMMC"), ("C21", "0.1uF", "VCC-1V8-EMMC")]):
    m.C(ref, val, X + 50 + 10 * i, Y + 65, net, "GND_D")

# ---------------- microSD ---------------------------------------------------------------------------------------------------
X, Y = 280, 330
m.text("J401 microSD (Hirose DM3AT) su SMHC0: VDD = 3V3_PERI (solo 3.3 V, niente UHS), CLK 33R serie, pull-up 47k a 3V3_PERI. SD_DET sull'espansore (P15), 10k a VCC-IO.", X - 30, Y - 30)
m.place("Connector:Micro_SD_Card_Det_Hirose_DM3AT", "J1", "DM3AT-SF-PEJM5", "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5", X, Y,
        {"DAT2": "SD_D2", "DAT3/CD": "SD_D3", "CMD": "SD_CMD", "VDD": "3V3_PERI", "CLK": "SD_CLK_S", "VSS": "GND_D", "DAT0": "SD_D0",
         "DAT1": "SD_D1", "DET_B": "SD_DET", "DET_A": "GND_D", "SHIELD": "GND_D"}, mpn="DM3AT-SF-PEJM5")
m.R("R17", "33R", X + 30, Y - 15, "SD_CLK", "SD_CLK_S")
for i, net in enumerate(["SD_CMD", "SD_D0", "SD_D1", "SD_D2", "SD_D3"]):
    m.R(f"R{18 + i}", "47k", X + 45 + 10 * i, Y - 15, "3V3_PERI", net)
m.R("R23", "10k", X + 100, Y - 15, "VCC-IO", "SD_DET")
m.C("C22", "10uF/10V", X + 45, Y + 10, "3V3_PERI", "GND_D", C0603)
m.C("C23", "0.1uF", X + 55, Y + 10, "3V3_PERI", "GND_D")
m.text("ESD TPD4E05U06DQA vicino allo slot: CLK (lato slot), CMD, DAT0-3, DET.", X + 40, Y + 25)
m.place("Power_Protection:TPD4E05U06DQA", "U3", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 50, Y + 45,
        {"1": "SD_CLK_S", "2": "SD_CMD", "4": "SD_D0", "5": "SD_D1", "3": "GND_D", "8": "GND_D"})
m.place("Power_Protection:TPD4E05U06DQA", "U4", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 95, Y + 45,
        {"1": "SD_D2", "2": "SD_D3", "4": "SD_DET", "5": "NC", "3": "GND_D", "8": "GND_D"})
print("porte:", m.write(PRJ, 431.8, 38.1, f"{PRJ}/H616.kicad_sym"))
