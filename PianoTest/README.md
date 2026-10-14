# PianoTest

Piano di test MuonScope per il bus **MIKILAB REV5.0**. Serve a trovare sperimentalmente i valori migliori della rete di retroazione (Rf/Cf), della formatura e del bias per il fotodiodo, prima di progettare la matrice dei sensori.

Progetto KiCad 10: `PianoTest.kicad_pro`. Simboli locali in `PianoTest.kicad_sym`. Schema esportato in `PianoTest-schema.pdf`.

## Fogli

| Foglio | Contenuto |
|---|---|
| Rivelatore | Fotodiodo VBPW34S. Preamplificatore di carica OPA4172 A (Cf 1 pF, Rf 100M di default). Shaper CR-RC τ ≈ 1 µs: C invertente ×10, D non invertente ×5 (totale ×50). Base 1V25 bufferizzata da B. ADS8326 con filtro 47 Ω + 1 nF. TMP117. SMA e test point su CSA_OUT e SHAPER_OUT. Opzione JFET BF862 in cascode, non montata, con jumper 0R. |
| RetroactionNetwork | MCP23S17. Rf da 10k a 10M su 2× TMUX1112 (pull-down: aperti al reset). Cf da 0.5 a 100 pF su 2× BGSA142: −IN → Cf → RFx → RFC → 10 nF C0G → uscita, con 100M verso GND su ogni porta. CTL con partitore 10k/22k. |
| EmettitoreTest | LTC6993-2 con AD5245 (I2C, 0x2C) + 47k sul SET. BSS138 → LED IR alimentato da +5V. TRIG dall'MCP (GPA7) o da J301. |
| BiasDiodo | DAC61402 alimentato da VHV_36V (RC 100 Ω + 2×1 µF/100 V). OUTA → shunt 10k (INA239) → RC 1k/100 nF vicino al diodo. OUTB di riserva. |
| bus-pnp | J_IN/J_OUT FPC 28 pin. 74HC283 (ID+1), 74HC85 (PREFIX = ID), 74HC138 (Y0 ADC, Y1 DAC, Y2 INA, Y3–Y5 TP, Y6 EEPROM 25AA02E48, Y7 MCP). Buffer 2G17 su SCLK/MOSI, 1G125 su MISO, 1G07 su ALERT#. ESD TPD1E10B06. |

## Bus

- Tutti i segnali passano da J_IN a J_OUT, tranne ID[0..2] (pin 25–27), che esce come ID+1.
- Pin 8/9 (ex V_BIAS_1/2) portano **VHV_36V** dal modulo Power.
- I2C (pin 14/15): AD5245 0x2C, TMP117 0x48. Le pull-up sono sulla scheda master.
- MCP23S17: configurare MIRROR=1 (INTA riassume entrambe le porte). Indirizzo hardware 000 (il CS è già decodificato per piano).
- Guasti (FAULT del DAC, ALERT di INA239 e TMP117) in wired-OR su PL_FAULT → GPA6 dell'MCP → ALERT#.

## Stato (2026-10-14)

- Schema: **ERC 0 violazioni**.
- PCB: 4 strati (F.Cu segnali, In1 GND, In2 PWR, B.Cu segnali), 120 × 90 mm. J_IN sul lato sinistro, J_OUT sul destro. Componenti piazzati a gruppi per foglio, **non sbrogliato**.
- DRC: 472 violazioni + 499 non connessi, attesi senza sbroglio. Sono soprattutto serigrafie sovrapposte, clearance interne ai footprint MIKILAB a passo fine e courtyard malformati di quei footprint.
- FPC J401/J402: XUNPU FPC-05F-28PH20 (LCSC C2856807), footprint e modello 3D importati da EasyEDA in `PianoTest.pretty` e `PianoTest.3dshapes` (pad 0.30 × 1.25 mm, passo 0.5 mm, pin 1–28 su 13.5 mm, ancoraggi 2.0 × 2.5 mm a ±8.44 mm).

## Punti aperti

- BGSA142: datasheet Infineon non scaricabile. VDD 1.65–3.6 V (alimentato a 3.3 V). VIH dei CTL e combinabilità delle porte da verificare: il partitore 10k/22k porta i CTL a 2.27 V.
- Rf 100M (0805 alta resistenza) e Cf piccoli: tenere pulita l'area attorno a CSA_IN (guard ring, niente solder mask, lavaggio).
- Bias: C101, C103 e C506 sono C0G 100 nF 100 V 1206 (TDK C3216C0G2A104J160AE), perché gli X7R perderebbero nA a 30 V.
- Opzione JFET: valori di polarizzazione (R124–R129) da tarare sul BF862 montato.
- FPC: quote del footprint EasyEDA da confrontare con il disegno XUNPU (il PDF LCSC non si scarica in automatico). Connettore con contatti in basso: verificare il verso del cavo.
- Piano di alimentazione In2: oggi è una sola zona +3V3, da dividere con +5V in fase di sbroglio.

Footprint `MIKILAB_*` dalla libreria esterna MIKILAB (variabile `${MIKILAB}`), non inclusa nel repository.
