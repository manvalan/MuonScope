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

Lo schema Orange Pi Zero3 ("OrangePi-Schematic of ZERO3.pdf", condiviso da Michele, non pubblicato nel repo) è stato usato per verificare la LPDDR4, l'AXP313A e la parte analogica e di reset dell'H616.
Per i pin di sistema dell'H616 è stato usato anche lo schema Orange Pi Zero2 (H616) v1.3, pagine SOC1/SOC2.
La Zero2 ha DDR3 e AXP305, quindi non dice nulla su LPDDR4 e AXP313A.

## Fogli

1. Radice
2. **CPU** (3xx): H616 in 5 unità, quarzo 24 MHz, RESET/FEL, UART0, SPI1 condiviso con le serie, pull-up/pull-down del bus, ESD, espansore TCA6416A
3. **Bus MIKILAB**: J1 BUS_POWER 30 pin, J2 MAIN 28 pin REV5.1 (HIT# sul pin 28), invariato rispetto alla A133
4. **Alimentazione** (1xx): eFuse TPS259470 sui 12 V, TPS56637 5 V, jack con TPS2121 U108, USB-C con FUSB302B e TPD2EUSB30A, TPS2121, SY6280AAC
5. **PMIC** (2xx): AXP313A, buck TPS563201 3V3_PERI
6. **Memorie** (4xx): LPDDR4 x32 2 GB, eMMC 64 GB 8 bit, microSD
7. **Rete** (5xx): RTL8211F, HR911130C, EEPROM MAC 25AA02E48
8. **Radio** (6xx): AP6256
9. **GNSS** (7xx): NEO-M9N, PPS e STROBE su SMA, CR1220 sul V_BCKP
10. **USB host** (8xx): TPS2553, USB-C solo host (TYPE-C-31-M-12, Rp 22k, USBLC6-2) come sulla SchedaA133

## Verifiche richieste dal brief

- **Bus DRAM a 16 bit**: il datasheet H616 dichiara solo un'interfaccia a 32 bit (paragrafo 2.3.2). U-Boot ha il supporto half-width (`bus_full_width`), ma è collaudato poco.
- **DDR4**: U-Boot mainline (`arch/arm/mach-sunxi/dram_sun50i_h616.c`, master del 2026-10-16) va in `panic("This DRAM setup is currently not supported")` su ogni ramo `SUNXI_DRAM_TYPE_DDR4`. Sono supportati solo DDR3, LPDDR3 e LPDDR4. **Scelta definitiva (Michele, 2026-10-16): una LPDDR4 x32 MT53E512M32D1ZW come la Orange Pi Zero3.** Niente VTT, niente TPS51200, niente VPP: l'AP2112K-2.5 e la K4AAG165WA della BOM escono.
- **NEO-M9N**: EXTINT c'è, sul pin 4 (PIO7) della tabella 9. Il datasheet non nomina TIM-TM2; il time mark è descritto nell'integration manual (verificato dal coordinatore).
- **ZQ**: 240R 1% sul SoC (SZQ, R304). Sulla LPDDR4 ci sono 2 x 240R 1% verso VDDQ (ZQ0/ZQ1). Niente VTT.

## Alimentazioni

| Rail | Sorgente | Utenti |
|---|---|---|
| VIN_SYS 12 V | BUS_POWER pin 24-26 | eFuse TPS259470 (3 A, UVLO 9.7 V, OVLO 15.1 V, blocco inverso) |
| 5V_BUCK | TPS56637 6 A (FCCM) | IN1 del TPS2121 U108 |
| 5V_JACK | jack 5 V, TVS D101 | IN2 del TPS2121 U108 |
| 5V_EXT | TPS2121 U108 (bus con priorità, poi jack) | IN1 del TPS2121 U103, SY6280AAC |
| 5V_SYS | TPS2121 (IN1 5V_EXT con priorità, IN2 VBUS USB-C) | AXP313A, TPS563201, TPS2553 |
| VDD-SYS 0.9 V | AXP313A DCDC1 | VDD_SYS + VDD_GPU (insieme, come la Zero3), sense da VDD_GPUFB |
| VDD-CPU | AXP313A DCDC2 | VDD_CPU, sense da VDD_CPUFB |
| VCC-DRAM 1.1 V | AXP313A DCDC3 | VCC_DRAM del SoC, VDD2/VDDQ LPDDR4, sense sulla LPDDR4 (R405) |
| VCC-1V8 | AXP313A ALDO1 (300 mA) | VCC_PLL, VDD18_DRAM, VCC_DCXO, AVCC, AC_AVCC, VCC_HDMI, VCC_TV, VDD1 LPDDR4, VCCI TCA6416A, pull-up S_TWI0 |
| VCC-1V8-EMMC | LDO AP2112K-1.8TRG1 (LCSC C176944, 600 mA) da 3V3_PERI, EN legato a VIN | VCCQ eMMC (fino a ~132 mA in HS400, Kingston EMMC16G-MW28 tabella 3), VCC_PC dell'H616, pull-up open-drain su PC |
| VCC-IO 3.3 V | AXP313A DLDO1 (500 mA) | VCC_IO, VCC_PG, VCC_PI, VCC_USB, VCC_EPHY, VDDIO AP6256, VCCP TCA6416A, pull-up del bus, VDD FUSB302B |
| 3V3_PERI | TPS563201 3 A (EN da VCC-IO) | AP6256 VBAT, RTL8211F, NEO-M9N, VCC eMMC, microSD, EEPROM, LDO VCC-1V8-EMMC |

Fusibili: F101 era già stato sostituito dall'eFuse. Su richiesta di Michele sono tolti anche quello del jack (F102) e
quello del VBUS USB-C (il 1812L300 indicato come F1 nella BOM). LM74700 e Q101 sono tolti, il blocco verso il bus lo fa l'eFuse.

**Jack 5 V con secondo TPS2121 (U108)** (scelta di Michele, 2026-10-16). Con il jack direttamente su IN1 del TPS2121 U103, jack e buck
finivano in parallelo: il blocco rapido della corrente inversa (RCB, paragrafo 9.3.6) separa gli ingressi dall'uscita, ma non due
sorgenti sullo stesso IN1. Ora la catena è:

- **U108**: IN1 = 5V_BUCK (bus 12 V), IN2 = 5V_JACK. L'uscita 5V_EXT va a IN1 di **U103**, che ha IN2 = VBUS USB-C. L'uscita di U103 è 5V_SYS.
- **Priorità: bus > jack > USB-C.** Il bus è l'alimentazione di esercizio, il jack è per il banco, l'USB-C è l'ultima risorsa (1.5-3 A).
- **U108**, valori dal datasheet SLVSEA3F:
  - PR1 = 1.06 V x (32.4k+10k)/10k = 4.49 V: sotto questa soglia passa al jack.
  - CP2 a GND: priorità fissa su IN1.
  - OV1/OV2 a 5.98 V (46.4k/10k).
  - ILM 22.1k = 4-5 A.
  - SS 100 nF.
  - ST (basso = uscita dal jack) con 100k a 5V_EXT e test point TP101.
- **TPS56637 di nuovo in FCCM** (R114 DNP): il buck è isolato da U108 e non vede corrente inversa. FCCM dà frequenza fissa e ripple basso,
  meglio vicino al GNSS. L'Eco-mode serviva solo con il jack in parallelo.
- Con solo il jack, il buck è spento e la sua uscita è separata da U108. L'eFuse continua a bloccare verso il bus.

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
- **Ingressi open-drain a 1.8 V su PC**: PC2 INT del TCA6416A, PC7 INT del FUSB302B, PC12 FAULT del TPS2553, con pull-up a VCC-1V8-EMMC (= VCC_PC). PC3/PC4 (BOOT_SEL1/2) liberi, con il pull-up interno.

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

**VERIFICATA** sullo schema Orange Pi Zero3 (pagina LPDDR4, tabella DDR3/DDR4/LPDDR3/LPDDR4 del simbolo H616):
sfera SA1 (U17) → CA0, SCS0 (V17) → CA1, SA0 (T21) → CA2, SCS1 (R20) → CA3, SA4 (R18) → CA4, SA3 (T16) → CA5, SA2 (T18) → CS0, SA5 (P15) → CS1,
SCKP/SCKN (T14/U14) → CK_t/CK_c, SCKE0/SCKE1 (V15/P13) → CKE0/CKE1, SRST (U21) → RESET_n. CA, CK, CKE e CS sono comuni ai canali A e B.
Corrispondono anche le sfere della LPDDR4 (29 sfere CA/CS/CK/CKE/ODT/RESET/ZQ confrontate), ODT_CA_A/B a VCC-DRAM con 100k
(RD1/RD2 R0201 "100K" sullo schema; il riassunto del coordinatore diceva 10k, ma il disegno riporta 100K), ZQ0/ZQ1 240R 1% a VCC-DRAM,
VDD1 = 1.8 V, VDD2/VDDQ = VCC-DRAM.

Linee dati: sulla Zero3 il canale A usa i byte 2-3 del SoC e il canale B i byte 0-1, con scambi di bit dentro ogni byte e del byte dentro
il canale. La nostra assegnazione (A = byte 0-1, B = byte 2-3, bit dritti) è equivalente, perché i CA sono in comune. In sbroglio si possono
scambiare i bit dentro un byte (DQ0-7 con il suo DQS/DM), come fa la Zero3.
I dati sono dritti: canale A = byte 0-1 del SoC, canale B = byte 2-3. I CA vanno in comune ai due canali, come nel reference A133.
SA6-SA16, SBA, SBG, SACT e SODT non sono usati.

## Punti aperti

1. **DRAM**: decisa, LPDDR4 MT53E512M32D1ZW (2026-10-16).
2. **Mappa CA/CS della LPDDR4**: **verificata** sullo schema Orange Pi Zero3, 8/8 identica (vedi sotto).
3. **AC_VRA1**: risolto, C17 (figura 7-1, footprint EasyEDA, schema Orange Pi Zero2 v1.3). La tabella 4-2 del datasheet dice D17 per errore.
4. **Pin di sistema**, confrontati con lo schema Orange Pi Zero2 (H616 + AXP305 + DDR3) v1.3, pagine SOC1/SOC2:
   - REXT (K18): 150k 1% ad AGND (R337), aggiunta.
   - Analogica: VRA1/VRA2 470 nF, AVCC 2.2 uF (C334, aggiunto), AC_AVCC 2.2 uF (C335, aggiunto), AC_VRA1 1 uF, DXLDO_OUT 220 nF. 100 nF su VCC-PLL, DCXO, HDMI, TV, VCC_IO/PG/PI, USB, EPHY.
   - RESET (A16): 10k a VCC-1V8 (= VCC-PLL) e 1 nF, collegato al PWROK del PMIC. Era già così.
   - JTAG_SEL (C16): non collegato come sulla Zero2 (JTAG di default su PF).
   - VCC_PC a 1.8 V per l'eMMC. VCC_PG a 3.3 V = VDDIO dell'AP6256.
   - Restano liberi PLLTEST, LRADC, le uscite HDMI/TV/LINEOUT/EPHY e USB2/USB3. VCC_HDMI e VCC_TV sono a 1.8 V e VCC_EPHY a 3.3 V, come sulla Zero2.
   - La Zero2 ha DDR3 e AXP305: **non** verifica la mappa CA/CS della LPDDR4 né i default dell'AXP313A, che restano aperti fino allo schema Zero3.
5. **AXP313A**, verificato sullo schema Orange Pi Zero3 (pagina PMU):
   - collegamenti identici: DCDC1 → VDD-GPU/SYS con sense da VDD-GPUFB, DCDC2 → VDD-CPU con sense da VDD-CPUFB, DCDC3 → VCC-DRAM senza strap, pin 8 con 1 uF, PWRON con 100 nF e test point, PWROK → AP-RESET con 1 nF;
   - valori allineati alla Zero3:
     - 22 uF su ogni VIN;
     - VDD-SYS, VDD-CPU e VCC-DRAM con 2x47 uF + 1 uF + 100 nF;
     - DLDO1 con 47 uF + 100 nF;
     - RTCLDO con 4.7 uF (l'H616 non lo usa);
     - induttori 1 uH (la Zero3 usa 2520 da 2 A);
   - **DCDC3 a 1.1 V**: lo imposta l'SPL di U-Boot prima di inizializzare la DRAM (`CONFIG_AXP_DCDC3_VOLT`, default 1100 per AXP313, usato anche da `orangepi_zero3_defconfig` con `SUNXI_DRAM_H616_LPDDR4`). Il default di accensione resta una personalizzazione di fabbrica.
   - IRQ: la Zero3 lo porta su PC9 con 0R. Qui resta non collegato, perché gli unici PC liberi (PC3/PC4) sono strap BOOT_SEL.
   - Bilancio di ALDO1: mancano ancora i consumi a 1.8 V della LPDDR4 (VDD1) e dell'H616. AVCC chiede ±2%, ALDO1 garantisce ±3%.
6. **Accensione**: l'AXP313A si accende quando arriva VIN, se la personalizzazione lo prevede (Zero3: sì).
7. **AP6256**: LPO da X32KFOUT (PG10), che sull'H616 è derivato dal 24 MHz (non c'è un quarzo a 32 kHz). Va verificata la precisione richiesta dal modulo. Il quarzo Y3 a 32.768 kHz della BOM non serve.
8. **CR1220**: l'H616 non ha un pin VCC_RTC e l'AXP313A non ha un pin di backup. La pila resta solo sul V_BCKP del NEO-M9N (D701/D704).
9. **NEO-M9N**: V_USB a GND con la USB non usata, da confermare sull'integration manual.
10. **SPI1 condiviso**: le MISO di BUS_POWER, MAIN ed EEPROM sono in parallelo. Tutti gli slave devono mettere SDO in alta impedenza quando il loro CS è alto.
11. **Footprint**: RPW0010A (TPS259470) disegnato in scala dal land pattern TI, da rifare con le quote. Da scegliere eMMC 64 GB e induttori dei DCDC dell'AXP313A. Il footprint H616 viene da EasyEDA (pad 0.256 mm su sfere da 0.35 mm): da confrontare con la figura 7-2.
12. **Valori da confermare**: condensatore dVdT dell'eFuse, carico del quarzo 24 MHz (ora 12 pF per lato come la Zero3), rete π del Wi-Fi, bias dell'antenna GNSS.
14. **Dalla Zero3, applicato il 2026-10-16**: RESET dell'H616 con 10k a VCC-1V8, 1 nF e 100R in serie verso il PWROK (AP-RESET); AC_AVCC 10 uF (2.2 uF sulla Zero2); quarzo 24 MHz con 12 pF; REXT 150k 1% confermato.
15. **Differenze volute rispetto alla Zero3**:
    - VCC_PG è a 3.3 V (sulla Zero3 è a 1.8 V da ALDO1): l'AP6256 lavora con VDDIO 3.3 V.
    - VCC_PC è a 1.8 V con un LDO dedicato (sulla Zero3 è a 3.3 V, che ha SPI flash e non ha eMMC): serve per l'eMMC in HS200/HS400.
16. **Strap BOOT_SEL[4:1] = PC6/PC5/PC4/PC3** [NON VERIFICATO, ordine di boot da confermare]:
    - Il datasheet H616 dice solo "Boot Media Select". La tabella livelli → supporto è nello User Manual H616 §3.4, che non abbiamo, e linux-sunxi non riporta l'ordine di boot dell'H616.
    - Zero2: nessuno strap, boot da SD e SPI NOR. Zero3 (blocco "SPI BOOT"): 10k pull-up su PC3/PC4/PC6, 10k pull-down su PC5.
    - **Scelta**: nessuno strap montato, come la Zero2. Ci sono footprint 10k **DNP** su ogni linea, uno di pull-up a VCC-1V8-EMMC (= VCC_PC) e uno di pull-down a GND: R340-R347 sul foglio CPU. La configurazione si può cambiare dopo le prime prove.
    - PC6 (CMD dell'eMMC) ha già un pull-up 10k montato (R407, richiesto dall'eMMC), quindi oggi BOOT_SEL4 = 1. PC3-PC5 restano con il pull-up interno al reset.
    - In layout, i footprint DNP su PC5/PC6 (CLK/CMD dell'eMMC) vanno messi direttamente sui via, senza stub.
13. **PCB**: placement 50 x 70 mm fatto (2026-10-16), senza piste. Dettagli ed esito del DRC in [pcb-placement.md](pcb-placement.md).
