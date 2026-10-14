# AP6256: simbolo e footprint partendo dall'AP6212

Data 2026-10-13. L'AP6256 non ha simbolo/footprint su EasyEDA né su UltraLibrarian. Appartiene alla stessa famiglia AMPAK 12x12 mm a 47 piazzole dell'AP6212, che invece è su LCSC/EasyEDA (**C2798300**) con simbolo e footprint.

## Procedura in EasyEDA

1. Libreria: cerca **C2798300** (AP6212) e importa simbolo e footprint.
2. Footprint: usalo così com'è (stesso corpo 12 x 12 mm, stesse 47 piazzole). Confronta comunque il disegno con il §6 del datasheet AP6256 prima del layout.
3. Simbolo: duplicalo, rinominalo AP6256 e cambia solo i nomi dei pin della tabella sotto. I numeri dei pin restano uguali.

## Confronto pin per pin (datasheet AP6212 §8.2 e AP6256 §5.2)

| Pin | AP6212 | AP6256 | Cosa cambia |
|---|---|---|---|
| 1, 3, 20, 31, 33, 36 | GND | GND | – |
| 2 | WL_BT_ANT | WL_BT_ANT | – |
| 4 | FM_RX | NC | Lasciare scollegato (non a massa) |
| 5, 8, 30, 32, 35 | NC | NC | – |
| 6 | BT_WAKE | BT_WAKE | – |
| 7 | BT_HOST_WAKE | BT_HOST_WAKE | – |
| 9 | VBAT | VBAT | 3.3 V, picco 1 A |
| 10, 11 | XTAL_IN, XTAL_OUT | XTAL_IN, XTAL_OUT | – (verificare sullo schema di riferimento AMPAK se vanno lasciati scollegati) |
| 12 | WL_REG_ON | WL_REG_ON | – |
| 13 | WL_HOST_WAKE | WL_HOST_WAKE | – |
| 14-19 | SDIO D2, D3, CMD, CLK, D0, D1 | uguali | – |
| 21 | VIN_LDO_OUT | VIN_LDO_OUT | – |
| 22 | VDDIO | VDDIO | – |
| 23 | VIN_LDO | VIN_LDO | – |
| 24 | LPO | LPO | 32.768 kHz |
| 25-28 | PCM_OUT, PCM_CLK, PCM_IN, PCM_SYNC | uguali | – |
| **29** | NC | **SDIO_VSEL** | **Collegare**: 1 (a VDDIO) con VDDIO 1.8 V, 0 (a GND) con VDDIO 3.3 V |
| **34** | BT_RST_N | **BT_REG_ON** | Stessa funzione, solo nome |
| **37** | NC | **GPIO_6** | Lasciare scollegato |
| **38** | NC | **GPIO_3** | Lasciare scollegato |
| **39** | GPIO2 | **GPIO_5** | Lasciare scollegato |
| **40** | GPIO1 | **GPIO_2** | Lasciare scollegato |
| 41-44 | UART_RTS_N, TXD, RXD, CTS_N | uguali | – |
| 45-47 | TP1, TP2, TP3 | TP1, TP2, TP3 (NC) | Piazzole di test, non collegare |

Unica modifica elettrica rispetto a un AP6212: il **pin 29 SDIO_VSEL** va collegato. Con VDDIO a 1.8 V (consigliato per SDIO 3.0) va a VDDIO.

## Footprint (dal datasheet AP6212 §9.2)

- Corpo 12 x 12 mm, passo piazzole 0.9 mm.
- Piazzola del modulo 0.65 x 0.95 mm; piazzola consigliata sul PCB 0.65-0.75 x 1.33 mm.
- Stencil 0.12-0.15 mm.
