"""Crea prova-ddr/ProvaDDR: copia completa della scheda (stesso schema, stesso placement, nessuna pista) con lo stackup standard PCBWay
e le classi di rete per la prova di sbroglio DDR con BoardLab. Va eseguito dopo build.sh e build_pcb.sh: python3 gen_prova_ddr.py"""
import json
import os
import re
import shutil

G = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(G, "..", "progetto-kicad")
DST = os.path.join(G, "..", "prova-ddr")
OLD, NEW = "SchedaIMX6ULL-SD", "ProvaDDR"
os.makedirs(DST, exist_ok=True)
for f in os.listdir(SRC):
    p = os.path.join(SRC, f)
    if f.endswith(".kicad_sch"):
        t = open(p).read().replace(f'(project "{OLD}"', f'(project "{NEW}"')
        open(os.path.join(DST, f.replace(OLD, NEW)), "w").write(t)
    elif f in ("Scheda.kicad_sym", "sym-lib-table", "fp-lib-table"):
        shutil.copy(p, DST)
os.makedirs(os.path.join(DST, "Scheda.pretty"), exist_ok=True)
for f in os.listdir(os.path.join(SRC, "Scheda.pretty")):
    shutil.copy(os.path.join(SRC, "Scheda.pretty", f), os.path.join(DST, "Scheda.pretty"))

# Stackup: PCBWay "Multi-layer laminated structure", 4 strati, voce 1: 1.6 mm, esterno 1 oz, interno 1 oz, rame residuo 70%.
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
t = open(os.path.join(SRC, f"{OLD}.kicad_pcb")).read()
t, n = re.subn(r"\(stackup.*?\(pad_to_mask_clearance", lambda m: STACKUP + "(pad_to_mask_clearance", t, count=1, flags=re.S)
assert n == 1
assert "(segment" not in t
open(os.path.join(DST, f"{NEW}.kicad_pcb"), "w").write(t)

# Regole: le stesse della scheda (5 mil, 4 mil sotto i componenti, via 0.45/0.2).
shutil.copy(os.path.join(SRC, f"{OLD}.kicad_dru"), os.path.join(DST, f"{NEW}.kicad_dru"))

d = json.load(open(os.path.join(SRC, f"{OLD}.kicad_pro")))
d["meta"]["filename"] = f"{NEW}.kicad_pro"
r = d["board"]["design_settings"]["rules"]
r["min_track_width"] = 0.1016
r["min_clearance"] = 0.1
r["min_via_diameter"] = 0.45
r["min_through_hole_diameter"] = 0.2
ns = d["net_settings"]
base = next(c for c in ns["classes"] if c["name"] == "Default")
# Larghezze da vendor/impedancefinder/zsolver.py di BoardLab (Hammerstad-Jensen, IPC-2141A) su prepreg 0.1855 mm, er 4.74, rame 35 um.
for name, width, dw, dg in (("DDR_SE_50R", 0.316, None, None), ("DDR_DIFF_100R", 0.178, 0.178, 0.127)):
    c = dict(base)
    c.update(name=name, track_width=width, clearance=0.127, via_diameter=0.45, via_drill=0.2)
    if dw:
        c.update(diff_pair_width=dw, diff_pair_gap=dg)
    ns["classes"] = [x for x in ns["classes"] if x["name"] != name] + [c]
SE = ["DDR_A[0-9]*", "DDR_DQ[0-9]*", "DDR_BA*", "DDR_CAS_N", "DDR_RAS_N", "DDR_WE_N", "DDR_CS_N", "DDR_ODT", "DDR_CKE", "DDR_RESET_N", "DDR_LDM", "DDR_UDM"]
ns["netclass_patterns"] = [{"netclass": "DDR_DIFF_100R", "pattern": p_} for p_ in ("*DDR_CK_?", "*DDR_LDQS_?", "*DDR_UDQS_?")] + [
    {"netclass": "DDR_SE_50R", "pattern": "*" + p_.replace("[0-9]*", "*")} for p_ in SE]
json.dump(d, open(os.path.join(DST, f"{NEW}.kicad_pro"), "w"), indent=2)
print("ok")
