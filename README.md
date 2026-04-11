# Sistema Astrologico Inverso

Genera una **data di nascita astrologicamente coerente** a partire dalla descrizione del carattere di un personaggio, dalla sua età e dal periodo storico in cui vive.

Utile per la costruzione di personaggi in narrativa, giochi di ruolo, ambientazioni storiche o fantastiche.

## Come funziona

```
descrizione testuale  →  segno solare   (keyword matching sui tratti caratteriali)
segno solare + età + range anni  →  data di nascita compatibile
ora di nascita        →  ascendente     (tavola semplificata a slot da 2h)
età                   →  fase di vita   (Giovinezza / Maturità / Senescenza)
```

## Struttura del progetto

```
├── app.py            # Interfaccia Streamlit (due tab: singolo e file multipli)
├── core.py           # Logica del sistema (funzioni principali)
├── database.py       # Database tratti zodiacali e finestre temporali
├── requirements.txt
└── README.md
```

## Avvio locale

```bash
pip install streamlit
streamlit run app.py
```

## Deploy su Streamlit Cloud

1. Fai il fork/push di questa cartella su GitHub
2. Vai su [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Seleziona il repo e imposta `app.py` come file principale
4. Clicca **Deploy**

> **Nota Python**: il progetto richiede Python ≥ 3.7. Il file `core.py` usa
> `from __future__ import annotations` per garantire compatibilità con
> Python 3.7–3.9 (versione usata da Streamlit Cloud).

---

## Esempio — personaggio singolo

**Input:**

| Campo | Valore |
|---|---|
| Nome | Elena Voss |
| Età | 34 |
| Range anni | 1880–1910 |
| Descrizione | `persona intensa, misteriosa, determinata e tenace, con un lato oscuro e passionale` |

**Output:**

```
PROFILO: ELENA VOSS
==================================================
Età:               34 anni
Range riferimento: 1880–1910
Data di nascita:   14/11/1861 alle 22:17
Segno Solare:      Scorpione
Ascendente:        Leone
Fase di vita:      Maturità → Seconda Casa
Match keyword:     Scorpione (4), Capricorno (1), Ariete (0)
```

---

## Esempio — file multipli

Per analizzare più personaggi in una volta, carica un file `.txt` nella **tab "File multipli"**.
Ogni blocco contiene 4 righe e i blocchi sono separati da `===`:

```
Elena Voss
34
1880-1910
"persona intensa, misteriosa, determinata e tenace, con un lato oscuro e passionale"
===========================
Luca Ferretti
22
1960-1975
"curioso, brillante, irrequieto, versatile, comunicativo e un po' superficiale"
===========================
Mara König
61
-
"sognante, empatica, spirituale, compassionevole, a tratti sfuggente e melancolica"
```

**Formato delle 4 righe:**
- **Riga 1** — nome del personaggio
- **Riga 2** — età (numero intero)
- **Riga 3** — range anni: `YYYY-YYYY` per un intervallo, `YYYY` per anno fisso, `-` per usare il range globale impostato nella UI
- **Riga 4+** — descrizione del carattere (le virgolette doppie sono opzionali)

---

## Note

- Il **segno solare** è deterministico: la stessa descrizione produce sempre lo stesso segno.
- La **data** e l'**ora** di nascita sono casuali *dentro* la finestra compatibile con segno, età e range.
- L'**ascendente** è calcolato con una tavola semplificata (±1 segno di precisione).
- Il **range anni** permette di collocare il personaggio in qualsiasi epoca storica o immaginaria.
- Per arricchire i risultati, aggiungi keyword a `database.py` senza toccare la struttura.
