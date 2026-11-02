# Scheda i.MX 6ULL con sola microSD: placement

Generato da `generatori/build_pcb.sh`. Solo placement, **nessuna pista**. Immagini: `../pcb-placement-imx6ull-sd.pdf` e `.png`.

## Scheda

- **80 x 100 mm** (Michele, 2026-11-02; la versione SSD è 120 x 143). Angoli raggiati 3 mm, quattro fori NPTH da 2.2 mm a 4 mm dai bordi con keepout di raggio 3.2 mm.
- **4 strati**, stackup JLC04161H-3313 da 1.6 mm: F.Cu segnali, In1 GND, In2 alimentazioni a isole, B.Cu segnali.
- Piste minime 0.127 mm (5 mil), 0.1016 mm (4 mil) ammessi sotto il courtyard di qualsiasi componente, su entrambi i lati; distanza 0.1 mm, via 0.45/0.2 mm con dogbone sotto le BGA. Regola provata in DRC con piste di prova.
- 229 componenti: 190 sul top, 39 sul bottom (Michele, 2026-11-02: il bottom si può usare): microSD J5, decoupling sotto U1 e U2, passivi lenti. Nessun pad fuori sagoma (controllato a parte: il DRC ha regole di bordo a 0 mm per SMA, USB-C e microSD).

| Impronta passivi | Pezzi |
|---|---|
| R_0603_1608Metric | 84 |
| C_0603_1608Metric | 66 |
| C_0805_2012Metric | 19 |
| C_1206_3216Metric | 7 |

Spazio tra i courtyard 0.8 mm, 0.3 mm per il disaccoppiamento di SoC e DDR.

## Bottom

| Dove | Componenti |
|---|---|
| Sotto U1, blocco centrale | 8 condensatori: VDD_ARM_CAP e VDD_SOC_CAP 1 uF, VDD_SOC_IN 100 nF, NVCC_DRAM 100 nF. A 0-2.3 mm dalla sfera più vicina del rail |
| Sotto U2, striscia senza sfere | 4 x 100 nF VDD/VDDQ |
| Fuori da U1, lato basso-destro | C109, C110 (VDD_HIGH_CAP), C112 (NVCC_PLL), C113 (VDD_SNVS_CAP), C115 (VDD_USB_CAP): 4-7 mm |
| Altrove | Boot e pull-up (R101-R107), bus (R401-R408, C401), EEPROM, POR_B |

Il bottom resta libero per 12 mm attorno al centro di U1 e tra U1 e U2, salvo il decoupling sopra: serve ai canali del fanout e alla DDR.

**I condensatori non coprono nessun via di segnale** (controllato con via dogbone a 0.4 mm in diagonale dalla sfera), ma **49 via di alimentazione del dogbone cadono sotto o troppo vicino a un pad**. Tra via su passo 0.8 mm resta un canale da 0.35 mm e un pad 0603 è largo 0.9 mm: quelle sfere vanno unite sul top a una sfera vicina dello stesso rail, con meno via e accanto ai pad. Da verificare in sbroglio che il piano di alimentazione regga.

## Fanout a 4 strati: stima, non sbroglio

`generatori/fanout.py`: 145 sfere di segnale. Togliere hub e SSD non aiuta: QSPI_CS1 e PREFIX_0 prendono il posto delle sfere liberate.

| Lato | Anelli 0-1 sul top (canali 33) | Anelli >= 2 sul bottom (canali 15) |
|---|---|---|
| Alto | 17 | 13 |
| Basso | 24 | 11 |
| Sinistra (DRAM) | 26 | 16 |
| Destra | 21 | 17 |

Sul bottom **57 segnali su 60 canali**: margine piccolo, come nella versione SSD. La prova col router a griglia è in `../SchedaIMX6ULL/docs/pcb-placement.md`, non conclusiva per la DDR e non ripetuta qui.

## Dove sta cosa

| Zona | Componenti |
|---|---|
| Centro-sinistra | U1 i.MX 6ULL, sotto a sinistra U2 DDR3L |
| Sopra il SoC | U5 NOR e U40 NAND, vicino alle sfere NAND |
| Bordo alto | J12 MAIN, J11 BUS_POWER, ESD e passivi sotto |
| In alto a sinistra | U35 Wi-Fi + U.FL J14; sul bottom J5 microSD |
| Bordo destro | J1 RJ45, sotto U7 PHY con Y3 e terminazioni: l'angolo in alto a destra resta libero |
| A destra del SoC | buck U26, U27 |
| In basso, al centro | buck U23 + L2 (3.3 V), nel posto liberato dalla pila |
| In basso a sinistra | U11 NEO-M9N, J4 SMA, J7 |
| Bordo basso | J3 e J8 USB-C affiancate; a destra U22/L1 12 -> 5 V e U17 |

## Esito

**DRC 0 violazioni, parità schema/PCB 0 problemi**, 0 errori di footprint. Il report elenca 499 collegamenti da fare (nessuna pista).

## Da rivedere in layout

- 12 V da J11 a U22 circa 87.2 mm in linea d'aria: pista larga o isola su In2.
- PHY-RJ45 circa 10-17 mm, RMII SoC-PHY circa 31 mm, USB2 verso U10 circa 39 mm in linea d'aria.
- Bus QSPI condiviso tra U5 e U40: tratti corti e simili verso i due chip.
- Sotto il pad centrale di U40 niente via scoperte (datasheet Winbond).
