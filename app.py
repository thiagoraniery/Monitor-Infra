import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import unicodedata
import re
from datetime import date, timedelta
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PAGE CONFIG
# ==============================================================================
st.set_page_config(page_title="Monitor iNFRA", page_icon="🏗️", layout="wide")

if 'pagina_ativa' not in st.session_state: st.session_state.pagina_ativa = "Home"
if 'n_noticias'   not in st.session_state: st.session_state.n_noticias   = 60

# ==============================================================================
# 2. HELPERS
# ==============================================================================
def normalizar_texto(texto):
    if not isinstance(texto, str): return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def destacar_palavra(texto, termo):
    if not termo or not isinstance(texto, str): return texto
    mapa = {'a':'[aáàãâä]','e':'[eéèêë]','i':'[iíìîï]','o':'[oóòõôö]','u':'[uúùûü]','c':'[ccç]'}
    padrao = "".join(mapa.get(c, re.escape(c)) for c in normalizar_texto(termo))
    try:
        return re.sub(
            f"({padrao})",
            r'<mark style="background:rgba(247,93,0,0.18);color:#F75D00;'
            r'padding:0 3px;border-radius:2px;font-weight:600;">\1</mark>',
            texto, flags=re.IGNORECASE
        )
    except re.error:
        return texto

# ==============================================================================
# 3. CSS — IDENTIDADE MONITOR iNFRA
# Estética: editorial técnico · tipografia serifada+condensada · laranja estrutural
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Barlow:wght@300;400;500&display=swap');

:root {
    --bg-base:        #07080a;
    --bg-card:        #0e1014;
    --bg-surface:     #13161b;
    --bg-hover:       #181c22;
    --border:         #1f2430;
    --border-bright:  #2e3850;
    --orange:         #F75D00;
    --orange-dim:     rgba(247,93,0,0.12);
    --orange-border:  rgba(247,93,0,0.28);
    --orange-glow:    rgba(247,93,0,0.08);
    --text-primary:   #f0ede8;
    --text-secondary: #b8b3aa;
    --text-muted:     #6b6760;
    --text-dim:       #3a3830;
    --green:          #2d6b4a;
    --green-bright:   #3fa06d;
    --red-bright:     #c04545;
    --teal:           #1e5c5c;
    --teal-bright:    #2e9090;
}

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: var(--bg-base);
    color: var(--text-primary);
}
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 1440px; }

/* ── SIDEBAR ── */
[data-testid="stSidebarUserContent"] { padding-top: 0 !important; }
section[data-testid="stSidebar"] {
    background-color: var(--bg-base);
    border-right: 1px solid var(--border);
}
hr { margin: 1rem 0 !important; border-color: var(--border) !important; }

.sidebar-brand {
    padding: 30px 0 20px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 6px;
}
.brand-eyebrow {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.55rem;
    color: var(--orange);
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.brand-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    line-height: 1;
}
.brand-accent { color: var(--orange); }
.brand-tagline {
    font-size: 0.57rem;
    color: var(--text-muted);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-top: 5px;
}

.sidebar-label {
    font-family: 'Barlow Condensed', sans-serif;
    color: var(--text-muted);
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 18px 0 8px 0;
    display: block;
}

div.stButton > button {
    width: 100%;
    height: 2.6rem !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 2px !important;
    border: 1px solid var(--border) !important;
    transition: all 0.2s ease;
    margin-bottom: 4px !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, rgba(247,93,0,0.15) 0%, rgba(247,93,0,0.05) 100%) !important;
    border-color: var(--orange-border) !important;
    color: var(--orange) !important;
    box-shadow: 0 0 20px var(--orange-glow) !important;
}

div[data-testid="stTextInput"] > div,
div[data-testid="stMultiSelect"] > div,
div[data-testid="stDateInput"] > div {
    background-color: var(--bg-card) !important;
    border-radius: 2px !important;
    border: 1px solid var(--border) !important;
}
div[data-baseweb="input"], div[data-baseweb="select"] { background-color: transparent !important; }
span[data-baseweb="tag"] {
    background-color: rgba(247,93,0,0.2) !important;
    color: var(--orange) !important;
    border-radius: 2px !important;
}

/* ── KPI CARDS ── */
div[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 2px solid var(--orange);
    padding: 22px 26px;
    border-radius: 2px;
    box-shadow: 0 0 32px rgba(247,93,0,0.04);
}
div[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.6rem !important;
    letter-spacing: 3px;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Lora', serif !important;
    font-size: 2rem !important;
}

