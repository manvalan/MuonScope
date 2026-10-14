"""PCB del PianoTest: 4 strati, contorno, connettori su lati opposti, piazzamento a gruppi (niente sbroglio).
Uso: python3 (di KiCad) build_pcb.py <netlist.xml> <uscita.kicad_pcb>"""
import sys, re, os
import xml.etree.ElementTree as ET
import pcbnew

NET, OUT = sys.argv[1], sys.argv[2]
HOME = os.path.expanduser("~")
VARS = {"MIKILAB": f"{HOME}/Development/mikylab_kikad_library",
        "KICAD10_FOOTPRINT_DIR": "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
        "KICAD9_FOOTPRINT_DIR": "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
        "KICAD8_FOOTPRINT_DIR": "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"}
LIBS = {}
for m in re.finditer(r'\(name "([^"]+)"\)\(type "[^"]*"\)\(uri "([^"]+)"\)', open(f"{HOME}/Library/Preferences/kicad/10.0/fp-lib-table").read()):
    uri = re.sub(r"\$\{(\w+)\}", lambda v: VARS.get(v.group(1), v.group(0)), m.group(2))
    LIBS[m.group(1)] = uri
STD = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
for d in os.listdir(STD):
    if d.endswith(".pretty"):
        LIBS.setdefault(d[:-7], f"{STD}/{d}")

LIBS["PianoTest"] = os.path.join(os.path.dirname(os.path.abspath(OUT)), "PianoTest.pretty")
W, H = 120.0, 90.0
MM = pcbnew.FromMM
b = pcbnew.BOARD()
b.SetCopperLayerCount(4)
b.SetLayerName(pcbnew.In1_Cu, "GND")
b.SetLayerName(pcbnew.In2_Cu, "PWR")
b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)

# contorno con angoli
pts = [(0, 0), (W, 0), (W, H), (0, H)]
for i in range(4):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    s.SetStart(pcbnew.VECTOR2I(MM(pts[i][0]), MM(pts[i][1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(pts[(i + 1) % 4][0]), MM(pts[(i + 1) % 4][1])))
    b.Add(s)

r = ET.parse(NET).getroot()
nets = {}
for n in r.iter("net"):
    name = n.get("name")
    ni = pcbnew.NETINFO_ITEM(b, name)
    b.Add(ni)
    for nd in n.iter("node"):
        nets[(nd.get("ref"), nd.get("pin"))] = ni

REG = {"/bus-pnp/": (8, 4, 40, 86), "/BiasDiodo/": (42, 4, 72, 34), "/EmettitoreTest/": (74, 4, 110, 34),
       "/Rivelatore/": (42, 36, 80, 86), "/RetroactionNetwork/": (82, 36, 112, 86)}
groups = {k: [] for k in REG}
missing = []
for c in r.iter("comp"):
    ref, fpid = c.get("ref"), c.findtext("footprint")
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(LIBS[lib], name)
    if fp is None:
        missing.append(fpid)
        continue
    fp.SetReference(ref)
    fp.SetValue(c.findtext("value"))
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    sp = c.find("sheetpath")
    fp.SetPath(pcbnew.KIID_PATH(sp.get("tstamps") + c.findtext("tstamps")))
    for f in c.iter("field"):
        if f.get("name") == "MPN":
            fp.SetField("MPN", f.text or "") if hasattr(fp, "SetField") else None
    if c.find("property[@name='dnp']") is not None:
        fp.SetDNP(True)
    for p in fp.Pads():
        ni = nets.get((ref, p.GetNumber()))
        if ni:
            p.SetNet(ni)
    b.Add(fp)
    if ref in ("J401", "J402"):
        continue
    groups[sp.get("names")].append(fp)


def place(fp, x, y, rot=0):
    fp.SetOrientationDegrees(rot)
    bb = fp.GetBoundingBox(False)
    c = bb.GetCenter()
    p = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(MM(x) + p.x - c.x, MM(y) + p.y - c.y))


for ref, x, rot in (("J401", 3.5, 270), ("J402", W - 3.5, 90)):
    place(b.FindFootprintByReference(ref), x, H / 2, rot)

over = []
for key, (x0, y0, x1, y1) in REG.items():
    fps = sorted(groups[key], key=lambda f: -f.GetBoundingBox(False).GetHeight())
    x, y, row = x0, y0, 0
    for fp in fps:
        bb = fp.GetBoundingBox(False)
        w, h = pcbnew.ToMM(bb.GetWidth()) + 1.5, pcbnew.ToMM(bb.GetHeight()) + 1.5
        if x + w > x1:
            x, y, row = x0, y + row, 0
        place(fp, x + w / 2, y + h / 2)
        x += w
        row = max(row, h)
        if y + h > y1:
            over.append(fp.GetReference())

# fori di fissaggio M3
for k, (x, y) in enumerate(((4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4))):
    fp = pcbnew.FootprintLoad(LIBS["MountingHole"], "MountingHole_3.2mm_M3")
    fp.SetReference(f"H{k + 1}")
    b.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))

# piani: GND su In1, +3V3 su In2 (da suddividere con +5V in fase di sbroglio)
for layer, netname in ((pcbnew.In1_Cu, "GND"), (pcbnew.In2_Cu, "+3V3")):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(b.FindNet(netname))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((0.5, 0.5), (W - 0.5, 0.5), (W - 0.5, H - 0.5), (0.5, H - 0.5)):
        ol.Append(MM(x), MM(y))
    b.Add(z)

d = pcbnew.VECTOR2I(MM(40), MM(40))   # dentro il foglio A4
for it in list(b.GetFootprints()) + list(b.GetDrawings()) + list(b.Zones()):
    it.Move(d)
b.Save(OUT)
print("footprint mancanti:", missing)
print("fuori regione:", over)
