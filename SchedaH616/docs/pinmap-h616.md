# H616: mappa dei pin della SchedaH616

Generata da `generatori/gen_pinmap.py` a partire dalla netlist dello schema e dalla ball map del datasheet
Allwinner H616 V1.0 (tabella 4-2, controllata sfera per sfera sulla figura 7-1).

Unica differenza tra tabella e figura: **AC_VRA1** e' D17 nella tabella 4-2 e C17 nella figura 7-1. Lo schema usa C17,
confermato dal footprint EasyEDA C5365289 e dallo schema Orange Pi Zero2 (H616) v1.3.

## GPIO

| Pin | Sfera | Dominio | Net | Funzione |
|---|---|---|---|---|
| PC0 | B1 | VCC_PC 1.8 V | EMMC_DS | SMHC2 eMMC 8 bit |
| PC1 | C2 | VCC_PC 1.8 V | EMMC_RST | SMHC2 eMMC 8 bit |
| PC2 | C1 | VCC_PC 1.8 V | IOX_INT_N | INT del TCA6416A (open-drain, 1.8 V) |
| PC3 | D1 | VCC_PC 1.8 V | - | libero |
| PC4 | D2 | VCC_PC 1.8 V | - | libero |
| PC5 | D3 | VCC_PC 1.8 V | EMMC_CLK | SMHC2 eMMC 8 bit |
| PC6 | E2 | VCC_PC 1.8 V | EMMC_CMD | SMHC2 eMMC 8 bit |
| PC7 | F4 | VCC_PC 1.8 V | PD_INT_N | INT del FUSB302B (open-drain, 1.8 V) |
| PC8 | E3 | VCC_PC 1.8 V | EMMC_D3 | SMHC2 eMMC 8 bit |
| PC9 | F1 | VCC_PC 1.8 V | EMMC_D4 | SMHC2 eMMC 8 bit |
| PC10 | F2 | VCC_PC 1.8 V | EMMC_D0 | SMHC2 eMMC 8 bit |
| PC11 | F3 | VCC_PC 1.8 V | EMMC_D5 | SMHC2 eMMC 8 bit |
| PC12 | G2 | VCC_PC 1.8 V | USB1_OC_N | FAULT del TPS2553 (open-drain, 1.8 V) |
| PC13 | G3 | VCC_PC 1.8 V | EMMC_D1 | SMHC2 eMMC 8 bit |
| PC14 | H1 | VCC_PC 1.8 V | EMMC_D6 | SMHC2 eMMC 8 bit |
| PC15 | H2 | VCC_PC 1.8 V | EMMC_D2 | SMHC2 eMMC 8 bit |
| PC16 | H3 | VCC_PC 1.8 V | EMMC_D7 | SMHC2 eMMC 8 bit |
| PF0 | J2 | VCC_IO 3.3 V | SD_D1 | SMHC0 microSD |
| PF1 | J3 | VCC_IO 3.3 V | SD_D0 | SMHC0 microSD |
| PF2 | K1 | VCC_IO 3.3 V | SD_CLK | SMHC0 microSD |
| PF3 | K3 | VCC_IO 3.3 V | SD_CMD | SMHC0 microSD |
| PF4 | L2 | VCC_IO 3.3 V | SD_D3 | SMHC0 microSD |
| PF5 | L3 | VCC_IO 3.3 V | SD_D2 | SMHC0 microSD |
| PF6 | K2 | VCC_IO 3.3 V | SOC_PREFIX_2 | PREFIX del bus (100R serie) |
| PG0 | A6 | VCC_PG 3.3 V | WL_SDIO_CLK | SMHC1 SDIO AP6256 |
| PG1 | C7 | VCC_PG 3.3 V | WL_SDIO_CMD | SMHC1 SDIO AP6256 |
| PG2 | C6 | VCC_PG 3.3 V | WL_SDIO_D0 | SMHC1 SDIO AP6256 |
| PG3 | B5 | VCC_PG 3.3 V | WL_SDIO_D1 | SMHC1 SDIO AP6256 |
| PG4 | C5 | VCC_PG 3.3 V | WL_SDIO_D2 | SMHC1 SDIO AP6256 |
| PG5 | B7 | VCC_PG 3.3 V | WL_SDIO_D3 | SMHC1 SDIO AP6256 |
| PG6 | A4 | VCC_PG 3.3 V | BT_UART_TX | UART1 Bluetooth |
| PG7 | B4 | VCC_PG 3.3 V | BT_UART_RX | UART1 Bluetooth |
| PG8 | C4 | VCC_PG 3.3 V | BT_UART_RTS | UART1 Bluetooth |
| PG9 | B3 | VCC_PG 3.3 V | BT_UART_CTS | UART1 Bluetooth |
| PG10 | C8 | VCC_PG 3.3 V | WIFI_32K | X32KFOUT, LPO AP6256 |
| PG11 | B10 | VCC_PG 3.3 V | MAIN_SPI_ALERT_N | EINT, ALERT# del bus |
| PG12 | C9 | VCC_PG 3.3 V | MAIN_HIT_N | EINT, HIT# del bus (pin 28 MAIN) |
| PG13 | C10 | VCC_PG 3.3 V | GNSS_PPS | EINT, PPS del NEO-M9N |
| PG14 | B9 | VCC_PG 3.3 V | GNSS_EXTINT | EINT, time mark (solo ingresso) |
| PG15 | A8 | VCC_PG 3.3 V | GNSS_UART2_TX | UART2 GNSS |
| PG16 | B8 | VCC_PG 3.3 V | GNSS_UART2_RX | UART2 GNSS |
| PG17 | C3 | VCC_PG 3.3 V | SOC_ADDR_0 | ADDR del bus (100R serie) |
| PG18 | A2 | VCC_PG 3.3 V | SOC_ADDR_1 | ADDR del bus (100R serie) |
| PG19 | B2 | VCC_PG 3.3 V | SOC_ADDR_2 | ADDR del bus (100R serie) |
| PH0 | D16 | VCC_IO 3.3 V | UART0_TX | UART0 debug |
| PH1 | D15 | VCC_IO 3.3 V | UART0_RX | UART0 debug |
| PH2 | B15 | VCC_IO 3.3 V | MAIN_I2C_SCL | TWI2 bus MIKILAB |
| PH3 | C15 | VCC_IO 3.3 V | MAIN_I2C_SDA | TWI2 bus MIKILAB |
| PH4 | A14 | VCC_IO 3.3 V | PWR_SPI_INA239B_CS | chip select GPIO (cs-gpios) |
| PH5 | B14 | VCC_IO 3.3 V | MAIN_SPI_CS_MASTER | SPI1_CS0 / CS_MASTER |
| PH6 | C14 | VCC_IO 3.3 V | SPI1_CLK | SPI1 condiviso BUS_POWER/MAIN + EEPROM |
| PH7 | B12 | VCC_IO 3.3 V | SPI1_MOSI | SPI1 condiviso BUS_POWER/MAIN + EEPROM |
| PH8 | C13 | VCC_IO 3.3 V | SPI1_MISO | SPI1 condiviso BUS_POWER/MAIN + EEPROM |
| PH9 | A12 | VCC_IO 3.3 V | PWR_SPI_INA239A_CS | chip select GPIO (cs-gpios) |
| PH10 | B13 | VCC_IO 3.3 V | PWR_SPI_DAC_CS | chip select GPIO (cs-gpios) |
| PI0 | H6 | VCC_PI 3.3 V | RGMII_RXD3 | EMAC0 RGMII |
| PI1 | D4 | VCC_PI 3.3 V | RGMII_RXD2 | EMAC0 RGMII |
| PI2 | G6 | VCC_PI 3.3 V | RGMII_RXD1 | EMAC0 RGMII |
| PI3 | E4 | VCC_PI 3.3 V | RGMII_RXD0 | EMAC0 RGMII |
| PI4 | G5 | VCC_PI 3.3 V | RGMII_RXCK | EMAC0 RGMII |
| PI5 | H4 | VCC_PI 3.3 V | RGMII_RXCTL | EMAC0 RGMII |
| PI6 | H5 | VCC_PI 3.3 V | SOC_PREFIX_0 | PREFIX del bus (100R serie) |
| PI7 | G4 | VCC_PI 3.3 V | RGMII_TXD3 | EMAC0 RGMII |
| PI8 | E6 | VCC_PI 3.3 V | RGMII_TXD2 | EMAC0 RGMII |
| PI9 | D5 | VCC_PI 3.3 V | RGMII_TXD1 | EMAC0 RGMII |
| PI10 | L5 | VCC_PI 3.3 V | RGMII_TXD0 | EMAC0 RGMII |
| PI11 | K4 | VCC_PI 3.3 V | RGMII_TXCK | EMAC0 RGMII |
| PI12 | K5 | VCC_PI 3.3 V | RGMII_TXCTL | EMAC0 RGMII |
| PI13 | E5 | VCC_PI 3.3 V | RGMII_CLKIN | EMAC0 RGMII |
| PI14 | L6 | VCC_PI 3.3 V | PHY_MDC | MDIO |
| PI15 | L4 | VCC_PI 3.3 V | PHY_MDIO | MDIO |
| PI16 | K6 | VCC_PI 3.3 V | SOC_PREFIX_1 | PREFIX del bus (100R serie) |
| PL0 | C18 | VCC_PLL 1.8 V | PMU-SCK | S_TWI0: AXP313A, FUSB302B, TCA6416A |
| PL1 | B18 | VCC_PLL 1.8 V | PMU-SDA | S_TWI0: AXP313A, FUSB302B, TCA6416A |

