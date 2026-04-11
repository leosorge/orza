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

from __future__ import annotations  # compatibilità type hint su Python 3.7–3.9

import re
import random
from datetime import datetime, date, timedelta
from typing import Optional

from database import TRATTI_SEGNI, FINESTRE_SEGNI


# ── 1. SEGNO SOLARE ───────────────────────────────────────────────────────────

def segno_da_descrizione(descrizione: str) -> tuple[str, list]:
    """
    Analizza la descrizione testuale del personaggio e restituisce
    il segno zodiacale con il maggior numero di keyword corrispondenti.

    Parametri
    ---------
    descrizione : str
        Testo libero che descrive il carattere del personaggio.

    Restituisce
    -----------
    segno : str
        Nome del segno zodiacale dominante.
    top3 : list
        Lista dei primi 3 segni per punteggio (utile per debug/UI).
    """
    desc = descrizione.lower()
    punteggi = {s: 0 for s in TRATTI_SEGNI}

    for segno, tratti in TRATTI_SEGNI.items():
        for tratto in tratti:
            if tratto in desc:
                punteggi[segno] += 1

    top3 = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)[:3]

    # Se nessuna keyword corrisponde, fallback casuale
    if max(punteggi.values()) == 0:
        return random.choice(list(TRATTI_SEGNI.keys())), top3

    return max(punteggi, key=punteggi.get), top3


# ── 2. DATA DI NASCITA ────────────────────────────────────────────────────────

def _finestra_segno_in_anno(segno: str, anno_nascita: int) -> tuple[date, date]:
    """
    Restituisce (start, end) della finestra zodiacale del segno
    nell'anno di nascita indicato.
    Gestisce il caso Capricorno che attraversa il capodanno.
    """
    mi, gi, mf, gf = FINESTRE_SEGNI[segno]
    if mi > mf:
        # Capricorno: metà dicembre → metà gennaio dell'anno dopo
        # Scegliamo casualmente su quale dei due semestri cadere
        if random.random() < 0.5:
            return date(anno_nascita, mi, gi), date(anno_nascita, 12, 31)
        else:
            return date(anno_nascita + 1, 1, 1), date(anno_nascita + 1, mf, gf)
    else:
        return date(anno_nascita, mi, gi), date(anno_nascita, mf, gf)


def data_da_segno_ed_eta(
    segno: str,
    eta: int,
    anno_min: int = None,
    anno_max: int = None,
) -> date:
    """
    Genera una data di nascita casuale ma astrologicamente coerente,
    compatibile con il segno solare, l'età e il range di anni fornito.

    Logica del range
    ----------------
    Se il personaggio ha 'eta' anni e il range è [anno_min, anno_max],
    allora l'anno di nascita cade nell'intervallo:
        [anno_min - eta,  anno_max - eta]
    La data viene poi scelta casualmente dentro la finestra zodiacale
    del segno, all'interno di quell'intervallo di anni di nascita.

    Se anno_min e anno_max coincidono (o viene passato un solo anno),
    si comporta come la versione precedente a anno fisso.

    Parametri
    ---------
    segno    : str  — segno zodiacale solare del personaggio
    eta      : int  — età del personaggio nell'anno di riferimento
    anno_min : int  — estremo inferiore del range (default: anno reale)
    anno_max : int  — estremo superiore del range (default: anno_min)

    Restituisce
    -----------
    date — data di nascita compatibile con segno, età e range
    """
    if anno_min is None:
        anno_min = datetime.now().year
    if anno_max is None or anno_max < anno_min:
        anno_max = anno_min

    # Intervallo degli anni di nascita compatibili con il range e l'età
    nascita_min = anno_min - eta
    nascita_max = anno_max - eta

    # Raccoglie tutte le date valide (dentro la finestra del segno)
    # per ciascun anno di nascita nell'intervallo.
    # Per evitare loop enormi su range molto ampi, campiona un anno casuale
    # nell'intervallo e poi genera la data dentro la finestra di quell'anno.
    anno_nascita = random.randint(nascita_min, nascita_max)
    start, end   = _finestra_segno_in_anno(segno, anno_nascita)

    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ── 3. ASCENDENTE ─────────────────────────────────────────────────────────────

