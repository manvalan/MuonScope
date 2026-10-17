# Scheda RK3568 (ex SchedaH616): scelte di progetto e punti aperti

Data: 2026-10-16. Schema generato dagli script in `generatori/` (`build.sh` rifà tutto, ERC, PDF e mappa dei pin).
La cartella si chiama ancora `SchedaH616` per non rompere i percorsi; progetto KiCad `progetto-kicad/SchedaRK3568.kicad_pro`,
libreria di progetto `Scheda` (`Scheda.kicad_sym`, `Scheda.pretty`, `Scheda.3dshapes`).

## Cosa è cambiato rispetto alla SchedaH616

1. **eFuse tolto** (richiesta di Michele): niente TPS259470 (ex U106), RILM, partitore UVLO/OVLO, dVdT e condensatore d'ingresso.
   VIN_SYS 12 V dal BUS_POWER va direttamente all'ingresso del buck TPS56637. Restano senza fusibili anche jack e USB-C.
2. **SoC**: Allwinner H616 → **Rockchip RK3568** (FCBGA636L 19x19 mm, passo 0.65, LCSC C2938930).
3. **PMIC**: AXP313A → **RK809-5** (LCSC C2939628) + **TCS4525** per VDD_CPU su I2C0, come Rockchip AIoT REF e Radxa ROCK 3A.
4. **RAM**: LPDDR4 MT53E512M32D1ZW → **DDR4 x16 Samsung K4AAG165WA-BCWE** (LCSC C2920140, 2 GB), un chip point-to-point,
   niente VTT, VPP 2.5 V da AP2112K-2.5.
