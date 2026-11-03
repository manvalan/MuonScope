"""Schema della scheda iMX6 ricostruito da nanoberry (github.com/EnzoRF/nanoberry, GPLv3) con le modifiche di Michele.

KiCad 10 non legge i fogli KiCad 5 di nanoberry da riga di comando, quindi lo schema viene rigenerato dalla netlist originale
(nanoberry-originale/nano.net) e dai simboli della sua cache (convertiti con kicad-cli sym upgrade). Poi si applicano le modifiche:
- via display (P2), touch (J6), header di espansione P1, hub USB2514B con le due USB-A, CP2102N con la micro-USB di debug;
- DDR3L da 1 GB (AS4C512M16D3LC, 8 Gb x16, A15 gia' sbrogliata in nanoberry);
- USB-C 1 alimentazione + OTG1, USB-C 2 host su USB_OTG2 con TPS2553, console su header UART1;
- bus MIKILAB: BUS_POWER 30 pin (12 V -> TPS56637 -> TPS2121 con la USB-C 1 -> 5 V) e MAIN 28 pin;
- Wi-Fi/BT BL-M8723DS1 su uSDHC2 (pad CSI) e UART2.
Uso: python3 converti.py <cartella libreria convertita> ../progetto-kicad
"""
import json
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
import netlist
from kisheet import Sheet, box_symbol, SHEETS, F, U, G
from kilib import LIBNAME, PROJ, ROOT_UUID, block, pins_by_unit

CONV, PRJ = sys.argv[1], sys.argv[2]
ORIG = os.path.join(SC, "..", "nanoberry-originale")

# ---------------- netlist di nanoberry ------------------------------------------------------------------------------------
root = netlist.sexpr(open(os.path.join(ORIG, "nano.net")).read())
FN, V = netlist.find, netlist.val
COMP = {}
for c in FN(FN(root, "components")[0], "comp"):
    ls = FN(c, "libsource")[0]
    COMP[V(c, "ref")] = dict(value=V(c, "value"), fp=V(c, "footprint"), sym=f'{V(ls, "lib")}_{V(ls, "part")}', sheet=V(FN(c, "sheetpath")[0], "names").strip("/"))
PIN = {}                                      # (ref, pin) -> net
for n in FN(FN(root, "nets")[0], "net"):
    name = V(n, "name").split("/")[-1]
    if name.startswith("Net-("):
        name = "N_" + re.sub(r"[^A-Za-z0-9]+", "_", name[5:-1]).strip("_")
    name = name.replace(" ", "_").replace("+", "P").replace("-", "_N") if name.endswith(("+", "-")) else name.replace(" ", "_")
    for x in FN(n, "node"):
        PIN[(V(x, "ref"), V(x, "pin"))] = name
CACHE = open(os.path.join(CONV, "nano-cache.kicad_sym")).read()

# ---------------- modifiche ----------------------------------------------------------------------------------------------
TOLTI = {"P2", "J6", "P1", "U8", "U10", "U11", "P4", "P5", "XTAL1", "U9", "J3", "D4", "D5", "D7", "F1", "D6", "J4", "SB5", "SB6"}
RAILS = {"GND", "5V", "DCDC_3V3", "VSYS", "VBATT", "DRAM_1V35", "VDD_SNVS", "VDD_HIGH_IN", "VDD_SOC_IN", "NVCC_SD", "NVCC_CSI", "VIN_SYS", "VBUS1", "VBUS2", "3V3_WIFI", "5V_BUCK"}
for r in TOLTI:
    COMP.pop(r)
BALL = {k: v["name"] for k, v in json.load(open(os.path.join(SC, "..", "..", "SchedaIMX6ULL-SD", "generatori", "imx6ull_balls.json"))).items()}
BYNAME = {v: k for k, v in BALL.items()}


def soc(ball_name, net):
    PIN[("U1", BYNAME[ball_name])] = net


# sfere del 6ULL liberate (display, touch, espansione, hub, CP2102N): si riassegnano; le non usate restano libere
for b, nm in BALL.items():
    n = PIN.get(("U1", b), "")
    if nm.startswith("LCD_") or n.startswith(("TOUCH_", "CSI_", "UART2_", "UART3_", "UART4_", "UART5_", "DBG_", "HUB_")) or n in ("SNVS0", "SNVS1", "SNVS3", "SNVS4"):
        PIN[("U1", b)] = "NC"
