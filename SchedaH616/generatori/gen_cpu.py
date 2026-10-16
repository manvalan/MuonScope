"""Foglio KiCad 10 'CPU' della scheda RK3568: SoC in 9 unità, 24 MHz, reset e Recovery, console UART2, disaccoppiamento,
interfaccia bus MIKILAB (BUS_POWER su SPI3_M1, MAIN su SPI2_M1). Serie 3xx."""
import json
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, multi_symbol, place_multi, G
from kilib import LIBNAME

PRJ = sys.argv[1]

# ---------------- ball map: Rockchip RK3568 PinOut V1.1 (foglio "PinOut List"), 636 sfere ----------------------------------
# Controllata sfera per sfera con la tabella 2-1 del datasheet RK3568 V1.2 (636/636 uguali).
BALLS = json.load(open(os.path.join(SC, "rk3568_balls.json")))
assert len(BALLS) == 636

# ---------------- assegnazione dei GPIO: gpio -> (net, funzione) -----------------------------------------------------------
GPIO = {
    # PMUIO1 (3.3 V, VCC3V3_PMU)
    "GPIO0_A1": ("TSADC_SHUT", "TSADC_SHUT_M0"), "GPIO0_A2": ("PMIC_SLEEP_H", "PMIC_SLEEP"), "GPIO0_A3": ("PMIC_INT_L", "GPIO"),
    "GPIO0_A4": ("SD_DET", "SDMMC0_DET"), "GPIO0_A5": ("VBUS_SRC_EN", "GPIO"), "GPIO0_A6": ("USB1_VBUS_EN", "GPIO"),
    "GPIO0_A7": ("FLASH_VOL_SEL", "FLASH_VOL_SEL"),
    # PMUIO2 (3.3 V, VCC3V3_PMU)
    "GPIO0_B0": ("CLK32K", "CLK32K_IN"), "GPIO0_B1": ("I2C0_SCL", "I2C0_SCL"), "GPIO0_B2": ("I2C0_SDA", "I2C0_SDA"),
    "GPIO0_B3": ("I2C1_SCL", "I2C1_SCL"), "GPIO0_B4": ("I2C1_SDA", "I2C1_SDA"), "GPIO0_B5": ("PD_INT_N", "GPIO"),
    "GPIO0_B6": ("USB1_OC_N", "GPIO"), "GPIO0_B7": ("PWR_SRC_ST", "GPIO"), "GPIO0_C0": ("WL_HOST_WAKE", "GPIO"),
    "GPIO0_C1": ("BT_HOST_WAKE", "GPIO"), "GPIO0_D0": ("UART2_RX", "UART2_RX_M0"), "GPIO0_D1": ("UART2_TX", "UART2_TX_M0"),
    # VCCIO2 (1.8 V, VCC1V8_EMMC): eMMC 8 bit
    "GPIO1_B4": ("EMMC_D0", "EMMC_D0"), "GPIO1_B5": ("EMMC_D1", "EMMC_D1"), "GPIO1_B6": ("EMMC_D2", "EMMC_D2"),
    "GPIO1_B7": ("EMMC_D3", "EMMC_D3"), "GPIO1_C0": ("EMMC_D4", "EMMC_D4"), "GPIO1_C1": ("EMMC_D5", "EMMC_D5"),
    "GPIO1_C2": ("EMMC_D6", "EMMC_D6"), "GPIO1_C3": ("EMMC_D7", "EMMC_D7"), "GPIO1_C4": ("EMMC_CMD", "EMMC_CMD"),
    "GPIO1_C5": ("EMMC_CLK_S", "EMMC_CLKOUT"), "GPIO1_C6": ("EMMC_DS", "EMMC_DATA_STROBE"), "GPIO1_C7": ("EMMC_RST", "EMMC_RSTn"),
    # VCCIO3 (VCCIO_SD 3.3 V): microSD su SDMMC0
    "GPIO1_D5": ("SD_D0", "SDMMC0_D0"), "GPIO1_D6": ("SD_D1", "SDMMC0_D1"), "GPIO1_D7": ("SD_D2", "SDMMC0_D2"),
    "GPIO2_A0": ("SD_D3", "SDMMC0_D3"), "GPIO2_A1": ("SD_CMD", "SDMMC0_CMD"), "GPIO2_A2": ("SD_CLK_S", "SDMMC0_CLK"),
    # VCCIO4 (3.3 V): GMAC0 RGMII verso RTL8211F, UART8_M0 (HCI dell'AP6256)
    "GPIO2_A3": ("RGMII_RXD2", "GMAC0_RXD2"), "GPIO2_A4": ("RGMII_RXD3", "GMAC0_RXD3"), "GPIO2_A5": ("RGMII_RXCK", "GMAC0_RXCLK"),
    "GPIO2_A6": ("RGMII_TXD2", "GMAC0_TXD2"), "GPIO2_A7": ("RGMII_TXD3", "GMAC0_TXD3"), "GPIO2_B0": ("RGMII_TXCK", "GMAC0_TXCLK"),
    "GPIO2_B3": ("RGMII_TXD0", "GMAC0_TXD0"), "GPIO2_B4": ("RGMII_TXD1", "GMAC0_TXD1"), "GPIO2_B5": ("RGMII_TXCTL", "GMAC0_TXEN"),
    "GPIO2_B6": ("RGMII_RXD0", "GMAC0_RXD0"), "GPIO2_B7": ("RGMII_RXD1", "GMAC0_RXD1"), "GPIO2_C0": ("RGMII_RXCTL", "GMAC0_RXDV_CRS"),
    "GPIO2_C2": ("RGMII_CLKIN", "GMAC0_MCLKINOUT"), "GPIO2_C3": ("PHY_MDC", "GMAC0_MDC"), "GPIO2_C4": ("PHY_MDIO", "GMAC0_MDIO"),
    "GPIO2_C5": ("BT_UART_TX", "UART8_TX_M0"), "GPIO2_C6": ("BT_UART_RX", "UART8_RX_M0"),
    "GPIO2_B1": ("BT_UART_RTS", "UART8_RTSn_M0"), "GPIO2_B2": ("BT_UART_CTS", "UART8_CTSn_M0"),
    # VCCIO5 (3.3 V): MAIN su SPI2_M1 + EEPROM MAC su CS1, I2C del bus su I2C3_M1, GNSS su UART3_M1, ADDR/PREFIX, EINT
    "GPIO2_D0": ("SOC_ADDR_0", "GPIO"), "GPIO2_D1": ("SOC_ADDR_1", "GPIO"), "GPIO2_D2": ("SOC_ADDR_2", "GPIO"),
    "GPIO2_D3": ("SOC_PREFIX_0", "GPIO"), "GPIO2_D4": ("PHY_EE_CS_N", "SPI2_CS1_M1"), "GPIO2_D5": ("MAIN_SPI_CS_MASTER", "SPI2_CS0_M1"),
    "GPIO2_D6": ("SPI2_MOSI", "SPI2_MOSI_M1"), "GPIO2_D7": ("SPI2_MISO", "SPI2_MISO_M1"), "GPIO3_A0": ("SPI2_CLK", "SPI2_CLK_M1"),
    "GPIO3_A1": ("SOC_PREFIX_1", "GPIO"), "GPIO3_A2": ("SOC_PREFIX_2", "GPIO"), "GPIO3_A3": ("MAIN_SPI_ALERT_N", "GPIO"),
    "GPIO3_A4": ("MAIN_HIT_N", "GPIO"), "GPIO3_A5": ("GNSS_PPS", "GPIO"), "GPIO3_A6": ("GNSS_EXTINT", "GPIO"),
    "GPIO3_A7": ("VREF_ENABLE", "GPIO"), "GPIO3_B0": ("VBIAS_ENABLE", "GPIO"), "GPIO3_B1": ("DAC61402_FAULT", "GPIO"),
    "GPIO3_B5": ("MAIN_I2C_SCL", "I2C3_SCL_M1"), "GPIO3_B6": ("MAIN_I2C_SDA", "I2C3_SDA_M1"),
    "GPIO3_B7": ("GNSS_UART_TX", "UART3_TX_M1"), "GPIO3_C0": ("GNSS_UART_RX", "UART3_RX_M1"),
    # VCCIO6 (3.3 V): AP6256 su SDMMC2_M0, controlli radio e PHY
    "GPIO3_C6": ("WL_SDIO_D0", "SDMMC2_D0_M0"), "GPIO3_C7": ("WL_SDIO_D1", "SDMMC2_D1_M0"), "GPIO3_D0": ("WL_SDIO_D2", "SDMMC2_D2_M0"),
    "GPIO3_D1": ("WL_SDIO_D3", "SDMMC2_D3_M0"), "GPIO3_D2": ("WL_SDIO_CMD", "SDMMC2_CMD_M0"), "GPIO3_D3": ("WL_SDIO_CLK_S", "SDMMC2_CLK_M0"),
    "GPIO3_D4": ("WL_REG_ON", "GPIO"), "GPIO3_D5": ("BT_REG_ON", "GPIO"), "GPIO3_D6": ("BT_WAKE", "GPIO"),
    "GPIO3_D7": ("PHY_RST_N", "GPIO"), "GPIO4_A0": ("PHY_INT_N", "GPIO"),
    # VCCIO7 (3.3 V): BUS_POWER su SPI3_M1 (CS0 INA239A, CS1 INA239B, DAC su cs-gpios: SPI3 ha solo due CS)
    "GPIO4_C2": ("SPI3_CLK", "SPI3_CLK_M1"), "GPIO4_C3": ("SPI3_MOSI", "SPI3_MOSI_M1"), "GPIO4_C5": ("SPI3_MISO", "SPI3_MISO_M1"),
    "GPIO4_C6": ("PWR_SPI_INA239A_CS", "SPI3_CS0_M1"), "GPIO4_D1": ("PWR_SPI_INA239B_CS", "SPI3_CS1_M1"),
    "GPIO4_C4": ("PWR_SPI_DAC_CS", "GPIO"),
}

