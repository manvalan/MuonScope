"""Prova di fanout di U1 e DDR3L con un router a griglia (negotiated congestion). Non scrive nulla sul PCB: la scheda resta solo placement.

Uso: python3 prova_fanout.py progetto-kicad/SchedaIMX6ULL.kicad_pcb F,B|F,In2,B out.json [out.png] [iterazioni]
Eseguita sul placement 80 x 95 mm del 2026-11-02 (commit 6aba93a): zona e allineamenti sono fissati per quella posizione di U1 e U2 e vanno adattati.
Griglia 0.1 mm allineata alle sfere di U1 (U2 spostata di 0.06 mm in y per stare in griglia). Pista 0.127, distanza 0.1, via 0.45/0.2.
- Net DDR con pin su U1 e U2: instradate da sfera a sfera, senza accordo delle lunghezze e senza coppie differenziali accoppiate.
- Altri segnali di U1: devono solo uscire dalla zona BGA + 3 mm (fanout), il resto dello sbroglio non e' provato.
- Sfere di alimentazione e di massa: via dogbone fissa verso i piani. Le isole del piano di alimentazione non sono verificate.
Ostacoli: tutti i pad reali nella zona, con il placement attuale."""
import heapq
import json
import math
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

PCB, LAYERS, OUT = sys.argv[1], sys.argv[2].split(","), sys.argv[3]
PNG = sys.argv[4] if len(sys.argv) > 4 else None
MAXIT = int(sys.argv[5]) if len(sys.argv) > 5 else 40
G = 0.1
X0, Y0, X1, Y1 = 4.0, 22.0, 46.0, 60.0      # zona della prova (mm locali)
NX, NY = int((X1 - X0) / G) + 1, int((Y1 - Y0) / G) + 1
NL = len(LAYERS)
TR, CL, VIA, PAD = 0.127, 0.1, 0.45, 0.32
PLANE = ("GND_D", "3V3", "V1P35", "V1P4", "VDD_SOC_CAP", "VDD_ARM_CAP", "VDD_HIGH_CAP", "5V_SYS")
REACH_T = TR / 2 + CL                        # distanza centro pista - bordo del rame altrui


def cell(x, y):
    return int(round((x - X0) / G)), int(round((y - Y0) / G))


def idx(i, j, l=0):
    return l * NX * NY + i + j * NX


board = pcbnew.LoadBoard(PCB)
to_local = lambda v, o: pcbnew.ToMM(v) - o
pads = []                                    # (ref, numero, net, x, y, w, h, tondo, layer F/B/all)
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for p in fp.Pads():
        pos = p.GetPosition()
        b = p.GetBoundingBox()
        x, y = to_local(pos.x, 100), to_local(pos.y, 100)
        if ref == "U2":
            y += 0.06
        w, h = pcbnew.ToMM(b.GetWidth()), pcbnew.ToMM(b.GetHeight())
        if x + w < X0 - 1 or x - w > X1 + 1 or y + h < Y0 - 1 or y - h > Y1 + 1:
            continue
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            lay = "all"
        else:
            lay = "F" if p.IsOnLayer(pcbnew.F_Cu) else "B"
        pads.append((ref, p.GetNumber(), p.GetNetname().split("/")[-1], x, y, w, h, ref in ("U1", "U2"), lay))

# ostacoli statici: per ogni strato e cella, 0 = libero, id net del proprietario, -1 = piu' proprietari o senza net
net_ids = {}


def nid(n):
    return net_ids.setdefault(n, len(net_ids) + 1)


own = [[0] * (NX * NY) for _ in range(NL)]
via_block = bytearray(NX * NY)


def mark(l, i, j, n):
    k = i + j * NX
    cur = own[l][k]
    own[l][k] = n if cur in (0, n) else -1


def stamp_shape(x, y, w, h, round_, n, layer_ids, reach):
    r_x, r_y = w / 2 + reach, h / 2 + reach
    i0, j0 = cell(x - r_x - G, y - r_y - G)
    i1, j1 = cell(x + r_x + G, y + r_y + G)
    for j in range(max(0, j0), min(NY, j1 + 1)):
        for i in range(max(0, i0), min(NX, i1 + 1)):
            px, py = X0 + i * G, Y0 + j * G
            if round_:
                hit = math.hypot(px - x, py - y) < w / 2 + reach
            else:
                dx, dy = max(abs(px - x) - w / 2, 0), max(abs(py - y) - h / 2, 0)
                hit = math.hypot(dx, dy) < reach
            if hit:
                for l in layer_ids:
                    mark(l, i, j, n)