ASSEGNA = {
    # BUS_POWER su ECSPI4 (pad ENET2, ex touch), CS extra su GPIO
    "ENET2_TX_DATA1": "PWR_SPI_SCLK_S", "ENET2_TX_EN": "PWR_SPI_MOSI", "ENET2_TX_CLK": "PWR_SPI_MISO", "ENET2_RX_ER": "PWR_SPI_INA239A_CS",
    "ENET2_TX_DATA0": "PWR_SPI_INA239B_CS", "ENET2_RX_EN": "PWR_SPI_DAC_CS",
    # MAIN su ECSPI1 (pad CSI_DATA04-07), I2C del bus su I2C1 (pad UART4)
    "CSI_DATA04": "MAIN_SPI_SCLK_S", "CSI_DATA05": "MAIN_SPI_CS_MASTER", "CSI_DATA06": "MAIN_SPI_MOSI", "CSI_DATA07": "MAIN_SPI_MISO",
    "UART4_TX_DATA": "MAIN_I2C_SCL", "UART4_RX_DATA": "MAIN_I2C_SDA",
    "UART3_TX_DATA": "MAIN_SPI_ADDR_0", "UART3_RX_DATA": "MAIN_SPI_ADDR_1", "UART3_RTS_B": "MAIN_SPI_ADDR_2",
    "UART3_CTS_B": "MAIN_SPI_PREFIX_0", "UART5_TX_DATA": "MAIN_SPI_PREFIX_1", "UART5_RX_DATA": "MAIN_SPI_PREFIX_2",
    "CSI_PIXCLK": "MAIN_SPI_ALERT_N", "CSI_MCLK": "MAIN_HIT_N",
    # linee lente del BUS_POWER su pad LCD che non sono strap di boot
    "LCD_CLK": "VREF_ENABLE", "LCD_ENABLE": "VBIAS_ENABLE", "LCD_HSYNC": "DAC61402_FAULT",
    # Wi-Fi su uSDHC2 (pad CSI), BT su UART2
    "CSI_VSYNC": "SD2_CLK_S", "CSI_HSYNC": "SD2_CMD", "CSI_DATA00": "SD2_D0", "CSI_DATA01": "SD2_D1", "CSI_DATA02": "SD2_D2", "CSI_DATA03": "SD2_D3",
    "UART2_TX_DATA": "BT_UART_RX", "UART2_RX_DATA": "BT_UART_TX", "UART2_RTS_B": "BT_UART_CTS", "UART2_CTS_B": "WL_WAKE_HOST",
    "LCD_VSYNC": "WL_DIS_N", "LCD_RESET": "BT_DIS_N", "SNVS_TAMPER3": "BT_HOST_WAKE",
    # console UART1 su header, USB host su USB_OTG2 con load switch
    "UART1_TX_DATA": "UART1_TX", "UART1_RX_DATA": "UART1_RX",
    "USB_OTG2_DP": "USB2_DP", "USB_OTG2_DN": "USB2_DM", "GPIO1_IO04": "USB2_VBUS_EN", "SNVS_TAMPER6": "USB2_OC_N",
}
for bn, net in ASSEGNA.items():
    soc(bn, net)
# GPIO1_IO00/01/02/05 e UART1_CTS/RTS erano del CP2102N: liberi
PIN = {k: v for k, v in PIN.items() if v != "NC"}
# rimappa le net residue del CP2102N e dell'hub
for k, v in list(PIN.items()):
    if v in ("DBG_RXD", "DBG_TXD"):
        PIN[k] = {"DBG_RXD": "UART1_TX", "DBG_TXD": "UART1_RX"}[v]
# OTG: la USB-C 1 prende il posto di J4, il polyfuse F2 va all'ingresso IN2 del mux al posto del diodo D6
for k, v in list(PIN.items()):
    if v == "N_D6_Pad2":
        PIN[k] = "VBUS1"
    if v in ("OTG_D_N", "OTG_DP", "OTG_D_P") or v.startswith("OTG_D"):
        PIN[k] = "USB1_DM" if v.endswith(("N", "-")) else "USB1_DP"
APPESI = []
# passivi rimasti appesi: tolti se una loro net (non di alimentazione) non tocca piu' nessun componente attivo
ATTIVO = lambda r: not re.match(r"(R|C|L|FB|SB)\d", r)
while True:
    nets = {}
    for (r, p), n in PIN.items():
        if r in COMP:
            nets.setdefault(n, set()).add(r)
    via = [r for r in COMP if not ATTIVO(r) and any(n not in RAILS and not any(ATTIVO(o) for o in nets[n] - {r}) and len(nets[n] - {r}) < 2
                                                     for (rr, p), n in PIN.items() if rr == r)]
    if not via:
        break
    for r in via:
        COMP.pop(r)
        APPESI.append(r)
