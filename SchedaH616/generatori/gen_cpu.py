"""Foglio KiCad 10 'CPU' della scheda H616: SoC in 5 unità, clock, reset/FEL, UART0, interfaccia bus MIKILAB, espansore I/O. Serie 3xx."""
import json
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, box_symbol, multi_symbol, place_multi

PRJ = sys.argv[1]

# ---------------- ball map: SOLO dal datasheet ufficiale Allwinner H616 V1.0, tabella 4-2 (parse.py) ----------------
BALLS = json.load(open(os.path.join(SC, "h616_balls.json")))
# Unica differenza tra tabella 4-2 e figura 7-1 (pin map): AC_VRA1 e' D17 nella tabella, C17 nella figura.
# Il footprint EasyEDA (C5365289) ha la sfera in C17 e non in D17: si segue la figura.
assert BALLS.pop("D17")[0] == "AC_VRA1"
BALLS["C17"] = ["AC_VRA1", "AO", "AC+EPHY"]
assert len(BALLS) == 284

UNIT = {"SDRAM": 1, "GPIOC": 2, "GPIOF": 2, "GPIOL": 2, "GPIOG": 3, "GPIOH": 3, "GPIOI": 3,
        "System": 4, "LRADC": 4, "USB": 4, "HDMI": 4, "TV OUT": 4, "Audio Codec": 4, "AC+EPHY": 4, "DCXO": 4,
        "Power": 5, "Ground": 5}
TITLES = ["DRAM", "PC-PF-PL", "PG-PH-PI", "SISTEMA-USB-ANALOGICA", "ALIMENTAZIONE-GND"]


def natkey(t):
    m = re.match(r"([A-Z_]+?)(\d+)([PN]?)$", t[1])
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (t[1], 0, "")


units = [[] for _ in range(5)]
for ball, (name, typ, grp) in BALLS.items():
    units[UNIT[grp] - 1].append((ball, name))
units = [sorted(u, key=natkey) for u in units]
H616_SYM, H616_PINS = multi_symbol("H616", "H616", units, "Allwinner H616, TFBGA-284 14x12 mm passo 0.65 mm", w=22.86, titles=TITLES)

RAILS = ["VDD-CPU", "VDD-CPUFB", "VDD-SYS", "VDD-SYSFB", "VCC-DRAM", "VCC-1V8", "VCC-1V8-EMMC", "VCC-IO", "AP-RESET", "PMU-SCK", "PMU-SDA",
         "USB0_DP", "USB0_DM", "3V3_SYS", "PD_INT_N", "VBUS_SRC_EN", "PWR_SRC_ST", "EFUSE_FLT_N"]
BUSNETS = ["PWR_SPI_SCLK", "PWR_SPI_MOSI", "PWR_SPI_MISO", "PWR_SPI_INA239A_CS", "PWR_SPI_INA239B_CS", "PWR_SPI_DAC_CS",
           "VREF_ENABLE", "VBIAS_ENABLE", "DAC61402_FAULT", "MAIN_SPI_SCLK", "MAIN_SPI_MOSI", "MAIN_SPI_MISO", "MAIN_I2C_SDA",
           "MAIN_I2C_SCL", "MAIN_SPI_CS_MASTER", "MAIN_SPI_ADDR_0", "MAIN_SPI_ADDR_1", "MAIN_SPI_ADDR_2", "MAIN_SPI_PREFIX_0",
           "MAIN_SPI_PREFIX_1", "MAIN_SPI_PREFIX_2", "MAIN_SPI_ALERT_N", "MAIN_HIT_N"]
