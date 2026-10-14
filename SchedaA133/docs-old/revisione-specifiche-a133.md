# Revisione tecnica specifiche: scheda custom Allwinner A133

Data: 2026-10-13, rev. 2 (dopo le decisioni di Michele). Sostituisce la scelta RK3308B (i file in `bom/` restano come archivio).

Decisioni prese il 2026-10-13: timing al nanosecondo tramite time mark del GNSS, USB-C completa (DRP), eMMC alla massima capienza. RAM: LPDDR4 2 GB (§2). PCB: 6 layer con via-in-pad (§1).
BOM proposta: [bom-a133.csv](bom-a133.csv). Codici LCSC verificati solo dove indicato.

## 0. Sintesi: cosa regge e cosa no

| Punto della specifica | Esito | In breve |
|---|---|---|
| A133, LFBGA-346, passo 0.5 mm | **OK, ma pesa sul PCB** | Confermato: 346 sfere, corpo 12 x 12 mm, passo 0.5 mm, sfera 0.3 mm (product brief Allwinner). Un passo 0.5 mm non si sbroglia con via passanti normali: servono via-in-pad riempite o HDI (§1) |
| PMIC AXP707 | OK con riserve | È il PMIC "customized" indicato da Allwinner per l'A133; in Linux mainline si usa il driver AXP803 (stesso set di regolatori). Le tensioni/abilitazioni di default sono in OTP: la mappatura dei rail va copiata dallo schema di riferimento, non scelta liberamente (§3). Stock LCSC instabile |
| DDR4 32 bit, 2 chip x16 FBGA-96 | **Sostituita da LPDDR4 2 GB** | DDR4/DDR3/LPDDR3/LPDDR4, 32 bit, max 4 GB, max 792 MHz. U-Boot mainline ha l'init DRAM A133 con timing DDR4 e LPDDR4, ma le schede mainline note (Liontron H-A133L, Baijie Helper A133) usano LPDDR4: DDR4 è meno collaudata (§2) |
| eMMC 5.1 su FBGA-153 | **Portata a 256 GB** | Massima taglia eMMC in commercio. SMHC2, 8 bit, fino a 150 MHz SDR a 1.8 V: VCCQ a 1.8 V per HS200 (§6) |
| EEPROM 25AA02E48 (MAC) | OK | Suggerito il gemello I2C 24AA02E48 (§6) |
| RTL8211F-CG su RGMII | OK | L'A133 ha 1 MAC 10/100/1000 RGMII/RMII; supporto EMAC0 A133 in mainline da Linux 6.17 |
| RTL8723DS su SDIO + UART | **Sostituito da AMPAK AP6256** | SMHC1 è il controller SDIO. RTL8723DS è un chip: usare un modulo (es. Fn-Link 6223A-SRD), driver mainline rtw88 |
| USB-C alimentazione + FEL + OTG | **Decisa: completa (DRP + PD)** | Controller FUSB302B, switch VBUS e secondo ingresso di alimentazione (§5) |
| PPS "nanosecondo-preciso" su pin di interrupt | **Decisa: ns via time mark GNSS** | L'interrupt GPIO in Linux dà µs; gli eventi (otturatore camera) si marcano al ns nell'ingresso EXTINT del NEO-F10T (§4) |
| microSD su "SD0/SD1" | **Deve essere SD0** | Il boot ROM avvia solo da SMHC0 (SD) e SMHC2 (eMMC); SMHC1 è per l'SDIO del Wi-Fi |
| Quarzi 24 MHz e 32.768 kHz | OK | |
| Stack-up 6 layer, 50 Ω / 100 Ω | OK con 1 correzione | USB va a **90 Ω** differenziali, non 100 Ω (§7) |

## 1. Package 0.5 mm: scelta via-in-pad su 6 layer (2026-10-13)

Primo passo prima dello schema definitivo: prova di fanout sul footprint reale dell'A133 con le regole del produttore (via 0.15/0.25 mm riempite e ricoperte, piste 3/3 mil). Se non si sbrogliano tutte le sfere, si passa all'HDI.

### Confronto fatto

Con passo 0.5 mm la distanza tra due sfere adiacenti lascia circa 0.2 mm di rame: non ci passa né una via (minimo tipico 0.15 mm foro / 0.25-0.3 mm pad) né, nelle file interne, una pista. Opzioni:

