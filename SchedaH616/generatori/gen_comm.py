"""Fogli Rete (RTL8211F), Radio (AP6256), GNSS (NEO-M9N) della scheda RK3568."""
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, box_symbol
from kilib import LIBNAME

PRJ = sys.argv[1]
LIBF = f"{PRJ}/{LIBNAME}.kicad_sym"
GP = ("RGMII_", "PHY_", "WL_", "BT_", "CLK32K", "GNSS_", "SPI2_")
RAILS = ["VCC_3V3"]
C0603 = "Capacitor_SMD:C_0603_1608Metric"

# =============================== RETE: RTL8211F-CG ==============================================
s = Sheet("Rete", "rete.kicad_sch", 500, 7, RAILS, GP)
RTL = [("20", "TXC", "L"), ("18", "TXD0", "L"), ("17", "TXD1", "L"), ("16", "TXD2", "L"), ("15", "TXD3", "L"), ("19", "TXCTL", "L"),
       ("27", "RXC/PHYAD1", "L"), ("25", "RXD0/RXDLY", "L"), ("24", "RXD1/TXDLY", "L"), ("23", "RXD2/PLLOFF", "L"), ("22", "RXD3/PHYAD0", "L"),
       ("26", "RXCTL/PHYAD2", "L"), ("13", "MDC", "L"), ("14", "MDIO", "L"), ("31", "INTB/PMEB", "L"), ("12", "PHYRSTB", "L"),
       ("35", "CLKOUT", "L"), ("36", "XTAL_IN", "L"), ("37", "XTAL_OUT", "L"),
       ("1", "MDIP0", "R"), ("2", "MDIN0", "R"), ("4", "MDIP1", "R"), ("5", "MDIN1", "R"), ("6", "MDIP2", "R"), ("7", "MDIN2", "R"),
       ("9", "MDIP3", "R"), ("10", "MDIN3", "R"), ("32", "LED0/CFG_EXT", "R"), ("33", "LED1/CFG_LDO0", "R"), ("34", "LED2/CFG_LDO1", "R"),
       ("39", "RSET", "R"), ("30", "REG_OUT", "R"), ("21", "DVDD10", "R"), ("3", "AVDD10", "R"), ("8", "AVDD10", "R"), ("38", "AVDD10", "R"),
       ("11", "AVDD33", "R"), ("40", "AVDD33", "R"), ("29", "DVDD33", "R"), ("28", "DVDD_RG", "R"), ("41", "EPAD_GND", "R")]
# simbolo di progetto (pin dal datasheet, tutti visibili): quello MIKILAB ha AVDD10/AVDD33 come pin di alimentazione nascosti,
# che KiCad collega a net globali con quel nome (VCC_3V3 diventerebbe "AVDD33"). Footprint dalla libreria MIKILAB.
RTL_ID = f"{LIBNAME}:RTL8211F-CG"
s.add_sym(RTL_ID, box_symbol(LIBNAME, "RTL8211F-CG", RTL, "Realtek RTL8211F-CG, PHY Gigabit RGMII, QFN-40 5x5"))
_, _, RTL_FP = __import__("kilib").mik("RTL8211F-CG")
for k in ["Device:R", "Device:C", "Device:L", "Device:Crystal_GND24"]:
    s.std(k)