GP = ("DRAM_", "EMMC_", "SD_", "WL_", "BT_", "RGMII_", "PHY_", "GNSS_", "WIFI_", "USB1_", "SPI1_")
s = Sheet("CPU", "cpu.kicad_sch", 300, 2, RAILS + BUSNETS, GP, paper="A1")
s.add_sym("H616:H616", H616_SYM)
s.add_sym("H616:TCA6416APWR", box_symbol("H616", "TCA6416APWR",
          [("2", "VCCI", "L"), ("24", "VCCP", "L"), ("22", "SCL", "L"), ("23", "SDA", "L"), ("1", "~{INT}", "L"), ("3", "~{RESET}", "L"),
           ("21", "ADDR", "L"), ("12", "GND", "L"),
           ("4", "P00", "R"), ("5", "P01", "R"), ("6", "P02", "R"), ("7", "P03", "R"), ("8", "P04", "R"), ("9", "P05", "R"), ("10", "P06", "R"),
           ("11", "P07", "R"), ("13", "P10", "R"), ("14", "P11", "R"), ("15", "P12", "R"), ("16", "P13", "R"), ("17", "P14", "R"),
           ("18", "P15", "R"), ("19", "P16", "R"), ("20", "P17", "R")],
          "TI TCA6416A, espansore I2C 16 bit a doppia alimentazione (VCCI/VCCP), TSSOP-24", w=12.7))
for k in ["Device:R", "Device:C", "Device:Crystal_GND24", "Switch:SW_Push", "Connector_Generic:Conn_01x03",
          "Power_Protection:TPD4E05U06DQA"]:
    s.std(k)
C0402, C0603 = "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric"

# ---------------- net di ogni sfera ----------------------------------------------------------------------------------
DRAM_USED = {"SA0", "SA1", "SA2", "SA3", "SA4", "SA5", "SCS0", "SCS1", "SCKE0", "SCKE1", "SCKP", "SCKN", "SRST"} | \
    {f"SDQ{i}" for i in range(32)} | {f"SDQS{i}{p}" for i in range(4) for p in "PN"} | {f"SDQM{i}" for i in range(4)}
