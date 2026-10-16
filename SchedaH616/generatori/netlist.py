"""Lettura della netlist KiCad in formato kicadsexpr (kicad-cli sch export netlist)."""
import re


def sexpr(text):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack, cur = [], []
    for t in tok:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    return cur[0]


def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def val(node, key, default=""):
    f = find(node, key)
    return f[0][1] if f and len(f[0]) > 1 else default


def read(path):
    """Ritorna (componenti, net): componenti = {ref: dict(value, footprint, path, dnp)}, net = {nome: [(ref, pin)]}."""
    root = sexpr(open(path).read())
    comps = {}
    for c in find(find(root, "components")[0], "comp"):
        sp = find(c, "sheetpath")[0]
        props = {val(p, "name"): val(p, "value") for p in find(c, "property")}
        comps[val(c, "ref")] = {"value": val(c, "value"), "footprint": val(c, "footprint"),
                                "path": val(sp, "tstamps") + val(c, "tstamps"), "sheet": val(sp, "names"),
                                "dnp": "dnp" in props, "mpn": props.get("MPN", "")}
    nets = {}
    for n in find(find(root, "nets")[0], "net"):
        nets[val(n, "name")] = [(val(x, "ref"), val(x, "pin")) for x in find(n, "node")]
    return comps, nets
