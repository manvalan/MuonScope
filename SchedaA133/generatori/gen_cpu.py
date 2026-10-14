"""Foglio KiCad 10 'CPU' della scheda A133: SoC in 5 unità, clock, reset/FEL, strap, UART0, interfaccia bus, porte verso i fogli futuri."""
import os
import json, re, sys, uuid
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
BALLS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "a133_balls.json")))

# ---------------- simbolo A133 multi-unità (ball map dal reference Allwinner A100_A133_B3) -------------
def short(n):
    return n.split("/")[0].strip()

UNIT_OF = {"A": 1, "B": None, "C": 4, "D": 5}
units = {i: [] for i in range(1, 6)}
for ball, (name, u) in BALLS.items():
    n = short(name)
    if u == "B":
        uu = 2 if n.startswith(("PB", "PC", "PD", "VCC_PC", "VCC_PD", "VCC_LVDS")) else 3
    else:
        uu = UNIT_OF[u]
    units[uu].append((ball, n, name))

def natkey(t):
    n = t[1]
    m = re.match(r"([A-Z_]+?)(\d+)$", n)
    return (m.group(1), int(m.group(2))) if m else (n, 0)

UNIT_TITLE = {1: "DRAM", 2: "PB-PC-PD", 3: "PE-PF-PG-PH-PL", 4: "SISTEMA-USB-ANALOGICA", 5: "ALIMENTAZIONE-GND"}
sub, A133_PINS = [], {}
for uu in range(1, 6):
    lst = sorted(units[uu], key=natkey)
    half = (len(lst) + 1) // 2
    left, right = lst[:half], lst[half:]
    w = 22.86
    top = 2.54 * (half + 1) / 2
    top = G(top)
    body = [f'(symbol "A133_{uu}_1" (rectangle (start {-w:.2f} {top:.2f}) (end {w:.2f} {-top - 2.54 * 1:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))',
            f'(text "{UNIT_TITLE[uu]}" (at 0 {top + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))']
    A133_PINS[uu] = []
    for side, group in ((0, left), (180, right)):
        for i, (ball, n, full) in enumerate(group):
            x = -w - 2.54 if side == 0 else w + 2.54
            y = top - 2.54 * (i + 1)
            body.append(f'(pin passive line (at {x:.2f} {y:.2f} {side}) (length 2.54) (name "{n}" (effects (font (size 1.016 1.016)))) (number "{ball}" (effects (font (size 1.016 1.016)))))')
            A133_PINS[uu].append((ball, n, x, y, side))
    body.append(")")
    sub.append(" ".join(body))