PIN = {
    # GPIO C: eMMC 8 bit su SMHC2 (VCC_PC 1.8 V); liberi solo ingressi open-drain con pull-up a 1.8 V
    "PC0": "EMMC_DS", "PC1": "EMMC_RST", "PC5": "EMMC_CLK", "PC6": "EMMC_CMD", "PC8": "EMMC_D3", "PC9": "EMMC_D4",
    "PC10": "EMMC_D0", "PC11": "EMMC_D5", "PC13": "EMMC_D1", "PC14": "EMMC_D6", "PC15": "EMMC_D2", "PC16": "EMMC_D7",
    "PC2": "IOX_INT_N", "PC7": "PD_INT_N", "PC12": "USB1_OC_N", "PC3": "SOC_BOOT_SEL1", "PC4": "SOC_BOOT_SEL2",
    # GPIO F: microSD su SMHC0, PF6 libero (rilevamento scheda sull'espansore)
    "PF0": "SD_D1", "PF1": "SD_D0", "PF2": "SD_CLK", "PF3": "SD_CMD", "PF4": "SD_D3", "PF5": "SD_D2", "PF6": "SOC_PREFIX_2",
    # GPIO L: S_TWI0 verso AXP313A, FUSB302B, TCA6416A (1.8 V)
    "PL0": "PMU-SCK", "PL1": "PMU-SDA",
    # GPIO G: AP6256 (SMHC1 + UART1 + 32 kHz), GNSS (UART2, PPS, EXTINT), bus
    "PG0": "WL_SDIO_CLK", "PG1": "WL_SDIO_CMD", "PG2": "WL_SDIO_D0", "PG3": "WL_SDIO_D1", "PG4": "WL_SDIO_D2", "PG5": "WL_SDIO_D3",
    "PG6": "BT_UART_TX", "PG7": "BT_UART_RX", "PG8": "BT_UART_RTS", "PG9": "BT_UART_CTS", "PG10": "WIFI_32K",
    "PG11": "MAIN_SPI_ALERT_N", "PG12": "MAIN_HIT_N", "PG13": "GNSS_PPS", "PG14": "GNSS_EXTINT",
    "PG15": "GNSS_UART2_TX", "PG16": "GNSS_UART2_RX", "PG17": "SOC_ADDR_0", "PG18": "SOC_ADDR_1", "PG19": "SOC_ADDR_2",
    # GPIO H: UART0, I2C del bus (TWI2), SPI1 condiviso e chip select
    "PH0": "UART0_TX", "PH1": "UART0_RX", "PH2": "MAIN_I2C_SCL", "PH3": "MAIN_I2C_SDA", "PH4": "PWR_SPI_INA239B_CS",
    "PH5": "MAIN_SPI_CS_MASTER", "PH6": "SPI1_CLK", "PH7": "SPI1_MOSI", "PH8": "SPI1_MISO", "PH9": "PWR_SPI_INA239A_CS",
    "PH10": "PWR_SPI_DAC_CS",
    # GPIO I: RGMII (EMAC0) verso RTL8211F, PI6 (RGMII_NULL) e PI16 liberi
    "PI0": "RGMII_RXD3", "PI1": "RGMII_RXD2", "PI2": "RGMII_RXD1", "PI3": "RGMII_RXD0", "PI4": "RGMII_RXCK", "PI5": "RGMII_RXCTL",
    "PI6": "SOC_PREFIX_0", "PI7": "RGMII_TXD3", "PI8": "RGMII_TXD2", "PI9": "RGMII_TXD1", "PI10": "RGMII_TXD0", "PI11": "RGMII_TXCK",
    "PI12": "RGMII_TXCTL", "PI13": "RGMII_CLKIN", "PI14": "PHY_MDC", "PI15": "PHY_MDIO", "PI16": "SOC_PREFIX_1",
    # sistema, USB, analogica, DCXO
    "FEL": "SOC_FEL", "RESET": "SOC_RESET", "USB0_DM": "USB0_DM", "USB0_DP": "USB0_DP", "USB1_DM": "USB1_DM", "USB1_DP": "USB1_DP",
    "VRA1": "SOC_VRA1", "VRA2": "SOC_VRA2", "AGND": "SOC_AGND", "REXT": "SOC_REXT", "AC_VRA1": "SOC_AC_VRA1", "DXIN": "DCXO_XIN", "DXOUT": "DCXO_XOUT",
    "DXLDO_OUT": "SOC_DXLDO",
    # alimentazioni
    "VCC_PC": "VCC-1V8-EMMC", "VCC_PG": "VCC-IO", "VCC_PI": "VCC-IO", "VCC_IO": "VCC-IO", "VCC_USB": "VCC-IO", "VCC_EPHY": "VCC-IO",
    "VCC_HDMI": "VCC-1V8", "VCC_TV": "VCC-1V8", "AVCC": "VCC-1V8", "AC_AVCC": "VCC-1V8", "VCC_DCXO": "VCC-1V8", "VCC_PLL": "VCC-1V8",
    "VDD18_DRAM": "VCC-1V8", "VCC_DRAM": "VCC-DRAM", "SZQ": "SOC_SZQ", "VDD_CPU": "VDD-CPU", "VDD_CPUFB": "VDD-CPUFB",
    "VDD_GPU": "VDD-SYS", "VDD_SYS": "VDD-SYS", "VDD_GPUFB": "VDD-SYSFB", "GND": "GND_D",
}


def net(num, name):
    if name in DRAM_USED:
        return "DRAM_" + name[1:]
    return PIN.get(name, "NC")  # non usati: SA6-SA16, SBA, SBG, SACT, SODT (LPDDR4), HDMI, TV, LINEOUT, EPHY, USB2/3, ...


place_multi(s, "H616:H616", "U1", "H616", "H616:BGA-284_L14.0-W12.0-P0.65-TL", H616_PINS, net,
            {1: (95, 140), 2: (95, 330), 3: (95, 470), 4: (560, 140), 5: (560, 330)}, mpn="H616")
