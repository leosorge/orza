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

from __future__ import annotations  # compatibilità type hint Python 3.7–3.9

# core.py — Sistema Astrologico ORZA
# ─────────────────────────────────────────────────────────────────────────────
# Motore semantico + generazione profilo astrologico inverso.
#
# Flusso:
#   1. descrizione testuale  →  segno solare
#      Prima prova il matching esatto (regex \b parola \b).
#      Se zero match, prova il matching per radice (stemming manuale):
#      cerca se la keyword è contenuta come sottostringa nella parola
#      del testo (es. "coraggi" in "coraggioso"). Questo permette di
#      catturare flessioni e derivati senza dipendere da spaCy.
#   2. segno + età + range anni  →  data di nascita dentro la finestra zodiacale
#   3. ora casuale               →  ascendente (tavola slot 2h)
#   4. età                       →  fase di vita
#
# spaCy è opzionale: se il modello italiano è disponibile, viene usato
# per lemmatizzare il testo prima del matching (migliora la copertura).
# Se non è disponibile, il sistema funziona comunque con regex+stemming.
# ─────────────────────────────────────────────────────────────────────────────

import re
import random
from datetime import datetime, date, timedelta
from typing import Optional

# ── spaCy opzionale ───────────────────────────────────────────────────────────
try:
    import spacy
    _nlp = spacy.load("it_core_news_sm")
except Exception:
    _nlp = None   # funzionamento degradato ma comunque operativo

from database import TRATTI_SEGNI, FINESTRE_SEGNI


# ── 1. MOTORE SEMANTICO ───────────────────────────────────────────────────────

def _lemmatizza(testo: str) -> str:
    """
    Se spaCy è disponibile, restituisce il testo lemmatizzato
    (forme base delle parole). Altrimenti restituisce il testo invariato.
    Questo permette di matchare "coraggioso" → "coraggioso",
    "coraggio" → "coraggioso" ecc.
    """
    if _nlp is None:
        return testo.lower()
    doc = _nlp(testo.lower())
    return " ".join(token.lemma_ for token in doc)


def analizza_testo(testo: str) -> tuple[list, dict]:
    """
    Analizza il testo in due passate:

    Passata 1 — match esatto (regex \\bparola\\b):
        Trova le keyword così come sono nel testo.

    Passata 2 — match per radice (stemming manuale):
        Se una keyword è contenuta come sottostringa in una parola
        del testo (min 5 caratteri), conta come match parziale (peso 0.5).
        Es: "coraggi" è nella parola "coraggiosamente" → match parziale.

    Se spaCy è disponibile, il testo viene prima lemmatizzato,
    migliorando la copertura delle flessioni.

    Parametri
    ---------
    testo : str — descrizione testuale del personaggio

    Restituisce
    -----------
    (ordinati, dettagli)
        ordinati : list[(segno, punteggio)] — ordinati per punteggio desc
        dettagli : dict{segno: [(keyword, conteggio)]} — per la UI
    """
    testo_elaborato = _lemmatizza(testo)
    # Estrae le singole parole per il matching per radice
    parole_testo = re.findall(r"[a-zàèéìòù]{4,}", testo_elaborato)

    punteggi = {s: 0.0 for s in TRATTI_SEGNI}
    dettagli = {s: [] for s in TRATTI_SEGNI}

    for segno, keywords in TRATTI_SEGNI.items():
        for kw in keywords:
            # Passata 1: match esatto
            pattern = rf"\b{re.escape(kw)}\b"
            trovati = re.findall(pattern, testo_elaborato)
            if trovati:
                n = len(trovati)
                punteggi[segno] += n
                dettagli[segno].append((kw, n))
                continue  # evita doppio conteggio

            # Passata 2: stemming manuale (solo keyword ≥ 5 caratteri)
            if len(kw) >= 5:
                radice = kw[:max(5, len(kw) - 2)]  # tronca ultimi 2 caratteri
                for parola in parole_testo:
                    if radice in parola:
                        punteggi[segno] += 0.5
                        dettagli[segno].append((f"~{kw}", 1))
                        break  # una sola volta per keyword

    ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
    return ordinati, dettagli


# ── 2. DATA DI NASCITA ────────────────────────────────────────────────────────

