"""Schema della scheda i.MX 6ULL: fogli CPU, DDR3L, Alimentazione, Bus MIKILAB, Storage, USB, Rete, Radio, GNSS.
Uso: python3 gen_sch.py ../progetto-kicad
I riferimenti dei componenti in BOM sono quelli di bom/bom-imx6ull.csv; i passivi sono numerati per foglio (R1xx CPU, R2xx DDR, ...).
Tutte le resistenze e i condensatori sono 0603 (Sheet.group)."""
import json
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, box_symbol, multi_symbol, place_multi, write_all, GROUPS
from kilib import LIBNAME, extract, mik

PRJ = sys.argv[1]
BALLS = {k: v["name"] for k, v in json.load(open(os.path.join(SC, "imx6ull_balls.json"))).items()}
assert len(BALLS) == 289
GND = "GND_D"
V33 = "3V3"
V135 = "V1P35"
V14 = "V1P4"
V5 = "5V_SYS"
SNVS = "VDD_SNVS"

# ================================ mappa funzionale delle sfere del 6ULL ==========================================================
# Nome della sfera -> net. Funzioni e ALT: linux imx6ul-pinfunc.h; sfere: tabelle 90/91 di IMX6ULLCEC Rev 1.2.
NET = {
    # alimentazioni
    "ADC_VREFH": V33, "VDDA_ADC_3P3": V33, "DRAM_VREF": "DDR_VREF", "GPANIO": "NC", "NGND_KEL0": GND, "VSS": GND,
    "NVCC_CSI": V33, "NVCC_DRAM": V135, "NVCC_DRAM_2P5": "VDD_HIGH_CAP", "NVCC_ENET": V33, "NVCC_GPIO": V33, "NVCC_LCD": V33,
    "NVCC_NAND": V33, "NVCC_PLL": "NVCC_PLL", "NVCC_SD1": V33, "NVCC_UART": V33, "VDD_ARM_CAP": "VDD_ARM_CAP",
    "VDD_HIGH_CAP": "VDD_HIGH_CAP", "VDD_HIGH_IN": V33, "VDD_SNVS_CAP": "VDD_SNVS_CAP", "VDD_SNVS_IN": SNVS,
    "VDD_SOC_CAP": "VDD_SOC_CAP", "VDD_SOC_IN": V14, "VDD_USB_CAP": "VDD_USB_CAP",
    # sistema
    "BOOT_MODE0": "BOOT_MODE0", "BOOT_MODE1": "BOOT_MODE1", "TEST_MODE": GND, "JTAG_MOD": "JTAG_MOD", "POR_B": "POR_B", "ONOFF": "ONOFF",
    "XTALI": "XTALI", "XTALO": "XTALO", "RTC_XTALI": "RTC_XTALI", "RTC_XTALO": "RTC_XTALO",
    "LCD_DATA04": "BOOT_CFG1_4", "LCD_DATA06": "BOOT_CFG1_6",
    # USB
    "USB_OTG1_DP": "USB1_DP", "USB_OTG1_DN": "USB1_DM", "USB_OTG1_VBUS": "VBUS1", "USB_OTG2_DP": "USB2_DP", "USB_OTG2_DN": "USB2_DM", "USB_OTG2_VBUS": V5,
    # console UART1, GNSS UART3, GPT1 CAPTURE1/2 sui pad UART2, BT su UART8 (pad ENET2)
    "UART1_TX_DATA": "UART1_TX", "UART1_RX_DATA": "UART1_RX", "UART3_TX_DATA": "GNSS_UART_RX", "UART3_RX_DATA": "GNSS_UART_TX",
    "UART2_TX_DATA": "GNSS_PPS", "UART2_RX_DATA": "GNSS_EXTINT",
    "ENET2_TX_DATA1": "BT_UART_RX", "ENET2_TX_EN": "BT_UART_TX", "ENET2_RX_ER": "BT_UART_CTS",
    # uSDHC1 microSD
    "SD1_CLK": "SD1_CLK_S", "SD1_CMD": "SD1_CMD", "SD1_DATA0": "SD1_D0", "SD1_DATA1": "SD1_D1", "SD1_DATA2": "SD1_D2", "SD1_DATA3": "SD1_D3", "UART1_RTS_B": "SD1_CD_N",
    # uSDHC2 Wi-Fi (pad NAND)
    "NAND_RE_B": "SD2_CLK_S", "NAND_WE_B": "SD2_CMD", "NAND_DATA00": "SD2_D0", "NAND_DATA01": "SD2_D1", "NAND_DATA02": "SD2_D2", "NAND_DATA03": "SD2_D3",
    # QSPI1 porta A (tabella 79)
    "NAND_WP_B": "QSPI_SCLK_S", "NAND_DQS": "QSPI_CS_N", "NAND_READY_B": "QSPI_D0", "NAND_CE0_B": "QSPI_D1", "NAND_CE1_B": "QSPI_D2", "NAND_CLE": "QSPI_D3",
    # ENET1 RMII
    "ENET1_TX_DATA0": "RMII_TXD0", "ENET1_TX_DATA1": "RMII_TXD1", "ENET1_TX_EN": "RMII_TXEN", "ENET1_TX_CLK": "RMII_REFCLK",
    "ENET1_RX_DATA0": "RMII_RXD0", "ENET1_RX_DATA1": "RMII_RXD1", "ENET1_RX_EN": "RMII_CRSDV", "ENET1_RX_ER": "RMII_RXER",
    "GPIO1_IO06": "PHY_MDIO", "GPIO1_IO07": "PHY_MDC", "GPIO1_IO01": "PHY_RST_N",
    # I2C1 EEPROM MAC (GPIO1_IO02/03), I2C2 bus MIKILAB (pad CSI)
    "GPIO1_IO02": "I2C1_SCL", "GPIO1_IO03": "I2C1_SDA", "CSI_HSYNC": "MAIN_I2C_SCL", "CSI_VSYNC": "MAIN_I2C_SDA",
    # BUS_POWER su ECSPI2 (pad UART4/UART5, per alleggerire il fanout del lato DRAM del BGA), MAIN su ECSPI1 (pad CSI_DATA04-07), CS extra via cs-gpios
    "UART4_TX_DATA": "ECSPI2_SCLK", "UART4_RX_DATA": "PWR_SPI_INA239A_CS", "UART5_TX_DATA": "ECSPI2_MOSI", "UART5_RX_DATA": "ECSPI2_MISO",
    "UART2_CTS_B": "PWR_SPI_INA239B_CS", "UART2_RTS_B": "PWR_SPI_DAC_CS",
    "CSI_DATA04": "ECSPI1_SCLK", "CSI_DATA05": "MAIN_SPI_CS_MASTER", "CSI_DATA06": "ECSPI1_MOSI", "CSI_DATA07": "ECSPI1_MISO",
    # linee lente del bus su GPIO
    "NAND_DATA04": "SOC_ADDR_0", "NAND_DATA05": "SOC_ADDR_1", "NAND_DATA06": "SOC_ADDR_2", "NAND_DATA07": "SOC_PREFIX_0",
    "NAND_ALE": "SOC_PREFIX_1", "LCD_CLK": "SOC_PREFIX_2", "LCD_ENABLE": "MAIN_SPI_ALERT_N", "LCD_HSYNC": "MAIN_HIT_N",
    "LCD_VSYNC": "VREF_ENABLE", "LCD_RESET": "VBIAS_ENABLE", "ENET2_RX_EN": "DAC61402_FAULT",
    # controlli Wi-Fi/BT
    "ENET2_RX_DATA0": "WL_DIS_N", "ENET2_RX_DATA1": "BT_DIS_N", "UART3_RTS_B": "WL_WAKE_HOST", "UART3_CTS_B": "BT_WAKE_HOST", "UART1_CTS_B": "BT_HOST_WAKE",
    # controlli USB e alimentazione
    "GPIO1_IO04": "HUB_RST_N", "GPIO1_IO05": "USB2_VBUS_EN", "GPIO1_IO08": "USB2_OC_N", "GPIO1_IO09": "PWR_SRC_ST",
}
for i in range(16):
    NET[f"DRAM_ADDR{i:02d}"] = f"DDR_A{i}"
    NET[f"DRAM_DATA{i:02d}"] = f"DDR_DQ{i}"
