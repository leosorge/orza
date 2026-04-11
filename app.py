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
st.caption("Generatore di date di nascita astrologicamente coerenti.")
st.divider()

# ── HELPER: FUNZIONE PER MOSTRARE IL PROFILO ──────────────────────────────────
def mostra_profilo(profilo: dict):
    """Renderizza graficamente un profilo astrologico nella UI."""
    st.subheader(f"Profilo di {profilo['nome'].upper()}")

    a_min = profilo.get("anno_min", "N/A")
    a_max = profilo.get("anno_max", "N/A")
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

    # SEZIONE KEYWORD MATCH CON LOGICA DI SICUREZZA
    with st.expander("🔍 Dettaglio keyword match (Top 3 segni)"):
        top_segni = profilo.get("top3_segni", [])
        dettagli_stat = profilo.get("match_dettagli", {})

        if not top_segni:
            st.info("Dati statistici non disponibili per questo profilo.")
        else:
            for i, (segno_k, punteggio) in enumerate(top_segni, 1):
                st.write(f"{i}. **{segno_k}** — Punteggio totale: `{punteggio}`")
                
                # Cerchiamo le parole specifiche
                parole = dettagli_stat.get(segno_k, [])
                if parole:
                    # Mostra le prime 3 con il valore statistico
                    top_3_words = parole[:3]
                    keyword_str = ", ".join([f"{w} ({s})" for w, s in top_3_words])
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*Parole chiave: {keyword_str}*")
                elif punteggio > 0:
                    st.write("&nbsp;&nbsp;&nbsp;&nbsp;*Dettaglio parole non disponibile (verificare core.py)*")
                else:
                    st.write("&nbsp;&nbsp;&nbsp;&nbsp;*Nessun match trovato per questo segno.*")

# ── SCHEDE (TAB) ──────────────────────────────────────────────────────────────
tab_singolo, tab_multi = st.tabs(["👤 Personaggio singolo", "📄 File multipli"])

# ==============================================================================
# TAB 1 — SINGOLO PERSONAGGIO
# ==============================================================================
with tab_singolo:
    with st.form("form_singolo"):
        nome = st.text_input("Nome e Cognome")
        col1, col2 = st.columns(2)
        with col1:
            eta = st.number_input("Età", min_value=1, max_value=120, value=35)
        with col2:
            st.markdown("**Range anni**")
            cy1, cy2 = st.columns(2)
            with cy1:
                anno_min = st.number_input("Da", value=datetime.now().year, key="amin_s")
            with cy2:
                anno_max = st.number_input("A", value=datetime.now().year, key="amax_s")

        descrizione = st.text_area("Descrizione del carattere", height=120)
        inviato = st.form_submit_button("✨ Genera profilo", use_container_width=True)

    if inviato:
        if not nome.strip() or not descrizione.strip():
            st.warning("Compila tutti i campi.")
        else:
            p = genera_profilo(nome.strip(), int(eta), descrizione.strip(), int(anno_min), int(anno_max))
            st.divider()
            mostra_profilo(p)

            # Download area
            t_full = formatta_profilo_testo(p)
            t_short = f"{p['nome']}, {p['data'].strftime('%d/%m/%Y')}"
            
            st.subheader("💾 Scarica Risultati")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Report Completo", t_full, f"{p['nome']}_full.txt", key="d1")
            with c2:
                st.download_button("⬇️ Nome e Data", t_short, f"{p['nome']}_data.txt", key="d2")

# ==============================================================================
# TAB 2 — FILE MULTIPLI
# ==============================================================================
with tab_multi:
    st.markdown("### 📄 Elaborazione File")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        a_min_g = st.number_input("Anno Min Globale", value=1900, key="am_g")
    with c_g2:
        a_max_g = st.number_input("Anno Max Globale", value=2026, key="ax_g")

    f_up = st.file_uploader("Carica .txt", type=["txt"], key="bulk")

    if f_up:
        t_raw = f_up.read().decode("utf-8")
        if st.button("🚀 Elabora Tutti", use_container_width=True):
            st.session_state.bulk_res = genera_profili_da_file(t_raw, int(a_min_g), int(a_max_g))

        if "bulk_res" in st.session_state:
            res = st.session_state.bulk_res
            f_txt, s_txt = "", ""
            for p in res:
                if "errore" not in p:
                    mostra_profilo(p)
                    st.divider()
                    f_txt += formatta_profilo_testo(p) + "\n" + "-"*40 + "\n"
                    s_txt += f"{p['nome']}, {p['data'].strftime('%d/%m/%Y')}\n"

            st.subheader("💾 Download")
            b1, b2 = st.columns(2)
            with b1:
                st.download_button("⬇️ Scarica Tutti (Full)", f_txt, "ORZA_full.txt", key="b1")
            with b2:
                st.download_button("⬇️ Scarica Lista (Date)", s_txt, "ORZA_date.txt", key="b2")