UNUSED_AVDD = ("USB2_AVDD", "MULTI_PHY_AVDD", "PCIE30_AVDD", "MIPI_CSI_RX_AVDD", "MIPI_DSI_TX0/LVDS_TX0_AVDD", "MIPI_DSI_TX1_AVDD",
               "HDMI_TX_AVDD", "EDP_TX_AVDD")


def gpio_of(name):
    m = re.search(r"GPIO\d_[A-D]\d", name)
    return m.group(0) if m else None


def ddr_net(name):
    """Segnali DDR: canale A del PHY (16 bit) verso la DDR4 x16, nomi dal lato DDR4 come nel reference Rockchip."""
    parts = name.split("/")
    d4 = next((p for p in parts if p.startswith("DDR4_")), None)
    if name.startswith("DDR_ECC") or d4 is None:
        return "NC"
    if d4.endswith("_B"):
        return "NC"                       # canale B del PHY non usato (DDR4 a 16 bit)
    sg = d4[5:]
    if sg.endswith("_A"):
        sg = sg[:-2]
    if sg in ("CS1n", "ODT1", "BG1"):
        return "NC"                       # singolo rank SDP x16: niente CS1/ODT1, BG1 non esiste sulla x16 SDP
    sg = {"A14_WEn": "A14_WE_N", "A15_CASn": "A15_CAS_N", "A16_RASn": "A16_RAS_N", "ACTn": "ACT_N", "CS0n": "CS_N", "ODT0": "ODT",
          "RESETn": "RESET_N", "CLKP": "CK_P", "CLKN": "CK_N", "DQSL_P": "DQSL_P", "DQSL_N": "DQSL_N"}.get(sg, sg)
    return "DDR_" + sg