RJ_ID, RJ_FP = s.mik("HR911130C")
s.text("RETE: PHY Realtek RTL8211F-CG (datasheet rev. 1.7) su GMAC0 RGMII dell'RK3568 (VCCIO4 3.3 V), alimentato da VCC_3V3 (SWOUT1). Serie 5xx. Net RGMII_*/PHY_* globali verso il foglio CPU.", 20, 15)
s.text("Strap (4.7k): PHYAD = 001, PLLOFF = 0, TXDLY = 1 e RXDLY = 1 (rgmii-id, ritardi nel PHY), CFG_EXT = 1 con CFG_LDO = 00: pad RGMII alimentati da fuori a 3.3 V.", 20, 20)
s.place(RTL_ID, "U1", "RTL8211F-CG", RTL_FP, 110, 120, {
    "20": "PHY_TXC_P", "18": "PHY_TXD0_P", "17": "PHY_TXD1_P", "16": "PHY_TXD2_P", "15": "PHY_TXD3_P", "19": "PHY_TXCTL_P",
    "27": "PHY_RXC_P", "25": "PHY_RXD0_P", "24": "PHY_RXD1_P", "23": "PHY_RXD2_P", "22": "PHY_RXD3_P", "26": "PHY_RXCTL_P",
    "13": "PHY_MDC", "14": "PHY_MDIO", "31": "PHY_INT_N", "12": "PHY_RST_N", "35": "PHY_CLKOUT", "36": "PHY_XI", "37": "PHY_XO",
    "1": "MDI0_P", "2": "MDI0_N", "4": "MDI1_P", "5": "MDI1_N", "6": "MDI2_P", "7": "MDI2_N", "9": "MDI3_P", "10": "MDI3_N",
    "32": "PHY_LED0", "33": "PHY_LED1", "34": "PHY_LED2", "39": "PHY_RSET", "30": "PHY_REG_OUT", "21": "PHY_VDD10",
    "3": "PHY_VDD10", "8": "PHY_VDD10", "38": "PHY_VDD10", "11": "VCC_3V3", "40": "VCC_3V3", "29": "VCC_3V3", "28": "VCC_3V3",
    "41": "GND_D"}, mpn="RTL8211F-CG")
X, Y = 200, 50
s.text("22R serie vicino al SoC su TXC, TXD0-3, TXCTL (MAC -> PHY) e vicino al PHY su RXC, RXD0-3, RXCTL (Hardware Design Guide RK3568, tabella 2-42).", X - 5, Y - 10)
for i, (a, b) in enumerate([("RGMII_TXCK", "PHY_TXC_P"), ("RGMII_TXD0", "PHY_TXD0_P"), ("RGMII_TXD1", "PHY_TXD1_P"),
                            ("RGMII_TXD2", "PHY_TXD2_P"), ("RGMII_TXD3", "PHY_TXD3_P"), ("RGMII_TXCTL", "PHY_TXCTL_P")]):
    s.R(f"R{1 + i}", "22R", X + 10 * i, Y, a, b)
for i, (a, b) in enumerate([("PHY_RXC_P", "RGMII_RXCK"), ("PHY_RXD0_P", "RGMII_RXD0"), ("PHY_RXD1_P", "RGMII_RXD1"),
                            ("PHY_RXD2_P", "RGMII_RXD2"), ("PHY_RXD3_P", "RGMII_RXD3"), ("PHY_RXCTL_P", "RGMII_RXCTL")]):
    s.R(f"R{24 + i}", "22R", X + 65 + 10 * i, Y, a, b)
X, Y = 200, 90
s.text("Strap su RXD/RXC/RXCTL e LED (4.7k). LED1/LED2 attivi alti verso i LED dell'RJ45 (510R); LED0 solo strap CFG_EXT.", X - 5, Y - 10)
straps = [("R7", "VCC_3V3", "PHY_RXD3_P"), ("R8", "PHY_RXC_P", "GND_D"), ("R9", "PHY_RXCTL_P", "GND_D"), ("R10", "PHY_RXD2_P", "GND_D"),
          ("R11", "VCC_3V3", "PHY_RXD1_P"), ("R12", "VCC_3V3", "PHY_RXD0_P"), ("R13", "VCC_3V3", "PHY_LED0"),
          ("R14", "PHY_LED1", "GND_D"), ("R15", "PHY_LED2", "GND_D")]
for i, (ref, a, b) in enumerate(straps):
    s.R(ref, "4.7k", X + 10 * i, Y, a, b)
