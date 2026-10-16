"""Foglio KiCad 10 'PMIC' della scheda H616: AXP313A (come Orange Pi Zero3) e buck 3V3_PERI, serie 2xx."""
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, box_symbol

PRJ = sys.argv[1]
RAILS = ["5V_SYS", "VDD-CPU", "VDD-SYS", "VCC-DRAM", "VCC-1V8", "VCC-IO", "3V3_PERI", "VDD-CPUFB", "VDD-SYSFB",
         "VCC-DRAM-FB", "PMU-SCK", "PMU-SDA", "AP-RESET", "VCC-1V8-EMMC"]
C0603, C0805 = "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric"
p = Sheet("PMIC", "pmic.kicad_sch", 200, 5, RAILS)

# Pinout AXP313A dal datasheet X-Powers v1.0 (tabella pin, QFN-20 3x3, pin 21 = pad esposto PGND)
AXP = [("17", "VIN1", "L"), ("20", "VIN2", "L"), ("2", "VIN3", "L"), ("5", "SDA", "L"), ("6", "SCL", "L"), ("14", "PWRON", "L"),
       ("13", "PWROK", "L"), ("11", "IRQ", "L"), ("8", "VREF", "L"), ("10", "NC", "L"),
       ("18", "LX1", "R"), ("16", "DCDC1", "R"), ("19", "LX2", "R"), ("1", "DCDC2", "R"), ("3", "LX3", "R"), ("4", "DCDC3", "R"),
       ("15", "ALDO1", "R"), ("12", "DLDO1", "R"), ("7", "RTCLDO", "R"), ("9", "GND", "R"), ("21", "PGND", "R")]
p.add_sym("H616:AXP313A", box_symbol("H616", "AXP313A", AXP, "X-Powers AXP313A, PMIC 3 DCDC + 3 LDO, QFN-20 3x3 mm", w=12.7))
for k in ["Device:R", "Device:C", "Device:L", "Regulator_Switching:TPS563201", "Connector:TestPoint", "Regulator_Linear:AP2112K-1.8"]:
    p.std(k)

p.text("PMIC AXP313A (datasheet X-Powers v1.0) come su Orange Pi Zero3 (H618 + AXP313A): VIN 3.0-5.5 V da 5V_SYS, I2C 0x36 su S_TWI0 (PL0/PL1). Serie 2xx.", 20, 15)
p.text("DCDC1 VDD-SYS 0.9 V (VDD_SYS + VDD_GPU, max 0.99 V) 1.5 A, DCDC2 VDD-CPU 0.81-1.1 V 3 A, DCDC3 VCC-DRAM 1.1 V (LPDDR4 VDD2/VDDQ) 2 A,", 20, 20)
p.text("ALDO1 VCC-1V8 300 mA (VCC_PLL, VDD18_DRAM, DCXO, AVCC, AC_AVCC, HDMI, TV, LPDDR4 VDD1, TCA6416A VCCI), DLDO1 VCC-IO 3.3 V 500 mA (VCC_IO/PG/PI/USB). RTCLDO non usato (H616 senza VCC_RTC).", 20, 25)

X0, Y0 = 150, 120
p.place("H616:AXP313A", "U1", "AXP313A", "H616:QFN-20_L3.0-W3.0-P0.40-BL-EP1.7", X0, Y0, {
    "17": "5V_SYS", "20": "5V_SYS", "2": "5V_SYS", "5": "PMU-SDA", "6": "PMU-SCK", "14": "PMU_PWRON", "13": "AP-RESET",
    "11": "NC", "8": "PMU_VREF", "10": "NC", "18": "PMU_LX1", "16": "VDD-SYSFB", "19": "PMU_LX2", "1": "VDD-CPUFB",
    "3": "PMU_LX3", "4": "VCC-DRAM-FB", "15": "VCC-1V8", "12": "VCC-IO", "7": "PMU_RTCLDO", "9": "GND_D", "21": "GND_D"}, mpn="AXP313A")