s.text("CPU: Allwinner H616 (TFBGA-284, 0.65 mm). Ball map solo dal datasheet H616 V1.0 (tabella 4-2, verificata sulla figura 7-1). Serie 3xx.", 20, 15)
s.text("AC_VRA1 su C17 (figura 7-1, footprint EasyEDA e schema Orange Pi Zero2 v1.3; la tabella 4-2 dice D17 per errore). Mappa completa dei pin in docs/pinmap-h616.md.", 20, 20)
s.text("Net DRAM_*/EMMC_*/SD_*/WL_*/BT_*/RGMII_*/PHY_*/GNSS_*/WIFI_*/USB1_*/SPI1_* globali verso gli altri fogli.", 20, 25)

# ---------------- clock 24 MHz (DCXO) ------------------------------------------------------------------------------
X, Y = 260, 60
s.text("Clock: quarzo 24 MHz su DXIN/DXOUT (12 pF come la Zero3, da verificare col carico del quarzo scelto; 0R in serie su DXOUT), DXLDO_OUT 220 nF. L'H616 non ha pin per il quarzo 32 kHz: X32KFOUT (PG10) e' derivato internamente.", X - 10, Y - 15)
s.place("Device:Crystal_GND24", "Y1", "24MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", X + 15, Y,
        {"1": "DCXO_XIN", "3": "DCXO_XOUT_R", "2": "GND_D", "4": "GND_D"}, mpn="X322524MOB4SI")
s.C("C1", "12pF/50V", X, Y + 10, "DCXO_XIN", "GND_D")
s.C("C2", "12pF/50V", X + 30, Y + 10, "DCXO_XOUT_R", "GND_D")
s.R("R1", "0R", X + 40, Y + 10, "DCXO_XOUT", "DCXO_XOUT_R")
s.C("C3", "220nF/16V", X + 55, Y + 10, "SOC_DXLDO", "GND_D")

# ---------------- reset, FEL, UART0 ----------------------------------------------------------------------------------
X, Y = 260, 110
s.text("RESET (dominio VCC_PLL 1.8 V): 10k a VCC-1V8 + 1 nF + tasto, 100R in serie dal PWROK dell'AXP313A (AP-RESET), come la Zero3; FEL a GND con tasto (10k a VCC-IO). JTAG_SEL NC come sulla Zero2 (JTAG su PF). PLLTEST, LRADC liberi.", X - 10, Y - 12)
s.C("C4", "1nF/50V", X, Y, "SOC_RESET", "GND_D")
s.R("R38", "100R", X + 8, Y + 12, "AP-RESET", "SOC_RESET")
s.R("R39", "10k", X + 14, Y + 12, "VCC-1V8", "SOC_RESET")
s.place("Switch:SW_Push", "SW1", "RESET", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X + 20, Y, {"1": "SOC_RESET", "2": "GND_D"}, mpn="TS-1088-AR02016")
s.place("Switch:SW_Push", "SW2", "FEL", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X + 45, Y, {"1": "SOC_FEL", "2": "GND_D"}, mpn="TS-1088-AR02016")
s.R("R2", "10k", X + 60, Y, "VCC-IO", "SOC_FEL")
s.place("Connector_Generic:Conn_01x03", "J1", "UART0 debug", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", X + 85, Y,
        {"1": "UART0_TX", "2": "UART0_RX", "3": "GND_D"})
s.text("J301: 1 = TX del SoC (PH0), 2 = RX del SoC (PH1), 3 = GND. Livelli 3.3 V.", X + 70, Y + 12)

