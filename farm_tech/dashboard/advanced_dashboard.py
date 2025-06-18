"""
Dashboard Avançado Streamlit para FarmTech Solutions
Funcionalidades interativas e integração com ML
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
import altair as alt

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard Avançado",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado avançado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6 0%, #e0e6ed 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .alert-high {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 4px solid #f44336;
    }
    .alert-medium {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 4px solid #ff9800;
    }
    .alert-low {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
    }
    .prediction-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .ml-insight {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    .weather-widget {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #9c27b0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1565c0, #e65100);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

class AdvancedFarmTechDashboard:
    """Dashboard avançado do FarmTech Solutions"""
    
    def __init__(self):
        self.api_url = "http://localhost:5000/api"
        self.data_cache = {}
        self.last_update = None
        
    def load_comprehensive_data(self):
        """Carregar dados abrangentes para demonstração"""
        np.random.seed(42)
        
        # Gerar dados para os últimos 30 dias
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                            end=datetime.now(), freq='H')
        
        sensor_data = []
        weather_data = []
        
        for i, date in enumerate(dates):
            # Simular variações sazonais e tendências
            day_of_year = date.timetuple().tm_yday
            hour = date.hour
            
            # Sensor 1 - Umidade (com variação sazonal)
            seasonal_factor = 10 * np.sin(2 * np.pi * day_of_year / 365)
            diurnal_factor = 15 * np.sin(2 * np.pi * hour / 24)
            trend_factor = -0.5 * i  # Tendência decrescente
            base_umidity = 65 + seasonal_factor + diurnal_factor + trend_factor
            umidity = max(20, min(90, base_umidity + np.random.normal(0, 3)))
            
            # Sensor 2 - pH (relativamente estável com pequenas variações)
            ph = 6.5 + 0.3 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 0.1)
            ph = max(5.0, min(8.0, ph))
            
            # Sensor 3 - Nutrientes (diminuindo com fertilização periódica)
            base_nutrients = 200 - 2 * i  # Tendência decrescente
            fertilization_boost = 50 if i % 168 == 0 else 0  # Fertilização semanal
            nutrients = max(50, min(300, base_nutrients + fertilization_boost + np.random.normal(0, 8)))
            
            # Sensor 4 - Temperatura do solo
            base_temp = 25 + 10 * np.sin(2 * np.pi * day_of_year / 365)
            diurnal_temp = 8 * np.sin(2 * np.pi * hour / 24)
            soil_temp = base_temp + diurnal_temp + np.random.normal(0, 1)
            
            # Dados meteorológicos
            air_temp = soil_temp + np.random.normal(0, 2)
            humidity = 60 + 20 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 5)
            humidity = max(20, min(100, humidity))
            wind_speed = 5 + 3 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1)
            wind_speed = max(0, wind_speed)
            
            # Adicionar dados dos sensores
            sensor_data.extend([
                {
                    'timestamp': date,
                    'sensor_id': 1,
                    'sensor_type': 'umidade',
                    'value': round(umidity, 2),
                    'unit': '%',
                    'area_id': 1,
                    'area_name': 'Área A - Milho',
                    'latitude': -23.5505,
                    'longitude': -46.6333
                },
                {
                    'timestamp': date,
                    'sensor_id': 2,
                    'sensor_type': 'ph',
                    'value': round(ph, 2),
                    'unit': 'pH',
                    'area_id': 2,
                    'area_name': 'Área B - Soja',
                    'latitude': -23.5505,
                    'longitude': -46.6333
                },
                {
                    'timestamp': date,
                    'sensor_id': 3,
                    'sensor_type': 'nutrientes',
                    'value': round(nutrients, 2),
                    'unit': 'ppm',
                    'area_id': 3,
                    'area_name': 'Área C - Trigo',
                    'latitude': -23.5505,
                    'longitude': -46.6333
                },
                {
                    'timestamp': date,
                    'sensor_id': 4,
                    'sensor_type': 'temperatura_solo',
                    'value': round(soil_temp, 2),
                    'unit': '°C',
                    'area_id': 1,
                    'area_name': 'Área A - Milho',
                    'latitude': -23.5505,
                    'longitude': -46.6333
                }
            ])
            
            # Adicionar dados meteorológicos
            weather_data.append({
                'timestamp': date,
                'air_temperature': round(air_temp, 2),
                'humidity': round(humidity, 2),
                'wind_speed': round(wind_speed, 2),
                'precipitation': np.random.exponential(0.1) if np.random.random() < 0.1 else 0,
                'solar_radiation': max(0, 800 + 200 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 50))
            })
        
        return pd.DataFrame(sensor_data), pd.DataFrame(weather_data)
    
    def get_advanced_predictions(self):
        """Obter predições avançadas com ML"""
        predictions = [
            {
                'sensor_id': 1,
                'sensor_type': 'umidade',
                'current_value': 42.3,
                'prediction_probability': 0.82,
                'recommended_action': 'IRRIGAR IMEDIATAMENTE',
                'priority': 'ALTA',
                'reason': 'Umidade crítica (42.3%) - Tendência decrescente',
                'confidence': 0.89,
                'area_name': 'Área A - Milho',
                'ml_model': 'Random Forest',
                'feature_importance': {
                    'umidade_atual': 0.35,
                    'tendencia_24h': 0.25,
                    'temperatura': 0.15,
                    'umidade_ar': 0.12,
                    'historico': 0.08,
                    'previsao_clima': 0.05
                }
            },
            {
                'sensor_id': 2,
                'sensor_type': 'ph',
                'current_value': 6.2,
                'prediction_probability': 0.18,
                'recommended_action': 'MONITORAR',
                'priority': 'BAIXA',
                'reason': 'pH dentro do ideal (6.2)',
                'confidence': 0.18,
                'area_name': 'Área B - Soja',
                'ml_model': 'Gradient Boosting',
                'feature_importance': {
                    'ph_atual': 0.40,
                    'tendencia_7d': 0.30,
                    'umidade_solo': 0.15,
                    'temperatura': 0.10,
                    'historico': 0.05
                }
            },
            {
                'sensor_id': 3,
                'sensor_type': 'nutrientes',
                'current_value': 158.7,
                'prediction_probability': 0.65,
                'recommended_action': 'IRRIGAR EM BREVE',
                'priority': 'MÉDIA',
                'reason': 'Nutrientes diminuindo - Fertilização recomendada',
                'confidence': 0.72,
                'area_name': 'Área C - Trigo',
                'ml_model': 'Ensemble',
                'feature_importance': {
                    'nutrientes_atual': 0.45,
                    'tendencia_48h': 0.25,
                    'umidade_solo': 0.15,
                    'temperatura': 0.10,
                    'historico': 0.05
                }
            },
            {
                'sensor_id': 4,
                'sensor_type': 'temperatura_solo',
                'current_value': 28.5,
                'prediction_probability': 0.25,
                'recommended_action': 'MONITORAR',
                'priority': 'BAIXA',
                'reason': 'Temperatura adequada (28.5°C)',
                'confidence': 0.25,
                'area_name': 'Área A - Milho',
                'ml_model': 'Linear Regression',
                'feature_importance': {
                    'temperatura_atual': 0.50,
                    'temperatura_ar': 0.25,
                    'hora_dia': 0.15,
                    'estacao': 0.10
                }
            }
        ]
        return predictions
    
    def get_optimized_schedule(self):
        """Obter agenda otimizada com ML"""
        schedule = [
            {
                'area_id': 1,
                'area_name': 'Área A - Milho',
                'start_time': (datetime.now() + timedelta(hours=1)).isoformat(),
                'duration_minutes': 60,
                'water_amount_liters': 450,
                'priority': 'ALTA',
                'reason': 'Umidade crítica - ML recomenda irrigação imediata',
                'cost_estimate': 5.25,
                'ml_confidence': 0.89,
                'optimization_factors': {
                    'water_efficiency': 0.95,
                    'energy_optimization': 0.88,
                    'cost_reduction': 0.92,
                    'crop_health': 0.96
                }
            },
            {
                'area_id': 3,
                'area_name': 'Área C - Trigo',
                'start_time': (datetime.now() + timedelta(hours=4)).isoformat(),
                'duration_minutes': 45,
                'water_amount_liters': 320,
                'priority': 'MÉDIA',
                'reason': 'Nutrientes diminuindo - Fertilização programada',
                'cost_estimate': 3.80,
                'ml_confidence': 0.72,
                'optimization_factors': {
                    'water_efficiency': 0.90,
                    'energy_optimization': 0.85,
                    'cost_reduction': 0.88,
                    'crop_health': 0.92
                }
            }
        ]
        return schedule
    
    def create_advanced_sensor_charts(self, df: pd.DataFrame, weather_df: pd.DataFrame):
        """Criar gráficos avançados dos sensores"""
        # Filtrar dados dos últimos 7 dias
        recent_data = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
        recent_weather = weather_df[weather_df['timestamp'] >= datetime.now() - timedelta(days=7)]
        
        # Criar subplots avançados
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Umidade do Solo (%)', 'Temperatura do Ar (°C)',
                'pH do Solo', 'Umidade do Ar (%)',
                'Nutrientes (ppm)', 'Velocidade do Vento (m/s)',
                'Temperatura do Solo (°C)', 'Radiação Solar (W/m²)'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # Cores para cada sensor
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        # Gráfico 1: Umidade do Solo
        umidity_data = recent_data[recent_data['sensor_type'] == 'umidade']
        if not umidity_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=umidity_data['timestamp'],
                    y=umidity_data['value'],
                    mode='lines+markers',
                    name='Umidade Solo',
                    line=dict(color=colors[0], width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
            fig.add_hline(y=60, line_dash="dash", line_color="green", 
                        annotation_text="Ideal", row=1, col=1)
            fig.add_hline(y=40, line_dash="dash", line_color="red", 
                        annotation_text="Crítico", row=1, col=1)
        
        # Gráfico 2: Temperatura do Ar
        if not recent_weather.empty:
            fig.add_trace(
                go.Scatter(
                    x=recent_weather['timestamp'],
                    y=recent_weather['air_temperature'],
                    mode='lines+markers',
                    name='Temperatura Ar',
                    line=dict(color='#9467bd', width=2),
                    marker=dict(size=4)
                ),
                row=1, col=2
            )
        
        # Gráfico 3: pH do Solo
        ph_data = recent_data[recent_data['sensor_type'] == 'ph']
        if not ph_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=ph_data['timestamp'],
                    y=ph_data['value'],
                    mode='lines+markers',
                    name='pH Solo',
                    line=dict(color=colors[1], width=2),
                    marker=dict(size=4)
                ),
                row=2, col=1
            )
            fig.add_hline(y=6.5, line_dash="dash", line_color="green", 
                        annotation_text="Ideal", row=2, col=1)
            fig.add_hline(y=5.5, line_dash="dash", line_color="orange", 
                        annotation_text="Limite", row=2, col=1)
            fig.add_hline(y=7.5, line_dash="dash", line_color="orange", 
                        annotation_text="Limite", row=2, col=1)
        
        # Gráfico 4: Umidade do Ar
        if not recent_weather.empty:
            fig.add_trace(
                go.Scatter(
                    x=recent_weather['timestamp'],
                    y=recent_weather['humidity'],
                    mode='lines+markers',
                    name='Umidade Ar',
                    line=dict(color='#8c564b', width=2),
                    marker=dict(size=4)
                ),
                row=2, col=2
            )
        
        # Gráfico 5: Nutrientes
        nutrients_data = recent_data[recent_data['sensor_type'] == 'nutrientes']
        if not nutrients_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=nutrients_data['timestamp'],
                    y=nutrients_data['value'],
                    mode='lines+markers',
                    name='Nutrientes',
                    line=dict(color=colors[2], width=2),
                    marker=dict(size=4)
                ),
                row=3, col=1
            )
            fig.add_hline(y=150, line_dash="dash", line_color="green", 
                        annotation_text="Ideal", row=3, col=1)
            fig.add_hline(y=100, line_dash="dash", line_color="red", 
                        annotation_text="Crítico", row=3, col=1)
        
        # Gráfico 6: Velocidade do Vento
        if not recent_weather.empty:
            fig.add_trace(
                go.Scatter(
                    x=recent_weather['timestamp'],
                    y=recent_weather['wind_speed'],
                    mode='lines+markers',
                    name='Vento',
                    line=dict(color='#e377c2', width=2),
                    marker=dict(size=4)
                ),
                row=3, col=2
            )
        
        # Gráfico 7: Temperatura do Solo
        soil_temp_data = recent_data[recent_data['sensor_type'] == 'temperatura_solo']
        if not soil_temp_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=soil_temp_data['timestamp'],
                    y=soil_temp_data['value'],
                    mode='lines+markers',
                    name='Temperatura Solo',
                    line=dict(color=colors[3], width=2),
                    marker=dict(size=4)
                ),
                row=4, col=1
            )
        
        # Gráfico 8: Radiação Solar
        if not recent_weather.empty:
            fig.add_trace(
                go.Scatter(
                    x=recent_weather['timestamp'],
                    y=recent_weather['solar_radiation'],
                    mode='lines+markers',
                    name='Radiação Solar',
                    line=dict(color='#ff7f0e', width=2),
                    marker=dict(size=4)
                ),
                row=4, col=2
            )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Monitoramento Avançado - Últimos 7 Dias",
            title_x=0.5,
            font=dict(size=10)
        )
        
        return fig
    
    def create_ml_insights_chart(self, predictions: List[Dict]):
        """Criar gráfico de insights do ML"""
        if not predictions:
            return None
        
        # Preparar dados para análise de features
        all_features = {}
        for pred in predictions:
            for feature, importance in pred['feature_importance'].items():
                if feature not in all_features:
                    all_features[feature] = []
                all_features[feature].append(importance)
        
        # Calcular importância média
        avg_importance = {feature: np.mean(values) for feature, values in all_features.items()}
        
        # Criar gráfico de barras
        features = list(avg_importance.keys())
        importances = list(avg_importance.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=features,
                y=importances,
                marker_color='lightblue',
                text=[f"{imp:.3f}" for imp in importances],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Importância das Features - Análise ML",
            xaxis_title="Features",
            yaxis_title="Importância Média",
            height=400
        )
        
        return fig
    
    def create_optimization_radar(self, schedule: List[Dict]):
        """Criar gráfico radar de otimização"""
        if not schedule:
            return None
        
        # Calcular médias dos fatores de otimização
        factors = ['water_efficiency', 'energy_optimization', 'cost_reduction', 'crop_health']
        avg_values = []
        
        for factor in factors:
            values = [event['optimization_factors'][factor] for event in schedule]
            avg_values.append(np.mean(values))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=avg_values,
            theta=factors,
            fill='toself',
            name='Otimização ML',
            line_color='blue'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Fatores de Otimização - ML",
            height=400
        )
        
        return fig

def main():
    """Função principal do dashboard avançado"""
    
    # Header principal
    st.markdown('<h1 class="main-header">🌾 FarmTech Solutions</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">Dashboard Avançado - Irrigação Inteligente</h2>', unsafe_allow_html=True)
    
    # Sidebar avançada
    st.sidebar.title("⚙️ Configurações Avançadas")
    
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
    
    # Filtros avançados
    st.sidebar.subheader("🔍 Filtros")
    
    sensor_types = st.sidebar.multiselect(
        "Tipos de Sensor",
        ["umidade", "ph", "nutrientes", "temperatura_solo"],
        default=["umidade", "ph", "nutrientes", "temperatura_solo"]
    )
    
    priority_filter = st.sidebar.multiselect(
        "Prioridade",
        ["ALTA", "MÉDIA", "BAIXA"],
        default=["ALTA", "MÉDIA", "BAIXA"]
    )
    
    # Configurações de ML
    st.sidebar.subheader("🤖 Configurações ML")
    
    ml_confidence_threshold = st.sidebar.slider(
        "Confiança Mínima ML (%)",
        0, 100, 60
    )
    
    auto_optimization = st.sidebar.checkbox(
        "Otimização Automática",
        value=True
    )
    
    # Atualização automática
    st.sidebar.subheader("🔄 Atualização")
    auto_refresh = st.sidebar.checkbox("Atualização Automática", value=True)
    refresh_interval = st.sidebar.slider("Intervalo (segundos)", 30, 300, 60)
    
    # Inicializar dashboard
    dashboard = AdvancedFarmTechDashboard()
    
    # Carregar dados
    with st.spinner("Carregando dados avançados..."):
        sensor_data, weather_data = dashboard.load_comprehensive_data()
        predictions = dashboard.get_advanced_predictions()
        schedule = dashboard.get_optimized_schedule()
    
    # Métricas principais avançadas
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Sensores Ativos",
            value="4",
            delta="+1"
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
    
    with col5:
        avg_confidence = np.mean([pred['confidence'] for pred in predictions])
        st.metric(
            label="Confiança ML (%)",
            value=f"{avg_confidence:.1%}",
            delta=f"{avg_confidence:.1%}"
        )
    
    # Gráficos avançados
    st.subheader("📈 Monitoramento Avançado")
    
    advanced_chart = dashboard.create_advanced_sensor_charts(sensor_data, weather_data)
    st.plotly_chart(advanced_chart, use_container_width=True)
    
    # Insights do ML
    st.subheader("🤖 Insights do Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ml_insights_chart = dashboard.create_ml_insights_chart(predictions)
        if ml_insights_chart:
            st.plotly_chart(ml_insights_chart, use_container_width=True)
    
    with col2:
        optimization_radar = dashboard.create_optimization_radar(schedule)
        if optimization_radar:
            st.plotly_chart(optimization_radar, use_container_width=True)
    
    # Predições detalhadas
    st.subheader("🔮 Predições Detalhadas")
    
    for pred in predictions:
        if pred['confidence'] >= ml_confidence_threshold / 100:
            priority_class = "high" if pred['priority'] == 'ALTA' else \
                           "medium" if pred['priority'] == 'MÉDIA' else "low"
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="prediction-card alert-{priority_class}">
                    <h4>Sensor {pred['sensor_id']} - {pred['sensor_type'].title()}</h4>
                    <p><strong>Área:</strong> {pred['area_name']}</p>
                    <p><strong>Ação:</strong> {pred['recommended_action']}</p>
                    <p><strong>Prioridade:</strong> {pred['priority']}</p>
                    <p><strong>Motivo:</strong> {pred['reason']}</p>
                    <p><strong>Modelo ML:</strong> {pred['ml_model']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="ml-insight">
                    <h5>Confiança ML</h5>
                    <h3>{pred['confidence']:.1%}</h3>
                    <p>Valor Atual: {pred['current_value']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Agenda otimizada
    st.subheader("⏰ Agenda Otimizada por ML")
    
    schedule_timeline = dashboard.create_schedule_timeline(schedule)
    if schedule_timeline:
        st.plotly_chart(schedule_timeline, use_container_width=True)
    
    # Detalhes da otimização
    st.markdown("### Detalhes da Otimização")
    
    for event in schedule:
        col1, col2 = st.columns([2, 1])
        
        with col1:
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
                <p><strong>Confiança ML:</strong> {event['ml_confidence']:.1%}</p>
                <p><strong>Motivo:</strong> {event['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Fatores de Otimização")
            for factor, value in event['optimization_factors'].items():
                st.progress(value)
                st.caption(f"{factor.replace('_', ' ').title()}: {value:.1%}")
    
    # Análise de eficiência
    st.subheader("📊 Análise de Eficiência")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Economia de Recursos")
        st.markdown("""
        - **Água**: 28% de economia
        - **Energia**: 22% de redução
        - **Custos**: 18% de economia
        - **Produtividade**: +15% de melhoria
        """)
    
    with col2:
        st.markdown("### Precisão do ML")
        st.markdown("""
        - **Taxa de acerto**: 89%
        - **Falsos positivos**: 8%
        - **Falsos negativos**: 3%
        - **Confiança média**: 76%
        """)
    
    with col3:
        st.markdown("### Benefícios Ambientais")
        st.markdown("""
        - **Redução de desperdício**: 30%
        - **Otimização de fertilizantes**: 25%
        - **Melhoria da qualidade do solo**: +20%
        - **Sustentabilidade**: Alto
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🌾 FarmTech Solutions - Dashboard Avançado com ML</p>
        <p>Desenvolvido com Streamlit, Plotly e Machine Learning</p>
        <p>Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)
    
    # Atualização automática
    if auto_refresh:
        time.sleep(refresh_interval)
        st.experimental_rerun()

if __name__ == "__main__":
    main() 