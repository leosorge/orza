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

st.set_page_config(page_title="ORZA - Sistema Astrologico", layout="wide")
st.title("♈ Sistema Astrologico Inverso (ORZA)")

def mostra_profilo(p):
    """Visualizzazione ricca (Metriche + Match)."""
    st.markdown(f"### Profilo di {p['nome'].upper()}")
    
    # Griglia 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Data di nascita", p["data"].strftime("%d/%m/%Y"))
    c2.metric("Ora di nascita", p["ora"])
    c3.metric("Età", f"{p['eta']} anni")
    
    # Griglia 2
    c4, c5 = st.columns(2)
    c4.metric("☀️ Segno Solare", p["segno"])
    c5.metric("⬆️ Ascendente", p["ascendente"])
    
    # Griglia 3
    c6, c7, c8 = st.columns(3)
    c6.metric("Fase di vita", p["fase"])
    c7.metric("Casa dominante", p["casa_dominante"])
    c8.metric("Anno riferimento", p["anno_max"])

    # Dettaglio Keyword (La sezione che non "parlava")
    with st.expander("🔍 Dettaglio keyword match (Top 3 segni)"):
        for i, (segno, score) in enumerate(p["top3_segni"], 1):
            st.write(f"{i}. **{segno}** — Totale: {score} match")
            # Legge dal dizionario match_dettagli sincronizzato
            parole_list = p["match_dettagli"].get(segno, [])
            if parole_list:
                keyword_str = ", ".join([f"{w} ({s})" for w, s in parole_list[:3]])
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*Principali: {keyword_str}*")
            else:
                st.write("&nbsp;&nbsp;&nbsp;&nbsp;*Nessun match trovato.*")

# TAB LAYOUT
t1, t2 = st.tabs(["👤 Singolo", "📄 Multiplo"])

with t1:
    with st.form("f_singolo"):
        nome = st.text_input("Nome e Cognome")
        col_e, col_r = st.columns(2)
        with col_e:
            eta = st.number_input("Età", value=30)
        with col_r:
            anno = st.number_input("Anno rif.", value=2026)
        desc = st.text_area("Carattere")
        inv = st.form_submit_button("✨ Genera")

    if inv and nome and desc:
        p = genera_profilo(nome, eta, desc, anno, anno)
        st.divider()
        mostra_profilo(p)
        
        # Download
        cd1, cd2 = st.columns(2)
        with cd1:
            st.download_button("⬇️ Report", formatta_profilo_testo(p), f"{nome}.txt", key="btn_f")
        with cd2:
            st.download_button("⬇️ Nome/Data", f"{nome}, {p['data'].strftime('%d/%m/%Y')}", f"{nome}_data.txt", key="btn_s")

with t2:
    f_up = st.file_uploader("Carica TXT", type=["txt"])
    if f_up:
        if st.button("🚀 Elabora", use_container_width=True):
            st.session_state.bulk = genera_profili_da_file(f_up.read().decode(), 2026, 2026)
        
        if "bulk" in st.session_state:
            for p in st.session_state.bulk:
                mostra_profilo(p)
                st.divider()