def stamp_via_block(x, y, r):
    i0, j0 = cell(x - r - G, y - r - G)
    i1, j1 = cell(x + r + G, y + r + G)
    for j in range(max(0, j0), min(NY, j1 + 1)):
        for i in range(max(0, i0), min(NX, i1 + 1)):
            if math.hypot(X0 + i * G - x, Y0 + j * G - y) < r:
                via_block[i + j * NX] = 1


F_ID = 0
B_ID = NL - 1
ALL = list(range(NL))
SOC = [p for p in pads if p[0] == "U1"]
DDR = [p for p in pads if p[0] == "U2"]
scx = sum(p[3] for p in SOC) / len(SOC)
scy = sum(p[4] for p in SOC) / len(SOC)
dcx = sum(p[3] for p in DDR) / len(DDR)
dcy = sum(p[4] for p in DDR) / len(DDR)
ROWS = "ABCDEFGHJKLMNPRTU"


def ring(num):
    r, c = ROWS.index(num[0]), int(num[1:]) - 1
    return min(r, 16 - r, c, 16 - c)


for p in pads:
    ref, num, net, x, y, w, h, tondo, lay = p
    n = nid(net or f"_{ref}_{num}")
    ids = ALL if lay == "all" else [F_ID] if lay == "F" else [B_ID]
    stamp_shape(x, y, w, h, tondo, n, ids, REACH_T)
    r_via = (w / 2 if tondo else max(w, h) / 2) + VIA / 2 + CL
    stamp_via_block(x, y, r_via)

# dogbone fissi: alimentazioni di U1 e U2, segnali di U1 dal terzo anello in poi
vias = {}                                    # (i, j) -> net
terminals = {}                               # net -> lista di terminali [(ref, numero, cella, strati)]
SKIP = {"", "NC"}


def add_via(x, y, net):
    i, j = cell(x, y)
    n = nid(net)
    vias[(i, j)] = net
    r_t = VIA / 2 + REACH_T
    i0, j0 = cell(x - r_t - G, y - r_t - G)
    i1, j1 = cell(x + r_t + G, y + r_t + G)
    for jj in range(max(0, j0), min(NY, j1 + 1)):
        for ii in range(max(0, i0), min(NX, i1 + 1)):
            if math.hypot(X0 + ii * G - x, Y0 + jj * G - y) < r_t:
                for l in ALL:
                    mark(l, ii, jj, n)
    stamp_via_block(x, y, VIA + CL)
    return i, j


for p in SOC + DDR:
    ref, num, net, x, y = p[:5]
    if net in SKIP or net.startswith("unconnected"):
        continue
    cx_, cy_ = (scx, scy) if ref == "U1" else (dcx, dcy)
    vx, vy = x + (0.4 if x >= cx_ else -0.4), y + (0.4 if y >= cy_ else -0.4)
    if net in PLANE:
        add_via(vx, vy, net)
        continue
    if ref == "U1" and ring(num) >= 2:
        v = add_via(vx, vy, net)
        for t in range(0, 5):                # moncone del dogbone sul top
            f = t / 4
            ii, jj = cell(x + (vx - x) * f, y + (vy - y) * f)
            own[F_ID][ii + jj * NX] = nid(net) if own[F_ID][ii + jj * NX] in (0, nid(net)) else own[F_ID][ii + jj * NX]
        terminals.setdefault(net, []).append((ref, num, v, ALL))
    else:
        terminals.setdefault(net, []).append((ref, num, cell(x, y), [F_ID]))

# ---------------- router ----------------------------------------------------------------------------------------
FOOT_T = [(dx, dy) for dx in range(-3, 4) for dy in range(-3, 4) if math.hypot(dx * G, dy * G) < TR + CL - 1e-9]
FOOT_V = [(dx, dy) for dx in range(-5, 6) for dy in range(-5, 6) if math.hypot(dx * G, dy * G) < VIA / 2 + TR / 2 + CL - 1e-9]
occ = [{} for _ in range(NL)]               # cella -> {net: conteggio}
hist = [{} for _ in range(NL)]
MOVES = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
ESC = (scx - 7 - 3, scy - 7 - 3, scx + 7 + 3, scy + 7 + 3)
VIA_COST = 6.0