X, Y = 200, 130
s.text("MDIO 1.5k a 3.3 V, INT 4.7k, PHYRSTB 10k + 100 nF (il PHY esce dal reset da solo, Linux puo' ripeterlo da GPIO3_D7). RSET 2.49k 1%.", X - 5, Y - 10)
s.R("R16", "1.5k", X, Y, "VCC_3V3", "PHY_MDIO")
s.R("R17", "4.7k", X + 10, Y, "VCC_3V3", "PHY_INT_N")
s.R("R18", "10k", X + 20, Y, "VCC_3V3", "PHY_RST_N")
s.C("C1", "100nF", X + 30, Y, "PHY_RST_N", "GND_D")
s.R("R19", "2.49k 1%", X + 40, Y, "PHY_RSET", "GND_D")
s.R("R20", "0R", X + 55, Y, "PHY_CLKOUT", "RGMII_CLKIN", dnp=True)
s.text("R520 DNP: CLKOUT 125 MHz verso GMAC0_MCLKINOUT (GPIO2_C2), non usato di default. PHY_RST_N su GPIO3_D7, PHY_INT_N su GPIO4_A0.", X - 5, Y + 14)
X, Y = 200, 175
s.text("Quarzo 25 MHz +-50 ppm (requisito datasheet) con 2x 15 pF. Switching regulator 1.0 V: REG_OUT -> 2.2 uH -> AVDD10/DVDD10.", X - 5, Y - 12)
s.place("Device:Crystal_GND24", "Y1", "25MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", X + 10, Y, {"1": "PHY_XI", "3": "PHY_XO", "2": "GND_D", "4": "GND_D"})
s.C("C2", "15pF", X, Y + 10, "PHY_XI", "GND_D")
s.C("C3", "15pF", X + 20, Y + 10, "PHY_XO", "GND_D")
s.place("Device:L", "L1", "2.2uH", "Inductor_SMD:L_0805_2012Metric", X + 40, Y, {"1": "PHY_REG_OUT", "2": "PHY_VDD10"})
for i, (ref, val, net, fp) in enumerate([("C4", "22uF", "PHY_VDD10", C0603), ("C5", "0.1uF", "PHY_VDD10", None), ("C6", "0.1uF", "PHY_VDD10", None),
                                         ("C7", "0.1uF", "PHY_VDD10", None), ("C8", "0.1uF", "PHY_VDD10", None), ("C9", "10uF", "VCC_3V3", C0603),
                                         ("C10", "0.1uF", "VCC_3V3", None), ("C11", "0.1uF", "VCC_3V3", None), ("C12", "0.1uF", "VCC_3V3", None),
                                         ("C13", "0.1uF", "VCC_3V3", None)]):
    if fp:
        s.C(ref, val, X + 55 + 10 * i, Y, net, "GND_D", fp)
    else:
        s.C(ref, val, X + 55 + 10 * i, Y, net, "GND_D")
X, Y = 120, 220
s.text("RJ45 HanRun HR911130C (100/1000Base-T, magnetici e LED integrati). Prese centrali lato PHY (P1, comuni) a GND con 100 nF. P10 = rete Bob Smith verso lo schermo.", 20, Y - 30)
s.place(RJ_ID, "J1", "HR911130C", RJ_FP, X, Y, {
    "P2": "MDI0_P", "P3": "MDI0_N", "P4": "MDI1_P", "P7": "MDI1_N", "P5": "MDI2_P", "P6": "MDI2_N", "P8": "MDI3_P", "P9": "MDI3_N",
    "P1": "ETH_CT", "11": "ETH_LED1_A", "12": "GND_D", "14": "ETH_LED2_A", "13": "GND_D", "P10": "GND_D",
    "SHIELD0": "GND_D", "SHIELD1": "GND_D"}, mpn="HR911130C")
s.C("C14", "100nF", X + 40, Y + 15, "ETH_CT", "GND_D")
s.R("R22", "510R", X + 85, Y + 15, "PHY_LED1", "ETH_LED1_A")
s.R("R23", "510R", X + 95, Y + 15, "PHY_LED2", "ETH_LED2_A")
s.text("LED verde = LED1 del PHY (100M), giallo = LED2 (1000M), entrambi attivi alti.", 20, Y + 30)
X, Y = 290, 220
EE_ID, EE_FP = s.mik("25AA02E48T-I_OT")
s.text("EEPROM MAC 25AA02E48 (EUI-48 per la MAC del GMAC0) su SPI2 locale (prima dei 33R verso il bus MAIN), CS1 hardware di SPI2 (GPIO2_D4) con 10k a VCC_3V3.", X - 50, Y - 25)
s.text("Pinout SOT-23-6 dal datasheet Microchip DS20002123G, tabella 4-1: 1 SCK, 2 VSS, 3 SI, 4 SO, 5 CS, 6 VCC.", X - 50, Y - 20)
s.place(EE_ID, "U2", "25AA02E48T-I/OT", EE_FP, X, Y,
        {"6": "VCC_3V3", "5": "PHY_EE_CS_N", "1": "SPI2_CLK", "3": "SPI2_MOSI", "4": "SPI2_MISO", "2": "GND_D"}, mpn="25AA02E48T-I/OT")
