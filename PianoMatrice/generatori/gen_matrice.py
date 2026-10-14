"""Generatore del progetto KiCad 10 "PianoMatrice": piano MuonScope 4x4 VBPW34S sul bus MIKILAB REV5.1.
Riusa simboli e classe PS del generatore del PianoTest. Uso: python3 gen_matrice.py <cartella progetto>"""
import sys, os, re, uuid, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "gen_piano.py")).read()
exec(src[:src.index("sheets = []")])          # simboli, PS, costanti
import kisheet

PRJ = sys.argv[1]
os.makedirs(PRJ, exist_ok=True)
ROOT = str(uuid.uuid4())
kisheet.PROJ = "PianoMatrice"
kisheet.ROOT_UUID = ROOT
LIB = "PianoTest"            # stessa libreria di simboli locale (copiata come PianoMatrice.kicad_sym)
FPC = "PianoMatrice:FPC-05F-28PH20"

GLOBALS = {
    "GND", "+3V3", "+5V", "2V5_REF", "1V25_REF", "VHV_36V", "VHV_36V_2",
    "SCLK_L", "MOSI_L", "MISO_L", "CS_ADC", "CS_DAC", "CS_INA", "CS_Y3", "CS_Y4", "CS_HITMAP", "CS_MCP",
    "I2C_SDA", "I2C_SCL", "PL_FAULT", "MCP_INTA", "VBIAS_SH", "VTH", "PK_RST", "TEST_INJ", "HIT_ANY",
} | {f"Q{i}" for i in range(16)} | {f"QN{i}" for i in range(16)} | {f"HOLD{i}" for i in range(16)}

HC30 = box("74HC30", L(*[(n, f"I{k}") for k, n in enumerate(("1", "2", "3", "4", "5", "6", "11", "12"))], ("14", "VCC"), ("7", "GND"), ("9", "NC"), ("10", "NC"), ("13", "NC"))
           + Rr(("8", "Y"),), "74HC30 NAND a 8 ingressi")
OPA4140 = box("OPA4140", L(("3", "+INA"), ("2", "-INA"), ("5", "+INB"), ("6", "-INB"), ("10", "+INC"), ("9", "-INC"), ("12", "+IND"), ("13", "-IND"), ("4", "V+"), ("11", "V-"))
              + Rr(("1", "OUTA"), ("7", "OUTB"), ("8", "OUTC"), ("14", "OUTD")), "OPA4140 quad JFET 11 MHz 5.1 nV/rtHz, TSSOP-14")
TLV3502 = box("TLV3502", L(("1", "+INA"), ("2", "-INA"), ("3", "+INB"), ("4", "-INB"), ("8", "V+"), ("5", "V-")) + Rr(("7", "OUTA"), ("6", "OUTB")), "TLV3502 doppio comparatore 4.5 ns")
LVC74 = box("74LVC74A", L(("2", "1D"), ("3", "1CLK"), ("1", "~{1CLR}"), ("4", "~{1PRE}"), ("12", "2D"), ("11", "2CLK"), ("13", "~{2CLR}"), ("10", "~{2PRE}"), ("14", "VCC"), ("7", "GND"))
            + Rr(("5", "1Q"), ("6", "~{1Q}"), ("9", "2Q"), ("8", "~{2Q}")), "SN74LVC74A doppio flip-flop D, TSSOP-14")
TMUX1108 = box("TMUX1108", L(("1", "A0"), ("16", "A1"), ("15", "A2"), ("2", "EN"), ("13", "VDD"), ("3", "VSS"), ("14", "GND"))
               + Rr(("4", "S1"), ("5", "S2"), ("6", "S3"), ("7", "S4"), ("12", "S5"), ("11", "S6"), ("10", "S7"), ("9", "S8"), ("8", "D")), "TMUX1108 mux 8:1 bassa perdita, TSSOP-16")
G32 = box("74LVC1G32", L(("1", "A"), ("2", "B"), ("5", "VCC"), ("3", "GND")) + Rr(("4", "Y"),), "SN74LVC1G32 OR, SOT-23-5", w=10.16)
G02 = box("74LVC1G02", L(("1", "A"), ("2", "B"), ("5", "VCC"), ("3", "GND")) + Rr(("4", "Y"),), "SN74LVC1G02 NOR, SOT-23-5", w=10.16)

