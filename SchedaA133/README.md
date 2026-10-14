# SchedaA133

Scheda Linux basata su **Allwinner A133** per il progetto MuonScope (rivelatore di muoni, astrometria). Prende il posto della Mainboard Command ESP32 sul **bus MIKILAB**.

- SoC Allwinner A133 (LFBGA-346), PMIC **AXP717**, **LPDDR4 2 GB** (MT53E512M32D1ZW-046), eMMC 256 GB, microSD
- Ethernet Gigabit RTL8211F, Wi-Fi/BT AMPAK AP6256, GNSS timing u-blox NEO-F10T (PPS e time mark)
- Alimentazione: 12 V dal BUS_POWER (buck 6 A), jack 5 V, USB-C con FUSB302B; porta USB-C host 1 A
- Bus MIKILAB: BUS_POWER 30 pin e MAIN 28 pin (BPS-MIKILAB-2026-REV5.0)

## Contenuto

| Percorso | Cosa |
|---|---|
| `progetto-kicad/` | Progetto KiCad 10 `SchedaA133.kicad_pro`, libreria simboli `A133.kicad_sym`, footprint `A133.pretty` |
| `schema-a133.pdf` | Schema completo esportato |
| `generatori/` | Script Python che hanno generato i fogli (servono `kicad-cli` e le librerie standard di KiCad) |
| `docs-old/` | Documentazione delle versioni precedenti, superata |

## Fogli dello schema

1. Radice
2. **CPU**: A133 in 5 unità, clock 24 MHz e 32 kHz, reset/FEL, strap di boot, UART0, interfaccia bus (serie, pull-up, ESD)
3. **Bus MIKILAB**: J1 BUS_POWER 30 pin, J2 MAIN 28 pin
4. **Alimentazione**: TPS56637 12 → 5 V, LM74700, jack DC, USB-C con FUSB302B, TPS2121, SY6280AAC
5. **PMIC**: AXP717 secondo il reference Allwinner, LDO per microSD/eMMC, buck 3V3_PERI
6. **Memorie**: LPDDR4, eMMC, microSD
7. **Rete**: RTL8211F + RJ45 HR911130A
8. **Radio**: AP6256 + U.FL
9. **GNSS**: NEO-F10T, PPS bufferizzato, time mark, backup CR1220
10. **USB host**: USB-C solo host con TPS2553

## Stato

- Schema completo, **ERC a 0 violazioni** (KiCad 10)
- Footprint mancanti creati o importati nella libreria `A133.pretty`
- **Layout da iniziare**

## Punti aperti

- VREF_ENABLE è attivo alto (modulo Power rivisto il 2026-10-14): R324 è un pull-down da 10k, quindi a riposo i riferimenti sono spenti.
- Footprint A133 LFBGA-346 ricavato dalla ball map e dal passo del product brief: da confrontare con il disegno meccanico ufficiale.
- Pinout del NEO-F10T (formato NEO) e ball map di LPDDR4/eMMC da verificare sui datasheet.
- AXP717: variante senza suffisso (come il reference Allwinner e la TrimUI Smart Pro A133), oggi non a magazzino su LCSC.
- Valori da confermare: partitori e induttori dei buck, quarzi (carico), RSET del PHY, bias dell'antenna GNSS, rete π del Wi-Fi.
- SDIO del Wi-Fi a 3.3 V (SDIO 2.0): passare a 1.8 V richiede di spostare PPS e UART BT.
