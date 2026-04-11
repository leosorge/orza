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
st.title("♈ Sistema ORZA")

def mostra_profilo(p):
    st.subheader(f"Profilo di {p['nome']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Data", p["data"].strftime("%d/%m/%Y"))
    c2.metric("Segno", p["segno"])
    c3.metric("Età", f"{p['eta']} anni")
    
    with st.expander("🔍 Dettaglio Keyword Match"):
        for i, (segno, score) in enumerate(p["top3_segni"], 1):
            parole = p["match_dettagli"].get(segno, "Nessun match")
            st.write(f"{i}. **{segno}** (Punteggio: {score})")
            st.write(f"&nbsp;&nbsp;&nbsp;*Parole: {parole}*")

t1, t2 = st.tabs(["👤 Singolo", "📄 Multiplo"])

with t1:
    with st.form("f1"):
        n = st.text_input("Nome")
        e = st.number_input("Età", value=30)
        d = st.text_area("Descrizione")
        btn = st.form_submit_button("Genera")
    if btn and n and d:
        p = genera_profilo(n, e, d, 2026, 2026)
        mostra_profilo(p)
        st.download_button("Scarica Data", f"{p['nome']}, {p['data'].strftime('%d/%m/%Y')}", f"{p['nome']}.txt")

with t2:
    f = st.file_uploader("Carica file")
    if f:
        if st.button("Elabora"):
            st.session_state.res = genera_profili_da_file(f.read().decode(), 2026, 2026)
        if "res" in st.session_state:
            for p in st.session_state.res:
                mostra_profilo(p)
                st.divider()
