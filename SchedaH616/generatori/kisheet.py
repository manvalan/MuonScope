"""Generatore di fogli KiCad 10 a etichette (stile dei fogli SchedaH616)."""
import re, uuid
from kilib import extract, pins, block

PROJ = "SchedaH616"
ROOT_UUID = "ca22b936-6f4a-45ef-aa0b-04959bbbf7ee"
F = "(effects (font (size 1.27 1.27)) (justify {j}))"
G = lambda v: round(v / 1.27) * 1.27
U = lambda: str(uuid.uuid4())


def lib_from_file(path, name, libname):
    t = open(path).read()
    i = t.find(f'(symbol "{name}"')
    s = block(t, i)
    return s.replace(f'(symbol "{name}"', f'(symbol "{libname}:{name}"', 1)


def box_symbol(libname, name, pinlist, desc, w=15.24):
    """pinlist: [(numero, nome, lato)] con lato 'L' o 'R'; un'unità sola."""
    left = [p for p in pinlist if p[2] == "L"]
    right = [p for p in pinlist if p[2] == "R"]
    n = max(len(left), len(right))
    top = G(2.54 * (n + 1) / 2)
    body = [f'(symbol "{name}_1_1" (rectangle (start {-w:.2f} {top:.2f}) (end {w:.2f} {-top - 2.54:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))']
    for side, group in ((0, left), (180, right)):
        for i, (num, nm, _) in enumerate(group):
            x = -w - 2.54 if side == 0 else w + 2.54
            body.append(f'(pin passive line (at {x:.2f} {top - 2.54 * (i + 1):.2f} {side}) (length 2.54) (name "{nm}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))')
    body.append(")")
    return (f'(symbol "{libname}:{name}" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no) '
            f'(property "Reference" "U" (at 0 {top + 2.54:.2f} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {-top - 5.08:.2f} 0) (effects (font (size 1.27 1.27)))) '
            '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) (property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Description" "{desc}" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) ' + " ".join(body) + " (embedded_fonts no))")