5. **TCA6416A tolto**: l'RK3568 ha GPIO a sufficienza, tutte le linee lente vanno su GPIO diretti.
6. **Bus MIKILAB su due SPI separati**: BUS_POWER su SPI3_M1, MAIN su SPI2_M1 (prima SPI1 condiviso con cs-gpios).
7. Pulsante FEL → **Recovery** su SARADC_VIN0; RESET sulla rete RESETn (RESETB dell'RK809-5 / nPOR del SoC).

Invariati: TPS56637, i due TPS2121, jack, USB-C di alimentazione con FUSB302B, SY6280AAC, TPS563201, AP2112K-1.8 per la VCCQ
dell'eMMC, eMMC FORESEE FEMDNN064G-C9A61, microSD, RTL8211F + HR911130C + 25AA02E48, AP6256, NEO-M9N con PPS/STROBE su SMA e CR1220,
USB-C host con TPS2553, connettori del bus e SMA.

## Fonti usate

| Cosa | Fonte |
|---|---|
| Ball map RK3568 | Rockchip `RK3568_PinOut_V1.1_20210202.xlsx` (fogli "Ball Map" e "PinOut List"), controllata sfera per sfera sulla tabella 2-1 del **datasheet RK3568 V1.2**: 636/636 uguali. Salvata in `generatori/rk3568_balls.json` |
| Regole di progetto RK3568 | Rockchip RK3568 Hardware Design Guide V1.2 (2022-01-26), "RK3568 Processing instructions for unused pins" V1.0 |
| Schema di riferimento | **Rockchip RK3568 AIoT REF SCH V1.1** (RK809-5 + TCS4525 + DDR4 2x16 di default): pagine 10-16 (SoC), 21-23 (alimentazione, PMIC, VDD_CPU), 28 (DDR4) |
| ROCK 3A | Schema non scaricabile (dl.radxa.com risponde 404); usato il device tree mainline `rk3568-rock-3a.dts` per l'uso dei regolatori (stesso schema del reference) |
| RK809-5 | Datasheet Rockchip RK809 Rev 2.3 (LCSC C2939628): pinout par. 2.8, default RK809-5 tabella 4-4, applicazione fig. 1-2 |
| TCS4525 | Datasheet TCS4525 Ver.1.0: pin WCSP-20, induttore 0.33/0.47 uH |
| DDR4 | Ballout JEDEC x16 FBGA-96, identico al simbolo EasyEDA di LCSC C2920140 e al simbolo "DDR4_16bit_SDP" del reference Rockchip |
| Footprint RK3568 | Generato da `generatori/gen_fp.py` (A1 in alto a sinistra, pad NSMD 0.30 mm). Confrontato con il footprint EasyEDA di C2938930: stesse 636 sfere, ruotate di 90 gradi, nessun ribaltamento |
| Resto | Come SchedaH616 (TPS56637, TPS2121, FUSB302B, NEO-M9N, RTL8211F, 25AA02E48, AP6256) |

## Fogli

1. Radice
2. **CPU** (3xx): RK3568 in 9 unità, 24 MHz, RESET e RECOVERY, console UART2, pull-up I2C0/I2C1, ferriti e condensatori USB, disaccoppiamento, DDR_RZQ e DDR_VREFOUT, interfaccia bus (serie, pull-up, ESD)
3. **Bus MIKILAB**: J1 BUS_POWER 30 pin, J2 MAIN 28 pin REV5.1 (HIT# sul pin 28), invariato
4. **Alimentazione** (1xx): TPS56637, jack con TPS2121 U108, USB-C con FUSB302B, TPS2121 U103, SY6280AAC, partitore OTG0_VBUSDET
5. **PMIC** (2xx): RK809-5, TCS4525, TPS563201 (VCC3V3_SYS), AP2112K-1.8 (VCC1V8_EMMC), AP2112K-2.5 (VCC2V5_DDR)
6. **Memorie** (4xx): DDR4 K4AAG165WA-BCWE, eMMC, microSD
7. **Rete** (5xx): RTL8211F, HR911130C, 25AA02E48
8. **Radio** (6xx): AP6256
9. **GNSS** (7xx): NEO-M9N
10. **USB host** (8xx): TPS2553 + USB-C host

I designatori dello schema sono per foglio (serie 1xx-8xx). Corrispondenza con i nomi delle note: TPS259470A "U21" = ex U106 (tolto),
H616 "U1" → RK3568 **U301**, AXP313A "U2" → RK809-5 **U201**, TCS4525 "U27" → **U202**, quarzo 32.768 kHz "Y3" → **Y201**,
DDR4 → **U401**.

## Alimentazioni

| Rail | Sorgente | Utenti |
|---|---|---|
| VIN_SYS 12 V | BUS_POWER pin 24-26 | TPS56637 (diretto, senza eFuse) |
| 5V_BUCK / 5V_JACK / 5V_EXT / 5V_SYS | TPS56637, jack, TPS2121 U108 e U103 (come prima) | 5V_SYS: TPS563201, TCS4525, TPS2553, partitore VDC dell'RK809 |
| VCC3V3_SYS 3.32 V | TPS563201 3 A, sempre acceso (EN 100k a 5V_SYS) | RK809-5 VCC1-VCC9 e VCC_RTC, VCC_SPK_HP, FUSB302B, AP2112K-1.8, AP2112K-2.5 |
| VDD_CPU 0.9 V (DVS) | TCS4525 (I2C0 0x1C, VSEL = PMIC_SLEEP_H, EN da VCC3V3_PMU) | VDD_CPU, sense VDD_CPU_COM (M15) sul FB |
| VDD_LOGIC 0.9 V | RK809-5 BUCK1 | VDD_LOGIC |
| VDD_GPU 0.9 V | BUCK2 | VDD_GPU |
| VCC_DDR 1.21 V | BUCK3, partitore 62k/120k | DDRPHY_VDDQ/VDDQL, VDD/VDDQ DDR4 |
| VDD_NPU | BUCK4 (spento all'accensione, lo accende Linux) | VDD_NPU |
| VCC_1V8 | BUCK5 | nessuno (test point TP201) |
| VDDA_0V9 / VDDA0V9_PMU | LDO2 / LDO3 | SYSPLL 0.9 V, USB3_AVDD_0V9 (ferrite) / PMUPLL e PMU_VDD_LOGIC |
| VCCIO_SD | LDO5 (3.3 V, 1.8 V per UHS) | VCCIO3 (SDMMC0), pull-up microSD |
| VCC3V3_PMU | LDO6 | PMUIO1, PMUIO2, pull-up I2C0/I2C1/RESETn/CLK32K, EN di TCS4525 e dei due AP2112K |
| VCCA_1V8 / VCCA1V8_PMU | LDO7 / LDO8 | SYSPLL 1.8 V, SARADC, OTP, USB3_AVDD_1V8 (ferrite) / PMUPLL 1.8 V |
| VCC_3V3 | SWOUT1 (2.1 A) | VCCIO4-7, USB3_AVDD_3V3, AP6256 (VBAT/VDDIO), RTL8211F, NEO-M9N, eMMC VCC, EEPROM, pull-up del bus |
| VCC3V3_SD | SWOUT2 | VDD della microSD |
| VCC1V8_EMMC | AP2112K-1.8 da VCC3V3_SYS, EN VCC3V3_PMU | VCCQ eMMC, VCCIO2 (FLASH_VOL_SEL alto) |
| VCC2V5_DDR | AP2112K-2.5 da VCC3V3_SYS, EN VCC3V3_PMU | VPP DDR4 (sale prima di VCC_DDR) |

Le periferiche che pilotano pin del SoC stanno su VCC_3V3 (SWOUT1, sequenza 4) e non più sul 3.3 V sempre acceso: così non
alimentano i domini VCCIO dai loro pin prima che il SoC sia acceso (stessa architettura del reference Rockchip).

**Sequenza** (default RK809-5 + reference): seq 1 BUCK1, LDO2/3; seq 2 BUCK2, BUCK5, LDO6, LDO7/8 → con LDO6 partono TCS4525,
VPP e VCC1V8_EMMC; seq 3 BUCK3 (VCC_DDR); seq 4 LDO5, SWOUT1/2; poi RESETB rilascia RESETn. È l'ordine raccomandato dalla
Hardware Design Guide (par. 2.2.1.2). Accensione: VDC dal partitore 100k/22k su 5V_SYS (0.9 V > 0.55 V, fronte di salita).

## Assegnazione GPIO

Tabella completa sfera per sfera in [pinmap-rk3568.md](pinmap-rk3568.md). Domini: PMUIO1/2 = VCC3V3_PMU, VCCIO2 = 1.8 V,
VCCIO3 = VCCIO_SD, VCCIO4-7 = VCC_3V3, VCCIO1 non usato (flottante come da Rockchip).

- **eMMC 8 bit** (VCCIO2): GPIO1_B4-C3 dati, C4 CMD, C5 CLKOUT (22R), C6 DATA_STROBE, C7 RSTn.
- **microSD su SDMMC0** (VCCIO3): GPIO1_D5-D7, GPIO2_A0 dati, A1 CMD, A2 CLK (22R); SDMMC0_DET = GPIO0_A4.
- **AP6256 su SDMMC2_M0** (VCCIO6): GPIO3_C6-D1 dati, D2 CMD, D3 CLK (22R). **HCI su UART8_M0** (VCCIO4): TX GPIO2_C5, RX C6, RTS B1, CTS B2.
  WL_REG_ON GPIO3_D4, BT_REG_ON D5, BT_WAKE D6, WL/BT_HOST_WAKE GPIO0_C0/C1 (dominio PMU, risveglio). LPO = CLK32K dell'RK809-5.
- **RTL8211F su GMAC0 RGMII** (VCCIO4 3.3 V): TXD0-3, TXEN, TXCLK con 22R al SoC; RXD0-3, RXDV, RXCLK con 22R al PHY (Hardware Design Guide tab. 2-42);
  MDC/MDIO GPIO2_C3/C4, MCLKINOUT GPIO2_C2 (CLKOUT del PHY tramite R520 DNP), PHY_RST_N GPIO3_D7, PHY_INT_N GPIO4_A0.
- **Console UART2_M0**: GPIO0_D1 TX, GPIO0_D0 RX su J301.
- **I2C0** (GPIO0_B1/B2): RK809-5 0x20, TCS4525 0x1C. **I2C1** (GPIO0_B3/B4): FUSB302B 0x22.
- **USB**: USB3_OTG0_DP/DM sulla USB-C di alimentazione (flash con rkdeveloptool, 2.2R serie, VBUSDET da partitore 10k/15k),
  USB3_HOST1_DP/DM sulla USB-C host (2.2R). USB2 HOST2/3, SS, PCIe, SATA non usati.
- **BUS_POWER su SPI3_M1** (VCCIO7): CLK GPIO4_C2, MOSI C3, MISO C5, CS0 INA239A C6, CS1 INA239B D1, **CS del DAC su GPIO4_C4 (cs-gpios)**.
- **MAIN su SPI2_M1** (VCCIO5): CLK GPIO3_A0, MOSI GPIO2_D6, MISO D7, CS0 = CS_MASTER D5; CS1 (D4) = EEPROM MAC 25AA02E48.
- **I2C del bus** su I2C3_M1 (GPIO3_B5/B6). ADDR_0-2 GPIO2_D0-D2, PREFIX_0-2 GPIO2_D3, GPIO3_A1, A2 (100R serie).
- **EINT e linee lente**: ALERT# GPIO3_A3, HIT# A4, GNSS PPS A5, GNSS EXTINT A6, VREF_ENABLE A7, VBIAS_ENABLE B0, DAC61402_FAULT B1.
- **GNSS su UART3_M1**: TX GPIO3_B7, RX GPIO3_C0.
- **PMU**: TSADC_SHUT_M0 GPIO0_A1 (0R su RESETn), PMIC_SLEEP GPIO0_A2, PMIC_INT GPIO0_A3, FLASH_VOL_SEL GPIO0_A7 (10k a VCC3V3_PMU),
  VBUS_SRC_EN GPIO0_A5, USB1_VBUS_EN GPIO0_A6, PD_INT_N GPIO0_B5, USB1_OC_N B6, PWR_SRC_ST B7, CLK32K_IN GPIO0_B0.

## DDR4

- U401 K4AAG165WA-BCWE sul **canale A** del PHY (DQ0-15_A): bit e byte come nel pinout Rockchip (DDR_DQx_A → DDR4_DQL/DQU_A);
  confrontato sfera per sfera con la pagina 28 del reference (chip U3300): indirizzi, comandi, DQ, DM, DQS identici.
- CA point-to-point senza serie (il reference ha 0R solo perché è a T con due chip). Canale B, ECC, CS1n, ODT1, BG1 non usati.
- ZQ 240R 1% a GND; TEN, PAR a GND; ALERT_n e T7 liberi; RESET_n con 1 nF DNP; VREFCA da DDR_VREFOUT con 0R e 2x 1 nF
  (più 1 nF a VCC_DDR e 1 nF a GND vicino al SoC); partitore 1k/1k DNP.
- **DDR_RZQ del SoC: 120R 1% a GND** (Hardware Design Guide 2.1.7.2 e reference). L'appunto parlava di "ZQ 240R": vale per la DDR4.
- VPP 2.5 V da AP2112K-2.5, abilitato da VCC3V3_PMU (seq 2), quindi prima di VCC_DDR (seq 3): VPP >= VDD come chiede JEDEC.

## Libreria MIKILAB

I componenti specifici stanno nella libreria personale **MIKILAB** (github.com/manvalan/mikilab-kicad-library, variabile `MIKILAB`;
`generatori/kilib.py` la cerca anche in `~/Develop/mikilab-kicad-library`). Simbolo e footprint MIKILAB per RK809-5, TCS4525,
K4AAG165WA-BCWE, FEMDNN064G-C9A61, AP2112K-1.8TRG1, TPS56637RPAR, TPS2121RUXR (x2), SY6280AAC, TPS563201DDCR, TPS2553DBVR,
TYPE-C-31-M-12 (x2), FH12-30S-0.5SH, FPC-05F-28PH20, HR911130C, 25AA02E48T-I/OT, DM3AT-SF-PEJM5; simbolo MIKILAB per l'AP6256.

Restano nella libreria di progetto `Scheda`:
- **RK3568**: il footprint EasyEDA ha pad da 0.35 mm, tra due sfere restano 0.30 mm e una pista da 5 mil con 0.1 mm per lato
  (0.327 mm) non passa; quello di progetto ha pad NSMD 0.30 mm. Il simbolo di progetto è in 9 unità leggibili.
- **RTL8211F**: footprint MIKILAB, ma simbolo di progetto: quello MIKILAB ha AVDD10/AVDD33 come pin di alimentazione nascosti,
  che KiCad collega a net globali con quel nome (VCC_3V3 diventava "AVDD33").
- **AP6256** footprint LGA-47 (in MIKILAB c'è solo quello QFN-44 dell'AP6212) e il portapila BS-12-B3AA003. In `Scheda.pretty` restano anche le vecchie copie di RJ45, FPC-05F e RPA0010A, non più usate.
- Restano dalle librerie standard KiCad i componenti generici (R, C, L, connettori, protezioni, AP2112K-2.5, FUSB302B, NEO-M9N, 74LVC1G17).

I simboli EasyEDA hanno pin "unspecified": `add_flags.py` imposta nella matrice ERC del progetto unspecified = OK con tutti i tipi
(tranne no_connect). Correzioni fatte ai footprint della libreria MIKILAB: via termiche dell'RK809-5 numerate 69, pioli della
TYPE-C-31-M-12 e dell'HR911130C non metallizzati, serigrafia dell'HR911130C fuori dai pad, margine maschera del RTL8211F 0.05 mm.

## Incongruenze tra le note e i datasheet (vince il datasheet)

1. **BUCK4 dell'RK809-5 come 3.3 V**: non possibile. Sull'RK809-5 BUCK4 è spento all'accensione a 0.5 V (datasheet tabella 4-4).
   Se tutto il 3.3 V dipendesse da BUCK4 la scheda resterebbe spenta. Il 3.3 V resta sul TPS563201 (VCC3V3_SYS), come nel reference
   Rockchip e sulla ROCK 3A; BUCK4 alimenta **VDD_NPU** (come ROCK 3A). BUCK2 alimenta solo VDD_GPU.
2. **VDD_GPU/NPU insieme su BUCK2**: Rockchip non prevede di unirli (per l'NPU non usata indica "VDD_NPU flottante"); con BUCK4 libero
   l'NPU ha il suo regolatore come nel reference.
3. **ZQ 240R 1%**: per il SoC (DDR_RZQ) con DDR4 serve **120R 1% a GND**; 240R è lo ZQ della DDR4.
4. **"BUS_POWER e MAIN su due SPI separati, niente CS su GPIO"**: il BUS_POWER ha tre slave (INA239A, INA239B, DAC61402) e ogni SPI
   dell'RK3568 ha solo due CS hardware (CS0/CS1). Il terzo CS (DAC) è per forza un GPIO (cs-gpios, GPIO4_C4).
5. **Pulsante FEL → Recovery su SARADC_VIN0 "pull-down al boot"**: Rockchip chiede 10k a 1.8 V su SARADC_VIN0; il tasto porta a GND.
   È la stessa cosa vista dal loader (VIN0 basso all'avvio = Recovery), messo come pull-up + tasto.
6. **AP6256 su SDMMC2 + UART8**: UART8 con RTS/CTS esiste solo come M0, nel dominio VCCIO4 insieme al GMAC0: VCCIO4 e VCCIO6 sono
   quindi entrambi a 3.3 V (VDDIO dell'AP6256 = 3.3 V). Rockchip raccomanda 1.8 V per l'RGMII; restiamo a 3.3 V per non cambiare gli
   strap del RTL8211F (punto aperto 3).
7. **VCC_SPK_HP**: il reference lo prende dal 5 V, ma il datasheet chiede che VCC_RTC (qui VCC3V3_SYS) sia la tensione più alta
   dell'RK809. Con il codec non usato VCC_SPK_HP va su VCC3V3_SYS.
8. **"VCC_DDR 1.2 V"**: con il partitore del reference (62k/120k, FB 0.8 V) vale 1.21 V.
9. Il pacchetto LCSC della DDR4 dice 13.3 x 10.3 mm; il footprint KiCad usato è BGA-96 9.0 x 13.0 (stessa griglia 0.8 mm JEDEC):
   corpo da confermare sul datasheet Samsung completo (punto aperto 6).

## Punti aperti

1. **TPS563201 al limite**: VCC3V3_SYS alimenta i buck dell'RK809-5 (VDD_LOGIC, GPU, NPU, DDR, 1V8), gli LDO e, tramite SWOUT1/2,
   tutte le periferiche a 3.3 V: stima 2.5-3 A di picco su 3 A. Valutare un buck da 4-6 A (il reference usa un SY8113 3 A con il
   5 V separato, ma lì AP6256 e PHY pesano meno). Il TCS4525 (VDD_CPU) è già sul 5 V.
2. **Template DDR4 16 bit**: la Hardware Design Guide chiede di usare il template Rockchip per le configurazioni a 16 bit; qui ci sono
   solo i template a 32 bit (2x16). Collegamento fatto sul canale A secondo il pinout, da confermare con il template DDR4 16 bit o con
   il loader (ddrbin) prima del layout. Il loader va configurato per 16 bit.
3. **RGMII a 3.3 V**: Rockchip raccomanda 1.8 V. Per passare a 1.8 V servono VCCIO4 a 1.8 V (e quindi anche UART8 e l'AP6256,
   oppure HCI su un'altra UART) e gli strap CFG_LDO del RTL8211F.
4. **Quarzo 24 MHz**: 18 pF come il reference; da adattare al CL del quarzo scelto (X322524MOB4SI), tolleranza <= 20 ppm.
5. **TCS4525**: codice LCSC non trovato (c'è il TCS4526_WT C7501360); induttore 0.33 uH XAL4020-331 da verificare sul datasheet completo.
6. **Corpo DDR4**: footprint BGA-96 9.0 x 13.0 mm; verificare il disegno del package K4AAG165WA-BC (la griglia delle sfere è standard).
7. **Footprint RK3568**: pad NSMD 0.30 mm (la sfera è 0.35 mm), da confermare con le regole JLCPCB per BGA 0.65 e via-in-pad.
8. **AP6256 sotto il NEO-M9N** (lati opposti della scheda): coesistenza Wi-Fi/GNSS da valutare; in alternativa spostare l'AP6256.
9. **SY6280AAC**: VBUS_SRC_EN ora su GPIO0_A5; il FUSB302B resta sull'I2C1.
10. **CR1220**: solo per il V_BCKP del NEO-M9N (l'RTC dell'RK809-5 è alimentato da VCC3V3_SYS, niente batteria).
11. Restano dalla SchedaH616: V_USB del NEO-M9N a GND da confermare, valori della rete π del Wi-Fi e del bias dell'antenna GNSS.
12. **PCB**: placement 70 x 90 a 6 strati fatto (2026-10-17, prima 50 x 70), tutto sul top tranne il disaccoppiamento sotto SoC e DDR4, senza piste: vedi [pcb-placement.md](pcb-placement.md).
