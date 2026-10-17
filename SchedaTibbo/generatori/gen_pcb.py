"""Crea SchedaTibbo.kicad_pcb dalla BOM (solo placement, niente piste e niente net: lo schema non esiste ancora).

Uso, con il Python di KiCad:
  python3 gen_pcb.py progetto-kicad   (Linux: python3 di sistema con pcbnew; macOS: python3 di KiCad.app)
Scheda 60 x 84 mm (50 x 70 non basta: vedi docs/pcb-placement.md), angoli raggiati 3 mm, 4 fori NPTH 2.2 mm con
keepout, 4 strati. Tutto sul top tranne la microSD J5 sul bottom. I componenti principali hanno una posizione fissa
(PLACE), gli integrati piccoli una zona preferita (MED); i passivi generici (circa 110, tutti 0603 o piu' grandi)
vengono messi in automatico vicino all'integrato del loro blocco.
"""
import json
import math
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
import pcbnew
from kilib import FPLIB, PROJ, LIBNAME, mik_fp_dir

PRJ = sys.argv[1]
OUT = os.path.join(PRJ, f"{PROJ}.kicad_pcb")
STD = FPLIB
W, H, RAD = 60.0, 84.0, 3.0          # scheda e raggio degli angoli
OX, OY = 100.0, 100.0                # origine dell'angolo in alto a sinistra
HOLES = [(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)]
HOLE_KEEP = 3.2                      # raggio del keepout attorno ai fori
mm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

