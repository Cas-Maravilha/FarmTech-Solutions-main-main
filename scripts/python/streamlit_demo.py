#!/usr/bin/env python3
"""
Demonstração Streamlit - FarmTech Solutions
Dashboard Interativo para Sistema de Irrigação Inteligente
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard",
    page_icon="🌾",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high { border-left-color: #f44336; }
    .alert-medium { border-left-color: #ff9800; }
    .alert-low { border-left-color: #4caf50; }
</style>
""", unsafe_allow_html=True)

def create_sample_data():
    """Criar dados de exemplo"""
    np.random.seed(42)
    
    # Gerar dados para os últimos 7 dias
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                         end=datetime.now(), freq='H')
    
    data = []
    for date in dates:
        # Umidade (tendência decrescente)
        umidity = max(20, 70 - (date - dates[0]).days * 2 + np.random.normal(0, 5))
        
        # pH (estável)
        ph = 6.5 + np.random.normal(0, 0.3)
        
        # Nutrientes (diminuindo)
        nutrients = max(50, 200 - (date - dates[0]).days * 3 + np.random.normal(0, 10))
        
        data.extend([
            {'timestamp': date, 'sensor': 'Umidade', 'value': umidity, 'unit': '%'},
            {'timestamp': date, 'sensor': 'pH', 'value': ph, 'unit': 'pH'},
            {'timestamp': date, 'sensor': 'Nutrientes', 'value': nutrients, 'unit': 'ppm'}
        ])
    
    return pd.DataFrame(data)

def create_sensor_chart(df):
    """Criar gráfico dos sensores"""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Umidade do Solo (%)', 'pH do Solo', 'Nutrientes (ppm)'),
        vertical_spacing=0.1
    )
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for i, sensor in enumerate(['Umidade', 'pH', 'Nutrientes']):
        sensor_data = df[df['sensor'] == sensor]
        
        fig.add_trace(
            go.Scatter(
                x=sensor_data['timestamp'],
                y=sensor_data['value'],
                mode='lines+markers',
                name=sensor,
                line=dict(color=colors[i], width=2)
            ),
            row=i+1, col=1
        )
        
        # Linhas de referência
        if sensor == 'Umidade':
            fig.add_hline(y=60, line_dash="dash", line_color="green", 
                         annotation_text="Ideal", row=i+1, col=1)
            fig.add_hline(y=40, line_dash="dash", line_color="red", 
                         annotation_text="Crítico", row=i+1, col=1)
        elif sensor == 'pH':
            fig.add_hline(y=6.5, line_dash="dash", line_color="green", 
                         annotation_text="Ideal", row=i+1, col=1)
        elif sensor == 'Nutrientes':
            fig.add_hline(y=150, line_dash="dash", line_color="green", 
                         annotation_text="Ideal", row=i+1, col=1)
    
    fig.update_layout(height=600, showlegend=True)
    return fig

