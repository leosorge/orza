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
    st.subheader(f"Profilo di {profilo['nome'].upper()}")

    # Range anni di riferimento
    a_min = profilo.get("anno_min")
    a_max = profilo.get("anno_max")
    if a_min and a_max and a_min != a_max:
        range_label = f"{a_min}–{a_max}"
    elif a_min:
        range_label = str(a_min)
    else:
        range_label = "anno corrente"

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Data di nascita",      profilo["data"].strftime("%d/%m/%Y"))
    col_b.metric("Ora di nascita",        profilo["ora"])
    col_c.metric("Età",                   f"{profilo['eta']} anni")

    col_d, col_e = st.columns(2)
    col_d.metric("☀️ Segno Solare",       profilo["segno"])
    col_e.metric("⬆️ Ascendente",         profilo["ascendente"])

    col_f, col_g, col_h = st.columns(3)
    col_f.metric("Fase di vita",          profilo["fase"])
    col_g.metric("Casa dominante",        profilo["casa_dominante"])
    col_h.metric("Range riferimento",     range_label)

    with st.expander("🔍 Dettaglio keyword match"):
        for i, (segno_k, punteggio) in enumerate(profilo["top3_segni"], 1):
            st.write(f"{i}. **{segno_k}** — {punteggio} keyword")
        if profilo["top3_segni"][0][1] == 0:
            st.info(
                "Nessuna keyword riconosciuta: segno assegnato casualmente. "
                "Prova ad arricchire la descrizione con aggettivi più specifici."
            )


# ── TAB LAYOUT ────────────────────────────────────────────────────────────────

tab_singolo, tab_multi = st.tabs(["👤 Personaggio singolo", "📄 File multipli"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGOLO PERSONAGGIO
# ════════════════════════════════════════════════════════════════════════════

with tab_singolo:

    with st.form("form_singolo"):

        nome = st.text_input(
            "Nome e Cognome", placeholder="es. Marco Rossi"
        )

        col1, col2 = st.columns(2)
        with col1:
            eta = st.number_input(
                "Età", min_value=1, max_value=120, value=35, step=1
            )
        with col2:
            st.markdown("**Range anni di riferimento**")
            # Anno minimo e massimo del periodo in cui il personaggio ha quell'età
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                anno_min = st.number_input(
                    "Da (YYYY)", min_value=1, max_value=9999,
                    value=datetime.now().year,
                    step=1, key="anno_min_s",
                    help="Anno iniziale del range. Es: 1850",
                )
            with col_y2:
                anno_max = st.number_input(
                    "A (YYYY)", min_value=1, max_value=9999,
                    value=datetime.now().year,
                    step=1, key="anno_max_s",
                    help="Anno finale del range. Uguale al precedente = anno fisso.",
                )

        descrizione = st.text_area(
            "Descrizione del carattere",
            placeholder=(
                "es. persona determinata, ambiziosa, disciplinata e seria "
                "nel lavoro, a volte fredda ma molto perseverante..."
            ),
            height=120,
        )

        inviato = st.form_submit_button(
            "✨ Genera profilo", use_container_width=True
        )

# --- QUESTO È FUORI DAL FORM ---
    st.write("---") # Una linea sottile di separazione
    st.markdown("### 💡 Esempio di Input")
    st.code(
        "Elena Voss\n"
        "34\n"
        "1880–1910\n"
        "persona intensa, misteriosa, determinata e tenace, con un lato oscuro e passionale",
        language="text"
    )
    
    if inviato:
        if not nome.strip():
            st.warning("Inserisci il nome del personaggio.")
            st.stop()
        if not descrizione.strip():
            st.warning("Inserisci una descrizione del carattere.")
            st.stop()
        if anno_min > anno_max:
            st.warning("L'anno iniziale non può essere maggiore dell'anno finale.")
            st.stop()

        profilo = genera_profilo(
            nome        = nome.strip(),
            eta         = int(eta),
            descrizione = descrizione.strip(),
            anno_min    = int(anno_min),
            anno_max    = int(anno_max),
        )

        st.divider()
        mostra_profilo(profilo)

        testo_out = formatta_profilo_testo(profilo)
        nome_file = profilo["nome"].replace(" ", "_").lower() + "-astro.txt"
        st.download_button(
            label               = "⬇️ Scarica profilo (.txt)",
            data                = testo_out,
            file_name           = nome_file,
            mime                = "text/plain",
            use_container_width = True,
        )


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FILE MULTIPLI
# ════════════════════════════════════════════════════════════════════════════

with tab_multi:
    st.markdown("### 📄 Caricamento Multiplo")
    st.info("Formato atteso: Nome, Età, Anno, Descrizione separati da === (vedi esempio nel Tab 1)")

    # 1. Range globale come fallback
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        anno_min_glob = st.number_input("Anno Min Globale", value=2000, key="min_g")
    with col_g2:
        anno_max_glob = st.number_input("Anno Max Globale", value=2026, key="max_g")

    # 2. Uploader
    file_caricato = st.file_uploader("Carica il file .txt", type=["txt"], key="uploader_bulk")

    if file_caricato:
        testo_raw = file_caricato.read().decode("utf-8")
        
        if st.button("✨ Avvia Elaborazione Massiva", use_container_width=True):
            # Eseguiamo il calcolo e salviamo subito nello stato
            risultati = genera_profili_da_file(
                testo_raw, 
                anno_min_default=int(anno_min_glob), 
                anno_max_default=int(anno_max_glob)
            )
            st.session_state['risultati_orza'] = risultati
            st.success(f"Elaborati {len(risultati)} personaggi!")

        # 3. Se abbiamo risultati in memoria, mostriamo i download
        if 'risultati_orza' in st.session_state:
            res = st.session_state['risultati_orza']
            
            # Prepariamo i due testi
            output_full = ""
            output_lista = ""
            
            for p in res:
                if "errore" not in p:
                    # File 1: Dettagliato
                    output_full += formatta_profilo_testo(p) + "\n" + "-"*40 + "\n"
                    # File 2: Sintetico (Nome, Data)
                    data_formattata = p["data"].strftime("%d/%m/%Y")
                    output_lista += f"{p['nome']}, {data_formattata}\n"
            
            st.divider()
            st.subheader("💾 Download Risultati")
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="⬇️ Scarica Profili Completi",
                    data=output_full,
                    file_name="ORZA_completo.txt",
                    mime="text/plain",
                    key="dl_full"
                )
            with c2:
                # Questo è il tasto che ci interessa
                st.download_button(
                    label="⬇️ Scarica Lista (Nome, Data)",
                    data=output_lista,
                    file_name="ORZA_lista_date.txt",
                    mime="text/plain",
                    key="dl_short"
                )
