"""Generatore di fogli KiCad 10 a etichette con disposizione automatica a blocchi.
Le net usate su piu' fogli diventano etichette globali, le altre etichette locali (risolte in write_all)."""
import re, uuid
from kilib import extract, pins, block, PROJ, ROOT_UUID, LIBNAME, mik
F = "(effects (font (size 1.27 1.27)) (justify {j}))"
G = lambda v: round(v / 1.27) * 1.27
U = lambda: str(uuid.uuid4())
R0603, C0603 = "Resistor_SMD:R_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric"
SHEETS = []
GROUPS = {}   # riferimento del passivo -> titolo del gruppo (per il placement)


def box_symbol(libname, name, pinlist, desc, w=15.24):
    """pinlist: [(numero, nome, lato)] con lato 'L' o 'R'; un'unita' sola, pin passivi."""
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


def multi_symbol(libname, name, units_pins, desc, w=20.32, titles=None):
    """units_pins: lista di unita', ognuna lista di (numero, nome); meta' a sinistra, meta' a destra."""
    sub, PM = [], {}
    for uu, lst in enumerate(units_pins, start=1):
        half = (len(lst) + 1) // 2
        top = G(2.54 * (half + 1) / 2)
        body = [f'(symbol "{name}_{uu}_1" (rectangle (start {-w:.2f} {top:.2f}) (end {w:.2f} {-top - 2.54:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))']
        if titles:
            body.append(f'(text "{titles[uu - 1]}" (at 0 {top + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))')
        PM[uu] = []
        for side, group in ((0, lst[:half]), (180, lst[half:])):
            for i, (num, nm) in enumerate(group):
                x = -w - 2.54 if side == 0 else w + 2.54
                y = top - 2.54 * (i + 1)
                body.append(f'(pin passive line (at {x:.2f} {y:.2f} {side}) (length 2.54) (name "{nm}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))')
                PM[uu].append((num, nm, x, y, side))
        body.append(")")
        sub.append(" ".join(body))
    sym = (f'(symbol "{libname}:{name}" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no) '
           f'(property "Reference" "U" (at 0 2.54 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 0 0) (effects (font (size 1.27 1.27)))) '
           '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) (property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) '
           f'(property "Description" "{desc}" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27)))) ' + " ".join(sub) + " (embedded_fonts no))")
    return sym, PM


