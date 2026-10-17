# BOM scheda Tibbo (2026-10-17)

## Il punto critico: Tibbo non ha un chip o modulo da 1 GB
L'unico chip Tibbo montabile su una scheda custom è il **Plus1 SP7021** (Sunplus/Tibbo), LQFP176-EP 20x20 mm:
- SP7021-IS: 128 MB DDR3 integrata
- SP7021-IF: 512 MB DDR3 integrata (quello in BOM)

Fonte: https://tibbo.com/store/plus1/specifications.html. Anche la LTPP3 Gen. 2 di Tibbo monta l'SP7021 con 512 MB (https://docs.tibbo.com/ltpp3g2).

Altri limiti rispetto alla scheda Octavo:
- **Ethernet solo 10/100** (MAC RMII, niente RGMII): il RTL8211F non si può usare, al suo posto LAN8720A.
- **eMMC 4.41 HS 52 MHz**: la FORESEE 64 GB funziona ma a circa 40-50 MB/s.
- Cortex-A7 32 bit a 1 GHz, sotto lo STM32MP157F dell'Octavo come ordine di grandezza (A7 dual 800 MHz) ma con 4 core.

Vantaggi: QFP (nessun fanout BGA, nessuna DDR da sbrogliare), alimentazione unica 3.3 V con DC-DC interni, niente PMIC. È la scheda più semplice di tutte quelle fatte finora.

## Alimentazione
VIN_SYS 12 V da BUS_POWER -> TPS56637 5 V -> TPS2121 (priorità bus, poi USB-C 1) -> TPS563201 3.3 V 3 A, unico rail. VBAT RTC dalla CR1220 con BAT54 in serie perché l'RTC dell'SP7021 prova a caricare la batteria.

## Periferiche riprese dalla scheda Octavo
2 USB-C (OTG/boot + host con TPS2553), eMMC FORESEE 64 GB, GNSS NEO-M9N con PPS e EXTINT su GPIO a interrupt + 3 SMA, BUS_POWER 30 pin, MAIN 28 pin, console UART.

## Da verificare
Codici LCSC marcati "da verificare", prezzo SP7021-IF (MEV Elektronik su richiesta), strap HW_CFG per il boot da eMMC (non descritti nel datasheet pubblico, servono gli schemi di riferimento Tibbo).
