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
from core import genera_profilo, formatta_report

st.set_page_config(page_title="ORZA Mark IV", layout="wide")

st.title("♈ Sistema Astrologico ORZA")
st.markdown("---")

def render_profilo(p):
    st.header(f"Profilo di {p['nome'].upper()}")
    
    # Griglia Metriche
    row1_1, row1_2, row1_3 = st.columns(3)
    row1_1.metric("Data di nascita", p["data"].strftime("%d/%m/%Y"))
    row1_2.metric("Ora di nascita", p["ora"])
    row1_3.metric("Età", f"{p['eta']} anni")
    
    row2_1, row2_2 = st.columns(2)
    row2_1.metric("☀️ Segno Solare", p["segno"])
    row2_2.metric("⬆️ Ascendente", p["ascendente"])
    
    row3_1, row3_2, row3_3 = st.columns(3)
    row3_1.metric("Fase di vita", p["fase"])
    row3_2.metric("Casa dominante", p["casa_dominante"])
    row3_3.metric("Range riferimento", p["anno_rif"])

    # Sezione Analisi
    with st.expander("🔍 Analisi Keyword e Corrispondenze"):
        for segno, score in p["top3"]:
            st.write(f"**{segno}** — Match totali: {score}")
            matches = p["dettagli"].get(segno, [])
            if matches:
                # Mostra le parole che hanno generato il match
                testo_parole = ", ".join([f"{parola} ({n})" for parola, n in matches])
                st.info(f"Keyword rilevate: {testo_parole}")
            else:
                st.write("*Nessun match diretto per questo segno.*")

# Form di input
with st.container():
    with st.form("input_form"):
        nome = st.text_input("Nome e Cognome")
        c1, c2 = st.columns(2)
        with c1: eta = st.number_input("Età", 1, 120, 35)
        with c2: anno = st.number_input("Anno Rif.", 1000, 2100, 2026)
        desc = st.text_area("Descrizione Caratteriale (usa parole chiave come 'coraggioso', 'analitico', ecc.)")
        submit = st.form_submit_button("🚀 GENERA ANALISI ORZA")

if submit and nome and desc:
    profilo = genera_profilo(nome, eta, desc, anno, anno)
    st.success("Analisi Completata")
    render_profilo(profilo)
    
    # Download
    st.divider()
    st.subheader("💾 Esportazione Dati")
    d1, d2 = st.columns(2)
    d1.download_button("Report Testuale", formatta_report(profilo), f"{nome}_report.txt")
    d2.download_button("Dati per Database", f"{nome}, {profilo['data'].strftime('%d/%m/%Y')}", f"{nome}_data.txt")