R0402, C0402 = "Resistor_SMD:R_0402_1005Metric", "Capacitor_SMD:C_0402_1005Metric"
C0G1206 = "C3216C0G2A104J160AE"


# ------------------------------------------------------------------ foglio canale ripetuto
class Multi(PS):
    """Foglio usato in N istanze: riferimenti R5 -> R105, R205, ... (istanza k -> (k+1)*100 + n)."""

    def __init__(self, *a, n=8, **k):
        super().__init__(*a, **k)
        self.n = n
        self.inst = [str(uuid.uuid4()) for _ in range(n)]
        self.hierset = {"QA", "QB", "QNA", "QNB", "HOLDA", "HOLDB"}

    def label(self, net, x, y, ang):
        if net in self.hierset:
            j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
            self.items.append(f'(hierarchical_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) {F.format(j=j)} (uuid "{U()}"))')
        else:
            super().label(net, x, y, ang)

    def place(self, lib_id, ref, val, fp, x, y, nets, dnp=False, mpn=None):
        super().place(lib_id, ref, val, fp, x, y, nets, dnp=dnp, mpn=mpn)
        m = re.match(r"([A-Z]+)(\d+)$", ref)
        pre, num = m.group(1), int(m.group(2))
        paths = " ".join(f'(path "/{ROOT}/{u}" (reference "{pre}{(k + 1) * 100 + num}") (unit 1))' for k, u in enumerate(self.inst))
        self.items[-1] = re.sub(r'\(instances \(project "PianoMatrice" \(path "[^"]*" \(reference "[^"]*"\) \(unit 1\)\)\)\)',
                                f'(instances (project "PianoMatrice" {paths}))', self.items[-1])


ch = Multi("Canali", "canali.kicad_sch", 0, "2")
ch.text("DUE CANALI (A, B) - foglio ripetuto 8 volte: canali 2k e 2k+1. Valori di retroazione da variabili di progetto: Rf = ${RF}, Cf = ${CF} (File > Impostazioni progetto > Variabili di testo).", 25.4, 15.24)
ch.text("Catena: VBPW34S -> CSA (OPA4140 A/B, +IN a 1V25_REF) -> shaper CR-RC invertente x50 tau 1 us (OPA4140 C/D) -> TLV3502 (soglia VTH) -> 74LVC74A (latch, CLR con CS_Y3) -> rilevatore di picco OPA2365 + BAS416 + 1 nF C0G.", 25.4, 20.32)
ch.text("Iniezione di carica di test: 0.5 pF da TEST_INJ (gradino di ~3.3 mV -> ~1.6 fC). Rf2/Cf2 DNP in parallelo per prove. Trim di soglia per canale DNP (R tra VTH_x e GND).", 25.4, 25.4)
OPA_N = {"4": "+5V", "11": "GND"}
for side, (pin_p, pin_n, pin_o, sp, sn, so) in (("A", ("3", "2", "1", "10", "9", "8")), ("B", ("5", "6", "7", "12", "13", "14"))):
    OPA_N.update({pin_p: "1V25_REF", pin_n: f"CSA_{side}", pin_o: f"CSO_{side}", sp: "1V25_REF", sn: f"SUM_{side}", so: f"SHO_{side}"})
