# Scheda i.MX 6ULL: scelte di progetto

## Fonti

| Componente | Fonte | Verifica |
|---|---|---|
| i.MX 6ULL | NXP IMX6ULLCEC Rev 1.2 (tabelle 90, 91, 78, 79; copia Farnell). I link diretti su nxp.com rispondevano 404 | 289/289 sfere uguali alla netlist di cebrax/iMX6ULL_tryout, a parte zeri iniziali e GPANIO/GPANAIO. **La parte è industriale (IEC): stessa tabella data per scontata, non controllata su IMX6ULLIEC** |
| ALT dei pad | linux `imx6ul-pinfunc.h`, `imx6ull-pinfunc.h` | |
| MT41K512M16HA | Simbolo KiCad MT41K256M16HA + A15 su M7 (JEDEC x16). Footprint KiCad Micron 9x14 | **Datasheet Micron 8 Gb non scaricato**: ball map non controllata sul documento della parte |
| JMS578 | JMicron Rev 1.01 | Pin dal datasheet. **QFN-48 6x6 passo 0.4**, non 7x7. Nessun reference pubblico |
| FE1.1s | Terminus Rev B12.4 e Rev 22 | SSOP-28 Rev B, simbolo di progetto (quello KiCad è la vecchia revisione) |
| BL-M8723DS1 | LB-LINK V1.0.1.3 | Footprint disegnato dal par. 6.2; quote del pad parzialmente dedotte dal disegno |
| HR911105A | Footprint KiCad, nomi dei pin dal simbolo EasyEDA C12074 | Polarità LED non verificata |
| Altri | Libreria MIKILAB e libreria KiCad; circuiti TPS56637, TPS2121, TPS563201 come scheda RK3568 | |

Footprint di progetto in `Scheda.pretty`: BL-M8723DS1, e copie corrette di SMA, quarzo 32.768 kHz e CR1220. La libreria MIKILAB non è stata modificata.

## Assegnazione dei pad

| Funzione | Pad |
|---|---|
| BUS_POWER ECSPI2 | UART4_TX SCLK, UART5_TX MOSI, UART5_RX MISO, UART4_RX SS0 (INA239A); CS INA239B su UART2_CTS, DAC su UART2_RTS con cs-gpios |
| MAIN ECSPI1 | CSI_DATA04 SCLK, 05 SS0 (CS_MASTER), 06 MOSI, 07 MISO |
| I2C bus (I2C2), EEPROM MAC (I2C1) | CSI_HSYNC/VSYNC; GPIO1_IO02/03 |
| ADDR, PREFIX, ALERT#, HIT# | NAND_DATA04-07, NAND_ALE, LCD_CLK, LCD_ENABLE, LCD_HSYNC |
| VREF_ENABLE, VBIAS_ENABLE, FAULT | LCD_VSYNC, LCD_RESET, ENET2_RX_EN |
| QSPI boot | NAND_WP_B, DQS, READY_B, CE0, CE1, CLE |
| uSDHC1 microSD, CD | SD1_*, UART1_RTS_B |
| uSDHC2 Wi-Fi | NAND_RE_B, WE_B, DATA00-03 |
| BT UART8 | ENET2_TX_DATA1, TX_EN, RX_ER; WL_DIS, BT_DIS su ENET2_RX_DATA0/1 |
| ENET1 RMII, MDIO | ENET1_*, GPIO1_IO06/07, PHY_RST GPIO1_IO01 |
| GNSS UART3; PPS, EXTINT | UART3_TX/RX; UART2_TX = GPT1_CAPTURE1, UART2_RX = GPT1_CAPTURE2 |
| Console UART1 | UART1_TX/RX |

## Differenze dalla BOM

- **Strap BOOT_CFG**: non ~20 resistenze. La tabella 78 dà pull-down interni da 100k, quindi tutti bassi senza componenti; solo BOOT_MODE e due pull-up DNP.
- **Aggiunti**: J14 U.FL con rete pi, L5 (buck SSD), L7 (JMS578), L6, FB1, TP1, TP2, H5. Y5 30 MHz, come da datasheet.
- **Bluetooth su UART8**: UART2 serve a GPT1 CAPTURE1/2.
- **Condensatori tutti 0603**, anche 22 uF/10 V e 10 uF/25 V al posto dei 0805/1206 delle altre schede.
- **Scheda 80 x 95**, vedi `pcb-placement.md`. BOM non modificata: va aggiornata con queste voci.

## Punti da verificare

1. **MT41K512M16HA-107:A risulta obsoleta** presso un distributore: controllare disponibilità o Alliance/Samsung K4B8G1646D.
2. **Boot QSPI con BOOT_CFG tutti bassi**: dedotto da SW601 tutto OFF sulla EVK (fonti NXP community). La fuse map non è stata consultata.
3. **Sequenza**: il datasheet vuole VDD_SNVS_IN prima di ogni altro rail. Senza pila, VDD_SNVS segue il 3V3 attraverso il diodo, quasi insieme a VDD_HIGH_IN. Spegnimento non sequenziato: alla caduta di 5V_SYS i rail calano da soli.
4. **Sequenza a RC** 3.3 -> 1.35 -> 1.4 V: tempi calcolati, da misurare. Il TPS3839 sorveglia solo il 3.3 V.
5. **JMS578 senza reference**: VCCO da AV33O, VREG_IN a 5 V, nessuna NVRAM SPI e temperatura ambiente 0-70 C (il SoC è -40..105 C). Da provare sul prototipo.
6. **Y5, J13**: parte da scegliere; footprint J13 TE 2199119-4, Y5 3225 generico.
7. **CR1220-2**: nel footprint di libreria non c'è il segno di polarità; assunto pad 1 = +. **Verificare sul disegno Seiko**.
8. **22 uF 0603 a 5 V** perde gran parte della capacità (DC bias): controllare le curve per il buck 5 V. Valori di compensazione TPS56637 calcolati per i 22 uF nominali.
9. **Carichi dei quarzi** (18 pF, 12 pF, 15 pF) stimati, CL da confermare per ogni parte.
10. **CK DDR 100R** differenziale: scelta da confermare in simulazione o con la Hardware Development Guide NXP, non scaricata. Capacità sui rail `_CAP` riprese dalla scheda aperta, non dalla Guide.
11. **ESD microSD**: U25 copre solo DAT0-3.
12. **LED di J1**: polarità da verificare; se invertita, solo i LED non si accendono.