| Opzione | Come | Costo/rischio |
|---|---|---|
| **A (consigliata)** | 6 layer, via passanti 0.15/0.25 mm **in pad**, riempite di resina e ricoperte (VIPPO/POFV), piste 3/3 mil sotto il BGA | JLCPCB e simili lo offrono su 6 layer a costo contenuto. Fattibilità da confermare con una prova di fanout sul footprint reale (quante sfere sono depopolate) |
| B | HDI 1+4+1 con microvia laser | Sicuramente fattibile, costo PCB molto più alto (x3-x5 sul prototipo) |
| C | Modulo SoM A133 (es. core board Baijie Helper A133: A133 + LPDDR4 + eMMC + AXP707) + carrier 4 layer con PHY, GNSS, Wi-Fi | Elimina BGA, DDR e PMIC dal tuo PCB; perdi la scelta DDR4 e il controllo sul form factor |

Anche le sfere della DDR4 FBGA-96 hanno passo 0.8 mm e si sbrogliano senza problemi; l'eMMC FBGA-153 ha passo 0.5 mm ma quasi tutte le sfere sono NC o massa.

## 2. RAM: scelta LPDDR4 2 GB (2026-10-13)

Chip: **Micron MT53E512M32D1ZW-046 IT:B** (16 Gbit x32, 200 sfere, industriale). Alimentazioni VDD1 1.8 V, VDD2/VDDQ 1.1 V da DCDC5 (DC5SET strappato per 1.1 V). Niente VPP, VREF esterna o VTT. Restano qui sotto il confronto e le note DDR4 come riferimento.

### Confronto fatto

Entrambe sono supportate dall'A133 (bus 32 bit, max 4 GB, max 792 MHz) e dall'init DRAM di U-Boot mainline (`a133_ddr4.c`, `a133_lpddr4.c`).

| | **A. DDR4, 2 chip x16** | **B. LPDDR4, 1 chip x32** |
|---|---|---|
| Chip | 2 x 8 Gbit = 2 GB: Micron MT40A512M16TB-062E, Samsung K4A8G165WC-BCTD. 2 x 16 Gbit = 4 GB: MT40A1G16TB-062E. 2 x 4 Gbit = 1 GB possibile ma in uscita di produzione | 16 Gbit = 2 GB o 32 Gbit = 4 GB, 200 sfere 10 x 14.5 mm (famiglia Micron MT53E...32D, es. MT53E512M32D1ZW-046 per 2 GB, codice da verificare). I chip "unified" LPDDR4/4X vanno usati con VDDQ 1.1 V |
| Package | FBGA-96, passo 0.8 mm, facile da sbrogliare | 200 sfere, passo 0.8 x 0.65 mm, più fitto |
| Alimentazioni | VDD/VDDQ 1.2 V, **VPP 2.5 V** (LDO esterno, vedi sotto), VREFCA 0.6 V da partitore | VDD1 1.8 V, VDD2/VDDQ 1.1 V; niente VPP, niente VREF esterna, niente VTT |
| Topologia | Indirizzi/comandi a T verso 2 chip, dati point-to-point. Footprint VTT (TPS51200) di riserva, non montato | Tutto point-to-point verso un solo chip: meno piste, meno area, routing più corto |
| Software mainline | Codice presente ma **nessuna scheda mainline nota con DDR4 su A133**: rischio di dover tarare i parametri. Boot0 del BSP Allwinner la supporta | **Collaudata**: Liontron H-A133L e Baijie Helper A133 usano LPDDR4 |
| Approvvigionamento | Facile (LCSC, Mouser, DigiKey), prezzi bassi | Meno distributori per pezzi singoli, prezzo più alto per GB |
| Costo PCB/area | 2 chip, più area e più nets | 1 chip, meno area |

Mio consiglio: **B (LPDDR4 2 GB)** se il primo obiettivo è che la scheda parta con il software mainline al primo giro; **A (DDR4 2 GB)** se conta di più la facilità di montaggio a mano/approvvigionamento e accetti di partire col BSP Allwinner. La BOM ora contiene solo la LPDDR4; LDO VPP e VTT della DDR4 sono stati tolti.

