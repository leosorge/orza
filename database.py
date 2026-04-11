# database.py
# ─────────────────────────────────────────────────────────────────────────────
# Database astrologico per il sistema di generazione inversa della data di nascita.
#
# Fonti di riferimento (semplificazione didattica):
#   - Tratti caratteriali: tradizione astrologica occidentale classica
#   - Finestre temporali: calendario zodiacale solare standard
#
# Per arricchire il sistema, aggiungere keyword alle liste di TRATTI_SEGNI
# senza modificare la struttura del dizionario.
# ─────────────────────────────────────────────────────────────────────────────


# Tratti caratteriali per segno (semplificato ma funzionale).
# Ogni voce è una lista di aggettivi/sostantivi che descrivono
# la personalità tipicamente associata a quel segno.
# Il motore di analisi cerca queste parole nella descrizione fornita
# e assegna un punteggio a ciascun segno: vince quello con più match.

TRATTI_SEGNI = {
    "Ariete": [
        "impulsivo", "coraggioso", "energico", "competitivo",
        "diretto", "aggressivo", "audace", "pioniere",
    ],
    "Toro": [
        "paziente", "testardo", "affidabile", "sensuale",
        "materiale", "ostinato", "concreto", "fedele",
    ],
    "Gemelli": [
        "curioso", "versatile", "comunicativo", "superficiale",
        "adattabile", "duplice", "brillante", "irrequieto",
    ],
    "Cancro": [
        "emotivo", "protettivo", "intuitivo", "sensibile",
        "nostalgico", "materno", "romantico", "chiuso",
    ],
    "Leone": [
        "carismatico", "orgoglioso", "creativo", "generoso",
        "dominante", "leadership", "teatrale", "ambizioso",
    ],
    "Vergine": [
        "analitico", "preciso", "critico", "metodico",
        "perfezionista", "pratico", "riservato", "ordinato",
    ],
    "Bilancia": [
        "diplomatico", "equilibrato", "indeciso", "estetico",
        "giusto", "sociale", "elegante", "mediatore",
    ],
    "Scorpione": [
        "intenso", "misterioso", "determinato", "vendicativo",
        "passionale", "oscuro", "profondo", "tenace",
    ],
    "Sagittario": [
        "ottimista", "avventuroso", "filosofico", "libero",
        "espansivo", "diretto", "idealista", "viaggiatore",
    ],
    "Capricorno": [
        "ambizioso", "disciplinato", "prudente", "serio",
        "responsabile", "freddo", "calcolatore", "perseverante",
    ],
    "Acquario": [
        "originale", "ribelle", "umanitario", "distaccato",
        "innovativo", "eccentrico", "visionario", "indipendente",
    ],
    "Pesci": [
        "sognatore", "empatico", "sfuggente", "creativo",
        "spirituale", "confuso", "melanconico", "compassionevole",
    ],
}


# Finestre temporali di ciascun segno zodiacale solare.
# Formato: (mese_inizio, giorno_inizio, mese_fine, giorno_fine)
# Nota: il Capricorno attraversa il capodanno (dic→gen),
#       per questo mese_inizio > mese_fine — la logica speciale
#       è gestita in core.py → data_da_segno_ed_eta().

FINESTRE_SEGNI = {
    "Ariete":      (3, 21,  4, 19),
    "Toro":        (4, 20,  5, 20),
    "Gemelli":     (5, 21,  6, 20),
    "Cancro":      (6, 21,  7, 22),
    "Leone":       (7, 23,  8, 22),
    "Vergine":     (8, 23,  9, 22),
    "Bilancia":    (9, 23, 10, 22),
    "Scorpione":  (10, 23, 11, 21),
    "Sagittario": (11, 22, 12, 21),
    "Capricorno": (12, 22,  1, 19),  # ← attraversa capodanno
    "Acquario":    (1, 20,  2, 18),
    "Pesci":       (2, 19,  3, 20),
}
