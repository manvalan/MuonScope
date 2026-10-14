"""Generatore del progetto KiCad 10 "PianoTest" (piano di test MuonScope sul bus MIKILAB REV5.0)."""
import sys, os, uuid, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kisheet
from kisheet import Sheet, box_symbol, U, F
from kilib import extract

PRJ = sys.argv[1]
os.makedirs(PRJ, exist_ok=True)
ROOT = str(uuid.uuid4())
kisheet.PROJ = "PianoTest"
kisheet.ROOT_UUID = ROOT
LIB = "PianoTest"

GLOBALS = {
    "GND", "+3V3", "+5V", "2V5_REF", "1V25_REF", "VHV_36V", "VHV_36V_2",
    "SCLK_L", "MOSI_L", "MISO_L", "CS_ADC", "CS_DAC", "CS_INA", "CS_MCP",
    "I2C_SDA", "I2C_SCL", "PL_FAULT", "HIT", "HIT_LATCH", "VTH", "CS_Y3", "CS_Y4", "TRIG_INPULSE", "MCP_INTA",
    "CSA_IN", "CSA_OUT", "VBIAS_SH",
}

R0603, C0603 = "Resistor_SMD:R_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric"
R0805, C1206 = "Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_1206_3216Metric"
TP_FP = "TestPoint:TestPoint_Pad_D1.0mm"

# ------------------------------------------------------------------ simboli a riquadro
SYMS = {}


def box(name, pinlist, desc, w=15.24):
    SYMS[name] = box_symbol(LIB, name, pinlist, desc, w)
    return f"{LIB}:{name}"


def L(*a):
    return [(n, nm, "L") for n, nm in a]


def Rr(*a):
    return [(n, nm, "R") for n, nm in a]


OPA4172 = box("OPA4172", L(("3", "+INA"), ("2", "-INA"), ("5", "+INB"), ("6", "-INB"), ("10", "+INC"), ("9", "-INC"), ("12", "+IND"), ("13", "-IND"), ("4", "V+"), ("11", "V-"))
              + Rr(("1", "OUTA"), ("7", "OUTB"), ("8", "OUTC"), ("14", "OUTD")), "OPA4172 quad, SOIC-14 (pinout quad standard)")
ADS8326 = box("ADS8326", L(("1", "REF"), ("2", "+IN"), ("3", "-IN"), ("8", "VDD"), ("4", "GND")) + Rr(("5", "~{CS}"), ("6", "DOUT"), ("7", "DCLOCK")), "ADS8326 16 bit SAR, VSSOP-8")
TMP117 = box("TMP117", L(("5", "V+"), ("2", "GND"), ("4", "ADD0"), ("7", "EP")) + Rr(("1", "SCL"), ("6", "SDA"), ("3", "ALERT")), "TMP117 I2C, WSON-6")
MCP = box("MCP23S17_QFN", L(("5", "VDD"), ("6", "VSS"), ("29", "EP"), ("7", "~{CS}"), ("8", "SCK"), ("9", "SI"), ("10", "SO"), ("11", "A0"), ("12", "A1"), ("13", "A2"), ("14", "~{RESET}"), ("15", "INTB"), ("16", "INTA"))
          + Rr(*[(str(17 + i), f"GPA{i}") for i in range(8)], *[(str(25 + i), f"GPB{i}") for i in range(4)], *[(str(1 + i), f"GPB{4 + i}") for i in range(4)]), "MCP23S17 QFN-28 (ML)")
TMUX = box("TMUX1112", L(("11", "VDD"), ("3", "GND"), ("15", "SEL1"), ("14", "SEL2"), ("7", "SEL3"), ("6", "SEL4"), ("2", "NC"), ("10", "NC"))
           + Rr(("1", "S1"), ("16", "D1"), ("12", "S2"), ("13", "D2"), ("9", "S3"), ("8", "D3"), ("4", "S4"), ("5", "D4")), "TMUX1112 4xSPST, chiuso con SEL=1, UQFN-16")
BGSA = box("BGSA142", L(("4", "VDD"), ("3", "GND"), ("8", "GND"), ("7", "CTL0"), ("5", "CTL1"), ("6", "CTL2"))
           + Rr(("11", "RFC1"), ("12", "RFC2"), ("1", "RF1"), ("2", "RF2"), ("10", "RF3"), ("9", "RF4")), "BGSA142GN12 commutatore RF, TSNP-12")
LTC6993 = box("LTC6993-2", L(("5", "V+"), ("2", "GND"), ("1", "TRIG"), ("3", "SET"), ("4", "DIV")) + Rr(("6", "OUT"),), "LTC6993-2 monostabile, SOT-23-6")
AD5245 = box("AD5245", L(("2", "VDD"), ("3", "GND"), ("4", "SCL"), ("5", "SDA"), ("6", "AD0")) + Rr(("8", "A"), ("1", "W"), ("7", "B")), "AD5245 potenziometro digitale I2C, SOT-23-8")
PD = box("VBPW34S", L(("A", "A"),) + Rr(("K", "K"),), "Fotodiodo PIN Vishay VBPW34S", w=5.08)
LED = box("VSMY2940G", L(("A", "A"),) + Rr(("C", "C"),), "LED IR Vishay VSMY2940G", w=5.08)
DAC = box("DAC61402", L(("28", "AVDD"), ("30", "DVDD"), ("15", "IOVDD"), ("26", "REFIO"), ("25", "REFGND"), ("27", "AVSS"), ("29", "AGND"), ("14", "GND"), ("33", "EP"),
                         ("12", "~{SYNC}"), ("10", "SCLK"), ("11", "SDIN"), ("9", "SDO"), ("13", "~{LDAC}"), ("16", "~{CLR}"), ("32", "~{RST}"), ("31", "~{FAULT}"))
          + Rr(("8", "OUTA"), ("6", "SENSEPA"), ("5", "SENSENA"), ("7", "CCOMPA"), ("17", "OUTB"), ("19", "SENSEPB"), ("20", "SENSENB"), ("18", "CCOMPB"),
               *[(str(n), "NC") for n in (1, 2, 3, 4, 21, 22, 23, 24)]), "DAC61402 2 canali 12 bit alta tensione, VQFN-32", w=17.78)
