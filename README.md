# orza
Inverse Astro (Ortsa -> Orza) logical Horoscope. Given characteristics, it sorts out the date of birth
# Sistema Astrologico Inverso

Genera una **data di nascita astrologicamente coerente** a partire dalla descrizione del carattere di un personaggio, dalla sua età e dall'anno di riferimento.

## Come funziona

```
descrizione testuale  →  segno solare   (keyword matching)
segno solare + età    →  data di nascita compatibile
ora di nascita        →  ascendente     (tavola semplificata a slot da 2h)
età                   →  fase di vita   (Giovinezza / Maturità / Senescenza)
```

## Struttura del progetto

```
├── app.py            # Interfaccia Streamlit
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

## Esempio di output

```
Nome:            Marco Rossi
Età:             35 anni
Data di nascita: 24/12/1991 alle 17:36
Segno Solare:    Capricorno
Ascendente:      Gemelli
Fase di vita:    Maturità → Seconda Casa
```

## Note

- Il **segno solare** è deterministico: la stessa descrizione produce sempre lo stesso segno.
- La **data** e l'**ora** di nascita sono casuali *dentro* la finestra compatibile col segno.
- L'**ascendente** è calcolato con una tavola semplificata (±1 segno di precisione).
- Per ambienti storici o fantastici, modifica l'**anno di riferimento** liberamente.
