"""Foglio KiCad 10 'PMIC' della scheda RK3568: RK809-5 (reference Rockchip RK3568 AIoT V1.1 / ROCK 3A), TCS4525 per VDD_CPU,
TPS563201 per VCC3V3_SYS, LDO AP2112K-1.8 (VCCQ eMMC) e AP2112K-2.5 (VPP DDR4). Serie 2xx."""
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet
from kilib import LIBNAME

PRJ = sys.argv[1]
RAILS = ["5V_SYS", "VCC3V3_SYS", "VCC_3V3", "VCC3V3_PMU", "VCC3V3_SD", "VCCIO_SD", "VCC1V8_EMMC", "VCCA_1V8", "VCCA1V8_PMU",
         "VDDA_0V9", "VDDA0V9_PMU", "VDD_CPU", "VDD_CPU_COM", "VDD_LOGIC", "VDD_GPU", "VDD_NPU", "VCC_DDR", "VCC2V5_DDR"]
C0402, C0603, C0805 = "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric"
L2520 = "Inductor_SMD:L_1008_2520Metric"
p = Sheet("PMIC", "pmic.kicad_sch", 200, 5, RAILS, ("I2C0_", "PMIC_", "CLK32K", "RESETn"), paper="A2")

# Pinout RK809 dal datasheet Rockchip RK809 (Rev 2.3, par. 2.8 "Pinout Number Order", QFN68 7x7 passo 0.35, pad esposto = GND)
RK809 = [("11", "VCC1", "L"), ("10", "VCC2", "L"), ("24", "VCC3", "L"), ("66", "VCC4", "L"), ("22", "VCC5", "L"), ("30", "VCC6", "L"),
         ("4", "VCC7", "L"), ("57", "VCC8", "L"), ("54", "VCC9", "L"), ("45", "VCC_RTC", "L"), ("33", "VCC_SPK_HP", "L"),
         ("1", "SCL", "L"), ("2", "SDA", "L"), ("7", "INT", "L"), ("49", "SLEEP", "L"), ("52", "PWRON", "L"), ("67", "RESETB", "L"),
         ("68", "CLK32K", "L"), ("50", "XIN", "L"), ("51", "XOUT", "L"), ("61", "VDC", "L"), ("60", "EXT_EN", "L"),
         ("56", "BATDIV", "L"), ("62", "SNSP", "L"), ("63", "SNSN", "L"), ("46", "VREF", "L"), ("47", "GNDREF", "L"),
         ("44", "VCC_1P8A", "L"), ("48", "VCC_1P8D", "L"), ("69", "EPAD", "L"),
         ("12", "SW1", "R"), ("13", "FB1", "R"), ("9", "SW2", "R"), ("8", "FB2", "R"), ("25", "SW3", "R"), ("26", "VBUCK3", "R"),
         ("27", "FB3", "R"), ("65", "SW4", "R"), ("64", "FB4", "R"), ("53", "SW5", "R"), ("59", "FB5", "R"),
         ("23", "LDO1", "R"), ("21", "LDO2", "R"), ("20", "LDO3", "R"), ("28", "LDO4", "R"), ("29", "LDO5", "R"), ("31", "LDO6", "R"),
         ("3", "LDO7", "R"), ("5", "LDO8", "R"), ("6", "LDO9", "R"), ("55", "SWOUT1", "R"), ("58", "SWOUT2", "R"),
         ("14", "LRCLK", "R"), ("15", "BCLK", "R"), ("16", "MCLK", "R"), ("17", "SDI", "R"), ("18", "SDO/PDMDATA", "R"),
         ("19", "PDMCLK", "R"), ("32", "SPKP_OUT", "R"), ("34", "SPKN_OUT", "R"), ("35", "VCC_CPVSS", "R"), ("36", "CPN", "R"),
         ("37", "CPP", "R"), ("38", "VCC_CPVDD", "R"), ("39", "HPL_OUT", "R"), ("40", "HP_SNS", "R"), ("41", "HPR_OUT", "R"),
         ("42", "MICIN", "R"), ("43", "MICIP", "R")]