# ---------------- componenti della BOM (bom-tibbo.csv) ---------------------------------------------------------------
# ref: (footprint, valore, MPN, LCSC)
C0603, C0805, C1206 = "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric", "Capacitor_SMD:C_1206_3216Metric"
R0603 = "Resistor_SMD:R_0603_1608Metric"
BOM = {
    "U1": (f"{LIBNAME}:LQFP-176-1EP_20x20mm_P0.4mm_EP10x10mm", "SP7021-IF", "SP7021-IF", ""),
    "Y1": ("Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "27MHz", "X322527MSB4SI", ""),
    "Y2": ("MIKILAB_Q13FC1350000400:FC-135R_L3.2-W1.5", "32.768kHz", "Q13FC13500004", "C32346"),
    "BT1": ("MIKILAB_CR1220_2:BAT-SMD_CR1220-2", "CR1220", "CR1220-2", "C70381"),
    "D4": ("Diode_SMD:D_SOD-323", "BAT54WS", "BAT54WS", ""),
    "U5": ("MIKILAB_FEMDNN064G_C9A61:BGA-153_L13.0-W11.5-P0.50-TL_FORESEE_FEMDME", "eMMC 8GB", "KLM8G1GETF-B041", "C499918"),   # FBGA-153 JEDEC, stesso footprint
    "U7": ("Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm", "LAN8720A", "LAN8720A-CP-TR", "C45223"),
    "Y3": ("MIKILAB_X322525MOB4SI:CRYSTAL-SMD_4P-L3.2-W2.5-BL", "25MHz", "X322525MOB4SI", "C9006"),
    "U6": ("Package_TO_SOT_SMD:SOT-23-5", "24AA02E48", "24AA02E48T-I/OT", "C38987"),
    "J1": ("Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal", "RJ45", "HR911105A", "C12074"),
    "J3": ("MIKILAB_TYPE_C_31_M_12:USB-C_SMD-TYPE-C-31-M-12_1", "USB-C OTG", "TYPE-C-31-M-12", "C165948"),
    "J8": ("MIKILAB_TYPE_C_31_M_12:USB-C_SMD-TYPE-C-31-M-12_1", "USB-C host", "TYPE-C-31-M-12", "C165948"),
    "U9": ("Package_TO_SOT_SMD:SOT-23-6", "USBLC6-2SC6", "USBLC6-2SC6", "C7519"),
    "U10": ("Package_TO_SOT_SMD:SOT-23-6", "USBLC6-2SC6", "USBLC6-2SC6", "C7519"),
    "U24": ("MIKILAB_TPS2553DBVR:TPS2553DBVR_SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR", "TPS2553", "TPS2553DBVR", "C55266"),
    "D1": ("MIKILAB_SMF5_0A:SOD-123F_L2.8-W1.8-LS3.7-RD", "SMF5.0A", "SMF5.0A", "C151296"),
    "U17": ("MIKILAB_TPS2121RUXR:IC_TPS2121RUXR", "TPS2121", "TPS2121RUXR", "C485916"),
    "U22": ("MIKILAB_TPS56637RPAR:VQFN-HR-10_L3.0-W3.0_RPA", "TPS56637", "TPS56637RPAR", "C841386"),
    "L1": ("Inductor_SMD:L_Coilcraft_XAL6030-XXX", "3.3uH", "XAL6030-332MEC", ""),
    "U23": ("MIKILAB_TPS563201DDCR:TPS563201DDCR_SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR", "TPS563201", "TPS563201DDCR", "C116592"),
    "L2": ("Inductor_SMD:L_Coilcraft_XAL4020-XXX", "2.2uH", "", ""),
    "U25": ("Package_TO_SOT_SMD:SOT-23-3", "TPS3839K33", "TPS3839K33DBZR", ""),
    "U11": ("RF_GPS:ublox_NEO", "NEO-M9N", "NEO-M9N-00B", ""),
    "J4": ("MIKILAB_BWSMA_KE_P001:SMA-SMD_BWSMA-KE-P001", "SMA ANT", "BWSMA-KE-P001", "C496550"),
    "J7": ("Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "PPS/EXTINT", "2.54-1*3P", "C49257"),
    "U19": ("MIKILAB_SN74LVC1G17DBVR:SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BR", "74LVC1G17", "SN74LVC1G17DBVR", "C7836"),
    "U20": ("MIKILAB_SN74LVC1G17DBVR:SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BR", "74LVC1G17", "SN74LVC1G17DBVR", "C7836"),
    "D2": ("MIKILAB_ESD9B5_0ST5G:SODFL1006X40N", "ESD9B5.0", "ESD9B5.0ST5G", "C111566"),
    "D3": ("MIKILAB_ESD9B5_0ST5G:SODFL1006X40N", "ESD9B5.0", "ESD9B5.0ST5G", "C111566"),
    "J11": ("MIKILAB_FH12_30S_0_5SH:FPC-SMD_FH12-30S-0.5SH-55", "BUS_POWER", "FH12-30S-0.5SH", "C506793"),
    "J12": ("MIKILAB_FPC_05F_28PH20:FPC-SMD_28P-P0.50_FPC-05F-28PH20", "MAIN", "FPC-05F-28PH20", "C2856807"),
    "SW1": ("MIKILAB_TS_1088_AR02016:SW-SMD_L3.9-W3.0-P4.45", "RESET", "TS-1088-AR02016", "C720477"),
    "SW2": ("MIKILAB_TS_1088_AR02016:SW-SMD_L3.9-W3.0-P4.45", "USER", "TS-1088-AR02016", "C720477"),
    "J5": ("MIKILAB_DM3AT_SF_PEJM5:SD-SMD_DM3AT-SF-PEJM5", "microSD", "DM3AT-SF-PEJM5", "C114218"),
    "J6": ("Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "CONSOLE", "2.54-1*3P", "C49257"),
}
for i in range(26, 32):
    BOM[f"U{i}"] = ("Package_SON:USON-10_2.5x1.0mm_P0.5mm", "TPD4E05U06", "TPD4E05U06DQAR", "")

# passivi generici per blocco, come /bom-osd32mp1: (integrato di riferimento, [(footprint, valore, quanti)])
BLOCKS = [
    ("U1", "C", [(C0603, "100nF", 12), (C0805, "10uF", 3), (C0805, "22uF", 3), (C0603, "12pF", 2)]),   # SoC, DC-DC interni, Y1
    ("U1", "L", [("Inductor_SMD:L_1008_2520Metric", "2.2uH", 3)]),                                    # DC-DC 0.9/1.2/1.5 V
    ("U1", "R", [(R0603, "10k", 8), (R0603, "1k", 3)]),                                               # strap HW_CFG, pull-up
    ("U5", "C", [(C0603, "100nF", 4), (C0805, "10uF", 2)]),
    ("U5", "R", [(R0603, "10k", 5)]),
    ("U7", "C", [(C0603, "100nF", 3), (C0603, "1uF", 2), (C0805, "4.7uF", 1), (C0603, "18pF", 2)]),
    ("U7", "R", [(R0603, "49.9R", 4), (R0603, "12.1k", 1), (R0603, "10k", 2)]),
    ("U6", "C", [(C0603, "100nF", 1)]),
    ("U6", "R", [(R0603, "4.7k", 2)]),
    ("J3", "R", [(R0603, "5.1k", 2)]),
    ("J8", "R", [(R0603, "56k", 2)]),
    ("J3", "C", [(C0805, "10uF", 1)]),
    ("U24", "R", [(R0603, "26.1k", 1), (R0603, "10k", 1), (R0603, "100k", 1)]),
    ("U24", "C", [(C0603, "1uF", 1), (C0805, "22uF", 1)]),
    ("U17", "R", [(R0603, "100k", 4)]),
    ("U17", "C", [(C0603, "1uF", 2), (C0603, "100nF", 1)]),
    ("U22", "C", [(C1206, "10uF 25V", 2), (C0805, "22uF", 2), (C0603, "100nF", 1), (C0603, "10nF", 1)]),
    ("U22", "R", [(R0603, "100k", 2), (R0603, "10k", 2)]),
    ("U23", "C", [(C0805, "10uF", 2), (C0805, "22uF", 2), (C0603, "100nF", 1)]),
    ("U23", "R", [(R0603, "33.2k", 1), (R0603, "10k", 1)]),
    ("U25", "R", [(R0603, "10k", 1)]),
    ("U11", "C", [(C0603, "100nF", 2), (C0805, "10uF", 1)]),
    ("U11", "R", [(R0603, "10R", 1), (R0603, "33R", 2)]),
    ("U11", "L", [("Inductor_SMD:L_0603_1608Metric", "27nH", 1)]),                                  # bias antenna attiva
    ("U19", "C", [(C0603, "100nF", 2)]),
    ("U19", "R", [(R0603, "100R", 4)]),
    ("J11", "C", [(C0603, "100nF", 2)]),
    ("J12", "C", [(C0603, "100nF", 2)]),
    ("BT1", "C", [(C0603, "1uF", 1)]),
    ("BT1", "R", [(R0603, "1k", 1)]),
]
num = {"C": 0, "R": 0, "L": 2}       # L1 e L2 sono gia' in BOM
ANCHOR = {}
for owner, kind, items in BLOCKS:
    for fpid, val, n in items:
        for _ in range(n):
            num[kind] += 1
            ref = f"{kind}{num[kind]}"
            BOM[ref] = (fpid, val, "", "")
            ANCHOR[ref] = owner

board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(mm(1.6))
ds.m_TrackMinWidth = mm(0.1)          # 4 mil per uscire dai pad 0.4 mm dell'LQFP
ds.m_MinClearance = mm(0.1)
ds.m_ViasMinSize = mm(0.45)
ds.m_MinThroughDrill = mm(0.2)
ds.m_HoleClearance = mm(0.2)
ds.m_CopperEdgeClearance = mm(0.3)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetTrackWidth(mm(0.127))
nc.SetClearance(mm(0.1))
nc.SetViaDiameter(mm(0.45))
nc.SetViaDrill(mm(0.2))


def load(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(PRJ, f"{LIBNAME}.pretty") if lib == LIBNAME else mik_fp_dir(lib) if lib.startswith("MIKILAB_") else f"{STD}/{lib}.pretty"
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise SystemExit(f"footprint non trovato: {fpid}")
    return fp


FP = {}
for ref, (fpid, val, mpn, lcsc) in BOM.items():
    fp = load(fpid)
    fp.SetReference(ref)
    fp.SetValue(val)
    lib_, name_ = fpid.split(":")
    fp.SetFPID(pcbnew.LIB_ID(lib_, name_))
    for k, v in (("MPN", mpn), ("LCSC", lcsc)):
        if v:
            fp.SetField(k, v)
            fp.GetField(k).SetVisible(False)
    fp.Reference().SetLayer(pcbnew.F_Fab)     # riferimenti sul Fab: la serigrafia dei 0603 a questa densita' non ci sta
    board.Add(fp)
    FP[ref] = fp


def bb_mm(b):
    return (pcbnew.ToMM(b.GetLeft()) - OX, pcbnew.ToMM(b.GetTop()) - OY, pcbnew.ToMM(b.GetRight()) - OX, pcbnew.ToMM(b.GetBottom()) - OY)


def crtyd(fp):
    """Ingombro = courtyard unito a pad e grafica (serigrafia compresa), senza i testi."""
    side = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(side)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    bb.Merge(fp.GetBoundingBox(False))
    for p in fp.Pads():
        bb.Merge(p.GetBoundingBox())
    return bb_mm(bb)


def crtyd_only(fp):
    cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    return bb_mm(cy.BBox()) if cy.OutlineCount() else bb_mm(fp.GetBoundingBox(False))


def is_tht(fp):
    return any(p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) for p in fp.Pads())


def put(ref, rot=0, side="T", **a):
    """Ruota/specchia e allinea l'ingombro: a = left/right/top/bottom/cx/cy in mm locali."""
    fp = FP[ref]
    fp.SetPosition(V(25, 35))
    if (side == "B") != fp.IsFlipped():
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetOrientationDegrees(rot)
    x0, y0, x1, y1 = crtyd(fp)
    dx = dy = 0
    if "left" in a: dx = a["left"] - x0
    if "right" in a: dx = a["right"] - x1
    if "cx" in a: dx = a["cx"] - (x0 + x1) / 2
    if "top" in a: dy = a["top"] - y0
    if "bottom" in a: dy = a["bottom"] - y1
    if "cy" in a: dy = a["cy"] - (y0 + y1) / 2
    fp.Move(pcbnew.VECTOR2I(mm(dx), mm(dy)))


def facing(ref, side, want):
    """Rotazione che porta il lato di innesto verso want = (dx, dy): il lato di innesto e' quello dove il disegno Fab
    e il courtyard sporgono di piu' oltre i pad (apertura della presa, scheda che esce dallo slot, corpo della SMA)."""
    fp = FP[ref]
    best = None
    for rot in (0, 90, 180, 270):
        put(ref, rot, side, cx=25, cy=35)
        ext = list(crtyd_only(fp))
        g = fp.GraphicalItems()
        for i in range(len(g)):
            try:
                it = g[i].Cast()
                if it.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab) and it.GetClass() == "PCB_SHAPE":
                    b_ = bb_mm(it.GetBoundingBox())
                    ext = [min(ext[0], b_[0]), min(ext[1], b_[1]), max(ext[2], b_[2]), max(ext[3], b_[3])]
            except (AttributeError, TypeError):
                pass
        pb = None
        for p_ in fp.Pads():
            q = bb_mm(p_.GetBoundingBox())
            pb = q if pb is None else (min(pb[0], q[0]), min(pb[1], q[1]), max(pb[2], q[2]), max(pb[3], q[3]))
        dx, dy = want
        over = {(-1, 0): pb[0] - ext[0], (1, 0): ext[2] - pb[2], (0, -1): pb[1] - ext[1], (0, 1): ext[3] - pb[3]}
        others = max(v for k, v in over.items() if k != (dx, dy))
        score = over[(dx, dy)] - others
        if best is None or score > best[0]:
            best = (score, rot)
    return best[1]


# ---------------- posizioni dei componenti principali (coordinate locali, mm; y verso il basso) -------------------
# Bordo alto: BUS_POWER J11 a sinistra e MAIN J12 a destra; sotto J11 i due buck 12 -> 5 V e 5 -> 3.3 V e il TPS2121.
# Centro: SP7021 U1, eMMC a sinistra del SoC, LAN8720A sotto il SoC verso l'RJ45. Bordo basso: RJ45 J1 e le due USB-C
# J3/J8 affiancate. Bordo destro: SMA d'antenna J4 con il NEO-M9N accanto, lontano dai buck (in alto a sinistra) e
# dall'Ethernet (in basso a sinistra), header PPS/EXTINT J7 sotto. CR1220 tra GNSS e USB. microSD J5 sul bottom, apertura sul bordo sinistro.
L_, R_, U_, D_ = (-1, 0), (1, 0), (0, -1), (0, 1)
PLACE = {
    "U1": dict(rot=0, cx=26.6, cy=35.5),                         # SP7021-IF, pin 1 in alto a sinistra
    "J11": dict(face=U_, left=7.4, top=0.3),                     # BUS_POWER, ingresso cavo sul bordo alto
    "J12": dict(face=U_, right=W - 7.4, top=0.3),                # MAIN sullo stesso bordo
    "L1": dict(rot=0, left=0.6, top=7.9),                        # induttore del TPS56637 sotto il BUS_POWER
    "U5": dict(rot=0, left=0.8, cy=31.5),                        # eMMC a sinistra del SoC
    "J5": dict(face=L_, side="B", left=0.0, cy=36.0),            # microSD sul bottom, apertura sul bordo sinistro
    "J1": dict(face=D_, left=7.3, bottom=H),                     # RJ45, apertura sul bordo basso
    "J3": dict(face=D_, left=28.0, bottom=H),                    # USB-C OTG accanto all'RJ45
    "J8": dict(face=D_, left=39.6, bottom=H),                    # USB-C host accanto alla OTG
    "U11": dict(rot=0, right=W - 5.6, top=21.5),                 # NEO-M9N accanto alle SMA (5.1 mm sulla scheda)
    "J4": dict(face=R_, cx=W, cy=29.5),                          # SMA antenna GNSS (x allineata al bordo piu' sotto)
    "BT1": dict(rot=0, right=W - 1.0, top=49.0),                 # CR1220 tra GNSS e USB
}
SMA_EDGE = {"J4"}
for ref, a in PLACE.items():
    a = dict(a)
    side = a.pop("side", "T")
    rot = facing(ref, side, a.pop("face")) if "face" in a else a.pop("rot", 0)
    put(ref, rot, side, **a)

# ---------------- correzioni ai footprint di libreria (solo su questa scheda) ---------------------------------------------
for ref in SMA_EDGE:   # la BWSMA disegna il proprio bordo scheda su Edge.Cuts: la allineo al bordo destro e lo tolgo
    fp = FP[ref]
    cut = [g for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.Edge_Cuts]
    fp.Move(pcbnew.VECTOR2I(mm(W - (pcbnew.ToMM(cut[0].GetBoundingBox().Centre().x) - OX)), 0))
    for g in cut:
        fp.Remove(g)
for p in list(FP["BT1"].Pads()):   # fori di centraggio del portapila CR1220-2 disegnati come PTH senza rame: NPTH
    if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and p.GetDrillSize().x >= min(p.GetSize().x, p.GetSize().y):
        p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        p.SetLayerSet(p.UnplatedHoleMask())
for p in list(FP["U17"].Pads()):   # via termiche del TPS2121RUXR MIKILAB con corona 0.05 mm: tolte, si rifanno in sbroglio
    if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
        FP["U17"].Remove(p)
for g in [g for g in FP["Y2"].GraphicalItems() if g.GetLayer() == pcbnew.F_SilkS and g.GetClass() == "PCB_SHAPE" and g.GetShape() == pcbnew.SHAPE_T_CIRCLE]:
    FP["Y2"].Remove(g)             # pallino del pin 1 del quarzo FC-135R sopra il pad

# ---------------- occupazione e posizionamento automatico ---------------------------------------------------------------
occ = {"T": [], "B": []}


def side_of(fp):
    return "B" if fp.IsFlipped() else "T"


def add_occ(fp):
    r = crtyd(fp)
    s = side_of(fp)
    if fp.GetReference() in SMA_EDGE:          # SMA a bordo scheda: pad su entrambi i lati
        r = (r[0], r[1], min(r[2], W), r[3])
        occ["T"].append(r)
        occ["B"].append(r)
        return
    occ[s].append(r)
    if is_tht(fp):                              # sull'altro lato contano solo fori e pad passanti
        o = "B" if s == "T" else "T"
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                b = bb_mm(p.GetBoundingBox())
                occ[o].append((b[0] - 0.2, b[1] - 0.2, b[2] + 0.2, b[3] + 0.2))


for (hx, hy) in HOLES:
    for s in "TB":
        occ[s].append((hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP))


def inside(r, m=0.25):
    x0, y0, x1, y1 = r
    if x0 < m or y0 < m or x1 > W - m or y1 > H - m:
        return False
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):  # angoli raggiati
        ex, ey = min(cx, W - cx), min(cy, H - cy)
        if ex < RAD and ey < RAD and math.hypot(RAD - ex, RAD - ey) > RAD - m:
            return False
    return True


def free(r, s, g=0.02):
    x0, y0, x1, y1 = r
    return all(x1 + g <= a0 or a1 + g <= x0 or y1 + g <= b0 or b1 + g <= y0 for a0, b0, a1, b1 in occ[s])


for ref in PLACE:
    r = crtyd(FP[ref])
    for s_ in ("T", "B"):
        if (s_ == side_of(FP[ref]) or ref in SMA_EDGE) and not free(r, s_, 0):
            print("ATTENZIONE: sovrapposizione tra componenti principali:", ref, s_, [round(v, 1) for v in r])
    add_occ(FP[ref])


def center_of(fp):
    x0, y0, x1, y1 = crtyd(fp)
    return (x0 + x1) / 2, (y0 + y1) / 2


def holes_of(fp):
    return [bb_mm(p.GetBoundingBox()) for p in fp.Pads() if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)]