A133_SYM = ('(symbol "A133:A133" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no) '
            '(property "Reference" "U" (at 0 2.54 0) (effects (font (size 1.27 1.27)))) (property "Value" "A133" (at 0 0 0) (effects (font (size 1.27 1.27)))) '
            '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) (property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            '(property "Description" "Allwinner A133, LFBGA-346 12x12 mm passo 0.5 mm" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            + " ".join(sub) + " (embedded_fonts no))")

SYMS = {
    "A133:A133": A133_SYM,
    "Device:C": extract("Device", "C"), "Device:R": extract("Device", "R"),
    "Device:Crystal_GND24": extract("Device", "Crystal_GND24"), "Device:Crystal": extract("Device", "Crystal"),
    "Switch:SW_Push": extract("Switch", "SW_Push"), "Connector_Generic:Conn_01x03": extract("Connector_Generic", "Conn_01x03"),
    "Power_Protection:TPD4E05U06DQA": extract("Power_Protection", "TPD4E05U06DQA"),
}
PINS = {k: pins(v) for k, v in SYMS.items() if k != "A133:A133"}

GLOBAL = {"GND_D"}
GLOBAL_PREFIX = ("DRAM_", "EMMC_", "SD_", "WL_", "BT_", "RGMII_", "PHY_", "GNSS_", "WIFI_", "USB1_")  # bus delle memorie: etichette globali verso il foglio Memorie
RAILS = ["VDD-CPU", "VDD-CPUFB", "VDD-SYS", "VDD-SYSFB", "VDD-CPUS", "VCC-DRAM", "VCC-PLL", "VCC-PE", "VCC-PL", "VCC-PG",
         "VCC-PC", "VCC-IO", "VCC-RTC", "AP-RESET", "AP-NMI", "PMU-SCK", "PMU-SDA", "USB0_DP", "USB0_DM", "3V3_SYS",
         "PD_I2C_SCL", "PD_I2C_SDA", "PD_INT_N", "VBUS_SRC_EN", "PWR_SRC_ST"]
BUSNETS = ["PWR_SPI_SCLK", "PWR_SPI_MOSI", "PWR_SPI_MISO", "PWR_SPI_INA239A_CS", "PWR_SPI_INA239B_CS", "PWR_SPI_DAC_CS",
           "VREF_ENABLE", "VBIAS_ENABLE", "DAC61402_FAULT", "MAIN_SPI_SCLK", "MAIN_SPI_MOSI", "MAIN_SPI_MISO", "MAIN_I2C_SDA",
           "MAIN_I2C_SCL", "MAIN_SPI_CS_MASTER", "MAIN_SPI_ADDR_0", "MAIN_SPI_ADDR_1", "MAIN_SPI_ADDR_2", "MAIN_SPI_PREFIX_0",
           "MAIN_SPI_PREFIX_1", "MAIN_SPI_PREFIX_2", "MAIN_SPI_ALERT_N"]
HIERSET = set(RAILS + BUSNETS)
items, hier = [], []


def is_hier(net):
    return net in HIERSET or net.startswith(("WL_", "BT_", "RGMII_", "PHY_", "GNSS_", "USB1_", "WIFI_"))


def label(net, x, y, ang):
    j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
    if net in GLOBAL or net.startswith(GLOBAL_PREFIX):
        items.append(f'(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) {F.format(j=j)} (uuid "{U()}"))')
    elif is_hier(net):
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
    return f"{m.group(1)}{300 + int(m.group(2))}"  # serie 3xx: foglio CPU


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


def text(s, x, y):
    items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')


R0402, C0402, C0603 = "Resistor_SMD:R_0402_1005Metric", "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric"
R = lambda ref, val, x, y, a, b, **k: place("Device:R", ref, val, R0402, x, y, {"1": a, "2": b}, **k)
C = lambda ref, val, x, y, a, b, fp=C0402, **k: place("Device:C", ref, val, fp, x, y, {"1": a, "2": b}, **k)

# ---------------- net di ogni ball del SoC --------------------------------------------------------
NET = {}
# Unità 1: DRAM -> etichette globali DRAM_* verso il foglio Memorie
DRAM_USED = {"SA0", "SA1", "SA2", "SA3", "SA4", "SA5", "SCS0", "SCS1", "SCKE0", "SCKE1", "SCKP", "SCKN", "SRST"} | {f"SDQ{i}" for i in range(32)} | {f"SDQS{i}{p}" for i in range(4) for p in "PN"} | {f"SDQM{i}" for i in range(4)}
for ball, n, full in units[1]:
    if n.startswith("VCC_DRAM"):
        NET[ball] = "VCC-DRAM"
    elif n == "VDD18_DRAM":
        NET[ball] = "VCC-PLL"
    elif n == "SZQ":
        NET[ball] = "SOC_SZQ"
    elif n in DRAM_USED:
        NET[ball] = "DRAM_" + n[1:]
    else:
        NET[ball] = "NC"  # SA6-SA16, SBA, SBG, SACT, SODT: non usati con LPDDR4 (come nel reference)
# Unità 2/3: GPIO
GPIO = {
    "PB1": "SOC_PWR_SCLK", "PB2": "SOC_PWR_MOSI", "PB3": "PWR_SPI_MISO", "PB4": "PWR_SPI_INA239A_CS",
    "PB5": "PWR_SPI_INA239B_CS", "PB6": "PWR_SPI_DAC_CS", "PB7": "VREF_ENABLE", "PB8": "VBIAS_ENABLE",
    "PB9": "UART0_TX", "PB10": "UART0_RX",
    "PC0": "EMMC_DS", "PC1": "EMMC_RST", "PC5": "EMMC_CLK", "PC6": "EMMC_CMD", "PC8": "EMMC_D3", "PC9": "EMMC_D4",
    "PC10": "EMMC_D0", "PC11": "EMMC_D5", "PC13": "EMMC_D1", "PC14": "EMMC_D6", "PC15": "EMMC_D2", "PC16": "EMMC_D7",
    "PD0": "MAIN_SPI_ALERT_N", "PD1": "DAC61402_FAULT", "PD2": "USB1_VBUS_EN", "PD3": "USB1_OC_N", "PD10": "MAIN_SPI_CS_MASTER", "PD11": "SOC_MAIN_SCLK",
    "PD12": "SOC_MAIN_MOSI", "PD13": "MAIN_SPI_MISO", "PD14": "GNSS_UART3_TX", "PD15": "GNSS_UART3_RX",
    "PD16": "SOC_ADDR_0", "PD17": "SOC_ADDR_1", "PD18": "SOC_ADDR_2", "PD19": "SOC_PREFIX_0", "PD20": "SOC_PREFIX_1",
    "PD21": "SOC_PREFIX_2", "PD22": "MAIN_I2C_SCL", "PD23": "MAIN_I2C_SDA",
    "PF0": "SD_D1", "PF1": "SD_D0", "PF2": "SD_CLK", "PF3": "SD_CMD", "PF4": "SD_D3", "PF5": "SD_D2", "PF6": "SD_DET",
    "PG0": "WL_SDIO_CLK", "PG1": "WL_SDIO_CMD", "PG2": "WL_SDIO_D0", "PG3": "WL_SDIO_D1", "PG4": "WL_SDIO_D2",
    "PG5": "WL_SDIO_D3", "PG6": "BT_UART_TX", "PG7": "BT_UART_RX", "PG8": "BT_UART_RTS", "PG9": "BT_UART_CTS",
    "PG10": "GNSS_PPS", "PG11": "WL_HOST_WAKE", "PG12": "BT_HOST_WAKE", "PG13": "BT_WAKE",
    "PH0": "RGMII_RXD1", "PH1": "RGMII_RXD0", "PH2": "RGMII_RXCTL", "PH3": "RGMII_CLKIN", "PH4": "RGMII_TXD1",
    "PH5": "RGMII_TXD0", "PH6": "RGMII_TXCK", "PH7": "RGMII_TXCTL", "PH9": "PHY_MDC", "PH10": "PHY_MDIO",
    "PH11": "PHY_RST_N", "PH12": "PHY_INT_N", "PH13": "PHY_25M", "PH14": "RGMII_RXD3", "PH15": "RGMII_RXD2",
    "PH16": "RGMII_RXCK", "PH17": "RGMII_TXD3", "PH18": "RGMII_TXD2",
    "PL0": "PMU-SCK", "PL1": "PMU-SDA", "PL4": "WL_REG_ON", "PL5": "BT_REG_ON", "PL6": "PWR_SRC_ST",
    "PL8": "PD_I2C_SCL", "PL9": "PD_I2C_SDA", "PL10": "PD_INT_N", "PL11": "VBUS_SRC_EN",
    "VCC_PC": "VCC-PC", "VCC_PD": "VCC-IO", "VCC_LVDS": "VCC-PC", "VCC_PE": "VCC-PE", "VCC_PG": "VCC-PG", "VCC_PL": "VCC-PL",
}
SYSN = {
    "USB0_DM": "USB0_DM", "USB0_DP": "USB0_DP", "USB1_DM": "USB1_DM", "USB1_DP": "USB1_DP", "VCC_USB": "VCC-IO",
    "VDD_USB": "VDD-SYS", "AVCC": "VCC-PLL", "VRA1": "SOC_VRA1", "VRA2": "SOC_VRA2", "AGND": "SOC_AGND",
    "CPVEE": "SOC_VEE", "VEE": "SOC_VEE", "CPVIN": "VCC-PC", "CPVDD": "SOC_CPVDD", "GPADC0": "BOOT_SEL_ADC",
    "GPADC1": "DDR_PARA_ADC", "VCC_MCSI": "VCC-PC", "FEL": "SOC_FEL", "NMI": "AP-NMI", "RESET": "AP-RESET",
    "VCC_EFUSE": "VCC-PC", "X32KIN": "X32KIN", "X32KOUT": "X32KOUT", "X32KFOUT": "WIFI_32K", "VCC_RTC": "VCC-RTC",
    "RTCVIO": "VCC-RTC", "VCC_PLL": "VCC-PLL", "DXIN": "DCXO_XIN", "DXOUT": "DCXO_XOUT", "REFCLK_OUT": "NC",
    "DXLDO_OUT": "SOC_DXLDO", "WREQIN": "SOC_WREQIN",
}
for uu in (2, 3, 4):
    for ball, n, full in units[uu]:
        NET[ball] = (GPIO if uu in (2, 3) else SYSN).get(n, "NC")
for ball, n, full in units[5]:
    if n.startswith("GND"):
        NET[ball] = "GND_D"
    elif n.startswith("VDD_CPU") and n != "VDD_CPUFB" and n != "VDD_CPUS":
        NET[ball] = "VDD-CPU"
    else:
        NET[ball] = {"VDD_CPUFB": "VDD-CPUFB", "VDD_SYSFB": "VDD-SYSFB", "VDD_CPUS": "VDD-CPUS", "VCC_IO": "VCC-IO"}.get(n, "VDD-SYS" if n.startswith("VDD_SYS") else "NC")

POS = {1: (95, 120), 2: (95, 275), 3: (95, 430), 4: (520, 150), 5: (520, 330)}
for uu in range(1, 6):
    x0, y0 = G(POS[uu][0]), G(POS[uu][1])
    for ball, n, px, py, side in A133_PINS[uu]:
        stub(round(x0 + px, 2), round(y0 - py, 2), side, NET[ball], L=5.08 if NET[ball] != "NC" else 2.54)
    sym_instance("A133:A133", "U301", "A133", "A133:LFBGA-346_12x12mm_P0.5mm", x0, y0,
                 [b for b, *_ in A133_PINS[uu]], unit=uu, fx=x0 - 20, fy=y0 - (len(A133_PINS[uu]) + 1) * 1.27 / 1 * 0.5 - 6)

text("CPU: Allwinner A133 (LFBGA-346). Ball map dal reference Allwinner A100_A133_B3_AXP707_LPDDR3 (pagine 06-08). Serie componenti 3xx.", 20, 15)
text("Porte verso i fogli futuri: DRAM_* (LPDDR4), EMMC_* (PC), SD_* (PF), WL_*/BT_* (AP6256 su PG + PL4/PL5), RGMII_*/PHY_* (RTL8211F su PH), GNSS_* (UART3 PD14/PD15, PPS su PG10).", 20, 20)
text("Bus: interfaccia-bus-mikilab rev. 4. FUSB302B su S_TWI1 (PL8/PL9) con pull-up a VCC-PL; 3V3_SYS del FUSB302B preso da VCC-PL tramite R 0R.", 20, 25)

# ---------------- clock: 24 MHz DCXO e 32.768 kHz -------------------------------------------------
X, Y = 230, 60
text("Clock come nel reference: quarzo 24 MHz su DXIN/DXOUT (18 pF), 32.768 kHz su X32KIN/X32KOUT (22 pF, 10M in parallelo). WREQIN a GND (fanout 24 MHz non usato).", X - 10, Y - 15)
place("Device:Crystal_GND24", "Y1", "24MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", X + 15, Y, {"1": "DCXO_XIN", "3": "DCXO_XOUT_R", "2": "GND_D", "4": "GND_D"}, extra_props=(("MPN", "E3SB24.0000F12E11"),))
C("C1", "18pF/50V", X, Y + 10, "DCXO_XIN", "GND_D")
C("C2", "18pF/50V", X + 30, Y + 10, "DCXO_XOUT_R", "GND_D")
R("R1", "0R", X + 40, Y + 10, "DCXO_XOUT", "DCXO_XOUT_R")
place("Device:Crystal", "Y2", "32.768kHz", "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", X + 70, Y, {"1": "X32KIN", "2": "X32KOUT"})
C("C3", "22pF/50V", X + 60, Y + 10, "X32KIN", "GND_D")
C("C4", "22pF/50V", X + 85, Y + 10, "X32KOUT", "GND_D")
R("R2", "10M", X + 95, Y + 10, "X32KIN", "X32KOUT")
C("C5", "220nF/16V", X + 110, Y + 10, "SOC_DXLDO", "GND_D")
R("R3", "0R", X + 120, Y + 10, "SOC_WREQIN", "GND_D")

# ---------------- reset, NMI, FEL, strap di boot, UART0 ------------------------------------------
X, Y = 230, 110
text("Reset/FEL: AP-RESET dal PWROK del PMIC + tasto RESET; tasto FEL (UBOOT) a GND. Strap GPADC0 = 10k/3k9 (riga 4: SMHC0 poi eMMC). GPADC1 DDR PARA come nel reference (DNP).", X - 10, Y - 12)
C("C6", "1nF/50V", X, Y, "AP-RESET", "GND_D")
C("C7", "1nF/50V", X + 10, Y, "AP-NMI", "GND_D")
place("Switch:SW_Push", "SW1", "RESET", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X + 25, Y, {"1": "AP-RESET", "2": "GND_D"})
place("Switch:SW_Push", "SW2", "FEL", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X + 45, Y, {"1": "SOC_FEL", "2": "GND_D"})
R("R4", "10k", X + 60, Y, "VCC-IO", "SOC_FEL")
R("R5", "10k 1%", X + 75, Y - 5, "VCC-PLL", "BOOT_SEL_ADC")
R("R6", "3.9k 1%", X + 75, Y + 10, "BOOT_SEL_ADC", "GND_D")
R("R7", "10k 1%", X + 90, Y - 5, "VCC-PLL", "DDR_PARA_ADC", dnp=True)
R("R8", "10k 1%", X + 90, Y + 10, "DDR_PARA_ADC", "GND_D", dnp=True)
place("Connector_Generic:Conn_01x03", "J1", "UART0 debug", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", X + 115, Y,
      {"1": "UART0_TX", "2": "UART0_RX", "3": "GND_D"})
text("J301: 1 = TX del SoC (PB9), 2 = RX del SoC (PB10), 3 = GND. Livelli 3.3 V.", X + 100, Y + 12)

# ---------------- disaccoppiamento e parte analogica (reference pag. 06) ------------------------------
X, Y = 230, 160
text("Disaccoppiamento come nel reference: VDD-CPU 10uF + 2x2.2uF, VDD-SYS 10uF + 2x2.2uF, 0.1uF su VDD-CPUS/VDD-USB/VCC-MCSI/VCC-EFUSE/VCC-RTC/VCC-PLL/VCC-USB, VCC-IO 1uF + 0.1uF.", X - 10, Y - 10)
caps = [("C8", "10uF/16V", "VDD-CPU", C0603), ("C9", "2.2uF/6.3V", "VDD-CPU", C0402), ("C10", "2.2uF/6.3V", "VDD-CPU", C0402),
        ("C11", "10uF/16V", "VDD-SYS", C0603), ("C12", "2.2uF/6.3V", "VDD-SYS", C0402), ("C13", "2.2uF/6.3V", "VDD-SYS", C0402),
        ("C14", "0.1uF", "VDD-CPUS", C0402), ("C15", "1uF/10V", "VCC-IO", C0402), ("C16", "0.1uF", "VCC-IO", C0402),
        ("C17", "0.1uF", "VCC-RTC", C0402), ("C18", "0.1uF", "VCC-PLL", C0402), ("C19", "0.1uF", "VCC-PC", C0402),
        ("C20", "0.1uF", "VCC-PE", C0402), ("C21", "0.1uF", "VCC-PG", C0402), ("C22", "0.1uF", "VCC-PL", C0402),
        ("C23", "0.1uF", "VCC-PC", C0402), ("C24", "0.1uF", "VCC-IO", C0402)]
for i, (ref, val, net, fp) in enumerate(caps):
    C(ref, val, X + 10 * (i % 12), Y + 18 * (i // 12), net, "GND_D", fp)
X, Y = 230, 215
text("Analogica: AVCC 2.2uF, VRA1/VRA2 470nF verso AGND, AGND a GND con 0R, CPVIN 10uF, VEE/CPVEE 2.2uF (stella, non fly-by), CPVDD 2.2uF.", X - 10, Y - 10)
C("C25", "2.2uF/6.3V", X, Y, "VCC-PLL", "SOC_AGND", C0603)
C("C26", "470nF/16V", X + 10, Y, "SOC_VRA1", "SOC_AGND")
C("C27", "470nF/16V", X + 20, Y, "SOC_VRA2", "SOC_AGND")
R("R9", "0R", X + 30, Y, "SOC_AGND", "GND_D")
C("C28", "10uF/16V", X + 40, Y, "VCC-PC", "GND_D", C0603)
C("C29", "2.2uF/6.3V", X + 50, Y, "SOC_VEE", "GND_D")
C("C30", "2.2uF/6.3V", X + 60, Y, "SOC_CPVDD", "GND_D")
R("R10", "240R 1%", X + 70, Y, "SOC_SZQ", "GND_D")
text("R310: ZQ della DRAM lato SoC, 240R 1% a GND (RD3 del reference).", X + 60, Y + 12)

# ---------------- interfaccia bus: serie, pull-up/pull-down ---------------------------------------
X, Y = 230, 260
text("Bus: 33R serie vicino al SoC su CLK/MOSI di SPI2 (BUS_POWER) e SPI1 (MAIN); 100R serie su ADDR/PREFIX. MISO diretti.", X - 10, Y - 10)
for i, (ref, a, b) in enumerate([("R11", "SOC_PWR_SCLK", "PWR_SPI_SCLK"), ("R12", "SOC_PWR_MOSI", "PWR_SPI_MOSI"),
                                 ("R13", "SOC_MAIN_SCLK", "MAIN_SPI_SCLK"), ("R14", "SOC_MAIN_MOSI", "MAIN_SPI_MOSI")]):
    R(ref, "33R", X + 12 * i, Y, a, b)
for i in range(3):
    R(f"R{15 + i}", "100R", X + 50 + 12 * i, Y, f"SOC_ADDR_{i}", f"MAIN_SPI_ADDR_{i}")
    R(f"R{18 + i}", "100R", X + 86 + 12 * i, Y, f"SOC_PREFIX_{i}", f"MAIN_SPI_PREFIX_{i}")
X, Y = 230, 295
text("Livelli di riposo sicuri: CS e CS_MASTER alti (10k), VREF_ENABLE basso = riferimenti spenti (attivo alto, 10k a GND), VBIAS_ENABLE basso = bias spento (100k a GND).", X - 10, Y - 12)
text("ALERT# 4.7k unico pull-up del bus. DAC61402_FAULT 10k (open-drain). I2C0 del bus 2.2k. S_TWI1 del FUSB302B 2.2k a VCC-PL, PD_INT_N 10k.", X - 10, Y - 7)
pu = [("R21", "10k", "VCC-IO", "PWR_SPI_INA239A_CS"), ("R22", "10k", "VCC-IO", "PWR_SPI_INA239B_CS"), ("R23", "10k", "VCC-IO", "PWR_SPI_DAC_CS"),
      ("R24", "10k", "GND_D", "VREF_ENABLE"), ("R25", "100k", "VBIAS_ENABLE", "GND_D"), ("R26", "10k", "VCC-IO", "DAC61402_FAULT"),
      ("R27", "10k", "VCC-IO", "MAIN_SPI_CS_MASTER"), ("R28", "4.7k", "VCC-IO", "MAIN_SPI_ALERT_N"), ("R29", "2.2k", "VCC-IO", "MAIN_I2C_SCL"),
      ("R30", "2.2k", "VCC-IO", "MAIN_I2C_SDA"), ("R31", "2.2k", "VCC-PL", "PD_I2C_SCL"), ("R32", "2.2k", "VCC-PL", "PD_I2C_SDA"),
      ("R33", "10k", "VCC-PL", "PD_INT_N"), ("R34", "10k", "VCC-PL", "PWR_SRC_ST"), ("R35", "0R", "VCC-PL", "3V3_SYS")]
for i, (ref, val, a, b) in enumerate(pu):
    R(ref, val, X + 10 * (i % 8), Y + 20 * (i // 8), a, b)

# ---------------- ESD sulle linee dei connettori -----------------------------------------------------
X, Y = 230, 360
text("ESD bassa capacita TPD4E05U06DQA (0.5 pF, 5.5 V) sulle linee logiche di J1/J2, da piazzare vicino ai connettori. Nessuna protezione sui V_BIAS (30 V) e sui riferimenti.", X - 10, Y - 15)
esd = BUSNETS[:]
for k in range(6):
    group = esd[4 * k: 4 * k + 4]
    nets = {"1": group[0], "2": group[1], "4": group[2] if len(group) > 2 else "NC", "5": group[3] if len(group) > 3 else "NC",
            "3": "GND_D", "8": "GND_D"}
    place("Power_Protection:TPD4E05U06DQA", f"U{2 + k}", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
          X + 45 * (k % 3), Y + 40 * (k // 3), nets)

# ---------------- uscita -----------------------------------------------------------------------------------
libp = f"{PRJ}/A133.kicad_sym"
lib = open(libp).read()
lib = re.sub(r'\s*\(symbol "A133"\s.*$', "", lib, flags=re.S) if '(symbol "A133"' in lib else lib
if '(symbol "A133"' not in lib:
    lib = lib.rstrip()[:-1] + " " + A133_SYM.replace('(symbol "A133:A133"', '(symbol "A133"', 1) + ")"
open(libp, "w").write(lib)
libsyms = "(lib_symbols " + " ".join(SYMS.values()) + ")"
open(f"{PRJ}/cpu.kicad_sch", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{SHEET_UUID}") (paper "A1") '
    + libsyms + " " + " ".join(items) + " (embedded_fonts no))")

# foglio radice: il blocco "CPU Unit" vuoto viene sostituito dal foglio CPU
root_path = f"{PRJ}/{PROJ}.kicad_sch"
root = open(root_path).read().replace('(paper "A3")', '(paper "A1")', 1)
i = root.find('(sheet\n\t\t(at 38.1 38.1)')
if i >= 0:
    d = 0
    for j in range(i, len(root)):
        if root[j] == "(":
            d += 1
        elif root[j] == ")":
            d -= 1
            if d == 0:
                break
    root = root[:i] + root[j + 1:]
sx, sy, w = 330.2, 38.1, 50.8
h = 5.08 + 2.54 * len(hier)
pinlist, extra = [], []
for k, n in enumerate(hier):
    py = sy + 2.54 * (k + 1)
    pinlist.append(f'(pin "{n}" passive (at {sx:.2f} {py:.2f} 180) (uuid "{U()}") {F.format(j="left")})')
    extra.append(f'(wire (pts (xy {sx:.2f} {py:.2f}) (xy {sx - 5.08:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
    extra.append(f'(label "{n}" (at {sx - 5.08:.2f} {py:.2f} 180) {F.format(j="right bottom")} (uuid "{U()}"))')
sheet = (f'(sheet (at {sx} {sy}) (size {w} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
         f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{SHEET_UUID}") '
         f'(property "Sheetname" "CPU" (at {sx} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
         f'(property "Sheetfile" "cpu.kicad_sch" (at {sx} {sy + h + 0.58:.2f} 0) {F.format(j="left top")}) '
         + " ".join(pinlist) + f' (instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "2")))))')
k = root.rfind("\t(sheet_instances")
root = root[:k] + "\t" + sheet + "\n\t" + "\n\t".join(extra) + "\n" + root[k:]
open(root_path, "w").write(root)
print("porte:", len(hier))