assert sorted(int(n) for n, _, _ in RK809) == list(range(1, 70))
# simbolo e footprint dalla libreria personale MIKILAB (EasyEDA C2939628); RK809 sopra resta come controllo del pinout
RK809_ID, RK809_FP = p.mik("RK809-5")
assert {n for n, *_ in __import__("kilib").pins(p.syms[RK809_ID])} == {n for n, _, _ in RK809}
# TCS4525 dal datasheet TCS4525 Ver.1.0 (WCSP-20 2.0x1.6 mm, passo 0.4)
TCS = [("D1", "AVIN", "L"), ("D2", "PVIN", "L"), ("E1", "PVIN", "L"), ("E2", "PVIN", "L"), ("A2", "EN", "L"), ("A1", "VSEL", "L"),
       ("B1", "SDA", "L"), ("A3", "SCL", "L"), ("B4", "AGND", "L"), ("B3", "PGND/PG", "L"),
       ("D3", "SW", "R"), ("D4", "SW", "R"), ("E3", "SW", "R"), ("E4", "SW", "R"), ("A4", "FB", "R"),
       ("B2", "PGND", "R"), ("C1", "PGND", "R"), ("C2", "PGND", "R"), ("C3", "PGND", "R"), ("C4", "PGND", "R")]
TCS_ID, TCS_FP = p.mik("TCS4525")
TPS563_ID, TPS563_FP = p.mik("TPS563201DDCR")
LDO18_ID, LDO18_FP = p.mik("AP2112K-1.8TRG1")
for k in ["Device:R", "Device:C", "Device:L", "Device:Crystal", "Connector:TestPoint", "Regulator_Linear:AP2112K-2.5"]:
    p.std(k)

p.text("PMIC RK809-5 (datasheet Rockchip RK809 Rev 2.3; schema come Rockchip RK3568 AIoT REF V1.1 pag. 22 e Radxa ROCK 3A): ingressi VCC1-VCC9 da VCC3V3_SYS, I2C0 0x20. Serie 2xx.", 20, 15)
p.text("Default RK809-5 (tabella 4-4): BUCK1 0.9 V seq 1, BUCK2 0.9 V seq 2, BUCK3 da partitore seq 3, BUCK4 SPENTO (0.5 V), BUCK5 1.8 V seq 2, LDO2/3 0.9 V seq 1, LDO5 3.3 V seq 4, LDO6 3.3 V seq 2, LDO7/8 1.8 V seq 2, SWOUT1/2 seq 4.", 20, 20)
p.text("BUCK4 parte spento a 0.5 V: non puo' essere il 3.3 V di sistema (resterebbe tutto spento). Il 3.3 V resta sul TPS563201 (VCC3V3_SYS) come nel reference Rockchip; BUCK4 alimenta VDD_NPU (come ROCK 3A).", 20, 25)

X0, Y0 = 170, 130
p.place(RK809_ID, "U1", "RK809-5", RK809_FP, X0, Y0, {
    "11": "VCC3V3_SYS", "10": "VCC3V3_SYS", "24": "VCC3V3_SYS", "66": "VCC3V3_SYS", "22": "VCC3V3_SYS", "30": "VCC3V3_SYS",
    "4": "VCC3V3_SYS", "57": "VCC3V3_SYS", "54": "VCC3V3_SYS", "45": "VCC3V3_SYS", "33": "PMIC_VCC_SPK",
    "1": "PMIC_SCL", "2": "PMIC_SDA", "7": "PMIC_INT_L", "49": "PMIC_SLEEP_H", "52": "PMIC_PWRON", "67": "RESETn",
    "68": "PMIC_CLK32K", "50": "PMIC_XIN", "51": "PMIC_XOUT", "61": "PMIC_VDC", "60": "NC",
    "56": "GND_D", "62": "GND_D", "63": "GND_D", "46": "PMIC_VREF", "47": "GND_D", "44": "PMIC_1P8A", "48": "PMIC_1P8D", "69": "GND_D",
    "12": "PMIC_SW1", "13": "VDD_LOGIC", "9": "PMIC_SW2", "8": "VDD_GPU", "25": "PMIC_SW3", "26": "VCC_DDR", "27": "PMIC_FB3",
    "65": "PMIC_SW4", "64": "VDD_NPU", "53": "PMIC_SW5", "59": "PMIC_FB5",
    "23": "PMIC_LDO1", "21": "VDDA_0V9", "20": "VDDA0V9_PMU", "28": "PMIC_LDO4", "29": "VCCIO_SD", "31": "VCC3V3_PMU",
    "3": "VCCA_1V8", "5": "VCCA1V8_PMU", "6": "PMIC_LDO9", "55": "VCC_3V3", "58": "VCC3V3_SD",
    "14": "GND_D", "15": "GND_D", "16": "GND_D", "17": "GND_D", "19": "GND_D", "40": "GND_D",
    "18": "NC", "36": "NC", "37": "NC", "38": "NC", "35": "NC", "39": "NC", "41": "NC", "34": "NC", "32": "NC", "43": "NC", "42": "NC"},
    mpn="RK809-5", lcsc="C2939628")