PIN = {k: v for k, v in PIN.items() if k[0] in COMP}
# net con un solo pin gia' in nanoberry (pin lasciati liberi senza flag): flag no connect
_cnt = {}
for v in PIN.values():
    _cnt[v] = _cnt.get(v, 0) + 1
SINGOLI = sorted(n for n, c in _cnt.items() if c == 1 and (n.startswith("N_") or n in ("BOOST_EN", "SNVS8")))
PIN = {k: v for k, v in PIN.items() if v not in SINGOLI}

print("tolti:", sorted(TOLTI), "passivi rimasti appesi e tolti:", sorted(APPESI))
COMP["U2"]["value"] = "AS4C512M16D3LC-12BIN"

# ---------------- simboli ----------------------------------------------------------------------------------------------------


def from_cache(name):
    i = CACHE.find(f'(symbol "{name}"\n')
    if i < 0:
        i = CACHE.find(f'(symbol "{name}"')
    s = block(CACHE, i)
    # i pin nascosti di alimentazione dei simboli KiCad 5 collegherebbero net per nome: qui tutti i pin sono visibili e collegati a mano
    s = re.sub(r"(\(pin \w+ \w+[^()]*?)\(hide yes\)", r"\1", s)
    s = re.sub(r"\(pin (\w+) (\w+)\s*\(at ([^)]*)\)\s*\(length ([^)]*)\)\s*\(hide yes\)", r"(pin \1 \2 (at \3) (length \4)", s)
    # tipi dei pin di nanoberry: molti segnali bidirezionali (DRAM, ENET, NAND) sono marcati "input"; qui diventano passivi
    s = s.replace("(pin input ", "(pin passive ")
    return s.replace(f'(symbol "{name}"', f'(symbol "{LIBNAME}:{name}"', 1)


SHEETNAME = {"DDR": "DDR3L", "IMX_Power_Pins": "SoC alimentazioni", "IMX_Peripherals_1": "SoC periferiche 1", "IMX_Peripherals_2": "SoC periferiche 2",
             "PMIC PF1550": "PMIC PF1550", "ETHERNET": "Ethernet", "USB DEBUG & OTG": "Boost batteria", "Clock_and_Control": "Clock e controllo"}
FNAME = {"DDR": "ddr.kicad_sch", "IMX_Power_Pins": "soc-alimentazioni.kicad_sch", "IMX_Peripherals_1": "soc-periferiche-1.kicad_sch",
         "IMX_Peripherals_2": "soc-periferiche-2.kicad_sch", "PMIC PF1550": "pmic.kicad_sch", "ETHERNET": "ethernet.kicad_sch",
         "USB DEBUG & OTG": "boost.kicad_sch", "Clock_and_Control": "clock.kicad_sch"}
sheets = {}
order = list(FNAME)
for i, key in enumerate(order):
    sheets[key] = Sheet(SHEETNAME[key], FNAME[key], 0, i + 2, paper="A1")


def place_units(sh, lib_id, text, ref, val, fp, nets, mpn=None):
    """Tutte le unita' di un simbolo: ogni pin con il suo moncone e la sua etichetta (pin senza net: flag no connect)."""
    sh.add_sym(lib_id, text)
    units = pins_by_unit(text)
    for u, pl in sorted(units.items()):
        xs, ys = [p[2] for p in pl], [p[3] for p in pl]
        w, h = (max(xs) - min(xs)) + 60, (max(ys) - min(ys)) + 30
        x0, y0 = sh._slot(w, h)
        x, y = G(x0 + 30 - min(xs)), G(y0 + 15 + max(ys))
        seen = set()
        for num, nm, px, py, a in pl:
            ax, ay = round(x + px, 2), round(y - py, 2)
            if (ax, ay) in seen:
                continue
            seen.add((ax, ay))
            sh.stub(ax, ay, a, nets.get(num, "NC"), L=5.08 if nets.get(num, "NC") != "NC" else 2.54)
        props = f' (property "MPN" "{mpn}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))' if mpn else ""
        allp = " ".join(f'(pin "{p[0]}" (uuid "{U()}"))' for p in pl)
        sh.items.append(
            f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit {u}) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (uuid "{U()}") '
            f'(property "Reference" "{ref}" (at {x - 7.62:.2f} {y - max(ys) - 7.62:.2f} 0) {F.format(j="left")}) '
            f'(property "Value" "{val}" (at {x - 7.62:.2f} {y - max(ys) - 5.08:.2f} 0) {F.format(j="left")}) '
            f'(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
            + allp + f' (instances (project "{PROJ}" (path "{sh.path}" (reference "{ref}") (unit {u})))))')


