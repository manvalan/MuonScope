"""Crea TestRouter6ULL.kicad_pcb dalla netlist (solo placement, niente piste): adattato da SchedaIMX6ULL-SD/generatori/gen_pcb.py.

Uso, con il Python di KiCad:  python3 gen_pcb.py netlist.net ../progetto
Scheda W x H con angoli raggiati 3 mm, 4 fori NPTH 2.2 mm con keepout, 4 strati (stackup standard PCBWay 4L 1.6 mm, come ProvaDDR).
I componenti principali hanno una posizione fissa (PLACE, MED); i passivi vengono messi vicino al componente con cui condividono
piu' net, fuori da una corona libera attorno a SoC e DDR3L che resta al fanout. Parte del disaccoppiamento e' sul bottom sotto le BGA.
"""
import json
import math
import os
import re
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
import pcbnew
import netlist
from kilib import FPLIB, PROJ, LIBNAME, mik_fp_dir

NET, PRJ = sys.argv[1], sys.argv[2]
OUT = os.path.join(PRJ, f"{PROJ}.kicad_pcb")
STD = FPLIB
W, H, RAD = float(os.environ.get("BOARD_W", 60)), float(os.environ.get("BOARD_H", 50)), 3.0
OX, OY = 30.0, 30.0   # la scheda deve stare nel foglio A4 dell'export PDF
HOLES = [(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)]
HOLE_KEEP = 3.2
FANOUT_SOC, FANOUT_DDR = 2.5, 2.0     # corona libera per il fanout sul top attorno a U1 e U2
mm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

comps, nets = netlist.read(NET)
board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(mm(1.6))
ds.m_TrackMinWidth = mm(0.1016)       # 4 mil sotto i componenti, 5 mil altrove (kicad_dru)
ds.m_MinClearance = mm(0.1)
ds.m_ViasMinSize = mm(0.45)
ds.m_MinThroughDrill = mm(0.2)
ds.m_ViasMinAnnularWidth = mm(0.05)       # via termiche dei footprint VQFN di libreria
ds.m_HoleClearance = mm(0.2)
ds.m_CopperEdgeClearance = mm(0.3)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetTrackWidth(mm(0.127))
nc.SetClearance(mm(0.1))
nc.SetViaDiameter(mm(0.45))
nc.SetViaDrill(mm(0.2))

# ---------------- net ----------------------------------------------------------------------------------------------
NI = {}
for name in nets:
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    NI[name] = ni
padnet = {}
for name, nodes in nets.items():
    for ref, pin in nodes:
        padnet[(ref, pin)] = NI[name]


# ---------------- footprint -----------------------------------------------------------------------------------------
def load(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(PRJ, f"{LIBNAME}.pretty") if lib == LIBNAME else mik_fp_dir(lib) if lib.startswith("MIKILAB_") else f"{STD}/{lib}.pretty"
    return pcbnew.FootprintLoad(path, name)


FP = {}
for ref, c in comps.items():
    fp = load(c["footprint"])
    fp.SetReference(ref)
    fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH(c["path"]))
    lib_, name_ = c["footprint"].split(":")
    fp.SetFPID(pcbnew.LIB_ID(lib_, name_))
    if c["mpn"]:
        fp.SetField("MPN", c["mpn"])
        fp.GetField("MPN").SetVisible(False)
    if c.get("lcsc"):
        fp.SetField("LCSC", c["lcsc"])
        fp.GetField("LCSC").SetVisible(False)
    if c["dnp"]:
        fp.SetDNP(True)
    for pad in fp.Pads():
        n = padnet.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(n)
    fp.Reference().SetLayer(pcbnew.F_Fab)
    board.Add(fp)
    FP[ref] = fp


def crtyd(fp):
    side = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(side)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    bb.Merge(fp.GetBoundingBox(False))
    for p in fp.Pads():
        bb.Merge(p.GetBoundingBox())
    return (pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY, pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY)


