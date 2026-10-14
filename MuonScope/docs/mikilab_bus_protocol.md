# SPECIFICA TECNICA DEL SISTEMA: BUS MIKILAB™
**Protocollo di Comunicazione, Alimentazione e Indirizzamento Modulare in Cascata per Rivelatori di Particelle e Strumentazione Scientifica**

* **Documento ID:** BPS-MIKILAB-2026-REV5.0  
* **Stato della specifica:** Approvata / Definitiva  
* **Frequenza di Bus SPI Supportata:** Fino a 20 MHz  
* **Target Hardware:** ESP32 NodeMCU / Sistemi di Acquisizione Distribuiti  

---

## 1. REQUISITI HARDWARE DEL MODULO (CHECKLIST VELOCE)
Ogni nuova scheda (Rivelatore, Timing GPS, Scintillatore SiPM) inserita nel BUS MIKILAB™ deve soddisfare rigorosamente i seguenti requisiti minimi hardware per garantire la compatibilità elettrica e meccanica:

### 1.1 Connettività e Meccanica
* [ ] **Doppio Connettore:** Presenza obbligatoria di due connettori a 28 pin passo 0.5 mm sul retro della scheda: `J_IN` (Ingresso) e `J_OUT` (Uscita verso il modulo successivo).
* [ ] **Package Connettori:** Formato SMT Right-Angle, tipo *Bottom Contact* (es. **XUNPU FPC-05F-28PH20**).
* [ ] **Ancoraggio Meccanico:** Alette metalliche laterali strutturali del connettore saldate a piazzole ampie connesse direttamente al piano di massa digitale (DGND).
* [ ] **Spessore Piattine FFC:** Cavi flessibili standard con spessore terminale di contatto pari a **0.3 mm** (Tipo A - contatti sullo stesso lato).

### 1.2 Logica Digitale e Alimentazione
* [ ] **Tensione Logica:** Tutti i circuiti integrati digitali e di interfaccia del bus devono operare rigorosamente a **+3.3V**.
* [ ] **Disaccoppiamento:** Ogni circuito integrato deve disporre di un condensatore ceramico di bypass locale da **100 nF / 50V / X7R / formato 0603** posizionato a meno di 2 mm dal pin VCC/VDD.
* [ ] **Logica di Indirizzamento:** Ogni piano deve integrare sul Layer BOTTOM la tripletta standard ad alta velocità:
  * 1x Sommatore Binario a 4-bit **74HC283** (Package TSSOP-16 / SOIC-16).
  * 1x Comparatore d'Identità a 4-bit **74HC85** (Package TSSOP-16 / SOIC-16).
  * 1x Decodificatore da 3 a 8 linee **74HC138** (Package TSSOP-16 / SOIC-16).

### 1.3 Gestione Interrupt locali (All'indirizzo 07)
* [ ] **Interrupt Manager di Piano:** Ogni scheda che necessita di inviare segnali di allarme/trigger deve utilizzare un espansore I/O **MCP23S17** (Interfaccia SPI a 10MHz) configurato all'interno della matrice locale del piano.
* [ ] **Assegnazione Chip Select:** Il pin `CS` dell'MCP23S17 deve essere tassativamente pilotato dall'uscita **`Y7` (Indirizzo binario `111` / `07`)** del decodificatore locale 74HC138.
* [ ] **Configurazione Uscite Allarme:** I pin di interrupt del chip (`INTA`/`INTB`) devono essere configurati a livello software in modalità **Open-Drain** (Mai in Push-Pull) e collegati alla linea comune `SPI_ALERT#`.

### 1.4 Vincoli del Layer-up (PCB a 4 Strati)
* [ ] **Layer 1 (TOP):** Esclusivo per sensori e stadi analogici d'ingresso. Nessuna traccia digitale ad alta velocità.
* [ ] **Layer 2 (INNER 1):** Piano di Massa Analogica (**AGND**) continuo al 100%, privo di interruzioni.
* [ ] **Layer 3 (INNER 2):** Piano di Massa Digitale (**DGND**) continuo al 100%, accoppiato ai segnali logici.
* [ ] **Layer 4 (BOTTOM):** Esclusivo per i chip logici (74HC, ADC, MCP), componenti passivi di filtro e bus digitali.

---

