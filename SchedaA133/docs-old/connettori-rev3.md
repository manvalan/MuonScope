# Connettori BUS_POWER e MAIN: proposta rev. 3

Data 2026-10-14. Parte da `interfaccia-bus-mikilab.md` rev. 2 e dalle indicazioni di Michele del 2026-10-13:
- la scheda A133 fa passare tutto direttamente ai piani;
- l'unica eccezione possibile è il 5 V, che servirebbe anche ad alimentare il PMIC della scheda A133.

## 1. Le correnti del simulatore non sono carichi reali

| Rail | Misurato a regime (1 piano) | "Picco" del simulatore | Da dove viene il picco |
|---|---|---|---|
| 5V | 6.4 mA | 6.21 A | Circa 2 volte il limite di corrente di un regolatore AP6320x (~3 A) |
| 3V3 | 18.5 mA | 3.15 A | Circa il limite di corrente dell'AP63203 sul modulo Power |

Come dice Michele, il simulatore ha preso la corrente massima dei regolatori, non il consumo dei piani. Inoltre il modulo Power non può erogare più di 2 A continui per rail: AP63205 e AP63203 sono buck da 2 A.

**Stima realistica**, con il massimo di 8 piani (PREFIX a 3 bit):

| Rail | 8 piani a regime | Con margine x3 (commutazione a 20 MHz, spunto) | Pin FPC necessari (0.5 A per contatto, FH12/XUNPU) |
|---|---|---|---|
| 5V analogico | 51 mA | ~0.15 A | 1 |
| 3V3 logica | 148 mA | ~0.45 A | 1, al limite: meglio 2 |

Le piste: 0.60 mm (5 V) e 0.40 mm (3V3) vanno bene ma sono sovradimensionate. Con 1 oz bastano 0.30 mm. Le lascerei per la caduta di tensione lungo la catena.

## 2. Il 5V della scheda A133: perché non dal 5V del bus

La scheda A133 assorbe circa 4 W (0.8 A a 5 V), più fino a 0.9 A se alimenta una periferica USB in modalità host. Totale fino a ~1.7 A. Prenderla dal pin 5V del BUS_POWER crea tre problemi:

1. Servirebbero almeno 4 pin in parallelo, mentre oggi c'è solo il pin 8.
2. L'AP63205 da 2 A dovrebbe alimentare insieme l'A133 e gli stadi analogici di tutti i piani.
3. Il 5V del bus è la **alimentazione di precisione degli OPA4172** (specifica REV5.0, pin 2). Il carico a impulsi di SoC, Wi-Fi e DDR ci metterebbe rumore proprio dove si misurano i muoni.

| Opzione | Cosa cambia | Pro | Contro |
|---|---|---|---|
| A. Alimentazione propria (com'è ora) | Niente: USB-C e jack DC sulla scheda A133 | Zero modifiche al modulo Power | Due alimentatori nel sistema |
| B. 5V_SYS dedicato | Nuovo buck 5 V / 3 A sul modulo Power, 4 pin 5V_SYS + 4 GND_D | Un solo alimentatore | Nuovo regolatore sul modulo Power, molti pin |
| **C. VIN passante (consigliata)** | Il VIN del modulo Power (12 V? da confermare) passa su 3 pin; sulla scheda A133 un buck 12 → 5 V entra nel mux TPS2121 come terza sorgente | Un solo alimentatore, pochi pin (0.7 A a 12 V), nessun carico digitale sul 5V analogico | Un buck in più sulla scheda A133 |

## 3. BUS_POWER: da 22 a 30 pin (opzione C)

I pin 1-22 restano identici alla rev. 2, così lo schema del modulo Power cambia solo per i pin nuovi. Connettore: Hirose FH12-30S-0.5SH (stessa serie del FH12-22S di J3).

| Pin | Segnale | Note |
|---|---|---|
| 1-22 | invariati | Come in `interfaccia-bus-mikilab.md` §3 |
| 23 | GND_D | Ritorno del VIN |
| 24, 25, 26 | VIN_SYS | VIN 12 V del modulo Power. 3 x 0.5 A = 1.5 A disponibili, ne servono ~0.7 A |
| 27, 28 | GND_D | Ritorni |
| 29 | 3V3 | Secondo pin del 3V3 del bus, in parallelo al pin 9 |
| 30 | GND_D | Chiusura del bordo |

**Deciso da Michele il 2026-10-13:** opzione C, VIN = 12 V, pinout come sopra.
Sulla scheda A133: VIN_SYS → buck TPS563201 (12 → 5 V, 3 A) → ideal diode LM66100 → nodo del jack DC, a monte del TPS2121. Il 5V del bus (pin 8) va solo al MAIN pin 2.

Con l'opzione A basta aggiungere il secondo pin 3V3: si può restare a 22 pin, usando uno dei 4 GND_D (es. pin 22 → 3V3, ne restano 3).

## 4. MAIN 28 pin: lo lascerei com'è

Tutti i segnali della REV5.0 passano già direttamente ai piani. 5 V e 3V3 stanno nei limiti con un pin ciascuno anche con 8 piani (§1). Cambiare la piedinatura vorrebbe dire rifare J_IN e J_OUT di **tutti** i piani e la specifica approvata.

Se invece vuoi più margine sul 3V3, l'unica modifica sensata è il pin 4 (GND "isolamento sezione potenza") → 3V3. Restano 5 GND (1, 7, 10, 16, 28), ma la specifica va portata a REV6.0 e i piani rifatti.

## 5. Da decidere

1. Opzione A, B o C per alimentare la scheda A133.
2. Tensione del VIN del modulo Power (dalle capacità da 25 V in ingresso sembra 12 V).
3. MAIN: lasciarlo REV5.0 (consigliato) o passare a REV6.0 con il pin 4 a 3V3.
4. Livello di riposo di VREF_ENABLE (ancora aperto).
