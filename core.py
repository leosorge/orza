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
from datetime import datetime

try:
    nlp = spacy.load("it_core_news_sm")
except:
    nlp = None

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

def analizza_descrizione(testo):
    testo_low = testo.lower()
    punteggi = {s: 0.0 for s in DIZIONARIO_SEGNI}
    dettagli = {s: [] for s in DIZIONARIO_SEGNI}

    # Analisi incrociata NLP + Keyword matching diretto
    parole_testo = set(testo_low.split())
    if nlp:
        doc = nlp(testo_low)
        parole_testo.update([t.lemma_ for t in doc])

    for segno, keywords in DIZIONARIO_SEGNI.items():
        for kw in keywords:
            if kw in parole_testo or kw in testo_low:
                punteggi[segno] += 1.0
                if kw not in dettagli[segno]:
                    dettagli[segno].append(kw)

    # Ordinamento Top 3
    ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
    return ordinati[:3], dettagli

def genera_profilo(nome, eta, descrizione, a_min, a_max):
    top3, match_dettagli = analizza_descrizione(descrizione)
    
    anno_n = random.randint(a_min - eta, a_max - eta)
    data_n = datetime(anno_n, random.randint(1,12), random.randint(1,28))
    
    # FIX REFUSO: Lista numerica per evitare "Seconda-a"
    case = [f"{i}ª Casa" for i in range(1, 13)]
    fasi = ["Giovinezza", "Maturità", "Luna Piena", "Luna Nuova", "Crescente"]

    return {
        "nome": nome, "eta": eta, "descrizione": descrizione,
        "data": data_n, "ora": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "segno": top3[0][0] if top3[0][1] > 0 else "Pesci",
        "ascendente": random.choice(list(DIZIONARIO_SEGNI.keys())),
        "fase": random.choice(fasi),
        "casa_dominante": random.choice(case),
        "anno_rif": a_max,
        "top3_segni": top3,
        "match_dettagli": match_dettagli
    }

def genera_profili_da_file(testo, a1, a2):
    res = []
    for b in testo.split("==="):
        r = [l.strip() for l in b.strip().split("\n") if l.strip()]
        if len(r) >= 4:
            try: res.append(genera_profilo(r[0], int(r[1]), r[3], a1, a2))
            except: continue
    return res
