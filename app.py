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
from core import genera_profilo, genera_profili_da_file

st.set_page_config(page_title="ORZA", layout="wide")
st.title("♈ Sistema Astrologico ORZA")

def mostra_profilo(p):
    st.markdown(f"## Profilo di {p['nome'].upper()}")
    
    # Riga 1: Metriche Temporali
    c1, c2, c3 = st.columns(3)
    c1.metric("Data di nascita", p["data"].strftime("%d/%m/%Y"))
    c2.metric("Ora di nascita", p["ora"])
    c3.metric("Età", f"{p['eta']} anni")
    
    # Riga 2: Metriche Astrologiche
    c4, c5 = st.columns(2)
    c4.metric("☀️ Segno Solare", p["segno"])
    c5.metric("⬆️ Ascendente", p["ascendente"])
    
    # Riga 3: Contesto
    c6, c7, c8 = st.columns(3)
    c6.metric("Fase di vita", p["fase"])
    c7.metric("Casa dominante", p["casa_dominante"])
    c8.metric("Range riferimento", p["anno_rif"])

    # Dettaglio Match - SINCRONIZZATO
    with st.expander("🔍 Dettaglio keyword match (Top 3 segni)"):
        for i, (segno, score) in enumerate(p["top3_segni"], 1):
            parole = p["match_dettagli"].get(segno, [])
            st.write(f"{i}. **{segno}** — Totale: {score} match")
            if parole:
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*Keyword: {', '.join([f'{w} (1.0)' for w in parole])}*")
            else:
                st.write("&nbsp;&nbsp;&nbsp;&nbsp;*Nessun match diretto rilevato.*")

t1, t2 = st.tabs(["👤 Singolo", "📄 Massivo"])

with t1:
    with st.form("f1"):
        n = st.text_input("Nome e Cognome")
        col_e, col_a = st.columns(2)
        with col_e: e = st.number_input("Età", value=35)
        with col_a: a = st.number_input("Anno rif.", value=2026)
        d = st.text_area("Descrizione")
        btn = st.form_submit_button("✨ GENERA PROFILO")
    
    if btn and n and d:
        p = genera_profilo(n, e, d, a, a)
        st.divider()
        mostra_profilo(p)
        
        # Download (Sistemati)
        st.subheader("💾 Scarica Profilo")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("⬇️ Report Completo", f"Profilo: {p['nome']}\nData: {p['data']}\nSegno: {p['segno']}", f"{p['nome']}_full.txt")
        with col_d2:
            st.download_button("⬇️ Solo Nome e Data", f"{p['nome']}, {p['data'].strftime('%d/%m/%Y')}", f"{p['nome']}_data.txt")

with t2:
    f = st.file_uploader("Carica file .txt")
    if f:
        if st.button("🚀 Elabora"):
            st.session_state.bulk = genera_profili_da_file(f.read().decode(), 2026, 2026)
        if "bulk" in st.session_state:
            for p in st.session_state.bulk:
                mostra_profilo(p)
                st.divider()