INA239 = box("INA239", L(("6", "VS"), ("7", "GND"), ("1", "CS"), ("5", "SCLK"), ("2", "MOSI"), ("4", "MISO"), ("3", "ALERT")) + Rr(("10", "IN+"), ("9", "IN-"), ("8", "VBUS")), "INA239 monitor 85 V SPI, VSSOP-10")
HC283 = box("74HC283", L(("5", "A1"), ("3", "A2"), ("14", "A3"), ("12", "A4"), ("6", "B1"), ("2", "B2"), ("15", "B3"), ("11", "B4"), ("7", "CIN"), ("16", "VCC"), ("8", "GND"))
            + Rr(("4", "S1"), ("1", "S2"), ("13", "S3"), ("10", "S4"), ("9", "COUT")), "74HC283 sommatore 4 bit")
HC85 = box("74HC85", L(("10", "A0"), ("12", "A1"), ("13", "A2"), ("15", "A3"), ("9", "B0"), ("11", "B1"), ("14", "B2"), ("1", "B3"), ("2", "IA<B"), ("3", "IA=B"), ("4", "IA>B"), ("16", "VCC"), ("8", "GND"))
           + Rr(("5", "QA>B"), ("6", "QA=B"), ("7", "QA<B")), "74HC85 comparatore 4 bit")
HC138 = box("74HC138", L(("1", "A0"), ("2", "A1"), ("3", "A2"), ("4", "~{E1}"), ("5", "~{E2}"), ("6", "E3"), ("16", "VCC"), ("8", "GND"))
            + Rr(("15", "~{Y0}"), ("14", "~{Y1}"), ("13", "~{Y2}"), ("12", "~{Y3}"), ("11", "~{Y4}"), ("10", "~{Y5}"), ("9", "~{Y6}"), ("7", "~{Y7}")), "74HC138 decoder 3-8")
G17 = box("74LVC2G17", L(("1", "1A"), ("3", "2A"), ("5", "VCC"), ("2", "GND")) + Rr(("6", "1Y"), ("4", "2Y")), "SN74LVC2G17 doppio buffer Schmitt, SOT-23-6", w=10.16)
G125 = box("74LVC1G125", L(("2", "A"), ("1", "~{OE}"), ("5", "VCC"), ("3", "GND")) + Rr(("4", "Y"),), "SN74LVC1G125 buffer tri-state, SOT-23-5", w=10.16)
G332 = box("74LVC1G332", L(("1", "A"), ("3", "B"), ("6", "C"), ("5", "VCC"), ("2", "GND")) + Rr(("4", "Y"),), "SN74LVC1G332 OR a 3 ingressi, SOT-23-6", w=10.16)
G07 = box("74LVC1G07", L(("2", "A"), ("1", "NC"), ("5", "VCC"), ("3", "GND")) + Rr(("4", "Y"),), "SN74LVC1G07 buffer open-drain, SOT-23-5", w=10.16)
EEP = box("25AA02E48", L(("1", "~{CS}"), ("6", "SCK"), ("5", "SI"), ("3", "~{WP}"), ("7", "~{HOLD}"), ("8", "VCC"), ("4", "VSS")) + Rr(("2", "SO"),), "EEPROM SPI 2 kbit con EUI-48, SOIC-8", w=10.16)


BSS138 = box("BSS138", L(("1", "G"),) + Rr(("3", "D"), ("2", "S")), "MOSFET N BSS138, SOT-23", w=5.08)


TLV3501 = box("TLV3501", L(("3", "+IN"), ("1", "-IN"), ("6", "SHDN"), ("4", "V+"), ("2", "V-")) + Rr(("5", "OUT"),), "TLV3501 comparatore 4.5 ns, SOT-23-6", w=10.16)
G74 = box("74LVC1G74", L(("2", "D"), ("1", "CLK"), ("7", "~{PRE}"), ("6", "~{CLR}"), ("8", "VCC"), ("4", "GND")) + Rr(("5", "Q"), ("3", "~{Q}")), "SN74LVC1G74 flip-flop D, VSSOP-8 (DCU)", w=10.16)
G04 = box("74LVC1G04", L(("2", "A"), ("1", "NC"), ("5", "VCC"), ("3", "GND")) + Rr(("4", "Y"),), "SN74LVC1G04 invertitore, SOT-23-5", w=10.16)
OPA2365 = box("OPA2365", L(("3", "+INA"), ("2", "-INA"), ("5", "+INB"), ("6", "-INB"), ("8", "V+"), ("4", "V-")) + Rr(("1", "OUTA"), ("7", "OUTB")), "OPA2365 doppio 50 MHz RRIO, SOIC-8")
BAT54S = box("BAT54S", L(("3", "K1/A2"),) + Rr(("1", "A1"), ("2", "K2")), "BAT54S doppio Schottky in serie, SOT-23", w=5.08)


G123 = box("74LVC1G123", L(("1", "~{A}"), ("2", "B"), ("3", "~{CLR}"), ("8", "VCC"), ("4", "GND")) + Rr(("5", "Q"), ("7", "Rext/Cext"), ("6", "Cext")), "SN74LVC1G123 monostabile, VSSOP-8 (DCU)", w=10.16)
G06 = box("74LVC1G06", L(("2", "A"), ("1", "NC"), ("5", "VCC"), ("3", "GND")) + Rr(("4", "Y"),), "SN74LVC1G06 invertitore open-drain, SOT-23-5", w=10.16)


