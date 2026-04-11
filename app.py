# app.py
# ─────────────────────────────────────────────────────────────────────────────
# Interfaccia Streamlit per il sistema astrologico inverso.
#
# Due modalità:
#   Tab 1 — Singolo personaggio: form manuale con range anni
#   Tab 2 — File multipli: carica .txt con N personaggi (ciascuno può avere
#            il proprio range); range globale come fallback
#
# Avvio locale:   streamlit run app.py
# Deploy:         share.streamlit.io → repo GitHub → file: app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime

from core import genera_profilo, genera_profili_da_file, formatta_profilo_testo


# ── CONFIGURAZIONE PAGINA ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="Sistema Astrologico Inverso",
    page_icon="♈",
    layout="centered",
)

st.title("♈ Sistema Astrologico Inverso")
st.caption(
    "Genera una data di nascita astrologicamente coerente a partire dalla "
    "descrizione del carattere, dall'età e dal periodo storico di riferimento. "
    "— Esempio: *età 34, range 1880–1910, \"intensa, misteriosa, tenace\"* "
    "→ Scorpione, nata il 14/11/1861."
)
st.divider()


# ── HELPER: mostra un profilo ─────────────────────────────────────────────────

def mostra_profilo(profilo: dict):
    """Renderizza un profilo astrologico nella UI Streamlit."""
    st.subheader(f"Profilo di {profilo['nome'].upper()}")

    # Range anni di riferimento
    a_min = profilo.get("anno_min")
    a_max = profilo.get("anno_max")
    if a_min and a_max and a_min != a_max:
        range_label = f"{a_min}–{a_max}"
    elif a_min:
        range_label = str(a_min)
    else:
        range_label = "anno corrente"

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Data di nascita",      profilo["data"].strftime("%d/%m/%Y"))
    col_b.metric("Ora di nascita",        profilo["ora"])
    col_c.metric("Età",                   f"{profilo['eta']} anni")

    col_d, col_e = st.columns(2)
    col_d.metric("☀️ Segno Solare",       profilo["segno"])
    col_e.metric("⬆️ Ascendente",         profilo["ascendente"])

    col_f, col_g, col_h = st.columns(3)
    col_f.metric("Fase di vita",          profilo["fase"])
    col_g.metric("Casa dominante",        profilo["casa_dominante"])
    col_h.metric("Range riferimento",     range_label)

    with st.expander("🔍 Dettaglio keyword match"):
        for i, (segno_k, punteggio) in enumerate(profilo["top3_segni"], 1):
            st.write(f"{i}. **{segno_k}** — {punteggio} keyword")
        if profilo["top3_segni"][0][1] == 0:
            st.info(
                "Nessuna keyword riconosciuta: segno assegnato casualmente. "
                "Prova ad arricchire la descrizione con aggettivi più specifici."
            )


# ── TAB LAYOUT ────────────────────────────────────────────────────────────────

