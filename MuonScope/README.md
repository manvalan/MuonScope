# MuonScope

Progetto KiCad 10 originale del rivelatore MuonScope (scheda di comando ESP32, modulo Power, rivelatore, rete di retroazione, emettitore di test), con le correzioni della revisione del 2026-10-14. Schema esportato in `MuonScope-schema.pdf`. La specifica del bus è in `docs/mikilab_bus_protocol.md` (BPS-MIKILAB-2026-REV5.0).

I fogli del rivelatore, della retroazione e dell'emettitore sono superati dal progetto `../PianoTest`. Qui contano soprattutto il modulo Power e la scheda di comando.

## Modulo Power (revisione 2026-10-14)

- **Boost LT8330:** collegamenti di SW, diodo e FBX corretti. Uscita fissa 36,1 V (R19 1M, R20 46,4k), L6 XFL4020-103MEC, condensatori da 100 V.
- **Uscita VHV_36V:** F2 100 mA/63 V, poi Q5 Si2309CDS (−60 V) comandato da VBIAS_ENABLE tramite Q6 BSS138, con D5 da 12 V sul gate, poi RC 10 Ω + 2×2,2 µF/100 V. R39 da 100k scarica l'uscita: a boost spento l'uscita va a 0 V.
- **Bus:** VHV_36V arriva ai pin V_BIAS_1/V_BIAS_2 attraverso R32/R33 10 Ω e C53/C54 100 nF C0G. Il pinout del connettore non cambia.
- **DAC61402, INA239 e contorno:** non montati (DNP), perché la regolazione del bias e la misura di corrente sono sul piano. SPI_DAC_CS, SPI_INA239A/B_CS e DAC61402_FAULT sul BUS_POWER restano non collegati.
- **VREF_ENABLE:** attivo alto. Pull-up a 5 V e comando con BSS138 (Q3), R31 100k: a riposo i riferimenti sono spenti.
- **Jack J1:** centro = +VIN. Aggiunti F1 PTC, Q4 P-MOS contro l'inversione di polarità e D4 SMAJ15A.
- **Net class:** V_Bias_36V per l'alta tensione. Regola di clearance per gli FPC a 0,5 mm in `MuonScope.kicad_dru`.

## Altre correzioni

- **Retroazione:** SI e SO dell'MCP23S17 corretti, MPN di C18.
- **Emettitore:** SDA e SCL dell'AD5245 corretti, SET dell'LTC6993 con reostato + 47k, R25 collegata al gate di Q1.
- **Rivelatore:** C1 da 100 V, secondo canale dell'OPA come inseguitore. Il simbolo dell'OPA4172 ha ancora il pinout del duale: è corretto solo nel PianoTest.
- **Comando:** pin 5V dell'ESP32 portato su +5V (prima era su 2V5_REF).

## Stato

- **ERC:** 93 violazioni. Sono soprattutto pin dell'ESP32 non usati e i segnali del modulo Power non esportati dal foglio di comando.
- **PCB:** layout precedente, non aggiornato con queste modifiche.
- **Footprint:** quelli `MIKILAB_*` vengono dalla libreria esterna MIKILAB (variabile `${MIKILAB}`), non inclusa nel repository.
