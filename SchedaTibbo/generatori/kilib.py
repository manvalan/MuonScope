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
PROJ = "SchedaTibbo"
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
    return [(n, nm, float(x), float(y), int(float(a)), typ) for typ, x, y, a, nm, n in
            re.findall(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) ([\d.]+)\).*?\(name "([^"]*)".*?\(number "([^"]+)"', s, re.S)]


# ---------------- libreria personale MIKILAB (github.com/manvalan/mikilab-kicad-library) -----------------------------------
def _first_or_none(*cands):
    return next((p for p in cands if p and os.path.isdir(p)), None)


MIKILAB = _first_or_none(os.environ.get("MIKILAB"), os.path.expanduser("~/Develop/mikilab-kicad-library"),
                         os.path.expanduser("~/Development/mikylab_kikad_library"), os.path.expanduser("~/Development/mikilab-kicad-library"))


def _libtable(name):
    if not MIKILAB:
        raise SystemExit("Libreria MIKILAB non trovata: impostare la variabile MIKILAB")
    t = open(os.path.join(MIKILAB, name)).read()
    return {n: u.replace("${KIPRJMOD}/", "") for n, u in re.findall(r'\(name "([^"]+)"\)\s*\(type "[^"]+"\)\s*\(uri "([^"]+)"\)', t)}


def mik(part, sym=None, footprint=True):
    """Simbolo (rinominato nick:simbolo) e footprint di un componente della libreria MIKILAB: (lib_id, testo, footprint)."""
    syms = _libtable("sym-lib-table")
    nick, rel = next((n, u) for n, u in syms.items() if u.endswith(f"/{part}.kicad_sym"))
    sym = sym or part
    t = open(os.path.join(MIKILAB, rel)).read()
    i = t.find(f'(symbol "{sym}"')
    s = block(t, i).replace(f'(symbol "{sym}"', f'(symbol "{nick}:{sym}"', 1)
    fp = None
    if footprint:
        fps = _libtable("fp-lib-table")
        fnick, frel = next((n, u) for n, u in fps.items() if u.endswith(f"/{part}.pretty"))
        mods = sorted(f for f in os.listdir(os.path.join(MIKILAB, frel)) if f.endswith(".kicad_mod"))
        fp = f"{fnick}:{mods[0][:-10]}"
    return f"{nick}:{sym}", s, fp


def mik_fp_dir(nick):
    return os.path.join(MIKILAB, _libtable("fp-lib-table")[nick])


def pins_by_unit(s):
    """Pin per unità di un simbolo di libreria: {unità: [(numero, nome, x, y, angolo)]} (unità 0 = comune, copiata in tutte)."""
    out = {}
    for m in re.finditer(r'\(symbol "[^"]+?_(\d+)_\d+"', s):
        u = int(m.group(1))
        b = block(s, m.start())
        out.setdefault(u, []).extend((n, nm, float(x), float(y), int(float(a))) for x, y, a, nm, n in
                                     re.findall(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([\d.]+)\).*?\(name "([^"]*)".*?\(number "([^"]+)"', b, re.S))
    common = out.pop(0, [])
    if not out:
        return {1: common}
    return {u: p + common for u, p in out.items()}