def crtyd_only(fp):
    b_ = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd).BBox()
    return (pcbnew.ToMM(b_.GetLeft()) - OX, pcbnew.ToMM(b_.GetTop()) - OY, pcbnew.ToMM(b_.GetRight()) - OX, pcbnew.ToMM(b_.GetBottom()) - OY)


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
    """Rotazione che porta il lato di innesto verso want: il lato dove disegno Fab e courtyard sporgono di piu' oltre i pad."""
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
                    b_ = it.GetBoundingBox()
                    ext = [min(ext[0], pcbnew.ToMM(b_.GetLeft()) - OX), min(ext[1], pcbnew.ToMM(b_.GetTop()) - OY),
                           max(ext[2], pcbnew.ToMM(b_.GetRight()) - OX), max(ext[3], pcbnew.ToMM(b_.GetBottom()) - OY)]
            except (AttributeError, TypeError):
                pass
        pb = None
        for p_ in fp.Pads():
            q = p_.GetBoundingBox()
            q = (pcbnew.ToMM(q.GetLeft()) - OX, pcbnew.ToMM(q.GetTop()) - OY, pcbnew.ToMM(q.GetRight()) - OX, pcbnew.ToMM(q.GetBottom()) - OY)
            pb = q if pb is None else (min(pb[0], q[0]), min(pb[1], q[1]), max(pb[2], q[2]), max(pb[3], q[3]))
        dx, dy = want
        over = {(-1, 0): pb[0] - ext[0], (1, 0): ext[2] - pb[2], (0, -1): pb[1] - ext[1], (0, 1): ext[3] - pb[3]}
        score = over[(dx, dy)] - max(v for k, v in over.items() if k != (dx, dy))
        if best is None or score > best[0]:
            best = (score, rot)
    return best[1]


# ---------------- posizioni dei componenti principali (coordinate locali, mm; y verso il basso) -------------------
# SoC con A1 in alto a sinistra: DRAM su sinistra e in basso a sinistra, USB in basso a destra, ENET1/UART a destra, SD1/NAND/CSI in alto a sinistra.
L_, R_, U_, D_ = (-1, 0), (1, 0), (0, -1), (0, 1)
SOC_CX, SOC_CY = 27.0, 20.0
SOC_RECT = (SOC_CX - 7, SOC_CY - 7, SOC_CX + 7, SOC_CY + 7)
PWR_X = W - 13.0                                                 # colonna dei buck sul lato destro
PLACE = {
    "U1": dict(rot=0, cx=SOC_CX, cy=SOC_CY),                     # i.MX 6ULL, A1 in alto a sinistra: sfere DRAM a sinistra e in basso a sinistra
    "U2": dict(rot=270, cx=SOC_CX - 13.0, top=SOC_CY + 10.0),    # DDR3L in basso a sinistra del SoC, 14 x 9
    "J1": dict(rot=90, cx=PWR_X + 2.0, bottom=H - 0.8),          # ingresso 5 V sul bordo basso, sotto la colonna dei buck
    "J2": dict(rot=90, cx=SOC_CX + 13.0, top=0.8),               # console UART1 sul bordo alto, verso le sfere UART1 (J14-K16)
}
for ref, a in PLACE.items():
    a = dict(a)
    side = a.pop("side", "T")
    rot = facing(ref, side, a.pop("face")) if "face" in a else a.pop("rot", 0)
    put(ref, rot, side, **a)
    print(f"{ref}: rot {rot}, ingombro", [round(v, 1) for v in crtyd(FP[ref])])

# ---------------- occupazione e posizionamento automatico ---------------------------------------------------------------
occ = {"T": [], "B": []}
EDGE_OVER = set()


def side_of(fp):
    return "B" if fp.IsFlipped() else "T"


def add_occ(fp):
    r = crtyd(fp)
    s = side_of(fp)
    if fp.GetReference() in EDGE_OVER:
        r = (max(r[0], 0), r[1], r[2], r[3])
        occ["T"].append(r)
        occ["B"].append(r)
        return
    occ[s].append(r)
    if is_tht(fp):
        o = "B" if s == "T" else "T"
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                b = p.GetBoundingBox()
                occ[o].append((pcbnew.ToMM(b.GetLeft()) - OX - 0.2, pcbnew.ToMM(b.GetTop()) - OY - 0.2,
                               pcbnew.ToMM(b.GetRight()) - OX + 0.2, pcbnew.ToMM(b.GetBottom()) - OY + 0.2))


for (hx, hy) in HOLES:
    for s in "TB":
        occ[s].append((hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP))