for k, v in {"DRAM_CAS_B": "DDR_CAS_N", "DRAM_RAS_B": "DDR_RAS_N", "DRAM_SDWE_B": "DDR_WE_N", "DRAM_CS0_B": "DDR_CS_N", "DRAM_ODT0": "DDR_ODT",
             "DRAM_RESET": "DDR_RESET_N", "DRAM_SDBA0": "DDR_BA0", "DRAM_SDBA1": "DDR_BA1", "DRAM_SDBA2": "DDR_BA2", "DRAM_SDCKE0": "DDR_CKE",
             "DRAM_SDCLK0_P": "DDR_CK_P", "DRAM_SDCLK0_N": "DDR_CK_N", "DRAM_SDQS0_P": "DDR_LDQS_P", "DRAM_SDQS0_N": "DDR_LDQS_N",
             "DRAM_SDQS1_P": "DDR_UDQS_P", "DRAM_SDQS1_N": "DDR_UDQS_N", "DRAM_DQM0": "DDR_LDM", "DRAM_DQM1": "DDR_UDM", "DRAM_ZQPAD": "SOC_DDR_ZQ"}.items():
    NET[k] = v
for n in NET:
    assert n in BALLS.values(), n
json.dump(NET, open(os.path.join(SC, "imx6ull_net.json"), "w"), indent=0, sort_keys=True)

# ================================ CPU ==================================================================================================
s = Sheet("CPU", "cpu.kicad_sch", 100, 2, paper="A0")
UNITS = [
    ("DDR3L", lambda n: n.startswith("DRAM_")),
    ("Alimentazioni", lambda n: n in ("ADC_VREFH", "VDDA_ADC_3P3", "NGND_KEL0", "GPANIO") or n.startswith(("NVCC_", "VDD_"))),
    ("Masse", lambda n: n == "VSS"),
    ("LCD / BOOT_CFG", lambda n: n.startswith(("LCD_", "BOOT_"))),
    ("NAND (QSPI, uSDHC2, GPIO) e SD1", lambda n: n.startswith(("NAND_", "SD1_"))),
    ("CSI (ECSPI1/2, I2C2) e ENET2", lambda n: n.startswith(("CSI_", "ENET2_"))),
    ("ENET1, UART, GPIO1, JTAG", lambda n: n.startswith(("ENET1_", "UART", "GPIO1_", "JTAG_"))),
    ("USB, clock, SNVS, sistema", lambda n: True),
]
assigned, unit_pins = set(), []
for title, test in UNITS:
    lst = sorted(((b, n) for b, n in BALLS.items() if b not in assigned and test(n)), key=lambda t: (t[1], t[0]))
    assigned.update(b for b, _ in lst)
    unit_pins.append(lst)
assert len(assigned) == 289
SYM, PM = multi_symbol(LIBNAME, "MCIMX6Y2CVM08AB", unit_pins, "NXP i.MX 6ULL, MAPBGA-289 14x14 mm passo 0.8", titles=[u[0] for u in UNITS])
s.add_sym(f"{LIBNAME}:MCIMX6Y2CVM08AB", SYM)
s.note("U1 NXP MCIMX6Y2CVM08AB (i.MX 6ULL full feature, 792 MHz, -40..105 C, MAPBGA-289 14x14 mm passo 0.8). Sfere: IMX6ULLCEC Rev 1.2 tabelle 90/91, confrontate con la netlist di una scheda KiCad aperta: 289/289.")
s.note("Boot: BOOT_MODE[1:0]=10 (boot interno) e BOOT_CFG tutti bassi con i pull-down interni da 100k (tabella 78) = QSPI, come SW601 tutto OFF sulla EVK NXP. Pull-up DNP su LCD_DATA04 e LCD_DATA06 (microSD). Se QSPI e' vuota il ROM va in download seriale su USB_OTG1.")
s.note("Assegnazione: ECSPI2=BUS_POWER, ECSPI1=MAIN, I2C2=bus MIKILAB, I2C1=EEPROM MAC, UART1=console, UART3=GNSS, UART8=BT, GPT1 CAPTURE1=PPS (UART2_TX), CAPTURE2=EXTINT (UART2_RX). Elenco completo in docs/pinmap-imx6ull.md.")
pos, X, Y = {}, 75.0, 60.0
for uu, lst in enumerate(unit_pins, start=1):
    half = (len(lst) + 1) // 2
    h = (half + 2) * 2.54 + 18
    if Y + h > 480:
        X, Y = X + 140, 60.0
    pos[uu] = (X, Y + h / 2)
    Y += h + 6
place_multi(s, f"{LIBNAME}:MCIMX6Y2CVM08AB", "U1", "MCIMX6Y2CVM08AB", "Package_BGA:MAPBGA-289_14x14mm_Layout17x17_P0.8mm", PM,
            lambda num, nm: NET.get(nm, "NC"), pos, mpn="MCIMX6Y2CVM08AB")
s.cx, s.cy, s.rowh = 25.0, 500.0, 0.0
s.group("VDD_ARM_CAP / VDD_SOC_CAP: uscite LDO interni, solo condensatori", [("C", "22uF", "VDD_ARM_CAP", GND), ("C", "1uF", "VDD_ARM_CAP", GND), ("C", "1uF", "VDD_ARM_CAP", GND),
        ("C", "22uF", "VDD_SOC_CAP", GND), ("C", "1uF", "VDD_SOC_CAP", GND), ("C", "1uF", "VDD_SOC_CAP", GND), ("C", "1uF", "VDD_SOC_CAP", GND)])
s.group("VDD_HIGH_CAP (a NVCC_DRAM_2P5), NVCC_PLL, VDD_SNVS_CAP, VDD_USB_CAP", [("C", "10uF", "VDD_HIGH_CAP", GND), ("C", "1uF", "VDD_HIGH_CAP", GND), ("C", "1uF", "VDD_HIGH_CAP", GND),
        ("C", "10uF", "NVCC_PLL", GND), ("C", "1uF", "NVCC_PLL", GND), ("C", "1uF", "VDD_SNVS_CAP", GND), ("C", "10uF", "VDD_USB_CAP", GND), ("C", "1uF", "VDD_USB_CAP", GND)])
s.group("VDD_SOC_IN 1.4 V", [("C", "22uF", V14, GND), ("C", "10uF", V14, GND)] + [("C", "100nF", V14, GND)] * 3)
s.group("VDD_HIGH_IN e NVCC 3.3 V (una per dominio: CSI, ENET, GPIO, LCD, NAND, SD1, UART), ADC", [("C", "22uF", V33, GND), ("C", "1uF", V33, GND)] + [("C", "100nF", V33, GND)] * 8)
s.group("NVCC_DRAM 1.35 V (lato SoC)", [("C", "22uF", V135, GND)] + [("C", "100nF", V135, GND)] * 4)
s.group("VDD_SNVS_IN", [("C", "1uF", SNVS, GND), ("C", "100nF", SNVS, GND)])
Y1_ID, Y1_FP = s.mik("X322524MOB4SI")
s.ic(Y1_ID, "Y1", "24MHz", Y1_FP, {"1": "XTALI", "3": "XTALO", "2": GND, "4": GND}, mpn="X322524MOB4SI")
s.group("Carico 24 MHz (CL da verificare sul quarzo YXC)", [("C", "18pF", "XTALI", GND), ("C", "18pF", "XTALO", GND)])
Y2_ID, Y2_FP = s.mik("Q13FC1350000400")
s.ic(Y2_ID, "Y2", "32.768kHz", f"{LIBNAME}:" + Y2_FP.split(":")[1], {"1": "RTC_XTALI", "2": "RTC_XTALO"}, mpn="Q13FC13500004", lcsc="C32346")
s.group("Carico RTC: circa 2xCL meno parassite (datasheet, tabella 3)", [("C", "12pF", "RTC_XTALI", GND), ("C", "12pF", "RTC_XTALO", GND)])
s.group("Boot: BOOT_MODE=10 (DNP per forzare 01 = download seriale); BOOT_CFG1[4] e [6] DNP; JTAG_MOD a GND con 4.7k (tabella 3); BOOT_MODE riferiti a VDD_SNVS",
        [("R", "10k", "BOOT_MODE1", SNVS), ("R", "10k", "BOOT_MODE1", GND, True), ("R", "10k", "BOOT_MODE0", GND), ("R", "10k", "BOOT_MODE0", SNVS, True),
         ("R", "10k", "BOOT_CFG1_4", V33, True), ("R", "10k", "BOOT_CFG1_6", V33, True), ("R", "4.7k", "JTAG_MOD", GND)])
SW_ID, SW_FP = s.mik("TS-1088-AR02016")
s.ic(SW_ID, "SW1", "RESET", SW_FP, {"1": "POR_B", "2": GND}, mpn="TS-1088-AR02016", lcsc="C720477")
s.ic(SW_ID, "SW2", "ONOFF", SW_FP, {"1": "ONOFF", "2": GND}, mpn="TS-1088-AR02016", lcsc="C720477")
s.std("Connector_Generic:Conn_01x03")
s.ic("Connector_Generic:Conn_01x03", "J6", "Console UART1", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     {"1": "UART1_TX", "2": "UART1_RX", "3": GND}, mpn="2.54-1*3P", lcsc="C49257")
s.group("Pull-up open drain USB2_OC_N, PWR_SRC_ST", [("R", "10k", V33, "USB2_OC_N"), ("R", "10k", V33, "PWR_SRC_ST")])
s.flags(["VDD_HIGH_CAP", "VDD_ARM_CAP", "VDD_SOC_CAP", "NVCC_PLL", "VDD_SNVS_CAP", "VDD_USB_CAP"])