SHAPE = {}


def shape(ref, rot, s):
    """Ingombro e fori del footprint relativi al centro dell'ingombro, per rotazione e lato (calcolati una volta)."""
    k = (FP[ref].GetFPID().GetUniStringLibItemName(), rot, s)
    if k not in SHAPE:
        fp = FP[ref]
        put(ref, rot, s, cx=25, cy=35)
        x0, y0, x1, y1 = crtyd(fp)
        hs = [(a - 25.2, b - 35.2, c - 24.8, d - 34.8) for a, b, c, d in holes_of(fp)] if is_tht(fp) else []  # 0.2 mm attorno ai fori
        SHAPE[k] = ((x0 - 25, y0 - 35, x1 - 25, y1 - 35), hs)
    return SHAPE[k]


def rings(maxr):
    """Spostamenti a spirale quadrata: passo 0.25 mm entro 5 mm, poi 0.5 mm."""
    for step, r0, r1 in ((0.25, 0, 20), (0.5, 10, int(maxr / 0.5))):
        for rr in range(r0, r1):
            ring = [(0, 0)] if rr == 0 else [(dx, dy) for dx in range(-rr, rr + 1) for dy in (-rr, rr)] + \
                [(dx, dy) for dy in range(-rr + 1, rr) for dx in (-rr, rr)]
            ring.sort(key=lambda d: d[0] ** 2 + d[1] ** 2)
            for dx, dy in ring:
                yield dx * step, dy * step


