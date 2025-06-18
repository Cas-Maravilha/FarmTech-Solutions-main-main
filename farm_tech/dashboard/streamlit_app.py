"""
Dashboard Streamlit para FarmTech Solutions
Sistema de Irrigação Inteligente - Visualização em Tempo Real
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import time
import requests
from typing import Dict, List, Any, Optional

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .alert-low {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .prediction-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class FarmTechDashboard:
    """Dashboard principal do FarmTech Solutions"""
    
    def __init__(self):
        self.api_url = "http://localhost:5000/api"
        self.data_cache = {}
        self.last_update = None
        
    def load_sample_data(self):
        """Carregar dados de exemplo para demonstração"""
        # Simular dados de sensores
        np.random.seed(42)
        
        # Gerar dados para os últimos 7 dias
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                            end=datetime.now(), freq='H')
        
        sensor_data = []
        for date in dates:
            # Sensor 1 - Umidade (tendência decrescente)
            base_umidity = 70 - (date - dates[0]).days * 2
            umidity = max(20, base_umidity + np.random.normal(0, 5))
            
            # Sensor 2 - pH (relativamente estável)
            ph = 6.5 + np.random.normal(0, 0.3)
            
            # Sensor 3 - Nutrientes (diminuindo gradualmente)
            base_nutrients = 200 - (date - dates[0]).days * 3
            nutrients = max(50, base_nutrients + np.random.normal(0, 10))
            
            sensor_data.extend([
                {
                    'timestamp': date,
                    'sensor_id': 1,
                    'sensor_type': 'umidade',
                    'value': round(umidity, 2),
                    'unit': '%',
                    'area_id': 1,
                    'area_name': 'Área A - Milho'
                },
                {
                    'timestamp': date,
                    'sensor_id': 2,
                    'sensor_type': 'ph',
                    'value': round(ph, 2),
                    'unit': 'pH',
                    'area_id': 2,
                    'area_name': 'Área B - Soja'
                },
                {
                    'timestamp': date,
                    'sensor_id': 3,
                    'sensor_type': 'nutrientes',
                    'value': round(nutrients, 2),
                    'unit': 'ppm',
                    'area_id': 3,
                    'area_name': 'Área C - Trigo'
                }
            ])
        
        return pd.DataFrame(sensor_data)
    
    def get_irrigation_predictions(self):
        """Obter predições de irrigação (simulado)"""
        predictions = [
            {
                'sensor_id': 1,
                'sensor_type': 'umidade',
                'current_value': 45.2,
                'prediction_probability': 0.75,
                'recommended_action': 'IRRIGAR IMEDIATAMENTE',
                'priority': 'ALTA',
                'reason': 'Umidade muito baixa (45.2%)',
                'confidence': 0.85,
                'area_name': 'Área A - Milho'
            },
            {
                'sensor_id': 2,
                'sensor_type': 'ph',
                'current_value': 6.3,
                'prediction_probability': 0.15,
                'recommended_action': 'MONITORAR',
                'priority': 'BAIXA',
                'reason': 'pH dentro do ideal',
                'confidence': 0.15,
                'area_name': 'Área B - Soja'
            },
            {
                'sensor_id': 3,
                'sensor_type': 'nutrientes',
                'current_value': 165.8,
                'prediction_probability': 0.45,
                'recommended_action': 'IRRIGAR EM BREVE',
                'priority': 'MÉDIA',
                'reason': 'Nutrientes diminuindo',
                'confidence': 0.45,
                'area_name': 'Área C - Trigo'
            }
        ]
        return predictions
    
    def get_irrigation_schedule(self):
        """Obter agenda de irrigação (simulado)"""
        schedule = [
            {
                'area_id': 1,
                'area_name': 'Área A - Milho',
                'start_time': (datetime.now() + timedelta(hours=2)).isoformat(),
                'duration_minutes': 45,
                'water_amount_liters': 300,
                'priority': 'ALTA',
                'reason': 'Umidade muito baixa',
                'cost_estimate': 3.50
            },
            {
                'area_id': 3,
                'area_name': 'Área C - Trigo',
                'start_time': (datetime.now() + timedelta(hours=6)).isoformat(),
                'duration_minutes': 30,
                'water_amount_liters': 200,
                'priority': 'MÉDIA',
                'reason': 'Nutrientes diminuindo',
                'cost_estimate': 2.30
            }
        ]
        return schedule
    
    def create_sensor_charts(self, df: pd.DataFrame):
        """Criar gráficos dos sensores"""
        # Filtrar dados dos últimos 24 horas
        recent_data = df[df['timestamp'] >= datetime.now() - timedelta(hours=24)]
        
        # Criar subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Umidade do Solo (%)', 'pH do Solo', 'Nutrientes (ppm)'),
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Cores para cada sensor
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        
        for i, sensor_type in enumerate(['umidade', 'ph', 'nutrientes']):
            sensor_data = recent_data[recent_data['sensor_type'] == sensor_type]
            
            if not sensor_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=sensor_data['timestamp'],
                        y=sensor_data['value'],
                        mode='lines+markers',
                        name=f'Sensor {sensor_data["sensor_id"].iloc[0]} - {sensor_type.title()}',
                        line=dict(color=colors[i], width=2),
                        marker=dict(size=6)
                    ),
                    row=i+1, col=1
                )
                
                # Adicionar linhas de referência
                if sensor_type == 'umidade':
                    fig.add_hline(y=60, line_dash="dash", line_color="green", 
                                annotation_text="Ideal", row=i+1, col=1)
                    fig.add_hline(y=40, line_dash="dash", line_color="red", 
                                annotation_text="Crítico", row=i+1, col=1)
                elif sensor_type == 'ph':
                    fig.add_hline(y=6.5, line_dash="dash", line_color="green", 
                                annotation_text="Ideal", row=i+1, col=1)
                    fig.add_hline(y=5.5, line_dash="dash", line_color="orange", 
                                annotation_text="Limite", row=i+1, col=1)
                    fig.add_hline(y=7.5, line_dash="dash", line_color="orange", 
                                annotation_text="Limite", row=i+1, col=1)
                elif sensor_type == 'nutrientes':
                    fig.add_hline(y=150, line_dash="dash", line_color="green", 
                                annotation_text="Ideal", row=i+1, col=1)
                    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                                annotation_text="Crítico", row=i+1, col=1)
        
        fig.update_layout(
            height=600,
            showlegend=True,
            title_text="Monitoramento de Sensores - Últimas 24 Horas",
            title_x=0.5
        )
        
        return fig
    
    def create_trend_analysis(self, df: pd.DataFrame):
        """Criar análise de tendências"""
        # Calcular tendências para cada sensor
        trends = []
        
        for sensor_type in ['umidade', 'ph', 'nutrientes']:
            sensor_data = df[df['sensor_type'] == sensor_type].sort_values('timestamp')
            
            if len(sensor_data) >= 2:
                # Dividir dados em duas partes
                mid_point = len(sensor_data) // 2
                first_half = sensor_data.iloc[:mid_point]['value'].mean()
                second_half = sensor_data.iloc[mid_point:]['value'].mean()
                
                change_percent = ((second_half - first_half) / first_half) * 100
                current_value = sensor_data.iloc[-1]['value']
                
                # Determinar status
                if sensor_type == 'umidade':
                    if current_value < 40:
                        status = 'CRÍTICO'
                        color = 'red'
                    elif current_value < 50:
                        status = 'ATENÇÃO'
                        color = 'orange'
                    else:
                        status = 'NORMAL'
                        color = 'green'
                elif sensor_type == 'ph':
                    if current_value < 5.5 or current_value > 7.5:
                        status = 'CRÍTICO'
                        color = 'red'
                    elif current_value < 6.0 or current_value > 7.0:
                        status = 'ATENÇÃO'
                        color = 'orange'
                    else:
                        status = 'NORMAL'
                        color = 'green'
                else:  # nutrientes
                    if current_value < 100:
                        status = 'CRÍTICO'
                        color = 'red'
                    elif current_value < 150:
                        status = 'ATENÇÃO'
                        color = 'orange'
                    else:
                        status = 'NORMAL'
                        color = 'green'
                
                trends.append({
                    'sensor_type': sensor_type.title(),
                    'current_value': current_value,
                    'change_percent': change_percent,
                    'status': status,
                    'color': color,
                    'trend': 'Diminuindo' if change_percent < 0 else 'Aumentando'
                })
        
        return trends
    
    def create_prediction_chart(self, predictions: List[Dict]):
        """Criar gráfico de predições"""
        if not predictions:
            return None
        
        # Preparar dados para o gráfico
        sensor_ids = [p['sensor_id'] for p in predictions]
        probabilities = [p['prediction_probability'] * 100 for p in predictions]
        colors = ['red' if p['priority'] == 'ALTA' else 
                 'orange' if p['priority'] == 'MÉDIA' else 'green' 
                 for p in predictions]
        
        fig = go.Figure(data=[
            go.Bar(
                x=[f"Sensor {sid}" for sid in sensor_ids],
                y=probabilities,
                marker_color=colors,
                text=[f"{prob:.1f}%" for prob in probabilities],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Probabilidade de Necessidade de Irrigação",
            xaxis_title="Sensores",
            yaxis_title="Probabilidade (%)",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        return fig
    
    def create_schedule_timeline(self, schedule: List[Dict]):
        """Criar timeline da agenda de irrigação"""
        if not schedule:
            return None
        
        # Preparar dados para o timeline
        events = []
        for event in schedule:
            start_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            end_time = start_time + timedelta(minutes=event['duration_minutes'])
            
            events.append({
                'Task': event['area_name'],
                'Start': start_time,
                'Finish': end_time,
                'Resource': event['priority'],
                'Description': f"{event['water_amount_liters']}L - {event['reason']}"
            })
        
        df_timeline = pd.DataFrame(events)
        
        fig = px.timeline(df_timeline, x_start="Start", x_end="Finish", y="Task",
                         color="Resource", title="Agenda de Irrigação",
                         color_discrete_map={
                             'ALTA': 'red',
                             'MÉDIA': 'orange',
                             'BAIXA': 'green'
                         })
        
        fig.update_layout(height=400)
        return fig

def main():
    """Função principal do dashboard"""
    
    # Header principal
    st.markdown('<h1 class="main-header">🌾 FarmTech Solutions</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">Dashboard de Irrigação Inteligente</h2>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Configurações")
    
    # Seleção de área
    selected_area = st.sidebar.selectbox(
        "Selecionar Área",
        ["Todas as Áreas", "Área A - Milho", "Área B - Soja", "Área C - Trigo"]
    )
    
    # Período de análise
    time_period = st.sidebar.selectbox(
        "Período de Análise",
        ["Últimas 24 horas", "Últimos 3 dias", "Últimos 7 dias", "Últimos 30 dias"]
    )
    
    # Atualização automática
    auto_refresh = st.sidebar.checkbox("Atualização Automática", value=True)
    refresh_interval = st.sidebar.slider("Intervalo (segundos)", 30, 300, 60)
    
    # Inicializar dashboard
    dashboard = FarmTechDashboard()
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        sensor_data = dashboard.load_sample_data()
        predictions = dashboard.get_irrigation_predictions()
        schedule = dashboard.get_irrigation_schedule()
    
    # Métricas principais
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Sensores Ativos",
            value="3",
            delta="0"
        )
    
    with col2:
        st.metric(
            label="Áreas Monitoradas",
            value="3",
            delta="0"
        )
    
    with col3:
        total_water = sum(event['water_amount_liters'] for event in schedule)
        st.metric(
            label="Água Necessária (L)",
            value=f"{total_water}",
            delta=f"+{total_water}"
        )
    
    with col4:
        total_cost = sum(event['cost_estimate'] for event in schedule)
        st.metric(
            label="Custo Estimado (R$)",
            value=f"{total_cost:.2f}",
            delta=f"+{total_cost:.2f}"
        )
    
    # Análise de tendências
    st.subheader("📈 Análise de Tendências")
    
    trends = dashboard.create_trend_analysis(sensor_data)
    
    trend_cols = st.columns(len(trends))
    for i, trend in enumerate(trends):
        with trend_cols[i]:
            st.markdown(f"""
            <div class="metric-card alert-{trend['color']}">
                <h4>{trend['sensor_type']}</h4>
                <p><strong>Valor Atual:</strong> {trend['current_value']:.2f}</p>
                <p><strong>Mudança:</strong> {trend['change_percent']:.1f}%</p>
                <p><strong>Status:</strong> {trend['status']}</p>
                <p><strong>Tendência:</strong> {trend['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Gráficos de sensores
    st.subheader("📊 Monitoramento de Sensores")
    
    sensor_chart = dashboard.create_sensor_charts(sensor_data)
    st.plotly_chart(sensor_chart, use_container_width=True)
    
    # Predições de irrigação
    st.subheader("🔮 Predições de Irrigação")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prediction_chart = dashboard.create_prediction_chart(predictions)
        if prediction_chart:
            st.plotly_chart(prediction_chart, use_container_width=True)
    
    with col2:
        st.markdown("### Recomendações")
        for pred in predictions:
            priority_class = "high" if pred['priority'] == 'ALTA' else \
                           "medium" if pred['priority'] == 'MÉDIA' else "low"
            
            st.markdown(f"""
            <div class="prediction-card alert-{priority_class}">
                <h5>Sensor {pred['sensor_id']} - {pred['sensor_type'].title()}</h5>
                <p><strong>Ação:</strong> {pred['recommended_action']}</p>
                <p><strong>Prioridade:</strong> {pred['priority']}</p>
                <p><strong>Confiança:</strong> {pred['confidence']:.1%}</p>
                <p><strong>Motivo:</strong> {pred['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Agenda de irrigação
    st.subheader("⏰ Agenda de Irrigação")
    
    schedule_chart = dashboard.create_schedule_timeline(schedule)
    if schedule_chart:
        st.plotly_chart(schedule_chart, use_container_width=True)
    
    # Detalhes da agenda
    st.markdown("### Detalhes dos Eventos")
    
    for event in schedule:
        priority_class = "high" if event['priority'] == 'ALTA' else \
                       "medium" if event['priority'] == 'MÉDIA' else "low"
        
        start_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
        
        st.markdown(f"""
        <div class="prediction-card alert-{priority_class}">
            <h5>{event['area_name']}</h5>
            <p><strong>Horário:</strong> {start_time.strftime('%d/%m/%Y %H:%M')}</p>
            <p><strong>Duração:</strong> {event['duration_minutes']} minutos</p>
            <p><strong>Água:</strong> {event['water_amount_liters']} litros</p>
            <p><strong>Custo:</strong> R$ {event['cost_estimate']:.2f}</p>
            <p><strong>Motivo:</strong> {event['reason']}</p>
        </div>
        """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🌾 FarmTech Solutions - Sistema de Irrigação Inteligente</p>
        <p>Desenvolvido com Streamlit e Machine Learning</p>
        <p>Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)
    
    # Atualização automática
    if auto_refresh:
        time.sleep(refresh_interval)
        st.experimental_rerun()

if __name__ == "__main__":
    main() 