def net(num, nm):
    name = BALLS[num][0]
    g = gpio_of(name)
    if g:
        return GPIO.get(g, ("NC",))[0]
    base = re.sub(r"_\d+$", "", name)
    if base in ("VSS", "AVSS", "DDR_AVSS", "PMUPLL_AVSS", "SYSPLL_AVSS", "TVSS"):
        return "GND_D"
    if base.startswith(UNUSED_AVDD):
        return "GND_D"                    # PHY non usati: alimentazioni a VSS (Rockchip, istruzioni per i pin non usati)
    if base.startswith(("DDR_", "DDR4_")) and base not in ("DDR_RZQ", "DDR_VREFOUT"):
        return ddr_net(name)
    return {
        "VDD_CPU": "VDD_CPU", "VDD_CPU_COM": "VDD_CPU_COM", "VDD_LOGIC": "VDD_LOGIC", "VDD_GPU": "VDD_GPU", "VDD_NPU": "VDD_NPU",
        "DDRPHY_VDDQ": "VCC_DDR", "DDRPHY_VDDQL": "VCC_DDR", "DDR_RZQ": "SOC_DDR_RZQ", "DDR_VREFOUT": "DDR_VREFOUT",
        "PMUPLL_AVDD_0V9": "VDDA0V9_PMU", "PMU_VDD_LOGIC_0V9": "VDDA0V9_PMU", "PMUPLL_AVDD_1V8": "VCCA1V8_PMU",
        "SYSPLL_AVDD_0V9": "VDDA_0V9", "SYSPLL_AVDD_1V8": "VCCA_1V8", "PMUIO1": "VCC3V3_PMU", "PMUIO2": "VCC3V3_PMU",
        "VCCIO2": "VCC1V8_EMMC", "VCCIO3": "VCCIO_SD", "VCCIO4": "VCC_3V3", "VCCIO5": "VCC_3V3", "VCCIO6": "VCC_3V3", "VCCIO7": "VCC_3V3",
        "SARADC_AVDD_1V8": "VCCA_1V8", "OTP_VCC18": "VCCA_1V8",
        "USB3_AVDD_0V9": "USB_AVDD_0V9", "USB3_AVDD_1V8": "USB_AVDD_1V8", "USB3_AVDD_3V3": "VCC_3V3",
        "XIN24M": "XIN24M", "XOUT24M": "XOUT24M", "nPOR_u": "RESETn", "SARADC_VIN0": "SARADC_VIN0",
        "USB3_OTG0_DP": "USB_OTG0_DP_S", "USB3_OTG0_DM": "USB_OTG0_DM_S", "USB3_OTG0_VBUSDET": "OTG_VBUSDET",
        "USB3_HOST1_DP": "USB1_DP", "USB3_HOST1_DM": "USB1_DM",
    }.get(base, "NC")   # VCCIO1 (dominio non usato), SARADC_VIN1-7, PHY video/PCIe/SATA, ECC, OTG0_ID: NC