def try_place(ref, cx, cy, s="T", maxr=30, gap=0.02):
    o = "B" if s == "T" else "T"
    for dx, dy in rings(maxr):
        x, y = cx + dx, cy + dy
        for rot in (0, 90):
            (a, b, c, d), hs = shape(ref, rot, s)
            r = (x + a, y + b, x + c, y + d)
            if inside(r) and free(r, s, gap) and all(free((x + h0, y + h1, x + h2, y + h3), o) for h0, h1, h2, h3 in hs):
                put(ref, rot, s, cx=x, cy=y)
                add_occ(FP[ref])
                return True
    return False


placed = set(PLACE)
MED = {  # integrati e componenti medi con zona preferita (cx, cy), tutti sul top
    "U22": (11.5, 10.5), "U17": (31.5, 10.5), "U23": (19.0, 11.0), "L2": (24.5, 12.0), "U25": (36.0, 14.5),
    "U26": (35.0, 9.0), "U27": (39.0, 9.0), "U28": (43.0, 9.0), "U29": (47.0, 9.0), "U30": (39.0, 12.0), "U31": (43.0, 12.0),
    "Y1": (14.5, 45.5), "Y2": (39.0, 47.5), "D4": (35.5, 50.5),
    "U7": (21.0, 53.0), "Y3": (14.5, 53.0), "U6": (28.5, 54.0),
    "U9": (33.0, 72.5), "U10": (44.5, 72.5), "U24": (49.5, 68.5), "D1": (40.0, 68.5),
    "U19": (43.0, 44.5), "U20": (48.5, 44.5), "D2": (45.5, 47.5), "D3": (51.5, 47.5), "J7": (56.0, 42.5),
    "SW1": (3.5, 49.0), "SW2": (3.5, 54.0), "J6": (10.5, 49.0),
}
missing = []
for ref, (cx, cy) in MED.items():
    if try_place(ref, cx, cy, "T", maxr=20, gap=0.1):
        placed.add(ref)
    else:
        missing.append(ref)

