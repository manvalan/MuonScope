import os
import re


def _first(*cands):
    for p in cands:
        if p and os.path.isdir(p):
            return p
    raise SystemExit("Librerie standard di KiCad 10 non trovate: impostare KICAD10_SYMBOL_DIR e KICAD10_FOOTPRINT_DIR")


# Librerie standard di KiCad 10: variabili d'ambiente, pacchetti kicad-symbols/kicad-footprints estratti in
# ~/Develop/kicad-libs (Linux senza root), installazione di sistema Linux, installazione macOS.
_HOME_LIBS = os.path.expanduser("~/Develop/kicad-libs/usr/share/kicad")
LIB = _first(os.environ.get("KICAD10_SYMBOL_DIR"), f"{_HOME_LIBS}/symbols", "/usr/share/kicad/symbols",
             "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
FPLIB = _first(os.environ.get("KICAD10_FOOTPRINT_DIR"), f"{_HOME_LIBS}/footprints", "/usr/share/kicad/footprints",
               "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
LIBNAME = "Scheda"  # libreria di progetto: Scheda.kicad_sym, Scheda.pretty, Scheda.3dshapes
PROJ = "SchedaRK3568"
ROOT_UUID = "ca22b936-6f4a-45ef-aa0b-04959bbbf7ee"


def block(t, i):
    d = 0
    for j in range(i, len(t)):
        if t[j] == "(": d += 1
        elif t[j] == ")":
            d -= 1
            if d == 0: return t[i:j + 1]
def raw(lib, name):
    t = open(f"{LIB}/{lib}.kicad_sym").read()
    i = t.find(f'(symbol "{name}"\n')
    if i < 0: i = t.find(f'(symbol "{name}"')
    return block(t, i)
def extract(lib, name):
    """Simbolo appiattito (risolve extends) e rinominato lib:name."""
    s = raw(lib, name)
    m = re.search(r'\(extends "([^"]+)"\)', s)
    if m:
        parent = raw(lib, m.group(1))
        props = re.findall(r'\(property "[^"]+".*?\n\t\t\)', s, re.S)
        body = parent
        # sostituisce le proprietà del genitore con quelle del figlio
        for p in props:
            pn = re.match(r'\(property "([^"]+)"', p).group(1)
            q = re.search(r'\(property "%s".*?\n\t\t\)' % re.escape(pn), body, re.S)
            body = body.replace(q.group(0), p) if q else body
        body = body.replace(f'"{m.group(1)}_', f'"{name}_')
        body = body.replace(f'(symbol "{m.group(1)}"', f'(symbol "{name}"', 1)
        s = body
    return s.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
def pins(s):
    return [(n, nm, float(x), float(y), int(a), typ) for typ, x, y, a, nm, n in
            re.findall(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(name "([^"]*)".*?\(number "([^"]+)"', s, re.S)]
