# Foglio PMIC (pmic.kicad_sch, serie 2xx)

PDF: ~/Development/SchedaA133/schema-a133.pdf, pagina 5 (Mac di Michele).

## Nota sul PMIC
Il datasheet dell'AXP707 non è più reperibile da LCSC né da JLCPCB. Il reference Allwinner
"A100_A133_B3_AXP707_LPDDR3" (2021), a pagina 05, disegna in realtà un AXP717
(QFN-52 6x6) anche se il titolo dice AXP707. Il foglio è disegnato con l'AXP717, con i pin
presi dal reference e verificati sul datasheet dell'AXP717D. Mainline Linux e U-Boot hanno
il driver axp717. La BOM ha ancora l'AXP707 (C2913551). L'AXP717 non risulta a
magazzino su LCSC.

## Assegnazione delle rail (ingresso VBUS = 5V_SYS dal TPS2121)
| Uscita | Rail | Tensione | Note |
|---|---|---|---|
| DCDC1 | VDD-CPU | 0.9-1.18 V, 4 A | FB1 = VDD-CPUFB, sense remoto |
| DCDC2 | VDD-SYS, VDD-USB | 0.95 V | FB2 = VDD-SYSFB |
| DCDC3 | VCC-DRAM | 1.1 V | VDD2/VDDQ LPDDR4, FB preso vicino alla DRAM |
| ALDO2 | VCC-PE | 1.8 V | |
| ALDO3 | VCC-PL | 3.3 V | |
| ALDO4 | VCC-PLL | 1.8 V | AVCC, VCC-PLL, VDD18-DRAM |
| BLDO1 | VCC-PG | 3.3 V | VCCIO-WIFI |
| BLDO2 | VDD18-LPDDR | 1.8 V | VDD1 LPDDR4 |
| CLDO1 | VCC-PC | 1.8 V | VCCQ eMMC (HS200), VCC-EFUSE, CPVIN |
| CLDO3 | VCC-IO | 3.3 V | VCC-IO, VCC-USB, VCC-PD, VCC-3V3 |
| AP2112K-3.3 esterno | VCC-CARD | 3.3 V | microSD + VCC eMMC, al posto del TCS2155 |
| CPUSLDO | VDD-CPUS | 0.9 V | |
| VRTC | VCC-RTC | | |
| TPS563201 (U, R211/R212 33.2k/10k, L205 2.2 µH) | 3V3_PERI | 3.32 V, 3 A | AP6256, RTL8211F, GNSS; EN da DCDCEN via 0 Ω, R210 DNP per sempre acceso |

Non usati (solo condensatore): ALDO1, BLDO3, BLDO4, CLDO2, CLDO4. VPP non serve con la LPDDR4.

Controllo: RSB PMU-SCK/PMU-SDA, AP-NMI (IRQ, 10k a VCC-RTC), AP-RESET (PWROK, 10k a VCC-RTC),
tasto PWRON, pila CR1220 su BACKUP montata come DNP.

## Valori da verificare
- Induttori 1.0 µH (4 A su DCDC1, 3 A su DCDC2 e DCDC3) e 22 µF in uscita: presi dal reference.
- Tensioni di default all'accensione: sono in OTP, da controllare su un esemplare reale o da chiedere al fornitore.
- 3V3_PERI: 33.2k/10k e 2.2 µH da ricontrollare sul datasheet.
- AP2112K da 600 mA: verificare che basti per microSD ed eMMC insieme.

## Dubbi aperti
1. Senza batteria: BAT ha solo 4.7 µF + 100 nF, TS è chiuso su 10k, il caricatore va disabilitato in U-Boot. Il datasheet non dice come gestire BAT senza batteria.
2. CC1/CC2 dell'AXP717 sono liberi (il Type-C lo gestisce il FUSB302B). Bisogna verificare che l'AXP717 non limiti VBUS senza CC.
3. DCDCEN segue la sequenza di CLDO2. Se CLDO2 è spento di default, 3V3_PERI resta spenta finché Linux non la accende. In alternativa si monta R210.
4. Il pin 38 è CHGLED sull'AXP717 e FB4 sull'AXP717D: va scelta la variante esatta.

ERC: segnala solo i collegamenti verso il foglio CPU, che non c'è ancora.