# ---------------- simbolo in 9 unità --------------------------------------------------------------------------------------
def pin_name(name):
    g = gpio_of(name)
    if g:
        f = GPIO.get(g, (None, None))[1]
        return f"{f}/{g}" if f and f != "GPIO" else g
    parts = name.split("/")
    if parts[0].startswith(("DDR_DQ", "DDR_DM")):
        return f"{parts[0]}/{parts[1]}"
    if parts[0].startswith("DDR4_"):
        return f"{parts[-1]}/{parts[0]}"
    return parts[0]


def unit_of(name, part):
    base = re.sub(r"_\d+$", "", name)
    if part == "VSS":
        return 3
    if part == "AVSS" or base in ("DDR_AVSS", "PMUPLL_AVSS", "SYSPLL_AVSS", "TVSS"):
        return 4
    if re.match(r"(VDD|VCC|DDRPHY_VDD|PMUIO|PMUPLL_AVDD|SYSPLL_AVDD|PMU_VDD|OTP_VCC|SARADC_AVDD)", name) or "AVDD" in name:
        return 2
    if part == "DDR":
        return 1
    if part.startswith(("OSC", "SARADC")):
        return 5
    if part.startswith(("VCCIO1", "VCCIO2", "VCCIO3", "VCCIO4")):
        return 6
    if part.startswith(("VCCIO5", "VCCIO6", "VCCIO7")):
        return 7
    if part.startswith(("USB", "PCIe")):
        return 8
    return 9


def natkey(t):
    s_ = t[1]
    g = re.search(r"GPIO(\d)_([A-D])(\d)", s_)
    if g:
        return ("GPIO", int(g.group(1)), g.group(2), int(g.group(3)), "")
    m = re.match(r"([A-Za-z_/]+?)(\d+)(.*)$", s_)
    return (m.group(1), 0, "", int(m.group(2)), m.group(3)) if m else (s_, 0, "", 0, "")


units = [[] for _ in range(9)]
for ball, (name, dom, part) in BALLS.items():
    units[unit_of(name, part) - 1].append((ball, pin_name(name)))
units = [sorted(u, key=natkey) for u in units]
TITLES = ["DDR PHY", "ALIMENTAZIONI", "VSS", "AVSS", "PMUIO1-2 / OSC / SARADC", "VCCIO1-4 (EMMC, SDMMC0, GMAC0)",
          "VCCIO5-7", "USB / PCIe / SATA", "VIDEO (non usato)"]
RK_SYM, RK_PINS = multi_symbol(LIBNAME, "RK3568", units, "Rockchip RK3568, FCBGA636L 19x19 mm passo 0.65 mm", w=30.48, titles=TITLES)

RAILS = ["5V_SYS", "VCC3V3_SYS", "VCC_3V3", "VCC3V3_PMU", "VCCIO_SD", "VCC1V8_EMMC", "VCCA_1V8", "VCCA1V8_PMU", "VDDA_0V9",
         "VDDA0V9_PMU", "VDD_CPU", "VDD_CPU_COM", "VDD_LOGIC", "VDD_GPU", "VDD_NPU", "VCC_DDR",
         "USB0_DP", "USB0_DM", "I2C1_SDA", "I2C1_SCL", "PD_INT_N", "VBUS_SRC_EN", "PWR_SRC_ST", "OTG_VBUSDET"]
BUSNETS = ["PWR_SPI_SCLK", "PWR_SPI_MOSI", "PWR_SPI_MISO", "PWR_SPI_INA239A_CS", "PWR_SPI_INA239B_CS", "PWR_SPI_DAC_CS",
           "VREF_ENABLE", "VBIAS_ENABLE", "DAC61402_FAULT", "MAIN_SPI_SCLK", "MAIN_SPI_MOSI", "MAIN_SPI_MISO", "MAIN_I2C_SDA",
           "MAIN_I2C_SCL", "MAIN_SPI_CS_MASTER", "MAIN_SPI_ADDR_0", "MAIN_SPI_ADDR_1", "MAIN_SPI_ADDR_2", "MAIN_SPI_PREFIX_0",
           "MAIN_SPI_PREFIX_1", "MAIN_SPI_PREFIX_2", "MAIN_SPI_ALERT_N", "MAIN_HIT_N"]
GP = ("DDR_", "EMMC_", "SD_", "WL_", "BT_", "RGMII_", "PHY_", "GNSS_", "USB1_", "SPI2_", "I2C0_", "CLK32K", "PMIC_", "RESETn")
s = Sheet("CPU", "cpu.kicad_sch", 300, 2, RAILS + BUSNETS, GP, paper="A0")
s.add_sym(f"{LIBNAME}:RK3568", RK_SYM)
for k in ["Device:R", "Device:C", "Device:Crystal_GND24", "Device:FerriteBead", "Switch:SW_Push", "Connector_Generic:Conn_01x03",
          "Power_Protection:TPD4E05U06DQA"]:
    s.std(k)
