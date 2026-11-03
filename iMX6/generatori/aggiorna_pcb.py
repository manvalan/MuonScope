"""Aggiorna il PCB di nanoberry (convertito in KiCad 10) alla netlist della scheda iMX6, conservando lo sbroglio esistente.

Uso, con il Python di KiCad:  python3 aggiorna_pcb.py netlist.net ../progetto-kicad
- toglie i componenti eliminati dallo schema (display, espansione, hub, CP2102N, micro-USB...);
- riassegna le net ai pad; le piste delle net invariate restano come sono (DDR e fanout del SoC compresi);
- le piste rimaste senza destinazione (verso i componenti tolti o per sfere riassegnate) vengono tolte a ritroso fino all'ultimo
  punto collegato;
- piazza i componenti nuovi nelle zone liberate, senza sovrapporsi a piste, via e pad esistenti (solo placement, niente piste);
- U2 diventa la DDR3L da 1 GB (package 9x13 mm): stesso footprint di nanoberry, sagoma e courtyard aggiornati.
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
from kilib import FPLIB, mik_fp_dir

NET, PRJ = sys.argv[1], sys.argv[2]
PCB = os.path.join(PRJ, "iMX6.kicad_pcb")
mm, MM = pcbnew.FromMM, pcbnew.ToMM
comps, nets = netlist.read(NET)
padnew = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
board = pcbnew.LoadBoard(PCB)
bb = board.GetBoardEdgesBoundingBox()
OX, OY = MM(bb.GetLeft()), MM(bb.GetTop())
W, H = MM(bb.GetWidth()), MM(bb.GetHeight())
V = lambda x, y: pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))
loc = lambda p: (MM(p.x) - OX, MM(p.y) - OY)

# ---------------- 1. componenti tolti -------------------------------------------------------------------------------------------
# tolti nel file di testo prima del caricamento: Remove() del binding Python lascia il board in uno stato non tipizzato
from kilib import block
_b0 = pcbnew.LoadBoard(PCB)
PAD_TOLTI = [(MM(p.GetPosition().x), MM(p.GetPosition().y)) for f in list(_b0.GetFootprints()) if f.GetReference() not in comps and not f.GetReference().startswith(("H", "#", "REF")) for p in f.Pads()]
txt = open(PCB).read()
tolti = []
for m in reversed(list(re.finditer(r"\n\t\(footprint ", txt))):
    blk = block(txt, m.start() + 2)
    ref = re.search(r'\(property "Reference" "([^"]+)"', blk).group(1)
    if ref not in comps and not ref.startswith(("H", "#", "REF")):
        tolti.append(ref)
        txt = txt[:m.start() + 1] + txt[m.start() + 2 + len(blk):]
open(PCB, "w").write(txt)
board = pcbnew.LoadBoard(PCB)
bb = board.GetBoardEdgesBoundingBox()
OX, OY = MM(bb.GetLeft()), MM(bb.GetTop())
FP = {f.GetReference(): f for f in list(board.GetFootprints())}

# ---------------- 2. net: vecchie -> nuove ----------------------------------------------------------------------------------------
old_pads = {}
for r, f in FP.items():
    for p in f.Pads():
        old_pads.setdefault(p.GetNetname(), set()).add((r, p.GetNumber()))
mappa = {}
for on, pads in old_pads.items():
    nuove = {padnew.get(k) for k in pads} - {None}
    mappa[on] = nuove.pop() if len(nuove) == 1 else None
cambiate = {on for on, nn in mappa.items() if nn is None or old_pads.get(on, set()) != {tuple(x) for x in nets.get(nn, [])}}

# ---------------- 3. piste da togliere: senza net nuova, o appese (calcolo in sola lettura, poi tolte nel testo per uuid) ----------
TR = list(board.GetTracks())
ZN = [z for z in board.Zones() if not z.GetIsRuleArea()]
dead = {t.m_Uuid.AsString() for t in TR if mappa.get(t.GetNetname()) is None}
dead_z = {z.m_Uuid.AsString() for z in ZN if mappa.get(z.GetNetname()) is None}
pads_by_net, tracks_by_net, zones_by_net = {}, {}, {}
for f in FP.values():
    for p in f.Pads():
        pads_by_net.setdefault(p.GetNetname(), []).append(p)
for t_ in TR:
    tracks_by_net.setdefault(t_.GetNetname(), []).append(t_)
for z in ZN:
    zones_by_net.setdefault(z.GetNetname(), []).append(z)
LAYERS = (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)


def ancorato(pos, layer, net, skip):
    for p in pads_by_net.get(net, []):
        if p.IsOnLayer(layer) and p.HitTest(pos):
            return True
    for t_ in tracks_by_net.get(net, []):
        if t_ is skip or t_.m_Uuid.AsString() in dead:
            continue
        if t_.GetClass() == "PCB_VIA":
            if t_.IsOnLayer(layer) and t_.HitTest(pos):
                return True
        elif t_.GetLayer() == layer and t_.HitTest(pos, 0):
            return True
    for z in zones_by_net.get(net, []):
        if z.IsOnLayer(layer) and z.HitTestFilledArea(layer, pos):
            return True
    return False


# propagazione a fronte: si parte dalle piste che toccano un pad tolto o una pista gia' morta, e si controllano solo i vicini
CELL = 1.0
idx = {}
for t_ in TR:
    if t_.GetNetname() not in cambiate:
        continue
    pts = [t_.GetPosition()] if t_.GetClass() == "PCB_VIA" else [t_.GetStart(), t_.GetEnd()]
    for q in pts:
        idx.setdefault((t_.GetNetname(), int(MM(q.x) // CELL), int(MM(q.y) // CELL)), []).append(t_)


def vicini(net, q):
    x, y = MM(q.x) // CELL, MM(q.y) // CELL
    out = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            out += idx.get((net, int(x + i), int(y + j)), [])
    return out


fronte = []
for (x, y) in PAD_TOLTI:
    for key in [(n, int(x // CELL) + i, int(y // CELL) + j) for n in cambiate for i in (-1, 0, 1) for j in (-1, 0, 1)]:
        fronte += idx.get(key, [])
for u_ in list(dead):
    pass
fronte += [t_ for t_ in TR if t_.m_Uuid.AsString() in dead]
visti = set()
while fronte:
    t_ = fronte.pop()
    k_ = t_.m_Uuid.AsString()
    on = t_.GetNetname()
    if k_ not in dead:
        if on not in cambiate:
            continue
        if t_.GetClass() == "PCB_VIA":
            morto = sum(1 for L in LAYERS if ancorato(t_.GetPosition(), L, on, t_)) < 2
        else:
            morto = not (ancorato(t_.GetStart(), t_.GetLayer(), on, t_) and ancorato(t_.GetEnd(), t_.GetLayer(), on, t_))
        if not morto:
            continue
        dead.add(k_)
    if k_ in visti:
        continue
    visti.add(k_)
    pts = [t_.GetPosition()] if t_.GetClass() == "PCB_VIA" else [t_.GetStart(), t_.GetEnd()]
    for q in pts:
        fronte += [o for o in vicini(on, q) if o.m_Uuid.AsString() not in dead]
print("componenti tolti:", len(tolti), "net cambiate:", len(cambiate), "piste e via tolte:", len(dead), "zone tolte:", len(dead_z))
txt = open(PCB).read()
for kind in ("segment", "via", "arc", "zone"):
    for m in reversed(list(re.finditer(r"\n\t\(%s[\s\n]" % kind, txt))):
        blk = block(txt, m.start() + 2)
        u = re.search(r'\(uuid "([^"]+)"\)', blk)
        if u and (u.group(1) in dead or u.group(1) in dead_z):
            txt = txt[:m.start() + 1] + txt[m.start() + 2 + len(blk):]
open(PCB, "w").write(txt)
board = pcbnew.LoadBoard(PCB)
FP = {f.GetReference(): f for f in list(board.GetFootprints())}
# scheda allargata: ESTENDI mm in alto e DESTRA mm a destra (Michele: 90 x 60 mm). Lati e raccordi si spostano, i lati
# perpendicolari si allungano. Nella fascia nuova e nella zona delle USB-A tolte vanno connettori MIKILAB, USB-C e Wi-Fi.
ESTENDI = float(os.environ.get("IMX6_ALTO", 4.0))
DESTRA = float(os.environ.get("IMX6_DESTRA", 0.0))
bb0 = board.GetBoardEdgesBoundingBox()
top0, right0 = MM(bb0.GetTop()), MM(bb0.GetRight())


def sposta(q):
    x, y = q.x, q.y
    if MM(q.y) <= top0 + 5.0:
        y -= mm(ESTENDI)
    if MM(q.x) >= right0 - 5.0:
        x += mm(DESTRA)
    return pcbnew.VECTOR2I(x, y)


for d in list(board.GetDrawings()):
    if d.GetLayer() != pcbnew.Edge_Cuts or d.GetClass() != "PCB_SHAPE":
        continue
    if d.GetShape() == pcbnew.SHAPE_T_ARC:
        d.SetArcGeometry(sposta(d.GetStart()), sposta(d.GetArcMid()), sposta(d.GetEnd()))
    else:
        d.SetStart(sposta(d.GetStart()))
        d.SetEnd(sposta(d.GetEnd()))
bb = board.GetBoardEdgesBoundingBox()
OX, OY = MM(bb.GetLeft()), MM(bb.GetTop())
W, H = MM(bb.GetWidth()), MM(bb.GetHeight())
print("scheda", round(W, 2), "x", round(H, 2))
# fori di fissaggio: in nanoberry sono 4 via GND da 5/2.75 mm sulla maglia Raspberry Pi. I due in alto vanno negli angoli nuovi;
# quello in basso a sinistra e' gia' nell'angolo; quello in basso a destra resta dov'e' (l'angolo e' occupato dall'RJ45).
FORI = []
for v in list(board.GetTracks()):
    if v.GetClass() == "PCB_VIA" and MM(v.GetWidth()) > 4:
        x, y = loc(v.GetPosition())
        if y < H / 2:
            x = 4.0 if x < W / 2 else W - 4.0
            v.SetPosition(V(x, 4.0))
        FORI.append(loc(v.GetPosition()))
print("fori:", [(round(a, 1), round(b_, 1)) for a, b_ in FORI])
NI = {}
for name in nets:
    ni = board.FindNet(name)
    if ni is None:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
    NI[name] = ni
for r, f in FP.items():
    c = comps[r]
    f.SetPath(pcbnew.KIID_PATH(c["path"]))
    f.SetValue(c["value"])
    for p in f.Pads():
        n = padnew.get((r, p.GetNumber()))
        p.SetNet(NI[n] if n else board.FindNet(""))
for t_ in list(board.GetTracks()):
    t_.SetNet(NI[mappa[t_.GetNetname()]])
for z in list(board.Zones()):
    if not z.GetIsRuleArea():
        z.SetNet(NI[mappa[z.GetNetname()]])

# ---------------- 4. U2: DDR3L 1 GB in FBGA-96 9x13 mm ------------------------------------------------------------------------------
u2 = FP["U2"]
cx = sum(MM(p.GetPosition().x) for p in u2.Pads()) / 96
cy = sum(MM(p.GetPosition().y) for p in u2.Pads()) / 96
xs = [MM(p.GetPosition().x) for p in u2.Pads()]
lx, ly = (13.0, 9.0) if max(xs) - min(xs) > 8 else (9.0, 13.0)
side = "B" if u2.IsFlipped() else "F"
for g in list(u2.GraphicalItems()):
    if g.GetLayer() in (pcbnew.B_CrtYd, pcbnew.F_CrtYd, pcbnew.B_Fab, pcbnew.F_Fab) and g.GetClass() == "PCB_SHAPE":
        u2.Remove(g)
for layer, (a, b_) in (((pcbnew.B_Fab if side == "B" else pcbnew.F_Fab), (lx / 2, ly / 2)), ((pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd), (lx / 2 + 0.5, ly / 2 + 0.5))):
    r_ = pcbnew.PCB_SHAPE(u2)
    r_.SetShape(pcbnew.SHAPE_T_RECT)
    r_.SetStart(pcbnew.VECTOR2I(mm(cx - a), mm(cy - b_)))
    r_.SetEnd(pcbnew.VECTOR2I(mm(cx + a), mm(cy + b_)))
    r_.SetLayer(layer)
    r_.SetWidth(mm(0.05 if layer in (pcbnew.B_CrtYd, pcbnew.F_CrtYd) else 0.1))
    u2.Add(r_)
u2.SetValue("AS4C512M16D3LC-12BIN")

# ---------------- 5. componenti nuovi ----------------------------------------------------------------------------------------
def load(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(PRJ, "iMX6.pretty") if lib == "iMX6" else os.path.join(PRJ, "custom_components.pretty") if lib == "Custom Components" else \
        mik_fp_dir(lib) if lib.startswith("MIKILAB_") else f"{FPLIB}/{lib}.pretty"
    return pcbnew.FootprintLoad(path, name)


NEW = {}
for ref, c in comps.items():
    if ref in FP:
        continue
    f = load(c["footprint"])
    f.SetReference(ref)
    f.SetValue(c["value"])
    f.SetPath(pcbnew.KIID_PATH(c["path"]))
    lib_, name_ = c["footprint"].split(":")
    f.SetFPID(pcbnew.LIB_ID(lib_, name_))
    for k in ("mpn", "lcsc"):
        if c.get(k):
            f.SetField(k.upper(), c[k])
            f.GetField(k.upper()).SetVisible(False)
    if c["dnp"]:
        f.SetDNP(True)
    for p in f.Pads():
        n = padnew.get((ref, p.GetNumber()))
        if n:
            p.SetNet(NI[n])
    f.Reference().SetLayer(pcbnew.F_Fab)
    board.Add(f)
    NEW[ref] = f
FP.update(NEW)


def bbox(f):
    side_ = pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd
    cyd = f.GetCourtyard(side_)
    b_ = cyd.BBox() if cyd.OutlineCount() else f.GetBoundingBox(False)
    b_.Merge(f.GetBoundingBox(False))
    for p in f.Pads():
        b_.Merge(p.GetBoundingBox())
    return (MM(b_.GetLeft()) - OX, MM(b_.GetTop()) - OY, MM(b_.GetRight()) - OX, MM(b_.GetBottom()) - OY)


# occupazione: componenti esistenti, piste per lato, via, fori, su griglia da 2 mm
GRID = 2.0
occ = {"T": {}, "B": {}}


def occupa(side_, r):
    x0, y0, x1, y1 = r
    for i in range(int(x0 // GRID), int(x1 // GRID) + 1):
        for j in range(int(y0 // GRID), int(y1 // GRID) + 1):
            occ[side_].setdefault((i, j), []).append(r)


def libero(side_, r, g=0.2):
    x0, y0, x1, y1 = r
    seen = set()
    for i in range(int((x0 - g) // GRID), int((x1 + g) // GRID) + 1):
        for j in range(int((y0 - g) // GRID), int((y1 + g) // GRID) + 1):
            for o in occ[side_].get((i, j), []):
                if id(o) in seen:
                    continue
                seen.add(id(o))
                a0, b0, a1, b1 = o
                if not (x1 + g <= a0 or a1 + g <= x0 or y1 + g <= b0 or b1 + g <= y0):
                    return False
    return True


def occupa_fp(f):
    r = bbox(f)
    s_ = "B" if f.IsFlipped() else "T"
    occupa(s_, r)
    for p in f.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            q = p.GetBoundingBox()
            occupa("B" if s_ == "T" else "T", (MM(q.GetLeft()) - OX - 0.2, MM(q.GetTop()) - OY - 0.2, MM(q.GetRight()) - OX + 0.2, MM(q.GetBottom()) - OY + 0.2))


for r, f in FP.items():
    if r not in NEW:
        occupa_fp(f)
for (hx, hy) in FORI:
    occupa("T", (hx - 3.2, hy - 3.2, hx + 3.2, hy + 3.2)), occupa("B", (hx - 3.2, hy - 3.2, hx + 3.2, hy + 3.2))
for t in list(board.GetTracks()):
    q = t.GetBoundingBox()
    r = (MM(q.GetLeft()) - OX - 0.1, MM(q.GetTop()) - OY - 0.1, MM(q.GetRight()) - OX + 0.1, MM(q.GetBottom()) - OY + 0.1)
    if t.GetClass() == "PCB_VIA":
        occupa("T", r), occupa("B", r)
    elif t.GetLayer() == pcbnew.F_Cu:
        occupa("T", r)
    elif t.GetLayer() == pcbnew.B_Cu:
        occupa("B", r)


def put(ref, rot, side_, **a):
    f = FP[ref]
    f.SetPosition(V(W / 2, H / 2))
    if (side_ == "B") != f.IsFlipped():
        f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot)
    x0, y0, x1, y1 = bbox(f)
    dx = dy = 0
    if "left" in a: dx = a["left"] - x0
    if "right" in a: dx = a["right"] - x1
    if "cx" in a: dx = a["cx"] - (x0 + x1) / 2
    if "top" in a: dy = a["top"] - y0
    if "bottom" in a: dy = a["bottom"] - y1
    if "cy" in a: dy = a["cy"] - (y0 + y1) / 2
    f.Move(pcbnew.VECTOR2I(mm(dx), mm(dy)))


def facing(ref, want):
    """Rotazione con il lato di innesto verso want (dove Fab e courtyard sporgono di piu' oltre i pad)."""
    best = None
    for rot in (0, 90, 180, 270):
        put(ref, rot, "T", cx=W / 2, cy=H / 2)
        f = FP[ref]
        ext = list(bbox(f))
        pb = None
        for p in f.Pads():
            q = p.GetBoundingBox()
            q = (MM(q.GetLeft()) - OX, MM(q.GetTop()) - OY, MM(q.GetRight()) - OX, MM(q.GetBottom()) - OY)
            pb = q if pb is None else (min(pb[0], q[0]), min(pb[1], q[1]), max(pb[2], q[2]), max(pb[3], q[3]))
        over = {(-1, 0): pb[0] - ext[0], (1, 0): ext[2] - pb[2], (0, -1): pb[1] - ext[1], (0, 1): ext[3] - pb[3]}
        score = over[want] - max(v for k, v in over.items() if k != want)
        if best is None or score > best[0]:
            best = (score, rot)
    return best[1]


def dentro(r, m=0.3):
    return r[0] >= m and r[1] >= m and r[2] <= W - m and r[3] <= H - m


def spirale(maxr):
    for step, r0, r1 in ((0.25, 0, 24), (0.5, 12, int(maxr / 0.5))):
        for rr in range(r0, r1):
            ring = [(0, 0)] if rr == 0 else [(dx, dy) for dx in range(-rr, rr + 1) for dy in (-rr, rr)] + [(dx, dy) for dy in range(-rr + 1, rr) for dx in (-rr, rr)]
            ring.sort(key=lambda d: d[0] ** 2 + d[1] ** 2)
            for dx, dy in ring:
                yield dx * step, dy * step


SHAPE = {}


def shape(ref, rot, s_):
    """Ingombro relativo al centro e fori passanti, per rotazione e lato (calcolati una volta)."""
    k = (ref, rot, s_)
    if k not in SHAPE:
        f = FP[ref]
        put(ref, rot, s_, cx=W / 2, cy=H / 2)
        x0, y0, x1, y1 = bbox(f)
        th = any(p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) for p in f.Pads())
        SHAPE[k] = ((x0 - W / 2, y0 - H / 2, x1 - W / 2, y1 - H / 2), th)
    return SHAPE[k]