def foot(path):
    out = []
    for (i, j, l, kind) in path:
        if kind == "v":
            for ll in ALL:
                for dx, dy in FOOT_V:
                    out.append((ll, i + dx + (j + dy) * NX))
        else:
            for dx, dy in FOOT_T:
                out.append((l, i + dx + (j + dy) * NX))
    return set(out)


via_at = {}


def add_path(net, path, sign):
    for i, j, l, kind in path:
        if kind == "v":
            if sign > 0:
                via_at[(i, j)] = net
            else:
                via_at.pop((i, j), None)
    for l, k in foot(path):
        d = occ[l].setdefault(k, {})
        d[net] = d.get(net, 0) + sign
        if d[net] <= 0:
            del d[net]


def route(net, starts, goal_cells, escape, pres, budget):
    n = nid(net)
    best, prev, heap = {}, {}, []
    gi, gj = (sum(c[0] for c in goal_cells) / len(goal_cells), sum(c[1] for c in goal_cells) / len(goal_cells)) if goal_cells else (0, 0)
    goal = set(goal_cells)
    for (i, j), ls in starts:
        for l in ls:
            best[(i, j, l)] = 0.0
            heapq.heappush(heap, (0.0, 0.0, i, j, l))
    pops = 0
    end = None
    while heap and pops < budget:
        f, g, i, j, l = heapq.heappop(heap)
        if best.get((i, j, l), 1e18) < g - 1e-9:
            continue
        pops += 1
        x, y = X0 + i * G, Y0 + j * G
        if escape:
            if not (ESC[0] < x < ESC[2] and ESC[1] < y < ESC[3]):
                end = (i, j, l)
                break
        elif (i, j) in goal:
            end = (i, j, l)
            break
        for dx, dy, c in MOVES:
            a, b = i + dx, j + dy
            if not (0 <= a < NX and 0 <= b < NY):
                continue
            k = a + b * NX
            o = own[l][k]
            if o not in (0, n):
                continue
            d = occ[l].get(k)
            pen = 0.0
            if d:
                oth = sum(1 for q in d if q != net)
                pen = pres * oth
            ng = g + c * (1.0 + pen + hist[l].get(k, 0.0))
            if ng < best.get((a, b, l), 1e18) - 1e-9:
                best[(a, b, l)] = ng
                prev[(a, b, l)] = (i, j, l, False)
                h = 0.0 if escape else math.hypot(a - gi, b - gj) * 0.9
                heapq.heappush(heap, (ng + h, ng, a, b, l))
        k0 = i + j * NX
        if not via_block[k0] and (i, j) not in vias and all(own[q][k0] in (0, n) for q in ALL):
            for q in ALL:
                if q != l:
                    ng = g + VIA_COST
                    if ng < best.get((i, j, q), 1e18) - 1e-9:
                        best[(i, j, q)] = ng
                        prev[(i, j, q)] = (i, j, l, True)
                        h = 0.0 if escape else math.hypot(i - gi, j - gj) * 0.9
                        heapq.heappush(heap, (ng + h, ng, i, j, q))
    if end is None:
        return None
    path = []
    cur = end
    while cur in prev:
        i, j, l, isv = prev[cur]
        path.append((cur[0], cur[1], cur[2], "v" if isv else "t"))
        cur = (i, j, l)
    path.append((cur[0], cur[1], cur[2], "t"))
    return path[::-1]


def conflicts(net, path):
    """Violazione: linea centrale di questa net dentro l'ingombro di un'altra (pista 0.227 mm, via 0.39 mm), o via a meno di 0.55 mm."""
    bad = []
    for i, j, l, kind in path:
        k = i + j * NX
        for ll in (ALL if kind == "v" else [l]):
            d = occ[ll].get(k)
            if d and any(q != net for q in d):
                bad.append((ll, k))
        if kind == "v":
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    q = via_at.get((i + dx, j + dy))
                    if q and q != net and math.hypot(dx * G, dy * G) < VIA + CL:
                        bad.append((l, k))
    return bad