C0201, C0402, C0603 = "Capacitor_SMD:C_0201_0603Metric", "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric"

# posizioni delle unità: colonne, unità impilate dall'alto (x centro, y del bordo alto)
COLS = {1: (90, 60), 8: (90, 290), 3: (250, 60), 4: (410, 60), 2: (410, 200), 5: (570, 60), 6: (570, 170), 7: (730, 60), 9: (730, 220)}
pos = {}
for uu, (x, ytop) in COLS.items():
    half = (len(RK_PINS[uu]) + 1) // 2
    pos[uu] = (x, ytop + G(2.54 * (half + 1) / 2) + 8)
place_multi(s, f"{LIBNAME}:RK3568", "U1", "RK3568", f"{LIBNAME}:Rockchip_FCBGA-636_19x19mm_P0.65mm", RK_PINS, net, pos,
            mpn="RK3568", lcsc="C2938930")
s.text("CPU: Rockchip RK3568 (FCBGA636L 19x19 mm, passo 0.65 mm, LCSC C2938930). Ball map: Rockchip RK3568 PinOut V1.1, verificata sulla tabella 2-1 del datasheet V1.2 (636/636). Serie 3xx.", 20, 20)
s.text("Domini IO: PMUIO1/PMUIO2 = VCC3V3_PMU (3.3 V), VCCIO2 = VCC1V8_EMMC (1.8 V, FLASH_VOL_SEL alto), VCCIO3 = VCCIO_SD, VCCIO4-7 = VCC_3V3 (3.3 V), VCCIO1 non usato (flottante, come da Rockchip).", 20, 26)
s.text("PHY non usati (USB2 HOST2/3, MULTI_PHY, PCIe3, MIPI CSI/DSI, HDMI, eDP): alimentazioni a VSS e segnali flottanti, secondo 'RK3568 Processing instructions for unused pins'. VDD_NPU su BUCK4 dell'RK809-5.", 20, 32)
s.text("DDR4 a 16 bit sul canale A del PHY (DQ0-15_A, nomi DDR4_DQL/DQU_A del pinout Rockchip); canale B, ECC, CS1n, ODT1, BG1 non usati. Mappa completa in docs/pinmap-rk3568.md.", 20, 38)

X0, Y0 = 850, 60