def prova(ref, cx, cy, sides="TB", maxr=40, g=0.25, rots=(0, 90)):
    for dx, dy in spirale(maxr):
        x, y = cx + dx, cy + dy
        for s_ in sides:
            for rot in rots:
                (a, b_, c_, d), th = shape(ref, rot, s_)
                r = (x + a, y + b_, x + c_, y + d)
                if dentro(r) and libero(s_, r, g) and (not th or libero("B" if s_ == "T" else "T", r, g)):
                    put(ref, rot, s_, cx=x, cy=y)
                    occupa_fp(FP[ref])
                    return True
    return False


L_, R_, U_, D_ = (-1, 0), (1, 0), (0, -1), (0, 1)
non = []
# connettori a bordo: BUS_POWER e MAIN sul bordo alto (ex espansione P1), USB-C affiancate sul bordo destro (ex USB-A)
SOLD = {"J11": (U_, 19.0, None), "J12": (U_, 42.0, None), "J8": (R_, None, 13.0), "J9": (R_, None, 23.0)}
ref_pwr = [r for r in NEW if comps[r]["value"] == "BUS_POWER_MIKILAB"][0]
ref_main = [r for r in NEW if comps[r]["value"] == "BUS_MIKILAB_MAIN"][0]
uc = sorted([r for r in NEW if comps[r]["value"] == "TYPE-C-31-M-12"], key=lambda r: int(r[1:]))
for ref, (face, cx_, cy_) in ((ref_pwr, SOLD["J11"]), (ref_main, SOLD["J12"]), (uc[0], SOLD["J8"]), (uc[1], SOLD["J9"])):
    rot = facing(ref, face)
    ok = False
    for d in sorted([k * 0.5 for k in range(-80, 81)], key=abs):
        if face == U_:
            if not (3.0 < cx_ + d < W - 3.0):
                continue
            put(ref, rot, "T", cx=cx_ + d, top=0.0)
        else:
            put(ref, rot, "T", right=W, cy=cy_ + d)
        r = bbox(FP[ref])
        th = any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in FP[ref].Pads())
        if libero("T", r) and (not th or libero("B", r)):
            occupa_fp(FP[ref])
            ok = True
            break
    if not ok:
        non.append(ref)

