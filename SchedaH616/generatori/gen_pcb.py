"""Crea SchedaH616.kicad_pcb dalla netlist (solo placement, niente piste).

Uso, con il Python di KiCad:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 gen_pcb.py netlist.net progetto-kicad
Scheda 50 x 70 mm, smussi 3 mm, 4 fori NPTH 2.2 mm con keepout, 6 strati. I componenti principali hanno una posizione
fissa (PLACE); i passivi vengono messi in automatico vicino al componente con cui condividono piu' net.
"""
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
import pcbnew
import netlist

NET, PRJ = sys.argv[1], sys.argv[2]
OUT = os.path.join(PRJ, "SchedaH616.kicad_pcb")
STD = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
W, H, CH = 50.0, 70.0, 3.0           # scheda e smusso
OX, OY = 100.0, 100.0                # origine dell'angolo in alto a sinistra
HOLES = [(4, 4), (46, 4), (4, 66), (46, 66)]
HOLE_KEEP = 3.2                      # raggio del keepout attorno ai fori
mm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

comps, nets = netlist.read(NET)
board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(6)
ds = board.GetDesignSettings()
ds.SetBoardThickness(mm(1.6))
ds.m_TrackMinWidth = mm(0.127)        # 5 mil
ds.m_MinClearance = mm(0.1)
ds.m_ViasMinSize = mm(0.25)           # via-in-pad 0.25/0.15 sotto l'H616 (JLCPCB POFV)
ds.m_MinThroughDrill = mm(0.15)
ds.m_ViasMinAnnularWidth = mm(0.05)
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
cache = {}


def load(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(PRJ, "H616.pretty") if lib == "H616" else f"{STD}/{lib}.pretty"
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
    if c["dnp"]:
        fp.SetDNP(True)
    for pad in fp.Pads():
        n = padnet.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(n)
    # riferimenti sul livello Fab: su 0402 a questa densita' la serigrafia non ci sta
    fp.Reference().SetLayer(pcbnew.F_Fab)
    board.Add(fp)
    FP[ref] = fp


def crtyd(fp):
    """Ingombro = courtyard unito a pad e grafica (serigrafia compresa), senza i testi."""
    side = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(side)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    bb.Merge(fp.GetBoundingBox(False))
    for p in fp.Pads():
        bb.Merge(p.GetBoundingBox())
    return (pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY, pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY)


def is_tht(fp):
    return any(p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) for p in fp.Pads())


def put(ref, rot=0, side="T", **a):
    """Ruota/specchia e allinea il courtyard: a = left/right/top/bottom/cx/cy in mm locali."""
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
        others = max(v for k, v in over.items() if k != (dx, dy))
        score = over[(dx, dy)] - others
        if best is None or score > best[0]:
            best = (score, rot)
    return best[1]


def crtyd_only(fp):
    cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    b_ = cy.BBox()
    return (pcbnew.ToMM(b_.GetLeft()) - OX, pcbnew.ToMM(b_.GetTop()) - OY, pcbnew.ToMM(b_.GetRight()) - OX, pcbnew.ToMM(b_.GetBottom()) - OY)