# componenti di nanoberry, foglio per foglio, nello stesso ordine della netlist (le grandi prima)
for ref in sorted(COMP, key=lambda r: (not ATTIVO(r), re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0))):
    c = COMP[ref]
    if c["sheet"] not in sheets:
        continue
    nets = {p: n for (r, p), n in PIN.items() if r == ref}
    place_units(sheets[c["sheet"]], f'{LIBNAME}:{c["sym"]}', from_cache(c["sym"]), ref, c["value"], c["fp"], nets)
sheets["DDR"].note("U2 DDR3L 8 Gb x16 = 1 GB: Alliance AS4C512M16D3LC-12BIN, FBGA-96 9x13 mm, stessa griglia JEDEC della W634GU6MB di nanoberry. A15 (M7) era gia' collegata e sbrogliata.")

# ---------------- nuovi fogli ----------------------------------------------------------------------------------------------
NEXT = {"R": 200, "C": 200, "U": 12, "J": 7, "D": 7, "L": 10}


def nuovo(prefix):
    NEXT[prefix] += 1
    return f"{prefix}{NEXT[prefix]}"


class S2(Sheet):
    def group(self, title, parts, cols=16):
        refs = []
        for p in parts:
            refs.append(nuovo(p[0]))
        self._refs = iter(refs)
        return super().group(title, parts, cols)

    def _next(self, prefix):
        return next(self._refs)


GND, V5, V33 = "GND", "5V", "DCDC_3V3"
# --- alimentazione dal bus e USB-C 1
p = S2("Alimentazione bus e USB-C", "alimentazione-bus.kicad_sch", 0, len(order) + 2)
p.note("VIN_SYS 12 V dal BUS_POWER -> TPS56637 5 V -> TPS2121 IN1 (priorita'). IN2 = VBUS della USB-C 1 (dopo il polyfuse F2 di nanoberry). Uscita -> 5V di nanoberry (VBUSIN del PF1550).")
p.note("Il boost MIC2877 di nanoberry resta sul 5V (alimentazione da LiPo): il TPS2121 blocca la corrente inversa. Circuiti come sulle schede MIKILAB (SchedaIMX6ULL-SD).")
B, BF = p.mik("TPS56637RPAR")
p.std("Device:L")
U_BUCK = nuovo("U")
p.ic(B, U_BUCK, "TPS56637RPAR", BF, {"8": "VIN_SYS", "1": "BUCK_EN", "2": "BUCK_FB", "10": "NC", "4": "BUCK_PG", "5": "NC", "7": "BUCK_BST", "6": "BUCK_SW", "3": GND, "9": GND}, mpn="TPS56637RPAR", lcsc="C841386")
L_BUCK = nuovo("L")
p.ic("Device:L", L_BUCK, "3.3uH/8A", "Inductor_SMD:L_Coilcraft_XAL6030-XXX", {"1": "BUCK_SW", "2": "5V_BUCK"}, mpn="XAL6030-332MEC")
p.group("TPS56637: EN 169k/36.1k, FB 73.2k/10k = 4.99 V, FF 20k + 100 pF", [
    ("C", "10uF/25V", "VIN_SYS", GND), ("C", "10uF/25V", "VIN_SYS", GND), ("C", "100nF/50V", "VIN_SYS", GND), ("R", "169k 1%", "VIN_SYS", "BUCK_EN"), ("R", "36.1k 1%", "BUCK_EN", GND),
    ("R", "100k", "5V_BUCK", "BUCK_PG"), ("C", "100nF", "BUCK_BST", "BUCK_SW"), ("R", "73.2k 1%", "5V_BUCK", "BUCK_FB"), ("R", "10k 1%", "BUCK_FB", GND),
    ("R", "20k", "5V_BUCK", "BUCK_FF"), ("C", "100pF", "BUCK_FF", "BUCK_FB"), ("C", "47uF/10V", "5V_BUCK", GND), ("C", "47uF/10V", "5V_BUCK", GND)])
M, MF = p.mik("TPS2121RUXR")
U_MUX = nuovo("U")
p.ic(M, U_MUX, "TPS2121RUXR", MF, {"7": "5V_BUCK", "6": "MUX_PR1", "5": "MUX_OV1", "2": "VBUS1", "4": "MUX_OV2", "3": GND, "1": V5, "8": V5, "9": "PWR_SRC_ST", "10": "MUX_ILM", "11": "MUX_SS", "12": GND},
     mpn="TPS2121RUXR", lcsc="C485916")
