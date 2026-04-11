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

# DEVE ESSERE COSÌ - NOTA LE VIRGOLE E LE PARENTESI
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime
from core import genera_profilo, genera_profili_da_file, formatta_profilo_testo

st.set_page_config(page_title="ORZA", layout="wide")
st.title("♈ Sistema Astrologico ORZA")

def mostra_profilo(p):
    st.markdown(f"## Profilo di {p['nome'].upper()}")
    
    # RIGA 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Data di nascita", p["data"].strftime("%d/%m/%Y"))
    c2.metric("Ora di nascita", p["ora"])
    c3.metric("Età", f"{p['eta']} anni")
    
    # RIGA 2
    c4, c5 = st.columns(2)
    c4.metric("☀️ Segno Solare", p["segno"])
    c5.metric("⬆️ Ascendente", p["ascendente"])
    
    # RIGA 3
    c6, c7, c8 = st.columns(3)
    c6.metric("Fase di vita", p["fase"])
    c7.metric("Casa dominante", p["casa_dominante"])
    c8.metric("Riferimento", p["anno_max"])

    # DETTAGLIO MATCH
    with st.expander("🔍 Dettaglio keyword match"):
        # Ora il core e l'app si parlano attraverso match_dettagli
        for i, (segno, score) in enumerate(p["top3_segni"], 1):
            parole_trovate = p["match_dettagli"].get(segno, [])
            if score > 0 or parole_trovate:
                st.write(f"{i}. **{segno}** (Punteggio: {score})")
                if parole_trovate:
                    # Mostra le parole trovate
                    txt_parole = ", ".join([f"{w} ({s})" for w, s in parole_trovate])
                    st.write(f"&nbsp;&nbsp;&nbsp;*Parole: {txt_parole}*")
            else:
                # Se è il primo e non c'è match, segnalalo
                if i == 1: st.write("Nessuna keyword specifica rilevata: assegnazione per affinità.")

# INTERFACCIA UTENTE
t1, t2 = st.tabs(["👤 Singolo", "📄 Massivo"])

with t1:
    with st.form("f1"):
        n = st.text_input("Nome e Cognome")
        col_e, col_a = st.columns(2)
        with col_e: e = st.number_input("Età", value=35)
        with col_a: a = st.number_input("Anno", value=2026)
        d = st.text_area("Descrizione caratteriale")
        btn = st.form_submit_button("✨ GENERA PROFILO")
    
    if btn and n and d:
        profilo = genera_profilo(n, e, d, a, a)
        st.divider()
        mostra_profilo(profilo)

with t2:
    f = st.file_uploader("Carica file .txt")
    if f:
        if st.button("🚀 Elabora"):
            st.session_state.bulk = genera_profili_da_file(f.read().decode(), 2026, 2026)
        if "bulk" in st.session_state:
            for p in st.session_state.bulk:
                mostra_profilo(p)
                st.divider()