# ---------------- strap BOOT_SEL (PC3-PC6): tutti DNP -----------------------------------------------------------------
X, Y = 400, 110
s.text("Strap BOOT_SEL[4:1] = PC6/PC5/PC4/PC3: nessuno montato, come la Zero2 (la tabella livelli -> supporto e' nello User Manual H616 par. 3.4, non disponibile).", X - 10, Y - 12)
s.text("Footprint DNP 10k: pull-up a VCC-1V8-EMMC (= VCC_PC) e pull-down a GND su ogni linea. La Zero3 (boot SPI) usa PC3/PC4/PC6 alti e PC5 basso. Su PC5/PC6 (eMMC) metterli sui via, senza stub.", X - 10, Y - 7)
for i, n in enumerate(["SOC_BOOT_SEL1", "SOC_BOOT_SEL2", "EMMC_CLK", "EMMC_CMD"]):
    s.R(f"R{40 + 2 * i}", "10k", X + 20 * i, Y + 5, "VCC-1V8-EMMC", n, dnp=True)
    s.R(f"R{41 + 2 * i}", "10k", X + 20 * i + 8, Y + 5, n, "GND_D", dnp=True)

# ---------------- disaccoppiamento e analogica ------------------------------------------------------------------------
X, Y = 260, 160
s.text("Disaccoppiamento vicino alle sfere. 100 nF su VCC-PLL, VCC_DCXO, VDD18_DRAM, VCC_HDMI, VCC_TV (VCC-1V8) e su VCC_IO, VCC_PG/PI, VCC_USB, VCC_EPHY (VCC-IO), come la Zero2.", X - 10, Y - 10)
caps = [("C5", "10uF/6.3V", "VDD-CPU", C0603), ("C6", "2.2uF/6.3V", "VDD-CPU", C0402), ("C7", "2.2uF/6.3V", "VDD-CPU", C0402),
        ("C8", "1uF", "VDD-CPU", C0402), ("C9", "1uF", "VDD-CPU", C0402), ("C10", "10uF/6.3V", "VDD-SYS", C0603),
        ("C11", "2.2uF/6.3V", "VDD-SYS", C0402), ("C12", "2.2uF/6.3V", "VDD-SYS", C0402), ("C13", "1uF", "VDD-SYS", C0402),
        ("C14", "1uF", "VCC-DRAM", C0402), ("C15", "1uF", "VCC-DRAM", C0402), ("C16", "0.1uF", "VCC-DRAM", C0402),
        ("C17", "1uF", "VCC-1V8", C0402), ("C18", "0.1uF", "VCC-1V8", C0402), ("C19", "0.1uF", "VCC-1V8", C0402),
        ("C20", "0.1uF", "VCC-1V8", C0402), ("C21", "0.1uF", "VCC-1V8", C0402), ("C22", "0.1uF", "VCC-1V8", C0402),
        ("C23", "0.1uF", "VCC-1V8-EMMC", C0402), ("C24", "1uF", "VCC-IO", C0402), ("C25", "0.1uF", "VCC-IO", C0402),
        ("C26", "0.1uF", "VCC-IO", C0402), ("C27", "0.1uF", "VCC-IO", C0402), ("C28", "0.1uF", "VCC-IO", C0402)]