# ---------------- posizioni dei componenti principali (coordinate locali, mm; y verso il basso) -------------------
# Bordo alto: bus MIKILAB. Bordo basso: RJ45 e USB-C host. Sinistra: USB-C alimentazione, jack, AP6256 + U.FL.
# Destra: GNSS NEO-M9N con le tre SMA (antenna opposta all'U.FL del Wi-Fi). Centro: H616 con LPDDR4 sotto (lato DRAM).
L_, R_, U_, D_ = (-1, 0), (1, 0), (0, -1), (0, 1)
PLACE = {
    "U301": dict(rot=0, cx=24.5, cy=26.5),                       # H616: righe DRAM (N-V) verso il basso
    "U401": dict(rot=90, cx=24.5, top=33.6),                     # LPDDR4 sul lato DRAM
    "J1": dict(face=U_, left=9.8, top=0.3),                        # BUS_POWER FH12-30, ingresso cavo sul bordo alto
    "J2": dict(face=U_, side="B", right=42.8, top=0.4),            # MAIN 28 pin sul lato bottom dello stesso bordo
    "J501": dict(face=D_, left=7.4, bottom=69.4),                  # RJ45, apertura sul bordo basso
    "J801": dict(face=D_, cx=31.5, bottom=70),                   # USB-C host, apertura sul bordo basso
    "J104": dict(face=L_, left=0, top=7.6),                      # USB-C alimentazione, bordo sinistro
    "J103": dict(face=L_, left=0, top=18.8),                     # jack 5 V, bordo sinistro
    "U601": dict(rot=0, left=0.4, top=30.8),                     # AP6256 al bordo sinistro
    "J601": dict(rot=0, left=0.3, top=44.6),                     # U.FL Wi-Fi accanto all'AP6256
    "U701": dict(rot=0, right=49.6, top=7.4),                    # NEO-M9N in alto a destra
    "J701": dict(face=R_, right=50 + 11.96, cy=30.0),            # SMA antenna GNSS (bordo destro, opposto all'U.FL)
    "J702": dict(face=R_, right=50 + 11.96, cy=41.6),            # SMA PPS OUT
    "J703": dict(face=R_, right=50 + 11.96, cy=53.2),            # SMA STROBE IN
    "J401": dict(face=R_, side="B", right=50.0, top=7.3),        # microSD sul bottom, apertura sul bordo destro, sotto il GNSS
    "BT701": dict(rot=90, side="B", right=43.6, top=34.0),        # CR1220 sul bottom
    "U402": dict(rot=0, side="B", left=0.5, top=31.0),           # eMMC sul bottom, vicino ai pin PC (lato sinistro H616)
    "U501": dict(rot=0, side="B", cx=37.0, top=54.0),            # PHY sul bottom vicino all'RJ45
    "L101": dict(rot=0, left=17.0, top=8.6),                     # induttore del TPS56637 vicino al BUS_POWER
}
SMA_EDGE = {"J701", "J702", "J703"}
for ref, a in PLACE.items():
    a = dict(a)
    side = a.pop("side", "T")
    rot = facing(ref, side, a.pop("face")) if "face" in a else a.pop("rot", 0)
    put(ref, rot, side, **a)

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
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):  # smussi
        if min(cx, W - cx) + min(cy, H - cy) < CH + m * 1.5:
            return False
    return True


def free(r, s, g=0.05):
    x0, y0, x1, y1 = r
    return all(x1 + g <= a0 or a1 + g <= x0 or y1 + g <= b0 or b1 + g <= y0 for a0, b0, a1, b1 in occ[s])


for ref in PLACE:
    r = crtyd(FP[ref])
    for s_ in ("T", "B"):
        if s_ == side_of(FP[ref]) or ref in SMA_EDGE:
            if not free(r, s_, 0):
                print("ATTENZIONE: sovrapposizione tra componenti principali:", ref, s_,
                      [round(v, 1) for v in r], [[round(v, 1) for v in o] for o in occ[s_] if not free(r, s_, 0) and not (r[2] <= o[0] or o[2] <= r[0] or r[3] <= o[1] or o[3] <= r[1])])
    add_occ(FP[ref])


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


def anchor(ref, placed):
    sc = {o: v for o, v in owner_score.get(ref, {}).items() if o in placed}
    if sc:
        return max(sc, key=lambda o: (sc[o], -len(owner_score.get(o, {}))))
    # condensatori di disaccoppiamento: integrato dello stesso foglio sulla stessa alimentazione
    series = "".join(ch for ch in ref if ch.isdigit())[:1]
    for n, nodes in nets.items():
        if not any(r == ref for r, _ in nodes) or n.endswith("GND_D"):
            continue
        for o, _ in nodes:
            if o in placed and o.startswith(("U", "L", "J")) and "".join(ch for ch in o if ch.isdigit())[:1] == series:
                return o
    return {"3": "U301", "4": "U401", "2": "U201", "1": "U101", "5": "U501", "6": "U601", "7": "U701", "8": "U801"}.get(series)