p.text("Codec non usato (nota del reference): pin 14, 15, 16, 17, 19, 40 a VSS; 18, 32, 34-39, 41-43 flottanti. VCC_SPK_HP (33) da VCC3V3_SYS: il datasheet chiede VCC_RTC (45) = tensione piu' alta dell'RK809.", 20, 205)
p.text("VCC_RTC (45) a VCC3V3_SYS con 1 uF (fig. 1-2 del datasheet, senza batteria). VDC (61) da 5V_SYS con 100k/22k = 0.9 V (>0.55 V: accensione al fronte di salita). BATDIV/SNSP/SNSN a GND. EXT_EN libero.", 20, 210)

# ---------------- ingressi --------------------------------------------------------------------------------------------------------
X, Y = 30, 50
p.text("Ingressi (reference AIoT): VCC1 22 uF, VCC2/VCC3/VCC4/VCC9 10 uF, VCC5-VCC8 1 uF, tutti vicino ai pin.", X - 10, Y - 10)
ins = [("C1", "22uF/10V", C0603), ("C2", "10uF/10V", C0603), ("C3", "10uF/10V", C0603), ("C4", "10uF/10V", C0603), ("C5", "1uF", C0402),
       ("C6", "1uF", C0402), ("C7", "1uF", C0402), ("C8", "1uF", C0402), ("C9", "10uF/10V", C0603), ("C10", "1uF", C0402)]
for i, (ref, val, fp) in enumerate(ins):
    p.C(ref, val, X + 10 * i, Y, "VCC3V3_SYS", "GND_D", fp)
p.C("C11", "10uF/10V", X + 100, Y, "PMIC_VCC_SPK", "GND_D", C0603)
p.R("R1", "0R", X + 110, Y, "VCC3V3_SYS", "PMIC_VCC_SPK")

# ---------------- BUCK ------------------------------------------------------------------------------------------------------------
X, Y = 260, 50
p.text("BUCK: induttori 0.47 uH 2520 (DCR < 50 mohm, datasheet: 0.47 uH/4 A BUCK1/2/5, 3 A BUCK3/4). FB1/FB2/FB4 sulle uscite (VDD_LOGIC/GPU/NPU), come il reference.", X - 10, Y - 12)
BUCKS = [("L1", "PMIC_SW1", "VDD_LOGIC", [("C12", "22uF"), ("C13", "22uF"), ("C14", "100nF")]),
         ("L2", "PMIC_SW2", "VDD_GPU", [("C15", "22uF"), ("C16", "22uF"), ("C17", "100nF")]),
         ("L3", "PMIC_SW3", "VCC_DDR", [("C18", "22uF"), ("C19", "10uF")]),
         ("L4", "PMIC_SW4", "VDD_NPU", [("C20", "22uF"), ("C21", "22uF"), ("C22", "100nF")]),
         ("L5", "PMIC_SW5", "VCC_1V8", [("C23", "22uF"), ("C24", "22uF")])]
for k, (lref, sw, out, caps) in enumerate(BUCKS):
    yy = Y + 22 * k
    p.place("Device:L", lref, "0.47uH/4A", L2520, X, yy, {"1": sw, "2": out}, mpn="TFM252012ALMA-R47MTAA")
    for i, (cref, val) in enumerate(caps):
        p.C(cref, val, X + 15 + 10 * i, yy, out, "GND_D", C0603 if "u" in val and val != "1uF" else C0402)
