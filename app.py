import streamlit as st
import pandas as pd
import plotly.express as px
import os
import unicodedata
import re 
from datetime import datetime, date, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
import google.generativeai as genai
import json

CHAVE_API = st.secrets["GEMINI_API_KEY"]  
genai.configure(api_key=CHAVE_API)
modelo_ia = genai.GenerativeModel('gemini-3-flash-preview') 

@st.cache_data(ttl=86400)
def gerar_resumo_consolidado_ia(categoria, lista_noticias, data_ref):
    # Prepara o lote de notícias para a IA
    texto_noticias = "\n".join([f"- {t}" for t in lista_noticias])
    
    prompt = f"""
    Você é um Analista Sênior de Inteligência Setorial.
    Analise o seguinte compilado de notícias da semana do setor de {categoria}.
    
    TÍTULOS:
    {texto_noticias}

    MISSÃO:
    Escreva um parágrafo único, denso e fluido (estilo briefing executivo) que conecte essas pautas. 
    Não use bullet points. Foque em tendências e no panorama geral. 
    O texto deve ser profissional e direto para uma diretoria.

    SAÍDA:
    Retorne apenas o texto do parágrafo, sem comentários adicionais.
    """

    for tentativa in range(3):
        try:
            resposta = modelo_ia.generate_content(prompt)
            return resposta.text.strip()
        except Exception as e:
            if "429" in str(e):
                time.sleep(20) # Espera se a cota bater
            else:
                return "Análise setorial em processamento. Por favor, atualize em instantes."
    return "Serviço de inteligência temporariamente indisponível."

# ==============================================================================
# 1. CONFIGURAÇÃO E ESTILO (UI/UX EXECUTIVA)
# ==============================================================================
st.set_page_config(page_title="Monitor iNFRA", page_icon="⚡", layout="wide")

# Inicialização de variáveis de estado
if 'pagina_ativa' not in st.session_state: st.session_state.pagina_ativa = "Home"
if 'n_noticias' not in st.session_state: st.session_state.n_noticias = 60

def normalizar_texto(texto):
    if not isinstance(texto, str): return ""
    texto_norm = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto_norm.lower()

def destacar_palavra(texto, termo_busca):
    if not termo_busca or not isinstance(texto, str): return texto
    mapa = {'a': '[aáàãâä]', 'e': '[eéèêë]', 'i': '[iíìîï]', 'o': '[oóòõôö]', 'u': '[uúùûü]', 'c': '[ccç]'}
    padrao = "".join(mapa.get(c, re.escape(c)) for c in normalizar_texto(termo_busca))
    try:
        return re.sub(f"({padrao})", r'<b style="color: #F75D00; background-color: rgba(247, 93, 0, 0.2); padding: 0 2px; border-radius: 3px;">\1</b>', texto, flags=re.IGNORECASE)
    except: return texto