class PS(Sheet):
    """Foglio con piazzamento automatico in colonne ed etichette globali per le net condivise."""

    def __init__(self, *a, **k):
        super().__init__(*a, hier=(), paper="A2", **k)
        self.cx, self.cy, self.colw = 25.4, 30.48, 0
        self.std("Device:R")
        self.std("Device:C")

    def label(self, net, x, y, ang):
        if net in GLOBALS:
            j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
            self.items.append(f'(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) {F.format(j=j)} (uuid "{U()}"))')
        else:
            super().label(net, x, y, ang)

    def need(self, lib_id):
        if lib_id in self.syms:
            return
        if lib_id.startswith(LIB + ":"):
            self.add_sym(lib_id, SYMS[lib_id.split(":")[1]])
        else:
            self.std(lib_id)

    def put(self, lib_id, ref, val, fp, nets, **k):
        """Piazza in colonna: altezza ricavata dai pin."""
        self.need(lib_id)
        pp = self.pins[lib_id]
        ys = [p[3] for p in pp]
        xs = [p[2] for p in pp]
        h = max(ys) - min(ys) + (40 if lib_id.startswith("Device:") else 20)
        w = max(xs) - min(xs) + 50
        if self.cy + h > 400:
            self.cx += self.colw + 10
            self.cy, self.colw = 30.48, 0
        x = self.cx + w / 2
        y = self.cy + max(ys) + (20 if lib_id.startswith("Device:") else 10)
        self.place(lib_id, ref, val, fp, x, y, nets, **k)
        self.cy += h
        self.colw = max(self.colw, w)

    def R(self, ref, val, a, b, fp=R0603, **k):
        self.put("Device:R", ref, val, fp, {"1": a, "2": b}, **k)

    def C(self, ref, val, a, b, fp=C0603, **k):
        self.put("Device:C", ref, val, fp, {"1": a, "2": b}, **k)

    def newcol(self):
        self.cx += self.colw + 10
        self.cy, self.colw = 30.48, 0

    def place(self, lib_id, ref, val, fp, x, y, nets, dnp=False, mpn=None):
        # riferimenti già completi: niente serie
        s, self.series = self.series, 0
        super().place(lib_id, ref, val, fp, x, y, nets, dnp=dnp, mpn=mpn)
        self.series = s


sheets = []

# =============================================================== 1. Rivelatore e formatura
BF862 = box("BF862", L(("3", "G"),) + Rr(("1", "D"), ("2", "S")), "JFET N BF862, SOT-23 (1 D, 2 S, 3 G)", w=5.08)
s = PS("Rivelatore", "rivelatore.kicad_sch", 0, "2")
s.text("PREAMPLIFICATORE DI CARICA (OPA4172 A, Cf 1 pF + Rf 100M di default) -> shaper CR-RC tau 1 us: C invertente x10 (CR), D non invertente x5 (RC) = x50. Base 1V25 bufferizzata da B.", 25.4, 15.24)
s.text("BPW34 a 30-36 V: Cd ~8-9 pF, MIP ~1-1.3 fC -> ~1 mV su CSA_OUT (negativo), ~50 mV positivi su SHAPER_OUT sopra 1.25 V. Filtro ADC 47R + 1 nF.", 25.4, 20.32)
s.text("OPZIONE JFET (DNP): BF862 a source comune + BF862 cascode. Diretto = R120/R121 montate; JFET = togliere R120/R121, montare R122/R123, Q101/Q102 e la polarizzazione (valori da tarare).", 25.4, 25.4)
s.put(OPA4172, "U101", "OPA4172ID", "MIKILAB_OPA4172ID:SOIC127P600X175-14N",
      {"3": "OPA_POS", "2": "OPA_NEG", "1": "CSA_OUT", "5": "1V25_REF", "6": "SH_BASE", "7": "SH_BASE",
       "10": "SH_BASE", "9": "SH_SUM", "8": "SH_C", "12": "SH_RC", "13": "SH_FB", "14": "SHAPER_OUT", "4": "+5V", "11": "GND"}, mpn="OPA4172ID")
s.put(PD, "D101", "VBPW34S", "MIKILAB_VBPW34S:XDCR_VBPW34S", {"A": "CSA_IN", "K": "DIODE_K"}, mpn="VBPW34S")
s.put(ADS8326, "U102", "ADS8326IDGKT", "MIKILAB_ADS8326IDGKT:SOP65P490X110-8N",
      {"1": "2V5_REF", "2": "ADC_IN", "3": "GND", "8": "+3V3", "4": "GND", "5": "CS_ADC", "6": "MISO_L", "7": "SCLK_L"}, mpn="ADS8326IDGKT")
s.put(TMP117, "U103", "TMP117AIDRVR", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
      {"5": "+3V3", "2": "GND", "4": "GND", "7": "GND", "1": "I2C_SCL", "6": "I2C_SDA", "3": "PL_FAULT"}, mpn="TMP117AIDRVR")