p.group("TPS2121: PR1 4.49 V, OV 5.98 V, ILM 22.1k, SS 100 nF; PWR_SRC_ST con 10k", [
    ("R", "32.4k 1%", "5V_BUCK", "MUX_PR1"), ("R", "10k 1%", "MUX_PR1", GND), ("R", "46.4k 1%", "5V_BUCK", "MUX_OV1"), ("R", "10k 1%", "MUX_OV1", GND), ("R", "46.4k 1%", "VBUS1", "MUX_OV2"), ("R", "10k 1%", "MUX_OV2", GND),
    ("R", "22.1k 1%", "MUX_ILM", GND), ("C", "100nF", "MUX_SS", GND), ("C", "1uF/10V", "5V_BUCK", GND), ("C", "1uF/10V", "VBUS1", GND), ("C", "47uF/10V", V5, GND), ("R", "10k", V33, "PWR_SRC_ST")])
UC, UCF = p.mik("TYPE-C-31-M-12")
J_C1 = nuovo("J")
p.ic(UC, J_C1, "TYPE-C-31-M-12", UCF, {"VBUS": "OTG_VBUS", "CC1": "USB1_CC1", "CC2": "USB1_CC2", "DP1": "USB1_DP", "DP2": "USB1_DP", "DN1": "USB1_DM", "DN2": "USB1_DM", "SBU1": "NC", "SBU2": "NC", "GND": GND, "EH": GND},
     mpn="TYPE-C-31-M-12", lcsc="C165948")
p.std("Power_Protection:USBLC6-2SC6"), p.std("Device:D_TVS")
p.ic("Power_Protection:USBLC6-2SC6", nuovo("U"), "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", {"1": "USB1_DP", "6": "USB1_DP", "3": "USB1_DM", "4": "USB1_DM", "5": "OTG_VBUS", "2": GND}, mpn="USBLC6-2SC6", lcsc="C7519")
p.ic("Device:D_TVS", nuovo("D"), "SMF5.0A", "Diode_SMD:D_SMF", {"1": "OTG_VBUS", "2": GND}, mpn="SMF5.0A", lcsc="C151296")
p.group("USB-C 1: sink 5.1k su CC1/CC2", [("R", "5.1k", "USB1_CC1", GND), ("R", "5.1k", "USB1_CC2", GND)])

# --- USB-C 2 host e console
u = S2("USB host e console", "usb-host.kicad_sch", 0, len(order) + 3)
u.note("USB-C 2 host su USB_OTG2 (ex hub), affiancata alla USB-C 1. VBUS dal TPS2553 (~1 A, RILIM 26.1k), EN su GPIO1_IO04 con 100k a GND, FAULT su SNVS_TAMPER6 con 10k. Rp 56k su CC (sorgente default).")
u.note("Console Linux su UART1 (al posto del CP2102N di nanoberry): header 1x3 TX, RX, GND a 3.3 V.")
J_C2 = nuovo("J")
u.mik("TYPE-C-31-M-12")
u.ic(UC, J_C2, "TYPE-C-31-M-12", UCF, {"VBUS": "VBUS2", "CC1": "USB2_CC1", "CC2": "USB2_CC2", "DP1": "USB2_DP", "DP2": "USB2_DP", "DN1": "USB2_DM", "DN2": "USB2_DM", "SBU1": "NC", "SBU2": "NC", "GND": GND, "EH": GND},
     mpn="TYPE-C-31-M-12", lcsc="C165948")
SW, SWF = u.mik("TPS2553DBVR")
u.ic(SW, nuovo("U"), "TPS2553DBVR", SWF, {"1": V5, "2": GND, "3": "USB2_VBUS_EN", "4": "USB2_OC_N", "5": "USB2_ILIM", "6": "VBUS2"}, mpn="TPS2553DBVR", lcsc="C55266")
u.std("Power_Protection:USBLC6-2SC6")
u.ic("Power_Protection:USBLC6-2SC6", nuovo("U"), "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", {"1": "USB2_DP", "6": "USB2_DP", "3": "USB2_DM", "4": "USB2_DM", "5": "VBUS2", "2": GND}, mpn="USBLC6-2SC6", lcsc="C7519")
u.group("USB-C 2 host", [("R", "56k", V5, "USB2_CC1"), ("R", "56k", V5, "USB2_CC2"), ("R", "26.1k 1%", "USB2_ILIM", GND), ("R", "100k", "USB2_VBUS_EN", GND), ("R", "10k", V33, "USB2_OC_N"),
                         ("C", "1uF", V5, GND), ("C", "47uF/10V", "VBUS2", GND), ("C", "100nF", "VBUS2", GND)])
