"""Footprint di progetto: copia del quarzo 32.768 kHz della libreria MIKILAB senza la serigrafia sul pad (come SchedaIMX6ULL-SD).
Uso: python3 gen_fp.py ../progetto/Scheda.pretty"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kilib import block, mik_fp_dir

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def local_copy(nick, name, drop_layers=()):
    txt = open(os.path.join(mik_fp_dir(nick), name + ".kicad_mod")).read()
    for m in reversed(list(re.finditer(r"\(fp_(?:line|arc|circle|rect|poly)\b", txt))):
        b = block(txt, m.start())
        if any(f'(layer "{L}")' in b or f"(layer {L})" in b for L in drop_layers):
            txt = txt[:m.start()] + txt[m.start() + len(b):]
    open(os.path.join(OUT, name + ".kicad_mod"), "w").write(txt)


local_copy("MIKILAB_Q13FC1350000400", "FC-135R_L3.2-W1.5", ("F.SilkS",))