X, Y = 25, 60
p.text("Ingressi VIN1/VIN2/VIN3: 22 uF + 100 nF ciascuno vicino ai pin (Zero3: 22 uF). Pin 8 (VREF, GPO sulla Zero3) 1 uF.", X, Y - 8)
for i, (ref, val, net, fp) in enumerate([("C1", "22uF/10V", "5V_SYS", C0603), ("C2", "22uF/10V", "5V_SYS", C0603), ("C3", "22uF/10V", "5V_SYS", C0603),
                                         ("C4", "100nF", "5V_SYS", None), ("C5", "100nF", "5V_SYS", None), ("C6", "100nF", "5V_SYS", None),
                                         ("C7", "1uF/10V", "PMU_VREF", None)]):
    if fp:
        p.C(ref, val, X + 10 * i, Y, net, "GND_D", fp)
    else:
        p.C(ref, val, X + 10 * i, Y, net, "GND_D")

X, Y = 230, 60
p.text("Uscite come la Zero3: VDD-GPU/SYS e VDD-CPU 2x47 uF + 1 uF + 100 nF, VCC-DRAM 2x47 uF + 1 uF + 100 nF, DLDO1 47 uF + 100 nF, RTCLDO 4.7 uF (non usato dall'H616). DCDC: induttori 1 uH (datasheet: Isat > 1.3 x carico, DCR < 30 mohm), uscite >= 10 uF. FB con sense remoto: DCDC1 da VDD_GPUFB (F8), DCDC2 da VDD_CPUFB (L8), DCDC3 dalla LPDDR4.", X - 10, Y - 12)
p.place("Device:L", "L1", "1uH/2.5A", "Inductor_SMD:L_1008_2520Metric", X, Y, {"1": "PMU_LX1", "2": "VDD-SYS"}, mpn="1uH 2.5A DCR<30m")
p.C("C8", "47uF/6.3V", X + 10, Y, "VDD-SYS", "GND_D", C0603)
p.C("C9", "47uF/6.3V", X + 20, Y, "VDD-SYS", "GND_D", C0603)
p.C("C24", "1uF", X + 27, Y, "VDD-SYS", "GND_D")
p.C("C27", "100nF", X + 32, Y + 8, "VDD-SYS", "GND_D")
p.place("Device:L", "L2", "1uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", X + 35, Y, {"1": "PMU_LX2", "2": "VDD-CPU"}, mpn="XAL4020-102")
p.C("C10", "47uF/6.3V", X + 45, Y, "VDD-CPU", "GND_D", C0603)
p.C("C11", "47uF/6.3V", X + 55, Y, "VDD-CPU", "GND_D", C0603)
p.C("C25", "1uF", X + 62, Y, "VDD-CPU", "GND_D")
p.C("C28", "100nF", X + 67, Y + 8, "VDD-CPU", "GND_D")
p.place("Device:L", "L3", "1uH/3A", "Inductor_SMD:L_1008_2520Metric", X + 70, Y, {"1": "PMU_LX3", "2": "VCC-DRAM"}, mpn="1uH 3A DCR<30m")
p.C("C12", "47uF/6.3V", X + 80, Y, "VCC-DRAM", "GND_D", C0603)
p.C("C13", "1uF", X + 90, Y, "VCC-DRAM", "GND_D")
p.C("C29", "47uF/6.3V", X + 100, Y, "VCC-DRAM", "GND_D", C0603)
p.C("C30", "100nF", X + 110, Y, "VCC-DRAM", "GND_D")

X, Y = 230, 110
p.text("LDO: ALDO1 VCC-1V8 e DLDO1 VCC-IO con 4.7 uF (datasheet: >= 1 uF). RTCLDO libero (LDO non usato: pin flottante, nessun condensatore).", X - 10, Y - 10)
p.C("C14", "4.7uF/10V", X, Y, "VCC-1V8", "GND_D")
p.C("C15", "47uF/6.3V", X + 10, Y, "VCC-IO", "GND_D", C0603)
p.C("C31", "4.7uF/10V", X + 30, Y, "PMU_RTCLDO", "GND_D")
p.C("C26", "100nF", X + 20, Y, "VCC-IO", "GND_D")

