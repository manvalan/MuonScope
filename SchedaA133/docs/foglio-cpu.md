# Foglio CPU (cpu.kicad_sch, serie 3xx, formato A1)

PDF: ~/Development/SchedaA133/schema-a133.pdf, pagina 2 (Mac di Michele).

## Scelte
- U301 A133: 346 ball prese dal reference Allwinner A100_A133_B3 (pagine 06-08), divise in 5 unità: DRAM / PB-PC-PD / PE-PF-PG-PH-PL / sistema-USB-analogica / alimentazioni-GND.
- Rail:
  - VCC_PD e VCC_USB vanno a VCC-IO (3.3 V).
  - VCC_PC, LVDS, EFUSE, MCSI e CPVIN vanno a VCC-PC (1.8 V).
  - AVCC e VDD18_DRAM vanno a VCC-PLL.
  - VDD_USB va a VDD-SYS.
  - FB1 e FB2 arrivano da VDD_CPUFB e VDD_SYSFB.
- Disaccoppiamento come nel reference:
  - VDD-CPU e VDD-SYS: 10 µF + 2x2.2 µF ciascuna.
  - 0.1 µF su ogni banco.
  - AVCC 2.2 µF, VRA1/2 470 nF, CPVIN 10 µF.
  - ZQ 240R 1%.
- Clock: 24 MHz E3SB24 con 18 pF e 0R su XOUT; 32.768 kHz con 22 pF e 10M.
- Reset e boot:
  - RESET = PWROK, con 1 nF e tasto.
  - Tasto FEL a GND con pull-up 10k.
  - Strap GPADC0 10k/3.9k: boot da SMHC0 (microSD) e poi eMMC.
  - DDR PARA DNP.
- UART0 su PB9/PB10, header a 3 pin.
- Bus (rev. 4):
  - SPI2: PB1-PB3, CS su PB4-PB6, VREF_ENABLE PB7, VBIAS_ENABLE PB8, FAULT PD1.
  - SPI1: PD10-PD13.
  - ADDR PD16-18 e PREFIX PD19-21, con 100 Ω serie.
  - I2C0 PD22/PD23, ALERT# PD0.
  - 33 Ω su CLK e MOSI di entrambe le SPI.
- Stati di riposo, a VCC-IO salvo dove indicato:
  - CS 10k su.
  - VREF_ENABLE 10k su (riferimento spento).
  - VBIAS_ENABLE 100k verso GND (bias spento).
  - ALERT# 4.7k (unico pull-up del bus).
  - FAULT 10k.
  - I2C0 2.2k.
- ESD: 6 TPD4E05U06DQA (0.5 pF) sulle 22 linee logiche di J1/J2. Nessuna protezione su V_BIAS e sui riferimenti.
- Porte verso i fogli futuri:
  - DRAM_*
  - EMMC (PC)
  - SD (PF, SD_DET su PF6)
  - Wi-Fi/BT (PG0-9, PG11-13, PL4/PL5, WIFI_32K)
  - RGMII su PH: MDC/MDIO PH9/10, reset/INT PH11/12, 25 MHz PH13
  - GNSS: UART3 PD14/15, PPS su PG10 (EINT)
  - USB1
- FUSB302B:
  - S_TWI1 su PL8/PL9 con 2.2k a VCC-PL.
  - INT su PL10, VBUS_SRC_EN su PL11.
  - ST del TPS2121 su PL6.
- PMU RSB su PL0/PL1.
- ERC: segnala solo le porte verso fogli non ancora disegnati e i PWR_FLAG mancanti.

## Da verificare
- Ball map presa dal PDF del reference: va confrontata con il datasheet A133 prima del layout.
- Footprint LFBGA-346 12x12 P0.5: da creare. Ora c'è un segnaposto.
- Carico dei quarzi: da adattare ai quarzi acquistati.
- Dominio del pin FEL: il pull-up 10k ora è su VCC-IO.

## Dubbi
1. PH17 è "DDR PARA-SEL" nel BSP Allwinner, qui è usato come RGMII_TXD3. U-Boot mainline non lo usa.
2. VCC-PD su CLDO3 insieme a VCC-IO: banco PD a 3.3 V, come serve al bus.
3. FUSB302B su I2C separata da quella del bus, così il controller USB-C non va sulla piattina.
4. Il blocco CPU sul foglio radice ha 180 porte: si accorcia quando arrivano i fogli DRAM, eMMC e rete.
