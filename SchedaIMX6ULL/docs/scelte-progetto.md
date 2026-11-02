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
- **Passivi 0603 come minimo**: 47 uF e 10 uF/25 V in 1206, 22 uF e 10 uF in 0805.
- **Scheda 120 x 143**, vedi `pcb-placement.md`. BOM non modificata: va aggiornata con queste voci.

## Sfoltimento dei passivi (2026-11-02): da 272 a 210

| Tolti | Pezzi | Conseguenza |
|---|---|---|
| Pull-up CMD/DAT di microSD e Wi-Fi | 10 | **Pull-up interni del 6ULL da impostare nel device tree**. CD conservato |
| Bulk dei buck: 14 x 22 uF in 2 x 47 uF (U22), 1 x 47 uF (U17, U23, U39), 1 x 22 uF (U26, U27) | 7 | TLV62569: 10-47 uF ammessi dal datasheet |
| 33R su MOSI/MISO, 100R su ADDR/PREFIX | 10 | Solo i clock SPI hanno la serie |
| Pull-up CS e FAULT del bus | 5 | **Pull-up interni da device tree; CS non definiti durante il boot** |
| 0R SPI_ID, ponte GND_A, schermo RJ45, condensatori BUS_3V3/BUS_5V | 7 | SPI_ID e schermo a GND diretti; GND_A solo passante tra J11 e J12 |
| DNP BUCK_MODE e BOOT_MODE | 3 | Forzare il download seriale richiede un filo; il ROM ci va da solo con QSPI vuota |
| Disaccoppiamento: VDD_SOC_IN, VDD_HIGH_IN/NVCC, NVCC_DRAM, VDD_SNVS_IN, DDR3L | 10 | Vedi punto 10 |
| Altri condensatori doppi (JMS578, M.2, hub, PHY, Wi-Fi, ingressi U17 e U23) | 10 | |

Conservati: partitori di feedback, 49.9R Ethernet, carico dei quarzi, CC USB-C, ZQ e VREF DDR, rete pi del Wi-Fi, DNP di BOOT_CFG1[4] e [6] (lo strap QSPI non è confermato, punto 2).


## Punti da verificare

1. **MT41K512M16HA-107:A risulta obsoleta** presso un distributore: controllare disponibilità o Alliance/Samsung K4B8G1646D.
2. **Boot QSPI con BOOT_CFG tutti bassi**: dedotto da SW601 tutto OFF sulla EVK (fonti NXP community). La fuse map non è stata consultata.
3. **Sequenza**: il datasheet vuole VDD_SNVS_IN prima di ogni altro rail. Senza pila, VDD_SNVS segue il 3V3 attraverso il diodo, quasi insieme a VDD_HIGH_IN. Spegnimento non sequenziato: alla caduta di 5V_SYS i rail calano da soli.
4. **Sequenza a RC** 3.3 -> 1.35 -> 1.4 V: tempi calcolati, da misurare. Il TPS3839 sorveglia solo il 3.3 V.
5. **JMS578 senza reference**: VCCO da AV33O, VREG_IN a 5 V, nessuna NVRAM SPI e temperatura ambiente 0-70 C (il SoC è -40..105 C). Da provare sul prototipo.
6. **Y5, J13**: parte da scegliere; footprint J13 TE 2199119-4, Y5 3225 generico.
7. **CR1220-2**: nel footprint di libreria non c'è il segno di polarità; assunto pad 1 = +. **Verificare sul disegno Seiko**.
8. **Bulk dei buck**: i valori di compensazione del TPS56637 sono per 4 x 22 uF nominali, ora 2 x 47 uF; controllare stabilità e range di uscita ammesso per TPS56637 e TPS563201 sui rispettivi datasheet.
9. **Carichi dei quarzi** (18 pF, 12 pF, 15 pF) stimati, CL da confermare per ogni parte.
10. **Hardware Development Guide NXP non trovata** (link NXP 404, forum bloccato): il disaccoppiamento non è confrontato con la sua Tabella 9. Un tecnico NXP avverte che cambiare quei valori può compromettere suspend/resume, quindi i rail `_CAP` restano ai valori della scheda aperta e i tagli sono su VDD_SOC_IN, NVCC e DDR3L. **Da confrontare con la Tabella 9**, come il CK DDR da 100R.
11. **ESD microSD**: U25 copre solo DAT0-3.
12. **LED di J1**: polarità da verificare; se invertita, solo i LED non si accendono.
