import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import sqlite3
import os
import plotly.graph_objects as go

st.set_page_config(
    page_title="Servidor KES | Painel",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #1a1f2e;
    border: 1px solid #2D2D3B;
    border-radius: 10px;
    padding: 15px 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-card_horas, .st-key-card_perfil, .st-key-card_eficiencia, .st-key-card_demandas {
    background-color: #161b26;
    border-radius: 12px;
    padding: 20px 15px 12px 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-card_tendencia {
    background-color: #161b26;
    border-radius: 12px;
    padding: 20px 15px 10px 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-visao_integrada {
    background-color: #161b26;
    border-radius: 12px;
    padding: 20px 15px 70px 15px;
    min-height: 480px
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-card_ranking_equip {
    background-color: #161b26;
    border-radius: 12px;
    padding: 20px 15px 30px 15px;
    min-height: 480px
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-card_mapeamento {
    background-color: #161b26;
    border-radius: 12px;
    padding: 20px 15px 70px 15px;
    min-height: 480px
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-visao_negocios {
    background-color: #161b26;
    border-radius: 12px;
    padding: 20px 15px 12px 15px;
}
</style>
""", unsafe_allow_html=True)

# Cabeçalho principal
st.title("Painel de Gestão - KES")
# ==========================================
# 1. CONEXÃO E COLETA DE OPÇÕES PARA OS FILTROS
# ==========================================
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(DIRETORIO_ATUAL, '..', 'banco_local', 'banco_kes.db')

try:
    conn = sqlite3.connect(CAMINHO_BANCO)
    
    # Busca localizações e tipos únicos direto da tabela KES
    lista_localizacoes = ["Todas"] + [
        row[0] for row in conn.execute("SELECT DISTINCT localizacao FROM chamados_itsm WHERE localizacao IS NOT NULL AND localizacao != '' ORDER BY localizacao").fetchall()
    ]
    
    lista_tipos = ["Todos"] + [
        row[0] for row in conn.execute("SELECT DISTINCT tipo_chamado FROM chamados_itsm WHERE tipo_chamado IS NOT NULL AND tipo_chamado != '' ORDER BY tipo_chamado").fetchall()
    ]
    
except Exception as e:
    st.error(f"⚠️ Erro ao conectar ao banco para gerar filtros: {e}")
    lista_localizacoes, lista_tipos = ["Todas"], ["Todos"]
# Atenção: NÃO fechamos a conexão (conn.close()) aqui, pois vamos usá-la no passo 4.

# ==========================================
# 2. BARRA LATERAL (SIDEBAR) E OS FILTROS
# ==========================================
st.sidebar.header("🔍 Filtros Globais")
st.sidebar.markdown("Filtros aplicados aos dados do ITSM KES.")

filtro_local = st.sidebar.selectbox("Localização", lista_localizacoes)
filtro_tipo = st.sidebar.selectbox("Tipo de Chamado", lista_tipos)
filtro_data = st.sidebar.date_input("Período (Data de Fechamento)", []) 

# ==========================================
# 3. A CONSTRUÇÃO DA QUERY DINÂMICA
# ==========================================
query_base = "SELECT * FROM chamados_itsm WHERE 1=1"
condicoes = []
parametros = []

if filtro_local != "Todas":
    condicoes.append("localizacao = ?")
    parametros.append(filtro_local)
    
if filtro_tipo != "Todos":
    condicoes.append("tipo_chamado = ?")
    parametros.append(filtro_tipo)

if condicoes:
    query_base += " AND " + " AND ".join(condicoes)

# ==========================================
# 4. EXECUTANDO A BUSCA CIRÚRGICA
# ==========================================
try:
    # 1. Puxa os dados com base nos dropdowns textuais
    df_chamados = pd.read_sql_query(query_base, conn, params=parametros)
    
    # 2. Filtro de Datas usando Inteligência do Pandas
    if len(filtro_data) == 2 and not df_chamados.empty:
        data_inicio, data_fim = filtro_data
        
        # Converte a string "07/08/2026 17:23" do banco para formato de data entendível pelo Python
        df_chamados['data_temp'] = pd.to_datetime(df_chamados['data_fechamento'], format='%d/%m/%Y %H:%M', errors='coerce')
        
        # Corta a tabela mantendo só o que está dentro do calendário
        df_chamados = df_chamados[(df_chamados['data_temp'].dt.date >= data_inicio) & (df_chamados['data_temp'].dt.date <= data_fim)]
        
        # Remove a coluna temporária para manter o dataframe limpo
        df_chamados = df_chamados.drop(columns=['data_temp'])

except Exception as e:
    st.error(f"⚠️ Erro ao executar a busca otimizada no banco: {e}")
    df_chamados = pd.DataFrame() # Tabela vazia como backup em caso de erro

finally:
    # Agora sim, com todos os dados salvos no Pandas, fechamos o banco de dados.
    if 'conn' in locals():
        conn.close()
        
# ==========================================
# A PARTIR DAQUI COMEÇAM AS SUAS ABAS NORMAIS
# ==========================================
aba1, aba2, aba3, aba4 = st.tabs(["SERVICE DESK", "GESTÃO DE MUDANÇAS", "INFRAESTRUTURA", "TECNOLOGIA OPERACIONAL"])

# ==========================================
# ABA 1: VISÃO GERAL (O seu código original de gráficos)
# ==========================================
with aba1:
    # 1. CABEÇALHO ELEGANTE
    st.markdown("### DESEMPENHO GERAL – REQUISIÇÕES E INCIDENTES")
    # ==========================================
    # ESTRUTURA DA TELA: 1ª LINHA (3 GRÁFICOS)
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h5 style='text-align: center; color: #E0E0E0;'>CHAMADOS POR PERÍODO</h5>", unsafe_allow_html=True)

        if not df_chamados.empty:
            df_aberturas = df_chamados.dropna(subset=['data_abertura']).copy()
            df_fechamentos = df_chamados.dropna(subset=['data_fechamento']).copy()
            
            df_aberturas['data_abertura_dt'] = pd.to_datetime(df_aberturas['data_abertura'], format='%d/%m/%Y %H:%M', errors='coerce')
            df_fechamentos['data_fechamento_dt'] = pd.to_datetime(df_fechamentos['data_fechamento'], format='%d/%m/%Y %H:%M', errors='coerce')
            
            # 1. INTELIGÊNCIA DE TEMPO: Analisa o filtro da barra lateral
            agrupamento_diario = False
            if 'filtro_data' in locals() and len(filtro_data) == 2:
                if (filtro_data[1] - filtro_data[0]).days <= 31:
                    agrupamento_diario = True # Se o filtro for curto, quebra por dia
                    
            # 2. Extrai a data baseada na inteligência de tempo
            if agrupamento_diario:
                df_aberturas['periodo'] = df_aberturas['data_abertura_dt'].dt.date
                df_fechamentos['periodo'] = df_fechamentos['data_fechamento_dt'].dt.date
            else:
                # Arredonda para o mês (ex: transforma 15/08/2026 em 01/08/2026 para agrupar)
                df_aberturas['periodo'] = df_aberturas['data_abertura_dt'].dt.to_period('M').dt.to_timestamp().dt.date
                df_fechamentos['periodo'] = df_fechamentos['data_fechamento_dt'].dt.to_period('M').dt.to_timestamp().dt.date
                
            # 3. Contagens
            contagem_criados = df_aberturas['periodo'].value_counts().reset_index()
            contagem_criados.columns = ['Periodo', 'Criados']
            
            contagem_fechados = df_fechamentos['periodo'].value_counts().reset_index()
            contagem_fechados.columns = ['Periodo', 'Fechados']
            
            # Junta os dados e ordena cronologicamente
            df_periodo = pd.merge(contagem_criados, contagem_fechados, on='Periodo', how='outer').fillna(0)
            df_periodo = df_periodo.sort_values('Periodo', ascending=True) # O mais antigo embaixo, mais novo em cima
            
            # 4. Criação dos Rótulos Bonitos para o Eixo Y
            if agrupamento_diario:
                df_periodo['Eixo_Y'] = pd.to_datetime(df_periodo['Periodo']).dt.strftime('%d/%m')
            else:
                meses_pt = {1:'JAN', 2:'FEV', 3:'MAR', 4:'ABR', 5:'MAI', 6:'JUN', 7:'JUL', 8:'AGO', 9:'SET', 10:'OUT', 11:'NOV', 12:'DEZ'}
                df_periodo['Eixo_Y'] = pd.to_datetime(df_periodo['Periodo']).dt.month.map(meses_pt) + "/" + pd.to_datetime(df_periodo['Periodo']).dt.year.astype(str)

            # 5. Matemática das Porcentagens e Melt
            df_periodo['pct_fechados'] = df_periodo.apply(
                lambda row: round((row['Fechados'] / row['Criados']) * 100, 1) if row['Criados'] > 0 else 0, axis=1
            )
            
            df_melt = pd.melt(df_periodo, id_vars=['Eixo_Y', 'pct_fechados'], value_vars=['Criados', 'Fechados'], var_name='Status', value_name='Quantidade')
            
            # Texto dentro da barra igual ao Book (Ex: 2246 - (100%))
            df_melt['texto_label'] = df_melt.apply(
                lambda row: f"{int(row['Quantidade'])} - (100%)" if row['Status'] == 'Criados' 
                else f"{int(row['Quantidade'])} - ({row['pct_fechados']}%)", axis=1
            )
            
            # 6. Desenha o Gráfico Plotly
            fig1 = px.bar(
                df_melt, 
                y="Eixo_Y", 
                x="Quantidade", 
                color="Status",
                orientation='h', 
                barmode='group',
                text="texto_label",
                color_discrete_map={"Criados": "#0033cc", "Fechados": "#b3cce6"}
            )
            
            fig1.update_traces(
                textposition='outside', 
                textfont=dict(color='#E0E0E0', size=11),
                marker_line_width=0,
                cliponaxis=False
            )
            
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=70, t=10, b=30), height=150,
                xaxis=dict(showgrid=False, visible=False), 
                yaxis=dict(showgrid=False, title="", type='category', tickfont=dict(size=11, color='#A0A0B0')), 
                legend=dict(
                    orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5,
                    title="", font=dict(color='#A0A0B0')
                )
            )
            
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Nenhum dado encontrado.")

    with col2:
        st.markdown("<h5 style='text-align: center; color: #E0E0E0;'>CHAMADOS: REQUESTIA / EVENTOS</h5>", unsafe_allow_html=True)
        st.info("Aguardando Regra de Negócio: Como diferenciar Requestia de Eventos?")

    with col3:
        st.markdown("<h5 style='text-align: center; color: #E0E0E0;'>SLA DE RESOLUÇÃO</h5>", unsafe_allow_html=True)
        st.info("Aguardando Regra de Negócio: Como calcular SLA Fora do Prazo?")

        
with aba2:
    pass
with aba3:
    pass