# SchedaH616: scelte di progetto e punti aperti

Data: 2026-10-16. Schema generato dagli script in `generatori/` (`build.sh` rifà tutto, ERC e PDF).
Le voci **[NON VERIFICATO]** sono da controllare prima del layout.

## Fonti usate

| Cosa | Fonte |
|---|---|
| Ball map H616 | Datasheet Allwinner H616 V1.0 (linux-sunxi, `H616_Datasheet_V1.0_cleaned.pdf`), tabella 4-2, letta con `generatori/parse.py` e controllata sfera per sfera sulla figura 7-1 |
| Mux GPIO H616 | Stesso datasheet, tabella 4-3 |
| Tensioni H616 | Stesso datasheet, tabella 5-2 |
| AXP313A | Datasheet X-Powers v1.0 (LCSC C5365290): tabella pin, limiti, note applicative |
| LPDDR4 | Chip e ball map già usati sulla SchedaA133 (MT53E512M32D1ZW-046 IT:B); mappa CA/CS ricavata da U-Boot (vedi sotto) |
| NEO-M9N | Data sheet u-blox UBX-19014285 R08, tabella 9 |
| TPS259470 | Datasheet TI SLVSFC9C (pin, soglie UVLO/OVLO, ILIM, land pattern RPW0010A) |
| TCA6416A | Datasheet TI, tabella 5-1 |
| 25AA02E48 | Datasheet Microchip DS20002123G, tabella 4-1 |
| FUSB302B | Datasheet onsemi: I2C VIH 1.32 V, pull-up tra 1.71 V e VDD (va bene a 1.8 V), dead battery supportato |

Lo schema Orange Pi Zero3 non si è potuto scaricare: Google Drive ha superato la quota e il mirror ha risposto 403.
Le parti che il brief chiedeva di prendere da lì (PMIC, LPDDR4, disaccoppiamento) seguono i datasheet e il DTS
mainline della Zero3 (AXP313A su r_i2c 0x36, DCDC1 VDD-GPU-SYS, DCDC2 VDD-CPU, DCDC3 VDD-DRAM, ALDO1 1.8 V, DLDO1 3.3 V).
Il confronto con lo schema resta da fare.

## Fogli

