# Scheda i.MX 6ULL con sola microSD (MuonScope)

Variante di `../SchedaIMX6ULL/` senza SSD: niente M.2, bridge JMS578, buck dell'SSD e hub FE1.1s. BOM in `bom/bom-imx6ull-sd.csv`.

- SoC NXP i.MX 6ULL (MCIMX6Y2CVM08AB), DDR3L 1 GB
- **Boot da NOR QSPI 16 MB** (W25Q128JV, SS0), **rootfs UBIFS su SPI NAND SLC 512 MB** (W25N04KV, SS1), microSD per dati o boot alternativo
- USB-C 1 device/download seriale e alimentazione, USB-C 2 host diretta su USB_OTG2
- Ethernet 10/100, Wi-Fi/BT SDIO, GNSS NEO-M9N con PPS ed EXTINT su GPT1, bus MIKILAB

| Percorso | Cosa |
|---|---|
| `progetto-kicad/` | Progetto KiCad 10 `SchedaIMX6ULL-SD.kicad_pro` |
| `schema-imx6ull-sd.pdf` | Schema gerarchico completo |
| `pcb-placement-imx6ull-sd.pdf` / `.png` | Placement, top e bottom |
| `docs/scelte-progetto.md` | Differenze dalla versione SSD, **punti da verificare** |
| `docs/pcb-placement.md` | Scheda, stackup, regole, stima di fanout, esito DRC |
| `docs/pinmap-imx6ull.md` | Mappa sfera per sfera con la net |
| `generatori/` | `build.sh` rifà lo schema, `build_pcb.sh` il PCB, `fanout.py` la stima di fanout |

```bash
sh SchedaIMX6ULL-SD/generatori/build.sh
sh SchedaIMX6ULL-SD/generatori/build_pcb.sh
```

## Stato

- Schema gerarchico, **ERC 0 violazioni**.
- PCB **100 x 125 mm, 4 strati**, solo placement, **DRC 0 violazioni, parità schema/PCB 0 problemi**. 232 componenti, di cui 177 passivi.
- **Non sbrogliato**: il fanout a 4 strati è solo stimato, con margine piccolo.
