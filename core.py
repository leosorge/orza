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
try:
    nlp = spacy.load("it_core_news_sm")
except:
    nlp = None

# ── DIZIONARIO ASTROLOGICO ──────────────────────────────────────────────────
# Mappa dei segni e delle keyword associate
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
    e il dettaglio delle parole chiave.
    """
    if not nlp:
        return [("Neutro", 0)], {}

    doc = nlp(testo.lower())
    punteggi = {segno: 0 for segno in DIZIONARIO_SEGNI.keys()}
    dettagli_stat = {segno: [] for segno in DIZIONARIO_SEGNI.keys()}

    for token in doc:
        testo_token = token.text.lower()
        lemma_token = token.lemma_.lower()
        
        for segno, keywords in DIZIONARIO_SEGNI.items():
            for kw in keywords:
                # Confronto elastico: controlla sia la parola esatta che il lemma
                if testo_token == kw or lemma_token == kw:
                    peso = 1.0
                    punteggi[segno] += peso
                    # Aggiunge ai dettagli se non già presente
                    if testo_token not in [x[0] for x in dettagli_stat[segno]]:
                        dettagli_stat[segno].append((testo_token, peso))
                    break # Passa al prossimo token se trovato match per questo segno

    # Ordina per punteggio e prendi i primi 3
    segni_ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
    top3 = segni_ordinati[:3]

    return top3, dettagli_stat

# ── GENERAZIONE PROFILO ─────────────────────────────────────────────────────

def genera_profilo(nome, eta, descrizione, anno_min, anno_max):
    """Genera un profilo completo."""
    top3, match_dettagli = analizza_descrizione(descrizione)
    
    # Se il primo segno ha punteggio 0, sceglie a caso per non lasciare vuoto
    if top3[0][1] > 0:
        segno_dominante = top3[0][0]
    else:
        segno_dominante = random.choice(list(DIZIONARIO_SEGNI.keys()))

    # Calcolo data nascita
    anno_nascita_min = anno_min - eta
    anno_nascita_max = anno_max - eta
    anno_scelto = random.randint(anno_nascita_min, anno_nascita_max)
    
    data_nascita = datetime(anno_scelto, random.randint(1,12), random.randint(1,28))
    
    # Liste fisse per dati casuali
    asc_list = ["Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine", "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"]
    fasi = ["Luna Piena", "Luna Nuova", "Primo Quarto", "Ultimo Quarto"]
    
    return {
        "nome": nome, "eta": eta, "descrizione": descrizione,
        "anno_min": anno_min, "anno_max": anno_max,
        "data": data_nascita, "ora": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "segno": segno_dominante, "ascendente": random.choice(asc_list),
        "fase": random.choice(fasi), "casa_dominante": f"Casa {random.randint(1,12)}",
        "top3_segni": top3, "match_dettagli": match_dettagli
    }

# ── FORMATTAZIONE E FILE ────────────────────────────────────────────────────

def formatta_profilo_testo(p):
    """Testo per download."""
    return (f"PROFILO DI {p['nome'].upper()}\n"
            f"Data: {p['data'].strftime('%d/%m/%Y')} | Segno: {p['segno']}\n"
            f"Descrizione: {p['descrizione']}\n")

def genera_profili_da_file(testo_raw, a_min_def, a_max_def):
    """Gestione multipla."""
    blocchi = testo_raw.split("===")
    risultati = []
    for b in blocchi:
        r = [line.strip() for line in b.strip().split("\n") if line.strip()]
        if len(r) >= 4:
            try:
                # Parsing anno/range
                if "-" in r[2]:
                    a1, a2 = map(int, r[2].split("-"))
                elif r[2].isdigit():
                    a1 = a2 = int(r[2])
                else:
                    a1, a2 = a_min_def, a_max_def
                risultati.append(genera_profilo(r[0], int(r[1]), r[3], a1, a2))
            except:
                continue
    return risultati
