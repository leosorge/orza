# core.py
# ─────────────────────────────────────────────────────────────────────────────
# Funzioni principali del sistema astrologico inverso.
#
# Flusso logico:
#   1. descrizione testuale  →  segno solare  (keyword matching)
#   2. segno solare + età    →  data di nascita compatibile
#   3. ora di nascita        →  ascendente (tavola semplificata a slot da 2h)
#   4. età                   →  fase di vita (Giovinezza / Maturità / Senescenza)
# ─────────────────────────────────────────────────────────────────────────────

import random
from datetime import datetime, date, timedelta

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

def data_da_segno_ed_eta(segno: str, eta: int, anno_rif: int = None) -> date:
    """
    Genera una data di nascita casuale ma astrologicamente coerente:
    cade sempre nella finestra temporale del segno solare indicato,
    nell'anno di nascita ricavato da (anno_rif - eta).

    Parametri
    ---------
    segno    : str  — segno zodiacale solare del personaggio
    eta      : int  — età attuale del personaggio in anni
    anno_rif : int  — anno di riferimento "corrente" (default: anno reale)

    Restituisce
    -----------
    date — data di nascita compatibile con segno ed età
    """
    if anno_rif is None:
        anno_rif = datetime.now().year

    anno_nascita = anno_rif - eta
    mi, gi, mf, gf = FINESTRE_SEGNI[segno]

    # Il Capricorno attraversa il capodanno: scegliamo casualmente
    # se mettere la nascita nella parte di dicembre o in quella di gennaio
    if mi > mf:
        if random.random() < 0.5:
            start = date(anno_nascita, mi, gi)
            end   = date(anno_nascita, 12, 31)
        else:
            start = date(anno_nascita + 1, 1, 1)
            end   = date(anno_nascita + 1, mf, gf)
    else:
        start = date(anno_nascita, mi, gi)
        end   = date(anno_nascita, mf, gf)

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

def genera_profilo(nome: str, eta: int, descrizione: str, anno_rif: int = None) -> dict:
    """
    Funzione principale: aggrega tutti i passaggi e restituisce
    il profilo astrologico completo come dizionario.

    Parametri
    ---------
    nome        : str — nome del personaggio
    eta         : int — età del personaggio
    descrizione : str — descrizione testuale del carattere
    anno_rif    : int — anno corrente di riferimento (default: anno reale)

    Restituisce
    -----------
    dict con chiavi: nome, eta, data, ora, segno, ascendente,
                     fase, casa_dominante, top3_segni
    """
    segno, top3 = segno_da_descrizione(descrizione)
    data         = data_da_segno_ed_eta(segno, eta, anno_rif)
    ora          = random.randint(0, 23)
    minuti       = random.randint(0, 59)
    ascendente   = calcola_ascendente(ora, minuti, segno)
    fase, casa   = fase_eta(eta)

    return {
        "nome":           nome,
        "eta":            eta,
        "data":           data,
        "ora":            f"{ora:02d}:{minuti:02d}",
        "segno":          segno,
        "ascendente":     ascendente,
        "fase":           fase,
        "casa_dominante": casa,
        "top3_segni":     top3,   # utile per mostrare il ragionamento nella UI
    }
