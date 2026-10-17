# PCB SchedaTibbo: placement (2026-10-17)

Solo posizionamento, niente piste e niente net: lo schema non esiste ancora, il `.kicad_pcb` e' generato dalla BOM
(`bom-tibbo.csv`) con `generatori/build_pcb.sh` (gen_fp.py + gen_pcb.py, stesso flusso della SchedaH616).
Risultato in `progetto-kicad/SchedaTibbo.kicad_pcb`, `pcb-placement-tibbo.pdf` e `.png` (top e bottom affiancati).

## Scheda
- **60 x 84 mm** invece di 50 x 70 (stesso rapporto circa 0.71): a 50 x 70 non ci sta. SoC 23 x 23 (courtyard),
  RJ45 19 x 22, portapila CR1220 22 x 15, NEO 14 x 17, eMMC 12 x 13, due connettori bus da 19-20 mm: con i 117 passivi
  servono circa 3300 mm² contro i 3500 della 50 x 70, senza spazio per piste e fori.
- 4 strati, 1.6 mm, angoli raggiati 3 mm, 4 fori NPTH 2.2 mm (M2) a 4 mm dagli spigoli con keepout di 3.2 mm su tutti
  gli strati.
- 157 componenti sul top, 1 sul bottom (microSD J5). Passivi tutti 0603 (R/C), 0805 e 1206 per i bulk, 1008 per le
  induttanze dei DC-DC interni del SoC: niente 0402/0201.

## Disposizione
- **Bordo alto**: BUS_POWER J11 (FH12-30) a sinistra e MAIN J12 (FPC-28) a destra. Sotto J11 i buck 12 -> 5 V
  (TPS56637 U22 + XAL6030 L1) e 5 -> 3.3 V (TPS563201 U23 + L2), il TPS2121 U17 e il supervisore U25; sotto J12 le sei
  ESD TPD4E05 U26-U31.
- **Centro**: SP7021-IF U1, eMMC U5 (Samsung KLM8G1GETF 8 GB, FBGA-153 JEDEC: footprint MIKILAB della FORESEE) subito a sinistra, LAN8720A U7 con quarzo Y3 ed EEPROM MAC U6 sotto il SoC verso
  l'RJ45. Quarzi Y1 (27 MHz) e Y2 (32.768 kHz) vicino al SoC.
- **Bordo basso**: RJ45 J1, USB-C OTG J3 e USB-C host J8 affiancate; ESD USBLC6 U9/U10, TPS2553 U24 e TVS D1 subito
  dietro le USB-C.
- **Bordo destro**: SMA d'antenna J4 con il NEO-M9N U11 accanto; sotto, buffer U19/U20, ESD D2/D3 e header
  PPS OUT / EXTINT IN J7 (BOM aggiornata: un solo SMA). Il GNSS sta a oltre 25 mm dai buck e dall'Ethernet.
- CR1220 BT1 con BAT54 D4 tra GNSS e USB, pulsanti SW1/SW2 e header console J6 sul bordo sinistro.
- **Bottom**: solo la microSD J5, apertura sul bordo sinistro.

## DRC
0 violazioni, 0 collegamenti mancanti (non ci sono net).

## Da verificare / note
- **Pad esposto SP7021**: la dimensione non e' nel datasheet pubblico. Footprint di progetto
  `Scheda:LQFP-176-1EP_20x20mm_P0.4mm_EP10x10mm` (LQFP-176 KiCad + EP 10 x 10 mm provvisorio): da correggere sul disegno
  del package Sunplus/Tibbo.
- Footprint MIKILAB corretti solo su questa scheda (gen_pcb.py): BWSMA-KE-P001 disegna un proprio Edge.Cuts (allineato
  al bordo e tolto), CR1220-2 ha i fori di centraggio come PTH senza rame (resi NPTH), TPS2121RUXR ha via termiche con
  corona 0.05 mm (tolte, si rifanno in sbroglio), Q13FC ha il pallino del pin 1 sul pad (tolto). Conviene correggerli
  in libreria.
- I passivi sono generici (conteggi per blocco come /bom-osd32mp1) e piazzati in automatico vicino al loro integrato:
  dopo lo schema vanno riassegnati sulle net vere e il disaccoppiamento del SoC avvicinato ai pin.
