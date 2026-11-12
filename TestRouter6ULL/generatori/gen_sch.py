"""Schema di TestRouter6ULL: scheda minima i.MX 6ULL + una DDR3L x16, da dare a BoardLab per provare lo sbroglio. Fogli CPU, DDR3L, Alimentazione.
Uso: python3 gen_sch.py ../progetto
Mappa delle sfere del 6ULL, simbolo DDR3L e reti di supporto ripresi da SchedaIMX6ULL-SD/ProvaDDR (branch claude/project-thread-034nik).
Resistenze 0603; condensatori 0603 minimo, bulk 0805 e 1206 (kisheet.cap_fp)."""
import json
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, multi_symbol, place_multi, write_all, GROUPS
from kilib import LIBNAME, extract

PRJ = sys.argv[1]
BALLS = {k: v["name"] for k, v in json.load(open(os.path.join(SC, "imx6ull_balls.json"))).items()}
assert len(BALLS) == 289
GND = "GND_D"
V33 = "3V3"
V135 = "V1P35"
V14 = "V1P4"
V5 = "5V_SYS"

# ================================ mappa delle sfere del 6ULL usate ===============================================================
# Nome della sfera -> net. Sfere: tabelle 90/91 di IMX6ULLCEC Rev 1.2. Tutto quello che non e' qui resta scollegato (no_connect).
NET = {
    # alimentazioni
    "ADC_VREFH": V33, "VDDA_ADC_3P3": V33, "DRAM_VREF": "DDR_VREF", "GPANIO": "NC", "NGND_KEL0": GND, "VSS": GND,
    "NVCC_CSI": V33, "NVCC_DRAM": V135, "NVCC_DRAM_2P5": "VDD_HIGH_CAP", "NVCC_ENET": V33, "NVCC_GPIO": V33, "NVCC_LCD": V33,
    "NVCC_NAND": V33, "NVCC_PLL": "NVCC_PLL", "NVCC_SD1": V33, "NVCC_UART": V33, "VDD_ARM_CAP": "VDD_ARM_CAP",
    "VDD_HIGH_CAP": "VDD_HIGH_CAP", "VDD_HIGH_IN": V33, "VDD_SNVS_CAP": "VDD_SNVS_CAP", "VDD_SNVS_IN": V33,
    "VDD_SOC_CAP": "VDD_SOC_CAP", "VDD_SOC_IN": V14, "VDD_USB_CAP": "VDD_USB_CAP",
    # sistema
    "BOOT_MODE0": "BOOT_MODE0", "BOOT_MODE1": "BOOT_MODE1", "TEST_MODE": GND, "JTAG_MOD": "JTAG_MOD", "POR_B": "POR_B",
    "XTALI": "XTALI", "XTALO": "XTALO", "RTC_XTALI": "RTC_XTALI", "RTC_XTALO": "RTC_XTALO",
    # console UART1
    "UART1_TX_DATA": "UART1_TX", "UART1_RX_DATA": "UART1_RX",
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

# ================================ CPU ==================================================================================================
s = Sheet("CPU", "cpu.kicad_sch", 100, 2, paper="A0")
UNITS = [
    ("DDR3L", lambda n: n.startswith("DRAM_")),
    ("Alimentazioni", lambda n: n in ("ADC_VREFH", "VDDA_ADC_3P3", "NGND_KEL0", "GPANIO") or n.startswith(("NVCC_", "VDD_"))),
    ("Masse", lambda n: n == "VSS"),
    ("LCD / BOOT_CFG", lambda n: n.startswith(("LCD_", "BOOT_"))),
    ("NAND e SD1", lambda n: n.startswith(("NAND_", "SD1_"))),
    ("CSI e ENET2", lambda n: n.startswith(("CSI_", "ENET2_"))),
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
s.note("U1 NXP MCIMX6Y2CVM08AB (i.MX 6ULL, MAPBGA-289 14x14 mm passo 0.8). Scheda di prova per lo sbroglio: collegati solo DDR3L, alimentazioni, clock, reset, boot e console UART1.")
s.note("Boot: BOOT_MODE[1:0]=01 (serial downloader, la scheda non ha memorie di boot): il ROM resta in attesa su UART1/USB. R105/R106 DNP per BOOT_MODE=10 (boot interno).")
s.note("POR_B: RC 10k/1uF dal 3.3 V (circa 10 ms). JTAG non usato: JTAG_MOD a GND con 4.7k (tabella 3).")
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
s.group("VDD_SOC_IN 1.4 V", [("C", "22uF", V14, GND)] + [("C", "100nF", V14, GND)] * 2)
s.group("VDD_HIGH_IN e NVCC 3.3 V: un 100 nF per dominio (CSI, ENET, GPIO, LCD, NAND, SD1, UART)", [("C", "22uF", V33, GND)] + [("C", "100nF", V33, GND)] * 7)
s.group("NVCC_DRAM 1.35 V (lato SoC)", [("C", "22uF", V135, GND)] + [("C", "100nF", V135, GND)] * 3)
s.group("VDD_SNVS_IN", [("C", "1uF", V33, GND)])
Y1_ID, Y1_FP = s.mik("X322524MOB4SI")
s.ic(Y1_ID, "Y1", "24MHz", Y1_FP, {"1": "XTALI", "3": "XTALO", "2": GND, "4": GND}, mpn="X322524MOB4SI", lcsc="C70590")
s.group("Carico 24 MHz (CL da verificare sul quarzo YXC)", [("C", "18pF", "XTALI", GND), ("C", "18pF", "XTALO", GND)])
Y2_ID, Y2_FP = s.mik("Q13FC1350000400")
s.ic(Y2_ID, "Y2", "32.768kHz", f"{LIBNAME}:" + Y2_FP.split(":")[1], {"1": "RTC_XTALI", "2": "RTC_XTALO"}, mpn="Q13FC13500004", lcsc="C32346")
s.group("Carico RTC: circa 2xCL meno parassite (datasheet, tabella 3)", [("C", "12pF", "RTC_XTALI", GND), ("C", "12pF", "RTC_XTALO", GND)])
s.group("Boot: BOOT_MODE=01 serial downloader; le due DNP danno BOOT_MODE=10; JTAG_MOD a GND con 4.7k",
        [("R", "10k", "BOOT_MODE0", V33), ("R", "10k", "BOOT_MODE1", GND), ("R", "4.7k", "JTAG_MOD", GND),
         ("R", "10k", "BOOT_MODE0", GND, True), ("R", "10k", "BOOT_MODE1", V33, True)])
s.group("POR_B: RC 10k/1uF", [("R", "10k", V33, "POR_B"), ("C", "1uF", "POR_B", GND)])
s.std("Connector_Generic:Conn_01x03")
s.ic("Connector_Generic:Conn_01x03", "J2", "Console UART1", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     {"1": "UART1_TX", "2": "UART1_RX", "3": GND}, mpn="2.54-1*3P", lcsc="C49257")
s.flags(["VDD_HIGH_CAP", "VDD_ARM_CAP", "VDD_SOC_CAP", "NVCC_PLL", "VDD_SNVS_CAP", "VDD_USB_CAP"])

# ================================ DDR3L ===================================================================================================
d = Sheet("DDR3L", "ddr3l.kicad_sch", 200, 3)
# AS4C512M16D3LC non c'e' nella libreria MIKILAB: MT41K512M16HA, stessa ball map JEDEC x16 e stesso FBGA-96 9x14.
t = extract("Memory_RAM", "MT41K256M16HA")
i = t.find('(number "M7"')
j = t.rfind('(name "NC"', 0, i)
k = t.rfind("(pin ", 0, j)
t = t[:k] + t[k:j].replace("(pin no_connect", "(pin input", 1).replace("(hide yes)", "") + '(name "A15"' + t[j + len('(name "NC"'):]
t = t.replace("Memory_RAM:MT41K256M16HA", f"{LIBNAME}:MT41K512M16HA").replace("MT41K256M16HA", "MT41K512M16HA")
d.add_sym(f"{LIBNAME}:MT41K512M16HA", t)
d.note("U2 Micron MT41K512M16HA-107:A, 8 Gb x16 = 1 GB, FBGA-96 9x14 passo 0.8, a 1.35 V (equivalente: Alliance AS4C512M16D3LC, stessa ball map). Un solo chip punto-punto: niente VTT. Simbolo da MT41K256M16HA di KiCad con A15 su M7.")
d.note("VREF a partitore 1k/1k con 100 nF su ogni resistenza, unica per DRAM_VREF, VREFCA, VREFDQ. ZQ 240R 1% su SoC e DRAM. RESET# e CKE con 10k a GND. CK con 100R differenziale vicino alla DRAM.")
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
d.group("VREF, ZQ, pull-down", [("R", "1k 1%", V135, "DDR_VREF"), ("R", "1k 1%", "DDR_VREF", GND), ("C", "100nF", V135, "DDR_VREF"), ("C", "100nF", "DDR_VREF", GND),
        ("R", "240R 1%", "DDR_ZQ", GND), ("R", "240R 1%", "SOC_DDR_ZQ", GND), ("R", "10k", "DDR_RESET_N", GND), ("R", "10k", "DDR_CKE", GND), ("R", "100R", "DDR_CK_P", "DDR_CK_N")])
d.group("VDD / VDDQ 1.35 V", [("C", "22uF", V135, GND)] + [("C", "100nF", V135, GND)] * 5)
d.flags(["DDR_VREF"])

# ================================ Alimentazione ==========================================================================================
p = Sheet("Alimentazione", "alimentazione.kicad_sch", 300, 4)
p.note("Ingresso 5 V su J1 (header 2 pin) -> buck 3.3 V (U3 TPS563201), 1.35 V DDR (U4 TLV62569), 1.4 V VDD_SOC_IN (U5 TLV62569). Stessi valori della scheda SchedaIMX6ULL-SD.")
p.note("Sequenza 3.3 -> 1.35 -> 1.4 V a RC sugli EN dei TLV62569 (soglia EN max 1.2 V): 100k/470nF circa 21 ms, 100k/1uF circa 45 ms. Passivi 0603 minimo; 47 uF in 1206, 22 uF e 10 uF in 0805.")
p.std("Connector_Generic:Conn_01x02"), p.std("Device:L")
p.ic("Connector_Generic:Conn_01x02", "J1", "5V IN", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", {"1": V5, "2": GND}, mpn="2.54-1*2P", lcsc="C49661")
p.group("Ingresso 5 V", [("C", "22uF", V5, GND), ("C", "100nF", V5, GND)])
T, TF = p.mik("TPS563201DDCR")
p.ic(T, "U3", "TPS563201DDCR", TF, {"VIN": V5, "EN": "U3_EN", "GND": GND, "SW": "U3_SW", "VBST": "U3_BST", "VFB": "U3_FB"}, mpn="TPS563201DDCR", lcsc="C116592")
p.ic("Device:L", "L1", "2.2uH/4A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U3_SW", "2": V33}, mpn="XAL4020-222")
p.group("U3 3.3 V / 3 A: FB 33.2k/10k = 3.32 V, primo della sequenza", [("C", "10uF/16V", V5, GND), ("R", "100k", V5, "U3_EN"), ("C", "100nF", "U3_BST", "U3_SW"),
        ("R", "33.2k 1%", V33, "U3_FB"), ("R", "10k 1%", "U3_FB", GND), ("C", "47uF/10V", V33, GND)])
TL, TLF = p.mik("TLV62569DBVR")
p.ic(TL, "U4", "TLV62569DBVR", TLF, {"1": "U4_EN", "2": GND, "3": "U4_SW", "4": V5, "5": "U4_FB"}, mpn="TLV62569DBVR")
p.ic("Device:L", "L2", "2.2uH/3A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U4_SW", "2": V135}, mpn="XAL4020-222")
p.group("U4 1.35 V DDR: FB 150k/120k (0.6 V x 2.25), EN 100k/470nF da 3V3", [("C", "10uF/10V", V5, GND), ("R", "100k", V33, "U4_EN"), ("C", "470nF", "U4_EN", GND), ("R", "150k 1%", V135, "U4_FB"), ("R", "120k 1%", "U4_FB", GND),
        ("C", "22uF/10V", V135, GND)])
p.ic(TL, "U5", "TLV62569DBVR", TLF, {"1": "U5_EN", "2": GND, "3": "U5_SW", "4": V5, "5": "U5_FB"}, mpn="TLV62569DBVR")
p.ic("Device:L", "L3", "2.2uH/3A", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", {"1": "U5_SW", "2": V14}, mpn="XAL4020-222")
p.group("U5 1.4 V VDD_SOC_IN: FB 133k/100k = 1.398 V, EN 100k/1uF da 3V3", [("C", "10uF/10V", V5, GND), ("R", "100k", V33, "U5_EN"), ("C", "1uF", "U5_EN", GND), ("R", "133k 1%", V14, "U5_FB"), ("R", "100k 1%", "U5_FB", GND),
        ("C", "22uF/10V", V14, GND)])
p.flags([V5, V33, V135, V14, GND])

json.dump(GROUPS, open(os.path.join(SC, "gruppi.json"), "w"), indent=0, sort_keys=True)
RAILS = {GND, V33, V5, V135, V14}
BUSES = {"DDR_A[0..15]": [f"DDR_A{i}" for i in range(16)], "DDR_DQ[0..15]": [f"DDR_DQ{i}" for i in range(16)], "DDR_BA[0..2]": [f"DDR_BA{i}" for i in range(3)]}
ORDER = ["DDR3L", "Alimentazione"]
used, multi, pins = write_all(PRJ, f"{PRJ}/{LIBNAME}.kicad_sym", RAILS, BUSES, ORDER)
print("fogli:", 3, "net:", len(used), "tra fogli:", len(multi), "pin sul blocco CPU:", len(pins["CPU"]))
