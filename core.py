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

# Dizionario semplificato
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
    if not nlp: return [("Neutro", 0)], {}
    doc = nlp(testo.lower())
    punteggi = {s: 0 for s in DIZIONARIO_SEGNI}
    dettagli = {s: [] for s in DIZIONARIO_SEGNI}

    for token in doc:
        t_low = token.text.lower()
        l_low = token.lemma_.lower()
        for segno, keywords in DIZIONARIO_SEGNI.items():
            if t_low in keywords or l_low in keywords:
                punteggi[segno] += 1
                if t_low not in dettagli[segno]:
                    dettagli[segno].append(t_low)
    
    # Prende i top 3
    top3 = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)[:3]
    # Crea la stringa statistica per l'app
    stat_per_app = {}
    for s, p in top3:
        # Se ci sono parole, crea la lista formattata (parola (1.0))
        parole_formattate = ", ".join([f"{w} (1.0)" for w in dettagli[s][:3]])
        stat_per_app[s] = parole_formattate if parole_formattate else "Nessun match diretto"
        
    return top3, stat_per_app

def genera_profilo(nome, eta, descrizione, anno_min, anno_max):
    top3, dettagli = analizza_descrizione(descrizione)
    anno_n = random.randint(anno_min - eta, anno_max - eta)
    data_n = datetime(anno_n, random.randint(1,12), random.randint(1,28))
    
    return {
        "nome": nome, "eta": eta, "descrizione": descrizione,
        "anno_min": anno_min, "anno_max": anno_max,
        "data": data_n, "ora": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "segno": top3[0][0] if top3[0][1] > 0 else "Pesci",
        "ascendente": random.choice(list(DIZIONARIO_SEGNI.keys())),
        "fase": random.choice(["Luna Piena", "Luna Nuova", "Crescente", "Calante"]),
        "casa_dominante": f"Casa {random.randint(1,12)}",
        "top3_segni": top3,
        "match_dettagli": dettagli
    }

def formatta_profilo_testo(p):
    return f"PROFILO: {p['nome']}\nData: {p['data'].strftime('%d/%m/%Y')}\nSegno: {p['segno']}\n"

def genera_profili_da_file(testo, a1, a2):
    res = []
    for b in testo.split("==="):
        r = [l.strip() for l in b.strip().split("\n") if l.strip()]
        if len(r) >= 4:
            try: res.append(genera_profilo(r[0], int(r[1]), r[3], a1, a2))
            except: continue
    return res