jobs = {}
for net, ts in terminals.items():
    u1 = [t for t in ts if t[0] == "U1"]
    u2 = [t for t in ts if t[0] == "U2"]
    if not u1:
        continue                             # net della sola DRAM (es. ZQ): resistenza accanto al pin, fuori dalla prova
    jobs[net] = (u1, u2)
paths, failed = {}, set()
order = sorted(jobs, key=lambda n: (not jobs[n][1], n))
t0 = time.time()
log = []
pres = 0.5
to_route = list(order)
for it in range(1, MAXIT + 1):
    for net in to_route:
        if net in paths:
            add_path(net, paths[net], -1)
            del paths[net]
    failed = set()
    for net in to_route:
        u1, u2 = jobs[net]
        starts = [(t[2], t[3]) for t in u1]
        goals = [t[2] for t in u2]
        p = route(net, starts, goals, not u2, pres, 250000)
        if p is None:
            failed.add(net)
        else:
            paths[net] = p
            add_path(net, p, 1)
    bad = {}
    for net, p in paths.items():
        c = conflicts(net, p)
        if c:
            bad[net] = c
            for l, k in c:
                hist[l][k] = hist[l].get(k, 0.0) + 0.6
    log.append({"it": it, "instradate": len(paths), "conflitti": len(bad), "fallite": len(failed), "sec": round(time.time() - t0)})
    print(log[-1], flush=True)
    if not bad and not failed:
        break
    to_route = sorted(set(bad) | failed, key=lambda n: (not jobs[n][1], n))
    pres = min(pres * 1.5, 60.0)
    json.dump({"strati": LAYERS, "log": log}, open(OUT, "w"))

ddr_ok = [n for n in jobs if jobs[n][1] and n in paths and n not in bad]
esc_ok = [n for n in jobs if not jobs[n][1] and n in paths and n not in bad]
res = {"strati": LAYERS, "net_totali": len(jobs), "net_ddr": sum(1 for n in jobs if jobs[n][1]), "ddr_ok": len(ddr_ok), "escape": sum(1 for n in jobs if not jobs[n][1]), "escape_ok": len(esc_ok),
       "conflitti": sorted(bad), "fallite": sorted(failed), "via_segnale": sum(sum(1 for q in p if q[3] == "v") for p in paths.values()),
       "lunghezze_ddr_mm": {n: round(sum(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(paths[n], paths[n][1:])) * G, 1) for n in ddr_ok}, "log": log}
res["dove"] = {n: sorted({(round(X0 + (k % NX) * G, 1), round(Y0 + (k // NX) * G, 1), l) for l, k in bad[n]})[:6] for n in sorted(bad)}
res["terminali_u2"] = {n: [(t_[1], t_[2]) for t_ in terminals[n] if t_[0] == "U2"] for n in sorted(bad)[:6]}
json.dump(res, open(OUT, "w"), indent=0)
print({k: res[k] for k in ("strati", "net_totali", "net_ddr", "ddr_ok", "escape", "escape_ok", "conflitti", "fallite", "via_segnale")})
if PNG:
    from PIL import Image, ImageDraw
    S = 24
    im = Image.new("RGB", (int((X1 - X0) * S) + 1, int((Y1 - Y0) * S) + 1), "white")
    d = ImageDraw.Draw(im)
    P = lambda x, y: ((x - X0) * S, (y - Y0) * S)
    for p in pads:
        x, y, w, h = p[3:7]
        d.rectangle([P(x - w / 2, y - h / 2), P(x + w / 2, y + h / 2)], fill=(205, 205, 205))
    COL = {0: (200, 30, 30), NL - 1: (30, 70, 200)}
    if NL == 3:
        COL[1] = (30, 160, 60)
    for net, p in paths.items():
        for a, b in zip(p, p[1:]):
            if a[2] == b[2]:
                c = (255, 0, 255) if net in bad else COL[a[2]]
                d.line([P(X0 + a[0] * G, Y0 + a[1] * G), P(X0 + b[0] * G, Y0 + b[1] * G)], fill=c, width=2)
    for (i, j) in vias:
        x, y = X0 + i * G, Y0 + j * G
        d.ellipse([P(x - .2, y - .2), P(x + .2, y + .2)], outline=(0, 0, 0))
    im.save(PNG)