# ================================ DDR3L ===================================================================================================
d = Sheet("DDR3L", "ddr3l.kicad_sch", 200, 3)
t = extract("Memory_RAM", "MT41K256M16HA")
i = t.find('(number "M7"')
j = t.rfind('(name "NC"', 0, i)
k = t.rfind("(pin ", 0, j)
t = t[:k] + re.sub(r"\(pin no_connect", "(pin input", t[k:j], 1).replace("(hide yes)", "") + '(name "A15"' + t[j + len('(name "NC"'):]
t = t.replace("Memory_RAM:MT41K256M16HA", f"{LIBNAME}:MT41K512M16HA").replace("MT41K256M16HA", "MT41K512M16HA")
d.add_sym(f"{LIBNAME}:MT41K512M16HA", t)
d.note("U2 Micron MT41K512M16HA-107:A, 8 Gb x16 = 1 GB, FBGA-96 9x14 passo 0.8, a 1.35 V. Un solo chip punto-punto: niente VTT. Simbolo da MT41K256M16HA di KiCad con A15 su M7 (ball map JEDEC x16).")
d.note("VREF a partitore 1k 0.5% con 100 nF su ogni resistenza (datasheet 6ULL, tabella 3), unica per DRAM_VREF, VREFCA, VREFDQ. ZQ 240R 1% su SoC e DRAM. RESET# e CKE con 10k a GND. CK con 100R differenziale vicino alla DRAM (da confermare in simulazione).")
ddr = {"A10/AP": "DDR_A10", "A12/~{BC}": "DDR_A12", "A15": "DDR_A15", "~{RAS}": "DDR_RAS_N", "~{CAS}": "DDR_CAS_N", "~{WE}": "DDR_WE_N", "~{CS}": "DDR_CS_N",
       "ODT": "DDR_ODT", "CKE": "DDR_CKE", "CK": "DDR_CK_P", "~{CK}": "DDR_CK_N", "LDQS": "DDR_LDQS_P", "~{LDQS}": "DDR_LDQS_N", "UDQS": "DDR_UDQS_P",
       "~{UDQS}": "DDR_UDQS_N", "LDM": "DDR_LDM", "UDM": "DDR_UDM", "BA0": "DDR_BA0", "BA1": "DDR_BA1", "BA2": "DDR_BA2", "~{RESET}": "DDR_RESET_N",
       "ZQ": "DDR_ZQ", "V_{REFCA}": "DDR_VREF", "V_{REFDQ}": "DDR_VREF", "V_{DD}": V135, "V_{DDQ}": V135, "V_{SS}": GND, "V_{SSQ}": GND}
for i in range(16):
    ddr[f"DQ{i}"] = f"DDR_DQ{i}"
    ddr[f"A{i}"] = f"DDR_A{i}"
# per numero di sfera: i numeri A1-A9 si confonderebbero con i nomi degli indirizzi
d.ic(f"{LIBNAME}:MT41K512M16HA", "U2", "MT41K512M16HA-107:A", "Package_BGA:Micron_FBGA-96_9x14mm_Layout9x16_P0.8mm",
     {q[0]: ddr.get(q[1], "NC") for q in d.pins[f"{LIBNAME}:MT41K512M16HA"]}, mpn="MT41K512M16HA-107:A")
d.group("VREF, ZQ, pull-down", [("R", "1k 0.5%", V135, "DDR_VREF"), ("R", "1k 0.5%", "DDR_VREF", GND), ("C", "100nF", V135, "DDR_VREF"), ("C", "100nF", "DDR_VREF", GND),
        ("R", "240R 1%", "DDR_ZQ", GND), ("R", "240R 1%", "SOC_DDR_ZQ", GND), ("R", "10k", "DDR_RESET_N", GND), ("R", "10k", "DDR_CKE", GND), ("R", "100R", "DDR_CK_P", "DDR_CK_N")])
d.group("VDD / VDDQ 1.35 V", [("C", "22uF", V135, GND), ("C", "22uF", V135, GND)] + [("C", "100nF", V135, GND)] * 8)
d.flags(["DDR_VREF"])

# ================================ Alimentazione ==========================================================================================
p = Sheet("Alimentazione", "alimentazione.kicad_sch", 300, 4)
p.note("VIN_SYS 12 V dal BUS_POWER -> TPS56637 5 V (U22) -> TPS2121 U17 (IN1 bus con priorita, IN2 VBUS USB-C 1) -> 5V_SYS -> buck 3.3 V (U23), 1.35 V DDR (U26), 1.4 V VDD_SOC_IN (U27), 3.3 V SSD (U39).")
p.note("Sequenza 3.3 -> 1.35 -> 1.4 V a RC sugli EN del TLV62569 (soglia EN max 1.2 V): 100k/470nF circa 21 ms, 100k/1uF circa 45 ms. POR_B dal TPS3839K33 (2.93 V, push-pull) con 1k in serie, cosi' SW1 puo' cortocircuitare POR_B.")
p.note("VDD_SNVS: OR a diodi BAT54C tra 3V3 e CR1220 (BT1), alimenta anche V_BCKP del GNSS. Nessuna ricarica della pila. Tutti i condensatori 0603 (22uF/10V, 10uF/25V X5R).")
B, BF = p.mik("TPS56637RPAR")
p.std("Device:L"), p.std("Diode:BAT54C"), p.std("Power_Supervisor:TPS3839DBZ")
p.ic(B, "U22", "TPS56637RPAR", BF, {"8": "VIN_SYS", "1": "BUCK_EN", "2": "BUCK_FB", "10": "BUCK_MODE", "4": "BUCK_PG", "5": "NC", "7": "BUCK_BST", "6": "BUCK_SW", "3": GND, "9": GND},
     mpn="TPS56637RPAR", lcsc="C841386")
p.ic("Device:L", "L1", "3.3uH/8A", "Inductor_SMD:L_Coilcraft_XAL6030-XXX", {"1": "BUCK_SW", "2": "5V_BUCK"}, mpn="XAL6030-332MEC")
p.group("TPS56637: EN 169k/36.1k, FB 73.2k/10k = 4.99 V, FF 20k+100pF, MODE aperto = FCCM (come schede Octavo/RK3568)", [
    ("C", "10uF/25V", "VIN_SYS", GND), ("C", "10uF/25V", "VIN_SYS", GND), ("C", "100nF/50V", "VIN_SYS", GND), ("R", "169k 1%", "VIN_SYS", "BUCK_EN"), ("R", "36.1k 1%", "BUCK_EN", GND),
    ("R", "10k", "BUCK_MODE", GND, True), ("R", "100k", "5V_BUCK", "BUCK_PG"), ("C", "100nF", "BUCK_BST", "BUCK_SW"), ("R", "73.2k 1%", "5V_BUCK", "BUCK_FB"), ("R", "10k 1%", "BUCK_FB", GND),
    ("R", "20k", "5V_BUCK", "BUCK_FF"), ("C", "100pF", "BUCK_FF", "BUCK_FB"), ("C", "22uF/10V", "5V_BUCK", GND), ("C", "22uF/10V", "5V_BUCK", GND), ("C", "22uF/10V", "5V_BUCK", GND), ("C", "22uF/10V", "5V_BUCK", GND)])
M, MF = p.mik("TPS2121RUXR")
p.ic(M, "U17", "TPS2121RUXR", MF, {"7": "5V_BUCK", "6": "MUX_PR1", "5": "MUX_OV1", "2": "VBUS1", "4": "MUX_OV2", "3": GND, "1": V5, "8": V5, "9": "PWR_SRC_ST", "10": "MUX_ILM", "11": "MUX_SS", "12": GND},
     mpn="TPS2121RUXR", lcsc="C485916")
p.group("TPS2121 (come RK3568): PR1 4.49 V, OV 5.98 V, ILM 22.1k = 4-5 A, SS 100 nF", [
    ("R", "32.4k 1%", "5V_BUCK", "MUX_PR1"), ("R", "10k 1%", "MUX_PR1", GND), ("R", "46.4k 1%", "5V_BUCK", "MUX_OV1"), ("R", "10k 1%", "MUX_OV1", GND), ("R", "46.4k 1%", "VBUS1", "MUX_OV2"), ("R", "10k 1%", "MUX_OV2", GND),
    ("R", "22.1k 1%", "MUX_ILM", GND), ("C", "100nF", "MUX_SS", GND), ("C", "1uF/10V", "5V_BUCK", GND), ("C", "1uF/10V", "VBUS1", GND), ("C", "22uF/10V", V5, GND), ("C", "22uF/10V", V5, GND), ("C", "1uF/10V", V5, GND)])
