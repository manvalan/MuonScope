# Scheda RK3568 (cartella SchedaH616)

Scheda Linux basata su **Rockchip RK3568** per il progetto MuonScope, sul **bus MIKILAB**. Nasce come SchedaH616: la cartella
mantiene il vecchio nome, il progetto KiCad è `progetto-kicad/SchedaRK3568.kicad_pro`.

- SoC **RK3568** (FCBGA636L 19x19 mm, passo 0.65, LCSC C2938930), PMIC **RK809-5** + **TCS4525** per VDD_CPU, come Rockchip RK3568 AIoT REF e Radxa ROCK 3A
- **DDR4 2 GB** x16 Samsung K4AAG165WA-BCWE (un chip, point-to-point, niente VTT, VPP 2.5 V da AP2112K-2.5)
- eMMC FORESEE FEMDNN064G-C9A61 (64 GB, HS400) su EMMC 8 bit a 1.8 V (AP2112K-1.8), microSD su SDMMC0
- Ethernet Gigabit RTL8211F su GMAC0 RGMII + HR911130C con EEPROM MAC 25AA02E48, Wi-Fi/BT AP6256 su SDMMC2 + UART8, GNSS NEO-M9N (PPS e time mark su GPIO)
- Alimentazione: 12 V dal BUS_POWER direttamente al buck TPS56637 (niente eFuse), jack 5 V, due TPS2121 in cascata (bus > jack > USB-C),
  USB-C con FUSB302B (anche porta OTG per il flash con rkdeveloptool), VCC3V3_SYS dal TPS563201; porta USB-C host con TPS2553
- Bus MIKILAB: BUS_POWER 30 pin su SPI3, MAIN 28 pin REV5.1 su SPI2 (HIT# sul pin 28), linee lente su GPIO diretti (niente espansore)
- Tasti RESET (rete RESETn della PMIC) e RECOVERY (SARADC_VIN0), console UART2 su J301

## Contenuto

| Percorso | Cosa |
|---|---|
| `progetto-kicad/` | Progetto KiCad 10 `SchedaRK3568.kicad_pro`, libreria simboli `Scheda.kicad_sym`, footprint `Scheda.pretty`, modelli 3D `Scheda.3dshapes` |
| `schema-rk3568.pdf` | Schema completo esportato |
| `pcb-placement-rk3568.pdf` / `.png` | Placement del PCB 70 x 90 mm, top e bottom |
| `generatori/` | Script Python che generano fogli, footprint del SoC e PCB; `build.sh` rifà lo schema (ERC, PDF, mappa dei pin), `build_pcb.sh` il PCB |
| `docs/scelte-progetto.md` | Fonti, rail, assegnazione GPIO, DDR4, incongruenze con le note, **punti aperti** |
| `docs/pinmap-rk3568.md` | Mappa RK3568 sfera per sfera con la net di ogni sfera |
| `docs/pcb-placement.md` | Scheda, regole, dove sta ogni componente, esito DRC |

Per rigenerare servono python3, KiCad 10 (Linux o macOS; i percorsi delle librerie standard sono in `generatori/kilib.py`) e la libreria
personale [MIKILAB](https://github.com/manvalan/mikilab-kicad-library) (variabile `MIKILAB`, o clonata in `~/Develop/mikilab-kicad-library`),
da cui vengono simboli e footprint dei componenti specifici; cosa resta nella libreria di progetto `Scheda` e perché è in `docs/scelte-progetto.md`:

```bash
sh SchedaH616/generatori/build.sh
sh SchedaH616/generatori/build_pcb.sh
```

## Fogli dello schema

1. Radice
2. **CPU**: RK3568 in 9 unità, 24 MHz, RESET/RECOVERY, UART2, disaccoppiamento, interfaccia bus (serie, pull-up, ESD)
3. **Bus MIKILAB**: J1 BUS_POWER 30 pin, J2 MAIN 28 pin
4. **Alimentazione**: TPS56637, jack con TPS2121 U108, USB-C con FUSB302B, TPS2121 U103, SY6280AAC
5. **PMIC**: RK809-5, TCS4525, TPS563201, AP2112K-1.8, AP2112K-2.5
6. **Memorie**: DDR4, eMMC, microSD
7. **Rete**: RTL8211F, HR911130C, 25AA02E48
8. **Radio**: AP6256 + U.FL
9. **GNSS**: NEO-M9N, PPS OUT e STROBE IN su SMA, CR1220 sul V_BCKP
10. **USB host**: TPS2553 + USB-C solo host

## Stato

- Schema completo, **ERC a 0 violazioni** (KiCad 10.0.7), nessuna net con un solo pin
- Ball map RK3568 dal pinout ufficiale Rockchip, verificata sul datasheet V1.2 (636/636); DDR4 confrontata con il reference Rockchip AIoT
- **PCB**: 70 x 90 mm, 6 strati, solo placement, tutto sul top tranne il disaccoppiamento sotto SoC e DDR4; dettagli ed esito del DRC in `docs/pcb-placement.md`

## Punti aperti principali

L'elenco completo è in `docs/scelte-progetto.md`.

- TPS563201 (3 A) al limite per VCC3V3_SYS, che ora alimenta anche i buck dell'RK809-5
- DDR4 a 16 bit sul canale A: da confermare con il template Rockchip a 16 bit e con il loader
- RGMII a 3.3 V (Rockchip consiglia 1.8 V), quarzo 24 MHz e induttore del TCS4525 da confermare