def _finestra_segno_in_anno(segno: str, anno_nascita: int) -> tuple[date, date]:
    """Restituisce (start, end) della finestra zodiacale nell'anno dato."""
    mi, gi, mf, gf = FINESTRE_SEGNI[segno]
    if mi > mf:  # Capricorno attraversa capodanno
        if random.random() < 0.5:
            return date(anno_nascita, mi, gi), date(anno_nascita, 12, 31)
        else:
            return date(anno_nascita + 1, 1, 1), date(anno_nascita + 1, mf, gf)
    return date(anno_nascita, mi, gi), date(anno_nascita, mf, gf)


def data_da_segno_ed_eta(
    segno: str,
    eta: int,
    anno_min: Optional[int] = None,
    anno_max: Optional[int] = None,
) -> date:
    """
    Genera una data di nascita casuale ma astrologicamente coerente:
    - anno di nascita random in [anno_min - eta, anno_max - eta]
    - giorno random dentro la finestra zodiacale del segno
    """
    if anno_min is None:
        anno_min = datetime.now().year
    if anno_max is None or anno_max < anno_min:
        anno_max = anno_min

    anno_nascita = random.randint(anno_min - eta, anno_max - eta)
    start, end   = _finestra_segno_in_anno(segno, anno_nascita)
    delta        = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ── 3. ASCENDENTE ─────────────────────────────────────────────────────────────

def calcola_ascendente(ora: int, minuti: int, segno_solare: str) -> str:
    """
    Tavola semplificata: ogni 2 ore cambia segno.
    Al sorgere del sole (ore 6) l'ascendente coincide col segno solare.
    """
    segni = list(TRATTI_SEGNI.keys())
    indice_solare = segni.index(segno_solare)
    slot = (ora * 60 + minuti) // 120
    return segni[(indice_solare + slot - 3) % 12]


# ── 4. FASE DI VITA ───────────────────────────────────────────────────────────

def fase_eta(eta: int) -> tuple[str, str]:
    """0–29 → Giovinezza / 30–50 → Maturità / 51+ → Senescenza"""
    if eta <= 29:
        return "Giovinezza", "Prima Casa"
    elif eta <= 50:
        return "Maturità", "Seconda Casa"
    else:
        return "Senescenza", "Influenza mista"


# ── 5. FUNZIONE AGGREGATRICE ──────────────────────────────────────────────────

def genera_profilo(
    nome: str,
    eta: int,
    descrizione: str,
    anno_min: Optional[int] = None,
    anno_max: Optional[int] = None,
) -> dict:
    """
    Genera il profilo astrologico completo.

    Restituisce un dict con:
        nome, eta, descrizione, data, ora, segno, ascendente,
        fase, casa_dominante, anno_rif (label stringa per la UI),
        anno_min, anno_max, top3, dettagli
    """
    risultati, dettagli = analizza_testo(descrizione)

    # Segno: primo con punteggio > 0, altrimenti Bilancia come fallback neutro
    segno = risultati[0][0] if risultati[0][1] > 0 else "Bilancia"

    data   = data_da_segno_ed_eta(segno, eta, anno_min, anno_max)
    ora    = random.randint(0, 23)
    minuti = random.randint(0, 59)
    ascendente = calcola_ascendente(ora, minuti, segno)
    fase, casa = fase_eta(eta)

    # Label leggibile del range per la UI
    if anno_min and anno_max and anno_min != anno_max:
        anno_rif_label = f"{anno_min}–{anno_max}"
    elif anno_min:
        anno_rif_label = str(anno_min)
    else:
        anno_rif_label = "anno corrente"

    return {
        "nome":           nome,
        "eta":            eta,
        "descrizione":    descrizione,
        "data":           data,          # oggetto date — usa .strftime() in app
        "ora":            f"{ora:02d}:{minuti:02d}",
        "segno":          segno,
        "ascendente":     ascendente,
        "fase":           fase,
        "casa_dominante": casa,
        "anno_rif":       anno_rif_label,  # stringa per UI — es. "1850–1880"
        "anno_min":       anno_min,
        "anno_max":       anno_max,
        "top3":           risultati[:3],
        "dettagli":       dettagli,
    }


# ── 6. GESTIONE FILE MULTIPLI ─────────────────────────────────────────────────

def _parse_range_anni(testo_range: str) -> tuple[Optional[int], Optional[int]]:
    """
    Interpreta la stringa del range anni.
    "1850-1880" → (1850, 1880)
    "1865"      → (1865, 1865)
    "-" o ""    → (None, None)
    """
    t = testo_range.strip()
    if not t or t == "-":
        return None, None
    if "-" in t:
        parti = t.split("-")
        try:
            a1, a2 = int(parti[0].strip()), int(parti[1].strip())
            return (a1, a2) if a1 <= a2 else (a2, a1)
        except (ValueError, IndexError):
            return None, None
    try:
        anno = int(t)
        return anno, anno
    except ValueError:
        return None, None