T, TF = p.mik("TPS563201DDCR")
p.ic(T, "U23", "TPS563201DDCR", TF, {"VIN": V5, "EN": "U23_EN", "GND": GND, "SW": "U23_SW", "VBST": "U23_BST", "VFB": "U23_FB"}, mpn="TPS563201DDCR", lcsc="C116592")
p.ic("Device:L", "L2", "2.2uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U23_SW", "2": V33}, mpn="XAL4020-222")
p.group("U23 3.3 V / 3 A: FB 33.2k/10k = 3.32 V, primo della sequenza", [("C", "10uF/16V", V5, GND), ("C", "100nF", V5, GND), ("R", "100k", V5, "U23_EN"), ("C", "100nF", "U23_BST", "U23_SW"),
        ("R", "33.2k 1%", V33, "U23_FB"), ("R", "10k 1%", "U23_FB", GND), ("C", "22uF/10V", V33, GND), ("C", "22uF/10V", V33, GND)])
TL, TLF = p.mik("TLV62569DBVR")
p.ic(TL, "U26", "TLV62569DBVR", TLF, {"1": "U26_EN", "2": GND, "3": "U26_SW", "4": V5, "5": "U26_FB"}, mpn="TLV62569DBVR")
p.ic("Device:L", "L3", "2.2uH/3A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U26_SW", "2": V135}, mpn="XAL4020-222")
p.group("U26 1.35 V DDR: FB 150k/120k (0.6 V x 2.25), EN 100k/470nF da 3V3", [("C", "10uF/10V", V5, GND), ("R", "100k", V33, "U26_EN"), ("C", "470nF", "U26_EN", GND), ("R", "150k 1%", V135, "U26_FB"), ("R", "120k 1%", "U26_FB", GND),
        ("C", "22uF/10V", V135, GND), ("C", "22uF/10V", V135, GND)])
p.ic(TL, "U27", "TLV62569DBVR", TLF, {"1": "U27_EN", "2": GND, "3": "U27_SW", "4": V5, "5": "U27_FB"}, mpn="TLV62569DBVR")
p.ic("Device:L", "L4", "2.2uH/3A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U27_SW", "2": V14}, mpn="XAL4020-222")
p.group("U27 1.4 V VDD_SOC_IN: FB 133k/100k = 1.398 V (min 1.375 V, 125 mV sopra VDD_ARM_CAP), EN 100k/1uF da 3V3", [("C", "10uF/10V", V5, GND), ("R", "100k", V33, "U27_EN"), ("C", "1uF", "U27_EN", GND), ("R", "133k 1%", V14, "U27_FB"), ("R", "100k 1%", "U27_FB", GND),
        ("C", "22uF/10V", V14, GND), ("C", "22uF/10V", V14, GND)])
p.ic(T, "U39", "TPS563201DDCR", TF, {"VIN": V5, "EN": "U39_EN", "GND": GND, "SW": "U39_SW", "VBST": "U39_BST", "VFB": "U39_FB"}, mpn="TPS563201DDCR", lcsc="C116592")
p.ic("Device:L", "L5", "2.2uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U39_SW", "2": "3V3_SSD"}, mpn="XAL4020-222")
p.group("U39 3.3 V SSD, sempre acceso", [("C", "10uF/16V", V5, GND), ("R", "100k", V5, "U39_EN"), ("C", "100nF", "U39_BST", "U39_SW"), ("R", "33.2k 1%", "3V3_SSD", "U39_FB"), ("R", "10k 1%", "U39_FB", GND),
        ("C", "22uF/10V", "3V3_SSD", GND), ("C", "22uF/10V", "3V3_SSD", GND)])
p.ic("Power_Supervisor:TPS3839DBZ", "U28", "TPS3839K33DBZR", "Package_TO_SOT_SMD:SOT-23", {"1": GND, "2": "POR_DRV", "3": V33}, mpn="TPS3839K33DBZR")
p.group("POR_B", [("R", "1k", "POR_DRV", "POR_B"), ("C", "100nF", V33, GND)])
BAT, BATF = p.mik("CR1220-2")
p.ic(BAT, "BT1", "CR1220", f"{LIBNAME}:" + BATF.split(":")[1], {"1": "VBAT", "2": GND}, mpn="CR1220-2", lcsc="C70381")
p.ic("Diode:BAT54C", "D4", "BAT54C", "Package_TO_SOT_SMD:SOT-23", {"1": V33, "2": "VBAT", "3": SNVS}, mpn="BAT54C")
p.flags(["VIN_SYS", "5V_BUCK", V5, V33, V135, V14, "3V3_SSD", SNVS, "VBUS1", GND])

# ================================ Bus MIKILAB ===============================================================================================
b = Sheet("Bus MIKILAB", "bus-mikilab.kicad_sch", 400, 5)
b.note("J11 BUS_POWER 30 pin (Hirose FH12-30S) su ECSPI2, J12 MAIN 28 pin REV5.1 (XUNPU FPC-05F-28PH20, pin 28 = HIT#) su ECSPI1. Mappa dei connettori identica a SchedaA133/RK3568. Rail BUS_* passanti, non collegati ai rail della scheda.")
b.note("Serie 33R su CLK/MOSI/MISO, 100R su ADDR/PREFIX, pull-up 10k sui CS, 4.7k su ALERT#/HIT#, 2.2k su I2C. VREF_ENABLE 10k e VBIAS_ENABLE 100k a GND. ESD TPD4E05U06DQA sulle linee logiche.")
MAIN = {1: GND, 2: "BUS_5V", 3: "BUS_3V3", 4: GND, 5: "BUS_2V5_REF", 6: "BUS_1V25_REF", 7: "GND_A", 8: "BUS_VBIAS_1", 9: "BUS_VBIAS_2", 10: GND, 11: "MAIN_SPI_SCLK", 12: "MAIN_SPI_MOSI",
        13: "MAIN_SPI_MISO", 14: "MAIN_I2C_SDA", 15: "MAIN_I2C_SCL", 16: GND, 17: "MAIN_SPI_CS_MASTER", 18: "MAIN_SPI_ADDR_0", 19: "MAIN_SPI_ADDR_1", 20: "MAIN_SPI_ADDR_2", 21: "MAIN_SPI_PREFIX_0",
        22: "MAIN_SPI_PREFIX_1", 23: "MAIN_SPI_PREFIX_2", 24: "MAIN_SPI_ALERT_N", 25: "SPI_ID_0", 26: "SPI_ID_1", 27: "SPI_ID_2", 28: "MAIN_HIT_N"}
PWR = {1: "GND_A", 2: "BUS_VBIAS_1", 3: "BUS_VBIAS_2", 4: "GND_A", 5: "BUS_2V5_REF", 6: "BUS_1V25_REF", 7: "GND_A", 8: "BUS_5V", 9: "BUS_3V3", 10: GND, 11: "PWR_SPI_SCLK", 12: "PWR_SPI_MOSI",
       13: "PWR_SPI_MISO", 14: GND, 15: "PWR_SPI_INA239A_CS", 16: "PWR_SPI_INA239B_CS", 17: "PWR_SPI_DAC_CS", 18: "VREF_ENABLE", 19: "VBIAS_ENABLE", 20: "DAC61402_FAULT", 21: GND,
       22: GND, 23: GND, 24: "VIN_SYS", 25: "VIN_SYS", 26: "VIN_SYS", 27: GND, 28: GND, 29: "BUS_3V3", 30: GND}