p.text("BUCK3 VCC_DDR = 0.8 V x (1 + 62k/120k) = 1.21 V per DDR4 (tabella del reference: DDR4 1.21 V con 62K 1%).", X + 50, Y + 44)
p.R("R2", "62k 1%", X + 55, Y + 50, "VCC_DDR", "PMIC_FB3")
p.R("R3", "120k 1%", X + 65, Y + 50, "PMIC_FB3", "GND_D")
p.R("R4", "0R", X + 55, Y + 92, "VCC_1V8", "PMIC_FB5")
p.R("R5", "DNP", X + 65, Y + 92, "PMIC_FB5", "GND_D", dnp=True)
p.place("Connector:TestPoint", "TP1", "VCC_1V8", "TestPoint:TestPoint_Pad_D1.0mm", X + 80, Y + 88, {"1": "VCC_1V8"})
p.text("BUCK5 VCC_1V8 (1.8 V, seq 2) libero: la VCCQ dell'eMMC e VCCIO2 restano sull'AP2112K-1.8 come richiesto. Test point TP201.", X + 50, Y + 100)

# ---------------- LDO e switch ---------------------------------------------------------------------------------------------------
X, Y = 260, 175
p.text("LDO e switch (reference AIoT): 1 uF su ogni uscita, LDO4 4.7 uF, SWOUT1 10 uF. LDO1/LDO4/LDO9 (IMAGE, ACODEC) non usati: spenti di default, solo il condensatore.", X - 10, Y - 12)
LDO = [("C25", "1uF", "PMIC_LDO1"), ("C26", "1uF", "VDDA_0V9"), ("C27", "1uF", "VDDA0V9_PMU"), ("C28", "4.7uF", "PMIC_LDO4"),
       ("C29", "1uF", "VCCIO_SD"), ("C30", "1uF", "VCC3V3_PMU"), ("C31", "1uF", "VCCA_1V8"), ("C32", "1uF", "VCCA1V8_PMU"),
       ("C33", "1uF", "PMIC_LDO9"), ("C34", "1uF", "VCC3V3_SD"), ("C35", "10uF/10V", "VCC_3V3")]
for i, (ref, val, net) in enumerate(LDO):
    p.C(ref, val, X + 10 * i, Y, net, "GND_D", C0603 if val.startswith("10u") else C0402)
p.text("LDO2 VDDA_0V9, LDO3 VDDA0V9_PMU, LDO5 VCCIO_SD (VCCIO3), LDO6 VCC3V3_PMU (PMUIO1/2), LDO7 VCCA_1V8, LDO8 VCCA1V8_PMU, SWOUT1 VCC_3V3 (VCCIO4-7 e periferiche), SWOUT2 VCC3V3_SD (microSD).", X - 10, Y + 15)

# ---------------- gestione ---------------------------------------------------------------------------------------------------------
X, Y = 30, 120
p.text("Gestione: VREF 1 uF, VCC_1P8A/1P8D 1 uF, VCC_RTC 1 uF, quarzo 32.768 kHz Y201 con 2x 22 pF (reference). SDA/SCL 22R serie verso I2C0.", X - 10, Y - 12)
for i, (ref, val, net) in enumerate([("C36", "1uF", "PMIC_VREF"), ("C37", "1uF", "PMIC_1P8A"), ("C38", "1uF", "PMIC_1P8D"),
                                     ("C39", "1uF", "VCC3V3_SYS")]):
    p.C(ref, val, X + 10 * i, Y, net, "GND_D")
