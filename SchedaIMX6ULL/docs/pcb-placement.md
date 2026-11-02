# Scheda i.MX 6ULL: placement del PCB

Generato da `generatori/build_pcb.sh`. Solo placement, **nessuna pista**. Immagini: `../pcb-placement-imx6ull.pdf` (top, poi bottom visto da sotto) e `.png`.

## Scheda

- **80 x 95 mm**, angoli raggiati 3 mm, quattro fori NPTH da 2.2 mm a 4 mm dai bordi con keepout di raggio 3.2 mm. Quinto foro H5 per il dado M2 dell'SSD.
- **Perché non 70 x 90**: M.2 e RJ45 ci stanno, ma i 272 passivi 0603, tutti sul top e con 0.2 mm tra i courtyard, no: a 70 x 90 ne restavano 15 senza posto e oltre 100 finivano sotto l'SSD.
- 334 componenti: 333 sul top, la microSD J5 sul bottom. 272 passivi tutti 0603 (144 C, 128 R).

## Stackup e regole

| Strato | Uso | Spessore nominale |
|---|---|---|
| F.Cu | segnali, componenti | 35 um |
| prepreg 3313 | | 0.0994 mm |
| In1.Cu | GND continuo | 15 um |
| core | | 0.5 mm |
| In2.Cu | segnali (riferiti a In1) | 15 um |
| prepreg | | 0.24 mm |
| In3.Cu | alimentazioni a isole (3V3, 5V_SYS, V1P35, V1P4) | 15 um |
| core | | 0.5 mm |
| In4.Cu | GND continuo | 15 um |
| prepreg 3313 | | 0.0994 mm |
| B.Cu | segnali | 35 um |

Spessore totale 1.6 mm. **Spessori nominali: vanno allineati allo stackup a 6 strati del produttore prima di calcolare le impedenze.** Piste minime 0.127 mm (5 mil), distanza 0.1 mm, via 0.45/0.2 mm con dogbone sotto le BGA, distanza dal bordo 0.3 mm (0 per SMA, USB-C e microSD).

## Perché 6 strati

Michele aveva chiesto 6 strati, o 4 se si riesce, e ha giudicato difficile farla in 4 (2026-11-02). La stima conferma: a 4 strati restavano 57 segnali su 60 canali.

`generatori/fanout.py` sulla netlist reale (è una stima, **non uno sbroglio**): 145 sfere di segnale su 289. Un canale tra due via 0.45 su passo 0.8 è 0.35 mm e contiene una pista da 5 mil (0.327 mm). In2.Cu raddoppia i canali per gli anelli interni:

| Lato | Anelli 0-1 sul top (canali 33) | Anelli >= 2 su bottom + In2 (canali 30) |
|---|---|---|
| Alto | 17 | 13 |
| Basso | 24 | 11 |
| Sinistra (DRAM) | 25 | 16 |
| Destra | 22 | 17 |

Oltre al margine di fanout, i 6 strati danno a DDR e USB piani di riferimento continui e separano le alimentazioni dai segnali. Costo: scheda più cara.

## Prova a 4 strati (2026-11-02)

Michele ha chiesto di provare anche a 4 strati. Freerouting non si è potuto usare: scaricare ed eseguire Java e il router esterno è stato bloccato dai permessi di questa macchina. Ho scritto `generatori/prova_fanout.py`, un router a griglia 0.1 mm sul placement reale con piste 5 mil e via 0.45/0.2. Non scrive sul PCB. Limiti: griglia fissa, niente accordo delle lunghezze, niente coppie accoppiate, isole di alimentazione non verificate; i segnali non DDR devono solo uscire dalla zona BGA + 3 mm.

**Esito: non conclusivo per la DDR, a 4 come a 6 strati.** Il router non risolve gli incroci DDR nemmeno con uno strato in più, e i conflitti cadono soprattutto fuori dal BGA, nel tratto aperto verso la RAM: è un limite del router, non una misura del numero di strati. Sul campione dei punti di conflitto, 322 su 344 a 4 strati e 279 su 308 a 6 strati sono fuori dal BGA.

| Dopo 6 iterazioni | 4 strati (F, B) | 6 strati (F, In2, B) |
|---|---|---|
| Net DDR senza conflitti | 0 su 51 | 2 su 51 |
| Altri segnali usciti puliti | 83 su 94 | 90 su 94 |

Lasciando girare di più non migliora: 51 net in conflitto dopo 38 iterazioni a 4 strati (fermato dal limite di 25 minuti), circa 50 dopo 40 a 6 strati. L'unico confronto utile è sugli altri segnali, a favore dei 6 strati.

Resta quindi la scelta di 6 strati. Una verifica vera richiede uno sbroglio con Freerouting o a mano.

## Dove sta cosa (mm dall'angolo in alto a sinistra)

| Zona | Componenti |
|---|---|
| Centro-sinistra | U1 i.MX 6ULL (x 22-36, y 29-43), A1 in alto a sinistra |
| Sotto il SoC, a sinistra | U2 DDR3L ruotata, righe dati verso il SoC. Corridoio libero per gli indirizzi |
| Bordo alto | J12 MAIN (x 9-28), J11 BUS_POWER (x 30-50), ESD sotto i connettori |
| In alto a sinistra | U35 Wi-Fi + U.FL J14; sul bottom J5 microSD |
| Bordo destro | J1 RJ45 (y 12-31), con U7 PHY e Y3 tra SoC e RJ45 |
| Destra | J13 M.2 (y 32-42), SSD 2242 verso il basso (sagoma su F.Fab). Sotto l'SSD solo 17 passivi 0603 |
| Tra SoC e M.2 | U38 JMS578, U36 hub, buck U26/U27/U39 |
| In basso a sinistra | U11 NEO-M9N, J4 SMA, J7: lontani da Wi-Fi e buck |
| Bordo basso | J3 e J8 USB-C affiancate, BT1 sopra; a destra U22/L1 12 -> 5 V e U17 mux |

## Esito

- **DRC 0 violazioni, parità schema/PCB 0 problemi**, 0 errori di footprint. Il report elenca 499 collegamenti da fare (nessuna pista).
- Le regole di bordo a 0 mm valgono per SMA, USB-C e microSD: il DRC non controlla che questi connettori restino dentro la scheda, le posizioni vanno viste sul render.

## Da rivedere in layout

- **Passivi del bus MIKILAB lontani da J11/J12** (R401-R427, in media 12-40 mm) e pull-up/strap di U1 (R101-R109, fino a 40 mm): linee lente, ma da riavvicinare a mano.
- **Disaccoppiamento di U1 solo sul top** (regola di Michele): i 100 nF stanno fuori dal package, con induttanza maggiore rispetto al bottom sotto le sfere. Da valutare con il primo prototipo o con la simulazione.
- 12 V VIN_SYS da J11 a U22 percorre circa 80 mm: pista larga o isola su In3.
- Distanza dello zoccolo M.2 dal foro H5 (41.75 mm) dedotta dai footprint: da controllare sul disegno del connettore scelto.
- 17 passivi 0603 sotto l'SSD: altezza libera da verificare con lo zoccolo definitivo.
- Lunghezze DDR, impedenze USB e SATA, separazione delle isole su In3 da definire in sbroglio.
