# SchedaH616

Scheda Linux basata su **Allwinner H616** per il progetto MuonScope. Prende il posto della SchedaA133 (archiviata in `../SchedaA133`) sul **bus MIKILAB**.

- SoC H616 (TFBGA-284, 0.65 mm), PMIC **AXP313A** come su Orange Pi Zero3
- **LPDDR4 2 GB** x32 MT53E512M32D1ZW (1 chip, niente VTT), scelta definitiva
- eMMC FORESEE FEMDNN064G-C9A61 (64 GB, eMMC 5.1 HS400, LCSC C49284704) su SMHC2 (8 bit, 1.8 V), microSD su SMHC0
- Ethernet Gigabit RTL8211F + HR911130C con EEPROM MAC 25AA02E48, Wi-Fi/BT AP6256 su SMHC1 + UART1, GNSS NEO-M9N (PPS e time mark su EINT)
- Alimentazione: 12 V dal BUS_POWER direttamente nel buck TPS56637 (senza eFuse), jack 5 V, due TPS2121 in cascata (bus > jack > USB-C), USB-C con FUSB302B, 3V3_PERI dal TPS563201, LDO 1.8 V dedicato a eMMC e banco PC; porta USB-C host con TPS2553
- Bus MIKILAB: BUS_POWER 30 pin e MAIN 28 pin REV5.1 (HIT# sul pin 28), SPI1 condiviso tra i due connettori
- Espansore I/O TCA6416A per le linee lente: l'H616 non ha abbastanza GPIO

## Contenuto

| Percorso | Cosa |
|---|---|
| `progetto-kicad/` | Progetto KiCad 10 `SchedaH616.kicad_pro`, libreria simboli `H616.kicad_sym`, footprint `H616.pretty`, modelli 3D `H616.3dshapes` |
| `schema-h616.pdf` | Schema completo esportato |
| `pcb-placement-h616.pdf` / `.png` | Placement del PCB 50 x 70 mm, top e bottom |
| `generatori/` | Script Python che generano i fogli; `build.sh` rifà tutto, esegue l'ERC ed esporta PDF e mappa dei pin |
| `docs/scelte-progetto.md` | Fonti, rail, assegnazione GPIO, mappa LPDDR4, **punti aperti** |
| `docs/pinmap-h616.md` | Mappa H616 sfera per sfera con la net di ogni sfera |
| `docs/pcb-placement.md` | Scheda, regole, dove sta ogni componente, esito DRC |

Per rigenerare (servono python3 e KiCad 10 in `/Applications/KiCad`):

```bash
sh SchedaH616/generatori/build.sh
sh SchedaH616/generatori/build_pcb.sh
```

## Fogli dello schema

1. Radice
2. **CPU**: H616 in 5 unità, 24 MHz, RESET/FEL, UART0, SPI1 e interfaccia bus (serie, pull-up, ESD), TCA6416A
3. **Bus MIKILAB**: J1 BUS_POWER 30 pin, J2 MAIN 28 pin
4. **Alimentazione**: TPS56637, jack con TPS2121 U108, USB-C con FUSB302B, TPS2121 U103, SY6280AAC
5. **PMIC**: AXP313A, TPS563201 3V3_PERI, AP2112K-1.8 VCC-1V8-EMMC
6. **Memorie**: LPDDR4, eMMC, microSD
7. **Rete**: RTL8211F, HR911130C, 25AA02E48
8. **Radio**: AP6256 + U.FL
9. **GNSS**: NEO-M9N, PPS OUT e STROBE IN su SMA, CR1220 sul V_BCKP
10. **USB host**: TPS2553 + USB-C solo host

## Stato

- Schema completo, **ERC a 0 violazioni** (KiCad 10), nessuna net con un solo pin
- Ball map H616 presa **solo** dal datasheet ufficiale (tabella 4-2, controllata sulla figura 7-1)
- **PCB**: 50 x 70 mm, 6 strati, solo placement (352 componenti, 122 top e 230 bottom), DRC a 0 violazioni (restano solo i collegamenti da sbrogliare)

## Punti aperti principali

L'elenco completo è in `docs/scelte-progetto.md`.

- **DRAM**: scelta la LPDDR4 come la Orange Pi Zero3 (U-Boot mainline non supporta la DDR4 sull'H616).
- Mappa CA/CS della LPDDR4 e AXP313A verificati sullo schema Orange Pi Zero3. Restano: bilancio di ALDO1, strap BOOT_SEL con l'eMMC, LPO dell'AP6256 da X32KFOUT.
- Ingresso 12 V senza protezioni (eFuse tolto): niente limite di corrente, OVP né blocco inverso, e non c'è TVS sui 12 V.