def inside(r, m=0.25):
    x0, y0, x1, y1 = r
    if x0 < m or y0 < m or x1 > W - m or y1 > H - m:
        return False
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        if min(cx, W - cx) + min(cy, H - cy) < RAD:
            return False
    return True


def free(r, s, g=0.02):
    x0, y0, x1, y1 = r
    return all(x1 + g <= a0 or a1 + g <= x0 or y1 + g <= b0 or b1 + g <= y0 for a0, b0, a1, b1 in occ[s])


for ref in PLACE:
    r = crtyd(FP[ref])
    if ref not in EDGE_OVER and not free(r, side_of(FP[ref]), 0):
        print("ATTENZIONE: sovrapposizione tra componenti principali:", ref, [round(v, 1) for v in r])
    if ref not in EDGE_OVER and not inside(r, 0):
        print("ATTENZIONE: fuori scheda:", ref, [round(v, 1) for v in r])
    add_occ(FP[ref])
for ref, m in (("U1", FANOUT_SOC), ("U2", FANOUT_DDR)):
    x0, y0, x1, y1 = crtyd_only(FP[ref])
    occ["T"].append((x0 - m, y0 - m, x1 + m, y1 + m))

occ["T"].append((SOC_CX - 21.0, SOC_CY + 3.0, SOC_CX - 8.0, SOC_CY + 10.0))    # corridoio indirizzi DRAM tra il lato sinistro del SoC e la DDR3L
GAP = 1.0                                  # spazio tra i courtyard dei passivi, per le piste sul top



def is_small(ref):
    """Passivi R/C: distanza maggiore tra i courtyard."""
    return ref[0] in "RC" and ref[1:].isdigit()


BIG_NET = {n for n, nodes in nets.items() if len(nodes) > 14}
owner_score = {}
for n, nodes in nets.items():
    if n in BIG_NET:
        continue
    refs = {r for r, _ in nodes}
    for r in refs:
        for o in refs:
            if o != r:
                owner_score.setdefault(r, {}).setdefault(o, 0)
                owner_score[r][o] += 1
SHEET_OWNER = {"1": "U1", "2": "U2", "3": "U3"}


def anchor(ref, placed):
    sc = {o: v for o, v in owner_score.get(ref, {}).items() if o in placed}
    if sc:
        return max(sc, key=lambda o: (sc[o], -len(owner_score.get(o, {}))))
    num = re.sub(r"\D", "", ref)
    return SHEET_OWNER.get(num[0]) if len(num) == 3 else None


def center_of(fp):
    x0, y0, x1, y1 = crtyd(fp)
    return (x0 + x1) / 2, (y0 + y1) / 2


SHAPE = {}


def shape(ref, rot, s):
    k = (ref, rot, s)
    if k not in SHAPE:
        fp = FP[ref]
        put(ref, rot, s, cx=25, cy=35)
        x0, y0, x1, y1 = crtyd(fp)
        hs = []
        if is_tht(fp):
            for p in fp.Pads():
                if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                    b = p.GetBoundingBox()
                    hs.append((pcbnew.ToMM(b.GetLeft()) - OX - 25.2, pcbnew.ToMM(b.GetTop()) - OY - 35.2, pcbnew.ToMM(b.GetRight()) - OX - 24.8, pcbnew.ToMM(b.GetBottom()) - OY - 34.8))
        SHAPE[k] = ((x0 - 25, y0 - 35, x1 - 25, y1 - 35), hs)
    return SHAPE[k]


def rings(maxr):
    for step, r0, r1 in ((0.25, 0, 20), (0.5, 10, int(maxr / 0.5))):
        for rr in range(r0, r1):
            ring = [(0, 0)] if rr == 0 else [(dx, dy) for dx in range(-rr, rr + 1) for dy in (-rr, rr)] + \
                [(dx, dy) for dy in range(-rr + 1, rr) for dx in (-rr, rr)]
            ring.sort(key=lambda d: d[0] ** 2 + d[1] ** 2)
            for dx, dy in ring:
                yield dx * step, dy * step


def try_place(ref, cx, cy, side="T", maxr=30):
    for dx, dy in rings(maxr):
        x, y = cx + dx, cy + dy
        o = "B" if side == "T" else "T"
        for rot in (0, 90):
            (a, b, c, d), hs = shape(ref, rot, side)
            r = (x + a, y + b, x + c, y + d)
            if not inside(r) or not free(r, side, GAP if is_small(ref) else 0.05):
                continue
            if all(free((x + h0, y + h1, x + h2, y + h3), o) for h0, h1, h2, h3 in hs):
                put(ref, rot, side, cx=x, cy=y)
                add_occ(FP[ref])
                return True
    return False