FH, FHF = b.mik("FH12-30S-0.5SH")
FP_, FPF = b.mik("FPC-05F-28PH20")
b.ic(FH, "J11", "BUS_POWER_MIKILAB", FHF, {str(k): (PWR[k] if k in PWR else GND) for k in range(1, 40)}, mpn="FH12-30S-0.5SH", lcsc="C506793")
b.ic(FP_, "J12", "BUS_MIKILAB_MAIN", FPF, {str(k): (MAIN[k] if k in MAIN else GND) for k in range(1, 40)}, mpn="FPC-05F-28PH20", lcsc="C2856807")
ser = [("ECSPI2_SCLK", "PWR_SPI_SCLK"), ("ECSPI2_MOSI", "PWR_SPI_MOSI"), ("ECSPI2_MISO", "PWR_SPI_MISO"), ("ECSPI1_SCLK", "MAIN_SPI_SCLK"), ("ECSPI1_MOSI", "MAIN_SPI_MOSI"), ("ECSPI1_MISO", "MAIN_SPI_MISO")]
b.group("Serie SPI 33R", [("R", "33R", x, y) for x, y in ser])
b.group("Serie ADDR/PREFIX 100R", [("R", "100R", f"SOC_ADDR_{i}", f"MAIN_SPI_ADDR_{i}") for i in range(3)] + [("R", "100R", f"SOC_PREFIX_{i}", f"MAIN_SPI_PREFIX_{i}") for i in range(3)])
b.group("Livelli di riposo", [("R", "10k", V33, "PWR_SPI_INA239A_CS"), ("R", "10k", V33, "PWR_SPI_INA239B_CS"), ("R", "10k", V33, "PWR_SPI_DAC_CS"), ("R", "10k", V33, "MAIN_SPI_CS_MASTER"), ("R", "10k", "VREF_ENABLE", GND), ("R", "100k", "VBIAS_ENABLE", GND),
        ("R", "10k", V33, "DAC61402_FAULT"), ("R", "4.7k", V33, "MAIN_SPI_ALERT_N"), ("R", "4.7k", V33, "MAIN_HIT_N"), ("R", "2.2k", V33, "MAIN_I2C_SCL"), ("R", "2.2k", V33, "MAIN_I2C_SDA")])
b.group("ID 000 su J_OUT (testa della catena); GND_A-GND_D ponte apribile, DNP", [("R", "0R", "SPI_ID_0", GND), ("R", "0R", "SPI_ID_1", GND), ("R", "0R", "SPI_ID_2", GND), ("R", "0R", "GND_A", GND, True)])
BUSNETS = ["PWR_SPI_SCLK", "PWR_SPI_MOSI", "PWR_SPI_MISO", "PWR_SPI_INA239A_CS", "PWR_SPI_INA239B_CS", "PWR_SPI_DAC_CS", "VREF_ENABLE", "VBIAS_ENABLE", "DAC61402_FAULT", "MAIN_SPI_SCLK", "MAIN_SPI_MOSI", "MAIN_SPI_MISO",
           "MAIN_I2C_SDA", "MAIN_I2C_SCL", "MAIN_SPI_CS_MASTER", "MAIN_SPI_ADDR_0", "MAIN_SPI_ADDR_1", "MAIN_SPI_ADDR_2", "MAIN_SPI_PREFIX_0", "MAIN_SPI_PREFIX_1", "MAIN_SPI_PREFIX_2", "MAIN_SPI_ALERT_N", "MAIN_HIT_N"]
b.std("Power_Protection:TPD4E05U06DQA")
for k in range(6):
    g_ = BUSNETS[4 * k: 4 * k + 4]
    b.ic("Power_Protection:TPD4E05U06DQA", f"U{29 + k}", "TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
         {"1": g_[0], "2": g_[1], "4": g_[2] if len(g_) > 2 else "NC", "5": g_[3] if len(g_) > 3 else "NC", "3": GND, "8": GND}, mpn="TPD4E05U06DQAR")
b.group("Disaccoppiamento connettori", [("C", "100nF", "VIN_SYS", GND), ("C", "100nF", "BUS_3V3", GND), ("C", "100nF", "BUS_5V", GND)])
b.flags(["GND_A", "BUS_3V3", "BUS_5V"])

# ================================ Storage: QSPI, microSD, JMS578, M.2 =====================================================================
m = Sheet("Storage", "storage.kicad_sch", 500, 6)
m.note("U5 W25Q128JV su QSPI1 porta A (tabella 79, boot). J5 microSD DM3AT su uSDHC1 (sul BOTTOM), 3.3 V, CD su UART1_RTS_B (USDHC1_CD_B). U25 protegge DAT0-3: CMD e CLK non hanno ESD (un solo TPD4E in BOM, 4 linee).")
m.note("U38 JMS578 (QFN-48 6x6 passo 0.4): solo USB 2.0, SuperSpeed non collegati. Datasheet Rev 1.01: 12K su REXT, 10 nF serie su SATA, 4.7 uH su LXO -> 1.2 V (VCCK/AVDDL), 30 MHz, MODE[1:0]=01, TME=0. VREG_IN e VBUS da 5V_SYS, VCCO dal suo AV33O.")
m.note("Niente SPI NVRAM del JMS578 (facoltativa, solo VID/PID vendor e firmware aggiornabile): usa il ROM interno. J13 solo SSD SATA: DEVSLP basso, PEDET libero. Nessun reference JMicron pubblico: da confermare sul primo prototipo.")
m.std("Memory_Flash:W25Q128JVS")
m.ic("Memory_Flash:W25Q128JVS", "U5", "W25Q128JVSIQ", "Package_SO:SOIC-8_5.3x5.3mm_P1.27mm", {"1": "QSPI_CS_N", "2": "QSPI_D1", "3": "QSPI_D2", "4": GND, "5": "QSPI_D0", "6": "QSPI_SCLK", "7": "QSPI_D3", "8": V33}, mpn="W25Q128JVSIQ", lcsc="C97521")
m.group("QSPI: 22R su SCLK, pull-up 10k su CS/IO2/IO3", [("R", "22R", "QSPI_SCLK_S", "QSPI_SCLK"), ("R", "10k", V33, "QSPI_CS_N"), ("R", "10k", V33, "QSPI_D2"), ("R", "10k", V33, "QSPI_D3"), ("C", "100nF", V33, GND)])
SD, SDF = m.mik("DM3AT-SF-PEJM5")
m.ic(SD, "J5", "DM3AT-SF-PEJM5", SDF, {"1": "SD1_D2", "2": "SD1_D3", "3": "SD1_CMD", "4": V33, "5": "SD1_CLK", "6": GND, "7": "SD1_D0", "8": "SD1_D1", "9": "SD1_CD_N", "11": GND, "10": GND, "12": GND, "13": GND, "14": GND}, mpn="DM3AT-SF-PEJM5", lcsc="C114218")
m.group("microSD: 22R su CLK, pull-up 10k", [("R", "22R", "SD1_CLK_S", "SD1_CLK")] + [("R", "10k", V33, n_) for n_ in ("SD1_CMD", "SD1_D0", "SD1_D1", "SD1_D2", "SD1_D3", "SD1_CD_N")] + [("C", "10uF", V33, GND), ("C", "100nF", V33, GND)])
m.std("Power_Protection:TPD4E05U06DQA")
m.ic("Power_Protection:TPD4E05U06DQA", "U25", "TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", {"1": "SD1_D0", "2": "SD1_D1", "4": "SD1_D2", "5": "SD1_D3", "3": GND, "8": GND}, mpn="TPD4E05U06DQAR")
J = [("1", "TME", "L"), ("2", "GPIO0", "L"), ("3", "GPIO1", "L"), ("4", "VCCK", "L"), ("5", "GPIO2", "L"), ("6", "GPIO3", "L"), ("7", "VCCO", "L"), ("8", "GPIO4", "L"), ("9", "GPIO5", "L"), ("10", "VCCK", "L"), ("11", "GPIO6", "L"), ("12", "VBUS", "L"),
     ("13", "DM", "L"), ("14", "AV33O", "L"), ("15", "DP", "L"), ("16", "NC", "L"), ("17", "NC", "L"), ("18", "AVDDL", "L"), ("19", "SSTXN", "L"), ("20", "SSTXP", "L"), ("21", "AVDDL", "L"), ("22", "SSRXN", "L"), ("23", "SSRXP", "L"), ("24", "AVDDL", "L"), ("25", "NC", "L"),
     ("26", "NC", "R"), ("27", "XIN", "R"), ("28", "XOUT", "R"), ("29", "AVDDL", "R"), ("30", "RXP", "R"), ("31", "RXN", "R"), ("32", "AVDDL", "R"), ("33", "TXN", "R"), ("34", "TXP", "R"), ("35", "NC", "R"), ("36", "REXT", "R"), ("37", "GPIO8", "R"), ("38", "RST_N", "R"),
     ("39", "VCCO", "R"), ("40", "VCCK", "R"), ("41", "GPIO7", "R"), ("42", "MODE1", "R"), ("43", "GND", "R"), ("44", "LXO", "R"), ("45", "VREG_IN", "R"), ("46", "MODE0", "R"), ("47", "NC", "R"), ("48", "GPIO9", "R"), ("49", "EP", "R")]
