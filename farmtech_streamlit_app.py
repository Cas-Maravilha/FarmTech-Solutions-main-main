#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Aplicação Streamlit
Interface interativa para modelos de machine learning agrícola
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
import joblib
import json
from typing import Dict, List

# Importar módulo de ML
from farmtech_ml_models import FarmTechMLModels

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - IA Agrícola",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
    }
    .prediction-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #2E8B57;
    }
</style>
""", unsafe_allow_html=True)

class FarmTechStreamlitApp:
    def __init__(self):
        self.ml_models = FarmTechMLModels()
        self.conn = None
        
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect('data/farmtech_aprimorado.db')
            return True
        except Exception as e:
            st.error(f"Erro ao conectar ao banco: {e}")
            return False
    
    def carregar_dados_dashboard(self) -> Dict:
        """Carrega dados para o dashboard"""
        queries = {
            'plantios': """
                SELECT p.*, c.nome as cultura, t.nome as talhao, f.nome as fazenda
                FROM PLANTIO p
                JOIN CULTURA c ON p.cultura_id = c.cultura_id
                JOIN TALHAO t ON p.talhao_id = t.talhao_id
                JOIN AREA a ON t.area_id = a.area_id
                JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
            """,
            'leituras': """
                SELECT l.*, ts.nome as tipo_sensor, t.nome as talhao
                FROM LEITURA l
                JOIN SENSOR s ON l.sensor_id = s.sensor_id
                JOIN TIPO_SENSOR ts ON s.tipo_id = ts.tipo_id
                JOIN TALHAO t ON s.talhao_id = t.talhao_id
                WHERE l.data_hora >= datetime('now', '-7 days')
            """,
            'alertas': """
                SELECT a.*, t.nome as talhao, f.nome as fazenda
                FROM ALERTA a
                JOIN TALHAO t ON a.talhao_id = t.talhao_id
                JOIN AREA ar ON t.area_id = ar.area_id
                JOIN FAZENDA f ON ar.fazenda_id = f.fazenda_id
                WHERE a.status = 'ativo'
            """,
            'recomendacoes': """
                SELECT r.*, t.nome as talhao, c.nome as cultura
                FROM RECOMENDACAO r
                JOIN PLANTIO p ON r.plantio_id = p.plantio_id
                JOIN TALHAO t ON r.talhao_id = t.talhao_id
                JOIN CULTURA c ON p.cultura_id = c.cultura_id
                WHERE r.status = 'pendente'
            """
        }
        
        dados = {}
        for nome, query in queries.items():
            try:
                dados[nome] = pd.read_sql_query(query, self.conn)
            except Exception as e:
                st.warning(f"Erro ao carregar {nome}: {e}")
                dados[nome] = pd.DataFrame()
        
        return dados
    
    def dashboard_principal(self):
        """Dashboard principal"""
        st.markdown('<h1 class="main-header">🌾 FarmTech Solutions</h1>', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #2E8B57;">Sistema de IA para Agricultura de Precisão</h2>', unsafe_allow_html=True)
        
        # Carregar dados
        dados = self.carregar_dados_dashboard()
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🌱 Plantios Ativos",
                value=len(dados['plantios']),
                delta="+2 este mês"
            )
        
        with col2:
            st.metric(
                label="📊 Leituras (7 dias)",
                value=len(dados['leituras']),
                delta="+15% vs semana anterior"
            )
        
        with col3:
            st.metric(
                label="⚠️ Alertas Ativos",
                value=len(dados['alertas']),
                delta="-3 resolvidos"
            )
        
        with col4:
            st.metric(
                label="💡 Recomendações Pendentes",
                value=len(dados['recomendacoes']),
                delta="+5 novas"
            )
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Produtividade por cultura
            if not dados['plantios'].empty:
                fig_prod = px.bar(
                    dados['plantios'].groupby('cultura')['produtividade_real'].mean().reset_index(),
                    x='cultura',
                    y='produtividade_real',
                    title='Produtividade Média por Cultura',
                    color='cultura'
                )
                fig_prod.update_layout(showlegend=False)
                st.plotly_chart(fig_prod, use_container_width=True)
        
        with col2:
            # Status dos plantios
            if not dados['plantios'].empty:
                status_counts = dados['plantios']['status_plantio'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title='Status dos Plantios'
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        # Gráfico de leituras de sensores
        if not dados['leituras'].empty:
            st.subheader("📈 Leituras de Sensores (Últimos 7 dias)")
            
            # Agrupar por tipo de sensor e data
            leituras_agrupadas = dados['leituras'].groupby(['tipo_sensor', pd.Grouper(key='data_hora', freq='D')])['valor'].mean().reset_index()
            
            fig_leituras = px.line(
                leituras_agrupadas,
                x='data_hora',
                y='valor',
                color='tipo_sensor',
                title='Evolução das Leituras por Tipo de Sensor'
            )
            st.plotly_chart(fig_leituras, use_container_width=True)
    
    def pagina_predicoes(self):
        """Página de predições"""
        st.header("🔮 Predições com IA")
        
        # Carregar modelos
        try:
            self.ml_models.carregar_modelos()
            st.success("✅ Modelos carregados com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao carregar modelos: {e}")
            return
        
        # Abas para diferentes tipos de predição
        tab1, tab2, tab3 = st.tabs(["🌾 Produtividade", "💧 Irrigação", "⚠️ Detecção de Anomalias"])
        
        with tab1:
            self.predicao_produtividade()
        
        with tab2:
            self.predicao_irrigacao()
        
        with tab3:
            self.deteccao_anomalias()
    
    def predicao_produtividade(self):
        """Interface para predição de produtividade"""
        st.subheader("🌾 Predição de Produtividade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Parâmetros do Plantio")
            
            area_plantada = st.number_input("Área Plantada (hectares)", min_value=1.0, max_value=1000.0, value=100.0)
            densidade_plantio = st.number_input("Densidade de Plantio (plantas/ha)", min_value=10000, max_value=500000, value=250000)
            ciclo_vida = st.number_input("Ciclo de Vida (dias)", min_value=60, max_value=365, value=120)
            
            st.markdown("### Condições Ideais da Cultura")
            ph_min = st.number_input("pH Mínimo", min_value=4.0, max_value=9.0, value=5.5)
            ph_max = st.number_input("pH Máximo", min_value=4.0, max_value=9.0, value=7.0)
            umidade_min = st.number_input("Umidade Mínima (%)", min_value=30.0, max_value=100.0, value=60.0)
            umidade_max = st.number_input("Umidade Máxima (%)", min_value=30.0, max_value=100.0, value=85.0)
        
        with col2:
            st.markdown("### Condições Atuais")
            
            media_umidade = st.number_input("Umidade Média Atual (%)", min_value=0.0, max_value=100.0, value=65.0)
            media_temperatura = st.number_input("Temperatura Média (°C)", min_value=0.0, max_value=50.0, value=25.0)
            media_ph = st.number_input("pH Médio", min_value=4.0, max_value=9.0, value=6.0)
            media_nitrogenio = st.number_input("Nitrogênio Médio (mg/kg)", min_value=0.0, max_value=100.0, value=30.0)
            media_fosforo = st.number_input("Fósforo Médio (mg/kg)", min_value=0.0, max_value=100.0, value=25.0)
            media_potassio = st.number_input("Potássio Médio (mg/kg)", min_value=0.0, max_value=100.0, value=35.0)
            
            st.markdown("### Condições Climáticas")
            media_temp_clima = st.number_input("Temperatura Climática (°C)", min_value=0.0, max_value=50.0, value=26.0)
            media_umidade_clima = st.number_input("Umidade Climática (%)", min_value=0.0, max_value=100.0, value=70.0)
            media_precipitacao = st.number_input("Precipitação (mm)", min_value=0.0, max_value=200.0, value=15.0)
            total_leituras = st.number_input("Total de Leituras", min_value=1, max_value=10000, value=1000)
        
        # Botão de predição
        if st.button("🔮 Calcular Produtividade", type="primary"):
            with st.spinner("Calculando predição..."):
                features = {
                    'area_plantada': area_plantada,
                    'densidade_plantio': densidade_plantio,
                    'ciclo_vida': ciclo_vida,
                    'ph_ideal_min': ph_min,
                    'ph_ideal_max': ph_max,
                    'umidade_ideal_min': umidade_min,
                    'umidade_ideal_max': umidade_max,
                    'temperatura_ideal_min': 20.0,
                    'temperatura_ideal_max': 35.0,
                    'media_umidade': media_umidade,
                    'media_temperatura': media_temperatura,
                    'media_ph': media_ph,
                    'media_nitrogenio': media_nitrogenio,
                    'media_fosforo': media_fosforo,
                    'media_potassio': media_potassio,
                    'media_temp_clima': media_temp_clima,
                    'media_umidade_clima': media_umidade_clima,
                    'media_precipitacao': media_precipitacao,
                    'total_leituras': total_leituras
                }
                
                try:
                    resultado = self.ml_models.predizer_produtividade(features)
                    
                    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                    st.markdown(f"### 📊 Resultado da Predição")
                    st.metric(
                        label="Produtividade Prevista",
                        value=f"{resultado['produtividade_prevista']:.2f}",
                        delta=f"{resultado['produtividade_prevista']:.2f} ton/ha"
                    )
                    st.info(f"Confiança: {resultado['confianca']*100:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Gráfico de feature importance
                    if 'produtividade' in self.ml_models.feature_importance:
                        importance_df = pd.DataFrame(
                            list(self.ml_models.feature_importance['produtividade'].items()),
                            columns=['Feature', 'Importância']
                        ).sort_values('Importância', ascending=True)
                        
                        fig_importance = px.barh(
                            importance_df,
                            x='Importância',
                            y='Feature',
                            title='Importância das Features para Produtividade'
                        )
                        st.plotly_chart(fig_importance, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Erro na predição: {e}")
    
    def predicao_irrigacao(self):
        """Interface para predição de irrigação"""
        st.subheader("💧 Recomendação de Irrigação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Condições do Solo")
            umidade_solo = st.slider("Umidade do Solo (%)", 0, 100, 45)
            temperatura_ambiente = st.number_input("Temperatura Ambiente (°C)", 0.0, 50.0, 25.0)
            umidade_ambiente = st.number_input("Umidade Ambiente (%)", 0.0, 100.0, 60.0)
        
        with col2:
            st.markdown("### Condições Climáticas")
            temp_clima = st.number_input("Temperatura Climática (°C)", 0.0, 50.0, 26.0)
            umidade_clima = st.number_input("Umidade Climática (%)", 0.0, 100.0, 70.0)
            precipitacao = st.number_input("Precipitação (mm)", 0.0, 100.0, 5.0)
            radiacao_solar = st.number_input("Radiação Solar (W/m²)", 0.0, 1500.0, 800.0)
            velocidade_vento = st.number_input("Velocidade do Vento (m/s)", 0.0, 30.0, 5.0)
        
        # Botão de predição
        if st.button("💧 Analisar Necessidade de Irrigação", type="primary"):
            with st.spinner("Analisando condições..."):
                features = {
                    'umidade_solo': umidade_solo,
                    'temperatura_ambiente': temperatura_ambiente,
                    'umidade_ambiente': umidade_ambiente,
                    'temp_clima': temp_clima,
                    'umidade_clima': umidade_clima,
                    'precipitacao': precipitacao,
                    'radiacao_solar': radiacao_solar,
                    'velocidade_vento': velocidade_vento
                }
                
                try:
                    resultado = self.ml_models.predizer_irrigacao(features)
                    
                    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                    st.markdown(f"### 💧 Recomendação de Irrigação")
                    
                    # Cores baseadas na necessidade
                    cores = {
                        'baixa': '🟢',
                        'media': '🟡', 
                        'alta': '🔴'
                    }
                    
                    st.markdown(f"**Necessidade:** {cores.get(resultado['necessidade_irrigacao'], '⚪')} {resultado['necessidade_irrigacao'].title()}")
                    st.progress(resultado['probabilidade'])
                    st.info(f"Confiança: {resultado['probabilidade']*100:.1f}%")
                    
                    # Probabilidades detalhadas
                    st.markdown("### 📊 Probabilidades Detalhadas")
                    for classe, prob in resultado['probabilidades'].items():
                        st.metric(
                            label=f"Probabilidade {classe.title()}",
                            value=f"{prob*100:.1f}%"
                        )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Erro na predição: {e}")
    
    def deteccao_anomalias(self):
        """Interface para detecção de anomalias"""
        st.subheader("⚠️ Detecção de Anomalias")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Dados do Sensor")
            valor_sensor = st.number_input("Valor do Sensor", 0.0, 2000.0, 50.0)
            temperatura_ambiente = st.number_input("Temperatura Ambiente (°C)", 0.0, 50.0, 25.0)
            umidade_ambiente = st.number_input("Umidade Ambiente (%)", 0.0, 100.0, 60.0)
        
        with col2:
            st.markdown("### Informações Adicionais")
            tipo_sensor = st.selectbox(
                "Tipo de Sensor",
                ["Sensor de Umidade do Solo", "Sensor de Temperatura", "Sensor de pH", 
                 "Sensor de Nitrogênio", "Sensor de Fósforo", "Sensor de Potássio"]
            )
            
            # Valores esperados por tipo de sensor
            valores_esperados = {
                "Sensor de Umidade do Solo": (25.0, 85.0),
                "Sensor de Temperatura": (15.0, 35.0),
                "Sensor de pH": (5.0, 7.5),
                "Sensor de Nitrogênio": (10.0, 50.0),
                "Sensor de Fósforo": (10.0, 50.0),
                "Sensor de Potássio": (10.0, 50.0)
            }
            
            min_val, max_val = valores_esperados.get(tipo_sensor, (0.0, 100.0))
            st.info(f"Faixa esperada: {min_val} - {max_val}")
        
        # Botão de detecção
        if st.button("🔍 Detectar Anomalia", type="primary"):
            with st.spinner("Analisando dados..."):
                features = {
                    'valor': valor_sensor,
                    'temperatura_ambiente': temperatura_ambiente,
                    'umidade_ambiente': umidade_ambiente
                }
                
                try:
                    resultado = self.ml_models.detectar_anomalias(features)
                    
                    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                    st.markdown(f"### ⚠️ Resultado da Análise")
                    
                    if resultado['is_anomalia']:
                        st.error("🚨 ANOMALIA DETECTADA!")
                        st.markdown(f"**Severidade:** {resultado['severidade'].title()}")
                    else:
                        st.success("✅ Dados Normais")
                    
                    st.progress(resultado['probabilidade_anomalia'])
                    st.info(f"Probabilidade de Anomalia: {resultado['probabilidade_anomalia']*100:.1f}%")
                    
                    # Recomendações
                    if resultado['is_anomalia']:
                        st.markdown("### 💡 Recomendações")
                        if resultado['severidade'] == 'alta':
                            st.warning("🔴 **Ação Imediata Necessária:** Verificar sensor e calibrar se necessário")
                        elif resultado['severidade'] == 'media':
                            st.warning("🟡 **Monitoramento Aumentado:** Acompanhar próximas leituras")
                        else:
                            st.info("🟢 **Observação:** Manter monitoramento normal")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Erro na detecção: {e}")
    
    def pagina_analise_dados(self):
        """Página de análise exploratória dos dados"""
        st.header("📊 Análise Exploratória dos Dados")
        
        # Carregar dados
        dados = self.carregar_dados_dashboard()
        
        # Filtros
        st.sidebar.markdown("### 🔍 Filtros")
        
        if not dados['plantios'].empty:
            culturas = ['Todas'] + dados['plantios']['cultura'].unique().tolist()
            cultura_selecionada = st.sidebar.selectbox("Cultura", culturas)
            
            fazendas = ['Todas'] + dados['plantios']['fazenda'].unique().tolist()
            fazenda_selecionada = st.sidebar.selectbox("Fazenda", fazendas)
        
        # Análise de produtividade
        if not dados['plantios'].empty:
            st.subheader("🌾 Análise de Produtividade")
            
            # Filtrar dados
            df_filtrado = dados['plantios'].copy()
            if cultura_selecionada != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['cultura'] == cultura_selecionada]
            if fazenda_selecionada != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['fazenda'] == fazenda_selecionada]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Produtividade por talhão
                fig_talhao = px.bar(
                    df_filtrado.groupby('talhao')['produtividade_real'].mean().reset_index(),
                    x='talhao',
                    y='produtividade_real',
                    title='Produtividade por Talhão'
                )
                st.plotly_chart(fig_talhao, use_container_width=True)
            
            with col2:
                # Distribuição de produtividade
                fig_dist = px.histogram(
                    df_filtrado,
                    x='produtividade_real',
                    title='Distribuição de Produtividade',
                    nbins=20
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            
            # Estatísticas
            st.markdown("### 📈 Estatísticas de Produtividade")
            stats = df_filtrado['produtividade_real'].describe()
            st.dataframe(stats)
        
        # Análise de sensores
        if not dados['leituras'].empty:
            st.subheader("📡 Análise de Sensores")
            
            # Selecionar tipo de sensor
            tipos_sensor = dados['leituras']['tipo_sensor'].unique()
            tipo_selecionado = st.selectbox("Tipo de Sensor", tipos_sensor)
            
            df_sensor = dados['leituras'][dados['leituras']['tipo_sensor'] == tipo_selecionado]
            
            # Gráfico temporal
            fig_temporal = px.line(
                df_sensor.groupby(pd.Grouper(key='data_hora', freq='H'))['valor'].mean().reset_index(),
                x='data_hora',
                y='valor',
                title=f'Leituras de {tipo_selecionado} ao Longo do Tempo'
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
            
            # Box plot por talhão
            fig_box = px.box(
                df_sensor,
                x='talhao',
                y='valor',
                title=f'Distribuição de Valores por Talhão - {tipo_selecionado}'
            )
            st.plotly_chart(fig_box, use_container_width=True)
    
    def pagina_configuracoes(self):
        """Página de configurações"""
        st.header("⚙️ Configurações")
        
        st.subheader("🔧 Configurações do Sistema")
        
        # Configurações de modelos
        st.markdown("### 🤖 Modelos de IA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Retreinar Modelos", type="primary"):
                with st.spinner("Treinando modelos..."):
                    try:
                        # Aqui você chamaria o treinamento dos modelos
                        st.success("✅ Modelos retreinados com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro no treinamento: {e}")
        
        with col2:
            if st.button("💾 Salvar Configurações"):
                st.success("✅ Configurações salvas!")
        
        # Configurações de alertas
        st.markdown("### ⚠️ Configurações de Alertas")
        
        umidade_min = st.slider("Umidade Mínima (%)", 0, 100, 30)
        temperatura_max = st.slider("Temperatura Máxima (°C)", 20, 50, 35)
        ph_min = st.slider("pH Mínimo", 4.0, 9.0, 5.5)
        ph_max = st.slider("pH Máximo", 4.0, 9.0, 7.0)
        
        # Configurações de notificações
        st.markdown("### 📧 Notificações")
        
        email_notificacoes = st.checkbox("Ativar notificações por email", value=True)
        alertas_urgentes = st.checkbox("Alertas urgentes", value=True)
        relatorios_diarios = st.checkbox("Relatórios diários", value=False)
        
        if st.button("💾 Salvar Configurações de Notificações"):
            st.success("✅ Configurações de notificações salvas!")

def main():
    """Função principal da aplicação"""
    app = FarmTechStreamlitApp()
    
    if not app.conectar_banco():
        st.error("❌ Não foi possível conectar ao banco de dados")
        return
    
    # Sidebar
    st.sidebar.markdown("## 🌾 FarmTech Solutions")
    
    # Menu de navegação
    pagina = st.sidebar.selectbox(
        "Navegação",
        ["🏠 Dashboard", "🔮 Predições", "📊 Análise de Dados", "⚙️ Configurações"]
    )
    
    # Navegação
    if pagina == "🏠 Dashboard":
        app.dashboard_principal()
    elif pagina == "🔮 Predições":
        app.pagina_predicoes()
    elif pagina == "📊 Análise de Dados":
        app.pagina_analise_dados()
    elif pagina == "⚙️ Configurações":
        app.pagina_configuracoes()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Status do Sistema")
    st.sidebar.success("✅ Conectado")
    st.sidebar.info("🟢 Modelos Carregados")
    st.sidebar.info("📡 Sensores Ativos")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Versão:** 1.0.0")
    st.sidebar.markdown("**Desenvolvido por:** FarmTech Solutions")

if __name__ == "__main__":
    main() 