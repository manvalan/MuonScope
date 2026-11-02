# ProvaDDR: progetto per la prova di sbroglio DDR con BoardLab

Copia completa di `SchedaIMX6ULL-SD` (stesso schema, stesso placement 80 x 100 mm, 229 componenti), **senza piste**. Rigenerabile con `../generatori/gen_prova_ddr.py`. ERC 0, DRC 0, parità schema/PCB 0.

Aprire `ProvaDDR.kicad_pro`.

## Stackup

Fonte: [PCBWay, Multi-layer laminated structure](https://www.pcbway.com/multi-layer-laminated-structure.html), 4 strati, voce 1 (1.6 mm, rame residuo interno 70%). Consultata il 2026-11-02.

| Strato | Materiale | Spessore (mm) | Er |
|---|---|---|---|
| L1 F.Cu | 0.5 oz placcato a 1 oz | 0.035 | |
| PP | 7628 RC46% | 0.1855 | 4.74 |
| L2 In1.Cu | GND, 1 oz | 0.035 | |
| Core | FR4 | 1.03 | 4.6 |
| L3 In2.Cu | alimentazioni, 1 oz | 0.035 | |
| PP | 7628 RC46% | 0.1855 | 4.74 |
| L4 B.Cu | 0.5 oz placcato a 1 oz | 0.035 | |

Finito 1.61 mm +-10%. **La richiesta era 0.5 oz interni, ma la tabella PCBWay non ha una voce 4 strati 1.6 mm con 1 oz esterni e 0.5 oz interni**: ho usato 1 oz interni. Spessore della maschera (0.01 mm) non dichiarato da PCBWay, indicativo.

## Regole

Piste 5 mil (0.127 mm), 4 mil (0.1016 mm) solo dentro i courtyard di U1 e U2, distanza 0.1 mm, via 0.45/0.2 mm. Regole in `ProvaDDR.kicad_dru`.

## Impedenze calcolate

Microstrip su F.Cu verso In1 (stesso risultato su B.Cu verso In2): h 0.1855 mm, Er 4.74, rame 35 um. Formule Hammerstad-Jensen e IPC-2141A da `vendor/impedancefinder/zsolver.py` di BoardLab, senza maschera. Da confermare col calcolo di PCBWay.

| Obiettivo | Larghezza | Note |
|---|---|---|
| 50 ohm singola | 0.316 mm | classe `DDR_SE_50R` |
| 40 ohm singola | 0.460 mm | non assegnata |
| 100 ohm differenziale | 0.178 mm, gap 0.127 mm | classe `DDR_DIFF_100R` |
| 80 ohm differenziale | 0.281 mm, gap 0.127 mm | non assegnata |
| Pista da 5 mil | 76.6 ohm | |
| Pista da 4 mil | 83.1 ohm | |

**Conseguenza:** su questo stackup una pista da 5 mil non è a 50 ohm, e 0.316 mm non passano nel corridoio tra le sfere: dentro le BGA servono colli da 4-5 mil, fuori le piste larghe occupano molto spazio. La classe può rendere lo sbroglio più difficile di quello a 5 mil: se BoardLab non chiude, va provato anche con piste strette.

Con un prepreg sottile (stackup personalizzato PCBWay), per esempio h 0.1 mm ed Er 4.1, la stima è 0.185 mm per 50 ohm e 61 ohm a 5 mil. Valori indicativi.

## Classi di rete

- `DDR_DIFF_100R`: CK, LDQS, UDQS (6 net).
- `DDR_SE_50R`: A, BA, DQ, DM e comandi (44 net).
- `DDR_VREF`, `DDR_ZQ`, `SOC_DDR_ZQ`: classe Default, non sono linee veloci.

Il parser `parse_kicad_pcb` di BoardLab legge il file; non ho lanciato lo sbroglio.
