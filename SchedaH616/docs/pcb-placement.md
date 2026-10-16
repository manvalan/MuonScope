# Scheda RK3568: placement del PCB

Generato da `generatori/build_pcb.sh` (netlist dallo schema → `gen_pcb.py`, con il Python di KiCad 10). Solo placement, **nessuna pista**.
Immagini: `../pcb-placement-rk3568.pdf` (pagina 1 top, pagina 2 bottom vista da sotto) e `../pcb-placement-rk3568.png`.

## Scheda

- 50 x 70 mm, angoli smussati 3 mm. Quattro fori NPTH da 2.2 mm (MountingHole_2.2mm_M2) a 4 mm dai bordi, con keepout di raggio 3.2 mm su tutti gli strati rame.
- 6 strati, spessore 1.6 mm.
- Regole: piste minime 0.127 mm (5 mil, anche sugli interni), distanza 0.1 mm, via minime 0.25/0.15 mm (via-in-pad JLCPCB POFV sotto l'RK3568, regola in `SchedaRK3568.kicad_dru`), via di default 0.45/0.2 mm, distanza dal bordo 0.3 mm (0 per le SMA a bordo scheda).
- Footprint del SoC `Scheda:Rockchip_FCBGA-636_19x19mm_P0.65mm` generato da `generatori/gen_fp.py`: pad NSMD 0.30 mm; tra due pad restano 0.35 mm, giusto per una pista da 5 mil con 0.1 mm per lato.
- RK809-5 su `Package_DFN_QFN:ArtInChip_QFN-68-1EP_7x7mm_P0.35mm_EP5.49x5.49mm` (pad 0.25 mm, distanza tra pad 0.1 mm), TCS4525 su WLCSP-20 0.4 mm, DDR4 su `Package_BGA:BGA-96_9.0x13.0mm_Layout2x3x16_P0.8mm`.
- I riferimenti sono sul livello Fab: a questa densità la serigrafia degli 0402/0201 non ci sta.

## Dove sta cosa

| Zona | Lato | Componenti |
|---|---|---|
| Centro | top | RK3568 (U301) ruotato di 180°: A1 in basso a destra. Angolo DDR verso la DDR4, GMAC0/SDMMC0/eMMC in basso a sinistra, SDMMC2/I2C0/GPIO verso l'alto |
| Sotto il SoC | top | DDR4 K4AAG165WA (U401) subito sotto l'angolo DDR (righe A-F, colonne 1-18), ruotata di 90° |
| Sotto le sfere | bottom | Disaccoppiamento: 45 dei 54 condensatori del foglio CPU sotto il SoC, 13 dei 15 della DDR4 sotto la DDR4 (gli altri accanto) |
| Bordo alto | top / bottom | J1 BUS_POWER 30 pin (top) e J2 MAIN 28 pin (bottom), ingresso cavo sul bordo; ESD del bus sul bottom vicino |
| Tra bus e SoC | top | RK809-5 (U201) con i 5 induttori 2520 e il quarzo 32.768 kHz; sul bottom TCS4525 (U202) + 0.33 uH, TPS563201 (U203) + 2.2 uH |
| In alto a sinistra | top / bottom | USB-C di alimentazione/OTG (J104) e jack 5 V (J103) sul bordo sinistro; TPS56637 + L101, TPS2121, FUSB302B, SY6280 sul bottom |
| In alto a destra | top | NEO-M9N (U701) con la SMA d'antenna J701 sul bordo destro accanto all'ingresso RF |
| In alto a destra | bottom | AP6256 (U601) sotto il NEO, vicino alle sfere SDMMC2; U.FL J601 vicino |
| Bordo destro | top+bottom | SMA J701 (antenna GNSS), J702 (PPS OUT), J703 (STROBE IN) |
| Sinistra | top | eMMC (U402) vicino alle sfere EMMC; sotto, tasti RESET/RECOVERY, console J301, AP2112K |
| Sinistra | bottom | microSD (J401), apertura sul bordo sinistro, vicino a SDMMC0 |
| In basso | top | RJ45 J501 (sinistra) e USB-C host J801 (centro) con TPS2553 e USBLC6, header PPS/STROBE J704 |
| In basso | bottom | PHY RTL8211F (U501) tra GMAC0 e RJ45, CR1220 (BT701) in basso a destra |

I passivi sono messi in automatico vicino al componente con cui condividono più net: prima lo stesso lato entro 7 mm, poi entrambi i lati, infine dovunque ci sia posto.

## Esito

- **DRC**: 0 violazioni. Restano 499 collegamenti da fare (nessuna pista). **Parità schema/PCB: 0 problemi.**
- **Componenti**: piazzati tutti e 439 (150 top, 289 bottom).
- Rispetto alla SchedaH616: tolto l'eFuse, tolti TCA6416A e AXP313A, aggiunti RK809-5, TCS4525, i due AP2112K, ferriti USB e molti più condensatori (reference Rockchip).

## Da rivedere in layout

- La scheda è piena: 289 componenti sul bottom. Montaggio su due lati.
- Le 0201 di disaccoppiamento vanno tra i via-in-pad del SoC; verificare con le regole JLCPCB (via 0.25/0.15 POFV).
- DDR4: tutte le linee dati sul lato destro-basso del SoC, CA sul lato basso; tenere i byte in gruppo e la lunghezza secondo la RK3568 High Speed PCB Design Guide.
- AP6256 sotto il NEO-M9N: valutare la coesistenza RF o spostarlo.
- Il PHY è sul bottom a ~5 mm dall'RJ45: coppie MDI corte. L'RGMII parte dall'angolo GMAC0 del SoC.
- Lo stackup a 6 strati è quello di default di KiCad e va allineato a quello di JLCPCB.
