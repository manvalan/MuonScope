# PianoMatrice

Piano di rivelazione MuonScope con **16 fotodiodi VBPW34S in matrice 4×4 a passo 10 mm**, per il bus **MIKILAB REV5.1**. È la scheda definitiva del piano: i valori del front-end trovati sperimentalmente con il `PianoTest` si inseriscono come variabili di progetto.

Progetto KiCad 10: `PianoMatrice.kicad_pro`. Schema esportato in `PianoMatrice-schema.pdf`. Generatori Python in `generatori/`.

## Variabili da determinare sperimentalmente

Si impostano in *File → Impostazioni progetto → Variabili di testo* e si aggiornano schema, distinta materiali e serigrafia di tutti i 16 canali.

| Variabile | Default | Dove |
|---|---|---|
| `${RF}` | 100M | Resistenza di retroazione del preamplificatore di carica (R×11, R×31) |
| `${CF}` | 1p | Condensatore di retroazione (C×11, C×31) |
| `${VBIAS}` | 30V | Tensione di polarizzazione nominale (programmata nel DAC61402) |

Ogni canale ha anche una piazzola DNP in parallelo a Rf (Rf2) e una in parallelo a Cf (Cf2), per le prove.

## Fogli

| Foglio | Contenuto |
|---|---|
| Canali (8 istanze, canali 2k e 2k+1) | 2 VBPW34S con filtro di bias 1k + 100 nF C0G. OPA4140: A/B preamplificatori di carica, C/D shaper CR-RC invertente ×50 (τ = 1 µs). TLV3502 doppio comparatore con soglia VTH (trim per canale DNP). 74LVC74A doppio latch (azzerato da CS_Y3). OPA2365 doppio rilevatore di picco con BAS416 e hold 1 nF C0G, reset con BSS138. Iniezione di carica di test da 0,5 pF. |
| Acquisizione | MCP23S17 *mappa dei colpi* (Y5): 16 latch in una transazione. MCP23S17 *di controllo* (Y7, interrupt manager): indirizzo del mux, FAULT, HIT_ANY, abilitazione del test. 2× TMUX1108 (16:1) → buffer OPA2365 → 47 Ω + 1 nF → ADS8326 (Y0). HIT_ANY = OR dei 16 latch (2× 74HC30 + 74LVC1G32). |
| Bias | DAC61402: OUTA = bias comune (shunt 10k con INA239, 125 pA/LSB), OUTB = soglia VTH (0–1,56 V, ~0,4 mV/LSB). TMP117 al centro della matrice. |
| bus-pnp | J_IN/J_OUT XUNPU FPC-05F-28PH20, 74HC283/85/138, buffer LVC, ESD, EEPROM 25AA02E48, HIT# (74LVC1G123 + 74LVC1G06). |

## Mappa degli indirizzi del piano (74HC138)

| Y | Funzione |
|---|---|
| 0 | ADS8326 (ampiezza del canale selezionato dal mux) |
| 1 | DAC61402 (bias e soglia) |
| 2 | INA239 (corrente di buio totale) |
| 3 | Strobe: azzera i 16 latch e i 16 picchi |
| 4 | Strobe: gradino di test (se TEST_EN_N = 0), ~3,3 mV su 0,5 pF ≈ 1,6 fC per canale |
| 5 | MCP23S17 mappa dei colpi |
| 6 | EEPROM 25AA02E48 (identità del piano) |
| 7 | MCP23S17 di controllo (interrupt manager, ALERT#) |

## Sequenza di un evento

1. Uno o più comparatori scattano: i latch memorizzano i canali e i picchi tengono l'ampiezza.
2. HIT_ANY sale e genera un impulso di ~170–200 ns su HIT#. È un solo fronte per evento: gli impulsi dei piani colpiti dalla stessa particella si sovrappongono.
3. Il master marca il tempo del fronte e legge da ogni piano la mappa dei colpi (Y5).
4. Per ogni canale colpito il master imposta il mux (Y7) e converte il picco (Y0).
5. Infine azzera latch e picchi con un accesso a Y3.

## Scelte

- **OPA4140 al posto dell'OPA4172.** Ingresso JFET: rumore di corrente trascurabile e 10 pA massimi di corrente di polarizzazione. Rumore di tensione 5,1 nV/√Hz contro 7, quindi ENC serie circa −25 %. 11 MHz di banda, uscita rail-to-rail. Il quad copre preamplificatore e shaper di due canali.
- **Shaper a uno stadio ×50.** Si risparmia un operazionale per canale. Con 11 MHz la banda a guadagno 50 è ~200 kHz, compatibile con τ = 1 µs.
- **Peak hold con l'ingresso invertente sul condensatore.** L'OPA2365 ha 0,2 pA di corrente di polarizzazione, quindi niente buffer per canale: un solo buffer dopo il mux protegge l'hold dal kickback dell'ADC.
- **Mux TMUX1108 (3 pA).** Le perdite sul condensatore da 1 nF sono trascurabili nei tempi di lettura. L'ADG706 è un'alternativa equivalente: il suo datasheet non era raggiungibile, quindi ho scelto il TMUX1108 di cui ho verificato il pinout.

## Stato (2026-10-14)

- Schema: **ERC 0**, 486 componenti.
- PCB: **140 × 120 mm, 4 strati** (segnali, GND, alimentazioni, segnali). Sensori sul lato inferiore, al centro, in griglia 4×4. Elettronica di canale a gruppi sul lato superiore, logica comune in basso. J_IN a sinistra e J_OUT a destra, fori M3 agli angoli nelle stesse posizioni su ogni piano, così i piani si impilano. **Non sbrogliato.**
- 4 strati dovrebbero bastare; 6 strati (due piani di massa ai lati dei segnali analogici) sono da valutare se lo sbroglio dei 16 canali risulta troppo denso.
- DRC: centinaia di serigrafie sovrapposte e non connessi (KiCad si ferma a 199/499 per categoria), più 59 clearance tra componenti vicini o dentro i footprint a passo fine. Tutto atteso prima dello sbroglio.

## Stima dei costi dei componenti per piano

Prezzi indicativi per 10 piani (distributori, ottobre 2026), esclusi PCB e montaggio: **circa 140–170 USD per piano**.

| Voce | Quantità | Stima |
|---|---|---|
| OPA4140 | 8 | 35–45 |
| TLV3502 | 8 | 18–24 |
| OPA2365 | 9 | 15–20 |
| VBPW34S | 16 | 10–15 |
| DAC61402, INA239, ADS8326, TMP117 | 1 ciascuno | 20–25 |
| MCP23S17 ×2, TMUX1108 ×2, logica 74HC/LVC, EEPROM | — | 10–12 |
| Condensatori C0G 100 nF 100 V 1206 | 17 | 5–8 |
| Altri passivi (~350), Rf ad alto valore, connettori FPC, ESD | — | 15–20 |

## Punti aperti

- Valori di `${RF}`, `${CF}` e `${VBIAS}` dai dati del PianoTest.
- Il gradino di test dipende dalla tensione a 3,3 V del bus: per la calibrazione assoluta misurare il 3V3, oppure sostituire il partitore con un riferimento.
- La capacità di iniezione da 0,5 pF aggiunge 0,5 pF all'ingresso di ogni canale: si può lasciare DNP dopo la calibrazione.
- Quote del footprint FPC da confrontare con il disegno XUNPU.

Footprint `MIKILAB_*` dalla libreria esterna MIKILAB (variabile `${MIKILAB}`), non inclusa nel repository.