placed = set(PLACE)
MED = {  # componenti con zona preferita (cx, cy), coordinate assolute dall'angolo in alto a sinistra; ogni induttore accanto al suo buck
    # quarzi sotto il SoC, vicino alle sfere XTAL (T11/U11) e RTC (T16/T17)
    "Y1": (SOC_CX + 2.5, SOC_CY + 11.5), "Y2": (SOC_CX + 8.0, SOC_CY + 11.0),
    # buck in colonna sul lato destro, lontani dalla DDR3L: 1.4 V in alto, 1.35 V al centro, 3.3 V in basso vicino all'ingresso
    "U5": (PWR_X, 9.0), "L3": (PWR_X + 6.0, 9.0),
    "U4": (PWR_X, 21.0), "L2": (PWR_X + 6.0, 21.0),
    "U3": (PWR_X, 33.0), "L1": (PWR_X + 6.0, 33.0),
}
missing = []
for ref, (cx, cy) in MED.items():
    if ref in FP and ref not in placed:
        if try_place(ref, cx, cy, "T", 25):
            placed.add(ref)
        else:
            missing.append(ref)

GRUPPI = json.load(open(os.path.join(SC, "gruppi.json")))
# gruppo di passivi (inizio del titolo) -> componente vicino; l'ordine e' la priorita': prima cio' che deve stare vicino ai pin
VICINO = [("Carico 24", "Y1"), ("Carico RTC", "Y2"), ("VDD_ARM_CAP", "U1"), ("VDD_HIGH_CAP", "U1"), ("VDD_SOC_IN", "U1"), ("NVCC_DRAM", "U1"), ("VDD_SNVS_IN", "U1"), ("VDD_HIGH_IN", "U1"), ("VREF, ZQ", "U2"), ("VDD / VDDQ", "U2"),
          ("U4", "U4"), ("U5", "U5"), ("U3", "U3"), ("Ingresso", "J1"), ("Boot", "U1"), ("POR_B", "U1")]


def group_anchor(ref):
    title = GRUPPI.get(ref, "")
    for k, (pre, a) in enumerate(VICINO):
        if title.startswith(pre):
            return k, a
    return len(VICINO), anchor(ref, placed)


def dist(ref, a):
    x, y = center_of(FP[ref])
    ax, ay = center_of(FP[a])
    return math.hypot(x - ax, y - ay)


NET_OF = {}
for n_, nodes_ in nets.items():
    for r_, _p in nodes_:
        NET_OF.setdefault(r_, []).append(n_)
TURNO = {}


def target(ref, a):
    """Punto di partenza del passivo: il pad del componente vicino sulla net in comune, a turno se i pad sono piu' d'uno (massa esclusa)."""
    for n_ in NET_OF.get(ref, []):
        if n_.endswith("GND_D"):
            continue
        pins_ = [p_ for r_, p_ in nets[n_] if r_ == a]
        if pins_:
            k_ = TURNO.get((a, n_), 0)
            TURNO[(a, n_)] = k_ + 1
            num = pins_[k_ % len(pins_)]
            for pad in FP[a].Pads():
                if pad.GetNumber() == num:
                    q = pad.GetPosition()
                    return pcbnew.ToMM(q.x) - OX, pcbnew.ToMM(q.y) - OY
    return center_of(FP[a])


# Disaccoppiamento sul bottom sotto le BGA (Michele, 2026-11-02): solo i piccoli sui rail interni di U1 e i 100 nF di U2.
# Sotto U1 il blocco centrale, dove non ci sono segnali; sotto U2 la striscia senza sfere tra le colonne 3 e 7. Il resto del bottom resta al fanout.
def decap_bottom(refs, slots, a):
    libere = list(slots)
    for ref in refs:
        n_ = next(n for n in NET_OF[ref] if not n.endswith("GND_D"))
        pts = [center_pad(a, p_) for r_, p_ in nets[n_] if r_ == a]
        cx_, cy_ = sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)
        s_ = min(libere, key=lambda q: math.hypot(q[0] - cx_, q[1] - cy_))
        libere.remove(s_)
        put(ref, 0, "B", cx=s_[0], cy=s_[1])
        add_occ(FP[ref])
        placed.add(ref)