## 2. PANORAMICA DEL SISTEMA
Il **BUS MIKILAB™** implementa un'architettura **Plug-and-Play asincrona tridimensionale**: ogni modulo interconnesso tramite il bus auto-determina la propria posizione fisica all'interno della catena grazie a un incremento matematico hardware riprodotto sui singoli PCB, consentendo la produzione di schede slave elettronicamente identiche al 100% e prive di jumper o resistenze di configurazione manuale.

---

## 3. ARCHITETTURA DI INDIRIZZAMENTO E LOGICA DI COMANDO

### 3.1 Il Meccanismo del Prefisso Telefonico
Il controllo dei chip SPI distribuiti sulle matrici dei vari piani avviene tramite il principio "Prefisso + Interno", centralizzato nel firmware del Master (ESP32):
* **Il Prefisso (Identità di Piano):** Gestito dalle linee `SPI_PREFIX_[0..2]`. Trasporta il codice del livello con cui il Master vuole comunicare (fino a 8 piani indipendenti).
* **L'Interno (Selezione del Chip locale):** Gestito dalle linee `SPI_ADDR_[0..2]`. Trasporta l'indirizzo binario del chip specifico da attivare all'interno del modulo selezionato (fino a 8 periferiche SPI locali, es. ADC, Espansori I/O).

### 3.2 Autoconfigurazione Hardwired (Incremento +1)
Ogni modulo integra un sommatore binario completo a 4 bit (**74HC283**) inserito a ponte tra il connettore di ingresso (`J_IN`) e quello di uscita (`J_OUT`). 
1. Il modulo acquisisce l'ID del piano corrente leggendo le tre linee dedicate `SPI_ID_[0..2]` provenienti dal connettore di ingresso `J_IN`.
2. Il chip **74HC283** addiziona matematicamente il valore fisso binario `0001` (ottenuto legando il bit `B1` a VCC e il riporto iniziale `C0` a GND).
3. Le uscite della somma ($\Sigma_1, \Sigma_2, \Sigma_3$) vengono instradate in isolamento elettrico **esclusivamente verso i pin 25, 26, 27 del connettore di uscita `J_OUT`**, interrompendo la continuità elettrica parallela con il connettore `J_IN` su quelle specifiche posizioni.
4. Il comparatore d'identità a 4 bit (**74HC85**) confronta in tempo reale l'ID del piano locale con il prefisso `SPI_PREFIX_[0..2]` inviato dal Master. Se i codici coincidono, sblocca l'abilitazione `E3` (Active-High) del decodificatore locale **74HC138**.

---

## 4. SISTEMA ALERT ED EVITAMENTO COLLISIONI (SPI_ALERT#)

