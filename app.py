# app.py — Sistema Astrologico ORZA
# ─────────────────────────────────────────────────────────────────────────────
# Interfaccia Streamlit con due tab:
#   Tab 1 — Singolo personaggio (form manuale + range anni)
#   Tab 2 — File multipli (.txt con N personaggi, download risultati)
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime

from core import (
    genera_profilo,
    genera_profili_da_file,
    formatta_report,
)

st.set_page_config(page_title="ORZA Mark IV", page_icon="♈", layout="wide")

st.title("♈ Sistema Astrologico ORZA")
st.caption(
    "Genera una data di nascita astrologicamente coerente a partire dalla "
    "descrizione del carattere, dall'età e dal periodo storico di riferimento. "
    "— Esempio: età 34, range 1880–1910, \"intensa, misteriosa, tenace\" "
    "→ Scorpione, nata il 14/11/1861."
)
st.markdown("---")


# ── HELPER: mostra un profilo ─────────────────────────────────────────────────

def render_profilo(p: dict):
    """Renderizza un profilo nella UI Streamlit."""
    st.header(f"Profilo di {p['nome'].upper()}")

    # Riga 1: date e età
    c1, c2, c3 = st.columns(3)
    c1.metric("Data di nascita", p["data"].strftime("%d/%m/%Y"))
    c2.metric("Ora di nascita",  p["ora"])
    c3.metric("Età",             f"{p['eta']} anni")

    # Riga 2: segno e ascendente
    c4, c5 = st.columns(2)
    c4.metric("☀️ Segno Solare", p["segno"])
    c5.metric("⬆️ Ascendente",   p["ascendente"])

    # Riga 3: fase, casa, range
    c6, c7, c8 = st.columns(3)
    c6.metric("Fase di vita",        p["fase"])
    c7.metric("Casa dominante",      p["casa_dominante"])
    c8.metric("Range riferimento",   p["anno_rif"])

    # Dettaglio keyword
    with st.expander("🔍 Analisi Keyword e Corrispondenze"):
        if p["top3"][0][1] == 0:
            st.info(
                "Nessuna keyword riconosciuta nella descrizione. "
                "Il segno è stato assegnato come fallback (Bilancia). "
                "Prova ad aggiungere tratti caratteriali alla descrizione, "
                "es: 'coraggioso, impulsivo, determinato'."
            )
        for segno, score in p["top3"]:
            st.write(f"**{segno}** — Score: {round(score, 1)}")
            matches = p["dettagli"].get(segno, [])
            if matches:
                testo_match = ", ".join(
                    f"{parola} (×{n})" for parola, n in matches
                )
                st.info(f"Keyword rilevate: {testo_match}")
            else:
                st.write("*Nessun match per questo segno.*")


# ── TAB LAYOUT ────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["👤 Personaggio singolo", "📄 File multipli"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGOLO PERSONAGGIO
# ════════════════════════════════════════════════════════════════════════════

