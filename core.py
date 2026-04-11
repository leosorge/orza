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

# Caricamento NLP
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
    """Analisi statistica delle keyword: ritorna Top 3 e dettagli."""
    if not nlp: return [("Neutro", 0)], {}
    doc = nlp(testo.lower())
    punteggi = {s: 0 for s in DIZIONARIO_SEGNI}
    match_parole = {s: [] for s in DIZIONARIO_SEGNI}

    for token in doc:
        t, l = token.text.lower(), token.lemma_.lower()
        for segno, keywords in DIZIONARIO_SEGNI.items():
            if t in keywords or l in keywords:
                punteggi[segno] += 1
                if t not in [x[0] for x in match_parole[segno]]:
                    match_parole[segno].append((t, 1.0)) # Peso statistico
    
    # Ordiniamo e prendiamo i top 3 segni
    top3 = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)[:3]
    return top3, match_parole

def genera_profilo(nome, eta, descrizione, a_min, a_max):
    """Crea il dizionario profilo completo per l'interfaccia."""
    top3, dettagli = analizza_descrizione(descrizione)
    
    # Calcolo data
    anno_n = random.randint(a_min - eta, a_max - eta)
    data_n = datetime(anno_n, random.randint(1,12), random.randint(1,28))
    
    # Variabili estetiche (CORRETTO "Seconda")
    segni_tutti = list(DIZIONARIO_SEGNI.keys())
    fasi = ["Luna Piena", "Luna Nuova", "Crescente", "Calante"]
    case_lista = [f"{n}ª Casa" for n in ["Prima", "Seconda", "Terza", "Quarta", "Quinta", "Sesta", "Settima"]]

    return {
        "nome": nome, "eta": eta, "descrizione": descrizione,
        "anno_min": a_min, "anno_max": a_max,
        "data": data_n, "ora": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "segno": top3[0][0] if top3[0][1] > 0 else random.choice(segni_tutti),
        "ascendente": random.choice(segni_tutti),
        "fase": random.choice(fasi),
        "casa_dominante": random.choice(case_lista),
        "top3_segni": top3,
        "match_dettagli": dettagli
    }

def formatta_profilo_testo(p):
    """Report testuale per download."""
    return f"ORZA REPORT: {p['nome'].upper()}\nData: {p['data'].strftime('%d/%m/%Y')} | Segno: {p['segno']}\n"

def genera_profili_da_file(testo, a1, a2):
    """Parsing per blocchi multipli."""
    res = []
    for b in testo.split("==="):
        r = [l.strip() for l in b.strip().split("\n") if l.strip()]
        if len(r) >= 4:
            try: res.append(genera_profilo(r[0], int(r[1]), r[3], a1, a2))
            except: continue
    return res