La gestione delle richieste di attenzione provenienti dai sensori distribuiti (fronti di trigger o completamento di misura) è affidata alla linea **`SPI_ALERT#`** (Pin 24). Il sistema è strutturato per operare in totale sicurezza elettrica senza causare loop di blocco o cortocircuiti transitori:
* Sulla scheda madre Command (Master), la linea è mantenuta stabile a **3.3V** (*Stato di Idle*) da una singola resistenza di pull-up da **4.7 kΩ**.
* All'interno di ciascun piano, l'espansore GPIO a 16-bit **MCP23S17** (mappato all'indirizzo locale `Y7` / `07` del decodificatore 74HC138) raccoglie sui suoi ingressi locali le linee di interrupt dei comparatori o dei circuiti analogici di riga del piano.
* Quando un modulo richiede attenzione, "apre un canale interno" e scarica la linea globale direttamente a massa (`GND_D`), portandola a **0V**. Essendo collegamenti Open-Drain in parallelo, non si verifica alcuna collisione elettrica se più piani si attivano contemporaneamente.
* **Smaltimento della Coda:** Il Master esegue un polling sequenziale interrogando l'indirizzo `07` di ciascun piano. L'azione fisica della lettura del registro SPI resetta i flag interni dell'MCP23S17 del piano servito, il quale si stacca dalla massa. Se un altro modulo era in attesa nella Daisy Chain, la linea `SPI_ALERT#` rimane fissa a 0V e il Master passa istantaneamente a interrogare il livello successivo, gestendo la coda in modo rigoroso.

---

## 5. ASSEGNAZIONE PIEDINATURA (PINOUT) - CONNETTORE STANDARD FPC 28 PIN

| Pin | Nome Segnale | Direzione (Rispetto a IN) | Descrizione Tecnica e Livelli Elettrici |
| :--- | :--- | :--- | :--- |
| **1** | `GND` | - | Massa di schermatura principale ed equipotenziale di bordo |
| **2** | `5V` | Ingresso Potenza | Alimentazione stadi analogici di precisione (Amplificatori *OPA4172*) |
| **3** | `3V3` | Ingresso Potenza | Alimentazione stadi digitali interni (*74HC138, 74HC283, 74HC85*) |
| **4** | `GND` | - | Massa di isolamento della sezione di potenza |
| **5** | `2V5_REF` | Ingresso Analogico | Riferimento di tensione ultra-stabile per la calibrazione di fondo scala dell'ADC |
| **6** | `1V25_REF` | Ingresso Analogico | Tensione di banchina analogica (VCC/2) per il bias degli operazionali |
| **7** | `GND` | - | Massa analogica dedicata di precisione. Collegata direttamente al Layer 2 (AGND) |
| **8** | `V_BIAS_1` | Ingresso Bias | Alta tensione positiva (+24V) controllata per polarizzazione inversa dei fotodiodi |
| **9** | `V_BIAS_2` | Ingresso Bias | Seconda linea di ritorno / Riserva di sicurezza ad alta impedenza |
| **10** | `GND` | - | Massa di separazione per l'isolamento della sezione ad alta tensione |
| **11** | `SPI_SCLK` | Ingresso Digitale | Orologio di sincronizzazione del bus SPI (Fino a 20 MHz, linea condivisa) |
| **12** | `SPI_MOSI` | Ext. Out / Slv In | Master Output / Slave Input (Linea dati logica condivisa) |
| **13** | `SPI_MISO` | Slv Out / Ext In | Master Input / Slave Output (Linea dati logica in push-pull/tri-state) |
| **14** | `I2C_SDA` | Bidirezionale | Linea dati bus I2C (Predisposta per futura estensione timing modulo GPS) |
| **15** | `I2C_SCL` | Ingresso Digitale | Linea clock bus I2C (Predisposta per futura estensione timing modulo GPS) |
| **16** | `GND` | - | **MASSA DI ISOLAMENTO CENTRALE.** Agisce da schermo fisico nel nastro flessibile |
| **17** | `SPI_CS_MASTER`| Ingresso Digitale | Abilitazione temporale principale (Active-Low). Connessa ai pin E1/E2 del 74HC138 |
| **18** | `SPI_ADDR_0` | Ingresso Digitale | Bit 0 dell'indirizzo interno del chip (Va al pin A0 del 74HC138 locale) |
| **19** | `SPI_ADDR_1` | Ingresso Digitale | Bit 1 dell'indirizzo interno del chip (Va al pin A1 del 74HC138 locale) |
| **20** | `SPI_ADDR_2` | Ingresso Digitale | Bit 2 dell'indirizzo interno del chip (Va al pin A2 del 74HC138 locale) |
| **21** | `SPI_PREFIX_0`| Ingresso Digitale | Bit 0 del prefisso del piano chiamato dal Master (Va al comparatore 74HC85) |
| **22** | `SPI_PREFIX_1`| Ingresso Digitale | Bit 1 del prefisso del piano chiamato dal Master (Va al comparatore 74HC85) |
| **23** | `SPI_PREFIX_2`| Ingresso Digitale | Bit 2 del prefisso del piano chiamato dal Master (Va al comparatore 74HC85) |
| **24** | `SPI_ALERT#` | Uscita Open-Drain | Linea di richiesta attenzione globale (Active-Low). Interfaccia OR-Cablata |
| **25** | `SPI_ID_0` | Speciale IN/OUT | Bit 0 ID Piano: Ingressi XOR/Sommatore su `J_IN` → Interrotto → Uscita Somma su `J_OUT` |
| **26** | `SPI_ID_1` | Speciale IN/OUT | Bit 1 ID Piano: Ingressi XOR/Sommatore su `J_IN` → Interrotto → Uscita Somma su `J_OUT` |
| **27** | `SPI_ID_2` | Speciale IN/OUT | Bit 2 ID Piano: Ingressi XOR/Sommatore su `J_IN` → Interrotto → Uscita Somma su `J_OUT` |
| **28** | `GND` | - | Massa di chiusura finale. Schermatura del bordo esterno contro i disturbi RF |
