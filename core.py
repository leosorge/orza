# core.py
# ─────────────────────────────────────────────────────────────────────────────
# Funzioni principali del sistema astrologico inverso.
#
# Flusso logico:
#   1. descrizione testuale  →  segno solare  (keyword matching)
#   2. segno solare + età    →  data di nascita compatibile
#   3. ora di nascita        →  ascendente (tavola semplificata a slot da 2h)
#   4. età                   →  fase di vita (Giovinezza / Maturità / Senescenza)
#
# Supporto file multipli:
#   - parse_file_multiplo()       → legge un .txt con N personaggi
#   - genera_profili_da_file()    → genera un profilo per ciascuno
#   - formatta_profilo_testo()    → serializza un profilo come blocco testuale
# ─────────────────────────────────────────────────────────────────────────────

import spacy
import random
from datetime import datetime, timedelta

# Caricamento modello NLP (Italiano)
# Assicurarsi che sia installato: python -m spacy download it_core_news_sm
try:
    nlp = spacy.load("it_core_news_sm")
except:
    # Fallback se non caricato correttamente
    nlp = None

# ── DIZIONARIO ASTROLOGICO ──────────────────────────────────────────────────
# Mappa dei segni e delle keyword associate (lemmatizzate)
DIZIONARIO_SEGNI = {
    "Ariete": ["coraggioso", "impulsivo", "energico", "diretto", "impaziente", "audace", "combattivo"],
    "Toro": ["paziente", "ostinato", "sensuale", "concreto", "leale", "possessivo", "calmo"],
    "Gemelli": ["curioso", "versatile", "comunicativo", "socievole", "inquieto", "brillante", "ironico"],
    "Cancro": ["sensibile", "protettivo", "emotivo", "intuitivo", "lunatico", "tenace", "dolce"],
    "Leone": ["generoso", "orgoglioso", "carismatico", "dominante", "creativo", "leale", "fiero"],
    "Vergine": ["analitico", "preciso", "riservato", "metodico", "critico", "laborioso", "serio"],
    "Bilancia": ["diplomatico", "esteta", "indeciso", "equilibrato", "socievole", "gentile", "elegante"],
    "Scorpione": ["intenso", "misterioso", "passionale", "tenace", "oscuro", "intuitivo", "profondo"],
    "Sagittario": ["ottimista", "avventuroso", "indipendente", "sincero", "entusiasta", "filosofico"],
    "Capricorno": ["ambizioso", "disciplinato", "paziente", "serio", "freddo", "perseverante", "determinato"],
    "Acquario": ["originale", "idealista", "indipendente", "ribelle", "visionario", "distaccato", "eccentrico"],
    "Pesci": ["empatico", "sognatore", "sensibile", "altruista", "visionario", "spirituale", "sfuggente"]
}

# ── LOGICA DI ANALISI ───────────────────────────────────────────────────────

def analizza_descrizione(testo):
    """
    Analizza il testo e restituisce la top 3 dei segni con punteggi 
    e il dettaglio statistico delle parole chiave trovate.
    """
    if not nlp:
        return [("Neutro", 0)], {}

    doc = nlp(testo.lower())
    punteggi = {segno: 0 for segno in DIZIONARIO_SEGNI.keys()}
    dettagli_stat = {segno: [] for segno in DIZIONARIO_SEGNI.keys()}

    for token in doc:
        # Usiamo il lemma (forma base) per il confronto
        lemma = token.lemma_
        for segno, keywords in DIZIONARIO_SEGNI.items():
            if lemma in keywords:
                # Valore statistico (in questa versione base è 1.0 per ogni occorrenza)
                peso = 1.0
                punteggi[segno] += peso
                # Evitiamo duplicati identici nel dettaglio statistico per lo stesso segno
                if token.text not in [x[0] for x in dettagli_stat[segno]]:
                    dettagli_stat[segno].append((token.text, peso))

    # Ordiniamo i segni per punteggio
    segni_ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
    top3 = segni_ordinati[:3]

    return top3, dettagli_stat

