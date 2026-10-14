# Proposta BUS_POWER_MIKILAB a 32 pin

Data 2026-10-13. **SUPERATA il 2026-10-13 da `bus-power-30pin.md` (opzione C, VIN più buck sulla scheda).** Il BUS MIKILAB MAIN a 28 pin (REV5.0) resta invariato.

## Perché

- Il 5V del modulo Power alimenta anche la scheda A133: circa 1 A, fino a 2 A con una periferica USB in host.
- Un contatto FPC da 0.5 mm porta in genere 0.5 A: servono più pin in parallelo per il 5V e per il suo ritorno di massa.
- Il 3V3 dei piani resta basso (sotto 300 mA con 8 piani) ma passa su 2 pin per margine.
- I piani consumano poco, quindi il MAIN non cambia: le schede dei piani restano compatibili.

## Pinout (connettore FPC/FFC 32 pin, passo 0.5 mm, stessa famiglia del MAIN)

| Pin | Segnale | Note |
|---|---|---|
| 1 | GND_A | |
| 2 | V_BIAS_1 | +24 V |
| 3 | V_BIAS_2 | |
| 4 | GND_A | Separa il bias dai riferimenti |
| 5 | 2V5_REF | |
| 6 | 1V25_REF | |
| 7 | GND_A | |
| 8 | GND_D | Separa la sezione analogica da quella di potenza |
| 9-13 | 5V | 5 pin in parallelo, 2.5 A di portata nominale |
| 14-18 | GND_D | Ritorno del 5V, 5 pin |
| 19, 20 | 3V3 | Per i piani, 2 pin |
| 21 | GND_D | |
| 22 | SPI_SCLK | |
| 23 | SPI_MOSI | |
| 24 | SPI_MISO | |
| 25 | GND_D | Schermo tra SPI e controlli |
| 26 | SPI_INA239A_CS | |
| 27 | SPI_INA239B_CS | |
| 28 | SPI_DAC_CS | |
| 29 | VREF_ENABLE | |
| 30 | VBIAS_ENABLE | |
| 31 | DAC61402_FAULT | Open-drain |
| 32 | GND_D | |

## Lato scheda A133

- I pin 9-13 entrano nella scheda come terza sorgente: un ideal diode (es. LM66100) in OR con il jack DC, a monte del TPS2121. Lo stesso nodo 5V va anche al pin 2 del MAIN verso i piani.
- Sul modulo Power: un fusibile o un limitatore sul 5V e sul 3V3, tarato sotto la portata totale dei pin.
- Assegnazione dei pin dell'A133 invariata rispetto a interfaccia-bus-mikilab.md §3.

## Alternativa

Lasciare il BUS_POWER a 22 pin com'è e portare il 5V della scheda su un connettore di potenza separato (morsetto o JST a 2-4 poli).
