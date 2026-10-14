# BUS_POWER_MIKILAB a 30 pin (opzione C)

Data 2026-10-13. **Scelta da Michele il 2026-10-13**: sostituisce la bozza a 32 pin (`bus-power-32pin-proposta.md`, superata). Il BUS MIKILAB MAIN a 28 pin resta alla REV5.0.

## Perché

- Il 5V del bus viene da un buck AP63205 da 2 A e alimenta gli OPA4172 di precisione dei piani. Se ci si attacca la scheda A133 (fino a circa 1.7 A), il buck lavora al limite e il rumore del SoC arriva agli stadi analogici.
- I piani consumano poco: con 8 piani, 51 mA sul 5V e 148 mA sul 3V3 (valori misurati da Michele). Restano sui pin di oggi, con un secondo pin 3V3 per margine.
- La scheda A133 prende il VIN del modulo Power su pin dedicati e si fa il suo 5V con un buck locale.
- I pin 1-22 sono identici al connettore a 22 pin attuale.

## Pinout (FPC 30 pin passo 0.5 mm, es. Hirose FH12-30S-0.5SH)

| Pin | Segnale | Note |
|---|---|---|
| 1-22 | Come il BUS_POWER a 22 pin | Vedi interfaccia-bus-mikilab.md §3 |
| 23 | GND_D | Separa i segnali dalla sezione VIN |
| 24, 25, 26 | VIN_SYS | VIN del modulo Power, 3 pin in parallelo (1.5 A nominali) |
| 27, 28 | GND_D | Ritorno del VIN |
| 29 | 3V3 | Secondo pin 3V3 per i piani, in parallelo al pin 9 |
| 30 | GND_D | |

Corrente su VIN_SYS: a 12 V la scheda (circa 8.5 W con l'USB host) assorbe circa 0.8 A con un buck al 90 %, quindi 3 pin da 0.5 A hanno margine. VIN = 12 V (confermato da Michele il 2026-10-13): il TPS563201 (4.5-17 V) va bene.

## Lato scheda A133

- VIN_SYS → buck da VIN a 5 V, 3 A (es. TI TPS563201, ingresso 4.5-17 V) → ideal diode LM66100 → stesso nodo del jack DC, a monte del TPS2121.
- Il 5V del bus (pin 8) non alimenta la scheda: passa solo al MAIN pin 2 verso i piani.
- Sul modulo Power: fusibile o limitatore su VIN_SYS.