def center_pad(a, num):
    for pad in FP[a].Pads():
        if pad.GetNumber() == num:
            q = pad.GetPosition()
            return pcbnew.ToMM(q.x) - OX, pcbnew.ToMM(q.y) - OY


def scelti(titolo, valore, quanti=99):
    return sorted(r for r, tt in GRUPPI.items() if tt.startswith(titolo) and comps[r]["value"] == valore)[:quanti]


# Blocco centrale di U1: solo sopra gli anelli >= 5 (alimentazioni), i via dei segnali degli anelli fino al 4 restano scoperti.
U1_BOT = scelti("VDD_ARM_CAP", "1uF") + scelti("VDD_SOC_IN", "100nF") + scelti("NVCC_DRAM", "100nF", 1)
decap_bottom(U1_BOT, [(SOC_CX + dx, SOC_CY + dy) for dx in (-1.6, 1.6) for dy in (-2.4, -0.8, 0.8, 2.4)], "U1")
ux, uy = center_of(FP["U2"])
U2_BOT = scelti("VDD / VDDQ", "100nF", 4)
decap_bottom(U2_BOT, [(ux + dx, uy) for dx in (-4.8, -1.6, 1.6, 4.8)], "U2")
# Rail _CAP sul lato basso-destro di U1 (sfere N12-R15): subito fuori dal package, verso l'angolo dove i corridoi sono meno fitti.
CAP_BOT = scelti("VDD_HIGH_CAP", "1uF")
decap_bottom(CAP_BOT, [(SOC_CX + dx, SOC_CY + dy) for dx, dy in ((9.0, 3.4), (9.0, 5.0), (9.0, 6.6), (9.0, 8.2), (5.6, 8.8))], "U1")
print("disaccoppiamento sul bottom:", U1_BOT, U2_BOT, CAP_BOT)
# Il bottom attorno a U1 e U2 e tra i due resta ai canali del fanout e allo sbroglio DDR.
for x0_, y0_, x1_, y1_ in ((SOC_CX - 12, SOC_CY - 12, SOC_CX + 12, SOC_CY + 12), (ux - 11, uy - 8, ux + 11, uy + 8)):
    occ["B"].append((x0_, y0_, x1_, y1_))
SUL_BOTTOM = ("Boot", "POR_B")   # passivi lenti: alleggeriscono il top
rest = sorted((r for r in FP if r not in placed), key=lambda r: (group_anchor(r)[0], r))
far = []
for lontano in (False, True):
    for ref in rest:
        if ref in placed:
            continue
        a = group_anchor(ref)[1]
        if a is None:
            continue
        GAP = 0.3 if a in ("U1", "U2") else 0.8   # il disaccoppiamento di SoC e DDR il piu' vicino possibile alle sfere
        lato = "B" if GRUPPI.get(ref, "").startswith(SUL_BOTTOM) else "T"
        if try_place(ref, *target(ref, a), lato, 90 if lontano else 25):
            placed.add(ref)
            far.append((round(dist(ref, a), 1), ref, a))
for ref in FP:
    if ref not in placed:
        missing.append(ref)
print("passivi piu' lontani:", sorted(far, reverse=True)[:25])
print("distanza media per gruppo:", {a: round(sum(d for d, r_, b in far if b == a) / max(1, sum(1 for d, r_, b in far if b == a)), 1) for a in sorted({x[2] for x in far})})


# ---------------- bordo raggiato, fori, keepout ----------------------------------------------------------------------
def seg(a, b):
    s_ = pcbnew.PCB_SHAPE(board)
    s_.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s_.SetStart(V(*a))
    s_.SetEnd(V(*b))
    s_.SetLayer(pcbnew.Edge_Cuts)
    s_.SetWidth(mm(0.1))
    board.Add(s_)


def arc(center, start, end):
    a_ = pcbnew.PCB_SHAPE(board)
    a_.SetShape(pcbnew.SHAPE_T_ARC)
    a_.SetCenter(V(*center))
    a_.SetStart(V(*start))
    a_.SetEnd(V(*end))
    a_.SetLayer(pcbnew.Edge_Cuts)
    a_.SetWidth(mm(0.1))
    board.Add(a_)