m.add_sym(f"{LIBNAME}:JMS578", box_symbol(LIBNAME, "JMS578", J, "JMicron JMS578, bridge USB-SATA, QFN-48 6x6 passo 0.4"))
JN = {"VCCK": "JMS_1V2", "AVDDL": "JMS_1V2", "VCCO": "JMS_3V3", "AV33O": "JMS_3V3", "VBUS": V5, "VREG_IN": V5, "GND": GND, "EP": GND, "LXO": "JMS_LX", "DM": "HUB_P2_DM", "DP": "HUB_P2_DP", "XIN": "JMS_XIN", "XOUT": "JMS_XOUT",
      "RXP": "JMS_RXP", "RXN": "JMS_RXN", "TXP": "JMS_TXP", "TXN": "JMS_TXN", "REXT": "JMS_REXT", "RST_N": "JMS_RST_N", "TME": "JMS_TME", "MODE1": "JMS_MODE1", "MODE0": "JMS_MODE0"}
m.ic(f"{LIBNAME}:JMS578", "U38", "JMS578", "Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.2x4.2mm", JN, mpn="JMS578-QGBA0A")
m.std("Device:L"), m.std("Device:Crystal_GND24")
m.ic("Device:L", "L7", "4.7uH", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "JMS_LX", "2": "JMS_1V2"})
m.ic("Device:Crystal_GND24", "Y5", "30MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", {"1": "JMS_XIN", "3": "JMS_XOUT", "2": GND, "4": GND}, mpn="da scegliere: 3225 30 MHz +-30 ppm")
m.group("JMS578", [("R", "12k 1%", "JMS_REXT", GND), ("R", "10k", "JMS_TME", GND), ("R", "10k", "JMS_MODE1", GND), ("R", "10k", "JMS_3V3", "JMS_MODE0"), ("R", "10k", "JMS_3V3", "JMS_RST_N"), ("C", "1uF", "JMS_RST_N", GND),
        ("C", "10uF", V5, GND), ("C", "1uF", "JMS_3V3", GND), ("C", "100nF", "JMS_3V3", GND), ("C", "100nF", "JMS_3V3", GND), ("C", "10uF", "JMS_1V2", GND), ("C", "10uF", "JMS_1V2", GND)] + [("C", "100nF", "JMS_1V2", GND)] * 4 + [("C", "18pF", "JMS_XIN", GND), ("C", "18pF", "JMS_XOUT", GND)])
m.group("SATA: 10 nF serie (datasheet)", [("C", "10nF", "JMS_TXP", "SATA_TXP"), ("C", "10nF", "JMS_TXN", "SATA_TXN"), ("C", "10nF", "JMS_RXP", "SATA_RXP"), ("C", "10nF", "JMS_RXN", "SATA_RXN")])
M2_NUM = list(range(1, 59)) + list(range(67, 76))
M2_NAME = {41: "SATA_B+", 43: "SATA_B-", 47: "SATA_A-", 49: "SATA_A+", 38: "DEVSLP", 69: "PEDET", 10: "DAS"}
for n_ in (1, 3, 9, 15, 21, 27, 33, 39, 45, 51, 57, 71, 73, 75):
    M2_NAME[n_] = "GND"
for n_ in (2, 4, 12, 14, 16, 18, 70, 72, 74):
    M2_NAME[n_] = "3V3"
M2P = [(str(n_), M2_NAME.get(n_, f"NC{n_}"), "L" if n_ % 2 else "R") for n_ in M2_NUM] + [("MP", "MP", "L")]
m.add_sym(f"{LIBNAME}:M.2_Key_M", box_symbol(LIBNAME, "M.2_Key_M", M2P, "Zoccolo M.2 key M, solo SSD SATA"))
M2N = {"GND": GND, "MP": GND, "3V3": "3V3_SSD", "SATA_B+": "SATA_RXP", "SATA_B-": "SATA_RXN", "SATA_A+": "SATA_TXP", "SATA_A-": "SATA_TXN", "DEVSLP": "SATA_DEVSLP"}
m.ic(f"{LIBNAME}:M.2_Key_M", "J13", "M.2 key M", "Connector_PCBEdge:TE_M.2_M_2x38-1MP_P0.5mm", M2N, mpn="da scegliere: M.2 M-key H 4.2 mm")
m.group("M.2", [("R", "10k", "SATA_DEVSLP", GND), ("C", "22uF/10V", "3V3_SSD", GND), ("C", "22uF/10V", "3V3_SSD", GND), ("C", "100nF", "3V3_SSD", GND), ("C", "100nF", "3V3_SSD", GND)])
m.flags(["JMS_3V3", "JMS_1V2"])

