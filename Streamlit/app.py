import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="🌱 Dashboard CEPEA - Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #4ECDC4;
        font-weight: 600;
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #4ECDC4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    df = pd.read_csv("cepea_dados_3.csv")
    
    if 'data' not in df.columns:
        df['data'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str) + '-01')
    
    np.random.seed(42)
    df['volume'] = np.random.randint(1000, 10000, len(df))
    df['lucro'] = df['preco'] * df['volume'] * 0.1
    
    return df

df = carregar_dados()

st.markdown('<h1 class="main-header">🌱 DASHBOARD CEPEA ANALYTICS</h1>', unsafe_allow_html=True)
st.markdown("### *Análise Inteligente de Commodities Agrícolas* 📈")

with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h2>🎛️ Painel de Controle</h2>
        <p>Filtre os dados conforme sua análise</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.header("🔍 Filtros Avançados")
    
    produtos = st.multiselect(
        "**🌾 Commodities**",
        df['commodity'].unique(),
        default=df['commodity'].unique(),
        help="Selecione uma ou mais commodities"
    )
    
    regioes = st.multiselect(
        "**🗺️ Regiões**",
        df['regiao'].unique(),
        default=df['regiao'].unique(),
        help="Selecione as regiões de interesse"
    )
    
    anos = st.slider(
        "**📅 Período de Análise**",
        int(df['ano'].min()),
        int(df['ano'].max()),
        (int(df['ano'].min()), int(df['ano'].max())),
        help="Selecione o intervalo de anos"
    )
    
    tipo_analise = st.selectbox(
        "**📊 Tipo de Análise**",
        ["Análise Completa", "Tendências", "Comparativo", "Performance"]
    )

df_filtrado = df[
    (df['commodity'].isin(produtos)) &
    (df['regiao'].isin(regioes)) &
    (df['ano'] >= anos[0]) &
    (df['ano'] <= anos[1])
]

st.markdown("## 📊 Métricas Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    preco_medio = df_filtrado['preco'].mean()
    st.metric(
        label="💰 Preço Médio",
        value=f"R$ {preco_medio:,.2f}"
    )

with col2:
    total_commodities = df_filtrado['commodity'].nunique()
    st.metric(
        label="🌾 Commodities",
        value=total_commodities
    )

with col3:
    volume_total = df_filtrado['volume'].sum()
    st.metric(
        label="📦 Volume Total",
        value=f"{volume_total:,.0f}"
    )

with col4:
    regioes_ativas = df_filtrado['regiao'].nunique()
    st.metric(
        label="🏙️ Regiões Ativas",
        value=regioes_ativas
    )

st.markdown('<div class="section-header">📈 Análise de Tendências</div>', unsafe_allow_html=True)

col1, _ = st.columns([2, 1])

with col1:
    fig_tendencia = px.line(
        df_filtrado.groupby(['data', 'commodity'])['preco'].mean().reset_index(),
        x='data',
        y='preco',
        color='commodity',
        title='📈 Evolução Temporal de Preços',
        template='plotly_white',
        height=400
    )
    fig_tendencia.update_layout(
        hovermode='x unified',
        showlegend=True,
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        font=dict(size=12)
    )
    st.plotly_chart(fig_tendencia, use_container_width=True)

st.markdown('<div class="section-header">📊 Análise Comparativa</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig_box = px.box(
        df_filtrado,
        x='commodity',
        y='preco',
        color='commodity',
        title='📦 Distribuição de Preços por Commodity',
        template='plotly_white',
        height=400
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    volume_por_commodity = df_filtrado.groupby('commodity')[['lucro']].sum().reset_index()
    
    fig_barras = go.Figure()
    fig_barras.add_trace(go.Bar(
        name='Lucro',
        x=volume_por_commodity['commodity'],
        y=volume_por_commodity['lucro'],
        marker_color='#FF6B6B'
    ))
    
    fig_barras.update_layout(
        title='💰 Lucro por Commodity',
        barmode='group',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_barras, use_container_width=True)

st.markdown('<div class="section-header">🗺️ Análise por Região</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    preco_regiao = df_filtrado.groupby('regiao')['preco'].mean().sort_values(ascending=False)
    
    fig_regiao = px.bar(
        preco_regiao.reset_index(),
        x='preco',
        y='regiao',
        orientation='h',
        title='🏆 Ranking de Preços por Região',
        color='preco',
        color_continuous_scale='Viridis',
        height=400
    )
    st.plotly_chart(fig_regiao, use_container_width=True)

with col2:
    scatter_data = df_filtrado.groupby(['regiao', 'commodity']).agg({
        'preco': 'mean',
        'volume': 'sum'
    }).reset_index()
    
    fig_scatter = px.scatter(
        scatter_data,
        x='volume',
        y='preco',
        size='preco',
        color='commodity',
        hover_name='regiao',
        title='🎯 Relação Volume vs Preço',
        size_max=40,
        height=400
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown('<div class="section-header">💡 Insights Inteligentes</div>', unsafe_allow_html=True)

col1, col3 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-box'>
        <h4>🎯 Top Performer</h4>
        <p>Commodity com melhor performance no período</p>
        <h3>{}</h3>
    </div>
    """.format(df_filtrado.groupby('commodity')['preco'].mean().idxmax()), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-box'>
        <h4>🕒 Melhor Período</h4>
        <p>Mês com maior volume</p>
        <h3>Mês {}</h3>
    </div>
    """.format(df_filtrado.groupby('mes')['volume'].sum().idxmax()), unsafe_allow_html=True)

st.markdown('<div class="section-header">📋 Dados Detalhados</div>', unsafe_allow_html=True)

styled_df = df_filtrado.style.background_gradient(
    subset=['preco'], cmap='YlOrRd'
).format({
    'preco': 'R$ {:.2f}',
    'volume': '{:,.0f}',
    'lucro': 'R$ {:,.0f}'
})

st.dataframe(styled_df, use_container_width=True, height=400)

st.markdown("---")
col1, col2 = st.columns([3, 1])

with col2:
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Baixar Relatório CSV",
        data=csv,
        file_name=f"relatorio_cepea_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 2rem;'>
    <p>🌱 <strong>Dashboard CEPEA Analytics</strong> - Desenvolvido para insights inteligentes em commodities agrícolas</p>
</div>
""", unsafe_allow_html=True)