Note comuni:
- **DDR4 e VPP**: l'AXP707 non ha un rail VPP abilitato all'avvio. JEDEC richiede VPP ≥ VDD sempre, e VPP che sale prima o insieme a VDD. Soluzione: LDO 2.5 V dedicato (TLV75525PDBVR) alimentato dall'ingresso di sistema, primo a salire e ultimo a scendere.
- ZQ: 240 Ω 1% per ogni chip e per i pin ZQ del SoC.
- VCC-DRAM: con l'AXP707 è DCDC5, il cui default si fissa col pin DC5SET (1.2 V per DDR4, 1.1 V per LPDDR4).

## 3. Alimentazione: AXP707

AXP707 (QFN-68 8x8, LCSC C2913551): ingresso VBUS/ACIN 3.5-7 V, caricatore Li-ion fino a 2.8 A (inutilizzato), 6 buck + 15 LDO, interfaccia RSB per SoC Allwinner (o I2C).

| Canale | Range / corrente | Uso proposto (da allineare allo schema di riferimento A133) |
|---|---|---|
| DCDC1 | 1.6-3.4 V, 1.5 A | 3.3 V: VCC-IO, banchi PF (microSD), PH (RGMII), eMMC VCC, EEPROM |
| DCDC2+DCDC3 (dual phase) | 0.5-1.3 V, 2 x 3 A, DVM | VDD-CPU (DVFS) |
| DCDC4 | 0.5-1.3 V, 3 A | VDD-SYS / GPU |
| DCDC5 | 0.8-1.84 V, 2.5 A | **VCC-DRAM** 1.2 V (DDR4) o 1.1 V (LPDDR4). Il default è fissato dal pin DC5SET: va strappato per la tensione giusta, altrimenti la RAM riceve la tensione sbagliata al primo avvio |
| DCDC6 | 0.6-1.52 V, 2.5 A | VDD-CPUS / altri rail core |
| ELDO1-3, FLDO1-2 | 0.7-1.9 V / 0.7-1.45 V | 1.8 V: VCC-PLL, VDD18-DRAM (anche VDD1 della LPDDR4), AVCC, VCC-PC (VCCQ eMMC) |
| ALDO1-3, DLDO1-4 | 0.7-3.3 V, 200-500 mA | VCC-PG (I/O SDIO Wi-Fi), VCC-PE/PL, alimentazione GNSS se non dal buck esterno |
| RTCLDO | 1.8 o 3.0 V, 60 mA | VCC-RTC 1.8 V |

Note:
- **L'OTP decide sequenza e rail accesi all'avvio.** Per la versione "customized" A133 la sequenza è già corretta solo se colleghi i canali come nel riferimento Allwinner (schema tablet A133 nel pacchetto documenti linux-sunxi/whycan). La tabella sopra è un'ipotesi da confermare su quello schema.
- DCDC1 da 1.5 A non basta per tutto il 3.3 V con Wi-Fi in trasmissione (picchi 500-600 mA), PHY gigabit, eMMC e SD. Proposto un **buck 3.3 V / 2 A esterno** dall'ingresso 5 V per Wi-Fi, GNSS e PHY.
- Senza batteria: il pin BAT va gestito come da app note (condensatore, caricatore disabilitato in U-Boot) e va verificato il **limite di corrente VBUS** di default, da alzare presto in U-Boot.
- Mainline: la Baijie Helper A133 usa l'AXP707 con `compatible = "x-powers,axp803"`.

Budget stimato a pieno carico: SoC 1.5-2 W, RAM 0.5 W, eMMC 0.4 W, PHY 0.4 W, Wi-Fi 1 W di picco, GNSS 0.1 W: circa **4 W**, più fino a 4.5 W (5 V / 0.9 A) da fornire a una periferica in modalità host. Ingresso: 5 V / 3 A da USB-C oppure 5 V / 4 A dal jack DC (§5).

## 4. GNSS e PPS