s.put(BF862, "Q101", "BF862", "Package_TO_SOT_SMD:SOT-23", {"3": "CSA_IN", "1": "JFET_C", "2": "JFET_S"}, dnp=True, mpn="BF862")
s.put(BF862, "Q102", "BF862", "Package_TO_SOT_SMD:SOT-23", {"3": "CASC_B", "1": "JFET_D", "2": "JFET_C"}, dnp=True, mpn="BF862")
s.newcol()
s.R("R101", "1k", "VBIAS_SH", "VBIAS_DIODE")
s.C("C101", "100nF/100V C0G", "VBIAS_DIODE", "GND", fp=C1206, mpn="C3216C0G2A104J160AE")
s.R("R102", "1M", "VBIAS_DIODE", "DIODE_K")
s.C("C103", "100nF/100V C0G", "DIODE_K", "GND", fp=C1206, mpn="C3216C0G2A104J160AE")
s.R("R120", "0R", "CSA_IN", "OPA_NEG")
s.R("R121", "0R", "1V25_REF", "OPA_POS")
s.R("R122", "0R", "JFET_D", "OPA_POS", dnp=True)
s.R("R123", "0R", "JFET_REF", "OPA_NEG", dnp=True)
s.newcol()
s.R("R124", "750R", "JFET_S", "GND", dnp=True)
s.C("C124", "10uF", "JFET_S", "GND", fp="Capacitor_SMD:C_0805_2012Metric", dnp=True)
s.R("R125", "1k", "+5V", "JFET_D", dnp=True)
s.R("R126", "10k", "+5V", "CASC_B", dnp=True)
s.R("R127", "4.3k", "CASC_B", "GND", dnp=True)
s.C("C127", "1uF", "CASC_B", "GND", dnp=True)
s.R("R128", "10k", "+5V", "JFET_REF", dnp=True)
s.R("R129", "15k", "JFET_REF", "GND", dnp=True)
s.C("C129", "1uF", "JFET_REF", "GND", dnp=True)
s.newcol()
s.C("C102", "1nF C0G", "CSA_OUT", "SH_CD")
s.R("R103", "1k", "SH_CD", "SH_SUM")
s.R("R104", "10k", "SH_SUM", "SH_C")
s.C("C105", "100pF C0G", "SH_SUM", "SH_C")
s.R("R105", "1k", "SH_C", "SH_RC")
s.C("C106", "1nF C0G", "SH_RC", "SH_BASE")
s.R("R112", "1k", "SH_FB", "SH_BASE")
s.R("R113", "4.02k", "SH_FB", "SHAPER_OUT")
s.R("R106", "47R", "ADC_SRC", "ADC_IN")
s.C("C107", "1nF C0G", "ADC_IN", "GND")
s.newcol()
s.R("R107", "100R", "CSA_OUT", "SMA_PRE")
s.put("Connector:Conn_Coaxial", "J101", "SMA preampl.", "Connector_Coaxial:SMA_Amphenol_132134_Vertical", {"1": "SMA_PRE", "2": "GND"})
s.R("R108", "100R", "SHAPER_OUT", "SMA_SH")
s.put("Connector:Conn_Coaxial", "J102", "SMA shaper", "Connector_Coaxial:SMA_Amphenol_132134_Vertical", {"1": "SMA_SH", "2": "GND"})
s.put("Connector:TestPoint", "TP101", "CSA_OUT", TP_FP, {"1": "CSA_OUT"})
s.put("Connector:TestPoint", "TP102", "SHAPER_OUT", TP_FP, {"1": "SHAPER_OUT"})
s.put("Connector:TestPoint", "TP103", "VBIAS_DIODE", TP_FP, {"1": "VBIAS_DIODE"})
s.newcol()
s.C("C111", "47uF", "2V5_REF", "GND", fp=C1206)
s.C("C112", "1uF", "+5V", "GND")
s.C("C113", "100nF", "+5V", "GND")
s.C("C114", "1uF", "+3V3", "GND")
s.C("C115", "100nF", "+3V3", "GND")
s.C("C116", "100nF", "+3V3", "GND")
s.C("C117", "100nF", "SH_BASE", "GND")
s.newcol()
s.text("COMPARATORE E PICCO: TLV3501 (isteresi interna 6 mV) confronta SHAPER_OUT con VTH (DAC OUTB, partitore). HIT memorizzato da U105 -> HIT_LATCH -> MCP GPA7 -> ALERT#.", 25.4, 395)
s.text("Rilevatore di picco U106 (OPA2365 a 3V3, BAS416, hold 1 nF C0G) tra shaper e ADC. Reset di picco e latch: accesso SPI all'indirizzo 3 del piano (CS_Y3 basso). R135 diretto / R136 (DNP) scavalca il picco.", 25.4, 400)
s.put(TLV3501, "U104", "TLV3501AIDBVR", "Package_TO_SOT_SMD:SOT-23-6", {"3": "CMP_P", "1": "VTH", "6": "GND", "4": "+3V3", "2": "GND", "5": "HIT"}, mpn="TLV3501AIDBVR (LCSC C193413)")
s.put(G74, "U105", "SN74LVC1G74DCUR", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", {"2": "+3V3", "1": "HIT", "7": "+3V3", "6": "CS_Y3", "8": "+3V3", "4": "GND", "5": "HIT_LATCH", "3": "NC"}, mpn="SN74LVC1G74DCUR")
s.put(OPA2365, "U106", "OPA2365AIDR", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", {"3": "PK_IN", "2": "PK_FB", "1": "PK_A", "5": "PK_HOLD", "6": "PK_OUT", "7": "PK_OUT", "8": "+3V3", "4": "GND"}, mpn="OPA2365AIDR")
s.put(G04, "U107", "SN74LVC1G04DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "CS_Y3", "1": "NC", "5": "+3V3", "3": "GND", "4": "PK_RST"}, mpn="SN74LVC1G04DBVR")
s.put(BSS138, "Q103", "BSS138", "Package_TO_SOT_SMD:SOT-23", {"1": "PK_RST", "3": "PK_HOLD", "2": "GND"})
s.newcol()
s.R("R130", "1k", "SHAPER_OUT", "CMP_P")
s.R("R131", "1M", "HIT", "CMP_P", dnp=True)
s.R("R132", "1k", "SHAPER_OUT", "PK_IN")
s.put("Device:D", "D102", "BAS416", "Diode_SMD:D_SOD-323", {"1": "PK_HOLD", "2": "PK_A"}, mpn="BAS416")
s.put("Device:D", "D103", "BAS416", "Diode_SMD:D_SOD-323", {"1": "PK_A", "2": "PK_FB"}, mpn="BAS416")
s.R("R133", "10k", "PK_OUT", "PK_FB")
s.C("C108", "1nF C0G", "PK_HOLD", "GND")
s.R("R134", "100k", "PK_RST", "GND")
s.newcol()
s.R("R135", "0R", "PK_OUT", "ADC_SRC")
s.R("R136", "0R", "SHAPER_OUT", "ADC_SRC", dnp=True)
s.R("R137", "100R", "HIT", "SMA_HIT")
s.put("Connector:Conn_Coaxial", "J103", "SMA HIT", "Connector_Coaxial:SMA_Amphenol_132134_Vertical", {"1": "SMA_HIT", "2": "GND"})
s.put("Connector:TestPoint", "TP104", "HIT", TP_FP, {"1": "HIT"})
s.put("Connector:TestPoint", "TP105", "PK_OUT", TP_FP, {"1": "PK_OUT"})
s.C("C118", "100nF", "+3V3", "GND")
s.C("C119", "100nF", "+3V3", "GND")
s.C("C120", "100nF", "+3V3", "GND")
s.text("SMA con 100R in serie: oscilloscopio a 1 MOhm. C101/C103/C506 C0G 100 nF 100 V 1206 (TDK C3216C0G2A104J160AE): niente X7R, perdono nA a 30 V.", 25.4, 410)
sheets.append(s)

# =============================================================== 2. Rete di retroazione
s = PS("RetroactionNetwork", "retroaction-network.kicad_sch", 0, "3")
s.text("RETROAZIONE: R201 100M sempre presente (DC definita anche con MCP in reset). Rf 10k..10M con TMUX1112 (chiuso con SEL=1, pull-down 100k = aperti al reset).", 25.4, 15.24)
s.text("Cf: C201 1 pF fisso (default) + banchi BGSA142: -IN -> Cf -> RFx -> RFC -> 10 nF C0G -> uscita. 100M verso GND su ogni RFx e RFC. CTL tramite partitore 10k/22k (3.3 V -> 2.27 V, pull-down al reset).", 25.4, 20.32)
mcp_n = {"5": "+3V3", "6": "GND", "29": "GND", "7": "CS_MCP", "8": "SCLK_L", "9": "MOSI_L", "10": "MISO_L", "11": "GND", "12": "GND", "13": "GND",
         "14": "MCP_RST", "15": "NC", "16": "MCP_INTA", "23": "PL_FAULT", "24": "HIT_LATCH"}
for i, g in enumerate(("17", "18", "19", "20", "21", "22")):
    mcp_n[g] = f"GPA{i}"
for i, g in enumerate(("25", "26", "27", "28", "1", "2", "3", "4")):
    mcp_n[g] = f"SEL_R{i + 1}"
s.put(MCP, "U201", "MCP23S17-E/ML", "Package_DFN_QFN:QFN-28-1EP_6x6mm_P0.65mm_EP4.25x4.25mm", mcp_n, mpn="MCP23S17-E/ML")
RF = ("10k", "47k", "100k", "470k", "1M", "2.2M", "4.7M", "10M")
for u, base in (("U202", 0), ("U203", 4)):
    n = {"11": "+5V", "3": "GND", "2": "NC", "10": "NC"}
    for k, (sp, dp, sel) in enumerate((("1", "16", "15"), ("12", "13", "14"), ("9", "8", "7"), ("4", "5", "6"))):
        n[sp] = "CSA_IN"
        n[dp] = f"RF_{base + k + 1}"
        n[sel] = f"SEL_R{base + k + 1}"
    s.put(TMUX, u, "TMUX1112RSVR", "MIKILAB_TMUX1112RSVR:RSV0016A-MFG", n, mpn="TMUX1112RSVR")
for u, grp in (("U204", "A"), ("U205", "B")):
    off = 0 if grp == "A" else 3
    s.put(BGSA, u, "BGSA142GN12", "MIKILAB_BGSA142GN12E6327XTSA1:PG-TSNP-12-1",
          {"4": "+3V3", "3": "GND", "8": "GND", "7": f"CTL{grp}0", "5": f"CTL{grp}1", "6": f"CTL{grp}2",
           "11": f"CF{grp}_COM", "12": f"CF{grp}_COM", "1": f"CF{grp}1", "2": f"CF{grp}2", "10": f"CF{grp}3", "9": f"CF{grp}4"}, mpn="BGSA142GN12E6327XTSA1")
s.newcol()
s.R("R201", "100M", "CSA_IN", "CSA_OUT", fp=R0805, mpn="HVC0805T1006FET")
s.C("C201", "1pF C0G", "CSA_IN", "CSA_OUT")
for k, v in enumerate(RF):
    s.R(f"R{211 + k}", v, f"RF_{k + 1}", "CSA_OUT")
s.newcol()
for k in range(8):
    s.R(f"R{221 + k}", "100k", f"SEL_R{k + 1}", "GND")
s.newcol()
CF = {"A": ("0.5pF", "1pF", "2.2pF", "4.7pF"), "B": ("10pF", "22pF", "47pF", "100pF")}
for grp, base in (("A", 231), ("B", 241)):
    for k, v in enumerate(CF[grp]):
        s.C(f"C{base + k}", v + " C0G", "CSA_IN", f"CF{grp}{k + 1}")
        s.R(f"R{base + k}", "100M", f"CF{grp}{k + 1}", "GND", fp=R0805)
    s.C(f"C{base + 5}", "10nF C0G", f"CF{grp}_COM", "CSA_OUT")
    s.R(f"R{base + 5}", "100M", f"CF{grp}_COM", "GND", fp=R0805)
    s.newcol()
for i in range(6):
    grp, b = ("A", i) if i < 3 else ("B", i - 3)
    s.R(f"R{251 + i}", "10k", f"GPA{i}", f"CTL{grp}{b}")
    s.R(f"R{261 + i}", "22k", f"CTL{grp}{b}", "GND")
s.newcol()
s.R("R270", "10k", "+3V3", "MCP_RST")
s.C("C270", "100nF", "MCP_RST", "GND")
s.put("Connector:TestPoint", "TP201", "MCP_RST", TP_FP, {"1": "MCP_RST"})
for k, net in enumerate(("+3V3", "+5V", "+5V", "+3V3", "+3V3")):
    s.C(f"C{271 + k}", "100nF", net, "GND")
s.C("C276", "1uF", "+3V3", "GND")
sheets.append(s)

# =============================================================== 3. Emettitore di test
s = PS("EmettitoreTest", "emittier.kicad_sch", 0, "4")
s.text("EMETTITORE: LTC6993-2 (durata con AD5245 100k reostato + 47k) -> BSS138 -> LED IR alimentato da +5V (non piu da V_BIAS).", 25.4, 15.24)
s.text("TRIG dallo strobe CS_Y4 (accesso SPI all indirizzo 4 del piano: il fronte di salita a fine accesso avvia l impulso) o dal connettore J301. AD5245 su I2C del bus, indirizzo 0x2C (AD0 a GND).", 25.4, 20.32)
s.put(LTC6993, "U301", "LTC6993CS6-2", "MIKILAB_LTC6993CS6_2TRMPBF:SOT95P280X100-6N",
      {"5": "+3V3", "2": "GND", "1": "TRIG_INPULSE", "3": "LTC_SET", "4": "GND", "6": "LTC_OUT"}, mpn="LTC6993CS6-2#TRMPBF")
s.put(AD5245, "U302", "AD5245BRJZ100", "MIKILAB_AD5245BRJZ10_RL7:SOT65P280X145-8N",
      {"2": "+3V3", "3": "GND", "4": "I2C_SCL", "5": "I2C_SDA", "6": "GND", "8": "NC", "1": "RHEO_W", "7": "GND"}, mpn="AD5245BRJZ100-RL7")
s.put(BSS138, "Q301", "BSS138", "Package_TO_SOT_SMD:SOT-23", {"1": "Q_G", "2": "GND", "3": "LED_K"})
s.put(LED, "D301", "VSMY2940G", "MIKILAB_VSMY2940G:DIO_VSMY2940G", {"A": "LED_A", "C": "LED_K"}, mpn="VSMY2940G")
s.newcol()
s.R("R301", "47k 1%", "RHEO_W", "LTC_SET")
s.R("R302", "47R", "LTC_OUT", "Q_G")
s.R("R303", "10k", "Q_G", "GND")
s.R("R305", "220R", "+5V", "LED_A", fp=R0805)
s.R("R304", "1k", "CS_Y4", "TRIG_INPULSE")
s.R("R306", "10k", "TRIG_INPULSE", "GND")
s.newcol()
s.put("Connector_Generic:Conn_01x02", "J301", "TRIG est.", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", {"1": "TRIG_INPULSE", "2": "GND"})
s.C("C301", "100nF", "+3V3", "GND")
s.C("C302", "100nF", "+3V3", "GND")
s.C("C303", "10uF", "+5V", "GND", fp="Capacitor_SMD:C_0805_2012Metric")
sheets.append(s)

# =============================================================== 4. Bias del diodo
s = PS("BiasDiodo", "bias.kicad_sch", 0, "5")
s.text("BIAS LOCALE: DAC61402 alimentato da VHV_36V (bus pin 8) con RC 100R + 2x1uF/100V. OUTA -> shunt 10k (INA239) -> VBIAS_SH -> RC 1k/100nF vicino al diodo.", 25.4, 15.24)
s.text("INA239 con shunt 10k: ADCRANGE=1 -> 1.25 uV/LSB = 125 pA/LSB, fondo scala 4.1 uA; ADCRANGE=0 -> 500 pA/LSB, 16.4 uA. Errori: Vos 5 uV max (0.5 nA), IB 0.1 nA tip / 2.5 nA max.", 25.4, 20.32)
s.text("DAC: AVDD ~36 V -> uscita max ~34.5 V (headroom 1.5 V). OUTB (range 0-5 V) -> partitore 22k/10k -> VTH soglia del comparatore (0-1.56 V, 0.38 mV/LSB), BAT54S di protezione. CCOMP DNP.", 25.4, 25.4)
s.put(DAC, "U501", "DAC61402RHBR", "MIKILAB_DAC61402RHBR:VQFN32_RHB_TEX",
      {"28": "AVDD_DAC", "30": "+5V", "15": "+3V3", "26": "DAC_REF", "25": "GND", "27": "GND", "29": "GND", "14": "GND", "33": "GND",
       "12": "CS_DAC", "10": "SCLK_L", "11": "MOSI_L", "9": "MISO_L", "13": "GND", "16": "+3V3", "32": "+3V3", "31": "PL_FAULT",
       "8": "DAC_OUTA", "6": "DAC_OUTA", "5": "GND", "7": "CCOMPA", "17": "DAC_OUTB", "19": "DAC_OUTB", "20": "GND", "18": "CCOMPB"}, mpn="DAC61402RHBR")
s.put(INA239, "U502", "INA239AIDGSR", "MIKILAB_INA239AIDGSR:VSSOP_9AIDGST_TEX",
      {"6": "+3V3", "7": "GND", "1": "CS_INA", "5": "SCLK_L", "2": "MOSI_L", "4": "MISO_L", "3": "PL_FAULT", "10": "DAC_OUTA", "9": "VBIAS_SH", "8": "VBIAS_SH"}, mpn="INA239AIDGSR")
s.newcol()
s.R("R501", "100R", "VHV_36V", "AVDD_DAC", fp=R0805)
s.C("C501", "1uF/100V", "AVDD_DAC", "GND", fp=C1206)
s.C("C502", "1uF/100V", "AVDD_DAC", "GND", fp=C1206)
s.C("C503", "100nF/100V", "AVDD_DAC", "GND", fp=C1206)
s.C("C504", "470pF/100V", "CCOMPA", "DAC_OUTA", fp=C1206, dnp=True)
s.C("C505", "470pF/100V", "CCOMPB", "DAC_OUTB", fp=C1206, dnp=True)
s.newcol()
s.R("R502", "10k 0.1%", "DAC_OUTA", "VBIAS_SH", fp=R0805, mpn="ERA-6ARB103V")
s.R("R503", "22k", "DAC_OUTB", "VTH")
s.R("R505", "10k", "VTH", "GND")
s.put(BAT54S, "D501", "BAT54S", "Package_TO_SOT_SMD:SOT-23", {"3": "VTH", "1": "GND", "2": "+3V3"}, mpn="BAT54S")
s.C("C506", "100nF", "VTH", "GND")
s.R("R504", "10k", "+3V3", "PL_FAULT")
s.put("Connector:TestPoint", "TP501", "DAC_OUTA", TP_FP, {"1": "DAC_OUTA"})
s.put("Connector:TestPoint", "TP502", "VTH", TP_FP, {"1": "VTH"})
s.newcol()
s.C("C507", "100nF", "+5V", "GND")
s.C("C508", "100nF", "+3V3", "GND")
s.C("C509", "100nF", "DAC_REF", "GND")
s.C("C510", "100nF", "+3V3", "GND")
sheets.append(s)

# =============================================================== 5. Bus MIKILAB plug and play
s = PS("bus-pnp", "bus-pnp.kicad_sch", 0, "6")
s.text("BUS MIKILAB REV5.0 - MAIN 28 pin. J_IN dal piano precedente, J_OUT verso il successivo: tutto passante tranne ID (25-27), che esce come ID+1 (74HC283).", 25.4, 15.24)
s.text("Piano selezionato se PREFIX = ID_IN (74HC85 QA=B -> E3 del 138). CS_MASTER su ~E1, ~E2 a GND. Y0 ADC, Y1 DAC, Y2 INA, Y3-Y5 test point, Y6 EEPROM ID, Y7 MCP23S17.", 25.4, 20.32)
s.text("MISO verso il bus tramite 74LVC1G125, abilitato solo con piano selezionato e CS_MASTER basso. ALERT# open-drain (74LVC1G07) da INTA (MCP con MIRROR=1). Pull-up I2C e ALERT# sulla scheda master.", 25.4, 25.4)
s.text("REV5.1: pin 28 = HIT# (open-drain, attivo basso, pull-up 4.7k sul master). HIT del comparatore -> monostabile 74LVC1G123 (2k + 27 pF, ~170-200 ns) -> 74LVC1G06 open-drain. Passante J_IN -> J_OUT.", 25.4, 35.56)
s.text("FPC: XUNPU FPC-05F-28PH20 (LCSC C2856807), footprint PianoTest:FPC-05F-28PH20 importato da EasyEDA. Contatti in basso.", 25.4, 30.48)
BUS = {1: "GND", 2: "+5V", 3: "+3V3", 4: "GND", 5: "2V5_REF", 6: "1V25_REF", 7: "GND_A", 8: "VHV_36V", 9: "VHV_36V_2", 10: "GND",
       11: "BUS_SCLK", 12: "BUS_MOSI", 13: "BUS_MISO", 14: "I2C_SDA", 15: "I2C_SCL", 16: "GND", 17: "BUS_CS_MASTER",
       18: "BUS_ADDR0", 19: "BUS_ADDR1", 20: "BUS_ADDR2", 21: "BUS_PREFIX0", 22: "BUS_PREFIX1", 23: "BUS_PREFIX2", 24: "BUS_ALERT_N",
       25: "ID_IN0", 26: "ID_IN1", 27: "ID_IN2", 28: "BUS_HIT_N"}
FPC = "PianoTest:FPC-05F-28PH20"
jin = {str(k): v for k, v in BUS.items()}
jin["MP"] = "GND"
jout = dict(jin)
jout.update({"25": "ID_OUT0", "26": "ID_OUT1", "27": "ID_OUT2"})
s.put("Connector_Generic_MountingPin:Conn_01x28_MountingPin", "J401", "J_IN MAIN", FPC, jin, mpn="FPC-05F-28PH20")
s.put("Connector_Generic_MountingPin:Conn_01x28_MountingPin", "J402", "J_OUT MAIN", FPC, jout, mpn="FPC-05F-28PH20")
s.newcol()
s.put(HC283, "U401", "74HC283", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
      {"5": "ID_IN0", "3": "ID_IN1", "14": "ID_IN2", "12": "GND", "6": "GND", "2": "GND", "15": "GND", "11": "GND", "7": "+3V3",
       "16": "+3V3", "8": "GND", "4": "ID_OUT0", "1": "ID_OUT1", "13": "ID_OUT2", "10": "NC", "9": "NC"}, mpn="74HC283PW")
s.put(HC85, "U402", "74HC85", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
      {"10": "BUS_PREFIX0", "12": "BUS_PREFIX1", "13": "BUS_PREFIX2", "15": "GND", "9": "ID_IN0", "11": "ID_IN1", "14": "ID_IN2", "1": "GND",
       "2": "GND", "3": "+3V3", "4": "GND", "16": "+3V3", "8": "GND", "5": "AGTB", "6": "PL_SEL", "7": "ALTB"}, mpn="74HC85PW")
s.put(HC138, "U403", "74HC138", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
      {"1": "BUS_ADDR0", "2": "BUS_ADDR1", "3": "BUS_ADDR2", "4": "BUS_CS_MASTER", "5": "GND", "6": "PL_SEL", "16": "+3V3", "8": "GND",
       "15": "CS_ADC", "14": "CS_DAC", "13": "CS_INA", "12": "CS_Y3", "11": "CS_Y4", "10": "CS_Y5", "9": "CS_EEP", "7": "CS_MCP"}, mpn="74HC138PW")
s.newcol()
s.put(G17, "U404", "SN74LVC2G17DBVR", "Package_TO_SOT_SMD:SOT-23-6", {"1": "BUS_SCLK", "3": "BUS_MOSI", "5": "+3V3", "2": "GND", "6": "SCLK_L", "4": "MOSI_L"}, mpn="SN74LVC2G17DBVR")
s.put(G125, "U405", "SN74LVC1G125DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "MISO_L", "1": "MISO_OE_N", "5": "+3V3", "3": "GND", "4": "BUS_MISO"}, mpn="SN74LVC1G125DBVR")
s.put(G332, "U406", "SN74LVC1G332DBVR", "Package_TO_SOT_SMD:SOT-23-6", {"1": "BUS_CS_MASTER", "3": "AGTB", "6": "ALTB", "5": "+3V3", "2": "GND", "4": "MISO_OE_N"}, mpn="SN74LVC1G332DBVR")
s.put(G07, "U407", "SN74LVC1G07DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "MCP_INTA", "1": "NC", "5": "+3V3", "3": "GND", "4": "BUS_ALERT_N"}, mpn="SN74LVC1G07DBVR")
s.put(G123, "U409", "SN74LVC1G123DCUR", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", {"1": "GND", "2": "HIT", "3": "+3V3", "8": "+3V3", "4": "GND", "5": "HIT_PULSE", "7": "MONO_RC", "6": "MONO_C"}, mpn="SN74LVC1G123DCUR")
s.put(G06, "U410", "SN74LVC1G06DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "HIT_PULSE", "1": "NC", "5": "+3V3", "3": "GND", "4": "BUS_HIT_N"}, mpn="SN74LVC1G06DBVR")
s.put(EEP, "U408", "25AA02E48T-I/SN", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
      {"1": "CS_EEP", "6": "SCLK_L", "5": "MOSI_L", "3": "+3V3", "7": "+3V3", "8": "+3V3", "4": "GND", "2": "MISO_L"}, mpn="25AA02E48T-I/SN")
s.newcol()
for k, n in enumerate(("CS_Y3", "CS_Y4", "CS_Y5")):
    s.put("Connector:TestPoint", f"TP{401 + k}", n, TP_FP, {"1": n})
s.R("R401", "0R", "GND_A", "GND")
s.R("R402", "100k", "+3V3", "BUS_CS_MASTER")
s.R("R403", "100k", "MISO_L", "GND")
for k in range(3):
    s.R(f"R{404 + k}", "100k", f"ID_IN{k}", "GND")
s.R("R407", "2k", "+3V3", "MONO_RC")
s.C("C415", "27pF C0G", "MONO_RC", "MONO_C")
s.C("C416", "100nF", "+3V3", "GND")
s.C("C417", "100nF", "+3V3", "GND")
s.newcol()
for k in range(8):
    s.C(f"C{401 + k}", "100nF", "+3V3", "GND")
s.C("C409", "10uF", "+3V3", "GND", fp="Capacitor_SMD:C_0805_2012Metric")
s.C("C410", "10uF", "+5V", "GND", fp="Capacitor_SMD:C_0805_2012Metric")
s.C("C411", "100nF/100V", "VHV_36V", "GND", fp=C1206)
s.C("C412", "100nF/100V", "VHV_36V_2", "GND", fp=C1206)
s.C("C413", "1uF", "2V5_REF", "GND")
s.C("C414", "1uF", "1V25_REF", "GND")
s.newcol()
ESD = ["BUS_SCLK", "BUS_MOSI", "BUS_MISO", "I2C_SDA", "I2C_SCL", "BUS_CS_MASTER", "BUS_ADDR0", "BUS_ADDR1", "BUS_ADDR2",
       "BUS_PREFIX0", "BUS_PREFIX1", "BUS_PREFIX2", "BUS_ALERT_N", "BUS_HIT_N", "ID_IN0", "ID_IN1", "ID_IN2", "ID_OUT0", "ID_OUT1", "ID_OUT2"]
for k, n in enumerate(ESD):
    if k in (10,):
        s.newcol()
    s.put("Device:D_TVS", f"D{401 + k}", "TPD1E10B06", "Diode_SMD:D_0402_1005Metric", {"1": n, "2": "GND"}, mpn="TPD1E10B06DPYR")
sheets.append(s)

# =============================================================== scrittura
lib = "(kicad_symbol_lib (version 20251024) (generator \"gen_piano\") " + " ".join(
    v.replace(f'(symbol "{LIB}:{k}"', f'(symbol "{k}"', 1) for k, v in SYMS.items()) + ")"
open(f"{PRJ}/PianoTest.kicad_sym", "w").write(lib)
open(f"{PRJ}/fp-lib-table", "w").write(f'(fp_lib_table (version 7) (lib (name "{LIB}") (type "KiCad") (uri "${{KIPRJMOD}}/PianoTest.pretty") (options "") (descr "Footprint PianoTest")))\n')
open(f"{PRJ}/sym-lib-table", "w").write(f'(sym_lib_table (version 7) (lib (name "{LIB}") (type "KiCad") (uri "${{KIPRJMOD}}/PianoTest.kicad_sym") (options "") (descr "Simboli PianoTest")))\n')
open(f"{PRJ}/PianoTest.kicad_sch", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{ROOT}") (paper "A4") (lib_symbols)\n'
    f'\t(text "PianoTest - piano di test MuonScope sul bus MIKILAB (REV5.0). Vedi README.md." (exclude_from_sim no) (at 25.4 20.32 0) {F.format(j="left bottom")} (uuid "{U()}"))\n'
    '\t(sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
for i, sh in enumerate(sheets):
    sh.write(PRJ, 25.4 + 60 * (i % 3), 40.64 + 30 * (i // 3))
# ogni foglio senza pin: altezza minima
r = open(f"{PRJ}/PianoTest.kicad_sch").read()
r = re.sub(r"\(size 50.8 5.08\)", "(size 50.8 15.24)", r)
open(f"{PRJ}/PianoTest.kicad_sch", "w").write(r)
print("ok", [len(sh.items) for sh in sheets])