seg((RAD, 0), (W - RAD, 0)), seg((W, RAD), (W, H - RAD)), seg((W - RAD, H), (RAD, H)), seg((0, H - RAD), (0, RAD))
arc((RAD, RAD), (0, RAD), (RAD, 0)), arc((W - RAD, RAD), (W - RAD, 0), (W, RAD)), arc((W - RAD, H - RAD), (W, H - RAD), (W - RAD, H)), arc((RAD, H - RAD), (RAD, H), (0, H - RAD))


def hole(ref, hx, hy, keep=True):
    h = pcbnew.FootprintLoad(f"{STD}/MountingHole.pretty", "MountingHole_2.2mm_M2")
    h.SetReference(ref)
    h.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_2.2mm_M2"))
    h.SetBoardOnly(True)
    h.SetPosition(V(hx, hy))
    h.Reference().SetLayer(pcbnew.F_Fab)
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
    z.SetZoneName(f"KEEPOUT_{ref}")
    ol = z.Outline()
    ol.NewOutline()
    for i in range(24):
        a = 2 * math.pi * i / 24
        ol.Append(mm(OX + hx + HOLE_KEEP * math.cos(a)), mm(OY + hy + HOLE_KEEP * math.sin(a)))
    board.Add(z)


for k, (hx, hy) in enumerate(HOLES):
    hole(f"H{k + 1}", hx, hy)
pcbnew.SaveBoard(OUT, board)

# Stackup standard PCBWay 4 strati 1.6 mm (Multi-layer laminated structure, voce 1), lo stesso di ProvaDDR; il binding Python non lo espone.
STACKUP = """(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.1855) (material "7628 RC46%") (epsilon_r 4.74) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 2" (type "core") (thickness 1.03) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.1855) (material "7628 RC46%") (epsilon_r 4.74) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))
\t\t\t(copper_finish "ENIG")
\t\t\t(dielectric_constraints no)
\t\t)
\t\t"""
t = open(OUT).read()
t = re.sub(r"\(stackup.*?\(pad_to_mask_clearance", STACKUP + "(pad_to_mask_clearance", t, count=1, flags=re.S) if "(stackup" in t else \
    re.sub(r"\(setup\s*", "(setup\n\t\t" + STACKUP, t, count=1)
for lname, alias in (("In1.Cu", "GND"), ("In2.Cu", "PWR")):
    t, n_ = re.subn(r'\((\d+) "%s" signal\)' % re.escape(lname), r'(\1 "%s" power "%s")' % (lname, alias), t)
    assert n_ == 1, lname
open(OUT, "w").write(t)
open(os.path.join(PRJ, f"{PROJ}.kicad_dru"), "w").write("""(version 1)
# dogbone sotto le BGA: via 0.45/0.2, una pista da 5 mil tra due via (0.35 mm di canale, 0.127 + 2 x 0.1)
(rule "Via BGA"
    (condition "A.intersectsCourtyard('U1') || A.intersectsCourtyard('U2')")
    (constraint via_diameter (min 0.45mm))
    (constraint hole_size (min 0.2mm)))
# piste: 5 mil fuori dai componenti, 4 mil sotto i componenti (courtyard di qualsiasi componente, top o bottom)
(rule "Piste 5 mil"
    (condition "A.Type == 'Track'")
    (constraint track_width (min 0.127mm)))
(rule "Piste 4 mil sotto i componenti"
    (condition "A.Type == 'Track' && (A.intersectsFrontCourtyard('*') || A.intersectsBackCourtyard('*'))")
    (constraint track_width (min 0.1016mm)))
""")
pro = os.path.join(PRJ, f"{PROJ}.kicad_pro")
d = json.load(open(pro))
for c in d["net_settings"]["classes"]:
    c["clearance"] = {"Default": 0.1, "Power_Heavy": 0.1, "Power_Logic": 0.1, "Analog_REF": 0.2, "V_Bias_36V": 0.2}.get(c["name"], c["clearance"])
json.dump(d, open(pro, "w"), indent=2)
top = sum(1 for r in placed if side_of(FP[r]) == "T")
print(f"piazzati {len(placed)}/{len(FP)} (top {top}, bottom {len(placed) - top}); non piazzati: {missing}")