# passivi: vicino al loro integrato, prima i piu' grandi, sempre sul top
rest = sorted((r for r in FP if r not in placed), key=lambda r: (BOM[r][0].split("_")[-1], r), reverse=True)
for ref in rest:
    cx, cy = center_of(FP[ANCHOR[ref]])
    if try_place(ref, cx, cy, "T", maxr=40) or try_place(ref, cx, cy, "T", maxr=90):
        placed.add(ref)
    else:
        missing.append(ref)

# ---------------- bordo, fori, keepout -----------------------------------------------------------------------------------
def edge(shape_, **k):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(shape_)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    for f, v in k.items():
        getattr(s, f)(v)
    board.Add(s)


for a, b in (((RAD, 0), (W - RAD, 0)), ((W, RAD), (W, H - RAD)), ((W - RAD, H), (RAD, H)), ((0, H - RAD), (0, RAD))):
    edge(pcbnew.SHAPE_T_SEGMENT, SetStart=V(*a), SetEnd=V(*b))
for cx, cy, sx, sy in ((RAD, RAD, 0, RAD), (W - RAD, RAD, W - RAD, 0), (W - RAD, H - RAD, W, H - RAD), (RAD, H - RAD, RAD, H)):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    s.SetCenter(V(cx, cy))
    s.SetStart(V(sx, sy))
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T), True)
    board.Add(s)