- Modulo consigliato: **u-blox NEO-F10T** (timing, L1/L5, accuratezza 10 ns 1σ, jitter time pulse ±8 ns, 2.7-3.6 V, V_BCKP 1.65-3.6 V, UART, uscita time pulse e **ingresso time mark**). Alternativa più economica non-timing: MAX-M10S.
- PPS verso un pin del SoC con interrupt esterno (banchi PB/PE/PG/PH supportano EINT) e driver `pps-gpio`. Precisione reale: 1-10 µs di jitter da latenza interrupt, ottima per chrony/NTP stratum 1 e ampiamente sufficiente per le occultazioni (servono ~1 ms).
- **Precisione ns (decisa)**: l'uscita strobe/trigger della camera va all'**ingresso time mark (EXTINT) del NEO-F10T**. Il modulo marca il fronte in hardware rispetto al tempo GNSS e lo invia via UART (messaggio UBX-TIM-TM2, risoluzione ns). L'incertezza finale è quella del modulo (10 ns 1σ) più il ritardo del cavo e dello strobe della camera, che si misura una volta e si corregge.
- Connettore dedicato per EXTINT: SMA o header schermato, con resistenza serie 100 Ω, ESD (es. ESD9B5.0ST5G) e, se la camera ha strobe a 5 V o open-collector, un buffer/traslatore 3.3 V veloce (es. 74LVC1G17 alimentato a 3.3 V, ingressi tolleranti 5 V). Ritardo del buffer ~3-4 ns, stabile e calibrabile.
- Utile anche un'**uscita PPS bufferizzata** su SMA (stesso 74LVC1G17) per verificare il timing con un oscilloscopio o sincronizzare strumenti esterni.
- Instradare il PPS anche verso un pin con funzione PWM (resistenza 0 Ω di selezione), per un'eventuale cattura hardware: la capacità di capture del PWM A133 va verificata sul manuale utente.
- VBACKUP: supercap 0.2 F 3.3 V (es. CPH3225A, o PAS3225) caricato dal 3.3 V tramite diodo Schottky + 1 kΩ. Mantiene effemeridi ore/giorni; con la CR1220 si arriva ad anni.
- Antenna attiva via SMA o U.FL, con alimentazione 3.3 V tramite induttore e limitazione di corrente; buffer/level-shift non necessario se VCC-banco del pin PPS è 3.3 V.

### Collegamenti NEO-F10T (dal datasheet UBX-22022576)

