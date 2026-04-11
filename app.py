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

# 1. PRIMISSIMA COSA: Configurazione pagina
st.set_page_config(
    page_title="ORZA",
    page_icon="🔮",
    layout="wide"
)

# 2. ALTRI IMPORT (opzionali)
from datetime import datetime

# 3. IMPORTA TUTTO DA CORE (Incluso nlp)

from core import genera_profilo, genera_profili_da_file, formatta_profilo_testo, nlp

# 4. ORA PUOI USARE NLP NELL'INTERFACCIA
st.title("Sistema ORZA")
if st.button("Verifica Motore"):
    st.write(f"Modello caricato: {nlp.meta['name']}")

st.title("♈ Sistema Astrologico Inverso")
st.caption(
    "Genera una data di nascita astrologicamente coerente a partire dalla "
    "descrizione del carattere, dall'età e dal periodo storico di riferimento. "
)
st.divider()


# ── HELPER: mostra un profilo ─────────────────────────────────────────────────

def mostra_profilo(profilo: dict):
    """Renderizza un profilo astrologico nella UI Streamlit."""
    # --- PARTE FINALE TAB SINGOLO ---
    st.divider()
    mostra_profilo(profilo)
        
    testo_dettagliato = formatta_profilo_testo(profilo)
    data_f = profilo["data"].strftime("%d/%m/%Y")
    testo_lista_singola = f"{profilo['nome']}, {data_f}"
        
    st.subheader("💾 Scarica Profilo")
    col_s1, col_s2 = st.columns(2)
        
    with col_s1:
        st.download_button(
            label="⬇️ Report Completo (.txt)",
            data=testo_dettagliato,
            file_name=f"{profilo['nome'].replace(' ', '_')}_dettaglio.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_single_full"
        )
            
    with col_s2:
        st.download_button(
            label="⬇️ Solo Nome e Data (.txt)",
            data=testo_lista_singola,
            file_name=f"{profilo['nome'].replace(' ', '_')}_data.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_single_short"
        )