def grid(items, x0, y0, cols=12, dx=10, dy=20):
    for i, (ref, val, a, b, fp) in enumerate(items):
        x, y = x0 + dx * (i % cols), y0 + dy * (i // cols)
        if ref.startswith("C"):
            s.C(ref, val, x, y, a, b, fp)
        else:
            s.R(ref, val, x, y, a, b)


# ---------------- clock 24 MHz, reset, Recovery, console ----------------------------------------------------------------------
X, Y = X0, Y0
s.text("24 MHz (Hardware Design Guide RK3568 fig. 2-1 / reference AIoT): 22R serie su XOUT24M, 1M tra XIN e XOUT, 18 pF per lato (da adattare al CL del quarzo, tolleranza 20 ppm).", X - 10, Y - 12)
s.place("Device:Crystal_GND24", "Y1", "24MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", X + 15, Y + 4,
        {"1": "XTAL24_X1", "3": "XIN24M", "2": "GND_D", "4": "GND_D"}, mpn="X322524MOB4SI")
s.C("C1", "18pF/50V", X, Y + 14, "XTAL24_X1", "GND_D")
s.C("C2", "18pF/50V", X + 30, Y + 14, "XIN24M", "GND_D")
s.R("R1", "22R", X + 40, Y + 14, "XOUT24M", "XTAL24_X1")
s.R("R2", "1M", X + 50, Y + 14, "XIN24M", "XOUT24M")

X, Y = X0, Y0 + 45
s.text("nPOR (AH27, dominio PMUIO1): rete RESETn con 100 nF vicino alla sfera, RESETB dell'RK809-5 (open drain, 10k a VCC3V3_PMU sul foglio PMIC), TSADC_SHUT_M0 con 0R e tasto RESET.", X - 10, Y - 12)
s.text("Il tasto RESET tira giu' RESETn: l'RK809-5 rifa' la sequenza di accensione (Hardware Design Guide, par. Reset). FLASH_VOL_SEL (GPIO0_A7) 10k a VCC3V3_PMU: VCCIO2 a 1.8 V.", X - 10, Y - 7)
s.C("C3", "100nF", X, Y + 5, "RESETn", "GND_D")
s.R("R3", "0R", X + 10, Y + 5, "TSADC_SHUT", "RESETn")
s.place("Switch:SW_Push", "SW1", "RESET", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X + 25, Y + 5, {"1": "RESETn", "2": "GND_D"}, mpn="TS-1088-AR02016")
s.R("R4", "10k", X + 50, Y + 5, "VCC3V3_PMU", "FLASH_VOL_SEL")
s.text("Recovery (ex FEL): SARADC_VIN0 (B27) con 10k a VCCA_1V8 (obbligatorio, Rockchip) e tasto a GND: tenuto premuto all'accensione il loader entra in modalita' Recovery/rockusb.", X - 10, Y + 22)
s.R("R5", "10k", X, Y + 32, "VCCA_1V8", "SARADC_VIN0")
s.C("C4", "1nF", X + 10, Y + 32, "SARADC_VIN0", "GND_D")
s.place("Switch:SW_Push", "SW2", "RECOVERY", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", X + 25, Y + 32, {"1": "SARADC_VIN0", "2": "GND_D"}, mpn="TS-1088-AR02016")
s.place("Connector_Generic:Conn_01x03", "J1", "UART2 debug", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", X + 60, Y + 32,
        {"1": "UART2_TX", "2": "UART2_RX", "3": "GND_D"})
s.text("J301 console UART2_M0 (GPIO0_D1 TX, GPIO0_D0 RX, PMUIO2 3.3 V): 1 = TX del SoC, 2 = RX del SoC, 3 = GND. 1500000 baud (default Rockchip).", X - 10, Y + 47)

# ---------------- pull-up e I2C dei domini PMU ---------------------------------------------------------------------------------
X, Y = X0, Y0 + 115
s.text("I2C0 (GPIO0_B1/B2, PMUIO2): RK809-5 0x20 e TCS4525 0x1C, pull-up 2.2k a VCC3V3_PMU. I2C1 (GPIO0_B3/B4): FUSB302B 0x22, 2.2k a VCC3V3_PMU.", X - 10, Y - 12)
s.text("Open drain verso i GPIO PMU: PMIC_INT_L, PD_INT_N (FUSB302B), USB1_OC_N (TPS2553), PWR_SRC_ST (TPS2121) con 10k a VCC3V3_PMU. SD_DET 10k sul foglio Memorie.", X - 10, Y - 7)
grid([("R6", "2.2k", "VCC3V3_PMU", "I2C0_SCL", None), ("R7", "2.2k", "VCC3V3_PMU", "I2C0_SDA", None),
      ("R8", "2.2k", "VCC3V3_PMU", "I2C1_SCL", None), ("R9", "2.2k", "VCC3V3_PMU", "I2C1_SDA", None),
      ("R10", "10k", "VCC3V3_PMU", "PMIC_INT_L", None), ("R11", "10k", "VCC3V3_PMU", "PD_INT_N", None),
      ("R12", "10k", "VCC3V3_PMU", "USB1_OC_N", None), ("R13", "10k", "VCC3V3_PMU", "PWR_SRC_ST", None)], X, Y + 5)

# ---------------- USB: serie 2.2R (Hardware Design Guide, tabella USB) e alimentazioni del PHY USB2 ---------------------------
X, Y = X0, Y0 + 150
s.text("USB3_OTG0_DP/DM (porta di flash rkdeveloptool, USB-C di alimentazione) con 2.2R in serie. USB3_HOST1_DP/DM verso la USB-C host (2.2R sul foglio USB host).", X - 10, Y - 12)
s.text("USB3_AVDD_0V9/1V8 da VDDA_0V9/VCCA_1V8 con ferrite 120R@100MHz (reference AIoT), USB3_AVDD_3V3 da VCC_3V3. USB2_AVDD (HOST2/3 non usati) a VSS.", X - 10, Y - 7)
s.R("R14", "2.2R", X, Y + 5, "USB0_DP", "USB_OTG0_DP_S")
s.R("R15", "2.2R", X + 10, Y + 5, "USB0_DM", "USB_OTG0_DM_S")
s.place("Device:FerriteBead", "FB1", "120R@100MHz", "Inductor_SMD:L_0603_1608Metric", X + 30, Y + 5, {"1": "VDDA_0V9", "2": "USB_AVDD_0V9"}, mpn="BLM18PG121SN1D")
s.place("Device:FerriteBead", "FB2", "120R@100MHz", "Inductor_SMD:L_0603_1608Metric", X + 45, Y + 5, {"1": "VCCA_1V8", "2": "USB_AVDD_1V8"}, mpn="BLM18PG121SN1D")
grid([("C5", "4.7uF", "USB_AVDD_0V9", "GND_D", C0402), ("C6", "100nF", "USB_AVDD_0V9", "GND_D", C0201),
      ("C7", "4.7uF", "USB_AVDD_1V8", "GND_D", C0402), ("C8", "100nF", "USB_AVDD_1V8", "GND_D", C0201),
      ("C9", "100nF", "VCC_3V3", "GND_D", C0201)], X + 60, Y + 5)

# ---------------- disaccoppiamento (reference RK3568 AIoT V1.1, pagine 10-15) --------------------------------------------------
X, Y = X0, Y0 + 200
s.text("Disaccoppiamento secondo il reference Rockchip RK3568 AIoT V1.1: 100 nF/1 nF in 0201 e 4.7 uF/1 uF in 0402 sotto il package, 22 uF/10 uF 0603 vicino.", X - 10, Y - 12)
s.text("VDD_CPU >= 135 uF in totale con le uscite del TCS4525 (Hardware Design Guide 2.2.2.4), un 22 uF DNP di riserva. VDD_LOGIC/GPU/NPU >= 90 uF con le uscite dell'RK809-5.", X - 10, Y - 7)
DEC = [  # (ref, valore, net, footprint)
    ("C10", "100nF", "VDD_CPU", C0201), ("C11", "4.7uF", "VDD_CPU", C0402), ("C12", "22uF", "VDD_CPU", C0603), ("C13", "22uF", "VDD_CPU", C0603),
    ("C14", "22uF", "VDD_CPU", C0603),
    ("C16", "100nF", "VDD_LOGIC", C0201), ("C17", "4.7uF", "VDD_LOGIC", C0402), ("C18", "1uF", "VDD_LOGIC", C0402), ("C19", "1uF", "VDD_LOGIC", C0402),
    ("C20", "22uF", "VDD_LOGIC", C0603), ("C21", "22uF", "VDD_LOGIC", C0603), ("C22", "10uF", "VDD_LOGIC", C0603),
    ("C23", "100nF", "VDD_GPU", C0201), ("C24", "4.7uF", "VDD_GPU", C0402), ("C25", "22uF", "VDD_GPU", C0603), ("C26", "22uF", "VDD_GPU", C0603),
    ("C27", "10uF", "VDD_GPU", C0603),
    ("C28", "100nF", "VDD_NPU", C0201), ("C29", "22uF", "VDD_NPU", C0603), ("C30", "22uF", "VDD_NPU", C0603), ("C31", "10uF", "VDD_NPU", C0603),
    ("C32", "100nF", "VCC_DDR", C0201), ("C33", "100nF", "VCC_DDR", C0201), ("C34", "4.7uF", "VCC_DDR", C0402), ("C35", "4.7uF", "VCC_DDR", C0402),
    ("C36", "10uF", "VCC_DDR", C0603),
    ("C37", "1uF", "VDDA0V9_PMU", C0402), ("C38", "100nF", "VDDA0V9_PMU", C0201), ("C39", "1uF", "VDDA0V9_PMU", C0402), ("C40", "100nF", "VDDA0V9_PMU", C0201),
    ("C41", "1uF", "VCCA1V8_PMU", C0402), ("C42", "100nF", "VCCA1V8_PMU", C0201), ("C43", "1uF", "VDDA_0V9", C0402), ("C44", "100nF", "VDDA_0V9", C0201),
    ("C45", "1uF", "VCCA_1V8", C0402), ("C46", "100nF", "VCCA_1V8", C0201), ("C47", "100nF", "VCCA_1V8", C0201), ("C48", "100nF", "VCCA_1V8", C0201),
    ("C49", "100nF", "VCC3V3_PMU", C0201), ("C50", "100nF", "VCC3V3_PMU", C0201), ("C51", "100nF", "VCC1V8_EMMC", C0201), ("C52", "1uF", "VCC1V8_EMMC", C0402),
    ("C53", "100nF", "VCCIO_SD", C0201), ("C54", "100nF", "VCC_3V3", C0201), ("C55", "100nF", "VCC_3V3", C0201), ("C56", "100nF", "VCC_3V3", C0201),
    ("C57", "100nF", "VCC_3V3", C0201), ("C58", "100nF", "VCC_3V3", C0201), ("C59", "100nF", "VCC_3V3", C0201), ("C60", "100nF", "VCC_3V3", C0201),
    ("C61", "1uF", "VCC_3V3", C0402),
]
grid([(r, v, n, "GND_D", fp) for r, v, n, fp in DEC], X, Y + 5, cols=14)
s.C("C15", "22uF", X + 140, Y + 5, "VDD_CPU", "GND_D", C0603, dnp=True)
s.text("C315 DNP: 22 uF di riserva su VDD_CPU (Hardware Design Guide). VCCIO4 ha due 100 nF (RGMII), VCCIO5/VCCIO6 due sfere ciascuno.", X - 10, Y + 75)
s.text("DDR_RZQ (H7): 120R 1% a GND per DDR4 (Hardware Design Guide 2.1.7.2; l'appunto diceva 240R, che vale per lo ZQ della DDR4). DDR_VREFOUT (P8): 1 nF a VCC_DDR e 1 nF a GND vicino al SoC.", X - 10, Y + 80)
s.R("R16", "120R 1%", X, Y + 90, "SOC_DDR_RZQ", "GND_D")
s.C("C62", "1nF", X + 10, Y + 90, "DDR_VREFOUT", "VCC_DDR", C0201)
s.C("C63", "1nF", X + 20, Y + 90, "DDR_VREFOUT", "GND_D", C0201)

# ---------------- interfaccia bus MIKILAB --------------------------------------------------------------------------------------
X, Y = X0, Y0 + 330
s.text("BUS_POWER su SPI3_M1 (VCCIO7): CLK GPIO4_C2, MOSI GPIO4_C3, MISO GPIO4_C5, CS0 INA239A GPIO4_C6, CS1 INA239B GPIO4_D1; CS del DAC su GPIO4_C4 con cs-gpios (SPI3 ha solo due CS hardware).", X - 10, Y - 17)
s.text("MAIN su SPI2_M1 (VCCIO5): CLK GPIO3_A0, MOSI GPIO2_D6, MISO GPIO2_D7, CS0 = CS_MASTER GPIO2_D5; CS1 (GPIO2_D4) = EEPROM MAC locale. 33R serie su CLK/MOSI/MISO verso i connettori.", X - 10, Y - 12)
s.text("I2C del bus su I2C3_M1 (GPIO3_B5/B6). ADDR/PREFIX con 100R serie. Linee lente (VREF/VBIAS_ENABLE, FAULT, ALERT#, HIT#, PPS, EXTINT) su GPIO diretti: niente TCA6416A.", X - 10, Y - 7)
for i, (ref, a, b) in enumerate([("R17", "SPI3_CLK", "PWR_SPI_SCLK"), ("R18", "SPI3_MOSI", "PWR_SPI_MOSI"), ("R19", "SPI3_MISO", "PWR_SPI_MISO"),
                                 ("R20", "SPI2_CLK", "MAIN_SPI_SCLK"), ("R21", "SPI2_MOSI", "MAIN_SPI_MOSI"), ("R22", "SPI2_MISO", "MAIN_SPI_MISO")]):
    s.R(ref, "33R", X + 12 * i, Y + 5, a, b)
for i in range(3):
    s.R(f"R{23 + i}", "100R", X + 75 + 12 * i, Y + 5, f"SOC_ADDR_{i}", f"MAIN_SPI_ADDR_{i}")
    s.R(f"R{26 + i}", "100R", X + 111 + 12 * i, Y + 5, f"SOC_PREFIX_{i}", f"MAIN_SPI_PREFIX_{i}")
X, Y = X0, Y0 + 365
s.text("Livelli di riposo: CS e CS_MASTER alti (10k), VREF_ENABLE basso (10k a GND), VBIAS_ENABLE basso (100k a GND), ALERT# e HIT# 4.7k, I2C del bus 2.2k, FAULT 10k (tutti a VCC_3V3).", X - 10, Y - 12)
pu = [("R29", "10k", "VCC_3V3", "PWR_SPI_INA239A_CS"), ("R30", "10k", "VCC_3V3", "PWR_SPI_INA239B_CS"), ("R31", "10k", "VCC_3V3", "PWR_SPI_DAC_CS"),
      ("R32", "10k", "VCC_3V3", "MAIN_SPI_CS_MASTER"), ("R33", "10k", "VREF_ENABLE", "GND_D"), ("R34", "100k", "VBIAS_ENABLE", "GND_D"),
      ("R35", "10k", "VCC_3V3", "DAC61402_FAULT"), ("R36", "4.7k", "VCC_3V3", "MAIN_SPI_ALERT_N"), ("R37", "4.7k", "VCC_3V3", "MAIN_HIT_N"),
      ("R38", "2.2k", "VCC_3V3", "MAIN_I2C_SCL"), ("R39", "2.2k", "VCC_3V3", "MAIN_I2C_SDA")]
grid([(r, v, a, b, None) for r, v, a, b in pu], X, Y, cols=11)
X, Y = X0, Y0 + 400
s.text("ESD bassa capacita TPD4E05U06DQA (0.5 pF, 5.5 V) sulle linee logiche di J1/J2, vicino ai connettori. Nessuna protezione su V_BIAS e riferimenti.", X - 10, Y - 15)
for k in range(6):
    g = BUSNETS[4 * k: 4 * k + 4]
    nets = {"1": g[0], "2": g[1], "4": g[2] if len(g) > 2 else "NC", "5": g[3] if len(g) > 3 else "NC", "3": "GND_D", "8": "GND_D"}
    s.place("Power_Protection:TPD4E05U06DQA", f"U{2 + k}", "TPD4E05U06DQA", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", X + 45 * (k % 3), Y + 40 * (k // 3), nets)
print("porte:", s.write(PRJ, 330.2, 38.1, f"{PRJ}/{LIBNAME}.kicad_sym"))