def is_decap(ref):
    if not ref.startswith("C"):
        return False
    pins = [n for n, nodes in nets.items() if any(r == ref for r, _ in nodes)]
    return "/GND_D" in pins or "GND_D" in pins


def center_of(fp):
    x0, y0, x1, y1 = crtyd(fp)
    return (x0 + x1) / 2, (y0 + y1) / 2


def holes_of(fp):
    out = []
    for p in fp.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            b = p.GetBoundingBox()
            out.append((pcbnew.ToMM(b.GetLeft()) - OX, pcbnew.ToMM(b.GetTop()) - OY, pcbnew.ToMM(b.GetRight()) - OX, pcbnew.ToMM(b.GetBottom()) - OY))
    return out


def try_place(ref, cx, cy, sides, maxr=30, first=True):
    if first and len(sides) > 1:   # prima lo stesso lato del proprietario entro 7 mm, poi entrambi
        return try_place(ref, cx, cy, sides[0], 7) or try_place(ref, cx, cy, sides, maxr, False)
    fp = FP[ref]
    step = 0.25
    for rr in range(0, int(maxr / step)):
        ring = [(0, 0)] if rr == 0 else [(dx, dy) for dx in range(-rr, rr + 1) for dy in (-rr, rr)] + \
            [(dx, dy) for dy in range(-rr + 1, rr) for dx in (-rr, rr)]
        ring.sort(key=lambda d: d[0] ** 2 + d[1] ** 2)
        for dx, dy in ring:
            for s in sides:
                for rot in (0, 90):
                    put(ref, rot, s, cx=cx + dx * step, cy=cy + dy * step)
                    r = crtyd(fp)
                    if inside(r) and free(r, s) and (not is_tht(fp) or all(free(h, "B" if s == "T" else "T") for h in holes_of(fp))):
                        add_occ(fp)
                        return True
    return False


# ordine: prima i circuiti integrati e i componenti medi, poi i passivi, ognuno vicino al suo "proprietario"
placed = set(PLACE)
MED = {  # componenti medi con zona preferita (cx, cy, lati)
    "U106": (14, 11, "T"), "U101": (22, 13, "T"), "U103": (13, 15, "B"), "U104": (9, 13, "B"), "U105": (17, 15, "B"),
    "U107": (5, 15, "B"), "U108": (17, 17, "B"), "D101": (12, 24, "T"), "D102": (5, 12, "B"),
    "U201": (17.5, 20, "T"), "L201": (12.5, 21.5, "T"), "L202": (14, 26.5, "T"), "L203": (14.5, 31, "T"), "U202": (30, 12, "T"),
    "L204": (31, 16, "T"), "U203": (5, 26, "B"),
    "U308": (24, 52, "B"), "Y301": (33.5, 21, "T"), "SW301": (40.5, 46, "T"), "SW302": (40.5, 50.5, "T"), "J301": (44.5, 64, "T"),
    "U302": (16, 4, "B"), "U303": (21, 4, "B"), "U304": (26, 4, "B"), "U305": (31, 4, "B"), "U306": (36, 4, "B"), "U307": (12, 4, "B"),
    "Y501": (5, 47, "T"), "L501": (17, 47, "T"), "U502": (14, 56, "B"),
    "J704": (42, 63, "T"), "U702": (40, 26, "T"), "U703": (40, 52, "T"), "L701": (40, 29, "T"), "D702": (40.5, 31, "T"),
    "D703": (40.5, 55, "T"), "D701": (36, 26, "T"), "D704": (38, 26, "T"),
    "U801": (30, 50, "B"), "U802": (31, 52, "T"), "L801": (31, 54, "T"), "C802": (37, 50, "B"),
    "U403": (6, 44, "T"), "U404": (16, 50, "B"),
}
missing = []
for ref, (cx, cy, s) in MED.items():
    if ref in FP and ref not in placed:
        if try_place(ref, cx, cy, s):
            placed.add(ref)
        else:
            missing.append(ref)

