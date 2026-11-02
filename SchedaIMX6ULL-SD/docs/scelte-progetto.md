# Scheda i.MX 6ULL con sola microSD: scelte di progetto

Fonti, assegnazione dei pad e punti comuni sono in `../SchedaIMX6ULL/docs/scelte-progetto.md`, che resta valido salvo quanto segue.

## Differenze dalla versione SSD

| | Modifica |
|---|---|
| Tolti | J13 M.2, SSD1, foro H5, U38 JMS578, Y5, L7, U39, L5, U36 FE1.1s, Y4 e i loro passivi |
| USB | USB_OTG2 diretto sulla USB-C 2 host, via U10 ESD. Unica porta host |
| Aggiunto | U40 W25N04KVZEIR su QSPI SS1 (NAND_DATA07, ALT2) |
| PREFIX_0 | Da NAND_DATA07 a CSI_DATA03 (GPIO4_IO24), per liberare SS1 |
| Liberi | GPIO1_IO04, ex reset dell'hub |

## Scelta della memoria (Michele, 2026-11-02)

NOR 16 MB per il boot + SPI NAND 512 MB per il rootfs UBIFS. Il ROM del 6ULL non avvia da SPI NAND (risposte NXP), quindi servono due chip.

## Punti da verificare

1. **Driver SPI NAND**: NXP dichiara che il suo BSP non supporta SPI NAND su i.MX6. Serve il driver mainline `spi-fsl-qspi`. In U-Boot esiste una scheda i.MX6UL con SPI NAND (Kontron SL-MX6UL), ma non è stata provata questa combinazione.
2. **Datasheet W25N04KV non letto**: pinout dal datasheet della famiglia W25N04LW (versione 1.8 V, stesso WSON 8x6) e tensione 2.7-3.6 V dal listino LCSC C5342170. **Attenzione al codice: W25N04KW e W25N04LW sono a 1.8 V** e qui si romperebbero.
3. **Footprint U40**: `WSON-8-1EP_8x6mm_P1.27mm_EP3.4x4.3mm` di KiCad, pad centrale a GND (ammesso dal datasheet). Quote del pad centrale da confrontare col disegno Winbond.
4. **Boot QSPI con BOOT_CFG tutti bassi**: dedotto dalla EVK, come nella versione SSD.
5. **UBIFS**: la NAND va gestita in Linux con MTD e UBI (blocchi difettosi); serve flash della NAND da U-Boot o Linux, il download seriale del ROM scrive solo in RAM.
6. **Altri punti comuni**: DDR3L obsoleta presso un distributore, decoupling da confrontare con la Tabella 9 NXP, pull-up interni nel device tree, compensazione dei buck.