## Altre sfere (non GPIO)

| Sfera | Nome | Net |
|---|---|---|
| A1 | GND | GND_D |
| A10 | GND | GND_D |
| A16 | RESET | SOC_RESET |
| A18 | GND | GND_D |
| A19 | EPHY_TXP | NC |
| A20 | EPHY_TXN | NC |
| A21 | GND | GND_D |
| B6 | GND | GND_D |
| B11 | DXIN | DCXO_XIN |
| B16 | GND | GND_D |
| B17 | FEL | SOC_FEL |
| B19 | EPHY_RTX | NC |
| B20 | EPHY_RXP | NC |
| B21 | EPHY_RXN | NC |
| C11 | REFCLK_OUT | NC |
| C12 | DXOUT | DCXO_XOUT |
| C16 | JTAG_SEL | NC |
| C17 | AC_VRA1 | SOC_AC_VRA1 |
| C19 | HTX2P | NC |
| C20 | HTX2N | NC |
| D7 | VCC_PG | VCC-IO |
| D10 | VCC_IO | VCC-IO |
| D11 | VCC_DCXO | VCC-1V8 |
| D12 | VCC_PLL | VCC-1V8 |
| D13 | DXLDO_OUT | SOC_DXLDO |
| D14 | PLLTEST | NC |
| D18 | AC_AVCC | VCC-1V8 |
| D19 | GND | GND_D |
| D20 | HTX1P | NC |
| D21 | HTX1N | NC |
| E18 | VCC_EPHY | VCC-IO |
| E19 | HTX0P | NC |
| E20 | HTX0N | NC |
| F5 | VCC_PC | VCC-1V8-EMMC |
| F8 | VDD_GPUFB | VDD-SYSFB |
| F9 | VDD_GPU | VDD-SYS |
| F10 | VDD_GPU | VDD-SYS |
| F11 | VDD_SYS | VDD-SYS |
| F12 | VDD_SYS | VDD-SYS |
| F13 | VDD_SYS | VDD-SYS |
| F14 | GND | GND_D |
| F15 | GND | GND_D |
| F18 | VCC_HDMI | VCC-1V8 |
| F19 | HSCL | NC |
| F20 | HTXCP | NC |
| F21 | HTXCN | NC |
| G8 | VDD_GPU | VDD-SYS |
| G9 | VDD_GPU | VDD-SYS |
| G10 | VDD_SYS | VDD-SYS |
| G11 | VDD_SYS | VDD-SYS |
| G12 | VDD_SYS | VDD-SYS |
| G13 | GND | GND_D |
| G14 | GND | GND_D |
| G15 | GND | GND_D |
| G17 | HCEC | NC |
| G18 | HHPD | NC |
| G19 | LINEOUTL | NC |
| G20 | LINEOUTR | NC |
| G21 | HSDA | NC |
| H8 | VDD_CPU | VDD-CPU |
| H9 | VDD_CPU | VDD-CPU |
| H10 | GND | GND_D |
| H11 | GND | GND_D |
| H12 | GND | GND_D |
| H13 | GND | GND_D |
| H14 | GND | GND_D |
| H15 | GND | GND_D |
| H17 | AVCC | VCC-1V8 |
| H18 | AGND | SOC_AGND |
| H19 | GND | GND_D |
| H20 | VCC_TV | VCC-1V8 |
| J6 | VCC_PI | VCC-IO |
| J8 | VDD_CPU | VDD-CPU |
| J9 | VDD_CPU | VDD-CPU |
| J10 | VDD_CPU | VDD-CPU |
| J11 | VDD_CPU | VDD-CPU |
| J12 | GND | GND_D |
| J13 | GND | GND_D |
| J14 | GND | GND_D |
| J15 | GND | GND_D |
| J17 | VRA2 | SOC_VRA2 |
| J18 | VRA1 | SOC_VRA1 |
| J19 | USB0_DM | USB0_DM |
| J20 | USB0_DP | USB0_DP |
| J21 | TV_OUT | NC |
| K8 | GND | GND_D |
| K9 | GND | GND_D |
| K10 | GND | GND_D |
| K11 | GND | GND_D |
| K12 | GND | GND_D |
| K13 | GND | GND_D |
| K14 | GND | GND_D |
| K15 | GND | GND_D |
| K18 | REXT | SOC_REXT |
| K19 | USB2_DM | NC |
| K20 | USB2_DP | NC |
| L8 | VDD_CPUFB | VDD-CPUFB |
| L9 | VCC_DRAM | VCC-DRAM |
| L10 | VCC_DRAM | VCC-DRAM |
| L11 | VCC_DRAM | VCC-DRAM |
| L12 | VCC_DRAM | VCC-DRAM |
| L13 | VCC_DRAM | VCC-DRAM |
| L14 | VDD18_DRAM | VCC-1V8 |
| L15 | SZQ | SOC_SZQ |
| L18 | LRADC | NC |
| L19 | USB3_DM | NC |
| L20 | USB3_DP | NC |
| L21 | GND | GND_D |
| M1 | GND | GND_D |
| M2 | GND | GND_D |
| M3 | GND | GND_D |
| M18 | VCC_USB | VCC-IO |
| M19 | USB1_DM | USB1_DM |
| M20 | USB1_DP | USB1_DP |
| N2 | SDQ2 | DRAM_DQ2 |
| N3 | SDQ0 | DRAM_DQ0 |
| N4 | SDQ13 | DRAM_DQ13 |
| N5 | SDQ15 | DRAM_DQ15 |
| N6 | GND | GND_D |
| N7 | SDQ26 | DRAM_DQ26 |
| N9 | GND | GND_D |
| N10 | SDQM3 | DRAM_DQM3 |
| N12 | GND | GND_D |
| N13 | SA15 | NC |
| N15 | GND | GND_D |
| N16 | SA9 | NC |
| N18 | GND | GND_D |
| N19 | SA7 | NC |
| N20 | SODT1 | NC |
| N21 | SBA0 | NC |
| P1 | SDQ5 | DRAM_DQ5 |
| P2 | SDQ7 | DRAM_DQ7 |
| P3 | GND | GND_D |
| P4 | SDQ10 | DRAM_DQ10 |
| P5 | SDQ8 | DRAM_DQ8 |
| P6 | SDQ14 | DRAM_DQ14 |
| P7 | SDQ25 | DRAM_DQ25 |
| P9 | SDQ27 | DRAM_DQ27 |
| P10 | SDQ28 | DRAM_DQ28 |
| P12 | SDQ30 | DRAM_DQ30 |
| P13 | SCKE1 | DRAM_CKE1 |
| P15 | SA5 | DRAM_A5 |
| P16 | SA13 | NC |
| P18 | SACT | NC |
| P20 | SBG0 | NC |
| P21 | SBG1 | NC |
| R1 | SDQS0N | DRAM_DQS0N |
| R2 | SDQS0P | DRAM_DQS0P |
| R3 | SDQM1 | DRAM_DQM1 |
| R4 | SDQ11 | DRAM_DQ11 |
| R5 | GND | GND_D |
| R6 | SDQ12 | DRAM_DQ12 |
| R9 | SDQ24 | DRAM_DQ24 |
| R12 | SDQ31 | DRAM_DQ31 |
| R15 | SBA1 | NC |
| R18 | SA4 | DRAM_A4 |
| R19 | SA10 | NC |
| R20 | SCS1 | DRAM_CS1 |
| R21 | GND | GND_D |
| T1 | GND | GND_D |
| T2 | SDQ6 | DRAM_DQ6 |
| T3 | GND | GND_D |
| T4 | SDQ3 | DRAM_DQ3 |
| T5 | SDQ23 | DRAM_DQ23 |
| T6 | SDQ20 | DRAM_DQ20 |
| T7 | SDQ22 | DRAM_DQ22 |
| T8 | GND | GND_D |
| T9 | SDQM2 | DRAM_DQM2 |
| T10 | GND | GND_D |
| T11 | SDQ16 | DRAM_DQ16 |
| T12 | SDQ18 | DRAM_DQ18 |
| T14 | SCKP | DRAM_CKP |
| T15 | GND | GND_D |
| T16 | SA3 | DRAM_A3 |
| T17 | GND | GND_D |
| T18 | SA2 | DRAM_A2 |
| T20 | SODT0 | NC |
| T21 | SA0 | DRAM_A0 |
| U1 | SDQM0 | DRAM_DQM0 |
| U2 | SDQS1P | DRAM_DQS1P |
| U3 | SDQ4 | DRAM_DQ4 |
| U4 | SDQ1 | DRAM_DQ1 |
| U5 | SDQ21 | DRAM_DQ21 |
| U6 | GND | GND_D |
| U8 | SDQS2N | DRAM_DQS2N |
| U9 | SDQ19 | DRAM_DQ19 |
| U10 | SDQS3N | DRAM_DQS3N |
| U11 | SDQ29 | DRAM_DQ29 |
| U12 | SDQ17 | DRAM_DQ17 |
| U13 | GND | GND_D |
| U14 | SCKN | DRAM_CKN |
| U15 | SA11 | NC |
| U16 | SA12 | NC |
| U17 | SA1 | DRAM_A1 |
| U18 | SA16 | NC |
| U19 | SA8 | NC |
| U20 | SA6 | NC |
| U21 | SRST | DRAM_RST |
| V1 | GND | GND_D |
| V2 | SDQS1N | DRAM_DQS1N |
| V3 | SDQ9 | DRAM_DQ9 |
| V5 | GND | GND_D |
| V8 | SDQS2P | DRAM_DQS2P |
| V10 | SDQS3P | DRAM_DQS3P |
| V12 | GND | GND_D |
| V15 | SCKE0 | DRAM_CKE0 |
| V17 | SCS0 | DRAM_CS0 |
| V19 | GND | GND_D |
| V20 | SA14 | NC |
| V21 | GND | GND_D |