s.R("R21", "10k", X + 30, Y, "VCC_3V3", "PHY_EE_CS_N")
s.C("C15", "0.1uF", X + 40, Y, "VCC_3V3", "GND_D")
rete_ports = s.write(PRJ, 508.0, 38.1, LIBF)

# =============================== RADIO: AMPAK AP6256 ============================================
r = Sheet("Radio", "radio.kicad_sch", 600, 8, RAILS, GP)
AP_ID, _ = r.mik("AP6212", "AP6256", footprint=False)   # simbolo MIKILAB (libreria AP6212); footprint LGA-47 di progetto
for k in ["Device:R", "Device:C", "Connector:Conn_Coaxial"]:
    r.std(k)
r.text("RADIO: AMPAK AP6256 (Wi-Fi 5 + BT 5.0) su SDMMC2_M0 (SDIO, VCCIO6), HCI su UART8_M0 con RTS/CTS (VCCIO4), REG_ON e wake su GPIO. Serie 6xx. Net WL_*/BT_*/CLK32K globali.", 20, 15)
r.text("VDDIO = VCC_3V3 3.3 V (= VCCIO6/VCCIO4), SDIO 2.0 fino a 50 MHz. VBAT e VIN_LDO da VCC_3V3. LPO 32.768 kHz da CLK32K dell'RK809-5 (quarzo Y201).", 20, 20)
r.place(AP_ID, "U1", "AP6256", "Scheda:AP6256_LGA-47_12x12mm", 110, 110, {
    "1": "GND_D", "3": "GND_D", "20": "GND_D", "31": "GND_D", "33": "GND_D", "36": "GND_D", "2": "WL_ANT",
    "6": "BT_WAKE", "7": "BT_HOST_WAKE", "9": "VCC_3V3", "23": "VCC_3V3", "21": "WL_LDO_OUT", "22": "VCC_3V3",
    "12": "WL_REG_ON", "13": "WL_HOST_WAKE", "14": "WL_SDIO_D2", "15": "WL_SDIO_D3", "16": "WL_SDIO_CMD", "17": "WL_SDIO_CLK",
    "18": "WL_SDIO_D0", "19": "WL_SDIO_D1", "24": "CLK32K", "29": "GND_D", "34": "BT_REG_ON",
    "41": "BT_UART_CTS", "42": "BT_UART_RX", "43": "BT_UART_TX", "44": "BT_UART_RTS"}, mpn="AP6256")
r.text("UART incrociata: TXD del modulo -> BT_UART_RX (UART8_RX, GPIO2_C6), RXD <- BT_UART_TX (GPIO2_C5), RTS_N -> BT_UART_CTS (GPIO2_B2), CTS_N <- BT_UART_RTS (GPIO2_B1).", 20, 175)
r.text("PCM (25-28) non collegati: niente audio Bluetooth. XTAL_IN/OUT liberi (quarzo interno). GPIO e TP liberi.", 20, 180)
X, Y = 200, 60
r.text("REG_ON con 100k a GND (radio spenta finche Linux non la accende: GPIO3_D4/D5). Pull-up 10k su CMD e DAT0-3 a VCC_3V3. CLK 22R serie vicino al SoC.", X - 5, Y - 10)
r.R("R1", "100k", X, Y, "WL_REG_ON", "GND_D")
r.R("R2", "100k", X + 10, Y, "BT_REG_ON", "GND_D")
r.R("R9", "22R", X + 80, Y, "WL_SDIO_CLK_S", "WL_SDIO_CLK")
for i, net in enumerate(["WL_SDIO_CMD", "WL_SDIO_D0", "WL_SDIO_D1", "WL_SDIO_D2", "WL_SDIO_D3"]):
    r.R(f"R{3 + i}", "10k", X + 25 + 10 * i, Y, "VCC_3V3", net)
X, Y = 200, 100
r.text("Disaccoppiamento: VBAT 10uF + 0.1uF (picchi 1 A in trasmissione), VIN_LDO_OUT 4.7uF, VDDIO 1uF + 0.1uF.", X - 5, Y - 10)
for i, (ref, val, net, fp) in enumerate([("C1", "10uF", "VCC_3V3", C0603), ("C2", "0.1uF", "VCC_3V3", None), ("C3", "4.7uF", "WL_LDO_OUT", C0603),
                                         ("C4", "1uF", "VCC_3V3", None), ("C5", "0.1uF", "VCC_3V3", None)]):
    if fp:
        r.C(ref, val, X + 10 * i, Y, net, "GND_D", fp)
    else:
        r.C(ref, val, X + 10 * i, Y, net, "GND_D")