/* ── EXPANDER (Feed) ── */
details {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-left: 2px solid transparent !important;
    border-radius: 2px !important;
    margin-bottom: 4px !important;
    transition: all 0.18s ease;
}
details:hover {
    border-left-color: var(--orange) !important;
    background-color: var(--bg-surface) !important;
}
details[open] {
    border-left-color: var(--orange) !important;
    background-color: var(--bg-hover) !important;
}
details summary {
    padding: 12px 18px !important;
    font-size: 0.87rem !important;
    font-weight: 400 !important;
    color: #ccc8c0 !important;
    letter-spacing: 0.2px;
}

/* ── SECTION DIVIDERS ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 36px 0 20px 0;
}
.section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(247,93,0,0.4) 0%, transparent 70%);
}
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    color: var(--text-muted);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    white-space: nowrap;
}

.chart-label {
    font-family: 'Barlow Condensed', sans-serif;
    color: var(--text-muted);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
    display: block;
}

/* ── HERO STRIP ── */
.hero-strip {
    background: linear-gradient(180deg, #0c0f14 0%, var(--bg-base) 100%);
    border-bottom: 1px solid var(--border);
    padding: 36px 44px 30px 44px;
    margin: -1rem -1rem 2.5rem -1rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.hero-strip::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--orange) 45%, transparent 100%);
    opacity: 0.6;
}
.hero-strip::after {
    content: 'iNFRA';
    position: absolute;
    right: 44px; bottom: -10px;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 9rem;
    font-weight: 800;
    color: rgba(247,93,0,0.03);
    letter-spacing: -4px;
    pointer-events: none;
    line-height: 1;
}
.hero-eyebrow {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.58rem;
    color: var(--orange);
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.hero-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -1px;
}
.hero-accent {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    color: var(--orange);
    line-height: 1;
    letter-spacing: -1px;
}
.hero-sub {
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 10px;
}
.hero-right {
    text-align: right;
    font-family: 'Barlow Condensed', sans-serif;
}
.hero-count {
    font-size: 3.5rem;
    font-weight: 800;
    color: var(--orange);
    line-height: 1;
    letter-spacing: -2px;
}
.hero-count-label {
    font-size: 0.62rem;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── SETOR PILL ── */
.setor-pill {
    display: inline-block;
    background: var(--orange-dim);
    color: var(--orange);
    border: 1px solid var(--orange-border);
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 2px;
    margin-bottom: 14px;
}

/* ── ANÁLISE PAGE ── */
.analise-header {
    background: linear-gradient(135deg, #0f1218 0%, var(--bg-base) 100%);
    border: 1px solid var(--border-bright);
    border-left: 3px solid var(--orange);
    border-radius: 2px;
    padding: 34px 46px 30px 46px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}
.analise-header::after {
    content: 'ANÁLISE';
    position: absolute;
    right: 44px; top: 50%;
    transform: translateY(-50%);
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 5.5rem;
    font-weight: 800;
    color: rgba(247,93,0,0.03);
    letter-spacing: -2px;
    pointer-events: none;
}
.analise-eyebrow {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.58rem;
    color: var(--orange);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.analise-title {
    font-family: 'Lora', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.analise-sub {
    font-size: 0.77rem;
    color: var(--text-muted);
    margin-top: 9px;
    line-height: 1.8;
}

/* ── TERMÔMETROS ── */
.termo-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 26px 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.termo-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.75rem;
    color: var(--text-secondary);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.termo-value {
    font-family: 'Lora', serif;
    font-size: 3.2rem;
    font-weight: 700;
    line-height: 1;
}
.termo-sub {
    font-size: 0.7rem;
    color: var(--text-secondary);
    margin-top: 10px;
    letter-spacing: 0.3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.t-up   { color: var(--green-bright); border-top: 2px solid var(--green-bright); }
.t-down { color: var(--red-bright);   border-top: 2px solid var(--red-bright); }
.t-flat { color: var(--text-muted);   border-top: 2px solid var(--border-bright); }
.t-orange { color: var(--orange);     border-top: 2px solid var(--orange); }

/* ── SETOR CARD (Análise) ── */
.setor-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, #0b0e12 100%);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 18px 22px;
    margin-bottom: 8px;
    transition: all 0.18s ease;
}
.setor-card:hover { border-color: var(--orange-border); background-color: var(--bg-hover); }
.setor-card-name {
    font-family: 'Lora', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 3px;
}
.setor-card-stats {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.ativo-pill {
    display: inline-block;
    background: rgba(63,160,109,0.12);
    color: #3fa06d;
    border: 1px solid rgba(63,160,109,0.25);
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.54rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 1px 7px;
    border-radius: 2px;
    margin-left: 8px;
    vertical-align: middle;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(247,93,0,0.3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--orange); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. DADOS
# ==============================================================================
ARQUIVO_EXCEL = "AgenciaInfra_Historico.xlsx"

@st.cache_data(ttl=300)
def carregar_dados():
    if not os.path.exists(ARQUIVO_EXCEL):
        return pd.DataFrame()
    df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Visão Geral")
    if not df.empty:
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Data'])
        df['Título'] = df['Título'].str.replace("Agência iNFRA", "", case=False).str.strip(" -|: ")
    return df

df_bruto = carregar_dados()

# Clique no gráfico de setores → filtra
if "grafico_setores" in st.session_state and st.session_state.grafico_setores:
    selecao = st.session_state.grafico_setores.get("selection", {}).get("points", [])
    if selecao:
        setor_clicado = selecao[0]["y"]
        if st.session_state.get('setores_input', []) != [setor_clicado]:
            st.session_state.setores_input = [setor_clicado]
            st.rerun()

data_padrao_inicio = date(2026, 1, 1)
data_maxima_base   = df_bruto['Data'].max().date() if not df_bruto.empty else date.today()

if 'busca_input'  not in st.session_state: st.session_state.busca_input  = ""
if 'setores_input'not in st.session_state: st.session_state.setores_input= []
if 'data_ini'     not in st.session_state: st.session_state.data_ini     = data_padrao_inicio
if 'data_fim'     not in st.session_state: st.session_state.data_fim     = data_maxima_base

def reset_filtros():
    st.session_state.busca_input   = ""
    st.session_state.setores_input = []
    st.session_state.data_ini      = data_padrao_inicio
    st.session_state.data_fim      = data_maxima_base
    st.session_state.n_noticias    = 60

# ==============================================================================
# 5. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-eyebrow">Agência</div>
            <div class="brand-name">Monitor<span class="brand-accent">.</span>iNFRA</div>
            <div class="brand-tagline">Infraestrutura · Regulação · Mercado</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sidebar-label">Navegação</span>', unsafe_allow_html=True)
    st.button("▸  PAINEL DE NOTÍCIAS",
              on_click=lambda: st.session_state.update({"pagina_ativa": "Home"}))
    st.button("▸  ANÁLISE SETORIAL",
              on_click=lambda: st.session_state.update({"pagina_ativa": "Analise"}))

    st.divider()

    st.markdown('<span class="sidebar-label">Período de Análise</span>', unsafe_allow_html=True)
    d_inicio = st.date_input("De",  key="data_ini", format="DD/MM/YYYY",
                             min_value=date(2025,1,1), max_value=date(2026,12,31))
    d_fim    = st.date_input("Até", key="data_fim", format="DD/MM/YYYY",
                             min_value=date(2025,1,1), max_value=date(2026,12,31))

    st.divider()

    st.markdown('<span class="sidebar-label">Setor</span>', unsafe_allow_html=True)
    setores_lista = sorted(df_bruto['Categoria'].unique().tolist()) if not df_bruto.empty else []
    sel_setores = st.multiselect("Setor", key="setores_input", options=setores_lista,
                                 placeholder="Todos os setores", label_visibility="collapsed")

    st.divider()

    st.markdown('<span class="sidebar-label">Palavra-chave</span>', unsafe_allow_html=True)
    busca = st.text_input("Busca", key="busca_input",
                          placeholder="Ex: PPI, leilão, concessão...", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.button("✕  LIMPAR FILTROS", on_click=reset_filtros)

    if not df_bruto.empty:
        st.markdown(f"""
            <div style='position:fixed;bottom:14px;font-family:Barlow Condensed,sans-serif;
                        font-size:0.57rem;color:var(--text-dim);letter-spacing:2px;
                        text-transform:uppercase;'>
                BASE · {data_maxima_base.strftime('%d/%m/%Y')}
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 6. FILTRAGEM GLOBAL
# ==============================================================================
df_f = df_bruto.copy()
if not df_f.empty:
    df_f = df_f[(df_f['Data'].dt.date >= d_inicio) & (df_f['Data'].dt.date <= d_fim)]
    if sel_setores:
        df_f = df_f[df_f['Categoria'].isin(sel_setores)]
    if busca:
        busca_norm = normalizar_texto(busca)
        df_f = df_f[
            df_f['Título'].apply(lambda x: busca_norm in normalizar_texto(str(x))) |
            df_f['Conteúdo'].apply(lambda x: busca_norm in normalizar_texto(str(x)))
        ]

# ==============================================================================
# 7. HERO STRIP
# ==============================================================================
hoje_fmt = date.today().strftime("%d/%m/%Y")
st.markdown(f"""
<div class="hero-strip">
    <div>
        <div class="hero-eyebrow">Inteligência Setorial Brasileira</div>
        <div style="display:flex;align-items:baseline;gap:14px;">
            <span class="hero-title">Monitor</span>
            <span class="hero-accent">iNFRA</span>
        </div>
        <div class="hero-sub">Energia · Transportes · Saneamento · Mineração · Petróleo &amp; Gás</div>
    </div>
    <div class="hero-right">
        <div class="hero-count">{len(df_f):,}</div>
        <div class="hero-count-label">Registros · {hoje_fmt}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 8. HOME — PAINEL DE NOTÍCIAS
# ==============================================================================
if st.session_state.pagina_ativa == "Home":
    if df_f.empty:
        st.warning("Nenhum dado localizado para os filtros selecionados.")
    else:
        k1, k2, k3 = st.columns(3)
        k1.metric("Notícias no Período", f"{len(df_f):,}")
        k2.metric("Setor em Destaque", df_f['Categoria'].mode()[0])
        k3.metric("Última Atualização", df_f['Data'].max().strftime('%d/%m/%Y'))

        st.markdown("""<div class="section-header"><span class="section-title">Análise Visual</span><div class="section-line"></div></div>""", unsafe_allow_html=True)

        col_bar, col_wc = st.columns([1, 1], gap="large")

        with col_bar:
            st.markdown('<span class="chart-label">Volume por Setor</span>', unsafe_allow_html=True)
            cont = df_f['Categoria'].value_counts().reset_index()
            n = len(cont)
            cores = ['#F75D00'] + ['#1f2d45'] * max(0, n - 1)

            fig_bar = px.bar(cont, x='count', y='Categoria', orientation='h',
                             color_discrete_sequence=['#1f2d45'], text='count')
            fig_bar.update_traces(
                textposition='outside', cliponaxis=False,
                textfont=dict(size=11, color="#F75D00"),
                marker_color=cores, marker_line_width=0
            )
            fig_bar.update_layout(
                height=max(260, 70 + n * 46),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#6b6760", family="Barlow"),
                xaxis=dict(visible=False),
                yaxis=dict(title=None, autorange="reversed",
                           tickfont=dict(size=13, color="#b8b3aa"),
                           gridcolor='rgba(0,0,0,0)'),
                margin=dict(l=0, r=60, t=0, b=0), bargap=0.42,
            )
            st.plotly_chart(fig_bar, width='stretch', on_select="rerun",
                            selection_mode="points", key="grafico_setores")

        with col_wc:
            st.markdown('<span class="chart-label">Nuvem de Palavras</span>', unsafe_allow_html=True)
            texto_nuvem = " ".join(df_f['Título'].astype(str)).lower()
            stop = {"agência","infra","de","da","do","para","com","em","um","uma","o","a",
                    "os","as","que","se","no","pa","mas","na","ao","aos","diz","vai","vamos",
                    "mantém","deve","tem","sob","sobre","entre","pela","pelo","nas","nos",
                    "até","dos","das","ser","foi","está","por","pede","mais","não","mi",
                    "pode","quer","terá","ano","nova","r","bi","1","e","anm","dia","após",
                    "é","à","como","esta","estão","seu","sua","são","novo","será"}
            if len(texto_nuvem) > 20:
                cores_nuvem = LinearSegmentedColormap.from_list(
                    "infra", ["#3a2010", "#b84400", "#F75D00", "#ff9a5c", "#f0ede8"]
                )
                wc = WordCloud(
                    width=900, height=600,
                    background_color='#07080a',
                    colormap=cores_nuvem,
                    stopwords=stop, max_words=50,
                    prefer_horizontal=0.65,
                    relative_scaling=0.5, min_font_size=10
                ).generate(texto_nuvem)
                fig_wc, ax = plt.subplots(figsize=(11, 5), facecolor='#07080a')
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                fig_wc.tight_layout(pad=0)
                st.pyplot(fig_wc, width='stretch')

        st.markdown("""<div class="section-header"><span class="section-title">Feed de Notícias</span><div class="section-line"></div></div>""", unsafe_allow_html=True)

        for _, r in df_f.head(st.session_state.n_noticias).iterrows():
            data_str     = r['Data'].strftime('%d/%m/%Y') if pd.notnull(r['Data']) else "S/D"
            conteudo_raw = str(r['Conteúdo']).replace("$", r"\$").replace("•", "\n\n- ")
            if "\n" not in conteudo_raw and len(conteudo_raw) > 400:
                conteudo_raw = conteudo_raw.replace(". ", ".\n\n")
            titulo_final   = destacar_palavra(str(r['Título']), busca)
            conteudo_final = destacar_palavra(conteudo_raw, busca)

            with st.expander(f"{data_str}   ·   {str(r['Título'])}"):
                st.markdown(f'<span class="setor-pill">{r["Categoria"]}</span>', unsafe_allow_html=True)
                st.markdown(conteudo_final, unsafe_allow_html=True)
                st.link_button("Acessar matéria completa →", r['Link'])

        if len(df_f) > st.session_state.n_noticias:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([3, 1, 3])
            with c2:
                if st.button("MAIS"):
                    st.session_state.n_noticias += 60
                    st.rerun()

# ==============================================================================
# 9. ANÁLISE SETORIAL (sem IA — análise visual completa)
# ==============================================================================
elif st.session_state.pagina_ativa == "Analise":

    if df_bruto.empty:
        st.warning("Base de dados vazia.")
    else:
        hoje     = date.today()
        data_max = df_bruto['Data'].max().date()

        df_7d      = df_bruto[df_bruto['Data'].dt.date >= data_max - timedelta(days=6)]
        df_7d_ant  = df_bruto[(df_bruto['Data'].dt.date >= data_max - timedelta(days=13)) &
                               (df_bruto['Data'].dt.date <= data_max - timedelta(days=7))]
        df_30d     = df_bruto[df_bruto['Data'].dt.date >= data_max - timedelta(days=29)]
        df_30d_ant = df_bruto[(df_bruto['Data'].dt.date >= data_max - timedelta(days=59)) &
                               (df_bruto['Data'].dt.date <= data_max - timedelta(days=30))]

        def variacao(atual, anterior):
            if anterior == 0: return None, "flat"
            pct = ((atual - anterior) / anterior) * 100
            return pct, ("up" if pct > 0 else ("down" if pct < 0 else "flat"))

        n7, n7_ant   = len(df_7d), len(df_7d_ant)
        n30, n30_ant = len(df_30d), len(df_30d_ant)
        pct7, dir7   = variacao(n7, n7_ant)
        pct30, dir30 = variacao(n30, n30_ant)

        seta7 = "↑" if dir7 == "up" else ("↓" if dir7 == "down" else "→")
        pct7_txt = f"{pct7:+.0f}%" if pct7 is not None else "—"
        setor_semana = df_7d['Categoria'].mode()[0] if not df_7d.empty else "—"
        n_setores_ativos = df_7d['Categoria'].nunique() if not df_7d.empty else 0
        cor_seta = "#3fa06d" if dir7 == "up" else ("#c04545" if dir7 == "down" else "#6b6760")

        semana_str = f"{(data_max - timedelta(days=6)).strftime('%d/%m')} – {data_max.strftime('%d/%m/%Y')}"

        st.markdown(f"""
            <div class="analise-header">
                <div class="analise-eyebrow">Semana · {semana_str}</div>
                <div class="analise-title">Análise Setorial</div>
                <div class="analise-sub">
                    <b style="color:var(--text-secondary)">{n7}</b> notícias nos últimos 7 dias
                    &nbsp;<span style="color:{cor_seta};font-weight:700;">{seta7} {pct7_txt}</span>
                    vs semana anterior &nbsp;·&nbsp;
                    <b style="color:var(--text-secondary)">{n_setores_ativos}</b> setor{'es ativos' if n_setores_ativos != 1 else ' ativo'}
                    &nbsp;·&nbsp; Destaque: <b style="color:var(--orange)">{setor_semana}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── TERMÔMETROS ─────────────────────────────────────────────────────
        st.markdown("""<div class="section-header"><span class="section-title">Termômetro de Atividade</span><div class="section-line"></div></div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        def render_termo(col, label, valor, pct, direcao, sub):
            seta = "↑" if direcao == "up" else ("↓" if direcao == "down" else "→")
            cls  = f"t-{direcao}"
            pct_txt = f"{pct:+.0f}%" if pct is not None else "—"
            col.markdown(f"""
                <div class="termo-card {cls}">
                    <div class="termo-label">{label}</div>
                    <div class="termo-value">{seta} {valor}</div>
                    <div class="termo-sub">{pct_txt} vs período anterior · {sub}</div>
                </div>
            """, unsafe_allow_html=True)

        render_termo(col1, "Notícias · 7 dias",  n7,  pct7,  dir7,  "vs sem. anterior")
        render_termo(col2, "Notícias · 30 dias", n30, pct30, dir30, "vs mês anterior")

        if not df_7d.empty:
            top7   = df_7d['Categoria'].value_counts()
            top30  = df_30d['Categoria'].value_counts() if not df_30d.empty else pd.Series(dtype=int)
            setor_top  = top7.index[0]
            n_top7     = top7.iloc[0]
            n_top30    = top30.get(setor_top, 0)
            pct_s, dir_s = variacao(n_top7, n_top30 / 4 if n_top30 > 0 else 0)
            render_termo(col3, f"Líder · {setor_top[:14]}", n_top7, pct_s, dir_s, "vs média 30d")
        else:
            col3.markdown('<div class="termo-card t-flat"><div class="termo-label">Líder</div><div class="termo-value">—</div></div>', unsafe_allow_html=True)

        dias_silencio = (hoje - data_max).days
        dir_ultimo = "t-orange" if dias_silencio == 0 else ("t-flat" if dias_silencio <= 2 else "t-down")
        col4.markdown(f"""
            <div class="termo-card {dir_ultimo}">
                <div class="termo-label" style="font-size:0.75rem;color:var(--text-secondary);">Última Notícia</div>
                <div class="termo-value" style="font-size:2.2rem;">{data_max.strftime('%d/%m/%Y')}</div>
                <div class="termo-sub" style="font-size:0.78rem;color:var(--text-secondary);">{'hoje' if dias_silencio == 0 else f'há {dias_silencio} dia{"s" if dias_silencio > 1 else ""}'}</div>
            </div>
        """, unsafe_allow_html=True)

        # ── VOLUME DIÁRIO 30d ────────────────────────────────────────────────
        st.markdown("""<div class="section-header"><span class="section-title">Volume Diário · Últimos 30 Dias</span><div class="section-line"></div></div>""", unsafe_allow_html=True)

        df_30d_plot = df_30d.copy()
        df_30d_plot['Dia'] = df_30d_plot['Data'].dt.date
        vol_dia = df_30d_plot.groupby('Dia').size().reset_index(name='Qtd')
        idx_completo = pd.date_range(data_max - timedelta(days=29), data_max)
        vol_dia = vol_dia.set_index('Dia').reindex(idx_completo.date, fill_value=0).reset_index()
        vol_dia.columns = ['Dia', 'Qtd']
        vol_dia['Media7'] = vol_dia['Qtd'].rolling(7, min_periods=1).mean().round(1)

        fig_diario = go.Figure()
        fig_diario.add_trace(go.Bar(
            x=vol_dia['Dia'], y=vol_dia['Qtd'],
            marker_color=[
                '#F75D00' if v == vol_dia['Qtd'].max() else
                ('rgba(31,45,69,0.25)' if v == 0 else '#1f2d45')
                for v in vol_dia['Qtd']
            ],
            marker_line_width=0, name='Notícias/dia',
            hovertemplate='%{x|%d/%m}<br>%{y} notícias<extra></extra>',
        ))
        fig_diario.add_trace(go.Scatter(
            x=vol_dia['Dia'], y=vol_dia['Media7'],
            mode='lines', line=dict(color='#F75D00', width=1.5, dash='dot'),
            name='Média 7d',
            hovertemplate='Média 7d: %{y:.1f}<extra></extra>',
        ))
        fig_diario.update_layout(
            height=220, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#6b6760', family='Barlow'),
            xaxis=dict(title=None, tickfont=dict(size=10, color='#6b6760'),
                       gridcolor='rgba(31,36,48,0.3)', showspikes=False, tickformat='%d/%m'),
            yaxis=dict(title=None, tickfont=dict(size=10, color='#3a3830'),
                       gridcolor='rgba(31,36,48,0.3)', zeroline=False),
            legend=dict(orientation='h', x=1, xanchor='right', y=1.15,
                        font=dict(size=10, color='#6b6760'), bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=30, r=20, t=10, b=0), bargap=0.15, hovermode='closest',
        )
        st.plotly_chart(fig_diario, width='stretch')

        # ── PERFIL POR SETOR ─────────────────────────────────────────────────
        st.markdown("""<div class="section-header"><span class="section-title">Perfil por Setor</span><div class="section-line"></div></div>""", unsafe_allow_html=True)

        setores_ord = df_bruto['Categoria'].value_counts().index.tolist()
        total_base  = len(df_bruto)

        for setor in setores_ord:
            df_src    = df_bruto[df_bruto['Categoria'] == setor].sort_values('Data', ascending=False)
            df_src_7d = df_src[df_src['Data'].dt.date >= data_max - timedelta(days=6)]
            n_total   = len(df_src)
            n_recente = len(df_src_7d)
            pct_share = n_total / total_base * 100
            ultima    = df_src['Data'].max().strftime('%d/%m/%Y') if not df_src.empty else "—"
            ativo_tag = '<span class="ativo-pill">ATIVO</span>' if n_recente > 0 else ''

            with st.expander(f"{setor}   ·   {n_total} notícias   ·   última: {ultima}"):
                st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;">
                        <div>
                            <div class="setor-card-name">{setor} {ativo_tag}</div>
                            <div class="setor-card-stats">
                                {n_total} publicações · {pct_share:.1f}% da base · {n_recente} nos últimos 7 dias
                            </div>
                        </div>
                    </div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.58rem;
                                color:var(--text-dim);letter-spacing:2px;text-transform:uppercase;margin-bottom:5px;">
                        Participação na base
                    </div>
                    <div style="height:4px;background:var(--border);border-radius:2px;
                                overflow:hidden;margin-bottom:20px;">
                        <div style="height:4px;width:{min(pct_share, 100):.1f}%;
                                    background:linear-gradient(90deg,#F75D00,#FF9952);
                                    border-radius:2px;"></div>
                    </div>
                """, unsafe_allow_html=True)

                # Mini gráfico mensal
                df_m = df_src.copy()
                df_m['Mes'] = df_m['Data'].dt.to_period('M').astype(str)
                vol_m = df_m.groupby('Mes').size().reset_index(name='Qtd')

                fig_mini = go.Figure(go.Bar(
                    x=vol_m['Mes'], y=vol_m['Qtd'],
                    marker_color='#1f2d45', marker_line_width=0,
                    text=vol_m['Qtd'], textposition='outside',
                    textfont=dict(size=9, color='#F75D00'),
                    hovertemplate='%{x}<br>%{y} notícias<extra></extra>',
                ))
                fig_mini.update_layout(
                    height=140, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#6b6760', family='Barlow'),
                    xaxis=dict(tickfont=dict(size=9), gridcolor='rgba(0,0,0,0)', showspikes=False),
                    yaxis=dict(visible=False),
                    margin=dict(l=0, r=10, t=10, b=0), bargap=0.35, hovermode='closest',
                )
                st.plotly_chart(fig_mini, width='stretch')

                # Últimas 3 notícias
                st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:0.58rem;color:var(--text-dim);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Últimas publicações</div>', unsafe_allow_html=True)
                for _, r in df_src.head(3).iterrows():
                    data_r = r['Data'].strftime('%d/%m/%Y') if pd.notnull(r['Data']) else "S/D"
                    st.markdown(f"""
                        <div style="border-left:2px solid var(--orange-border);padding:6px 14px;
                                    margin-bottom:6px;font-size:0.83rem;color:#b8b3aa;">
                            <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;
                                         color:var(--text-muted);letter-spacing:1.5px;">{data_r}</span><br>
                            {str(r['Título'])}
                        </div>
                    """, unsafe_allow_html=True)
                    st.link_button("↗ Ver notícia", r['Link'], use_container_width=False)