st.markdown(""" 
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000000; }
    
    /* AJUSTE DE TOPO: Aumentado para 2rem para não cortar o título */
    .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; }
    
    /* AJUSTE SIDEBAR: Compactação total para caber os botões */
    [data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
    section[data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #262730; }
    
    /* Linhas divisórias mais finas para ganhar espaço */
    hr { margin: 0.8rem 0px !important; }

    .sidebar-label { 
        color: #F75D00; 
        font-size: 0.85rem; 
        font-weight: 700; 
        text-transform: uppercase; 
        margin-bottom: 4px; 
        margin-top: 5px; 
        letter-spacing: 0.5px; 
    }

    div.stButton > button { 
        height: 3rem !important; /* Reduzido levemente de 3.5 para 3.0 */
        font-size: 0.95rem !important; 
        background-color: #1c1f26 !important; 
        color: #ffffff !important; 
        border-radius: 8px !important; 
        border: 1px solid #2d303e !important; 
        font-weight: 600 !important; 
        transition: 0.2s ease; 
        margin-bottom: 2px !important; 
    }
    div.stButton > button:hover { background-color: #F75D00 !important; border-color: #F75D00 !important; }

    /* Unifica o fundo de TODOS os campos: Texto, Multiselect e Data */
    div[data-testid="stTextInput"] > div, 
    div[data-testid="stMultiSelect"] > div, 
    div[data-testid="stDateInput"] > div {
        background-color: #1c1f26 !important;
        border-radius: 8px !important;
        border: 1px solid #2d303e !important;
    }

    /* Garante que o interior dos campos seja transparente para não chocar as cores */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: transparent !important;
    }
    
    /* Melhora a visibilidade do texto dentro do multiselect */
    span[data-baseweb="tag"] {
        background-color: #2d303e !important;
        color: #ffffff !important;
    }

    div[data-testid="metric-container"] {
        background-color: #1c1f26; border: 1px solid #2d303e; padding: 15px;
        border-radius: 12px; border-left: 5px solid #F75D00;
    }
    
    .main-title-container { 
        display: flex; 
        align-items: flex-end; 
        justify-content: center; 
        margin-bottom: 1.5rem; 
        margin-top: 0.5rem; /* Adicionado margem para o título não bater no teto */
    }
    
    .title-monitor { font-weight: 700; font-size: 3rem; color: #ffffff; margin-right: 1rem; line-height: 1; }
    .infra-i-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 3rem; margin-right: 0.1rem; }
    .infra-i-dot { width: 0.5rem; height: 0.5rem; background-color: #F75D00; border-radius: 50%; margin-bottom: 0.2rem; }
    .infra-i-body { width: 0.5rem; height: 2rem; background-color: #ffffff; }
    .title-nfra { font-weight: 700; font-size: 3rem; color: #F75D00; line-height: 1; }
    
    .chart-title { color: #F75D00; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True) 

# ==============================================================================
# 2. CARREGAMENTO E DADOS
# ==============================================================================
ARQUIVO_EXCEL = "AgenciaInfra_Historico.xlsx"

@st.cache_data(ttl=300)
def carregar_dados():
    if not os.path.exists(ARQUIVO_EXCEL): return pd.DataFrame()
    df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Visão Geral")
    if not df.empty:
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Título'] = df['Título'].str.replace("Agência iNFRA", "", case=False).str.strip(" -|: ")
    return df

df_bruto = carregar_dados() 

if "grafico_setores" in st.session_state and st.session_state.grafico_setores:
    selecao = st.session_state.grafico_setores.get("selection", {}).get("points", [])
    if selecao:
        setor_clicado = selecao[0]["y"]
        # Se o que foi clicado for diferente do que está no filtro, atualiza e recarrega
        if st.session_state.setores_input != [setor_clicado]:
            st.session_state.setores_input = [setor_clicado]
            st.rerun() 

# CONFIGURAÇÃO DE DATAS
data_padrao_inicio = date(2026, 1, 1)
data_maxima_base = df_bruto['Data'].max().date() if not df_bruto.empty else date.today()
data_limite_2025 = date(2025, 1, 1)
data_limite_2026 = date(2026, 12, 31)

if 'busca_input' not in st.session_state: st.session_state.busca_input = ""
if 'setores_input' not in st.session_state: st.session_state.setores_input = []
if 'data_ini' not in st.session_state: st.session_state.data_ini = data_padrao_inicio
if 'data_fim' not in st.session_state: st.session_state.data_fim = data_maxima_base

def reset_filtros():
    st.session_state.busca_input = ""
    st.session_state.setores_input = []
    st.session_state.data_ini = data_padrao_inicio
    st.session_state.data_fim = data_maxima_base
    st.session_state.n_noticias = 60

# ==============================================================================
# 3. SIDEBAR (COMPACTADA)
# ==============================================================================
with st.sidebar:
    # --- BLOCO 1: NAVEGAÇÃO ---
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-label">Navegação</p>', unsafe_allow_html=True)
    st.button("📊 PAINEL DE NOTÍCIAS", on_click=lambda: st.session_state.update({"pagina_ativa": "Home", "n_noticias": 60}))
    st.button("📋 BOLETIM SEMANAL", on_click=lambda: st.session_state.update({"pagina_ativa": "Boletim"}))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- BLOCO 2: PERÍODO ---
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-label">Período de Análise</p>', unsafe_allow_html=True)
    d_inicio = st.date_input("De", key="data_ini", format="DD/MM/YYYY", min_value=data_limite_2025, max_value=data_limite_2026)
    d_fim = st.date_input("Até", key="data_fim", format="DD/MM/YYYY", min_value=data_limite_2025, max_value=data_limite_2026)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOCO 3: SEGMENTAÇÃO ---
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-label">Setores</p>', unsafe_allow_html=True)
    setores_lista = sorted(df_bruto['Categoria'].unique().tolist()) if not df_bruto.empty else []
    sel_setores = st.multiselect("Setores", key="setores_input", options=setores_lista, placeholder="Todos", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOCO 4: BUSCA ---
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-label">Busca por Palavra</p>', unsafe_allow_html=True)
    busca = st.text_input("Busca", key="busca_input", placeholder="Ex: PPI, Leilão...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botão de Reset 
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🗑️ LIMPAR FILTROS", on_click=reset_filtros)

# FILTRAGEM
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
# 4. LOGO iNFRA
# ==============================================================================
st.markdown("""<div class="main-title-container"><span class="title-monitor">Monitor</span><div class="infra-i-wrapper"><div class="infra-i-dot"></div><div class="infra-i-body"></div></div><span class="title-nfra">NFRA</span></div>""", unsafe_allow_html=True)

# ==============================================================================
# 5. LÓGICA DE TELAS
# ==============================================================================
if st.session_state.pagina_ativa == "Home":
    if df_f.empty:
        st.warning("Nenhum dado localizado para os filtros selecionados.")
    else:
        # KPIs
        k1, k2, k3 = st.columns(3)
        k1.metric("Volume no Período", len(df_f))
        k2.metric("Setor em Destaque", df_f['Categoria'].mode()[0] if not df_f.empty else "-")
        k3.metric("Última atualização", df_f['Data'].max().strftime('%d/%m/%Y'))

        st.divider()

        # Insights Gráficos
        st.markdown("<br>", unsafe_allow_html=True)
        col_bar, col_wc = st.columns(2)

        with col_bar:
            st.markdown('<p class="chart-title">Volume por Categoria</p>', unsafe_allow_html=True)
            
            # 1. Preparação dos Dados
            cont_cat = df_f['Categoria'].value_counts().reset_index()
            # No Streamlit mais novo o reset_index gera colunas 'Categoria' e 'count'
            
            # 2. Criação do Gráfico com o parâmetro 'text'
            fig_freq = px.bar( 
                cont_cat, 
                x='count', 
                y='Categoria', 
                orientation='h', 
                color_discrete_sequence=['#F75D00'],
                text='count'  # <--- Isso ativa os números
            )
            
            # 3. Estilização dos Números (fora da barra, cinza e sem negrito)
            fig_freq.update_traces(
                textposition='outside', 
                cliponaxis=False,
                textfont=dict(size=11, color="#9da1ad") # Cor cinza para não "gritar" no layout
            )
            
            # 4. Layout (Nomes dos setores maiores e fundo transparente)
            fig_freq.update_layout(
                height=150 + (len(cont_cat) * 35) if len(cont_cat) < 10 else 450, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="white"), 
                xaxis=dict(visible=False), 
                yaxis=dict(
                    title=None, 
                    autorange="reversed",
                    tickfont=dict(size=16) # Nomes dos setores bem legíveis
                ),
                margin=dict(l=0, r=50, t=0, b=0), # Margem direita maior para o número não cortar
                bargap=0.4
            )
            
            # 5. Renderização com a KEY para o filtro funcionar
            st.plotly_chart(
                fig_freq, 
                width='stretch', 
                on_select="rerun", 
                selection_mode="points", 
                key="grafico_setores"
            )

        with col_wc:
            st.markdown('<p class="chart-title">Nuvem de palavras</p>', unsafe_allow_html=True)
            texto_nuvem = " ".join(df_f['Título'].astype(str)).lower()
            ignore = {"agência", "infra", "de", "da", "do", "para", "com", "em", "um", "uma", "o", "a", "os", "as", "que", "se", "no", "pa", "mas", "na", "ao", "aos", "diz", "vai", "vamos", "mantém", "deve", "tem", "sob", "sobre", "entre", "pela", "pelo", "nas", "nos", "até", "dos", "das", "ser", "foi", "está", "por", "pede", "mais", "não", "mi", "pode", "quer", "terá", "ano", "nova", "r", "bi", "1", "e", "anm", "dia", "após", "é", "à", "como", "esta", "estão"}
            if len(texto_nuvem) > 10:
                wc = WordCloud(width=800, height=400, background_color='#000000', colormap='Oranges', stopwords=ignore, max_words=50, prefer_horizontal=1.0).generate(texto_nuvem)
                fig_wc, ax = plt.subplots(figsize=(10, 5), facecolor='#000000')
                ax.imshow(wc, interpolation='bilinear'); ax.axis("off")
                st.pyplot(fig_wc, width='stretch')

        st.divider()
        st.markdown('<p class="chart-title">Feed de Notícias Recentes</p>', unsafe_allow_html=True)
        
        for _, r in df_f.head(st.session_state.n_noticias).iterrows():
            data_str = r['Data'].strftime('%d/%m/%Y') if pd.notnull(r['Data']) else "S/D"
            conteudo_raw = str(r['Conteúdo']).replace("$", r"\$").replace("•", "\n\n- ")
            if "\n" not in conteudo_raw and len(conteudo_raw) > 400:
                conteudo_raw = conteudo_raw.replace(". ", ".\n\n")

            titulo_final = destacar_palavra(r['Título'], busca)
            conteudo_final = destacar_palavra(conteudo_raw, busca)
            
            with st.expander(f" {data_str} | {titulo_final}"):
                st.markdown(f"**Setor:** <span style='color:#F75D00;'>{r['Categoria']}</span>", unsafe_allow_html=True)
                st.markdown(conteudo_final, unsafe_allow_html=True)
                st.link_button("Acessar Matéria Completa", r['Link'])
        
        if len(df_f) > st.session_state.n_noticias:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("CARREGAR MAIS NOTÍCIAS"):
                st.session_state.n_noticias += 60
                st.rerun()

# ==============================================================================
# 5. TELA: BOLETIM SEMANAL (DIFERENCIAL ESTRATÉGICO)
# ==============================================================================
elif st.session_state.pagina_ativa == "Boletim":
    # 1. Filtro dos últimos 7 dias
    d_max = df_bruto['Data'].max().date()
    d_ini_sem = d_max - timedelta(days=7)
    df_s = df_bruto[df_bruto['Data'].dt.date >= d_ini_sem]

    st.markdown(f"""
        <div style='background: linear-gradient(90deg, #1c1f26 0%, #000000 100%); padding: 40px; border-radius: 15px; border-left: 6px solid #F75D00; margin-bottom: 30px;'>
            <h1 style='margin:0; color:#ffffff; font-size:2.5rem; font-weight:800;'>Relatório Semanal</h1>
            <p style='font-size:1.1rem; color:#9da1ad; margin-top: 5px;'>Análise Consolidada: <b>{d_ini_sem.strftime('%d/%m/%Y')}</b> a <b>{d_max.strftime('%d/%m/%Y')}</b></p>
        </div>
    """, unsafe_allow_html=True)

    if df_s.empty:
        st.warning("Sem movimentações registradas nos últimos 7 dias.")
    else:
        hoje_id = date.today().strftime("%Y-%m-%d")
        
        with st.spinner("🧠 Redigindo análise executiva..."):
            for cat in sorted(df_s['Categoria'].unique()):
                df_cat = df_s[df_s['Categoria'] == cat]
                titulos_do_setor = df_cat['Título'].tolist()
                
                # CHAMADA DA IA 
                resumo_executivo = gerar_resumo_consolidado_ia(cat, titulos_do_setor, hoje_id)

                # Design do Cabeçalho
                st.markdown(f"""
                    <div style='margin-top: 40px; border-bottom: 2px solid #F75D00; width: fit-content; padding-right: 30px;'>
                        <h2 style='color:#ffffff; margin:0; font-size:1.8rem; text-transform: uppercase;'>{cat}</h2>
                    </div>
                """, unsafe_allow_html=True)

                # Box do Texto Fluido 
                links_fontes = " ".join([
    f"<a href='{r.Link}' target='_blank' title='{r.Título}' style='text-decoration:none; margin-right:5px; cursor:help;'>🔗</a>" 
    for r in df_cat.itertuples()
])  
                st.markdown(f"""
                    <div style='background-color: #16191f; padding: 25px; border-radius: 0 0 12px 12px; border: 1px solid #2d303e; border-top: none;'>
                        <div style='color: #e0e0e0; font-size: 1.15rem; line-height: 1.8; text-align: justify; font-weight: 300;'>
                            {resumo_executivo}
                        </div>
                        <div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid #262730; font-size: 0.8rem; color: #5d6370;'>
                            FONTES: {links_fontes}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)  