X, Y = 230, 150
p.text("Controllo: PWROK = AP-RESET -> 100R -> RESET del SoC (foglio CPU), pull-up 10k a VCC-1V8. Accensione all'arrivo di VIN; PWRON su test point. IRQ non collegato (la Zero3 lo porta su PC9 con 0R; qui non ci sono GPIO liberi sicuri: PC3/PC4 sono strap BOOT_SEL).", X - 10, Y - 12)
p.R("R1", "10k", X, Y, "VCC-1V8", "AP-RESET")
p.place("Connector:TestPoint", "TP1", "PWRON", "TestPoint:TestPoint_Pad_D1.0mm", X + 15, Y, {"1": "PMU_PWRON"})
p.C("C16", "100nF", X + 25, Y, "PMU_PWRON", "GND_D")

X, Y = 60, 200
p.text("3V3_PERI: TPS563201 da 5V_SYS, 3.3 V / 3 A per AP6256 (VBAT), RTL8211F, NEO-M9N, eMMC VCC, microSD, EEPROM MAC. EN da VCC-IO (parte dopo DLDO1).", X - 40, Y - 22)
p.C("C17", "10uF/16V", X - 35, Y, "5V_SYS", "GND_D", C0805)
p.C("C18", "100nF", X - 25, Y, "5V_SYS", "GND_D")
p.place("Regulator_Switching:TPS563201", "U2", "TPS563201DDCR", "Package_TO_SOT_SMD:SOT-23-6", X, Y,
        {"VIN": "5V_SYS", "EN": "PERI_EN", "GND": "GND_D", "SW": "PERI_SW", "VBST": "PERI_BST", "VFB": "PERI_FB"}, mpn="TPS563201DDCR")
p.R("R2", "0R", X - 15, Y + 18, "VCC-IO", "PERI_EN")
p.R("R3", "100k", X - 25, Y + 18, "5V_SYS", "PERI_EN", dnp=True)
p.C("C19", "100nF", X + 22, Y - 10, "PERI_BST", "PERI_SW")
p.place("Device:L", "L4", "2.2uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", X + 35, Y - 10, {"1": "PERI_SW", "2": "3V3_PERI"}, mpn="XAL4020-222")
p.R("R4", "33.2k 1%", X + 48, Y - 5, "3V3_PERI", "PERI_FB")
p.R("R5", "10k 1%", X + 48, Y + 10, "PERI_FB", "GND_D")
p.C("C20", "22uF/10V", X + 60, Y, "3V3_PERI", "GND_D", C0805)
p.C("C21", "22uF/10V", X + 70, Y, "3V3_PERI", "GND_D", C0805)
p.text("Vout = 0.768 V x (1 + R204/R205) = 3.32 V. R203 DNP: alternativa per accenderlo sempre da 5V_SYS.", X - 40, Y + 32)
X, Y = 200, 200
p.text("VCC-1V8-EMMC: LDO AP2112K-1.8TRG1 (LCSC C176944, 600 mA) da 3V3_PERI per VCCQ eMMC (fino a ~132 mA in HS400) e VCC_PC dell'H616: banco PC ed eMMC salgono insieme. Scarica ALDO1.", X - 30, Y - 22)
p.text("EN legato a VIN: parte con 3V3_PERI, cioe' dopo DLDO1 (EN del TPS563201 da VCC-IO). 1 uF in ingresso e in uscita.", X - 30, Y - 17)
p.C("C22", "1uF/10V", X - 20, Y, "3V3_PERI", "GND_D")
p.place("Regulator_Linear:AP2112K-1.8", "U3", "AP2112K-1.8TRG1", "Package_TO_SOT_SMD:SOT-23-5", X, Y,
        {"VIN": "3V3_PERI", "GND": "GND_D", "EN": "3V3_PERI", "NC": "NC", "VOUT": "VCC-1V8-EMMC"}, mpn="AP2112K-1.8TRG1")
p.C("C23", "1uF/10V", X + 25, Y, "VCC-1V8-EMMC", "GND_D")
print("porte:", p.write(PRJ, 254.0, 38.1, f"{PRJ}/H616.kicad_sym"))
