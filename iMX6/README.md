# iMX6: scheda i.MX 6ULL derivata da nanoberry

Derivata da **nanoberry** di **vpecanins** ([github.com/EnzoRF/nanoberry](https://github.com/EnzoRF/nanoberry), commit 63c6836, 2020-06-13), **GPLv3**: vedi `LICENSE`. Copyright (C) 2020 vpecanins per il progetto originale. L'autore chiede di essere avvisato se la scheda viene prodotta o modificata: **va avvisato da Michele**.

Il progetto originale, intatto (KiCad 5), è in `nanoberry-originale/`.

## Cosa cambia rispetto a nanoberry

| | nanoberry | iMX6 |
|---|---|---|
| RAM | DDR3L 512 MB (W634GU6MB) | **DDR3L 1 GB** Alliance AS4C512M16D3LC-12BIN, FBGA-96 9x13, stessa griglia; A15 era già collegata e sbrogliata |
| Display | connettore RGB P2 + touch J6 | tolti |
| Espansione | header 2x20 P1 | tolto: i suoi pad CSI/UART servono ai bus |
| USB | hub USB2514B, 2 USB-A, micro-USB OTG, micro-USB debug con CP2102N | **USB-C 1** alimentazione + OTG1 (boot seriale), **USB-C 2 host** su USB_OTG2 con TPS2553, affiancate sul bordo destro |
| Console | CP2102N | header UART1 1x3 (J10) |
| Alimentazione | USB a diodi + LiPo con boost MIC2877 | **BUS_POWER 12 V -> TPS56637 5 V -> TPS2121** (priorità) con la USB-C 1; PF1550, LiPo e boost restano |
| Bus | - | **MIKILAB**: BUS_POWER 30 pin (ECSPI4 sui pad ENET2) e MAIN 28 pin (ECSPI1 sui pad CSI_DATA04-07, I2C1 sui pad UART4, ADDR/PREFIX/ALERT#/HIT# su UART3/UART5/CSI) con ESD |
| Radio | - | **Wi-Fi/BT BL-M8723DS1** su uSDHC2 (pad CSI) e UART2, LDO dedicato, U.FL |
| Scheda | 85 x 56 mm | **85 x 60 mm**, 4 strati: +4 mm in alto per i connettori MIKILAB |

Restano come in nanoberry: i.MX 6ULL, PMIC PF1550, QSPI (2 x W25M512JV), microSD, Ethernet LAN8720A + RJ45, A71CH, JTAG, pila. Strap di boot: i pad LCD_DATA restano liberi.

## Contenuto

| Percorso | Cosa |
|---|---|
| `progetto-kicad/iMX6.kicad_pro` | Progetto KiCad 10 |
| `schema-imx6.pdf` | Schema (12 fogli) |
| `pcb-imx6.pdf`, `.png` | PCB, top e bottom |
| `generatori/` | `converti.py` (schema dalla netlist di nanoberry + modifiche), `aggiorna_pcb.py` (PCB), `build.sh` |
| `nanoberry-originale/` | Progetto originale KiCad 5 |

## Come è stato fatto

KiCad 10 da riga di comando non legge i fogli KiCad 5 di nanoberry, quindi lo schema è **ricostruito dalla netlist originale** (`nano.net`) e dai simboli della sua cache convertiti. Il disegno è a etichette, non quello originale. Il PCB è quello di nanoberry convertito:
- tolti i 43 componenti eliminati e le 821 piste e via che portavano a loro;
- **tutte le altre piste restano come in nanoberry**, comprese DDR e fanout del SoC (nessuna net DDR cambiata);
- i 74 componenti nuovi sono **solo piazzati**, senza piste;
- i 2 fori di fissaggio in alto spostati negli angoli nuovi, quello in basso a sinistra è già nell'angolo, quello in basso a destra resta dov'era perché l'angolo è dell'RJ45.

## Stato e punti aperti

- **ERC 0** (con i tipi dei pin di nanoberry corretti: molti pin bidirezionali erano marcati input).
- **Parità schema/PCB: 0 errori di footprint.**
- **DRC: 1376 violazioni, da rivedere in KiCad.** Su questa macchina il riempimento delle zone di KiCad 10 si blocca (anche sul PCB di nanoberry non modificato), quindi le zone sono **senza riempimento**: aprire il PCB e premere B. Nel conteggio:
  - 199 via di nanoberry da 0.3/0.254 mm: corona di 0.023 mm, **da verificare col produttore**;
  - via e piste "appese" e 499 collegamenti mancanti: in parte zone non riempite, in parte componenti nuovi non sbrogliati;
  - testi e serigrafie di nanoberry sotto i minimi;
  - **14 sovrapposizioni di courtyard, 3 clearance, 4 fori troppo vicini, 2 ponti di maschera: da controllare a mano**.
- **BOOST_EN del MIC2877 è flottante anche in nanoberry** (net con un solo pin): va collegato o forzato.
- **U-Boot**: il setup DDR (DCD e calibrazione) cambia per 1 GB e 8 Gb.
- Segnali Wi-Fi e USB host su pad SNVS_TAMPER (BT_HOST_WAKE, USB2_OC_N): dominio VDD_SNVS, livelli da verificare.
- Il modulo Wi-Fi è sul bottom, l'U.FL sul top.