GRUPPI = json.load(open(os.path.join(SC, "gruppi.json")))
VICINO = {"TPS56637": "U13", "TPS2121": "U14", "USB-C 1": uc[0], "USB-C 2 host": "U16", "Serie SPI": ref_main, "Livelli": ref_main, "Disaccoppiamento": ref_pwr, "Wi-Fi": None}
ic_new = sorted([r for r in NEW if r not in (ref_pwr, ref_main, *uc)], key=lambda r: (not r.startswith(("U", "L", "J", "D")), r))
ZONA = {  # (cx, cy) di partenza in mm dall'angolo in alto a sinistra della scheda allungata
    "BL-M8723DS1": (70.0, 32.0), "AP2112K-3.3TRG1": (62.0, 30.0), "U.FL": (64.0, 3.0), "TPS56637RPAR": (70.0, 12.0 + ESTENDI), "TPS2121RUXR": (66.0, 20.0 + ESTENDI),
    "TPS2553DBVR": (72.0, 15.0 + ESTENDI), "USBLC6-2SC6": (74.0, 10.0 + ESTENDI), "SMF5.0A": (74.0, 5.0 + ESTENDI), "Console UART1": (3.0, 45.0 + ESTENDI), "TPD4E05U06DQAR": (28.0, 10.5), "3.3uH/8A": (74.0, 12.0 + ESTENDI)}