p.place("Device:Crystal", "Y1", "32.768kHz", "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", X + 55, Y, {"1": "PMIC_XIN", "2": "PMIC_XOUT"}, mpn="Q13FC1350000400")
p.C("C40", "22pF", X + 50, Y + 12, "PMIC_XIN", "GND_D")
p.C("C41", "22pF", X + 62, Y + 12, "PMIC_XOUT", "GND_D")
p.R("R6", "22R", X, Y + 25, "I2C0_SDA", "PMIC_SDA")
p.R("R7", "22R", X + 10, Y + 25, "I2C0_SCL", "PMIC_SCL")
X, Y = 30, 170
p.text("RESETB -> RESETn (nPOR del SoC) con 10k a VCC3V3_PMU e 100 nF. CLK32K (open drain) -> 0R -> CLK32K: CLK32K_IN del SoC (GPIO0_B0) e LPO dell'AP6256, 10k a VCC3V3_PMU.", X - 10, Y - 12)
p.text("PWRON con 100 nF e test point (accensione a mano). VDC: partitore da 5V_SYS, la PMIC parte da sola quando arriva l'alimentazione.", X - 10, Y - 7)
p.R("R8", "10k", X, Y + 5, "VCC3V3_PMU", "RESETn")
p.C("C42", "100nF", X + 10, Y + 5, "RESETn", "GND_D")
p.R("R9", "0R", X + 20, Y + 5, "PMIC_CLK32K", "CLK32K")
p.R("R10", "10k", X + 30, Y + 5, "VCC3V3_PMU", "CLK32K")
p.C("C43", "100nF", X + 40, Y + 5, "PMIC_PWRON", "GND_D")
p.place("Connector:TestPoint", "TP2", "PWRON", "TestPoint:TestPoint_Pad_D1.0mm", X + 50, Y + 5, {"1": "PMIC_PWRON"})
p.R("R11", "100k", X + 60, Y + 5, "5V_SYS", "PMIC_VDC")
p.R("R12", "22k", X + 70, Y + 5, "PMIC_VDC", "GND_D")
p.C("C44", "100nF", X + 80, Y + 5, "PMIC_VDC", "GND_D")

# ---------------- VDD_CPU: TCS4525 ------------------------------------------------------------------------------------------------
X, Y = 70, 250
p.text("VDD_CPU: TCS4525 (datasheet TCS Ver.1.0) come reference AIoT pag. 23 e ROCK 3A: VIN da 5V_SYS, I2C0 0x1C, VSEL da PMIC_SLEEP_H, EN da VCC3V3_PMU con 51k (parte dopo LDO6).", X - 40, Y - 30)
p.text("FB (A4) = VDD_CPU_COM (sfera M15 del SoC, sense remoto) con 100R verso VDD_CPU. Induttore 0.33 uH (datasheet: 0.33 o 0.47 uH), Isat > 8 A (picco 8 A). PGND/PG (B3) a GND.", X - 40, Y - 25)
p.place(TCS_ID, "U2", "TCS4525_WT", TCS_FP, X, Y, {
    "D1": "5V_SYS", "D2": "5V_SYS", "E1": "5V_SYS", "E2": "5V_SYS", "A2": "TCS_EN", "A1": "PMIC_SLEEP_H", "B1": "I2C0_SDA", "A3": "I2C0_SCL",
    "B4": "GND_D", "B3": "GND_D", "D3": "TCS_SW", "D4": "TCS_SW", "E3": "TCS_SW", "E4": "TCS_SW", "A4": "VDD_CPU_COM",
    "B2": "GND_D", "C1": "GND_D", "C2": "GND_D", "C3": "GND_D", "C4": "GND_D"}, mpn="TCS4525_WT")
p.C("C45", "22uF/10V", X - 35, Y + 25, "5V_SYS", "GND_D", C0805)
p.C("C46", "22uF/10V", X - 25, Y + 25, "5V_SYS", "GND_D", C0805)
p.R("R13", "51k", X - 15, Y + 25, "VCC3V3_PMU", "TCS_EN")
p.C("C47", "100nF", X - 5, Y + 25, "TCS_EN", "GND_D", dnp=True)
p.place("Device:L", "L6", "0.33uH/9A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", X + 35, Y - 5, {"1": "TCS_SW", "2": "VDD_CPU"}, mpn="XAL4020-331")
p.R("R14", "100R", X + 50, Y + 5, "VDD_CPU", "VDD_CPU_COM")
for i, (ref, val, fp, dnp) in enumerate([("C48", "1uF", C0402, False), ("C49", "22uF", C0603, False), ("C50", "22uF", C0603, False),
                                         ("C51", "22uF", C0603, False), ("C52", "22uF", C0603, True)]):
    p.C(ref, val, X + 60 + 10 * i, Y + 5, "VDD_CPU", "GND_D", fp, dnp=dnp)