1. Radice
2. **CPU** (3xx): H616 in 5 unità, quarzo 24 MHz, RESET/FEL, UART0, SPI1 condiviso con le serie, pull-up/pull-down del bus, ESD, espansore TCA6416A
3. **Bus MIKILAB**: J1 BUS_POWER 30 pin, J2 MAIN 28 pin REV5.1 (HIT# sul pin 28), invariato rispetto alla A133
4. **Alimentazione** (1xx): eFuse TPS259470 sui 12 V, TPS56637 5 V, jack con Schottky, USB-C con FUSB302B e TPD2EUSB30A, TPS2121, SY6280AAC
5. **PMIC** (2xx): AXP313A, buck TPS563201 3V3_PERI
6. **Memorie** (4xx): LPDDR4 x32 2 GB, eMMC 64 GB 8 bit, microSD
7. **Rete** (5xx): RTL8211F, HR911130C, EEPROM MAC 25AA02E48
8. **Radio** (6xx): AP6256
9. **GNSS** (7xx): NEO-M9N, PPS e STROBE su SMA, CR1220 sul V_BCKP
10. **USB host** (8xx): TPS2553 e presa USB-A

## Verifiche richieste dal brief

- **Bus DRAM a 16 bit**: il datasheet H616 dichiara solo un'interfaccia a 32 bit (paragrafo 2.3.2). U-Boot ha il supporto half-width (`bus_full_width`), ma è collaudato poco.
- **DDR4**: U-Boot mainline (`arch/arm/mach-sunxi/dram_sun50i_h616.c`, master del 2026-10-16) va in `panic("This DRAM setup is currently not supported")` su ogni ramo `SUNXI_DRAM_TYPE_DDR4`. Sono supportati solo DDR3, LPDDR3 e LPDDR4. Per questo lo schema usa **un chip LPDDR4 x32 come la Orange Pi Zero3**: niente VTT, niente TPS51200, niente VPP (l'AP2112K-2.5 e la K4AAG165WA della BOM escono). **Decisione di Michele ancora aperta.**
- **NEO-M9N**: EXTINT c'è, sul pin 4 (PIO7) della tabella 9. Il datasheet non nomina TIM-TM2; il time mark è descritto nell'integration manual (verificato dal coordinatore).
- **ZQ**: 240R 1% sul SoC (SZQ, R304). Sulla LPDDR4 ci sono 2 x 240R 1% verso VDDQ (ZQ0/ZQ1). Niente VTT.

## Alimentazioni

| Rail | Sorgente | Utenti |
|---|---|---|
| VIN_SYS 12 V | BUS_POWER pin 24-26 | eFuse TPS259470 (3 A, UVLO 9.7 V, OVLO 15.1 V, blocco inverso) |
| 5V_EXT | TPS56637 6 A, oppure jack attraverso uno Schottky SS54 | TPS2121 IN1, SY6280AAC |
| 5V_SYS | TPS2121 (IN1 5V_EXT con priorità, IN2 VBUS USB-C) | AXP313A, TPS563201, TPS2553 |
| VDD-SYS 0.9 V | AXP313A DCDC1 | VDD_SYS + VDD_GPU (insieme, come la Zero3), sense da VDD_GPUFB |
| VDD-CPU | AXP313A DCDC2 | VDD_CPU, sense da VDD_CPUFB |
| VCC-DRAM 1.1 V | AXP313A DCDC3 | VCC_DRAM del SoC, VDD2/VDDQ LPDDR4, sense sulla LPDDR4 (R405) |
| VCC-1V8 | AXP313A ALDO1 (300 mA) | VCC_PLL, VDD18_DRAM, VCC_DCXO, AVCC, AC_AVCC, VCC_HDMI, VCC_TV, VCC_PC (VCCQ eMMC), VDD1 LPDDR4, VCCI TCA6416A, pull-up S_TWI0 |
| VCC-IO 3.3 V | AXP313A DLDO1 (500 mA) | VCC_IO, VCC_PG, VCC_PI, VCC_USB, VCC_EPHY, VDDIO AP6256, VCCP TCA6416A, pull-up del bus, VDD FUSB302B |
| 3V3_PERI | TPS563201 3 A (EN da VCC-IO) | AP6256 VBAT, RTL8211F, NEO-M9N, VCC eMMC, microSD, EEPROM |

Fusibili: F101 era già stato sostituito dall'eFuse. Su richiesta di Michele sono tolti anche quello del jack (F102) e
quello del VBUS USB-C (il 1812L300 indicato come F1 nella BOM). Al posto di LM74700 + Q101 il blocco inverso lo fa
l'eFuse, e il jack entra su 5V_EXT con uno Schottky. Così il jack non spinge corrente nell'uscita del buck.

## Assegnazione GPIO

La tabella completa, sfera per sfera, è in [pinmap-h616.md](pinmap-h616.md). In sintesi:

- **SMHC2 eMMC 8 bit**: PC0 DS, PC1 RST, PC5 CLK, PC6 CMD, PC8-PC11 e PC13-PC16 dati. VCC_PC a 1.8 V (HS200/HS400).
- **SMHC0 microSD**: PF0-PF5 (3.3 V). Il rilevamento della scheda va sull'espansore (P15). PF6 diventa PREFIX_2.
- **SMHC1 + UART1 AP6256**: PG0-PG5 e PG6-PG9. LPO a 32 kHz da X32KFOUT su PG10.
- **EMAC0 RGMII**: PI0-PI5 e PI7-PI13, MDC su PI14, MDIO su PI15. PI6 (RGMII_NULL) e PI16 restano liberi e diventano PREFIX_0/1.
- **UART0 debug**: PH0/PH1 su J301. PF2/PF4 servono alla microSD.
- **SPI1 condiviso BUS_POWER/MAIN**: PH6 CLK, PH7 MOSI, PH8 MISO, con un 33R serie per ogni ramo. Chip select (cs-gpios): PH5 CS_MASTER (SPI1_CS0), PH9 INA239A (SPI1_CS1), PH4 INA239B, PH10 DAC. SPI0 non è usabile perché è sugli stessi pin dell'eMMC.
- **I2C del bus**: TWI2 su PH2/PH3.
- **ADDR_0..2**: PG17-PG19. **PREFIX_0..2**: PI6, PI16, PF6. Tutti con 100R serie.
- **EINT**: ALERT# PG11, HIT# PG12, GNSS PPS PG13, GNSS EXTINT PG14 (solo ingresso: EXTINT lo pilota il buffer dello STROBE).
- **GNSS**: UART2 su PG15/PG16.
- **S_TWI0** (PL0/PL1, 1.8 V): AXP313A 0x36, FUSB302B 0x22, TCA6416A 0x20.
- **Ingressi open-drain a 1.8 V su PC**: PC2 INT del TCA6416A, PC7 INT del FUSB302B, PC12 FAULT del TPS2553. PC3/PC4 (BOOT_SEL1/2) liberi, con il pull-up interno.

**Perché serve l'espansore TCA6416A** (non è in BOM): l'H616 non ha PB/PD/PE. Tolti eMMC, SD, SDIO, RGMII, UART0 e SPI1,
restano 14 GPIO a 3.3 V, esattamente quanti ne servono per CS, I2C, ADDR/PREFIX, ALERT#, HIT#, PPS ed EXTINT.
Le linee lente vanno quindi su un TCA6416A a doppia alimentazione (I2C a 1.8 V, porte a 3.3 V):
VREF_ENABLE, VBIAS_ENABLE, DAC61402_FAULT, USB1_VBUS_EN, VBUS_SRC_EN, PWR_SRC_ST, PHY_RST_N, PHY_INT_N, WL/BT_REG_ON,
BT_WAKE, BT/WL_HOST_WAKE, SD_DET, CS dell'EEPROM MAC, FLT dell'eFuse. Al reset le porte sono ingressi, e i pull-up/pull-down
esterni mettono tutto nello stato sicuro: riferimenti e bias spenti, radio spenta, USB spenta, EEPROM deselezionata.

## LPDDR4: mappa CA/CS

L'H616 ha un rimappatore degli indirizzi nel PHY. U-Boot lo programma con la tabella `phy_init`
(`CONFIG_DRAM_SUNXI_PHY_ADDR_MAP_0`, indicata per H313/H616/H618/A133). Leggendo la tabella con lo schema
"posizione i = sfera SAi (0-16), 23 = SCS0, 25 = SCS1; valore = segnale del chip (0-5 = CA0-5, 0x17 = CS0, 0x19 = CS1)",
la tabella LPDDR4 dell'A133 riproduce esattamente il collegamento del reference Allwinner A133 già usato sulla SchedaA133:
CA0<-SA5, CA1<-SA0, CA2<-SA2, CA3<-SA1, CA4<-SCS0, CA5<-SCS1, CS0<-SA4, CS1<-SA3, con 8 corrispondenze su 8.
Con lo stesso schema la tabella LPDDR4 dell'H616 dà:

| LPDDR4 | Sfera H616 |
|---|---|
| CA0 | SA1 (U17) |
| CA1 | SCS0 (V17) |
| CA2 | SA0 (T21) |
| CA3 | SCS1 (R20) |
| CA4 | SA4 (R18) |
| CA5 | SA3 (T16) |
| CS0 | SA2 (T18) |
| CS1 | SA5 (P15), sfera NC sul chip a singolo rank |
| CKE0/CKE1 | SCKE0/SCKE1 |
| CK_t/CK_c | SCKP/SCKN |
| RESET_n | SRST |

**[NON VERIFICATO]**: è una deduzione, da confrontare con lo schema della Orange Pi Zero3 prima del layout.
I dati sono dritti: canale A = byte 0-1 del SoC, canale B = byte 2-3. I CA vanno in comune ai due canali, come nel reference A133.
SA6-SA16, SBA, SBG, SACT e SODT non sono usati.

## Punti aperti

1. **Tipo di DRAM**: LPDDR4 (supportata in mainline), DDR3L, oppure DDR4 con il boot0 del BSP. Decide Michele.
2. **Mappa CA/CS della LPDDR4** [NON VERIFICATO]: va confrontata con lo schema Orange Pi Zero3.
3. **AC_VRA1**: C17 (figura e footprint) o D17 (tabella)? Lo schema usa C17.
4. **Pin di sistema lasciati liberi** [NON VERIFICATO]: JTAG_SEL, PLLTEST, LRADC, REXT, uscite HDMI/TV/LINEOUT/EPHY, USB2/USB3. VCC_HDMI, VCC_TV, AC_AVCC sono a 1.8 V e VCC_EPHY a 3.3 V anche se i blocchi non si usano: da confrontare con la Zero2/Zero3.
5. **AXP313A** [NON VERIFICATO]: tensioni di default e sequenza sono una personalizzazione di fabbrica. DCDC3 deve partire a 1.1 V per la LPDDR4. IRQ non collegato (manca un GPIO), PWRON su test point. ALDO1 (300 mA) alimenta tutti i 1.8 V: va fatto il bilancio dei consumi. AVCC chiede ±2%, ALDO1 garantisce ±3%.
6. **Accensione**: l'AXP313A si accende quando arriva VIN, se la personalizzazione lo prevede (Zero3: sì).
7. **AP6256**: LPO da X32KFOUT (PG10), che sull'H616 è derivato dal 24 MHz (non c'è un quarzo a 32 kHz). Va verificata la precisione richiesta dal modulo. Il quarzo Y3 a 32.768 kHz della BOM non serve.
8. **CR1220**: l'H616 non ha un pin VCC_RTC e l'AXP313A non ha un pin di backup. La pila resta solo sul V_BCKP del NEO-M9N (D701/D704).
9. **NEO-M9N**: V_USB a GND con la USB non usata, da confermare sull'integration manual.
10. **SPI1 condiviso**: le MISO di BUS_POWER, MAIN ed EEPROM sono in parallelo. Tutti gli slave devono mettere SDO in alta impedenza quando il loro CS è alto.
11. **Footprint**: RPW0010A (TPS259470) disegnato in scala dal land pattern TI, da rifare con le quote. Da scegliere eMMC 64 GB e induttori dei DCDC dell'AXP313A. Il footprint H616 viene da EasyEDA (pad 0.256 mm su sfere da 0.35 mm): da confrontare con la figura 7-2.
12. **Valori da confermare**: condensatore dVdT dell'eFuse, disaccoppiamento H616/LPDDR4 (manca il reference), carico del quarzo, rete π del Wi-Fi, bias dell'antenna GNSS.
13. **Il PCB non è iniziato.**