with tab1:
    with st.form("input_form"):
        nome = st.text_input("Nome e Cognome", placeholder="es. Elena Voss")

        col_eta, col_range = st.columns(2)
        with col_eta:
            eta = st.number_input("Età", min_value=1, max_value=120, value=35)
        with col_range:
            st.markdown("**Range anni di riferimento**")
            cy1, cy2 = st.columns(2)
            with cy1:
                anno_min = st.number_input(
                    "Da (YYYY)", min_value=1, max_value=9999,
                    value=datetime.now().year, step=1, key="amin_s",
                    help="Anno iniziale. Es: 1850",
                )
            with cy2:
                anno_max = st.number_input(
                    "A (YYYY)", min_value=1, max_value=9999,
                    value=datetime.now().year, step=1, key="amax_s",
                    help="Anno finale. Uguale al precedente = anno fisso.",
                )

        desc = st.text_area(
            "Descrizione del carattere",
            placeholder=(
                "Usa tratti caratteriali, es: 'coraggioso, impulsivo, energico, "
                "determinato'. Per personaggi storici aggiungi tratti al contesto."
            ),
            height=120,
        )
        submit = st.form_submit_button("🚀 Genera Analisi ORZA", use_container_width=True)

    if submit:
        if not nome.strip():
            st.warning("Inserisci il nome del personaggio.")
            st.stop()
        if not desc.strip():
            st.warning("Inserisci una descrizione del carattere.")
            st.stop()
        if anno_min > anno_max:
            st.warning("L'anno iniziale non può essere maggiore dell'anno finale.")
            st.stop()

        profilo = genera_profilo(
            nome        = nome.strip(),
            eta         = int(eta),
            descrizione = desc.strip(),
            anno_min    = int(anno_min),
            anno_max    = int(anno_max),
        )

        st.success("Analisi completata.")
        render_profilo(profilo)

        st.divider()
        st.subheader("💾 Esportazione")
        d1, d2 = st.columns(2)
        nome_safe = nome.strip().replace(" ", "_").lower()
        d1.download_button(
            "⬇️ Report testuale",
            data      = formatta_report(profilo),
            file_name = f"{nome_safe}_report.txt",
            mime      = "text/plain",
        )
        d2.download_button(
            "⬇️ Riga per database",
            data      = (
                f"{profilo['nome']}, "
                f"{profilo['data'].strftime('%d/%m/%Y')}, "
                f"{profilo['segno']}, "
                f"{profilo['ascendente']}, "
                f"{profilo['anno_rif']}"
            ),
            file_name = f"{nome_safe}_data.txt",
            mime      = "text/plain",
        )


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FILE MULTIPLI
# ════════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown(
        """
        Carica un file `.txt` con più personaggi — **4 righe per blocco**,
        separati da `===` oppure senza separatore (blocchi compatti):
        ```
        Elena Voss
        34
        1880-1910
        intensa, misteriosa, tenace, passionale, profonda
        ===========================
        Andrew Jackson
        14
        1781-1781
        coraggioso, impulsivo, energico, combattivo, determinato
        ```
        > Per personaggi storici: aggiungi tratti di carattere alla riga 4,
        > non solo il contesto biografico.
        """
    )

    st.markdown("**Range globale** (fallback per blocchi con `-` alla riga 3):")
    cg1, cg2 = st.columns(2)
    with cg1:
        anno_min_g = st.number_input(
            "Da (YYYY)", min_value=1, max_value=9999,
            value=datetime.now().year, step=1, key="amin_g",
        )
    with cg2:
        anno_max_g = st.number_input(
            "A (YYYY)", min_value=1, max_value=9999,
            value=datetime.now().year, step=1, key="amax_g",
        )

    file_up = st.file_uploader("Carica il file .txt", type=["txt"])

    if file_up is not None:
        testo_raw = file_up.read().decode("utf-8")

        if st.button("🚀 Genera tutti i profili", use_container_width=True):

            if anno_min_g > anno_max_g:
                st.warning("Il range globale non è valido.")
                st.stop()

            profili = genera_profili_da_file(
                testo_raw,
                anno_min_default = int(anno_min_g),
                anno_max_default = int(anno_max_g),
            )

            if not profili:
                st.error("Nessun personaggio trovato. Controlla il formato.")
            else:
                st.success(f"Analizzati **{len(profili)}** personaggi.")
                st.divider()

                blocchi_output = ["PROFILI ASTROLOGICI — Sistema ORZA\n\n"]
                for p in profili:
                    if "errore" in p:
                        st.warning(f"⚠️ {p['errore']}")
                    else:
                        render_profilo(p)
                        st.divider()
                    blocchi_output.append(formatta_report(p))

                nome_out = file_up.name.replace(".txt", "") + "-orza.txt"
                st.download_button(
                    label               = "⬇️ Scarica tutti i profili (.txt)",
                    data                = "\n".join(blocchi_output),
                    file_name           = nome_out,
                    mime                = "text/plain",
                    use_container_width = True,
                )