def calcola_ascendente(ora: int, minuti: int, segno_solare: str) -> str:
    """
    Calcola l'ascendente in base all'ora di nascita e al segno solare,
    usando una tavola semplificata a slot da 2 ore.

    Logica: l'ascendente cambia ogni ~2 ore; per convenzione classica,
    al sorgere del sole (circa ore 6) l'ascendente coincide con il segno
    solare. Da lì si scorre la ruota zodiacale in avanti o indietro.

    Parametri
    ---------
    ora          : int — ora di nascita (0–23)
    minuti       : int — minuti di nascita (0–59)
    segno_solare : str — segno solare del personaggio

    Restituisce
    -----------
    str — nome del segno ascendente
    """
    segni = list(TRATTI_SEGNI.keys())
    indice_solare = segni.index(segno_solare)

    # Dividiamo le 24 ore in 12 slot da 2h; slot 3 corrisponde alle ore 6
    slot = (ora * 60 + minuti) // 120
    ascendente_indice = (indice_solare + slot - 3) % 12

    return segni[ascendente_indice]


# ── 4. FASE DI VITA ───────────────────────────────────────────────────────────

def fase_eta(eta: int) -> tuple[str, str]:
    """
    Restituisce la fase di vita e la casa astrologica dominante
    in base all'età del personaggio.

    Fasce:
        0–29  → Giovinezza  (Prima Casa)
        30–50 → Maturità    (Seconda Casa)
        51+   → Senescenza  (Influenza mista)

    Parametri
    ---------
    eta : int — età del personaggio

    Restituisce
    -----------
    (fase: str, casa_dominante: str)
    """
    if eta <= 29:
        return "Giovinezza", "Prima Casa"
    elif eta <= 50:
        return "Maturità", "Seconda Casa"
    else:
        return "Senescenza", "Influenza mista"


# ── FUNZIONE AGGREGATRICE ─────────────────────────────────────────────────────

def genera_profilo(
    nome: str,
    eta: int,
    descrizione: str,
    anno_min: int = None,
    anno_max: int = None,
) -> dict:
    """
    Funzione principale: aggrega tutti i passaggi e restituisce
    il profilo astrologico completo come dizionario.

    Parametri
    ---------
    nome        : str — nome del personaggio
    eta         : int — età del personaggio
    descrizione : str — descrizione testuale del carattere
    anno_min    : int — estremo inferiore del range di anni di riferimento
                        (default: anno reale corrente)
    anno_max    : int — estremo superiore del range di anni di riferimento
                        (default: uguale ad anno_min → anno fisso)

    Esempio: eta=35, anno_min=1850, anno_max=1880
        → anno di nascita casuale tra 1815 e 1845
        → data dentro la finestra del segno rilevato

    Restituisce
    -----------
    dict con chiavi: nome, eta, anno_min, anno_max, data, ora,
                     segno, ascendente, fase, casa_dominante, top3_segni
    """
    segno, top3 = segno_da_descrizione(descrizione)
    data         = data_da_segno_ed_eta(segno, eta, anno_min, anno_max)
    ora          = random.randint(0, 23)
    minuti       = random.randint(0, 59)
    ascendente   = calcola_ascendente(ora, minuti, segno)
    fase, casa   = fase_eta(eta)

    return {
        "nome":           nome,
        "eta":            eta,
        "anno_min":       anno_min,
        "anno_max":       anno_max,
        "data":           data,
        "ora":            f"{ora:02d}:{minuti:02d}",
        "segno":          segno,
        "ascendente":     ascendente,
        "fase":           fase,
        "casa_dominante": casa,
        "top3_segni":     top3,
    }


# ── GESTIONE FILE MULTIPLI ────────────────────────────────────────────────────

def parse_file_multiplo(testo: str) -> list[dict]:
    """
    Legge un file .txt contenente la descrizione di più personaggi e
    restituisce una lista di dizionari pronti per genera_profilo().

    Formato atteso per ogni personaggio (blocchi separati da '===…==='):
    ──────────────────────────────────────────────────────────────────
    Nome Cognome
    35
    1850-1880
    "descrizione libera del carattere, anche su più righe"
    ──────────────────────────────────────────────────────────────────
    - Riga 1 : nome
    - Riga 2 : età (intero)
    - Riga 3 : range anni nel formato YYYY-YYYY  (es. 1850-1880)
               oppure anno singolo YYYY           (es. 1865)
               oppure "-" / vuoto per usare l'anno reale corrente
    - Righe 4+: descrizione (le virgolette doppie sono opzionali)

    I blocchi possono essere separati da una riga di '=' (≥10 caratteri)
    oppure da due o più righe vuote consecutive.

    Parametri
    ---------
    testo : str — contenuto grezzo del file caricato

    Restituisce
    -----------
    list[dict] con chiavi: nome, eta, anno_min, anno_max, descrizione
                e 'errore' (str) se il blocco non è parsabile
    """
    blocchi_raw = re.split(r'={10,}|\n\s*\n\s*\n+', testo)

    personaggi = []
    for blocco in blocchi_raw:
        righe = [r.strip() for r in blocco.strip().splitlines() if r.strip()]
        if not righe:
            continue

        # Serve almeno nome + età + range + almeno una riga di descrizione
        if len(righe) < 4:
            personaggi.append({
                "errore": f"Blocco incompleto (meno di 4 righe): «{righe}»"
            })
            continue

        nome_p = righe[0]

        # Riga 2: età
        try:
            eta_p = int(righe[1])
        except ValueError:
            personaggi.append({
                "errore": f"Età non riconosciuta per «{nome_p}»: «{righe[1]}»"
            })
            continue

        # Riga 3: range anni — accetta "YYYY-YYYY", "YYYY" o "-" / vuoto
        anno_min_p, anno_max_p = _parse_range_anni(righe[2])

        # Righe 4+: descrizione
        desc_raw = " ".join(righe[3:]).strip()
        desc_p   = desc_raw.strip('"').strip()

        personaggi.append({
            "nome":        nome_p,
            "eta":         eta_p,
            "anno_min":    anno_min_p,
            "anno_max":    anno_max_p,
            "descrizione": desc_p,
        })

    return personaggi