# ================================ USB =======================================================================================================
u = Sheet("USB", "usb.kicad_sch", 600, 7)
u.note("J3 USB-C 1: USB_OTG1, device/download seriale e alimentazione (VBUS1 -> IN2 del TPS2121). Sink: 5.1k su CC1/CC2. J8 USB-C 2 host: porta 1 dell'hub, VBUS dal TPS2553 (~1 A), Rp 56k. Le due USB-C sono affiancate sullo stesso bordo.")
u.note("U36 FE1.1s Rev B su USB_OTG2 (3.3 V esterni su VD33F, VDD5 e pin 12/13/28 liberi come da datasheet Rev B12.4): porta 1 J8, porta 2 JMS578, porte 3-4 libere. VBUSM e BUSJ a 3.3 V (host sempre presente, self-powered). USB_OTG2_VBUS del 6ULL da 5V_SYS.")
UC, UCF = u.mik("TYPE-C-31-M-12")
u.std("Device:D_TVS"), u.std("Power_Protection:USBLC6-2SC6")
u.ic(UC, "J3", "TYPE-C-31-M-12", UCF, {"VBUS": "VBUS1", "CC1": "USB1_CC1", "CC2": "USB1_CC2", "DP1": "USB1_DP", "DP2": "USB1_DP", "DN1": "USB1_DM", "DN2": "USB1_DM", "SBU1": "NC", "SBU2": "NC", "GND": GND, "EH": GND}, mpn="TYPE-C-31-M-12", lcsc="C165948")
u.ic("Power_Protection:USBLC6-2SC6", "U9", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", {"1": "USB1_DP", "6": "USB1_DP", "3": "USB1_DM", "4": "USB1_DM", "5": "VBUS1", "2": GND}, mpn="USBLC6-2SC6", lcsc="C7519")
u.ic("Device:D_TVS", "D1", "SMF5.0A", "Diode_SMD:D_SMF", {"1": "VBUS1", "2": GND}, mpn="SMF5.0A", lcsc="C151296")
u.group("CC sink J3", [("R", "5.1k", "USB1_CC1", GND), ("R", "5.1k", "USB1_CC2", GND), ("C", "10uF", "VBUS1", GND)])
u.ic(UC, "J8", "TYPE-C-31-M-12", UCF, {"VBUS": "VBUS2", "CC1": "USB3_CC1", "CC2": "USB3_CC2", "DP1": "HUB_P1_DP", "DP2": "HUB_P1_DP", "DN1": "HUB_P1_DM", "DN2": "HUB_P1_DM", "SBU1": "NC", "SBU2": "NC", "GND": GND, "EH": GND}, mpn="TYPE-C-31-M-12", lcsc="C165948")
u.ic("Power_Protection:USBLC6-2SC6", "U10", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", {"1": "HUB_P1_DP", "6": "HUB_P1_DP", "3": "HUB_P1_DM", "4": "HUB_P1_DM", "5": "VBUS2", "2": GND}, mpn="USBLC6-2SC6", lcsc="C7519")
SWI, SWF = u.mik("TPS2553DBVR")
u.ic(SWI, "U24", "TPS2553DBVR", SWF, {"1": V5, "2": GND, "3": "USB2_VBUS_EN", "4": "USB2_OC_N", "5": "USB2_ILIM", "6": "VBUS2"}, mpn="TPS2553DBVR", lcsc="C55266")
u.group("J8 host: Rp 56k, RILIM 26.1k, EN 100k a GND", [("R", "56k", V5, "USB3_CC1"), ("R", "56k", V5, "USB3_CC2"), ("R", "26.1k 1%", "USB2_ILIM", GND), ("R", "100k", "USB2_VBUS_EN", GND), ("C", "1uF", V5, GND), ("C", "22uF/10V", "VBUS2", GND), ("C", "100nF", "VBUS2", GND)])
FE = [("1", "VSS", "L"), ("2", "XOUT", "L"), ("3", "XIN", "L"), ("4", "DM4", "L"), ("5", "DP4", "L"), ("6", "DM3", "L"), ("7", "DP3", "L"), ("8", "DM2", "L"), ("9", "DP2", "L"), ("10", "DM1", "L"), ("11", "DP1", "L"), ("12", "NC12", "L"), ("13", "NC13", "L"), ("14", "REXT", "L"),
      ("15", "DMU", "R"), ("16", "DPU", "R"), ("17", "XRSTJ", "R"), ("18", "VBUSM", "R"), ("19", "BUSJ", "R"), ("20", "VDD5", "R"), ("21", "VD33F", "R"), ("22", "DRV", "R"), ("23", "LED1", "R"), ("24", "LED2", "R"), ("25", "PWRJ", "R"), ("26", "OVCJ", "R"), ("27", "TESTJ", "R"), ("28", "NC28", "R")]
u.add_sym(f"{LIBNAME}:FE1.1s_RevB", box_symbol(LIBNAME, "FE1.1s_RevB", FE, "Terminus FE1.1s Rev B, hub USB 2.0 4 porte, SSOP-28"))
u.ic(f"{LIBNAME}:FE1.1s_RevB", "U36", "FE1.1s", "Package_SO:SSOP-28_3.9x9.9mm_P0.635mm",
     {"VSS": GND, "XOUT": "HUB_XOUT", "XIN": "HUB_XIN", "DM2": "HUB_P2_DM", "DP2": "HUB_P2_DP", "DM1": "HUB_P1_DM", "DP1": "HUB_P1_DP", "REXT": "HUB_REXT", "DMU": "USB2_DM", "DPU": "USB2_DP", "XRSTJ": "HUB_RST_N",
      "VBUSM": V33, "BUSJ": V33, "VD33F": V33, "DRV": "HUB_DRV", "OVCJ": "USB2_OC_N"}, mpn="FE1.1s-BSOP28BCN")
u.std("Device:Crystal_GND24")
u.ic("Device:Crystal_GND24", "Y4", "12MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", {"1": "HUB_XIN", "3": "HUB_XOUT", "2": GND, "4": GND}, mpn="X322512MSB4SI")
u.group("Hub: REXT 2.7k, XRSTJ 10k, DRV basso = hub normale", [("R", "2.7k 1%", "HUB_REXT", GND), ("R", "10k", V33, "HUB_RST_N"), ("R", "10k", "HUB_DRV", GND), ("C", "18pF", "HUB_XIN", GND), ("C", "18pF", "HUB_XOUT", GND), ("C", "10uF", V33, GND), ("C", "100nF", V33, GND), ("C", "100nF", V33, GND)])
u.flags(["VBUS2"])

# ================================ Rete ======================================================================================================
n = Sheet("Rete", "rete.kicad_sch", 700, 8)
n.note("U7 LAN8720A su ENET1 RMII. Y3 25 MHz montato: il PHY genera i 50 MHz (nINTSEL basso) su REFCLKO verso ENET1_TX_CLK (REF_CLK in ingresso, SION). nINT quindi non disponibile. Strap MODE=111 (10k su RXD0/RXD1/CRS_DV), PHYAD0=0.")
n.note("J1 HR911105A: magnetici e LED integrati. TX/RX con 49.9R a VDDA, CT a VDDA con 22 nF. Polarita' dei LED dal disegno Hanrun: da verificare (solo indicazione, non blocca il link). U6 24AA02E48 su I2C1 con il MAC EUI-48.")
n.std("Interface_Ethernet:LAN8720A"), n.std("Memory_EEPROM:24AA02E-OT"), n.std("Device:FerriteBead")
n.ic("Interface_Ethernet:LAN8720A", "U7", "LAN8720A-CP-TR", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
     {"1": "PHY_VDDA", "19": "PHY_VDDA", "2": "PHY_LED2", "3": "PHY_LED1", "4": "PHY_XTAL2", "5": "PHY_XTAL1", "6": "PHY_VDDCR", "7": "RMII_RXD1", "8": "RMII_RXD0", "9": V33, "10": "RMII_RXER", "11": "RMII_CRSDV", "12": "PHY_MDIO", "13": "PHY_MDC",
      "14": "PHY_REFCLK_S", "15": "PHY_RST_N", "16": "RMII_TXEN", "17": "RMII_TXD0", "18": "RMII_TXD1", "20": "ETH_TXN", "21": "ETH_TXP", "22": "ETH_RXN", "23": "ETH_RXP", "24": "PHY_RBIAS", "25": GND}, mpn="LAN8720A-CP-TR", lcsc="C45223")
Y3I, Y3F = n.mik("X322525MOB4SI")
n.ic(Y3I, "Y3", "25MHz", Y3F, {"1": "PHY_XTAL1", "3": "PHY_XTAL2", "2": GND, "4": GND}, mpn="X322525MOB4SI", lcsc="C9006")
n.ic("Device:FerriteBead", "FB1", "120R@100MHz", "Inductor_SMD:L_0603_1608Metric", {"1": V33, "2": "PHY_VDDA"}, mpn="BLM18PG121SN1D")
RJ = [("1", "TD+", "L"), ("2", "TD-", "L"), ("3", "RD+", "L"), ("4", "TCT", "L"), ("5", "RCT", "L"), ("6", "RD-", "L"), ("7", "NC", "L"), ("8", "CHS_GND", "L"), ("9", "LEDY_A", "R"), ("10", "LEDY_K", "R"), ("11", "LEDG_K", "R"), ("12", "LEDG_A", "R"), ("SH", "SHIELD", "R")]
n.add_sym(f"{LIBNAME}:HR911105A", box_symbol(LIBNAME, "HR911105A", RJ, "HanRun HR911105A, RJ45 10/100 con magnetici e LED"))
n.ic(f"{LIBNAME}:HR911105A", "J1", "HR911105A", "Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal",
     {"1": "ETH_TXP", "2": "ETH_TXN", "3": "ETH_RXP", "4": "PHY_VDDA", "5": "PHY_VDDA", "6": "ETH_RXN", "8": "ETH_SHIELD", "9": "LED1_R", "10": GND, "11": GND, "12": "LED2_R", "SH": "ETH_SHIELD"}, mpn="HR911105A", lcsc="C12074")
n.group("PHY: terminazioni, RBIAS 12.1k, VDDCR 1uF+470pF, straps, REFCLK 22R", [("R", "49.9R 1%", "PHY_VDDA", "ETH_TXP"), ("R", "49.9R 1%", "PHY_VDDA", "ETH_TXN"), ("R", "49.9R 1%", "PHY_VDDA", "ETH_RXP"), ("R", "49.9R 1%", "PHY_VDDA", "ETH_RXN"),
        ("C", "22nF", "PHY_VDDA", GND), ("C", "22nF", "PHY_VDDA", GND), ("C", "10uF", "PHY_VDDA", GND), ("C", "100nF", "PHY_VDDA", GND), ("R", "12.1k 1%", "PHY_RBIAS", GND), ("C", "1uF", "PHY_VDDCR", GND), ("C", "470pF", "PHY_VDDCR", GND),
        ("R", "10k", V33, "RMII_RXD0"), ("R", "10k", V33, "RMII_RXD1"), ("R", "10k", V33, "RMII_CRSDV"), ("R", "10k", "PHY_LED2", GND), ("R", "10k", V33, "PHY_RST_N"), ("R", "1.5k", V33, "PHY_MDIO"), ("R", "22R", "PHY_REFCLK_S", "RMII_REFCLK"),
        ("C", "100nF", V33, GND), ("C", "15pF", "PHY_XTAL1", GND), ("C", "15pF", "PHY_XTAL2", GND), ("R", "330R", "PHY_LED1", "LED1_R"), ("R", "330R", "PHY_LED2", "LED2_R"), ("R", "0R", "ETH_SHIELD", GND)])
n.ic("Memory_EEPROM:24AA02E-OT", "U6", "24AA02E48T-I/OT", "Package_TO_SOT_SMD:SOT-23-5", {"1": "I2C1_SCL", "2": GND, "3": "I2C1_SDA", "4": V33}, mpn="24AA02E48T-I/OT", lcsc="C38987")
n.group("EEPROM MAC: I2C1", [("R", "2.2k", V33, "I2C1_SCL"), ("R", "2.2k", V33, "I2C1_SDA"), ("C", "100nF", V33, GND)])
n.flags(["PHY_VDDA", "PHY_VDDCR"])

# ================================ Radio =====================================================================================================
r = Sheet("Radio", "radio.kicad_sch", 800, 9)
r.note("U35 LB-LINK BL-M8723DS1 (RTL8723DS, 12x12 mm, datasheet V1.0.1.3): Wi-Fi su uSDHC2 (pad NAND), BT su UART8 (pad ENET2). VDD33 e VDIO da U37 (3.3 V dedicati ai picchi TX). WL_DIS# e BT_DIS# senza pull-up nel modulo: 10k a GND, li alza Linux.")
r.note("Antenna su U.FL J14 (scelta del placement: la BOM lasciava u.FL o PCB) con rete pi 0R + 2 DNP da tarare. UART_CTS del modulo da UART8_RTS, il modulo non ha RTS (pin 41 = GND): H5 a 3 fili. PCM non usata: PCM_OUT libero (strap da non alzare).")
WN = {1: "GND", 2: "ANT", 3: "GND", 6: "BT_HOST_WAKE", 7: "BT_WAKE_HOST", 9: "VDD33", 12: "WL_DIS_N", 13: "WL_WAKE_HOST", 14: "SD_D2", 15: "SD_D3", 16: "SD_CMD", 17: "SD_CLK", 18: "SD_D0", 19: "SD_D1", 20: "GND", 22: "VDIO", 24: "GPIO8", 25: "PCM_OUT", 26: "PCM_CLK", 27: "PCM_IN", 28: "PCM_SYNC",
      31: "GND", 33: "GND", 34: "BT_DIS_N", 36: "GND", 41: "GND", 42: "UART_TX", 43: "UART_RX", 44: "UART_CTS"}
WIFI = [(str(k), WN.get(k, f"NC{k}"), "L" if k <= 22 else "R") for k in range(1, 45)]
r.add_sym(f"{LIBNAME}:BL-M8723DS1", box_symbol(LIBNAME, "BL-M8723DS1", WIFI, "LB-LINK BL-M8723DS1 Wi-Fi 802.11n + BT 4.2, SDIO/UART, 12x12 mm"))
r.ic(f"{LIBNAME}:BL-M8723DS1", "U35", "BL-M8723DS1", f"{LIBNAME}:LB-LINK_BL-M8723DS1_LGA-44_12x12mm",
     {"GND": GND, "ANT": "WL_ANT", "BT_HOST_WAKE": "BT_HOST_WAKE", "BT_WAKE_HOST": "BT_WAKE_HOST", "VDD33": "3V3_WIFI", "VDIO": "3V3_WIFI", "WL_DIS_N": "WL_DIS_N", "WL_WAKE_HOST": "WL_WAKE_HOST", "SD_D0": "SD2_D0", "SD_D1": "SD2_D1", "SD_D2": "SD2_D2", "SD_D3": "SD2_D3",
      "SD_CMD": "SD2_CMD", "SD_CLK": "SD2_CLK", "BT_DIS_N": "BT_DIS_N", "UART_TX": "BT_UART_TX", "UART_RX": "BT_UART_RX", "UART_CTS": "BT_UART_CTS"}, mpn="BL-M8723DS1")
LD, LDF = r.mik("AP2112K-3.3TRG1")
r.ic(LD, "U37", "AP2112K-3.3TRG1", LDF, {"1": V5, "2": GND, "3": V5, "5": "3V3_WIFI"}, mpn="AP2112K-3.3TRG1", lcsc="C51118")
r.std("Connector:Conn_Coaxial")
r.ic("Connector:Conn_Coaxial", "J14", "U.FL", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", {"1": "WL_ANT_C", "2": GND})
r.group("Wi-Fi: 22R su CLK, pull-up 10k SDIO, enable a GND, rete pi antenna", [("R", "22R", "SD2_CLK_S", "SD2_CLK")] + [("R", "10k", "3V3_WIFI", k_) for k_ in ("SD2_CMD", "SD2_D0", "SD2_D1", "SD2_D2", "SD2_D3")] + [("R", "10k", "WL_DIS_N", GND), ("R", "10k", "BT_DIS_N", GND),
        ("R", "0R", "WL_ANT", "WL_ANT_C"), ("C", "DNP", "WL_ANT", GND, True), ("C", "DNP", "WL_ANT_C", GND, True), ("C", "10uF", "3V3_WIFI", GND), ("C", "22uF/10V", "3V3_WIFI", GND), ("C", "100nF", "3V3_WIFI", GND), ("C", "1uF", V5, GND)])
r.flags(["3V3_WIFI"])

# ================================ GNSS =====================================================================================================
g = Sheet("GNSS", "gnss.kicad_sch", 900, 10)
g.note("U11 u-blox NEO-M9N-00B su UART3. TIMEPULSE -> 33R -> GNSS_PPS su GPT1_CAPTURE1 (UART2_TX) e buffer U20 -> 33R -> header J7. EXTINT IN da J7 -> ESD + 100R -> buffer U19 -> GNSS_EXTINT su NEO e GPT1_CAPTURE2 (UART2_RX): evento marcato da entrambi.")
g.note("J4 SMA antenna, bias 3.3 V attiva: VCC_RF -> 10R -> 27 nH (0603) -> RF_IN, 10 nF. Linea 50 ohm corta. V_BCKP da VDD_SNVS (CR1220 via BAT54C). J7: PPS OUT, EXTINT IN, GND (come scheda Tibbo).")
g.std("RF_GPS:NEO-M9N"), g.std("Device:L"), g.std("Connector_Generic:Conn_01x03"), g.std("Connector:TestPoint")
g.ic("RF_GPS:NEO-M9N", "U11", "NEO-M9N-00B", "RF_GPS:ublox_NEO", {"1": "GNSS_SAFEBOOT_N", "2": "NC", "3": "GNSS_TP", "4": "GNSS_EXTINT", "5": "NC", "6": "NC", "7": GND, "8": "GNSS_RESET_N", "9": "GNSS_VCC_RF", "10": GND, "11": "GNSS_RF_IN", "12": GND, "13": GND,
     "20": "GNSS_UART_RX", "21": "GNSS_UART_TX", "22": SNVS, "23": V33, "24": GND}, mpn="NEO-M9N-00B")
g.ic("Connector:TestPoint", "TP1", "SAFEBOOT_N", "TestPoint:TestPoint_Pad_D1.0mm", {"1": "GNSS_SAFEBOOT_N"}, inbom=False)
g.ic("Connector:TestPoint", "TP2", "RESET_N", "TestPoint:TestPoint_Pad_D1.0mm", {"1": "GNSS_RESET_N"}, inbom=False)
SM, SMF = g.mik("BWSMA-KE-P001")
g.ic(SM, "J4", "SMA antenna", f"{LIBNAME}:" + SMF.split(":")[1], {"5": "GNSS_RF_IN", "1": GND, "2": GND, "3": GND, "4": GND}, mpn="BWSMA-KE-P001", lcsc="C496550")
g.ic("Device:L", "L6", "27nH", "Inductor_SMD:L_0603_1608Metric", {"1": "GNSS_ANT_BIAS", "2": "GNSS_RF_IN"})
g.group("Bias antenna e alimentazione", [("R", "10R", "GNSS_VCC_RF", "GNSS_ANT_BIAS"), ("C", "10nF", "GNSS_ANT_BIAS", GND), ("C", "10uF", V33, GND), ("C", "100nF", V33, GND), ("C", "1uF", SNVS, GND)])
B1, B1F = g.mik("SN74LVC1G17DBVR")
g.ic(B1, "U20", "SN74LVC1G17DBVR", B1F, {"2": "GNSS_TP", "4": "GNSS_PPS_BUF", "5": V33, "3": GND}, mpn="SN74LVC1G17DBVR", lcsc="C7836")
g.ic(B1, "U19", "SN74LVC1G17DBVR", B1F, {"2": "EXTINT_R", "4": "GNSS_EXTINT", "5": V33, "3": GND}, mpn="SN74LVC1G17DBVR", lcsc="C7836")
E1F = mik("ESD9B5.0ST5G")[2]   # simbolo EasyEDA fuori griglia: simbolo KiCad, footprint della libreria
g.std("Device:D_TVS")
g.ic("Device:D_TVS", "D2", "ESD9B5.0ST5G", E1F, {"1": "PPS_OUT", "2": GND}, mpn="ESD9B5.0ST5G", lcsc="C111566")
g.ic("Device:D_TVS", "D3", "ESD9B5.0ST5G", E1F, {"1": "EXTINT_IN", "2": GND}, mpn="ESD9B5.0ST5G", lcsc="C111566")
g.ic("Connector_Generic:Conn_01x03", "J7", "PPS/EXTINT", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", {"1": "PPS_OUT", "2": "EXTINT_IN", "3": GND}, mpn="2.54-1*3P", lcsc="C49257")
g.group("Timing: serie e buffer", [("R", "33R", "GNSS_TP", "GNSS_PPS"), ("R", "33R", "GNSS_PPS_BUF", "PPS_OUT_R"), ("R", "100R", "PPS_OUT_R", "PPS_OUT"), ("R", "100R", "EXTINT_IN", "EXTINT_R"), ("R", "100k", "EXTINT_R", GND), ("C", "100nF", V33, GND), ("C", "100nF", V33, GND)])

json.dump(GROUPS, open(os.path.join(SC, "imx6ull_gruppi.json"), "w"), indent=0, sort_keys=True)
used, glob = write_all(PRJ, f"{PRJ}/{LIBNAME}.kicad_sym")
print("fogli:", 9, "net:", len(used), "globali:", len(glob))