X, Y = 200, 140
r.text("Antenna: linea 50 ohm verso U.FL con rete pi di adattamento (0R + 2x DNP) da tarare.", X - 5, Y - 12)
r.C("C6", "DNP", X, Y, "WL_ANT", "GND_D", dnp=True)
r.R("R8", "0R", X + 10, Y, "WL_ANT", "WL_ANT_C")
r.C("C7", "DNP", X + 20, Y, "WL_ANT_C", "GND_D", dnp=True)
r.place("Connector:Conn_Coaxial", "J1", "U.FL", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", X + 40, Y, {"1": "WL_ANT_C", "2": "GND_D"})
radio_ports = r.write(PRJ, 584.2, 38.1, LIBF)

# =============================== GNSS: u-blox NEO-M9N ==========================================
g = Sheet("GNSS", "gnss.kicad_sch", 700, 9, RAILS, GP)
g.std("RF_GPS:NEO-M9N")
for k in ["Device:R", "Device:C", "Device:L", "Device:D_Schottky", "Device:D_TVS", "Device:Battery_Cell", "Connector:Conn_Coaxial", "Connector:TestPoint",
          "74xGxx:74LVC1G17", "Connector_Generic:Conn_01x03"]:
    g.std(k)
g.text("GNSS: u-blox NEO-M9N-00B (formato NEO, stesso footprint del NEO-F10T). Pin dal datasheet UBX-19014285 R08, tabella 9 (= simbolo NEO-M9N di KiCad). Serie 7xx.", 20, 15)
g.text("UART3_M1: TXD del modulo -> GNSS_UART_RX (GPIO3_C0), RXD <- GNSS_UART_TX (GPIO3_B7). TIMEPULSE -> 33R -> GNSS_PPS (GPIO3_A5). EXTINT (pin 4, PIO7, time mark TIM-TM2) letto anche da GPIO3_A6 (solo ingresso).", 20, 20)
g.place("RF_GPS:NEO-M9N", "U1", "NEO-M9N-00B", "RF_GPS:ublox_NEO", 100, 110, {
    "1": "GNSS_SAFEBOOT_N", "2": "NC", "3": "GNSS_TP", "4": "GNSS_EXTINT", "5": "NC", "6": "NC", "7": "GND_D", "8": "GNSS_RESET_N",
    "9": "GNSS_VCC_RF", "10": "GND_D", "11": "GNSS_RF_IN", "12": "GND_D", "13": "GND_D", "14": "NC", "15": "NC", "16": "NC",
    "17": "NC", "18": "NC", "19": "NC", "20": "GNSS_UART_RX", "21": "GNSS_UART_TX", "22": "GNSS_V_BCKP", "23": "VCC_3V3",
    "24": "GND_D"}, mpn="NEO-M9N-00B")
g.place("Connector:TestPoint", "TP1", "SAFEBOOT_N", "TestPoint:TestPoint_Pad_D1.0mm", 60, 70, {"1": "GNSS_SAFEBOOT_N"})
g.place("Connector:TestPoint", "TP2", "RESET_N", "TestPoint:TestPoint_Pad_D1.0mm", 75, 70, {"1": "GNSS_RESET_N"})
g.text("D_SEL (pin 2) aperto = UART + I2C. V_USB (pin 7) a GND: USB non usata (da confermare sull'integration manual). LNA_EN e riservati liberi.", 20, 25)
X, Y = 200, 55
g.text("Alimentazione: VCC 10uF + 0.1uF. Backup V_BCKP da OR di diodi: VCC_3V3 (BAT54) e pila CR1220 (BAT54), nessuna ricarica della pila.", X - 5, Y - 10)
g.C("C1", "10uF", X, Y, "VCC_3V3", "GND_D", C0603)
g.C("C2", "0.1uF", X + 10, Y, "VCC_3V3", "GND_D")
g.place("Device:D_Schottky", "D1", "BAT54", "Diode_SMD:D_SOD-323", X + 25, Y, {"2": "VCC_3V3", "1": "GNSS_V_BCKP"})
g.place("Device:D_Schottky", "D4", "BAT54", "Diode_SMD:D_SOD-323", X + 25, Y + 15, {"2": "GNSS_BAT", "1": "GNSS_V_BCKP"})
g.place("Device:Battery_Cell", "BT1", "CR1220", "Scheda:BatteryHolder_MYOUNG_BS-12-B3AA003_CR1220", X + 45, Y + 15, {"1": "GNSS_BAT", "2": "GND_D"}, mpn="BS-12-B3AA003")
g.C("C3", "1uF", X + 55, Y, "GNSS_V_BCKP", "GND_D")
X, Y = 200, 100
g.text("Antenna attiva su SMA: VCC_RF -> 10R (limita il corto) -> 27 nH -> RF_IN. ESD a bassa capacita sul centrale. Linea 50 ohm corta.", X - 5, Y - 12)
g.R("R2", "10R", X, Y, "GNSS_VCC_RF", "GNSS_ANT_BIAS")
g.place("Device:L", "L1", "27nH", "Inductor_SMD:L_0402_1005Metric", X + 12, Y, {"1": "GNSS_ANT_BIAS", "2": "GNSS_RF_IN"})
g.C("C4", "10nF", X + 24, Y, "GNSS_ANT_BIAS", "GND_D")
g.place("Device:D_TVS", "D2", "ESD5V3U1U-02LS", "Diode_SMD:D_0402_1005Metric", X + 40, Y, {"1": "GNSS_RF_IN", "2": "GND_D"})
g.place("Connector:Conn_Coaxial", "J1", "SMA antenna", "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", X + 60, Y, {"1": "GNSS_RF_IN", "2": "GND_D"})
X, Y = 200, 150
g.text("Uscita PPS: TIMEPULSE -> 33R -> GNSS_PPS (SoC) e -> buffer 74LVC1G17 -> 33R -> SMA 'PPS OUT' e header J703. Nessun pull sul TIMEPULSE.", X - 5, Y - 14)
g.R("R3", "33R", X, Y, "GNSS_TP", "GNSS_PPS")
g.place("74xGxx:74LVC1G17", "U2", "74LVC1G17", "Package_TO_SOT_SMD:SOT-353_SC-70-5", X + 25, Y, {"2": "GNSS_TP", "4": "GNSS_PPS_BUF", "5": "VCC_3V3", "3": "GND_D", "1": "NC"})
g.C("C5", "0.1uF", X + 40, Y, "VCC_3V3", "GND_D")
g.R("R4", "33R", X + 50, Y, "GNSS_PPS_BUF", "GNSS_PPS_OUT")
g.place("Connector:Conn_Coaxial", "J2", "SMA PPS OUT", "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", X + 70, Y, {"1": "GNSS_PPS_OUT", "2": "GND_D"})
X, Y = 200, 200
g.text("Time mark: SMA 'STROBE IN' (o J703 pin 2) -> ESD -> 100R -> 74LVC1G17 (ingressi tolleranti 5 V) -> EXTINT. 100k a GND in ingresso.", X - 5, Y - 14)
g.place("Connector:Conn_Coaxial", "J3", "SMA STROBE IN", "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", X, Y, {"1": "GNSS_STROBE_IN", "2": "GND_D"})
g.place("Device:D_TVS", "D3", "ESD9B5.0ST5G", "Diode_SMD:D_SOD-923", X + 15, Y, {"1": "GNSS_STROBE_IN", "2": "GND_D"})
g.R("R5", "100R", X + 25, Y, "GNSS_STROBE_IN", "GNSS_STROBE_R")
g.R("R6", "100k", X + 35, Y, "GNSS_STROBE_R", "GND_D")
g.place("74xGxx:74LVC1G17", "U3", "74LVC1G17", "Package_TO_SOT_SMD:SOT-353_SC-70-5", X + 55, Y, {"2": "GNSS_STROBE_R", "4": "GNSS_EXTINT", "5": "VCC_3V3", "3": "GND_D", "1": "NC"})
g.C("C6", "0.1uF", X + 70, Y, "VCC_3V3", "GND_D")
g.place("Connector_Generic:Conn_01x03", "J4", "PPS/STROBE", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", X + 95, Y,
        {"1": "GNSS_PPS_OUT", "2": "GNSS_STROBE_IN", "3": "GND_D"})
gnss_ports = g.write(PRJ, 660.4, 38.1, LIBF)
print("porte:", rete_ports, radio_ports, gnss_ports)
