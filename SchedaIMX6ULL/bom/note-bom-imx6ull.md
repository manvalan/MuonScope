# Scheda i.MX 6ULL: note BOM (2026-11-02)

Richieste di Michele: i.MX 6ULL, RAM 1 GB, eMMC 32 GB con ball >= 0.8 mm, Ethernet, USB, microSD, Wi-Fi.

## i.MX 6ULL contro i vincoli
| Punto | Esito |
|---|---|
| Passo BGA | MCIMX6Y2CVM08AB, MAPBGA-289 14x14 **passo 0.8 mm**: ok (il 9x9 è a 0.5 mm, da evitare) |
| RAM | bus DDR **16 bit**, DDR3L-800. 1 GB con un solo chip MT41K512M16HA (FBGA-96, 0.8 mm) |
| Ethernet | solo **10/100 RMII** (2 MAC), niente Gigabit: LAN8720A |
| USB | 2 USB 2.0 OTG con PHY interno: OTG1 = USB-C device/boot, OTG2 = hub -> USB-C host + Wi-Fi |
| Storage | solo **2 uSDHC**: uno per eMMC, uno per microSD. Il Wi-Fi SDIO non ha un controller libero, per questo va su USB |
| PMIC | non serve: LDO interni. Rail esterni 3.3 V, 1.35 V (DDR), 1.4 V (VDD_SOC_IN) con sequenza 3.3 -> 1.35 -> 1.4, POR_B dal supervisore |
| Timing | PPS e EXTINT in input capture del timer GPT1 (risoluzione ~15 ns a 66 MHz) |

## eMMC con ball >= 0.8 mm
Le eMMC comuni (153 ball, quelle su LCSC) sono a **0.5 mm**. Esiste il package JEDEC **100 ball 14x18 passo 1.0 mm**, solo da produttori industriali:
- **ISSI IS21TF32G-JQLI**, 32 GB, -40..85 C, LCSC C17563769 (in BOM; prezzo e stock da verificare, stimato ~30 EUR)
- Smart Modular BGAE240 SPQBGP1CWW0132GB, 32 GB, -40..105 C (fuori LCSC)
- altre 100 ball 1.0 mm: Swissbit, ISSI, Flexxon (da verificare capienze e prezzi)

Alternativa a pad grandi: **SD NAND** LGA-8 6x8 mm (interfaccia SD, piedini da QFN largo). Però arriva al massimo a **8 GB** (MK MKDV64GCL-STH, 64 Gbit): i "32G" su LCSC sono 32 Gbit = 4 GB. Per 32 GB non basta.

## Wi-Fi
LB-LINK BL-M8723DU1 (RTL8723DU, Wi-Fi 2.4 GHz + BT 4.2, USB, driver mainline rtw88_8723du) dietro un hub FE1.1s su USB_OTG2.

## Da verificare
Codici LCSC marcati "no" o "da verificare", prezzo e disponibilità dell'eMMC 100 ball, VDD_SOC_IN esatto dal datasheet, fanout DDR a 4 strati.

Michele 2026-11-02: filesystem tutto a bordo sulla eMMC; la microSD resta solo come lettore.

## Disponibilità eMMC 100 ball (2026-11-02)
DigiKey (dati di Michele): IS21TF32G-JQLI e -TR attive ma stock 0; IS22TF32G-JQLA1 obsoleta. LCSC: esaurite. Kingston/Micron/Samsung/Swissbit 32 GB sono 153 ball 0.5 mm.
Proposta: footprint JEDEC 100 ball 14x18 passo 1.0 mm (intercambiabile tra produttori), chiedere lead time ISSI ad Avnet/Arrow e preventivo Smart Modular; ripiego per prototipi IS21TF16G-JQLI (16 GB, stesso package).

## Scelta finale storage (Michele 2026-11-02): SSD su USB
Niente eMMC. Boot da SPI NOR W25Q128JVSIQ (SOIC-8, QSPI1); rootfs ext4 su SSD M.2 2242 SATA 64 GB, zoccolo M.2 key M a bordo, bridge JMS578 su una porta dell'hub FE1.1s (USB_OTG2). Buck 3.3 V dedicato all'SSD.
Conseguenza: uSDHC2 libero, quindi Wi-Fi su SDIO (BL-M8723DS1) invece che su USB. uSDHC1 resta alla microSD (solo lettore).
