# Foglio Memorie (memorie.kicad_sch, serie 4xx)

PDF: ~/Development/SchedaA133/schema-a133.pdf, pagina 6. Il blocco CPU sul foglio radice è sceso da 180 a 86 porte. Le net DRAM_*, EMMC_* e SD_* sono etichette globali.

## Scelte
- U401 LPDDR4 MT53E512M32D1ZW-046 IT:B, BGA-200 10x14.5 mm. Collegamenti presi dal reference Allwinner A100_A133, pagina 08 (LPDDR4_FBGA200):
  - Indirizzi: CA0-5 ← SA5, SA0, SA2, SA1, SCS0, SCS1.
  - Chip select: CS0 ← SA4, CS1 ← SA3.
  - Byte scambiati come nel reference. DQ0_A-7_A ← SDQ14, 10, 15, 8, 9, 13, 12, 11, con DQS0_A = SDQS1. Il canale B prende SDQ16-31.
  - Pin DRAM del SoC non usati (SA6-16, SBA, SBG, SACT, SODT): NC.
  - Alimentazioni: VDD1 da VDD18-LPDDR, VDD2/VDDQ da VCC-DRAM.
  - ODT_CA 100k a VDD2, ZQ 240R 1%.
  - Disaccoppiamento: 4x1 µF + 6x0.1 µF su VDD2/VDDQ, 2x1 µF + 2x0.1 µF su VDD1.
- U402 eMMC Kingston EMMC256-IY29-5B101, FBGA-153 con pinout JEDEC:
  - VCC da VCC-CARD, VCCQ da VCC-PC 1.8 V (HS200), VDDI 1 µF.
  - 33 Ω su CLK, pull-up 10k a VCCQ su CMD, DAT e RST_n.
- J401 microSD Hirose DM3AT:
  - Alimentazione da VCC-CARD, 33 Ω su CLK.
  - Pull-up 47k su CMD e DAT0-3. SD_DET su PF6 con 10k.
  - ESD: 2 TPD4E05U06.

## Da verificare
- Ball map LPDDR4 contro il datasheet Micron. CS1 e CKE1 vanno su ball NC del chip a singolo rank.
- Pinout eMMC contro il datasheet Kingston, ball per ball.
- Disaccoppiamento LPDDR4: da rifinire con la PDN Micron e lo stack-up.
- Pull-up microSD 47k e CLK 33 Ω: da adattare alla lunghezza delle piste.

## Dubbi
1. Il layout deve rispettare esattamente lo scambio dei byte: DQS e DM vanno nel byte giusto.
2. microSD solo a 3.3 V (banco PF su VCC-IO): niente UHS a 1.8 V.
3. Nessuna resistenza sul DS dell'eMMC: serve solo in HS400, in HS200 il DS non si usa.
