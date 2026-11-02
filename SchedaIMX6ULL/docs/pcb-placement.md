# Scheda i.MX 6ULL: placement del PCB

Generato da `generatori/build_pcb.sh`. Solo placement, **nessuna pista**. Immagini: `../pcb-placement-imx6ull.pdf` (top, poi bottom visto da sotto) e `.png`.

## Scheda

- **120 x 143 mm** (Michele, 2026-11-02: almeno 150% per lato rispetto ai precedenti 80 x 95), angoli raggiati 3 mm, quattro fori NPTH da 2.2 mm a 4 mm dai bordi con keepout di raggio 3.2 mm. Quinto foro H5 per il dado M2 dell'SSD.
- **4 strati**, scelta di Michele.
- 272 componenti: 271 sul top, la microSD J5 sul bottom.

## Passivi

Lo 0603 è il minimo, non una misura obbligata. **210 passivi, 62 in meno dei 272 precedenti.** Impronte standard KiCad:

| Impronta | Pezzi | Pad (mm) | Uso |
|---|---|---|---|
| `Resistor_SMD:R_0603_1608Metric` | 95 | 0.80 x 0.95 | tutte le resistenze |
| `Capacitor_SMD:C_0603_1608Metric` | 82 | 0.90 x 0.95 | fino a 1 uF |
| `Capacitor_SMD:C_0805_2012Metric` | 24 | 1.00 x 1.45 | 22 uF e 10 uF |
| `Capacitor_SMD:C_1206_3216Metric` | 9 | 1.15 x 1.80 | 47 uF, 10 uF/25 V, 22 uF sui rail a 5 V |

Spazio tra i courtyard: 0.8 mm, 0.3 mm per il disaccoppiamento di SoC e DDR. Ogni passivo parte dal pad del componente che serve. Sotto l'SSD ne restano 3.

Più piccoli dello 0603, ma sono semiconduttori della BOM e non passivi: ESD9B5.0ST5G D2 e D3 (SOD-923, 1.0 x 0.6 mm), TPD4E05U06 (USON-10 passo 0.5).

## Stackup e regole

| Strato | Uso | Spessore |
|---|---|---|
| F.Cu | segnali, componenti | 35 um |
| prepreg 3313 | | 0.0994 mm |
| In1.Cu | GND continuo | 15 um |
| core FR4 | | 1.265 mm |
| In2.Cu | alimentazioni a isole (3V3, 5V_SYS, V1P35, V1P4) | 15 um |
| prepreg 3313 | | 0.0994 mm |
| B.Cu | segnali | 35 um |

JLC04161H-3313, 1.6 mm. Piste minime 0.127 mm (5 mil), distanza 0.1 mm, via 0.45/0.2 mm con dogbone sotto le BGA, distanza dal bordo 0.3 mm (0 per SMA, USB-C e microSD). Corona libera per il fanout sul top: 2.5 mm attorno a U1, 2 mm attorno a U2.

## Fanout a 4 strati: stima, non sbroglio

La scheda più grande non aiuta il fanout sotto il BGA: quel limite dipende da passo e strati. `generatori/fanout.py` sulla netlist reale: 145 sfere di segnale su 289. Un canale tra due via 0.45 su passo 0.8 è 0.35 mm e contiene una pista da 5 mil (0.327 mm).

| Lato | Anelli 0-1 sul top (canali 33) | Anelli >= 2 sul bottom (canali 15) |
|---|---|---|
| Alto | 17 | 13 |
| Basso | 24 | 11 |
| Sinistra (DRAM) | 25 | 16 |
| Destra | 22 | 17 |

Sul bottom sono **57 segnali su 60 canali**: ci stanno solo usando i canali liberi di alto e basso. Margine piccolo. Precedente: [cebrax/iMX6ULL_tryout](https://github.com/cebrax/iMX6ULL_tryout) è sbrogliata su 4 strati con lo stesso package e DDR3L, ma con piste da 4 mil e 512 MB. Il bottom è libero da componenti, salvo J5 e i pin THT.

## Prova con router a griglia (placement 80 x 95, 2026-11-02)

Freerouting non si è potuto usare: scaricare ed eseguire Java e il router esterno è bloccato dai permessi di questa macchina. `generatori/prova_fanout.py` è un router a griglia 0.1 mm mio, non scrive sul PCB. Limiti: griglia fissa, niente accordo delle lunghezze, niente coppie accoppiate, isole di alimentazione non verificate.

**Esito non conclusivo per la DDR.** Il router non risolve gli incroci DDR nemmeno con uno strato in più, e sul campione di punti di conflitto circa 9 su 10 sono fuori dal BGA: è un limite del router, non una misura dei layer. Non è stata ripetuta sul placement attuale.

| Dopo 6 iterazioni | 4 strati (F, B) | 6 strati (F, In2, B) |
|---|---|---|
| Net DDR senza conflitti | 0 su 51 | 2 su 51 |
| Altri segnali usciti puliti | 83 su 94 | 90 su 94 |

## Dove sta cosa (mm dall'angolo in alto a sinistra)

| Zona | Componenti |
|---|---|
| Centro-sinistra | U1 i.MX 6ULL (x 38-52, y 48-62), A1 in alto a sinistra, disaccoppiamento attorno |
| Sotto il SoC, a sinistra | U2 DDR3L ruotata, righe dati verso il SoC. Corridoio libero per gli indirizzi |
| Bordo alto | J12 MAIN, J11 BUS_POWER, con ESD e passivi sotto i connettori |
| In alto a sinistra | U35 Wi-Fi + U.FL J14; sul bottom J5 microSD |
| Bordo destro | J1 RJ45, U7 PHY e Y3 tra SoC e RJ45 |
| Destra | J13 M.2, SSD 2242 verso il basso (sagoma su F.Fab), foro H5 |
| Tra SoC e M.2 | U38 JMS578, U36 hub, buck U26/U27/U39 |
| In basso a sinistra | U11 NEO-M9N, J4 SMA, J7: lontani da Wi-Fi e buck |
| Bordo basso | J3 e J8 USB-C affiancate, BT1 sopra; a destra U22/L1 12 -> 5 V e U17 mux |

## Esito

- **DRC 0 violazioni, parità schema/PCB 0 problemi**, 0 errori di footprint. Il report elenca 499 collegamenti da fare (nessuna pista).
- Le regole di bordo a 0 mm valgono per SMA, USB-C e microSD: il DRC non controlla che questi connettori restino dentro la scheda. Controllato a parte: nessun pad fuori dalla sagoma.

## Da rivedere in layout

- **Disaccoppiamento di U1 solo sul top**: i condensatori sui rail `_CAP` restano a circa 8-12 mm dalla sfera più vicina, per le sfere al centro del package e la corona di fanout. Il bottom sotto il BGA li porterebbe molto più vicino: da valutare con Michele.
- 12 V VIN_SYS da J11 a U22 è lungo circa 130 mm con questa disposizione: pista larga o isola su In2, oppure spostare U22 verso J11.
- USB dal SoC alle USB-C circa 75 mm, più lunghe di prima con la scheda grande.
- Distanza dello zoccolo M.2 dal foro H5 (41.75 mm) dedotta dai footprint: da controllare sul disegno del connettore scelto.
- Lunghezze DDR, impedenze USB e SATA, separazione delle isole su In2 da definire in sbroglio.
