import re
LIB = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
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