rest = [r for r in FP if r not in placed]
rest.sort(key=lambda r: (not r.startswith(("U", "Y", "L", "D", "Q", "J", "SW", "BT")), r))
for _ in range(3):
    for ref in list(rest):
        if ref in placed:
            continue
        a = anchor(ref, placed)
        if a is None:
            continue
        cx, cy = center_of(FP[a])
        if a in ("U301", "U401") and is_decap(ref):
            sides = "B"                      # disaccoppiamento sotto le sfere
        else:
            sides = side_of(FP[a]) + ("B" if side_of(FP[a]) == "T" else "T")
        if try_place(ref, cx, cy, sides):
            placed.add(ref)
for ref in FP:
    if ref not in placed:
        missing.append(ref)

# ---------------- bordo, fori, keepout -----------------------------------------------------------------------------------
pts = [(CH, 0), (W - CH, 0), (W, CH), (W, H - CH), (W - CH, H), (CH, H), (0, H - CH), (0, CH)]
for i in range(len(pts)):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(V(*pts[i]))
    seg.SetEnd(V(*pts[(i + 1) % len(pts)]))
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(mm(0.1))
    board.Add(seg)
for k, (hx, hy) in enumerate(HOLES):
    h = pcbnew.FootprintLoad(f"{STD}/MountingHole.pretty", "MountingHole_2.2mm_M2")
    h.SetReference(f"H{k + 1}")
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
    for L in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu):
        ls.AddLayer(L)
    z.SetLayerSet(ls)
    z.SetZoneName(f"KEEPOUT_H{k + 1}")
    ol = z.Outline()
    ol.NewOutline()
    import math
    for i in range(24):
        a = 2 * math.pi * i / 24
        ol.Append(mm(OX + hx + HOLE_KEEP * math.cos(a)), mm(OY + hy + HOLE_KEEP * math.sin(a)))
    board.Add(z)

pcbnew.SaveBoard(OUT, board)
open(os.path.join(PRJ, "SchedaH616.kicad_dru"), "w").write("""(version 1)
# SMA a montaggio sul bordo: i pad arrivano al bordo per costruzione
(rule "SMA a bordo scheda"
    (condition "A.memberOfFootprint('J701') || A.memberOfFootprint('J702') || A.memberOfFootprint('J703') || B.memberOfFootprint('J701') || B.memberOfFootprint('J702') || B.memberOfFootprint('J703')")
    (constraint edge_clearance (min 0mm)))
# via-in-pad sotto l'H616 (JLCPCB POFV): 0.25/0.15
(rule "Via-in-pad H616"
    (condition "A.Type == 'Via' && A.intersectsCourtyard('U301')")
    (constraint via_diameter (min 0.25mm))
    (constraint hole_size (min 0.15mm)))
# piste interne fino a 5 mil
(rule "Piste interne 5 mil"
    (layer inner)
    (constraint track_width (min 0.127mm)))
""")
# classi di rete ereditate dalla A133: distanze compatibili con i passi 0.4-0.5 mm di connettori e QFN
import json
pro = os.path.join(PRJ, "SchedaH616.kicad_pro")
d = json.load(open(pro))
for c in d["net_settings"]["classes"]:
    c["clearance"] = {"Default": 0.1, "Power_Heavy": 0.1, "Power_Logic": 0.15, "Analog_REF": 0.2, "V_Bias_36V": 0.2}.get(c["name"], c["clearance"])
json.dump(d, open(pro, "w"), indent=2)
top = sum(1 for r in placed if side_of(FP[r]) == "T")
print(f"piazzati {len(placed)}/{len(FP)} (top {top}, bottom {len(placed) - top}); non piazzati: {missing}")