u.std("Connector_Generic:Conn_01x03")
u.ic("Connector_Generic:Conn_01x03", nuovo("J"), "Console UART1", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", {"1": "UART1_TX", "2": "UART1_RX", "3": GND}, mpn="2.54-1*3P", lcsc="C49257")

# --- bus MIKILAB
b = S2("Bus MIKILAB", "bus-mikilab.kicad_sch", 0, len(order) + 4)
b.note("J BUS_POWER 30 pin (Hirose FH12-30S) su ECSPI4 (pad ENET2, ex touch), J MAIN 28 pin REV5.1 (XUNPU FPC-05F-28PH20) su ECSPI1 (pad CSI_DATA04-07, ex espansione P1). Mappa dei connettori come SchedaIMX6ULL-SD.")
b.note("Serie 33R sui clock SPI. Pull-up 4.7k su ALERT#/HIT#, 2.2k su I2C. VREF_ENABLE 10k e VBIAS_ENABLE 100k a GND. CS e FAULT con i pull-up interni del 6ULL. ESD TPD4E05U06DQA sulle linee logiche.")
MAIN = {1: GND, 2: "BUS_5V", 3: "BUS_3V3", 4: GND, 5: "BUS_2V5_REF", 6: "BUS_1V25_REF", 7: "GND_A", 8: "BUS_VBIAS_1", 9: "BUS_VBIAS_2", 10: GND, 11: "MAIN_SPI_SCLK", 12: "MAIN_SPI_MOSI",
        13: "MAIN_SPI_MISO", 14: "MAIN_I2C_SDA", 15: "MAIN_I2C_SCL", 16: GND, 17: "MAIN_SPI_CS_MASTER", 18: "MAIN_SPI_ADDR_0", 19: "MAIN_SPI_ADDR_1", 20: "MAIN_SPI_ADDR_2", 21: "MAIN_SPI_PREFIX_0",
        22: "MAIN_SPI_PREFIX_1", 23: "MAIN_SPI_PREFIX_2", 24: "MAIN_SPI_ALERT_N", 25: GND, 26: GND, 27: GND, 28: "MAIN_HIT_N"}
PWR = {1: "GND_A", 2: "BUS_VBIAS_1", 3: "BUS_VBIAS_2", 4: "GND_A", 5: "BUS_2V5_REF", 6: "BUS_1V25_REF", 7: "GND_A", 8: "BUS_5V", 9: "BUS_3V3", 10: GND, 11: "PWR_SPI_SCLK", 12: "PWR_SPI_MOSI",
       13: "PWR_SPI_MISO", 14: GND, 15: "PWR_SPI_INA239A_CS", 16: "PWR_SPI_INA239B_CS", 17: "PWR_SPI_DAC_CS", 18: "VREF_ENABLE", 19: "VBIAS_ENABLE", 20: "DAC61402_FAULT", 21: GND,
       22: GND, 23: GND, 24: "VIN_SYS", 25: "VIN_SYS", 26: "VIN_SYS", 27: GND, 28: GND, 29: "BUS_3V3", 30: GND}
FH, FHF = b.mik("FH12-30S-0.5SH")
FP_, FPF = b.mik("FPC-05F-28PH20")
J_PWR, J_MAIN = nuovo("J"), nuovo("J")
b.ic(FH, J_PWR, "BUS_POWER_MIKILAB", FHF, {str(k): PWR.get(k, GND) for k in range(1, 40)}, mpn="FH12-30S-0.5SH", lcsc="C506793")
b.ic(FP_, J_MAIN, "BUS_MIKILAB_MAIN", FPF, {str(k): MAIN.get(k, GND) for k in range(1, 40)}, mpn="FPC-05F-28PH20", lcsc="C2856807")
b.group("Serie SPI 33R, solo clock", [("R", "33R", "PWR_SPI_SCLK_S", "PWR_SPI_SCLK"), ("R", "33R", "MAIN_SPI_SCLK_S", "MAIN_SPI_SCLK")])
b.group("Livelli di riposo", [("R", "10k", "VREF_ENABLE", GND), ("R", "100k", "VBIAS_ENABLE", GND), ("R", "4.7k", V33, "MAIN_SPI_ALERT_N"), ("R", "4.7k", V33, "MAIN_HIT_N"),
                              ("R", "2.2k", V33, "MAIN_I2C_SCL"), ("R", "2.2k", V33, "MAIN_I2C_SDA")])
BUSNETS = ["PWR_SPI_SCLK", "PWR_SPI_MOSI", "PWR_SPI_MISO", "PWR_SPI_INA239A_CS", "PWR_SPI_INA239B_CS", "PWR_SPI_DAC_CS", "VREF_ENABLE", "VBIAS_ENABLE", "DAC61402_FAULT", "MAIN_SPI_SCLK", "MAIN_SPI_MOSI", "MAIN_SPI_MISO",
           "MAIN_I2C_SDA", "MAIN_I2C_SCL", "MAIN_SPI_CS_MASTER", "MAIN_SPI_ADDR_0", "MAIN_SPI_ADDR_1", "MAIN_SPI_ADDR_2", "MAIN_SPI_PREFIX_0", "MAIN_SPI_PREFIX_1", "MAIN_SPI_PREFIX_2", "MAIN_SPI_ALERT_N", "MAIN_HIT_N"]
b.std("Power_Protection:TPD4E05U06DQA")
for k in range(6):
    g_ = BUSNETS[4 * k: 4 * k + 4]
    b.ic("Power_Protection:TPD4E05U06DQA", nuovo("U"), "TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
         {"1": g_[0], "2": g_[1], "4": g_[2] if len(g_) > 2 else "NC", "5": g_[3] if len(g_) > 3 else "NC", "3": GND, "8": GND}, mpn="TPD4E05U06DQAR")
b.group("Disaccoppiamento", [("C", "100nF", "VIN_SYS", GND)])
b.flags(["GND_A", "BUS_3V3", "BUS_5V", "VIN_SYS"])  # #FLG50-53

# --- Wi-Fi/BT
w = S2("Radio", "radio.kicad_sch", 0, len(order) + 5)
w.note("BL-M8723DS1 (RTL8723DS) su uSDHC2 sui pad CSI (VSYNC = CLK, HSYNC = CMD, DATA00-03), libero perche' il boot e' da QSPI; BT su UART2 (TX, RX, RTS -> CTS del modulo). SDIO con i pull-up interni del 6ULL.")
w.note("Alimentazione 3.3 V dedicata (AP2112K da 5V). WL_DIS# e BT_DIS# con 10k a GND. Antenna su U.FL con rete pi 0R + 2 DNP. Footprint LGA-44 dal datasheet LB-LINK V1.0.1.3.")
WN = {1: "GND", 2: "ANT", 3: "GND", 6: "BT_HOST_WAKE", 7: "BT_WAKE_HOST", 9: "VDD33", 12: "WL_DIS_N", 13: "WL_WAKE_HOST", 14: "SD_D2", 15: "SD_D3", 16: "SD_CMD", 17: "SD_CLK", 18: "SD_D0", 19: "SD_D1", 20: "GND", 22: "VDIO", 24: "GPIO8", 25: "PCM_OUT", 26: "PCM_CLK", 27: "PCM_IN", 28: "PCM_SYNC",
      31: "GND", 33: "GND", 34: "BT_DIS_N", 36: "GND", 41: "GND", 42: "UART_TX", 43: "UART_RX", 44: "UART_CTS"}
w.add_sym(f"{LIBNAME}:BL-M8723DS1", box_symbol(LIBNAME, "BL-M8723DS1", [(str(k), WN.get(k, f"NC{k}"), "L" if k <= 22 else "R") for k in range(1, 45)], "LB-LINK BL-M8723DS1 Wi-Fi 802.11n + BT 4.2"))
w.ic(f"{LIBNAME}:BL-M8723DS1", nuovo("U"), "BL-M8723DS1", f"{LIBNAME}:LB-LINK_BL-M8723DS1_LGA-44_12x12mm",
     {"GND": GND, "ANT": "WL_ANT", "BT_HOST_WAKE": "BT_HOST_WAKE", "VDD33": "3V3_WIFI", "VDIO": "3V3_WIFI", "WL_DIS_N": "WL_DIS_N", "WL_WAKE_HOST": "WL_WAKE_HOST", "SD_D0": "SD2_D0", "SD_D1": "SD2_D1", "SD_D2": "SD2_D2", "SD_D3": "SD2_D3",
      "SD_CMD": "SD2_CMD", "SD_CLK": "SD2_CLK", "BT_DIS_N": "BT_DIS_N", "UART_TX": "BT_UART_TX", "UART_RX": "BT_UART_RX", "UART_CTS": "BT_UART_CTS"}, mpn="BL-M8723DS1")
LD, LDF = w.mik("AP2112K-3.3TRG1")
w.ic(LD, nuovo("U"), "AP2112K-3.3TRG1", LDF, {"1": V5, "2": GND, "3": V5, "5": "3V3_WIFI"}, mpn="AP2112K-3.3TRG1", lcsc="C51118")
w.std("Connector:Conn_Coaxial")
w.ic("Connector:Conn_Coaxial", nuovo("J"), "U.FL", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", {"1": "WL_ANT_C", "2": GND})
w.group("Wi-Fi: 22R su CLK, enable a GND, rete pi", [("R", "22R", "SD2_CLK_S", "SD2_CLK"), ("R", "10k", "WL_DIS_N", GND), ("R", "10k", "BT_DIS_N", GND), ("R", "0R", "WL_ANT", "WL_ANT_C"),
                                                    ("C", "DNP", "WL_ANT", GND, True), ("C", "DNP", "WL_ANT_C", GND, True), ("C", "22uF/10V", "3V3_WIFI", GND), ("C", "100nF", "3V3_WIFI", GND), ("C", "1uF", V5, GND)])
w.std("power:PWR_FLAG")
w.place("power:PWR_FLAG", "#FLG090", "PWR_FLAG", "", 30, 200, {"1": "3V3_WIFI"}, inbom=False)

# PWR_FLAG sui rail generati dal PF1550 e dagli LDO (i simboli di nanoberry non hanno uscite di potenza su questi pin)
_flg = 0
for net in ("VDD_SOC_IN", "DRAM_1V35", "VDDA_ADC", "VDDOTP", "VCORE", "VDIG", "VBATT", "GND", "DCDC_3V3", "VSYS", "VDD_SNVS", "VDD_HIGH_IN", "NVCC_SD", "NVCC_CSI", "ETH_AVDD", "VDDCR", "5V", "DBG_VDD"):
    sh_ = next((s for s in SHEETS if net in s.nets), None)
    if sh_ is None:
        continue
    sh_.std("power:PWR_FLAG")
    x_, y_ = sh_._slot(12.7, 30)
    _flg += 1
    sh_.place("power:PWR_FLAG", f"#FLG{_flg:03d}", "PWR_FLAG", "", x_ + 6, y_ + 12, {"1": net}, inbom=False)
from kisheet import GROUPS
json.dump(GROUPS, open(os.path.join(SC, "gruppi.json"), "w"), indent=0, sort_keys=True)
# ---------------- scrittura ----------------------------------------------------------------------------------------------
used = {}
for s in SHEETS:
    for n, c in s.nets.items():
        used.setdefault(n, []).append((s.name, c))
single = sorted(n for n, v in used.items() if sum(c for _, c in v) == 1)
print("net con un solo collegamento:", single)
glob = {n for n, v in used.items() if len(v) > 1}
lib = ""
seen = set()
for s in SHEETS:
    for k, v in s.syms.items():
        if k.startswith(LIBNAME + ":") and k not in seen:
            seen.add(k)
            lib += " " + v.replace(f'(symbol "{k}"', f'(symbol "{k[len(LIBNAME) + 1:]}"', 1)
open(os.path.join(PRJ, f"{LIBNAME}.kicad_sym"), "w").write(f'(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0"){lib})')
blocks = []
for i, s in enumerate(SHEETS):
    s.write(PRJ, glob, set(), {})
    x, y = 30 + 70 * (i % 4), 40 + 30 * (i // 4)
    blocks.append(f'(sheet (at {x} {y}) (size 50.8 10.16) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
                  f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{s.uuid}") '
                  f'(property "Sheetname" "{s.name}" (at {x} {y - 0.71:.2f} 0) {F.format(j="left bottom")}) '
                  f'(property "Sheetfile" "{s.fname}" (at {x} {y + 10.74:.2f} 0) {F.format(j="left top")}) '
                  f'(instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "{s.page}")))))')
note = ("(text \"Scheda iMX6: derivata da nanoberry di vpecanins (github.com/EnzoRF/nanoberry), GPLv3. Modifiche: via display, touch, espansione, hub USB e CP2102N; "
        "DDR3L 1 GB; USB-C alimentazione/OTG + USB-C host; console su header; bus MIKILAB; Wi-Fi/BT. Alimentazioni e segnali tra fogli sono etichette globali.\" "
        f'(exclude_from_sim no) (at 30.00 25.00 0) {F.format(j="left bottom")} (uuid "{U()}"))')
open(os.path.join(PRJ, f"{PROJ}.kicad_sch"), "w").write(
    f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{ROOT_UUID}") (paper "A3") (lib_symbols) '
    + " ".join(blocks) + " " + note + ' (sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
print("fogli:", len(SHEETS), "componenti:", len(COMP) + sum(1 for s in SHEETS for it in s.items if isinstance(it, str) and it.startswith("(symbol (lib_id") and "(unit 1)" in it and "#FLG" not in it) - len(COMP))