def main():
    """Função principal"""
    
    # Header
    st.markdown('<h1 class="main-header">🌾 FarmTech Solutions</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Dashboard de Irrigação Inteligente</h2>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Configurações")
    
    selected_area = st.sidebar.selectbox(
        "Área",
        ["Todas", "Área A - Milho", "Área B - Soja", "Área C - Trigo"]
    )
    
    time_period = st.sidebar.selectbox(
        "Período",
        ["24h", "3 dias", "7 dias", "30 dias"]
    )
    
    auto_refresh = st.sidebar.checkbox("Atualização Automática", value=True)
    
    # Carregar dados
    df = create_sample_data()
    
    # Métricas
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sensores Ativos", "3", "0")
    
    with col2:
        st.metric("Áreas Monitoradas", "3", "0")
    
    with col3:
        st.metric("Água Necessária", "450L", "+450L")
    
    with col4:
        st.metric("Custo Estimado", "R$ 5,25", "+R$ 5,25")
    
    # Análise de tendências
    st.subheader("📈 Análise de Tendências")
    
    recent_data = df[df['timestamp'] >= datetime.now() - timedelta(hours=24)]
    
    trend_cols = st.columns(3)
    
    for i, sensor in enumerate(['Umidade', 'pH', 'Nutrientes']):
        with trend_cols[i]:
            sensor_data = recent_data[recent_data['sensor'] == sensor]
            if len(sensor_data) >= 2:
                current = sensor_data.iloc[-1]['value']
                previous = sensor_data.iloc[0]['value']
                change = ((current - previous) / previous) * 100
                
                if sensor == 'Umidade':
                    status = "CRÍTICO" if current < 40 else "ATENÇÃO" if current < 50 else "NORMAL"
                    color = "high" if current < 40 else "medium" if current < 50 else "low"
                elif sensor == 'pH':
                    status = "NORMAL" if 5.5 <= current <= 7.5 else "ATENÇÃO"
                    color = "low" if 5.5 <= current <= 7.5 else "medium"
                else:  # Nutrientes
                    status = "CRÍTICO" if current < 100 else "ATENÇÃO" if current < 150 else "NORMAL"
                    color = "high" if current < 100 else "medium" if current < 150 else "low"
                
                st.markdown(f"""
                <div class="metric-card alert-{color}">
                    <h4>{sensor}</h4>
                    <p><strong>Valor:</strong> {current:.2f}</p>
                    <p><strong>Mudança:</strong> {change:.1f}%</p>
                    <p><strong>Status:</strong> {status}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Gráfico dos sensores
    st.subheader("📊 Monitoramento de Sensores")
    chart = create_sensor_chart(df)
    st.plotly_chart(chart, use_container_width=True)
    
    # Predições de ML
    st.subheader("🔮 Predições de Machine Learning")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de predições
        predictions_data = {
            'Sensor': ['Sensor 1', 'Sensor 2', 'Sensor 3'],
            'Probabilidade': [75, 15, 45],
            'Prioridade': ['ALTA', 'BAIXA', 'MÉDIA']
        }
        pred_df = pd.DataFrame(predictions_data)
        
        fig = px.bar(pred_df, x='Sensor', y='Probabilidade',
                    color='Prioridade',
                    title="Probabilidade de Irrigação",
                    color_discrete_map={'ALTA': 'red', 'MÉDIA': 'orange', 'BAIXA': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Recomendações")
        
        recommendations = [
            {
                'sensor': 'Sensor 1 - Umidade',
                'action': 'IRRIGAR IMEDIATAMENTE',
                'priority': 'ALTA',
                'reason': 'Umidade muito baixa (45.2%)'
            },
            {
                'sensor': 'Sensor 2 - pH',
                'action': 'MONITORAR',
                'priority': 'BAIXA',
                'reason': 'pH dentro do ideal'
            },
            {
                'sensor': 'Sensor 3 - Nutrientes',
                'action': 'IRRIGAR EM BREVE',
                'priority': 'MÉDIA',
                'reason': 'Nutrientes diminuindo'
            }
        ]
        
        for rec in recommendations:
            priority_class = "high" if rec['priority'] == 'ALTA' else \
                           "medium" if rec['priority'] == 'MÉDIA' else "low"
            
            st.markdown(f"""
            <div class="metric-card alert-{priority_class}">
                <h5>{rec['sensor']}</h5>
                <p><strong>Ação:</strong> {rec['action']}</p>
                <p><strong>Prioridade:</strong> {rec['priority']}</p>
                <p><strong>Motivo:</strong> {rec['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Agenda de irrigação
    st.subheader("⏰ Agenda de Irrigação")
    
    schedule_data = {
        'Área': ['Área A - Milho', 'Área C - Trigo'],
        'Horário': ['18:00', '22:00'],
        'Duração': [60, 45],
        'Água (L)': [450, 320],
        'Prioridade': ['ALTA', 'MÉDIA']
    }
    
    schedule_df = pd.DataFrame(schedule_data)
    st.dataframe(schedule_df, use_container_width=True)
    
    # Insights do ML
    st.subheader("🤖 Insights do Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Análise de Padrões")
        st.markdown("""
        - **Tendência de umidade**: Diminuindo rapidamente (-21.2%)
        - **pH do solo**: Estável dentro do ideal
        - **Nutrientes**: Diminuindo gradualmente (-5.8%)
        - **Recomendação**: Irrigação imediata na Área A
        """)
    
    with col2:
        st.markdown("### Eficiência do Sistema")
        st.markdown("""
        - **Economia de água**: 25% vs irrigação manual
        - **Precisão das predições**: 87%
        - **Redução de custos**: 18%
        - **Melhoria de produtividade**: 15%
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <p>🌾 FarmTech Solutions - Dashboard Streamlit</p>
        <p>Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Atualização automática
    if auto_refresh:
        time.sleep(5)
        st.experimental_rerun()

if __name__ == "__main__":
    main() 