for k, (hx, hy) in enumerate(HOLES):
    h = pcbnew.FootprintLoad(f"{STD}/MountingHole.pretty", "MountingHole_2.2mm_M2")
    h.SetReference(f"H{k + 1}")
    h.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_2.2mm_M2"))
    h.SetBoardOnly(True)
    h.SetPosition(V(hx, hy))
    h.Reference().SetLayer(pcbnew.F_Fab)
    h.Value().SetVisible(False)
    board.Add(h)
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    for L in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        ls.AddLayer(L)
    z.SetLayerSet(ls)
    z.SetZoneName(f"KEEPOUT_H{k + 1}")
    ol = z.Outline()
    ol.NewOutline()
    for i in range(24):
        a = 2 * math.pi * i / 24
        ol.Append(mm(OX + hx + HOLE_KEEP * math.cos(a)), mm(OY + hy + HOLE_KEEP * math.sin(a)))
    board.Add(z)

pcbnew.SaveBoard(OUT, board)
open(os.path.join(PRJ, f"{PROJ}.kicad_dru"), "w").write("""(version 1)
# SMA a montaggio sul bordo: i pad arrivano al bordo per costruzione
(rule "SMA a bordo scheda"
    (condition "A.memberOfFootprint('J4') || B.memberOfFootprint('J4')")
    (constraint edge_clearance (min 0mm)))
""")
# progetto: i footprint corretti qui sopra (BT1, U17, Y2, SMA) differiscono volutamente dalla copia in libreria
pro = os.path.join(PRJ, f"{PROJ}.kicad_pro")
RULES = {"min_clearance": 0.1, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.2, "min_hole_to_hole": 0.25,
         "min_through_hole_diameter": 0.2, "min_track_width": 0.1, "min_via_annular_width": 0.1, "min_via_diameter": 0.45,
         "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1, "min_silk_clearance": 0.0, "min_text_height": 0.8,
         "min_text_thickness": 0.08, "solder_mask_to_copper_clearance": 0.0}
json.dump({"meta": {"filename": f"{PROJ}.kicad_pro", "version": 3},
           "board": {"design_settings": {"rules": RULES,
                                         "rule_severities": {"lib_footprint_mismatch": "ignore", "lib_footprint_issues": "ignore"}}},
           "libraries": {}, "net_settings": {"meta": {"version": 4}, "classes": [
               {"name": "Default", "clearance": 0.1, "track_width": 0.127, "via_diameter": 0.45, "via_drill": 0.2,
                "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.127, "diff_pair_gap": 0.127,
                "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
                "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647}]}}, open(pro, "w"), indent=2)
open(os.path.join(PRJ, "fp-lib-table"), "w").write(
    f'(fp_lib_table (version 7) (lib (name "{LIBNAME}") (type "KiCad") (uri "${{KIPRJMOD}}/{LIBNAME}.pretty") (options "") (descr "Footprint della scheda Tibbo")))\n')
top = sum(1 for r in placed if side_of(FP[r]) == "T")
npass = sum(1 for r in BOM if r in ANCHOR)
print(f"scheda {W:g} x {H:g} mm; piazzati {len(placed)}/{len(FP)} (top {top}, bottom {len(placed) - top}; passivi {npass}); non piazzati: {missing}")
