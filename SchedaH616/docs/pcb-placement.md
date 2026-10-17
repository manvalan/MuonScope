# Scheda RK3568: placement del PCB

Generato da `generatori/build_pcb.sh` (netlist dallo schema → `gen_pcb.py`, con il Python di KiCad 10). Solo placement, **nessuna pista**.
Immagini: `../pcb-placement-rk3568.pdf` (pagina 1 top, pagina 2 bottom vista da sotto) e `../pcb-placement-rk3568.png`.

## Scheda

- **70 x 90 mm** (dal 2026-10-17, prima 50 x 70), angoli smussati 3 mm. Quattro fori NPTH da 2.2 mm (MountingHole_2.2mm_M2) a 4 mm dai bordi, con keepout di raggio 3.2 mm su tutti gli strati rame.
- 6 strati, spessore 1.6 mm.
- Regole: piste minime 0.127 mm (5 mil, anche sugli interni), distanza 0.1 mm, via minime 0.25/0.15 mm (via-in-pad JLCPCB POFV sotto l'RK3568, regola in `SchedaRK3568.kicad_dru`), via di default 0.45/0.2 mm, distanza dal bordo 0.3 mm (0 per le SMA a bordo scheda).
- Footprint del SoC `Scheda:Rockchip_FCBGA-636_19x19mm_P0.65mm` generato da `generatori/gen_fp.py`: pad NSMD 0.30 mm; tra due pad restano 0.35 mm, giusto per una pista da 5 mil con 0.1 mm per lato.
- Componenti specifici con simbolo e footprint della libreria MIKILAB (vedi `scelte-progetto.md`).
- I riferimenti sono sul livello Fab: a questa densità la serigrafia degli 0402/0201 non ci sta.

## Lati

- **Top: 364 componenti**, tutto tranne il disaccoppiamento sotto le BGA e la microSD.
- **Bottom: 75 componenti**: i 59 condensatori di disaccoppiamento del RK3568 (C305-C363) tutti sotto il package, i 15 della DDR4 (C404-C418) tutti sotto la DDR4, come chiede il reference Rockchip ("caps should be placed under the U1000 package"), e lo slot microSD J401 sul bordo sinistro.
- Il placer prova prima il top (entro 30 mm dal componente con cui il passivo condivide più net, poi su tutta la scheda) e usa il bottom solo se sul top non c'è posto: con 70 x 90 non è mai servito. Il disaccoppiamento di SoC e DDR4 è ancorato al suo package anche quando la net è in comune con la PMIC.

## Passivi

Minimo 0402, niente 0201 (richiesta di Michele, 2026-10-17: troppo piccoli). 0603 di default; 0402 solo dove serve:
- disaccoppiamento di RK3568 e DDR4 sotto le BGA (100 nF, 1 nF, 1 uF, 4.7 uF);
- serie 22R RGMII (TX vicino al SoC, RX vicino al PHY), serie dei clock eMMC/microSD/SDIO, 2.2R USB, DDR_RZQ 120R, ZQ 240R e rete VREF della DDR4.

| | 0402 | 0603 | 0805 e più |
|---|---|---|---|
| Condensatori | 60 | 133 | 16 |
| Resistenze | 24 | 133 | - |

Storia: all'inizio condensatori 29 x 0201, 120 x 0402, 44 x 0603 e resistenze 157 x 0402; poi 0603 di default; ora anche i 29 da 0201 sono 0402.
Con 59 condensatori 0402 sotto una BGA da 0.65 mm con via-in-pad lo spazio va verificato in sbroglio: dove un 0402 non entra tra le via, va sul bottom appena fuori dall'ombra del package.

## Dove sta cosa (coordinate dall'angolo in alto a sinistra)

| Zona | Componenti |
|---|---|
| Centro | RK3568 (U301, x 25-45, y 35-55) ruotato di 180°: A1 in basso a destra. Angolo DDR verso la DDR4, GMAC0/SDMMC0/eMMC in basso a sinistra, SDMMC2/I2C0/GPIO verso l'alto |
| Sotto il SoC, a destra | DDR4 K4AAG165WA (U401, x 36-50, y 56-67) subito sotto l'angolo DDR (righe A-F, colonne 1-18), ruotata di 90° |
| Bordo alto | J1 BUS_POWER 30 pin (x 11-29) e J2 MAIN 28 pin (x 41-60), entrambi sul top, ingresso cavo sul bordo; ESD del bus vicino ai connettori |
| Tra bus e SoC | RK809-5 (U201) con i 5 induttori 2520 e il quarzo 32.768 kHz, TCS4525 (U202) + 0.33 uH verso VDD_CPU, TPS563201 (U203) |
| In alto a sinistra | jack 5 V (J103) sul bordo sinistro, TPS56637 + L101 e TPS2121 U108 vicino al BUS_POWER |
| Sinistra | microSD (J401) sul bottom con apertura sul bordo sinistro, eMMC (U402) sul top vicino all'angolo EMMC/SDMMC0 del SoC |
| In alto a destra | NEO-M9N (U701) con la SMA d'antenna J701 sul bordo destro accanto all'ingresso RF; AP6256 (U601) subito sotto, vicino alle sfere SDMMC2 |
| Bordo destro | SMA J701 (antenna GNSS), J702 (PPS OUT), J703 (STROBE IN) |
| In basso a destra | CR1220 (BT701), header PPS/STROBE J704 |
| In basso | RJ45 J501 (sinistra), PHY RTL8211F (U501) tra l'angolo GMAC0 del SoC e l'RJ45; le due USB-C affiancate sul bordo basso: host J801 (x 35.5) con TPS2553 (U801) e USBLC6 (U802), alimentazione/OTG J104 (x 47.5) con TPS2121 (U103), FUSB302B (U104), TPD2EUSB30 (U107), TVS (D102) e SY6280 (U105) accanto; tasti RESET/RECOVERY e console J301 a sinistra |

## Esito

- **DRC**: 0 violazioni. Restano 499 collegamenti da fare (nessuna pista). **Parità schema/PCB: 0 problemi.** Schema invariato (ERC 0).
- **Componenti**: piazzati tutti e 439 (364 top, 75 bottom).

## Da rivedere in layout

- I 0402 di disaccoppiamento vanno tra i via-in-pad del SoC; verificare con le regole JLCPCB (via 0.25/0.15 POFV).
- DDR4: linee dati sul lato destro-basso del SoC, CA sul lato basso; tenere i byte in gruppo e la lunghezza secondo la RK3568 High Speed PCB Design Guide.
- AP6256 e NEO-M9N sono vicini (antenne su U.FL e SMA): valutare la coesistenza RF.
- Lo stackup a 6 strati è quello di default di KiCad e va allineato a quello di JLCPCB.