class Sheet:
    PAGE_W = {"A0": 1189, "A1": 841, "A2": 594, "A3": 420}

    def __init__(self, name, fname, base, page, paper="A1"):
        self.name, self.fname, self.base, self.page, self.paper = name, fname, base, page, paper
        self.uuid = U()
        self.path = f"/{ROOT_UUID}/{self.uuid}"
        self.items, self.syms, self.pins = [], {}, {}
        self.nets, self.count = {}, {}
        self.notes = 0
        self.cx, self.cy, self.rowh = 25.0, None, 0.0
        SHEETS.append(self)

    # ---- simboli -----------------------------------------------------------------------------------------------
    def add_sym(self, lib_id, text):
        self.syms[lib_id] = text
        self.pins[lib_id] = pins(text)

    def mik(self, part, sym=None):
        lib_id, text, fp = mik(part, sym, True)
        self.add_sym(lib_id, text)
        return lib_id, fp

    def std(self, lib_id):
        if lib_id not in self.syms:
            lib, n = lib_id.split(":")
            self.add_sym(lib_id, extract(lib, n))

    # ---- etichette e fili ------------------------------------------------------------------------------------------
    def label(self, net, x, y, ang):
        self.nets[net] = self.nets.get(net, 0) + 1
        self.items.append(("L", net, x, y, ang))

    def stub(self, ax, ay, a, net, L=2.54):
        dx, dy, la = {0: (-1, 0, 180), 180: (1, 0, 0), 90: (0, 1, 270), 270: (0, -1, 90)}[a]
        if net == "NC":
            self.items.append(f'(no_connect (at {ax:.2f} {ay:.2f}) (uuid "{U()}"))')
            return
        ex, ey = ax + dx * L, ay + dy * L
        self.items.append(f'(wire (pts (xy {ax:.2f} {ay:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        self.label(net, ex, ey, la)

    # ---- disposizione a blocchi --------------------------------------------------------------------------------------
    def note(self, s):
        self.notes += 1
        s = s.replace('"', "'")
        self.items.append(f'(text "{s}" (exclude_from_sim no) (at 20.00 {12 + 5 * self.notes:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')

    def _slot(self, w, h):
        if self.cy is None:
            self.cy = 22.0 + 5 * self.notes
        if self.cx + w > self.PAGE_W[self.paper] - 25:
            self.cx, self.cy, self.rowh = 25.0, self.cy + self.rowh + 8, 0.0
        x, y = self.cx, self.cy
        self.cx += w + 8
        self.rowh = max(self.rowh, h)
        return x, y

    def ic(self, lib_id, ref, val, fp, nets, dnp=False, mpn=None, lcsc=None, inbom=True):
        ps = self.pins[lib_id]
        xs, ys = [p[2] for p in ps], [p[3] for p in ps]
        w = (max(xs) - min(xs)) + 60
        h = (max(ys) - min(ys)) + 32
        x, y = self._slot(w, h)
        return self.place(lib_id, ref, val, fp, x + 30 - min(xs), y + 16 + max(ys), nets, dnp, mpn, lcsc, inbom)

    def place(self, lib_id, ref, val, fp, x, y, nets, dnp=False, mpn=None, lcsc=None, inbom=True):
        x, y = G(x), G(y)
        seen = set()
        for num, nm, px, py, a, typ in self.pins[lib_id]:
            ax, ay = round(x + px, 2), round(y - py, 2)
            if (ax, ay) in seen:
                continue
            seen.add((ax, ay))
            net = nets.get(num, nets.get(nm, "NC"))
            if net == "NC" and typ == "no_connect":   # pin no_connect nascosti del simbolo KiCad: niente flag
                continue
            self.stub(ax, ay, a, net, L=5.08 if not lib_id.startswith("Device:") and net != "NC" else 2.54)
        big = not lib_id.startswith("Device:")
        maxpy = max(p[3] for p in self.pins[lib_id])
        fx, fy = (x - 7.62, y - maxpy - 5.08) if big else (x + 2.54, y + 1.27)
        props = f' (property "MPN" "{mpn}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))' if mpn else ""
        if lcsc:
            props += f' (property "LCSC" "{lcsc}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))'
        pl = " ".join(f'(pin "{p[0]}" (uuid "{U()}"))' for p in self.pins[lib_id])
        self.items.append(
            f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1) (body_style 1) (exclude_from_sim no) (in_bom {"yes" if inbom else "no"}) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}") '
            f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
            f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
            f'(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Description" "" (at {x:.2f} {y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
            + pl + f' (instances (project "{PROJ}" (path "{self.path}" (reference "{ref}") (unit 1)))))')
        return ref

    def _next(self, prefix):
        self.count[prefix] = self.count.get(prefix, 0) + 1
        return f"{prefix}{self.base + self.count[prefix]}"

    def group(self, title, parts, cols=16):
        """Blocco di passivi: parts = [('R'|'C', valore, net1, net2[, dnp])]. Ritorna i riferimenti."""
        self.std("Device:R"), self.std("Device:C")
        n = len(parts)
        c = min(cols, n)
        rows = (n + c - 1) // c
        w, rh = max(c * 12.7, min(len(title) * 1.5, 150)), 58.42
        x, y = self._slot(w, rows * rh + 8)
        s = title.replace('"', "'")
        self.items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y + 3:.2f} 0) {F.format(j="left bottom")} (uuid "{U()}"))')
        out = []
        for i, p in enumerate(parts):
            kind, val, a, b = p[:4]
            dnp = len(p) > 4 and p[4]
            px, py = x + 6.35 + 12.7 * (i % c), y + 34 + rh * (i // c)
            ref = self._next(kind)
            GROUPS[ref] = title
            if kind == "R":
                self.place("Device:R", ref, val, R0603, px, py, {"1": a, "2": b}, dnp=dnp)
            else:
                self.place("Device:C", ref, val, C0603, px, py, {"1": a, "2": b}, dnp=dnp)
            out.append(ref)
        return out

    def flags(self, nets):
        self.std("power:PWR_FLAG")
        x, y = self._slot(len(nets) * 12.7 + 4, 45)
        for k, net in enumerate(nets):
            self.place("power:PWR_FLAG", f"#FLG{self.base + 50 + k}", "PWR_FLAG", "", x + 6 + 12.7 * k, y + 12, {"1": net}, inbom=False)

    def write(self, prj, sx, sy, lab_global):
        out = []
        for it in self.items:
            if isinstance(it, tuple):
                _, net, x, y, ang = it
                j = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
                if net in lab_global:
                    out.append(f'(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) {F.format(j=j)} (uuid "{U()}"))')
                else:
                    out.append(f'(label "{net}" (at {x:.2f} {y:.2f} {ang}) {F.format(j=j + " bottom")} (uuid "{U()}"))')
            else:
                out.append(it)
        open(f"{prj}/{self.fname}", "w").write(
            f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{self.uuid}") (paper "{self.paper}") '
            + "(lib_symbols " + " ".join(self.syms.values()) + ") " + " ".join(out) + " (embedded_fonts no))")
        return (f'(sheet (at {sx} {sy}) (size 50.8 10.16) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) '
                f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{self.uuid}") '
                f'(property "Sheetname" "{self.name}" (at {sx} {sy - 0.71:.2f} 0) {F.format(j="left bottom")}) '
                f'(property "Sheetfile" "{self.fname}" (at {sx} {sy + 10.74:.2f} 0) {F.format(j="left top")}) '
                f'(instances (project "{PROJ}" (path "/{ROOT_UUID}" (page "{self.page}")))))')


def place_multi(sh, lib_id, ref, val, fp, PM, netfn, pos, mpn=None, lcsc=None):
    """Tutte le unita' di un simbolo multi-unita': netfn(numero, nome) -> net."""
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
        if lcsc:
            props += f' (property "LCSC" "{lcsc}" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))'
        pl = " ".join(f'(pin "{p[0]}" (uuid "{U()}"))' for p in PM[uu])
        sh.items.append(
            f'(symbol (lib_id "{lib_id}") (at {x0:.2f} {y0:.2f} 0) (unit {uu}) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (uuid "{U()}") '
            f'(property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0) {F.format(j="left")}) '
            f'(property "Value" "{val}" (at {fx:.2f} {fy:.2f} 0) {F.format(j="left")}) '
            f'(property "Footprint" "{fp}" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Datasheet" "" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))) '
            f'(property "Description" "" (at {x0:.2f} {y0:.2f} 0) (hide yes) (effects (font (size 1.27 1.27)))){props} '
            + pl + f' (instances (project "{PROJ}" (path "{sh.path}" (reference "{ref}") (unit {uu})))))')


def write_all(prj, libfile):
    """Scrive i fogli, la libreria di progetto e il foglio radice; controlla le net con un solo collegamento."""
    used = {}
    for s in SHEETS:
        for n, c in s.nets.items():
            used.setdefault(n, []).append((s.name, c))
    glob = {n for n, v in used.items() if len(v) > 1}
    single = sorted(n for n, v in used.items() if len(v) == 1 and v[0][1] == 1)
    if single:
        print("NET CON UN SOLO PIN:", single)
    lib = ""
    seen = set()
    for s in SHEETS:
        for k, v in s.syms.items():
            if k.startswith(LIBNAME + ":") and k not in seen:
                seen.add(k)
                lib += " " + v.replace(f'(symbol "{k}"', f'(symbol "{k[len(LIBNAME) + 1:]}"', 1)
    open(libfile, "w").write(f'(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0"){lib})')
    blocks = [s.write(prj, 30 + 70 * (i % 5), 40 + 30 * (i // 5), glob) for i, s in enumerate(SHEETS)]
    open(f"{prj}/{PROJ}.kicad_sch", "w").write(
        f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{ROOT_UUID}") (paper "A3") (lib_symbols) '
        + " ".join(blocks) + ' (sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
    return used, glob