| Pin NEO-F10T | Segnale | Collegamento |
|---|---|---|
| 23 VCC | 3.3 V (2.7-3.6 V) | Buck 3.3 V esterno, 10 µF + 100 nF vicino al pin. Spunto all'avvio fino a 100 mA |
| 22 V_BCKP | Backup 1.65-3.6 V | Supercap/CR1220 tramite Schottky + 1 kΩ dal 3.3 V |
| 10, 12, 13, 24 GND | Massa | Piano di massa, via multiple |
| 11 RF_IN | Antenna | SMA/U.FL con linea a 50 Ω corta |
| 9 VCC_RF | VCC - 0.1 V, max 300 mA | Alimentazione antenna attiva verso RF_IN tramite resistenza di limitazione + induttore (circuito dell'Integration Manual u-blox) |
| 20 TXD | UART uscita | RX della UART3 dell'A133 (PD14/PD15, banco PD a 3.3 V), 38400 baud di default |
| 21 RXD | UART ingresso | TX della UART3 dell'A133 |
| 3 TIMEPULSE | PPS | 33 Ω serie verso un GPIO EINT (pps-gpio) + ingresso del buffer 74LVC1G17 per l'uscita PPS su SMA. Non mettere pull-up/pull-down: deve restare libero all'avvio |
| 4 EXTINT | Time mark | Uscita del buffer 74LVC1G17 dall'SMA "strobe camera" (ESD + 100 Ω in ingresso). Pull-up interno |
| 8 RESET_N | Reset attivo basso | GPIO dell'A133 in open-drain (pull-up interno ~10 kΩ) |
| 1 SAFEBOOT_N | Safeboot | Solo piazzola di test (serve per aggiornare il firmware in emergenza). Collegato internamente a TIMEPULSE tramite 1 kΩ |
| 2, 5-7, 14-19 | Riservati | Non collegare |

Livelli: niente pin V_IO, gli I/O seguono VCC (VIH min 0.68 x VCC = 2.2 V a 3.3 V). I banchi dell'A133 usati per UART GNSS e PPS devono quindi essere a **3.3 V**: con un banco a 1.8 V il modulo non legge il TX del SoC. Il modulo non ha I2C né USB, solo UART. Risoluzione del time mark: 16 ns; accuratezza del PPS: 10 ns (1σ).

## 5. USB-C completa (decisa)

L'A133 ha USB 2.0 (USB0 OTG, usato per FEL) e nessuna USB 3: la porta Type-C porta solo D+/D-.

Architettura:
- **Controller CC con Power Delivery: FUSB302B** (I2C, driver mainline `fusb302` + `tcpm`). Gestisce sink, source e scambio di ruolo dati: la scheda può alimentarsi da un hub USB-C con PD e fare da host verso le periferiche dello stesso hub.
- **Due ingressi di alimentazione**: USB-C VBUS e jack DC 5 V (5.5/2.1 mm), uniti da un power mux con priorità al jack (**TPS2121**). Da USB-C la scheda si alimenta sempre; per fornire VBUS a una periferica senza hub PD serve il jack.
- **Switch VBUS source**: load switch 5 V con limite di corrente regolabile (SY6280AAC, limite 1 A) dal 5 V di sistema al VBUS del connettore, comandato dal FUSB302B/tcpm. Il mux impedisce il ritorno di corrente verso l'ingresso.
- Rilevamento VBUS verso il SoC (partitore su un GPIO o sul pin VBUS-DET dell'AXP707).
- Protezioni: USBLC6-2SC6 su D+/D-, ESD dedicato su CC1/CC2 (es. TPD2EUSB30), TVS su VBUS, fusibile resettabile 3 A.
- FEL: pulsante sul pin FEL del SoC + reset. La modalità FEL funziona con la scheda in ruolo device: il FUSB302B all'accensione parte come sink, quindi il PC vede l'A133 senza software.

Rischio software: il controller USB0 dell'A133 (musb sunxi) gestisce il cambio host/device tramite il pin ID e `usb0_vbus-supply`. Collegarlo al ruolo deciso da tcpm richiede un usb-role-switch o un piccolo adattamento nel kernel. Ripiego hardware senza software: **TUSB320LAI** in modalità DRP, la cui uscita ID va direttamente al GPIO ID del SoC (OTG classico, niente PD). I due chip non hanno lo stesso footprint, quindi si sceglie prima del layout. Proposta: FUSB302B, con il TUSB320LAI come piano B se il porting si rivela lungo.

Opzionale e quasi gratis: una presa **USB-A host** sulla seconda porta USB (USB1 host) dell'A133, per tenere collegata una periferica fissa (camera, focheggiatore) indipendentemente dal ruolo della Type-C.

## 6. Altre periferiche

- **microSD**: SMHC0 (PF0-PF6), I/O 3.3 V (niente UHS, 25 MB/s), pull-up 10-47 kΩ su CMD e D0-D3, 22-33 Ω in serie sul CLK vicino al SoC, card detect.
- **eMMC (massima capienza)**: 256 GB è la taglia massima delle eMMC in commercio. Proposta **Kingston EMMC256-IY29-5B101** (eMMC 5.1 HS400, FBGA-153 11.5 x 13 mm, industriale -40/+85 °C, utile per l'uso notturno all'aperto); versione commerciale EMMC256-TY29-5B101. SMHC2 8 bit, VCC 3.3 V, VCCQ 1.8 V (VCC-PC 1.8 V; verificare sul datasheet Kingston che VCCQ 1.8 V sia supportata), pull-up su CMD/RST, pull-down 10 kΩ su DS. L'A133 non ha limiti di capienza per l'eMMC (indirizzamento a settori). La velocità è limitata dal SoC (HS200, circa 100-150 MB/s), non dalla memoria.
- **Ethernet**: RTL8211F-CG con regolatore interno (induttore sul pin REG_OUT secondo datasheet), I/O RGMII a 3.3 V quindi VCC-PH = 3.3 V. Ritardi RGMII interni al PHY (`phy-mode = "rgmii-id"`), quindi non serve serpentinare per i 2 ns. Il PHY non ha PTP.
- **MAC address**: 25AA02E48 va bene (driver at25 + nvmem-cells). Il 24AA02E48 (I2C, SOT-23-5) fa lo stesso su un bus I2C già presente e libera un SPI.
- **Wi-Fi/BT (aggiornato 2026-10-13)**: modulo **AMPAK AP6256** (Wi-Fi 5 dual band 2.4/5 GHz 802.11ac 1x1 fino a 433 Mbps, BT 5.2, 12x12 mm) al posto dell'RTL8723DS. Driver mainline brcmfmac (firmware brcmfmac43456-sdio) + btbcm su UART, già usato con Allwinner sulla Orange Pi 3. Non è su LCSC: va comprato da Mouser/DigiKey o distributori AMPAK. Collegamenti: SDIO 3.0 su SMHC1 (PG0-PG5), UART BT con RTS/CTS (fino a 4 Mbaud), WL_REG_ON e BT_REG_ON su GPIO, WL_HOST_WAKE e BT_HOST_WAKE su pin EINT, LPO 32.768 kHz da X32KFOUT (±30 ppm), VBAT 3.3 V dal buck esterno (picco 1 A), VDDIO uguale a VCC-PG (1.8 V consigliato per SDIO 3.0 veloce). Antenna dual band su U.FL.
- **Clock**: 24 MHz 3225 (CL 12 pF), 32.768 kHz 3215 (CL 6-12.5 pF), carichi C0G calcolati dal CL.
- **Debug**: header UART0 a 3 pin (115200 baud).

## 7. PCB e stack-up

Stack-up proposto: L1 segnale (DDR, RGMII) / L2 GND / L3 segnale (DDR) / L4 piani di alimentazione / L5 GND / L6 segnale. La variante con due layer di segnale adiacenti (L3-L4) della specifica va bene solo con instradamento ortogonale tra L3 e L4; i piani di alimentazione su un layer dedicato riducono il rumore sul VDD-CPU.

Impedenze: 50 Ω single-ended (DDR, SDIO, RGMII), 100 Ω differenziali (Ethernet MDI, clock/DQS DDR4), **90 Ω differenziali per USB**. Verificare le impedenze consigliate dalla guida layout A133 (alcuni riferimenti Allwinner usano 40 Ω sulle DQ).

Length matching DDR4: DQ/DM entro ±5 mil rispetto al DQS del proprio byte, indirizzi/comandi entro ±25 mil rispetto al CK; RGMII entro ±50 mil per gruppo.

## 8. Decisioni

Prese il 2026-10-13: timing ns via time mark GNSS (§4), USB-C completa (§5), eMMC 256 GB (§6), RAM LPDDR4 2 GB (§2).

PCB: 6 layer con via-in-pad (§1), scelta il 2026-10-13. Nessuna decisione aperta.

## Fonti

- [A133 Product Brief (package, PMIC, DRAM)](https://linux-sunxi.org/images/1/16/A133_Product_Brief.pdf)
- [A133 Datasheet V1.1](https://dl.linux-sunxi.org/A133/A133_Datasheet_V1.1.pdf)
- [AXP707 datasheet (LCSC)](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2204261215_X-Powers-Tech-AXP707_C2913551.pdf)
- [U-Boot: init DRAM A133 (DDR4/LPDDR4)](https://lists.denx.de/pipermail/u-boot/2025-May/589483.html)
- [Linux: EMAC A100/A133](https://patchew.org/linux/20250707165155.581579-1-paulk@sys-base.io)
- [Baijie Helper A133 DTS (AXP707 come axp803)](https://lkml.indiana.edu/2605.2/01679.html)
- [Liontron H-A133L (linux-sunxi)](https://linux-sunxi.org/Liontron_H-A133L)
- [Schema A133 con AXP707/AXP717 (whycan)](https://whycan.com/files/members/7485/sil-aa-133-001-hw-sch-v13a.pdf)
- [Micron LPDDR4/4X x32 200 sfere (datasheet su LCSC)](https://atta.szlcsc.com/upload/public/pdf/source/20241203/45C9969522F81032D42FF04706207965.pdf)
- [Kingston EMMC256-IY29-5B101](https://futureelectronics.com/p/semiconductors--memory--storage--embedded-storage/emmc256-iy29-5b101-kingston-9176810)
- [u-blox NEO-F10T product summary](https://content.u-blox.com/sites/default/files/documents/NEO-F10T_ProductSummary_UBX-22025534.pdf)
