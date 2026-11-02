# Scheda i.MX 6ULL (MuonScope)

Scheda Linux con NXP **i.MX 6ULL** (MCIMX6Y2CVM08AB, MAPBGA-289 14x14 passo 0.8) sul bus MIKILAB: DDR3L 1 GB, boot da QSPI NOR, rootfs su SSD M.2 2242 SATA via USB, Ethernet 10/100, Wi-Fi/BT SDIO, GNSS NEO-M9N con PPS ed EXTINT su GPT1. BOM approvata in `bom/`.

| Percorso | Cosa |
|---|---|
| `progetto-kicad/` | Progetto KiCad 10 `SchedaIMX6ULL.kicad_pro`, simboli `Scheda.kicad_sym`, footprint `Scheda.pretty` |
| `schema-imx6ull.pdf` | Schema completo (10 pagine) |
| `pcb-placement-imx6ull.pdf` / `.png` | Placement, top e bottom |
| `docs/scelte-progetto.md` | Fonti, assegnazione dei pin, differenze dalla BOM, **punti da verificare** |
| `docs/pcb-placement.md` | Scheda, stackup, regole, stima di fanout, esito DRC |
| `docs/pinmap-imx6ull.md` | Mappa sfera per sfera con la net |
| `generatori/` | Script Python: `build.sh` rifà lo schema, `build_pcb.sh` il PCB, `fanout.py` la stima di fanout, `prova_fanout.py` la prova con router a griglia |

Servono python3, KiCad 10 e la libreria [MIKILAB](https://github.com/manvalan/mikilab-kicad-library) (variabile `MIKILAB`, o clonata in `~/Develop/mikilab-kicad-library`).

```bash
sh SchedaIMX6ULL/generatori/build.sh
sh SchedaIMX6ULL/generatori/build_pcb.sh
```

## Schema

Gerarchico. Nel foglio radice `SchedaIMX6ULL.kicad_sch` la CPU sta a sinistra e gli altri otto fogli a destra, collegati da fili e bus dritti tra i pin (bus `DDR_A[0..15]`, `DDR_DQ[0..15]`, `DDR_BA[0..2]`). Nei sottofogli i segnali tra fogli sono etichette gerarchiche; alimentazioni e masse restano etichette globali e non sono disegnate nel foglio radice.

## Stato

- Schema: **ERC 0 violazioni** (KiCad 10.0.7), nessuna net con un solo pin.
- PCB: **120 x 143 mm, 4 strati**, solo placement. **DRC 0 violazioni, parità schema/PCB 0 problemi**; non c'è nessuna pista.
- 272 componenti, di cui 210 passivi (minimo 0603).
- **Non sbrogliato**: i 4 strati sono una scelta di Michele; il fanout è solo stimato e il margine è piccolo (vedi `docs/pcb-placement.md`).
