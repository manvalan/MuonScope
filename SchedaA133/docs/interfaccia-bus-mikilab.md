# Interfaccia scheda A133 ↔ bus MIKILAB

Data 2026-10-13, rev. 4 (BUS_POWER a 30 pin, opzione C). Fonti:
- BUS_POWER_MIKILAB: pinout a 22 pin inviato da Michele, portato a 30 pin il 2026-10-13 (`bus-power-30pin.md`).
- BUS MIKILAB MAIN (28 pin): `MuonScope/docs/mikilab_bus_protocol`, documento BPS-MIKILAB-2026-REV5.1 (REV5.0 approvata + linea di coincidenza HIT# sul pin 28, 2026-10-14).
- Pin dell'A133: tabella pinmux del kernel mainline (`pinctrl-sun50i-a100.c`).

La scheda A133 prende il posto della Mainboard Command ESP32. Fa da master SPI su entrambi i bus ed è la testa della daisy chain.

## 1. Punti chiusi dalla specifica REV5.0

| Punto | Risposta della specifica | Conseguenza sulla scheda A133 |
|---|---|---|
| Logica dei 74HC | Tutta la logica del bus è a **3.3 V** (§1.2) | Collegamento diretto ai banchi PB/PD a 3.3 V, **niente traslatori** |
| Alimentazioni sul MAIN | 5V, 3V3, 2V5_REF, 1V25_REF, V_BIAS_1/2 sono **ingressi** per i piani (arrivano da monte) | La testa della catena (noi) deve fornirle su J_OUT, vedi §4 |
| SPI | Fino a 20 MHz, CS master attivo basso su E1/E2 del 74HC138 | SPI1 hardware, CS0 hardware usato come SPI_CS_MASTER |
| Indirizzamento | PREFIX[0..2] sceglie il piano, ADDR[0..2] il chip; ID piano automatico (+1 per piano) | 6 GPIO d'uscita, ID iniziale 000 su J_OUT |
| SPI_ALERT# | Open-drain wired-OR, **unico pull-up 4.7 kΩ** sul master | Pull-up 4.7 kΩ sulla scheda A133, ingresso con interrupt |
| I2C | Pin 14/15, predisposti per il futuro modulo timing GPS | I2C0 su PD22/PD23, pull-up 2.2 kΩ sul master |
| Connettore | FPC 28 pin passo 0.5 mm, right-angle bottom contact, es. XUNPU FPC-05F-28PH20 | Uno solo sulla scheda A133 (fa da J_OUT) |

## 2. Risorse dell'A133 assegnate

| Risorsa | Pin A133 | Uso |
|---|---|---|
| SPI0 | PC bank | **Non usabile**: condivide i pin con l'eMMC |
| SPI1 su PH | PH4-PH7 | **Non usabile**: pin occupati dall'RGMII |
| **SPI2** | PB0 CS, PB1 CLK, PB2 MOSI, PB3 MISO | BUS_POWER (CS hardware non usato, 3 `cs-gpios`) |
| **SPI1** | PD10 CS, PD11 CLK, PD12 MOSI, PD13 MISO | BUS MAIN |
| **I2C0** | PD22 SCK, PD23 SDA | BUS MAIN pin 14/15 |
| UART0 | PB9, PB10 | Console debug |
| UART1 | PG6-PG9 | Bluetooth AP6256 |
| UART3 | PD14 TX, PD15 RX | GNSS NEO-F10T |
| GPIO | PB4-PB8 | CS ed enable del BUS_POWER |
| GPIO | PD16-PD21 | ADDR e PREFIX del BUS MAIN |
| GPIO con interrupt | PD0, PD1, PD4 | SPI_ALERT#, DAC61402_FAULT, HIT# (PD_EINT4) |

Tutti i pin del banco PD hanno l'interrupt esterno (IRQ bank 2 nel driver). Il banco PD (LCD/LVDS/DSI, non usati) va alimentato a 3.3 V.

**Cambio rispetto alla rev. 1:** DAC61402_FAULT passa da PD22 a PD1, perché PD22/PD23 sono l'unica I2C libera vicino al bus MAIN. UART4 (PD18-PD21) non è più disponibile.

## 3. BUS_POWER_MIKILAB (30 pin) → scheda A133

Il 2026-10-13 Michele ha scelto il connettore a 30 pin (opzione C, `bus-power-30pin.md`): i pin 1-22 restano quelli di oggi, i pin 23-30 portano il VIN del modulo Power alla scheda A133.

| Pin | Segnale | Lato A133 | Note |
|---|---|---|---|
| 1, 4, 7 | GND_A | Massa analogica passante verso il MAIN pin 7 | Sul modulo Power GND_A e GND_D sono già la stessa net: il ponte 0 Ω sulla A133 (R4) è DNP, per non chiudere un anello di massa nella piattina |
| 2, 3 | V_BIAS_1, V_BIAS_2 | Passanti verso il MAIN pin 8, 9 | Bias regolabile fino a circa 30 V, generato da VIN (boost LT8330 a 36 V nel progetto MuonScope): distanza ≥ 0.6 mm dalle altre piste, nessun TVS a 5 V |
| 5, 6 | 2V5_REF, 1V25_REF | Passanti verso il MAIN pin 5, 6 | Piste corte, schermate da GND_A, nessun carico |
| 8 | 5V | Passante verso il MAIN pin 2 | Solo per i piani: **non** alimenta la scheda |
| 9, 29 | 3V3 | Passanti verso il MAIN pin 3 + monitor | Separato dal 3.3 V della scheda, vedi §5 |
| 10, 14, 21, 22, 23, 27, 28, 30 | GND_D | Massa digitale | 27-28 sono il ritorno del VIN |
| 11 | SPI_SCLK | PB1 (SPI2 CLK) | 33 Ω serie vicino al SoC |
| 12 | SPI_MOSI | PB2 (SPI2 MOSI) | 33 Ω serie |
| 13 | SPI_MISO | PB3 (SPI2 MISO) | 33 Ω serie vicino al connettore |
| 15 | SPI_INA239A_CS | PB4 (cs-gpios) | Pull-up 10 kΩ: CS disattivo durante il boot |
| 16 | SPI_INA239B_CS | PB5 (cs-gpios) | Pull-up 10 kΩ |
| 17 | SPI_DAC_CS | PB6 (cs-gpios) | Pull-up 10 kΩ |
| 18 | VREF_ENABLE | PB7, uscita | **Attivo alto** (modulo Power rivisto il 2026-10-14: BSS138 Q3 con pull-up del gate di Q2 a 5 V). Pull-down 10 kΩ (R324): a riposo i riferimenti sono spenti |
| 19 | VBIAS_ENABLE | PB8, uscita | Pull-down 100 kΩ: bias spento finché Linux non lo abilita |
| 20 | DAC61402_FAULT | PD1, ingresso con interrupt | Open-drain: pull-up 10 kΩ sul nostro lato |
| 24, 25, 26 | VIN_SYS | Ingresso del buck locale a 5 V | 3 pin in parallelo |

## 4. BUS MIKILAB MAIN (28 pin) → scheda A133 (testa della catena)

| Pin | Segnale | Lato A133 | Note |
|---|---|---|---|
| 1, 4, 10, 16 | GND | GND_D | Pin 16 è lo schermo centrale della piattina. Il pin 28 non è più GND dalla REV5.1 |
| 2 | 5V | Dal BUS_POWER pin 8 | |
| 3 | 3V3 | Dal BUS_POWER pin 9 e 29 | Alimenta i 74HC dei piani |
| 5 | 2V5_REF | Dal BUS_POWER pin 5 | |
| 6 | 1V25_REF | Dal BUS_POWER pin 6 | |
| 7 | GND (analogica) | GND_A, dal BUS_POWER pin 1/4/7 | La specifica la vuole collegata all'AGND dei piani |
| 8 | V_BIAS_1 | Dal BUS_POWER pin 2 | +24 V |
| 9 | V_BIAS_2 | Dal BUS_POWER pin 3 | |
| 11 | SPI_SCLK | PD11 (SPI1 CLK) | 33 Ω serie vicino al SoC |
| 12 | SPI_MOSI | PD12 (SPI1 MOSI) | 33 Ω serie |
| 13 | SPI_MISO | PD13 (SPI1 MISO) | 33 Ω serie vicino al connettore |
| 14 | I2C_SDA | PD23 (I2C0 SDA) | Pull-up 2.2 kΩ a 3.3 V |
| 15 | I2C_SCL | PD22 (I2C0 SCK) | Pull-up 2.2 kΩ a 3.3 V |
| 17 | SPI_CS_MASTER | PD10 (SPI1 CS0 hardware) | Pull-up 10 kΩ: nessun piano selezionato al boot |
| 18-20 | SPI_ADDR_0..2 | PD16, PD17, PD18 | Uscite GPIO, 100 Ω serie |
| 21-23 | SPI_PREFIX_0..2 | PD19, PD20, PD21 | Uscite GPIO, 100 Ω serie |
| 24 | SPI_ALERT# | PD0, interrupt sul fronte di discesa | **Unico** pull-up della linea, 4.7 kΩ a 3.3 V |
| 25-27 | SPI_ID_0..2 | GND tramite 0 Ω | ID iniziale 000: il primo piano ha ID 0 e passa 1 al successivo |
| 28 | HIT# (REV5.1) | PD4 (PD_EINT4), interrupt sul fronte di discesa | Linea di coincidenza open-drain, attiva bassa, impulso 100-200 ns per evento. **Unico** pull-up 4.7 kΩ a 3.3 V (R336), ESD su U307. R337 0 Ω DNP la porta anche sull'ingresso time mark (EXTINT) del NEO-F10T: da montare solo senza STROBE esterno |

Sequenza di una transazione (come nel firmware ESP32): scrivi PREFIX e ADDR sui GPIO, poi trasferimento `spidev` su SPI1: il CS hardware abbassa E1/E2 del 74HC138 del piano scelto. L'MCP23S17 dei piani è sempre ADDR = 7 e va a massimo 10 MHz. Il bus regge fino a 20 MHz, ma conviene partire da 4-8 MHz su piattina lunga e salire dopo le misure.

Gestione di SPI_ALERT#: interrupt su PD0, poi polling dei piani in ordine all'indirizzo 07. La lettura del registro dell'MCP23S17 rilascia la linea; se resta bassa si passa al piano successivo (§4 della specifica).

Gestione di HIT# (§4.1 della specifica): interrupt su PD4 al fronte di discesa, con il tempo del fronte preso dal kernel (o dal time mark del GNSS se R337 è montata). Poi lettura dei latch dei piani tramite gli MCP23S17: i piani con il latch attivo formano la coincidenza. Infine azzeramento di picco e latch (accesso all'indirizzo 3 di ogni piano colpito).

## 5. Alimentazioni e protezioni

- **Rail del bus passanti (confermato da Michele il 2026-10-13):** 5V, 3V3, 2V5_REF, 1V25_REF, V_BIAS_1/2 e GND_A passano dal connettore BUS_POWER al connettore MAIN senza toccare i rail della scheda.
- **Alimentazione della scheda (opzione C):** la scheda A133 non usa il 5V del bus, che è l'alimentazione di precisione degli OPA4172 e viene da un AP63205 da 2 A. Prende VIN_SYS (12 V, confermato da Michele) sui pin 24-26 e lo porta a 5 V con un buck locale (es. TPS563201, 3 A), poi un ideal diode LM66100 in OR con il jack DC, a monte del TPS2121.
- **Consumi dei piani:** con 8 piani 51 mA sul 5V e 148 mA sul 3V3 (misure di Michele). I picchi di 6.21 A e 3.15 A del simulatore erano la corrente massima del regolatore, non un carico: servono solo per tarare fusibile o limitatore sul modulo Power.
- **VREF_ENABLE (da progetto MuonScope, power-zone):** Q2 BSS84 commuta il +5V verso l'ingresso del REF5025; il gate ha 10 kΩ verso +3.3V ed è pilotato da VREF_ENABLE. A riposo il gate è a 3.3 V con il source a 5 V: Vgs = -1.7 V, vicino alla soglia del BSS84, quindi il riferimento potrebbe non spegnersi del tutto (dedotto dallo schema, da verificare al banco). Correzione proposta sul modulo Power: pull-up del gate a +5V e comando dall'A133 tramite un BSS138 (open-drain), con la logica invertita in software.
- **Accensione:** se il modulo Power è spento mentre l'A133 pilota il MAIN, i 74HC dei piani si alimentano dai diodi d'ingresso. Il 3V3 del bus va letto (partitore su un pin libero, o il power-good del modulo Power) e i GPIO del MAIN vanno pilotati solo con il 3V3 presente. Le resistenze serie da 33-100 Ω limitano la corrente nel frattempo.
- **ESD:** array TVS a 5.5 V (es. TPD4E05U06) solo sulle linee logiche (SPI, I2C, CS, ADDR, PREFIX, ALERT, FAULT, enable). Mai sui rail di bias da 24 V o sui riferimenti.
- **Connettore MAIN:** FPC 28 pin, passo 0.5 mm, right-angle bottom contact (XUNPU FPC-05F-28PH20 indicato dalla specifica). Le alette vanno saldate su piazzole ampie verso GND_D. Codice LCSC da verificare prima di inserirlo in BOM.

## 6. Software Linux

- BUS MAIN: `spidev` su SPI1 + `libgpiod` per PREFIX/ADDR e per l'interrupt di SPI_ALERT#; I2C0 con `i2c-dev`.
- BUS_POWER: `spidev` su SPI2 con 3 `cs-gpios`. Non ho verificato driver mainline per INA239 e DAC61402, quindi la via sicura è lo spazio utente (stessa logica del firmware ESP32).

## 7. Ancora da confermare con Michele

1. Correzione del pull-up di VREF_ENABLE sul modulo Power (§5).
2. Fusibile resettabile (ed eventuale protezione da inversione) sul VIN del modulo Power, che oggi non ne ha.