# ---------------- VCC3V3_SYS: TPS563201 --------------------------------------------------------------------------------------------
X, Y = 260, 250
p.text("VCC3V3_SYS: TPS563201 da 5V_SYS, 3.3 V / 3 A, sempre acceso (EN 100k a 5V_SYS). Alimenta RK809-5 (VCC1-9), FUSB302B e i due LDO. Le periferiche stanno su VCC_3V3 (SWOUT1).", X - 40, Y - 22)
p.C("C53", "10uF/16V", X - 35, Y, "5V_SYS", "GND_D", C0805)
p.C("C54", "100nF", X - 25, Y, "5V_SYS", "GND_D")
p.place(TPS563_ID, "U3", "TPS563201DDCR", TPS563_FP, X, Y,
        {"VIN": "5V_SYS", "EN": "PERI_EN", "GND": "GND_D", "SW": "PERI_SW", "VBST": "PERI_BST", "VFB": "PERI_FB"}, mpn="TPS563201DDCR")
p.R("R15", "100k", X - 15, Y + 18, "5V_SYS", "PERI_EN")
p.C("C55", "100nF", X + 22, Y - 10, "PERI_BST", "PERI_SW")
p.place("Device:L", "L7", "2.2uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", X + 35, Y - 10, {"1": "PERI_SW", "2": "VCC3V3_SYS"}, mpn="XAL4020-222")
p.R("R16", "33.2k 1%", X + 48, Y - 5, "VCC3V3_SYS", "PERI_FB")
p.R("R17", "10k 1%", X + 48, Y + 10, "PERI_FB", "GND_D")
p.C("C56", "22uF/10V", X + 60, Y, "VCC3V3_SYS", "GND_D", C0805)
p.C("C57", "22uF/10V", X + 70, Y, "VCC3V3_SYS", "GND_D", C0805)
p.text("Vout = 0.768 V x (1 + 33.2k/10k) = 3.32 V. Carico stimato 2.5-3 A di picco (bucks RK809 + SWOUT1/2): al limite dei 3 A, vedi punti aperti.", X - 40, Y + 32)

# ---------------- LDO: VCC1V8_EMMC e VCC2V5_DDR -----------------------------------------------------------------------------------
X, Y = 420, 250
p.text("VCC1V8_EMMC: AP2112K-1.8TRG1 (LCSC C176944) da VCC3V3_SYS per VCCQ dell'eMMC e VCCIO2 (FLASH_VOL_SEL alto). EN da VCC3V3_PMU: sale con la sequenza della PMIC.", X - 40, Y - 22)
p.C("C58", "1uF/10V", X - 20, Y, "VCC3V3_SYS", "GND_D")
p.place(LDO18_ID, "U4", "AP2112K-1.8TRG1", LDO18_FP, X, Y,
        {"VIN": "VCC3V3_SYS", "GND": "GND_D", "EN": "VCC3V3_PMU", "NC": "NC", "VOUT": "VCC1V8_EMMC"}, mpn="AP2112K-1.8TRG1", lcsc="C176944")
p.C("C59", "1uF/10V", X + 25, Y, "VCC1V8_EMMC", "GND_D")
X, Y = 420, 300
p.text("VCC2V5_DDR (VPP della DDR4): AP2112K-2.5TRG1 da VCC3V3_SYS, EN da VCC3V3_PMU (seq 2, prima di VCC_DDR seq 3: VPP >= VDD come chiede JEDEC). Uscita 2x 4.7 uF + 2x 100 nF (reference).", X - 40, Y - 22)
p.C("C60", "1uF/10V", X - 20, Y, "VCC3V3_SYS", "GND_D")
p.place("Regulator_Linear:AP2112K-2.5", "U5", "AP2112K-2.5TRG1", "Package_TO_SOT_SMD:SOT-23-5", X, Y,
        {"VIN": "VCC3V3_SYS", "GND": "GND_D", "EN": "VCC3V3_PMU", "NC": "NC", "VOUT": "VCC2V5_DDR"}, mpn="AP2112K-2.5TRG1")
for i, (ref, val) in enumerate([("C61", "4.7uF"), ("C62", "4.7uF"), ("C63", "100nF"), ("C64", "100nF")]):
    p.C(ref, val, X + 25 + 10 * i, Y, "VCC2V5_DDR", "GND_D")
print("porte:", p.write(PRJ, 254.0, 38.1, f"{PRJ}/{LIBNAME}.kicad_sym"))