class Sheet:
    def __init__(self, name, fname, series, page, hier, global_prefix=(), paper="A3"):
        self.name, self.fname, self.series, self.page = name, fname, series, page
        self.uuid = U()
        self.path = f"/{ROOT_UUID}/{self.uuid}"
        self.hierset, self.gp, self.paper = set(hier), tuple(global_prefix), paper
        self.items, self.hier, self.syms, self.pins = [], [], {}, {}

    def add_sym(self, lib_id, text):
        self.syms[lib_id] = text
        self.pins[lib_id] = pins(text)

    def std(self, lib_id):
        lib, n = lib_id.split(":")
        self.add_sym(lib_id, extract(lib, n))

    def label(self, net, x, y, ang):
        j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
        if net == "GND_D" or net.startswith(self.gp):
            self.items.append(f'(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) {F.format(j=j)} (uuid "{U()}"))')
        elif net in self.hierset:
            self.items.append(f'(hierarchical_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) {F.format(j=j)} (uuid "{U()}"))')
            if net not in self.hier:
                self.hier.append(net)
        else:
            self.items.append(f'(label "{net}" (at {x:.2f} {y:.2f} {ang}) {F.format(j=j + " bottom")} (uuid "{U()}"))')

    def stub(self, ax, ay, a, net, L=2.54):
        dx, dy, la = {0: (-1, 0, 180), 180: (1, 0, 0), 90: (0, 1, 270), 270: (0, -1, 90)}[a]
        if net == "NC":
            self.items.append(f'(no_connect (at {ax:.2f} {ay:.2f}) (uuid "{U()}"))')
            return
        ex, ey = ax + dx * L, ay + dy * L
        self.items.append(f'(wire (pts (xy {ax:.2f} {ay:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        self.label(net, ex, ey, la)

    def place(self, lib_id, ref, val, fp, x, y, nets, dnp=False, mpn=None):
        m = re.match(r"([A-Z]+)(\d+)$", ref)
        ref = f"{m.group(1)}{self.series + int(m.group(2))}"
        x, y = G(x), G(y)
        seen = set()
        for num, nm, px, py, a, typ in self.pins[lib_id]:
            ax, ay = round(x + px, 2), round(y - py, 2)
            if (ax, ay) in seen:
                continue
            seen.add((ax, ay))
            net = nets.get(num, nets.get(nm, "NC"))
            self.stub(ax, ay, a, net, L=5.08 if not lib_id.startswith("Device:") and net != "NC" else 2.54)
        big = not lib_id.startswith("Device:")
        maxpy = max(p[3] for p in self.pins[lib_id])
        fx, fy = (x - 7.62, y - maxpy - 5.08) if big else (x + 2.54, y + 1.27)
        props = f' (property "MPN" "{mpn}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))' if mpn else ""
        pl = " ".join(f'(pin "{p[0]}" (uuid "{U()}"))' for p in self.pins[lib_id])
        self.items.append(
            f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1) (body_style 1) (exclude_from_sim no) (in_bom {"no" if lib_id == "Connector:TestPoint" else "yes"}) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}") '
            f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
            f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
            f'(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
            + pl + f' (instances (project "{PROJ}" (path "{self.path}" (reference "{ref}") (unit 1)))))')

    def R(self, ref, val, x, y, a, b, **k):
        self.place("Device:R", ref, val, "Resistor_SMD:R_0402_1005Metric", x, y, {"1": a, "2": b}, **k)

    def C(self, ref, val, x, y, a, b, fp="Capacitor_SMD:C_0402_1005Metric", **k):
        self.place("Device:C", ref, val, fp, x, y, {"1": a, "2": b}, **k)

    def text(self, s, x, y):
        self.items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')

    def write(self, prj, sx, sy, libfile=None):
        if libfile:
            lib = open(libfile).read()
            for k, v in self.syms.items():
                if k.startswith("H616:") and f'(symbol "{k[5:]}"' not in lib:
                    lib = lib.rstrip()[:-1] + " " + v.replace(f'(symbol "{k}"', f'(symbol "{k[5:]}"', 1) + ")"
            open(libfile, "w").write(lib)
        open(f"{prj}/{self.fname}", "w").write(
            f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{self.uuid}") (paper "{self.paper}") '
            + "(lib_symbols " + " ".join(self.syms.values()) + ") " + " ".join(self.items) + " (embedded_fonts no))")
        root_path = f"{prj}/{PROJ}.kicad_sch"
        root = open(root_path).read()
        w = 50.8
        h = 5.08 + 2.54 * len(self.hier)
        pinlist, extra = [], []
        for k, n in enumerate(self.hier):
            py = sy + 2.54 * (k + 1)
            pinlist.append(f'(pin "{n}" passive (at {sx:.2f} {py:.2f} 180) (uuid "{U()}") {F.format(j="left")})')
            extra.append(f'(wire (pts (xy {sx:.2f} {py:.2f}) (xy {sx - 5.08:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
            extra.append(f'(label "{n}" (at {sx - 5.08:.2f} {py:.2f} 180) {F.format(j="right bottom")} (uuid "{U()}"))')
        sheet = (f'(sheet (at {sx} {sy}) (size {w} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
                 f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{self.uuid}") '
                 f'(property "Sheetname" "{self.name}" (at {sx} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
                 f'(property "Sheetfile" "{self.fname}" (at {sx} {sy + h + 0.58:.2f} 0) {F.format(j="left top")}) '
                 + " ".join(pinlist) + f' (instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "{self.page}")))))')
        k = root.rfind("\t(sheet_instances")
        root = root[:k] + "\t" + sheet + "\n\t" + "\n\t".join(extra) + "\n" + root[k:]
        open(root_path, "w").write(root)
        return self.hier


def multi_symbol(libname, name, units_pins, desc, w=20.32, titles=None):
    """units_pins: lista di unità, ognuna lista di (numero, nome); metà a sinistra, metà a destra."""
    sub, PINMAP = [], {}
    for uu, lst in enumerate(units_pins, start=1):
        half = (len(lst) + 1) // 2
        top = G(2.54 * (half + 1) / 2)
        body = [f'(symbol "{name}_{uu}_1" (rectangle (start {-w:.2f} {top:.2f}) (end {w:.2f} {-top - 2.54:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))']
        if titles:
            body.append(f'(text "{titles[uu - 1]}" (at 0 {top + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))')
        PINMAP[uu] = []
        for side, group in ((0, lst[:half]), (180, lst[half:])):
            for i, (num, nm) in enumerate(group):
                x = -w - 2.54 if side == 0 else w + 2.54
                y = top - 2.54 * (i + 1)
                body.append(f'(pin passive line (at {x:.2f} {y:.2f} {side}) (length 2.54) (name "{nm}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))')
                PINMAP[uu].append((num, nm, x, y, side))
        body.append(")")
        sub.append(" ".join(body))
    sym = (f'(symbol "{libname}:{name}" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no) '
           f'(property "Reference" "U" (at 0 2.54 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 0 0) (effects (font (size 1.27 1.27)))) '
           '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) (property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) '
           f'(property "Description" "{desc}" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) ' + " ".join(sub) + " (embedded_fonts no))")
    return sym, PINMAP


def place_multi(sh, lib_id, ref, val, fp, PM, netfn, pos, mpn=None):
    """Piazza tutte le unità di un simbolo multi-unità: netfn(numero, nome) -> net."""
    m = re.match(r"([A-Z]+)(\d+)$", ref)
    ref = f"{m.group(1)}{sh.series + int(m.group(2))}"
    for uu, (x0, y0) in pos.items():
        x0, y0 = G(x0), G(y0)
        seen = set()
        for num, nm, px, py, side in PM[uu]:
            ax, ay = round(x0 + px, 2), round(y0 - py, 2)
            if (ax, ay) in seen:
                continue
            seen.add((ax, ay))
            net = netfn(num, nm)
            sh.stub(ax, ay, side, net, L=5.08 if net != "NC" else 2.54)
        n = len(PM[uu])
        fx, fy = x0 - 15, y0 - G(2.54 * ((n + 1) // 2 + 1) / 2) - 4
        props = f' (property "MPN" "{mpn}" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))' if mpn else ""
        pl = " ".join(f'(pin "{p[0]}" (uuid "{U()}"))' for p in PM[uu])
        sh.items.append(
            f'(symbol (lib_id "{lib_id}") (at {x0:.2f} {y0:.2f} 0) (unit {uu}) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (uuid "{U()}") '
            f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
            f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
            f'(property "Footprint" "{fp}" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Datasheet" "" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Description" "" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
            + pl + f' (instances (project "{PROJ}" (path "{sh.path}" (reference "{ref}") (unit {uu})))))')