def _parse_blocchi(blocchi_raw: list) -> list[dict]:
    """Converte blocchi già separati in lista dizionari personaggio."""
    personaggi = []
    for blocco in blocchi_raw:
        righe = [r.strip() for r in blocco.strip().splitlines() if r.strip()]
        if not righe:
            continue
        if len(righe) < 4:
            personaggi.append({"errore": f"Blocco incompleto: «{righe}»"})
            continue
        nome_p = righe[0]
        try:
            eta_p = int(righe[1])
        except ValueError:
            personaggi.append({"errore": f"Età non valida per «{nome_p}»: «{righe[1]}»"})
            continue
        anno_min_p, anno_max_p = _parse_range_anni(righe[2])
        desc_p = " ".join(righe[3:]).strip().strip('"')
        personaggi.append({
            "nome": nome_p, "eta": eta_p,
            "anno_min": anno_min_p, "anno_max": anno_max_p,
            "descrizione": desc_p,
        })
    return personaggi


def parse_file_multiplo(testo: str) -> list[dict]:
    """
    Legge un .txt con più personaggi — 4 righe per blocco:
        Riga 1: nome
        Riga 2: età
        Riga 3: range anni (YYYY-YYYY, YYYY, o -)
        Riga 4: descrizione

    Separatori accettati: riga di "=" (≥10), doppia riga vuota,
    o nessun separatore (blocchi da 4 righe consecutive).
    """
    if re.search(r'={10,}|\n\s*\n\s*\n', testo):
        return _parse_blocchi(re.split(r'={10,}|\n\s*\n\s*\n+', testo))

    # Formato compatto: raggruppa righe non vuote a blocchi di 4
    righe = [r.strip() for r in testo.splitlines() if r.strip()]
    personaggi = []
    i = 0
    while i + 3 < len(righe):
        nome_c = righe[i]
        try:
            eta_c = int(righe[i + 1])
        except ValueError:
            personaggi.append({"errore": f"Età non valida per «{nome_c}»: «{righe[i+1]}»"})
            i += 1
            continue
        anno_min_c, anno_max_c = _parse_range_anni(righe[i + 2])
        desc_c = righe[i + 3].strip('"')
        personaggi.append({
            "nome": nome_c, "eta": eta_c,
            "anno_min": anno_min_c, "anno_max": anno_max_c,
            "descrizione": desc_c,
        })
        i += 4
    return personaggi


def genera_profili_da_file(
    testo: str,
    anno_min_default: Optional[int] = None,
    anno_max_default: Optional[int] = None,
) -> list[dict]:
    """Genera un profilo per ogni personaggio nel file."""
    personaggi = parse_file_multiplo(testo)
    risultati = []
    for p in personaggi:
        if "errore" in p:
            risultati.append(p)
        else:
            a_min = p["anno_min"] if p["anno_min"] is not None else anno_min_default
            a_max = p["anno_max"] if p["anno_max"] is not None else anno_max_default
            risultati.append(genera_profilo(
                nome=p["nome"], eta=p["eta"],
                descrizione=p["descrizione"],
                anno_min=a_min, anno_max=a_max,
            ))
    return risultati


def formatta_report(p: dict) -> str:
    """Serializza un profilo in testo scaricabile."""
    if "errore" in p:
        return f"[ERRORE] {p['errore']}\n"
    top3_str = ", ".join(f"{s} ({round(sc, 1)})" for s, sc in p["top3"])
    return (
        f"{'='*50}\n"
        f"PROFILO: {p['nome'].upper()}\n"
        f"{'='*50}\n"
        f"Età:               {p['eta']} anni\n"
        f"Range riferimento: {p['anno_rif']}\n"
        f"Data di nascita:   {p['data'].strftime('%d/%m/%Y')} alle {p['ora']}\n"
        f"Segno Solare:      {p['segno']}\n"
        f"Ascendente:        {p['ascendente']}\n"
        f"Fase di vita:      {p['fase']} → {p['casa_dominante']}\n"
        f"Match keyword:     {top3_str}\n"
    )


def formatta_profilo_testo(p: dict) -> str:
    """Alias di formatta_report per compatibilità con versioni precedenti."""
    return formatta_report(p)