def _parse_range_anni(testo_range: str) -> tuple[Optional[int], Optional[int]]:
    """
    Interpreta la stringa del range anni e restituisce (anno_min, anno_max).

    Formati accettati:
        "1850-1880"  → (1850, 1880)
        "1865"       → (1865, 1865)
        "-" o ""     → (None, None)  → usa anno reale corrente
    """
    t = testo_range.strip()
    if not t or t == "-":
        return None, None
    if "-" in t:
        parti = t.split("-")
        # gestisce il caso in cui ci siano esattamente due numeri
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


def genera_profili_da_file(
    testo: str,
    anno_min_default: int = None,
    anno_max_default: int = None,
) -> list[dict]:
    """
    Pipeline completa per file multipli: parsa il testo e genera
    un profilo astrologico per ogni personaggio valido trovato.

    Il range anni letto dal file ha priorità; se assente nel blocco,
    si usa il range di default passato a questa funzione (impostabile
    dalla UI come fallback globale).

    Parametri
    ---------
    testo            : str — contenuto grezzo del file .txt caricato
    anno_min_default : int — fallback se il blocco non specifica il range
    anno_max_default : int — fallback se il blocco non specifica il range

    Restituisce
    -----------
    list[dict] — ogni dict è un profilo completo (da genera_profilo)
                 oppure contiene solo la chiave 'errore' se il blocco
                 non era parsabile
    """
    personaggi = parse_file_multiplo(testo)
    risultati  = []

    for p in personaggi:
        if "errore" in p:
            risultati.append(p)
        else:
            # Il range del blocco ha priorità sul default globale
            a_min = p["anno_min"] if p["anno_min"] is not None else anno_min_default
            a_max = p["anno_max"] if p["anno_max"] is not None else anno_max_default

            profilo = genera_profilo(
                nome        = p["nome"],
                eta         = p["eta"],
                descrizione = p["descrizione"],
                anno_min    = a_min,
                anno_max    = a_max,
            )
            risultati.append(profilo)

    return risultati


def formatta_profilo_testo(profilo: dict) -> str:
    """
    Serializza un singolo profilo astrologico in un blocco testuale
    leggibile, adatto all'output su file .txt scaricabile.

    Parametri
    ---------
    profilo : dict — come restituito da genera_profilo()

    Restituisce
    -----------
    str — blocco testuale formattato
    """
    if "errore" in profilo:
        return f"[ERRORE] {profilo['errore']}\n"

    top3_str = ", ".join(f"{s} ({p})" for s, p in profilo["top3_segni"])

    # Formatta il range anni per l'output
    a_min = profilo.get("anno_min")
    a_max = profilo.get("anno_max")
    if a_min and a_max and a_min != a_max:
        range_str = f"{a_min}–{a_max}"
    elif a_min:
        range_str = str(a_min)
    else:
        range_str = "anno corrente"

    return (
        f"{'='*50}\n"
        f"PROFILO: {profilo['nome'].upper()}\n"
        f"{'='*50}\n"
        f"Età:               {profilo['eta']} anni\n"
        f"Range riferimento: {range_str}\n"
        f"Data di nascita:   {profilo['data'].strftime('%d/%m/%Y')} "
        f"alle {profilo['ora']}\n"
        f"Segno Solare:      {profilo['segno']}\n"
        f"Ascendente:        {profilo['ascendente']}\n"
        f"Fase di vita:      {profilo['fase']} → {profilo['casa_dominante']}\n"
        f"Match keyword:     {top3_str}\n"
    )