for i, (ref, val, n, fp) in enumerate(caps):
    s.C(ref, val, X + 10 * (i % 12), Y + 18 * (i // 12), n, "GND_D", fp)
X, Y = 260, 215
s.text("Analogica (codec e AC300 non usati): VRA1/VRA2 470 nF verso AGND, AGND a GND con 0R, AC_VRA1 1 uF. ZQ del controller DRAM 240R 1% a GND.", X - 10, Y - 10)
s.C("C29", "470nF/16V", X, Y, "SOC_VRA1", "SOC_AGND")
s.C("C30", "470nF/16V", X + 10, Y, "SOC_VRA2", "SOC_AGND")
s.R("R3", "0R", X + 20, Y, "SOC_AGND", "GND_D")
s.C("C31", "1uF", X + 30, Y, "SOC_AC_VRA1", "GND_D")
s.R("R4", "240R 1%", X + 45, Y, "SOC_SZQ", "GND_D")
s.R("R37", "150k 1%", X + 55, Y, "SOC_REXT", "SOC_AGND")
s.C("C34", "2.2uF/6.3V", X + 65, Y, "VCC-1V8", "GND_D")
s.C("C35", "10uF/6.3V", X + 75, Y, "VCC-1V8", "GND_D", C0603)
s.text("Come Orange Pi Zero2 (H616) v1.3: REXT (K18) 150k 1% ad AGND (R337), AVCC 2.2 uF (C334), AC_AVCC 10 uF (C335, come la Zero3), AC_VRA1 1 uF su C17.", X - 10, Y + 12)

# ---------------- interfaccia bus: SPI1 condiviso -----------------------------------------------------------------------
X, Y = 260, 260
s.text("SPI1 (PH6 CLK, PH7 MOSI, PH8 MISO) condiviso tra BUS_POWER e MAIN, chip select con cs-gpios. 33R serie per ramo su CLK/MOSI/MISO; EEPROM MAC locale su SPI1_* (foglio Rete).", X - 10, Y - 12)
s.text("Le MISO dei due rami si uniscono dopo i 33R: tutti gli slave (INA239, DAC61402, bus MAIN) devono tenere SDO in alta impedenza con CS alto. ADDR/PREFIX: 100R serie.", X - 10, Y - 7)
for i, (ref, a, b) in enumerate([("R5", "SPI1_CLK", "PWR_SPI_SCLK"), ("R6", "SPI1_MOSI", "PWR_SPI_MOSI"), ("R7", "SPI1_MISO", "PWR_SPI_MISO"),
                                 ("R8", "SPI1_CLK", "MAIN_SPI_SCLK"), ("R9", "SPI1_MOSI", "MAIN_SPI_MOSI"), ("R10", "SPI1_MISO", "MAIN_SPI_MISO")]):
    s.R(ref, "33R", X + 12 * i, Y + 5, a, b)
for i in range(3):
    s.R(f"R{11 + i}", "100R", X + 75 + 12 * i, Y + 5, f"SOC_ADDR_{i}", f"MAIN_SPI_ADDR_{i}")
    s.R(f"R{14 + i}", "100R", X + 111 + 12 * i, Y + 5, f"SOC_PREFIX_{i}", f"MAIN_SPI_PREFIX_{i}")
X, Y = 260, 300
s.text("Livelli di riposo: CS e CS_MASTER alti (10k), VREF_ENABLE basso (10k a GND), VBIAS_ENABLE basso (100k a GND), ALERT# e HIT# 4.7k, I2C del bus 2.2k, FAULT 10k.", X - 10, Y - 12)
pu = [("R17", "10k", "VCC-IO", "PWR_SPI_INA239A_CS"), ("R18", "10k", "VCC-IO", "PWR_SPI_INA239B_CS"), ("R19", "10k", "VCC-IO", "PWR_SPI_DAC_CS"),
      ("R20", "10k", "VCC-IO", "MAIN_SPI_CS_MASTER"), ("R21", "10k", "VREF_ENABLE", "GND_D"), ("R22", "100k", "VBIAS_ENABLE", "GND_D"),
      ("R23", "10k", "VCC-IO", "DAC61402_FAULT"), ("R24", "4.7k", "VCC-IO", "MAIN_SPI_ALERT_N"), ("R25", "4.7k", "VCC-IO", "MAIN_HIT_N"),
      ("R26", "2.2k", "VCC-IO", "MAIN_I2C_SCL"), ("R27", "2.2k", "VCC-IO", "MAIN_I2C_SDA")]
for i, (ref, val, a, b) in enumerate(pu):
    s.R(ref, val, X + 10 * (i % 11), Y, a, b)

X, Y = 260, 345
s.text("ESD bassa capacita TPD4E05U06DQA (0.5 pF, 5.5 V) sulle linee logiche di J1/J2, vicino ai connettori. Nessuna protezione su V_BIAS e riferimenti.", X - 10, Y - 15)
for k in range(6):
    g = BUSNETS[4 * k: 4 * k + 4]
    nets = {"1": g[0], "2": g[1], "4": g[2] if len(g) > 2 else "NC", "5": g[3] if len(g) > 3 else "NC", "3": "GND_D", "8": "GND_D"}
    s.place("Power_Protection:TPD4E05U06DQA", f"U{2 + k}", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 45 * (k % 3), Y + 40 * (k // 3), nets)

# ---------------- S_TWI0 (1.8 V) ed espansore TCA6416A ----------------------------------------------------------------------
X, Y = 320, 470
s.text("S_TWI0 (PL0/PL1, 1.8 V): AXP313A 0x36, FUSB302B 0x22, TCA6416A 0x20. Pull-up 2.2k a VCC-1V8. Gli open-drain su PC hanno pull-up a VCC-1V8-EMMC (= VCC_PC).", X - 60, Y - 55)
s.text("TCA6416A: VCCI = VCC-1V8 (lato I2C), VCCP = VCC-IO (porte a 3.3 V). Al reset tutte le porte sono ingressi: i pull-up/pull-down esterni fissano lo stato sicuro.", X - 60, Y - 50)
s.place("H616:TCA6416APWR", "U8", "TCA6416APWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", X, Y, {
    "2": "VCC-1V8", "24": "VCC-IO", "22": "PMU-SCK", "23": "PMU-SDA", "1": "IOX_INT_N", "3": "IOX_RESET_N", "21": "GND_D", "12": "GND_D",
    "4": "VREF_ENABLE", "5": "VBIAS_ENABLE", "6": "DAC61402_FAULT", "7": "USB1_VBUS_EN", "8": "VBUS_SRC_EN", "9": "PWR_SRC_ST",
    "10": "PHY_RST_N", "11": "PHY_INT_N", "13": "WL_REG_ON", "14": "BT_REG_ON", "15": "BT_WAKE", "16": "BT_HOST_WAKE",
    "17": "WL_HOST_WAKE", "18": "SD_DET", "19": "PHY_EE_CS_N", "20": "EFUSE_FLT_N"}, mpn="TCA6416APWR")
X2 = X + 55
for i, (ref, val, a, b) in enumerate([("R28", "2.2k", "VCC-1V8", "PMU-SCK"), ("R29", "2.2k", "VCC-1V8", "PMU-SDA"),
                                      ("R30", "10k", "VCC-1V8-EMMC", "IOX_INT_N"), ("R31", "10k", "VCC-1V8", "IOX_RESET_N"),
                                      ("R32", "10k", "VCC-1V8-EMMC", "PD_INT_N"), ("R33", "10k", "VCC-1V8-EMMC", "USB1_OC_N"),
                                      ("R34", "10k", "VCC-IO", "PWR_SRC_ST"), ("R35", "10k", "VCC-IO", "EFUSE_FLT_N"),
                                      ("R36", "0R", "VCC-IO", "3V3_SYS")]):
    s.R(ref, val, X2 + 10 * i, Y - 25, a, b)
s.C("C32", "0.1uF", X2, Y + 5, "VCC-1V8", "GND_D")
s.C("C33", "0.1uF", X2 + 10, Y + 5, "VCC-IO", "GND_D")
s.text("Porte: P00 VREF_ENABLE, P01 VBIAS_ENABLE, P02 DAC61402_FAULT (in), P03 USB1_VBUS_EN, P04 VBUS_SRC_EN, P05 PWR_SRC_ST (in), P06 PHY_RST_N, P07 PHY_INT_N (in),", X - 60, Y + 45)
s.text("P10 WL_REG_ON, P11 BT_REG_ON, P12 BT_WAKE, P13 BT_HOST_WAKE (in), P14 WL_HOST_WAKE (in), P15 SD_DET (in), P16 PHY_EE_CS_N, P17 EFUSE_FLT_N (in).", X - 60, Y + 50)
s.text("R336: 3V3_SYS (VDD del FUSB302B) da VCC-IO.", X - 60, Y + 55)
print("porte:", s.write(PRJ, 330.2, 38.1, f"{PRJ}/H616.kicad_sym"))
