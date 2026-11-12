# TestRouter6ULL: scheda minima i.MX 6ULL + DDR3L per provare lo sbroglio con BoardLab

Scheda di prova **solo placement, nessuna pista**: tutte le connessioni sono lasciate all'autorouter. Aprire `progetto/TestRouter6ULL.kicad_pro`.

| | |
|---|---|
| Scheda | 60 x 50 mm, angoli raggiati 3 mm, 4 fori M2 con keepout |
| Strati | 4 (F.Cu, In1.Cu GND, In2.Cu PWR, B.Cu), stackup standard PCBWay come ProvaDDR |
| Componenti | 89 (65 top, 24 bottom) + 4 fori |
| Net | 84 (44 classe `DDR`, 6 classe `DDR_DIFF`, 34 `Default`) |
| ERC | 0 errori, 0 avvisi |
| DRC | 0 violazioni, 0 problemi di parita' schema/PCB, 349 connessioni non sbrogliate (attese) |

File: `schema-testrouter6ull.pdf` (schema), `placement-testrouter6ull.png` (top a sinistra, bottom specchiato a destra).

## Contenuto

- **U1** NXP MCIMX6Y2CVM08AB, MAPBGA-289 14x14 passo 0.8. Mappa delle sfere da SchedaIMX6ULL-SD (IMX6ULLCEC Rev 1.2, tabelle 90/91). Collegati solo DDR, alimentazioni, clock, reset, boot e UART1; le altre sfere hanno il no_connect.
- **U2** Micron MT41K512M16HA-107:A, DDR3L x16 1 GB, FBGA-96 9x14 passo 0.8. **AS4C512M16D3LC non c'e' nella libreria MIKILAB**: uso il Micron, stessa ball map JEDEC x16 e stesso footprint, quindi si puo' montare l'Alliance senza modifiche. Simbolo: MT41K256M16HA di KiCad con A15 su M7.
- Bus DDR completo SoC-DRAM: DQ0-15, LDQS/UDQS P/N, LDM/UDM, A0-A15, BA0-2, CK P/N, CKE, CS#, RAS#, CAS#, WE#, ODT, RESET#. ZQ 240R 1% su SoC e DRAM, VREF a partitore 1k/1k con 100 nF su ogni resistenza (unica per DRAM_VREF, VREFCA, VREFDQ), 10k a GND su RESET# e CKE, 100R tra CK_P e CK_N vicino alla DRAM.
- Disaccoppiamento di SoC e DDR come SchedaIMX6ULL-SD, tutto 0603 o piu' grande: 17 condensatori sul bottom sotto e accanto alle BGA (8 sotto U1, 4 sotto U2, 5 sui rail `_CAP` vicino all'angolo basso destro di U1).
- Y1 24 MHz (X322524MOB4SI) con 2x18 pF, Y2 32.768 kHz (Q13FC1350000400) con 2x12 pF, sotto il SoC vicino alle sfere XTAL e RTC.
- POR_B: RC 10k/1uF dal 3.3 V. JTAG_MOD 4.7k a GND, JTAG non usato.
- BOOT_MODE[1:0] = 01 (serial downloader, la scheda non ha memorie di boot: il ROM aspetta su UART1/USB). Due resistenze DNP per passare a BOOT_MODE = 10.
- J2 console UART1 (header 3 pin: TX, RX, GND) sul bordo alto.

## Alimentazione

Scelta la soluzione con i regolatori sulla scheda (gli stessi, con gli stessi valori, di SchedaIMX6ULL-SD) invece dei rail da header: e' poco piu' complessa e la scheda resta alimentabile da sola con 5 V.

- J1 header 2 pin: 5 V e GND, sul bordo basso.
- U3 TPS563201 -> 3V3 (FB 33.2k/10k), primo della sequenza.
- U4 TLV62569 -> V1P35 per NVCC_DRAM e DDR3L (FB 150k/120k), EN 100k/470nF dal 3V3.
- U5 TLV62569 -> V1P4 per VDD_SOC_IN (FB 133k/100k = 1.398 V), EN 100k/1uF dal 3V3.
- VDD_SNVS_IN e VDD_HIGH_IN dal 3V3, niente pila.

I buck sono in colonna sul lato destro, lontani dalla DDR3L.

## Regole e classi

Stackup PCBWay 4 strati 1.6 mm (voce 1 della tabella *Multi-layer laminated structure*): prepreg 7628 0.1855 mm Er 4.74, core 1.03 mm, rame 1 oz su tutti gli strati. Identico a ProvaDDR.

Regole in `progetto/TestRouter6ULL.kicad_dru`: piste 5 mil (0.127 mm), 4 mil (0.1016 mm) sotto il courtyard di qualsiasi componente su entrambi i lati, distanza 0.1 mm, via 0.45/0.2 mm.

| Classe | Net | Pista | Distanza | Coppia |
|---|---|---|---|---|
| `DDR` | A, BA, DQ, DM e comandi (44) | 0.127 | 0.127 | |
| `DDR_DIFF` | CK, LDQS, UDQS (6) | 0.127 | 0.127 | 0.127 / gap 0.127 |
| `Default` | il resto, VREF e ZQ compresi | 0.127 | 0.1 | |

Le classi DDR sono a 5 mil, non a impedenza controllata: su questo stackup 5 mil sono circa 77 ohm singola (calcolo di ProvaDDR), 50 ohm richiederebbe 0.316 mm, che non passano tra le sfere. Per una scheda di prova dello sbroglio e' la scelta piu' semplice; per una scheda vera serve uno stackup con prepreg sottile.

## Rigenerazione

`generatori/build.sh` rigenera tutto in `progetto/` (schema, ERC, PDF, PCB, DRC, PNG). Serve KiCad 10 con il modulo Python `pcbnew`, le librerie standard di KiCad 10 e la libreria MIKILAB (`~/Develop/mikilab-kicad-library` o variabile `MIKILAB`). I generatori sono adattati da `SchedaIMX6ULL-SD/generatori` (branch `claude/project-thread-034nik`). Le posizioni dei passivi sono calcolate: ogni rigenerazione puo' spostarli di poco.

## Problemi aperti

- AS4C512M16D3LC assente dalla libreria: in schema c'e' MT41K512M16HA (compatibile pin a pin).
- Alcuni passivi lenti del SoC (boot, POR, bulk 22 uF) sono a 13-17 mm da U1, perche' la corona attorno alle BGA resta libera per il fanout.
- I resistori VREF/ZQ della DRAM sono nell'angolo basso sinistro, a 10-16 mm da U2: vanno bene per la prova del router, su una scheda vera ZQ e VREF vanno avvicinati.
- I condensatori sul bottom sotto le BGA occupano posti dove uno sbroglio con un via per sfera metterebbe i via di alimentazione: lo sbrogliatore dovra' condividerli o spostarli, come in ProvaDDR.
