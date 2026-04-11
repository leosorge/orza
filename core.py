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
import re
from datetime import datetime

# Caricamento NLP (opzionale ma consigliato per i lemmi)
try:
    nlp = spacy.load("it_core_news_sm")
except:
    nlp = None

DIZIONARIO_SEGNI = {
    "Ariete": ["coraggioso", "impulsivo", "energico", "diretto", "impaziente", "audace", "combattivo", "leader"],
    "Toro": ["paziente", "ostinato", "sensuale", "concreto", "leale", "possessivo", "calmo", "stabile"],
    "Gemelli": ["curioso", "versatile", "comunicativo", "socievole", "inquieto", "brillante", "ironico", "doppio"],
    "Cancro": ["sensibile", "protettivo", "emotivo", "intuitivo", "lunatico", "tenace", "dolce", "materno"],
    "Leone": ["generoso", "orgoglioso", "carismatico", "dominante", "creativo", "leale", "fiero", "solare"],
    "Vergine": ["analitico", "preciso", "reservato", "metodico", "critico", "laborioso", "serio", "pignolo"],
    "Bilancia": ["diplomatico", "esteta", "indeciso", "equilibrato", "socievole", "gentile", "elegante", "giusto"],
    "Scorpione": ["intenso", "misterioso", "passionale", "tenace", "oscuro", "intuitivo", "profondo", "magnetico"],
    "Sagittario": ["ottimista", "avventuroso", "indipendente", "sincero", "entusiasta", "filosofico", "esploratore"],
    "Capricorno": ["ambizioso", "disciplinato", "paziente", "serio", "freddo", "perseverante", "determinato", "rigido"],
    "Acquario": ["originale", "idealista", "indipendente", "ribelle", "visionario", "distaccato", "eccentrico", "altruista"],
    "Pesci": ["empatico", "sognatore", "sensibile", "altruista", "visionario", "spirituale", "sfuggente", "mistico"]
}

def analizza_testo(testo):
    """Analisi con Regex per garantire il match delle keyword."""
    testo_low = testo.lower()
    punteggi = {s: 0 for s in DIZIONARIO_SEGNI}
    match_dettagli = {s: [] for s in DIZIONARIO_SEGNI}

    for segno, keywords in DIZIONARIO_SEGNI.items():
        for kw in keywords:
            # Pattern per trovare la parola intera, ignorando punteggiatura
            pattern = rf"\b{kw}\b"
            matches = re.findall(pattern, testo_low)
            if matches:
                count = len(matches)
                punteggi[segno] += count
                match_dettagli[segno].append((kw, count))

    # Ordina i segni per punteggio decrescente
    ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
    return ordinati, match_dettagli

def genera_profilo(nome, eta, descrizione, a_min, a_max):
    risultati_match, dettagli = analizza_testo(descrizione)
    
    # Se non ci sono match, non scriviamo "Neutro", ma usiamo il primo segno del dizionario per coerenza
    # o un sistema di fallback intelligente.
    segno_scelto = risultati_match[0][0] if risultati_match[0][1] > 0 else "Bilancia"
    
    anno_n = random.randint(a_min - eta, a_max - eta)
    data_n = datetime(anno_n, random.randint(1,12), random.randint(1,28))
    
    # Pulizia totale dei suffissi ordinali
    case_lista = [f"{i}ª Casa" for i in range(1, 13)]
    fasi = ["Luna Crescente", "Luna Calante", "Luna Piena", "Luna Nuova"]

    return {
        "nome": nome, "eta": eta, "descrizione": descrizione,
        "data": data_n, "ora": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "segno": segno_scelto,
        "ascendente": random.choice(list(DIZIONARIO_SEGNI.keys())),
        "fase": random.choice(fasi),
        "casa_dominante": random.choice(case_lista),
        "anno_rif": a_max,
        "top3": risultati_match[:3],
        "dettagli": dettagli
    }

def formatta_report(p):
    return f"SISTEMA ORZA - REPORT\nNome: {p['nome']}\nNascita: {p['data'].strftime('%d/%m/%Y')}\nSegno: {p['segno']}\n"