for ref in ic_new:
    c = comps[ref]
    if re.match(r"[RC]\d", ref):
        continue
    cx_, cy_ = ZONA.get(c["value"], (W / 2, H / 2))
    if c["value"] == "USBLC6-2SC6" and padnew.get((ref, "1"), "").endswith("USB2_DP"):
        cy_ = 18.0 + ESTENDI
    if not prova(ref, cx_, cy_, "T" if c["value"] in ("U.FL", "Console UART1") else "TB", maxr=45):
        non.append(ref)


def anchor_of(ref):
    t = GRUPPI.get(ref, "")
    for k, a in VICINO.items():
        if t.startswith(k) and a:
            return a
    shared = {}
    for n, nodes in nets.items():
        rs = {r for r, _ in nodes}
        if ref in rs and len(rs) < 12:
            for o in rs - {ref}:
                if o in FP and not re.match(r"[RC]\d", o):
                    shared[o] = shared.get(o, 0) + 1
    return max(shared, key=shared.get) if shared else None


for ref in [r for r in NEW if re.match(r"[RC]\d", r)]:
    a = anchor_of(ref)
    cx_, cy_ = ((sum(bbox(FP[a])[0::2]) / 2, sum(bbox(FP[a])[1::2]) / 2) if a else (W / 2, H / 2))
    if not prova(ref, cx_, cy_, "TB", maxr=40, g=0.3):
        non.append(ref)

# ---------------- 6. regole, zone, salvataggio ----------------------------------------------------------------------------------------
ds = board.GetDesignSettings()
ds.m_TrackMinWidth = mm(0.1016)
# zone: il riempimento dal binding Python si blocca, le riempie kicad-cli (build_pcb.sh)
pcbnew.SaveBoard(PCB, board)
top = sum(1 for f in list(board.GetFootprints()) if not f.IsFlipped())
print(f"componenti {len(list(board.GetFootprints()))} (top {top}); nuovi {len(NEW)}, non piazzati: {non}")
