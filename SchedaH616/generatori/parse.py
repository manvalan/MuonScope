import re, json, sys
t = open(sys.argv[1]).read().splitlines()
# Table 4-2: righe dalla "SDRAM" fino a "4.3. GPIO Multiplex"
s = next(i for i, l in enumerate(t) if l.strip() == "SDRAM")
e = next(i for i, l in enumerate(t) if l.startswith("4.3. GPIO Multiplex"))
BALL = r"[A-V]\d{1,2}"
balls, pend, group = {}, [], None
for l in t[s:e]:
    x = l.strip()
    if not x or "Copyright" in x or x.startswith(("Ball", "State", "Pin Desc")) or x == "Pin Description":
        continue
    m = re.match(rf"^((?:{BALL},?)+)\s+([A-Z][A-Z0-9_]+)\s+(I/O|I|O|OD|A|AI|AO|AI/O|P|G)\b", x)
    if m:
        bl = [b for b in m.group(1).split(",") if b]
        for b in pend + bl:
            balls[b] = (m.group(2), m.group(3), group)
        pend = []
        last = m.group(2), m.group(3)
        continue
    m = re.match(rf"^((?:{BALL},)*{BALL},)$", x)  # ball list continues
    if m:
        pend += [b for b in x.split(",") if b]
        continue
    m = re.match(rf"^((?:{BALL},)*{BALL})$", x)  # final ball list after the name
    if m and not pend:
        for b in x.split(","):
            balls[b] = (last[0], last[1], group)
        continue
    m = re.match(rf"^((?:{BALL},?)+)$", x)
    if m:
        pend += [b for b in x.split(",") if b]
        continue
    m = re.match(r"^\s*([A-Z][A-Za-z0-9 +]+)$", x)
    if m and len(x) < 20:
        group = x
        continue
    m = re.match(r"^([A-Z][A-Z0-9_]+)\s+(I/O|I|O|OD|A|AI|AO|AI/O|P|G)\b", x)
    if m:  # name line whose balls are on the previous/next lines
        last = m.group(1), m.group(2)
        for b in pend:
            balls[b] = (last[0], last[1], group)
        pend = []
        continue
for b in pend:
    balls[b] = (last[0], last[1], group)
pend = []
json.dump({b: list(v) for b, v in sorted(balls.items())}, open(sys.argv[2], "w"), indent=0)
print(len(balls))
