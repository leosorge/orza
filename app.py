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

# 1. CONFIGURAZIONE DELLA PAGINA
st.set_page_config(
    page_title="ORZA",
    page_icon="🔮",
    layout="wide"
)

# 2. IMPORTAZIONE LOGICA DAL CORE
from core import genera_profilo, genera_profili_da_file, formatta_profilo_testo, nlp

# --- TITOLO E DESCRIZIONE ---
st.title("♈ Sistema Astrologico Inverso (ORZA)")
st.caption(
    "Genera una data di nascita astrologicamente coerente a partire dalla "
    "descrizione del carattere, dall'età e dal periodo storico di riferimento."
)
st.divider()

# ── HELPER: FUNZIONE PER MOSTRARE IL PROFILO NELL'INTERFACCIA ──────────────────
def mostra_profilo(profilo: dict):
    """Renderizza graficamente un profilo astrologico nella UI."""
    st.subheader(f"Profilo di {profilo['nome'].upper()}")

    # Gestione label anni
    a_min = profilo.get("anno_min")
    a_max = profilo.get("anno_max")
    range_label = f"{a_min}–{a_max}" if a_min != a_max else str(a_min)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Data di nascita", profilo["data"].strftime("%d/%m/%Y"))
    col_b.metric("Ora di nascita", profilo["ora"])
    col_c.metric("Età", f"{profilo['eta']} anni")

    col_d, col_e = st.columns(2)
    col_d.metric("☀️ Segno Solare", profilo["segno"])
    col_e.metric("⬆️ Ascendente", profilo["ascendente"])

    col_f, col_g, col_h = st.columns(3)
    col_f.metric("Fase di vita", profilo["fase"])
    col_g.metric("Casa dominante", profilo["casa_dominante"])
    col_h.metric("Range riferimento", range_label)

    # SEZIONE KEYWORD MATCH AGGIORNATA
    with st.expander("🔍 Dettaglio keyword match (Top 3 segni)"):
        # Mostriamo i primi 3 segni identificati
        for i, (segno_k, punteggio) in enumerate(profilo["top3_segni"], 1):
            # Recuperiamo le parole specifiche che hanno causato il match per quel segno
            # Nota: Assumiamo che il dizionario 'match_dettagli' sia presente nel profilo generato dal core
            dettagli = profilo.get("match_dettagli", {}).get(segno_k, [])
            
            # Prendiamo le prime 3 parole per valore statistico (già ordinate dal core)
            top_words = dettagli[:3]
            keyword_str = ", ".join([f"{parola} ({score})" for parola, score in top_words])
            
            st.write(f"{i}. **{segno_k}** — Totale: {punteggio} match")
            if keyword_str:
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*Principali: {keyword_str}*")
            else:
                st.write("&nbsp;&nbsp;&nbsp;&nbsp;*Nessuna keyword specifica trovata.*")

# ── LAYOUT A SCHEDE (TAB) ─────────────────────────────────────────────────────
tab_singolo, tab_multi = st.tabs(["👤 Personaggio singolo", "📄 File multipli"])

# ==============================================================================
# TAB 1 — SINGOLO PERSONAGGIO
# ==============================================================================
with tab_singolo:
    with st.form("form_singolo"):
        nome = st.text_input("Nome e Cognome", placeholder="es. Marco Rossi")
        
        col1, col2 = st.columns(2)
        with col1:
            eta = st.number_input("Età", min_value=1, max_value=120, value=35)
        with col2:
            st.markdown("**Range anni di riferimento**")
            cy1, cy2 = st.columns(2)
            with cy1:
                anno_min = st.number_input("Da (YYYY)", value=datetime.now().year, key="amin_s")
            with cy2:
                anno_max = st.number_input("A (YYYY)", value=datetime.now().year, key="amax_s")

        descrizione = st.text_area("Descrizione del carattere", height=120)
        inviato = st.form_submit_button("✨ Genera profilo", use_container_width=True)

    if inviato:
        if not nome.strip() or not descrizione.strip():
            st.warning("Inserisci nome e descrizione.")
        else:
            p = genera_profilo(nome.strip(), int(eta), descrizione.strip(), int(anno_min), int(anno_max))
            st.divider()
            mostra_profilo(p)

            testo_full = formatta_profilo_testo(p)
            testo_short = f"{p['nome']}, {p['data'].strftime('%d/%m/%Y')}"

            st.subheader("💾 Scarica Profilo")
            ds1, ds2 = st.columns(2)
            with ds1:
                st.download_button("⬇️ Report Completo", data=testo_full, 
                                 file_name=f"{p['nome']}_dettaglio.txt", key="ds_f")
            with ds2:
                st.download_button("⬇️ Solo Nome e Data", data=testo_short, 
                                 file_name=f"{p['nome']}_data.txt", key="ds_s")

# ==============================================================================
# TAB 2 — FILE MULTIPLI
# ==============================================================================
with tab_multi:
    st.markdown("### 📄 Caricamento Multiplo da file .txt")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        anno_min_g = st.number_input("Anno Min Globale", value=1900, key="amin_g")
    with col_g2:
        anno_max_g = st.number_input("Anno Max Globale", value=2026, key="amax_g")

    file_caricato = st.file_uploader("Carica file .txt", type=["txt"], key="bulk_up")

    if file_caricato:
        testo_raw = file_caricato.read().decode("utf-8")
        
        if st.button("🚀 Elabora tutti i personaggi", use_container_width=True):
            st.session_state.risultati_bulk = genera_profili_da_file(
                testo_raw, int(anno_min_g), int(anno_max_g)
            )

        if "risultati_bulk" in st.session_state:
            res = st.session_state.risultati_bulk
            out_full = ""
            out_short = ""

            for p in res:
                if "errore" not in p:
                    mostra_profilo(p)
                    st.divider()
                    out_full += formatta_profilo_testo(p) + "\n" + "-"*40 + "\n"
                    out_short += f"{p['nome']}, {p['data'].strftime('%d/%m/%Y')}\n"

            st.subheader("💾 Scarica Risultati Massivi")
            dm1, dm2 = st.columns(2)
            with dm1:
                st.download_button("⬇️ Scarica Tutti i Report", data=out_full, 
                                 file_name="ORZA_completi.txt", key="dm_f")
            with dm2:
                st.download_button("⬇️ Scarica Lista Date", data=out_short, 
                                 file_name="ORZA_lista_date.txt", key="dm_s")
