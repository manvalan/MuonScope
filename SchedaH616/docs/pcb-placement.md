# SchedaH616: placement del PCB

Generato da `generatori/build_pcb.sh` (netlist dallo schema → `gen_pcb.py`, con il Python di KiCad 10). Solo placement, **nessuna pista**.
Immagini: `../pcb-placement-h616.pdf` (pagina 1 top, pagina 2 bottom vista da sotto) e `../pcb-placement-h616.png`.

## Scheda

- 50 x 70 mm, angoli smussati 3 mm. Quattro fori NPTH da 2.2 mm (MountingHole_2.2mm_M2) a 4 mm dai bordi, con keepout di raggio 3.2 mm su tutti gli strati rame (niente piste, via o rame).
- 6 strati, spessore 1.6 mm.
- Regole di progetto: piste minime 0.127 mm (5 mil, anche sugli interni), distanza 0.1 mm, via minime 0.25/0.15 mm (via-in-pad JLCPCB POFV sotto l'H616, regola in `SchedaH616.kicad_dru`), via di default 0.45/0.2 mm, distanza dal bordo 0.3 mm (0 per le SMA a bordo scheda).
- Classi di rete ereditate dalla A133 (Power_Heavy, V_Bias_36V, Analog_REF, Power_Logic): restano le larghezze delle piste, ma le distanze sono state abbassate (0.1-0.2 mm) per stare nei passi da 0.4-0.5 mm di connettori e QFN.
- I riferimenti sono sul livello Fab: a questa densità la serigrafia degli 0402 non ci sta.

## Dove sta cosa

| Zona | Lato | Componenti |
|---|---|---|
| Centro | top | H616 (U301), LPDDR4 subito sotto (U401) sul lato delle sfere DRAM (righe N-V) |
| Sotto le sfere H616 e LPDDR4 | bottom | Disaccoppiamento: 26/26 condensatori dell'H616 e 14/14 della LPDDR4 |
| Bordo alto | top / bottom | J1 BUS_POWER 30 pin (top) e J2 MAIN 28 pin (bottom), ingresso cavo sul bordo |
| In alto a sinistra | top | buck TPS56637 + L101 vicino al BUS_POWER; sul bottom i due TPS2121 (U103 e U108, vicini tra loro e al jack) e il FUSB302B |
| Bordo sinistro | top | USB-C di alimentazione J104, jack 5 V J103, AP6256 (U601) con U.FL J601 sul bordo |
| Tra jack e H616 | top | AXP313A (U201) con L201-L203 vicino alle sfere VDD |
| Sinistra, sotto l'AP6256 | bottom | eMMC (U402), vicina ai pin PC (lato sinistro dell'H616) |
| In alto a destra | top | NEO-M9N (U701), lontano dai buck dei 12 V e del 3V3 |
| Sotto il NEO | bottom | microSD (J401), apertura sul bordo destro |
| Bordo destro | top+bottom | SMA antenna GNSS J701 (dalla parte opposta dell'U.FL Wi-Fi), PPS OUT J702, STROBE IN J703 |
| Bordo basso | top | RJ45 J501 e USB-C host J801, aperture sul bordo |
| In basso a destra | top | header UART0 J301 vicino al bordo destro, header PPS/STROBE J704, pulsanti RESET e FEL |
| In basso al centro | bottom | PHY RTL8211F (U501), TCA6416A (U308), EEPROM MAC, CR1220 (BT701) |

I passivi sono messi in automatico vicino al componente con cui condividono più net. Prima si prova lo stesso lato entro 7 mm, poi entrambi i lati.

## Esito

- **DRC**: 0 violazioni. Restano 499 collegamenti non fatti (nessuna pista). Parità schema/PCB: 0 problemi.
- **Componenti**: piazzati tutti e 352 (122 top, 230 bottom). Nessun footprint mancante.
- **Libreria H616.pretty corretta**:
  - serigrafia tolta dove finiva sui pad (footprint EasyEDA e AP6256);
  - pioli di centraggio di RJ45 e portapila diventati NPTH.

## Da rivedere in layout

- La scheda è molto piena: 230 componenti stanno sul bottom, quindi il montaggio è su due lati.
- Il PHY RTL8211F è a circa 15 mm dall'RJ45: le coppie MDI vanno tenute corte e accoppiate, oppure si sposta il PHY.
- L'AXP313A e i buck sono a 5-10 mm dal NEO-M9N: serve un piano di massa continuo e il percorso RF corto verso J701.
- Lo stackup a 6 strati è quello di default di KiCad e va allineato a quello di JLCPCB.
