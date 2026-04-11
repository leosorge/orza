# app.py
# ─────────────────────────────────────────────────────────────────────────────
# Interfaccia Streamlit per il sistema astrologico inverso.
#
# Avvio locale:
#   pip install streamlit
#   streamlit run app.py
#
# Deploy su Streamlit Cloud:
#   1. Pubblica la cartella su GitHub (assicurati che requirements.txt sia presente)
#   2. Vai su https://share.streamlit.io → "New app" → seleziona il repo
#   3. File principale: app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime

from core import genera_profilo


# ── CONFIGURAZIONE PAGINA ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="Sistema Astrologico Inverso",
    page_icon="♈",
    layout="centered",
)

st.title("♈ Sistema Astrologico Inverso")
st.caption(
    "Genera una data di nascita astrologicamente coerente "
    "a partire dalla descrizione del carattere di un personaggio."
)
st.divider()


# ── FORM DI INPUT ─────────────────────────────────────────────────────────────

with st.form("form_profilo"):

    nome = st.text_input(
        "Nome e Cognome",
        placeholder="es. Marco Rossi",
    )

    col1, col2 = st.columns(2)
    with col1:
        eta = st.number_input(
            "Età", min_value=1, max_value=120, value=35, step=1
        )
    with col2:
        anno_rif = st.number_input(
            "Anno di riferimento",
            min_value=1800,
            max_value=2200,
            value=datetime.now().year,
            step=1,
            help="Anno 'corrente' del personaggio. Utile per ambientazioni storiche o fantastiche.",
        )

    descrizione = st.text_area(
        "Descrizione del carattere",
        placeholder=(
            "es. persona determinata, ambiziosa, disciplinata e seria nel lavoro, "
            "a volte fredda ma molto perseverante..."
        ),
        height=120,
    )

    inviato = st.form_submit_button("✨ Genera profilo", use_container_width=True)


# ── GENERAZIONE E OUTPUT ──────────────────────────────────────────────────────

if inviato:

    # Validazione minima
    if not nome.strip():
        st.warning("Inserisci il nome del personaggio.")
        st.stop()
    if not descrizione.strip():
        st.warning("Inserisci una descrizione del carattere.")
        st.stop()

    # Generazione profilo
    profilo = genera_profilo(
        nome=nome.strip(),
        eta=int(eta),
        descrizione=descrizione.strip(),
        anno_rif=int(anno_rif),
    )

    st.divider()
    st.subheader(f"Profilo di {profilo['nome'].upper()}")

    # Riga principale: data, segno, ascendente
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Data di nascita", profilo["data"].strftime("%d/%m/%Y"))
    col_b.metric("Ora di nascita",  profilo["ora"])
    col_c.metric("Età",             f"{profilo['eta']} anni")

    st.divider()

    col_d, col_e = st.columns(2)
    col_d.metric("☀️ Segno Solare",  profilo["segno"])
    col_e.metric("⬆️ Ascendente",    profilo["ascendente"])

    st.divider()

    col_f, col_g = st.columns(2)
    col_f.metric("Fase di vita",     profilo["fase"])
    col_g.metric("Casa dominante",   profilo["casa_dominante"])

    # Dettaglio keyword match (espandibile)
    with st.expander("🔍 Dettaglio analisi del carattere"):
        st.write("**Top 3 segni per keyword trovate nella descrizione:**")
        for i, (segno_k, punteggio) in enumerate(profilo["top3_segni"], 1):
            st.write(f"{i}. **{segno_k}** — {punteggio} keyword")
        if profilo["top3_segni"][0][1] == 0:
            st.info(
                "Nessuna keyword riconosciuta: segno assegnato casualmente. "
                "Prova ad arricchire la descrizione con aggettivi più specifici."
            )

    # Download del profilo come .txt
    testo_output = (
        f"PROFILO ASTROLOGICO: {profilo['nome'].upper()}\n"
        f"Età:               {profilo['eta']} anni\n"
        f"Data di nascita:   {profilo['data'].strftime('%d/%m/%Y')} alle {profilo['ora']}\n"
        f"Segno Solare:      {profilo['segno']}\n"
        f"Ascendente:        {profilo['ascendente']}\n"
        f"Fase di vita:      {profilo['fase']} → {profilo['casa_dominante']}\n"
    )
    nome_file = profilo["nome"].replace(" ", "_").lower() + "-astro.txt"
    st.download_button(
        label="⬇️ Scarica profilo (.txt)",
        data=testo_output,
        file_name=nome_file,
        mime="text/plain",
        use_container_width=True,
    )