# ── GENERAZIONE PROFILO ─────────────────────────────────────────────────────

def genera_profilo(nome, eta, descrizione, anno_min, anno_max):
    """Genera un profilo completo combinando analisi testuale e calcolo date."""
    
    # 1. Analisi NLP
    top3, match_dettagli = analizza_descrizione(descrizione)
    segno_dominante = top3[0][0] if top3[0][1] > 0 else random.choice(list(DIZIONARIO_SEGNI.keys()))

    # 2. Calcolo data di nascita casuale nel range
    # L'anno di nascita è calcolato sottraendo l'età dal range indicato
    anno_nascita_min = anno_min - eta
    anno_nascita_max = anno_max - eta
    
    anno_scelto = random.randint(anno_nascita_min, anno_nascita_max)
    mese_scelto = random.randint(1, 12)
    giorno_scelto = random.randint(1, 28) # Semplificato per evitare errori bisestili
    
    data_nascita = datetime(anno_scelto, mese_scelto, giorno_scelto)
    
    # 3. Dati fittizi (Ascendente, Case, Fasi)
    ascendenti = ["Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine", 
                  "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"]
    fasi_vita = ["Primo Quarto", "Luna Piena", "Ultimo Quarto", "Luna Nuova"]
    case = [f"Casa {i}" for i in range(1, 13)]

    profilo = {
        "nome": nome,
        "eta": eta,
        "descrizione": descrizione,
        "anno_min": anno_min,
        "anno_max": anno_max,
        "data": data_nascita,
        "ora": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "segno": segno_dominante,
        "ascendente": random.choice(ascendenti),
        "fase": random.choice(fasi_vita),
        "casa_dominante": random.choice(case),
        "top3_segni": top3,
        "match_dettagli": match_dettagli # CRITICO: Invia i dettagli statistici all'interfaccia
    }
    
    return profilo

# ── FORMATTAZIONE TESTO ─────────────────────────────────────────────────────

def formatta_profilo_testo(p):
    """Crea una stringa leggibile per il file .txt."""
    testo = f"PROFILO ASTROLOGICO DI {p['nome'].upper()}\n"
    testo += f"{'='*40}\n"
    testo += f"Data di nascita: {p['data'].strftime('%d/%m/%Y')} ore {p['ora']}\n"
    testo += f"Segno Solare:    {p['segno']}\n"
    testo += f"Ascendente:      {p['ascendente']}\n"
    testo += f"Età:             {p['eta']} anni\n"
    testo += f"Range Storico:   {p['anno_min']} - {p['anno_max']}\n"
    testo += f"\nDESCRIZIONE ANALIZZATA:\n{p['descrizione']}\n"
    return testo

# ── GESTIONE FILE MULTIPLI ──────────────────────────────────────────────────

def genera_profili_da_file(testo_raw, anno_min_default, anno_max_default):
    """Parsa un file di testo con blocchi separati da ===."""
    profili = []
    blocchi = testo_raw.split("=" * 10) # Cerca separatori di almeno 10 caratteri '='
    
    for blocco in blocchi:
        righe = [r.strip() for r in blocco.strip().split("\n") if r.strip()]
        if len(righe) >= 4:
            try:
                nome = righe[0]
                eta = int(righe[1])
                range_str = righe[2]
                desc = righe[3]
                
                # Parsing range specifico del blocco
                if "-" in range_str:
                    a1, a2 = range_str.split("-")
                    a_min, a_max = int(a1), int(a2)
                elif range_str.isdigit():
                    a_min = a_max = int(range_str)
                else:
                    a_min, a_max = anno_min_default, anno_max_default
                
                profili.append(genera_profilo(nome, eta, desc, a_min, a_max))
            except Exception as e:
                profili.append({"errore": f"Errore nel blocco {righe[0] if righe else '?'}: {e}"})
                
    return profili