tab_singolo, tab_multi = st.tabs(["👤 Personaggio singolo", "📄 File multipli"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGOLO PERSONAGGIO
# ════════════════════════════════════════════════════════════════════════════

with tab_singolo:

    with st.form("form_singolo"):

        nome = st.text_input(
            "Nome e Cognome", placeholder="es. Marco Rossi"
        )

        col1, col2 = st.columns(2)
        with col1:
            eta = st.number_input(
                "Età", min_value=1, max_value=120, value=35, step=1
            )
        with col2:
            st.markdown("**Range anni di riferimento**")
            # Anno minimo e massimo del periodo in cui il personaggio ha quell'età
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                anno_min = st.number_input(
                    "Da (YYYY)", min_value=1, max_value=9999,
                    value=datetime.now().year,
                    step=1, key="anno_min_s",
                    help="Anno iniziale del range. Es: 1850",
                )
            with col_y2:
                anno_max = st.number_input(
                    "A (YYYY)", min_value=1, max_value=9999,
                    value=datetime.now().year,
                    step=1, key="anno_max_s",
                    help="Anno finale del range. Uguale al precedente = anno fisso.",
                )

        descrizione = st.text_area(
            "Descrizione del carattere",
            placeholder=(
                "es. persona determinata, ambiziosa, disciplinata e seria "
                "nel lavoro, a volte fredda ma molto perseverante..."
            ),
            height=120,
        )

        inviato = st.form_submit_button(
            "✨ Genera profilo", use_container_width=True
        )

    if inviato:
        if not nome.strip():
            st.warning("Inserisci il nome del personaggio.")
            st.stop()
        if not descrizione.strip():
            st.warning("Inserisci una descrizione del carattere.")
            st.stop()
        if anno_min > anno_max:
            st.warning("L'anno iniziale non può essere maggiore dell'anno finale.")
            st.stop()

        profilo = genera_profilo(
            nome        = nome.strip(),
            eta         = int(eta),
            descrizione = descrizione.strip(),
            anno_min    = int(anno_min),
            anno_max    = int(anno_max),
        )

        st.divider()
        mostra_profilo(profilo)

        testo_out = formatta_profilo_testo(profilo)
        nome_file = profilo["nome"].replace(" ", "_").lower() + "-astro.txt"
        st.download_button(
            label               = "⬇️ Scarica profilo (.txt)",
            data                = testo_out,
            file_name           = nome_file,
            mime                = "text/plain",
            use_container_width = True,
        )


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FILE MULTIPLI
# ════════════════════════════════════════════════════════════════════════════

with tab_multi:

    st.markdown(
        """
        Carica un file `.txt` con la descrizione di più personaggi.

        **Formato atteso** — 4 righe per blocco, separati da `===`:
        ```
        Marco Rossi
        35
        1850-1880
        "determinato, ambizioso, disciplinato, freddo ma perseverante"
        ===========================
        Lucia Ferretti
        28
        1920
        "creativa, sognante, empatica, spirituale, a tratti sfuggente"
        ===========================
        Giovanni Neri
        52
        -
        "ribelle, visionario, distaccato, eccentrico e indipendente"
        ```
        - **Riga 3**: `YYYY-YYYY` per un range, `YYYY` per anno fisso, `-` per usare il range globale sotto.
        """
    )

    st.markdown("**Range anni globale** (usato per i blocchi che hanno `-` alla riga 3):")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        anno_min_glob = st.number_input(
            "Da (YYYY)", min_value=1, max_value=9999,
            value=datetime.now().year, step=1, key="anno_min_g",
        )
    with col_g2:
        anno_max_glob = st.number_input(
            "A (YYYY)", min_value=1, max_value=9999,
            value=datetime.now().year, step=1, key="anno_max_g",
        )

    file_caricato = st.file_uploader("Carica il file .txt", type=["txt"])

    if file_caricato is not None:

        testo_raw = file_caricato.read().decode("utf-8")

        if st.button("✨ Genera tutti i profili", use_container_width=True):

            if anno_min_glob > anno_max_glob:
                st.warning("Il range globale non è valido (anno iniziale > anno finale).")
                st.stop()

            profili = genera_profili_da_file(
                testo_raw,
                anno_min_default = int(anno_min_glob),
                anno_max_default = int(anno_max_glob),
            )

            if not profili:
                st.error(
                    "Nessun personaggio trovato nel file. "
                    "Controlla il formato."
                )
            else:
                st.success(f"Analizzati **{len(profili)}** personaggi.")
                st.divider()

                righe_output = [
                    "PROFILI ASTROLOGICI\n"
                    "Generati dal Sistema Astrologico Inverso\n\n"
                ]

                for profilo in profili:
                    if "errore" in profilo:
                        st.warning(f"⚠️ {profilo['errore']}")
                    else:
                        mostra_profilo(profilo)
                        st.divider()

                    righe_output.append(formatta_profilo_testo(profilo))

                testo_completo = "\n".join(righe_output)
                nome_out = file_caricato.name.replace(".txt", "") + "-astro.txt"
                st.download_button(
                    label               = "⬇️ Scarica tutti i profili (.txt)",
                    data                = testo_completo,
                    file_name           = nome_out,
                    mime                = "text/plain",
                    use_container_width = True,
                )
