# Fogli Rete, Radio e GNSS

PDF: ~/Development/SchedaA133/schema-a133.pdf (9 pagine). Pagina 7 Rete (5xx), pagina 8 Radio (6xx), pagina 9 GNSS (7xx). Net verso la CPU come etichette globali. Il blocco CPU sul foglio radice ora ha 49 porte (rail e bus).

## Rete: RTL8211F-CG
- Strap da 4.7k:
  - PHYAD 001, PLLOFF 0;
  - TXDLY = RXDLY = 1 (rgmii-id);
  - CFG_EXT 1, CFG_LDO 00: pad RGMII a 3.3 V da 3V3_PERI.
- Quarzo 25 MHz ±50 ppm con 2x15 pF. In alternativa, DNP, il clock da PH13.
- REG_OUT → 2.2 µH → AVDD10/DVDD10, con 22 µF + 4x0.1 µF. RSET 2.49k 1%.
- 22 Ω su TXC, TXD0-3 e TXCTL. MDIO 1.5k, INT 4.7k, PHYRSTB 10k + 100 nF.
- Reset PH11, INT PH12, MDC/MDIO PH9/PH10.
- RJ45 Pulse JK0654219NL con magnetici e 2 LED attivi alti da 510 Ω.

## Radio: AP6256
- SDIO su PG0-5 con pull-up 10k a VCC-PG.
- UART1 BT con RTS/CTS su PG6-9.
- WL_REG_ON su PL4 e BT_REG_ON su PL5, entrambi con 100k a GND. Wake su PG11-13. LPO da WIFI_32K.
- Alimentazione: VBAT da 3V3_PERI, VDDIO da VCC-PG, SDIO_VSEL a GND (3.3 V).
- U.FL con rete π da tarare. PCM non collegato.

## GNSS: NEO-M9N (era NEO-F10T fino al 2026-10-16)
- UART3 su PD14/PD15. TIMEPULSE → 33 Ω → PG10 (EINT).
- VCC da 3V3_PERI. V_BCKP con supercap 0.2 F + BAT54 + 1k.
- Antenna attiva su SMA: VCC_RF → 10 Ω → 27 nH, con 10 nF ed ESD5V3U1U.
- PPS bufferizzato con 74LVC1G17 verso la SMA "PPS OUT" e l'header J704 (PPS, STROBE, GND).
- Time mark: SMA "STROBE IN" → ESD9B5.0 → 100 Ω / 100k → 74LVC1G17 (tollerante 5 V) → EXTINT.
- SAFEBOOT_N e RESET_N su test point.

## Altro
- R423 da 0R tra VCC-DRAM e VCC-DRAM-FB sul foglio Memorie, per il sense FB3 del PMIC.

## Da verificare
- Pinout NEO-M9N-00B dal data sheet UBX-19014285 R08 (tabella 9), uguale al simbolo NEO-M9N di KiCad. Rispetto al NEO-F10T (data sheet UBX-22022576) cambiano solo pin che sul F10T erano riservati: D_SEL (2) aperto = UART, USB_DM/DP (5/6) liberi, V_USB (7) a GND, LNA_EN (14) libero, SDA/SCL (18/19) liberi. Tutti gli altri collegamenti sono invariati.
- RSET e condensatori del quarzo del PHY: da prendere dalla Layout Guide Realtek.
- Bias dell'antenna GNSS e TVS RF: da controllare con l'Integration Manual u-blox.
- Rete π Wi-Fi: si tara dopo il layout.
- Footprint da creare: A133 BGA, AXP717, AP6256, supercap CPH3225A.

## Dubbi
1. SDIO a 3.3 V: l'AP6256 lavora in SDIO 2.0, fino a 50 MHz, quindi il Wi-Fi rende meno. Passare a 1.8 V vorrebbe dire:
   - BLDO1 a 1.8 V e SDIO_VSEL alto;
   - PPS e UART BT anche loro a 1.8 V, con il PPS da spostare su un altro banco.
   Per ora resta a 3.3 V.
2. Ritardi RGMII nel PHY tramite strap. Se si preferisce il device tree, bastano due resistenze da spostare.
3. USB1 del SoC ancora senza destinazione.