ch.put(OPA4140, "U1", "OPA4140AIPWR", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", OPA_N, mpn="OPA4140AIPWR")
ch.put(TLV3502, "U2", "TLV3502AIDGKR", "Package_SO:VSSOP-8_3x3mm_P0.65mm",
       {"1": "CP_A", "2": "VTH_A", "3": "CP_B", "4": "VTH_B", "8": "+3V3", "5": "GND", "7": "CMP_A", "6": "CMP_B"}, mpn="TLV3502AIDGKR")
ch.put(LVC74, "U3", "SN74LVC74APWR", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
       {"2": "+3V3", "3": "CMP_A", "1": "CS_Y3", "4": "+3V3", "12": "+3V3", "11": "CMP_B", "13": "CS_Y3", "10": "+3V3", "14": "+3V3", "7": "GND",
        "5": "QA", "6": "QNA", "9": "QB", "8": "QNB"}, mpn="SN74LVC74APWR")
ch.put(OPA2365, "U4", "OPA2365AIDR", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
       {"3": "PKI_A", "2": "HOLDA", "1": "PKO_A", "5": "PKI_B", "6": "HOLDB", "7": "PKO_B", "8": "+3V3", "4": "GND"}, mpn="OPA2365AIDR")
ch.put(PD, "D1", "VBPW34S", "MIKILAB_VBPW34S:XDCR_VBPW34S", {"A": "CSA_A", "K": "DK_A"}, mpn="VBPW34S")
ch.put(PD, "D2", "VBPW34S", "MIKILAB_VBPW34S:XDCR_VBPW34S", {"A": "CSA_B", "K": "DK_B"}, mpn="VBPW34S")
for i, side in enumerate("AB"):
    b = 10 * (i + 1)          # A: 10..29, B: 30..49 (riferimenti locali)
    b = 10 + 20 * i
    ch.newcol()
    ch.R(f"R{b}", "1k", "VBIAS_SH", f"DK_{side}")
    ch.C(f"C{b}", "100nF/100V C0G", f"DK_{side}", "GND", fp=C1206, mpn=C0G1206)
    ch.R(f"R{b + 1}", "${RF}", f"CSA_{side}", f"CSO_{side}", fp=R0805)
    ch.C(f"C{b + 1}", "${CF} C0G", f"CSA_{side}", f"CSO_{side}", fp=C0402)
    ch.R(f"R{b + 2}", "Rf2", f"CSA_{side}", f"CSO_{side}", fp=R0805, dnp=True)
    ch.C(f"C{b + 2}", "Cf2", f"CSA_{side}", f"CSO_{side}", fp=C0402, dnp=True)
    ch.C(f"C{b + 3}", "0.5pF C0G", "TEST_INJ", f"CSA_{side}", fp=C0402)
    ch.C(f"C{b + 4}", "1nF C0G", f"CSO_{side}", f"SD_{side}", fp=C0402)
    ch.R(f"R{b + 4}", "1k", f"SD_{side}", f"SUM_{side}", fp=R0402)
    ch.R(f"R{b + 5}", "49.9k", f"SUM_{side}", f"SHO_{side}", fp=R0402)
    ch.C(f"C{b + 5}", "20pF C0G", f"SUM_{side}", f"SHO_{side}", fp=C0402)
    ch.newcol()
    ch.R(f"R{b + 6}", "1k", f"SHO_{side}", f"CP_{side}", fp=R0402)
    ch.R(f"R{b + 7}", "0R", "VTH", f"VTH_{side}", fp=R0402)
    ch.R(f"R{b + 8}", "trim", f"VTH_{side}", "GND", fp=R0402, dnp=True)
    ch.R(f"R{b + 9}", "1k", f"SHO_{side}", f"PKI_{side}", fp=R0402)
    ch.put("Device:D", f"D{b}", "BAS416", "Diode_SMD:D_SOD-323", {"1": f"HOLD{side}", "2": f"PKO_{side}"}, mpn="BAS416")
    ch.C(f"C{b + 6}", "1nF C0G", f"HOLD{side}", "GND", fp=C0402)
    ch.put(BSS138, f"Q{b}", "BSS138", "Package_TO_SOT_SMD:SOT-23", {"1": "PK_RST", "3": f"HOLD{side}", "2": "GND"})
ch.newcol()
for k, net in enumerate(("+5V", "+5V", "+3V3", "+3V3", "+3V3")):
    ch.C(f"C{50 + k}", "100nF", net, "GND", fp=C0402)

sheets = []

# ------------------------------------------------------------------ acquisizione
s = PS("Acquisizione", "acquisizione.kicad_sch", 0, "3")
s.text("MAPPA DEI COLPI: MCP23S17 U1001 (indirizzo Y5, CS_HITMAP) legge i 16 latch Q0-Q15 in una transazione. CONTROLLO: MCP23S17 U1002 (Y7, interrupt manager) - mux, test, FAULT, HIT_ANY.", 25.4, 15.24)
s.text("AMPIEZZA: 2x TMUX1108 (8:1, 3 pA) sui 16 HOLD -> buffer OPA2365 -> 47R + 1 nF -> ADS8326 (Y0). Reset di latch e picchi: accesso all'indirizzo 3 (CS_Y3). Gradino di test: accesso all'indirizzo 4 con TEST_EN_N basso.", 25.4, 20.32)
s.text("HIT_ANY = OR dei 16 latch (2x 74HC30 sui ~Q + 74LVC1G32): un solo fronte per evento fino al reset.", 25.4, 25.4)
s.put(MCP, "U1001", "MCP23S17-E/ML", "Package_DFN_QFN:QFN-28-1EP_6x6mm_P0.65mm_EP4.25x4.25mm",
      {"5": "+3V3", "6": "GND", "29": "GND", "7": "CS_HITMAP", "8": "SCLK_L", "9": "MOSI_L", "10": "MISO_L", "11": "+3V3", "12": "GND", "13": "GND",
       "14": "MCP_RST", "15": "NC", "16": "NC", **{str(17 + i): f"Q{i}" for i in range(8)}, **{str(25 + i): f"Q{8 + i}" for i in range(4)},
       **{str(1 + i): f"Q{12 + i}" for i in range(4)}}, mpn="MCP23S17-E/ML")
s.put(MCP, "U1002", "MCP23S17-E/ML", "Package_DFN_QFN:QFN-28-1EP_6x6mm_P0.65mm_EP4.25x4.25mm",
      {"5": "+3V3", "6": "GND", "29": "GND", "7": "CS_MCP", "8": "SCLK_L", "9": "MOSI_L", "10": "MISO_L", "11": "GND", "12": "GND", "13": "GND",
       "14": "MCP_RST", "15": "NC", "16": "MCP_INTA", "17": "MUX_A0", "18": "MUX_A1", "19": "MUX_A2", "20": "MUX_EN_LO", "21": "MUX_EN_HI",
       "22": "PL_FAULT", "23": "HIT_ANY", "24": "TEST_EN_N", "25": "NC", "26": "NC", "27": "NC", "28": "NC", "1": "NC", "2": "NC", "3": "NC", "4": "NC"},
      mpn="MCP23S17-E/ML")
for u, en, base in (("U1003", "MUX_EN_LO", 0), ("U1004", "MUX_EN_HI", 8)):
    n = {"1": "MUX_A0", "16": "MUX_A1", "15": "MUX_A2", "2": en, "13": "+3V3", "3": "GND", "14": "GND", "8": "MUX_D"}
    for k, pin in enumerate(("4", "5", "6", "7", "12", "11", "10", "9")):
        n[pin] = f"HOLD{base + k}"
    s.put(TMUX1108, u, "TMUX1108PWR", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", n, mpn="TMUX1108PWR")
s.put(OPA2365, "U1005", "OPA2365AIDR", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
      {"3": "MUX_D", "2": "ADC_BUF", "1": "ADC_BUF", "5": "GND", "6": "OPB_UNUSED", "7": "OPB_UNUSED", "8": "+3V3", "4": "GND"}, mpn="OPA2365AIDR")
s.put(ADS8326, "U1006", "ADS8326IDGKT", "MIKILAB_ADS8326IDGKT:SOP65P490X110-8N",
      {"1": "2V5_REF", "2": "ADC_IN", "3": "GND", "8": "+3V3", "4": "GND", "5": "CS_ADC", "6": "MISO_L", "7": "SCLK_L"}, mpn="ADS8326IDGKT")
s.newcol()
for u, base in (("U1007", 0), ("U1008", 8)):
    s.put(HC30, u, "74HC30PW", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
          {**{p: f"QN{base + k}" for k, p in enumerate(("1", "2", "3", "4", "5", "6", "11", "12"))}, "14": "+3V3", "7": "GND", "9": "NC", "10": "NC", "13": "NC",
           "8": f"HIT_{'LO' if base == 0 else 'HI'}"}, mpn="74HC30PW")
s.put(G32, "U1009", "SN74LVC1G32DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"1": "HIT_LO", "2": "HIT_HI", "5": "+3V3", "3": "GND", "4": "HIT_ANY"}, mpn="SN74LVC1G32DBVR")
s.put(G04, "U1010", "SN74LVC1G04DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "CS_Y3", "1": "NC", "5": "+3V3", "3": "GND", "4": "PK_RST"}, mpn="SN74LVC1G04DBVR")
s.put(G02, "U1011", "SN74LVC1G02DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"1": "CS_Y4", "2": "TEST_EN_N", "5": "+3V3", "3": "GND", "4": "TEST_STEP"}, mpn="SN74LVC1G02DBVR")
s.newcol()
s.R("R1001", "47R", "ADC_BUF", "ADC_IN")
s.C("C1001", "1nF C0G", "ADC_IN", "GND")
s.R("R1002", "100k", "TEST_STEP", "TEST_INJ")
s.R("R1003", "100R", "TEST_INJ", "GND")
s.R("R1004", "10k", "+3V3", "MCP_RST")
s.C("C1002", "100nF", "MCP_RST", "GND")
s.R("R1005", "10k", "+3V3", "TEST_EN_N")
s.R("R1006", "100k", "PK_RST", "GND")
s.newcol()
for k in range(9):
    s.C(f"C{1003 + k}", "100nF", "+3V3", "GND", fp=C0402)
for k, n in enumerate(("HIT_ANY", "MUX_D", "TEST_INJ")):
    s.put("Connector:TestPoint", f"TP{1001 + k}", n, TP_FP, {"1": n})
sheets.append(s)

# ------------------------------------------------------------------ bias, soglia, temperatura
s = PS("Bias", "bias.kicad_sch", 0, "4")
s.text("BIAS: DAC61402 OUTA (V_BIAS nominale ${VBIAS}) -> shunt 10k (INA239, 125 pA/LSB) -> VBIAS_SH -> 16 filtri RC per diodo (1k + 100 nF C0G nei fogli dei canali).", 25.4, 15.24)
s.text("SOGLIA: OUTB in range 0-5 V -> partitore 22k/10k -> VTH (0-1.56 V, ~0.4 mV/LSB), unica per il piano. TMP117 da piazzare al centro della matrice (lato sensori).", 25.4, 20.32)
s.put(DAC, "U1101", "DAC61402RHBR", "MIKILAB_DAC61402RHBR:VQFN32_RHB_TEX",
      {"28": "AVDD_DAC", "30": "+5V", "15": "+3V3", "26": "DAC_REF", "25": "GND", "27": "GND", "29": "GND", "14": "GND", "33": "GND",
       "12": "CS_DAC", "10": "SCLK_L", "11": "MOSI_L", "9": "MISO_L", "13": "GND", "16": "+3V3", "32": "+3V3", "31": "PL_FAULT",
       "8": "DAC_OUTA", "6": "DAC_OUTA", "5": "GND", "7": "CCOMPA", "17": "DAC_OUTB", "19": "DAC_OUTB", "20": "GND", "18": "CCOMPB"}, mpn="DAC61402RHBR")
s.put(INA239, "U1102", "INA239AIDGSR", "MIKILAB_INA239AIDGSR:VSSOP_9AIDGST_TEX",
      {"6": "+3V3", "7": "GND", "1": "CS_INA", "5": "SCLK_L", "2": "MOSI_L", "4": "MISO_L", "3": "PL_FAULT", "10": "DAC_OUTA", "9": "VBIAS_SH", "8": "VBIAS_SH"}, mpn="INA239AIDGSR")
s.put(TMP117, "U1103", "TMP117AIDRVR", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
      {"5": "+3V3", "2": "GND", "4": "GND", "7": "GND", "1": "I2C_SCL", "6": "I2C_SDA", "3": "PL_FAULT"}, mpn="TMP117AIDRVR")
s.newcol()
s.R("R1101", "100R", "VHV_36V", "AVDD_DAC", fp=R0805)
s.C("C1101", "1uF/100V", "AVDD_DAC", "GND", fp=C1206)
s.C("C1102", "1uF/100V", "AVDD_DAC", "GND", fp=C1206)
s.C("C1103", "100nF/100V", "AVDD_DAC", "GND", fp=C1206)
s.C("C1104", "470pF/100V", "CCOMPA", "DAC_OUTA", fp=C1206, dnp=True)
s.C("C1105", "470pF/100V", "CCOMPB", "DAC_OUTB", fp=C1206, dnp=True)
s.R("R1102", "10k 0.1%", "DAC_OUTA", "VBIAS_SH", fp=R0805, mpn="ERA-6ARB103V")
s.C("C1106", "100nF/100V C0G", "VBIAS_SH", "GND", fp=C1206, mpn=C0G1206)
s.newcol()
s.R("R1103", "22k", "DAC_OUTB", "VTH")
s.R("R1104", "10k", "VTH", "GND")
s.C("C1107", "100nF", "VTH", "GND")
s.put(BAT54S, "D1101", "BAT54S", "Package_TO_SOT_SMD:SOT-23", {"3": "VTH", "1": "GND", "2": "+3V3"}, mpn="BAT54S")
s.R("R1105", "10k", "+3V3", "PL_FAULT")
for k, n in enumerate(("VBIAS_SH", "VTH")):
    s.put("Connector:TestPoint", f"TP{1101 + k}", n, TP_FP, {"1": n})
s.newcol()
for k, n in enumerate(("+5V", "+3V3", "DAC_REF", "+3V3", "+3V3")):
    s.C(f"C{1108 + k}", "100nF", n, "GND")
sheets.append(s)

# ------------------------------------------------------------------ bus
s = PS("bus-pnp", "bus-pnp.kicad_sch", 0, "5")
s.text("BUS MIKILAB REV5.1 - MAIN 28 pin, come il PianoTest. Y0 ADC, Y1 DAC, Y2 INA, Y3 reset latch e picchi, Y4 gradino di test, Y5 mappa dei colpi (MCP), Y6 EEPROM ID, Y7 MCP di controllo.", 25.4, 15.24)
s.text("HIT# (pin 28): HIT_ANY -> monostabile 74LVC1G123 (2k + 27 pF, ~170-200 ns) -> 74LVC1G06 open-drain. ALERT#: INTA dell'MCP di controllo via 74LVC1G07.", 25.4, 20.32)
BUS = {1: "GND", 2: "+5V", 3: "+3V3", 4: "GND", 5: "2V5_REF", 6: "1V25_REF", 7: "GND_A", 8: "VHV_36V", 9: "VHV_36V_2", 10: "GND",
       11: "BUS_SCLK", 12: "BUS_MOSI", 13: "BUS_MISO", 14: "I2C_SDA", 15: "I2C_SCL", 16: "GND", 17: "BUS_CS_MASTER",
       18: "BUS_ADDR0", 19: "BUS_ADDR1", 20: "BUS_ADDR2", 21: "BUS_PREFIX0", 22: "BUS_PREFIX1", 23: "BUS_PREFIX2", 24: "BUS_ALERT_N",
       25: "ID_IN0", 26: "ID_IN1", 27: "ID_IN2", 28: "BUS_HIT_N"}
jin = {str(k): v for k, v in BUS.items()}
jin["MP"] = "GND"
jout = dict(jin)
jout.update({"25": "ID_OUT0", "26": "ID_OUT1", "27": "ID_OUT2"})
s.put("Connector_Generic_MountingPin:Conn_01x28_MountingPin", "J1201", "J_IN MAIN", FPC, jin, mpn="FPC-05F-28PH20")
s.put("Connector_Generic_MountingPin:Conn_01x28_MountingPin", "J1202", "J_OUT MAIN", FPC, jout, mpn="FPC-05F-28PH20")
s.newcol()
s.put(HC283, "U1201", "74HC283", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
      {"5": "ID_IN0", "3": "ID_IN1", "14": "ID_IN2", "12": "GND", "6": "GND", "2": "GND", "15": "GND", "11": "GND", "7": "+3V3",
       "16": "+3V3", "8": "GND", "4": "ID_OUT0", "1": "ID_OUT1", "13": "ID_OUT2", "10": "NC", "9": "NC"}, mpn="74HC283PW")
s.put(HC85, "U1202", "74HC85", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
      {"10": "BUS_PREFIX0", "12": "BUS_PREFIX1", "13": "BUS_PREFIX2", "15": "GND", "9": "ID_IN0", "11": "ID_IN1", "14": "ID_IN2", "1": "GND",
       "2": "GND", "3": "+3V3", "4": "GND", "16": "+3V3", "8": "GND", "5": "AGTB", "6": "PL_SEL", "7": "ALTB"}, mpn="74HC85PW")
s.put(HC138, "U1203", "74HC138", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
      {"1": "BUS_ADDR0", "2": "BUS_ADDR1", "3": "BUS_ADDR2", "4": "BUS_CS_MASTER", "5": "GND", "6": "PL_SEL", "16": "+3V3", "8": "GND",
       "15": "CS_ADC", "14": "CS_DAC", "13": "CS_INA", "12": "CS_Y3", "11": "CS_Y4", "10": "CS_HITMAP", "9": "CS_EEP", "7": "CS_MCP"}, mpn="74HC138PW")
s.newcol()
s.put(G17, "U1204", "SN74LVC2G17DBVR", "Package_TO_SOT_SMD:SOT-23-6", {"1": "BUS_SCLK", "3": "BUS_MOSI", "5": "+3V3", "2": "GND", "6": "SCLK_L", "4": "MOSI_L"}, mpn="SN74LVC2G17DBVR")
s.put(G125, "U1205", "SN74LVC1G125DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "MISO_L", "1": "MISO_OE_N", "5": "+3V3", "3": "GND", "4": "BUS_MISO"}, mpn="SN74LVC1G125DBVR")
s.put(G332, "U1206", "SN74LVC1G332DBVR", "Package_TO_SOT_SMD:SOT-23-6", {"1": "BUS_CS_MASTER", "3": "AGTB", "6": "ALTB", "5": "+3V3", "2": "GND", "4": "MISO_OE_N"}, mpn="SN74LVC1G332DBVR")
s.put(G07, "U1207", "SN74LVC1G07DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "MCP_INTA", "1": "NC", "5": "+3V3", "3": "GND", "4": "BUS_ALERT_N"}, mpn="SN74LVC1G07DBVR")
s.put(G123, "U1209", "SN74LVC1G123DCUR", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", {"1": "GND", "2": "HIT_ANY", "3": "+3V3", "8": "+3V3", "4": "GND", "5": "HIT_PULSE", "7": "MONO_RC", "6": "MONO_C"}, mpn="SN74LVC1G123DCUR")
s.put(G06, "U1210", "SN74LVC1G06DBVR", "Package_TO_SOT_SMD:SOT-23-5", {"2": "HIT_PULSE", "1": "NC", "5": "+3V3", "3": "GND", "4": "BUS_HIT_N"}, mpn="SN74LVC1G06DBVR")
s.put(EEP, "U1208", "25AA02E48T-I/SN", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
      {"1": "CS_EEP", "6": "SCLK_L", "5": "MOSI_L", "3": "+3V3", "7": "+3V3", "8": "+3V3", "4": "GND", "2": "MISO_L"}, mpn="25AA02E48T-I/SN")
s.newcol()
s.R("R1201", "0R", "GND_A", "GND")
s.R("R1202", "100k", "+3V3", "BUS_CS_MASTER")
s.R("R1203", "100k", "MISO_L", "GND")
for k in range(3):
    s.R(f"R{1204 + k}", "100k", f"ID_IN{k}", "GND")
s.R("R1207", "2k", "+3V3", "MONO_RC")
s.C("C1215", "27pF C0G", "MONO_RC", "MONO_C")
s.newcol()
for k in range(10):
    s.C(f"C{1201 + k}", "100nF", "+3V3", "GND")
s.C("C1211", "10uF", "+3V3", "GND", fp="Capacitor_SMD:C_0805_2012Metric")
s.C("C1212", "10uF", "+5V", "GND", fp="Capacitor_SMD:C_0805_2012Metric")
s.C("C1213", "100nF/100V", "VHV_36V", "GND", fp=C1206)
s.C("C1214", "100nF/100V", "VHV_36V_2", "GND", fp=C1206)
s.C("C1216", "1uF", "2V5_REF", "GND")
s.C("C1217", "1uF", "1V25_REF", "GND")
s.newcol()
ESD = ["BUS_SCLK", "BUS_MOSI", "BUS_MISO", "I2C_SDA", "I2C_SCL", "BUS_CS_MASTER", "BUS_ADDR0", "BUS_ADDR1", "BUS_ADDR2",
       "BUS_PREFIX0", "BUS_PREFIX1", "BUS_PREFIX2", "BUS_ALERT_N", "BUS_HIT_N", "ID_IN0", "ID_IN1", "ID_IN2", "ID_OUT0", "ID_OUT1", "ID_OUT2"]
for k, n in enumerate(ESD):
    if k == 10:
        s.newcol()
    s.put("Device:D_TVS", f"D{1201 + k}", "TPD1E10B06", "Diode_SMD:D_0402_1005Metric", {"1": n, "2": "GND"}, mpn="TPD1E10B06DPYR")
sheets.append(s)

# ------------------------------------------------------------------ scrittura
lib = "(kicad_symbol_lib (version 20251024) (generator \"gen_matrice\") " + " ".join(
    v.replace(f'(symbol "{LIB}:{k}"', f'(symbol "{k}"', 1) for k, v in SYMS.items()) + ")"
open(f"{PRJ}/PianoTest.kicad_sym", "w").write(lib)
open(f"{PRJ}/sym-lib-table", "w").write('(sym_lib_table (version 7) (lib (name "PianoTest") (type "KiCad") (uri "${KIPRJMOD}/PianoTest.kicad_sym") (options "") (descr "Simboli PianoTest/PianoMatrice")))\n')
open(f"{PRJ}/fp-lib-table", "w").write('(fp_lib_table (version 7) (lib (name "PianoMatrice") (type "KiCad") (uri "${KIPRJMOD}/PianoMatrice.pretty") (options "") (descr "Footprint PianoMatrice")))\n')
open(f"{PRJ}/PianoMatrice.kicad_sch", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{ROOT}") (paper "A3") (lib_symbols)\n'
    f'\t(text "PianoMatrice - piano MuonScope 4x4 VBPW34S (passo 10 mm) sul bus MIKILAB REV5.1. Variabili: RF=${{RF}}, CF=${{CF}}, VBIAS=${{VBIAS}}. Vedi README.md." (exclude_from_sim no) (at 25.4 20.32 0) {F.format(j="left bottom")} (uuid "{U()}"))\n'
    '\t(sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
for i, sh in enumerate(sheets):
    sh.write(PRJ, 25.4 + 60.96 * i, 200.66)

# foglio dei canali: file unico, 8 istanze con pin gerarchici
open(f"{PRJ}/{ch.fname}", "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{ch.uuid}") (paper "A2") '
    + "(lib_symbols " + " ".join(ch.syms.values()) + ") " + " ".join(ch.items) + " (embedded_fonts no))")
root = open(f"{PRJ}/PianoMatrice.kicad_sch").read()
blocks, extra = [], []
PINS = ("QA", "QB", "QNA", "QNB", "HOLDA", "HOLDB")
for k, u in enumerate(ch.inst):
    sx, sy = 25.4 + 96.52 * (k % 4), 40.64 + 63.5 * (k // 4)
    h = 5.08 + 2.54 * len(PINS)
    pl = []
    for j, pn in enumerate(PINS):
        py = sy + 2.54 * (j + 1)
        pl.append(f'(pin "{pn}" passive (at {sx + 40.64:.2f} {py:.2f} 0) (uuid "{U()}") {F.format(j="right")})')
        idx = 2 * k + (0 if pn.endswith("A") else 1)
        net = {"QA": "Q", "QB": "Q", "QNA": "QN", "QNB": "QN", "HOLDA": "HOLD", "HOLDB": "HOLD"}[pn] + str(idx)
        extra.append(f'(wire (pts (xy {sx + 40.64:.2f} {py:.2f}) (xy {sx + 45.72:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        extra.append(f'(global_label "{net}" (shape passive) (at {sx + 45.72:.2f} {py:.2f} 0) (fields_autoplaced yes) {F.format(j="left")} (uuid "{U()}"))')
    blocks.append(f'(sheet (at {sx:.2f} {sy:.2f}) (size 40.64 {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
                  f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{u}") '
                  f'(property "Sheetname" "Canali{2 * k:02d}-{2 * k + 1:02d}" (at {sx:.2f} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
                  f'(property "Sheetfile" "{ch.fname}" (at {sx:.2f} {sy + h + 0.58:.2f} 0) {F.format(j="left top")}) '
                  + " ".join(pl) + f' (instances (project "PianoMatrice" (path "/{ROOT}" (page "{2 + k}")))))')
k = root.rfind("\t(sheet_instances")
root = root[:k] + "\t" + "\n\t".join(blocks + extra) + "\n" + root[k:]
root = re.sub(r"\(size 50.8 5.08\)", "(size 50.8 15.24)", root)
for i, sh in enumerate(sheets):        # pagine dopo gli 8 fogli dei canali
    root = root.replace(f'(page "{sh.page}")', f'(page "{10 + i}")', 1)
open(f"{PRJ}/PianoMatrice.kicad_sch", "w").write(root)
print("ok", len(ch.items), [len(sh.items) for sh in sheets])
