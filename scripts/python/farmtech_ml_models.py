#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Módulo de Machine Learning
Modelos preditivos para agricultura de precisão usando Scikit-learn
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import joblib
import json
import logging
from typing import Dict, List, Tuple, Optional

# Scikit-learn imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FarmTechMLModels:
    """Classe principal para modelos de machine learning do FarmTech"""
    
    def __init__(self, db_path='data/farmtech_aprimorado.db'):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Conectado ao banco: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return False
    
    def carregar_dados_produtividade(self) -> pd.DataFrame:
        """Carrega dados para modelo de produtividade"""
        query = """
        SELECT 
            p.plantio_id,
            COALESCE(p.producao_real, p.producao_estimada) as producao_real,
            COALESCE(p.produtividade_real, p.produtividade_estimada) as produtividade_real,
            p.area_plantada,
            p.densidade_plantio,
            c.ciclo_vida,
            c.ph_ideal_min,
            c.ph_ideal_max,
            c.umidade_ideal_min,
            c.umidade_ideal_max,
            c.temperatura_ideal_min,
            c.temperatura_ideal_max,
            AVG(l.valor) as media_umidade,
            AVG(CASE WHEN ts.nome LIKE '%Temperatura%' THEN l.valor END) as media_temperatura,
            AVG(CASE WHEN ts.nome LIKE '%pH%' THEN l.valor END) as media_ph,
            AVG(CASE WHEN ts.nome LIKE '%Nitrogênio%' THEN l.valor END) as media_nitrogenio,
            AVG(CASE WHEN ts.nome LIKE '%Fósforo%' THEN l.valor END) as media_fosforo,
            AVG(CASE WHEN ts.nome LIKE '%Potássio%' THEN l.valor END) as media_potassio,
            AVG(dc.temperatura) as media_temp_clima,
            AVG(dc.umidade_relativa) as media_umidade_clima,
            AVG(dc.precipitacao) as media_precipitacao,
            COUNT(l.leitura_id) as total_leituras
        FROM PLANTIO p
        JOIN CULTURA c ON p.cultura_id = c.cultura_id
        JOIN TALHAO t ON p.talhao_id = t.talhao_id
        JOIN SENSOR s ON t.talhao_id = s.talhao_id
        JOIN TIPO_SENSOR ts ON s.tipo_sensor_id = ts.tipo_sensor_id
        LEFT JOIN LEITURA l ON s.sensor_id = l.sensor_id
        LEFT JOIN DADOS_CLIMA dc ON t.talhao_id = dc.talhao_id
        GROUP BY p.plantio_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Se não há dados suficientes, gerar dados simulados
        if len(df) < 3:
            logger.info("Gerando dados simulados para demonstração...")
            df = self._gerar_dados_simulados_produtividade()
        
        logger.info(f"Carregados {len(df)} registros para modelo de produtividade")
        return df
    
    def _gerar_dados_simulados_produtividade(self) -> pd.DataFrame:
        """Gera dados simulados para demonstração do modelo de produtividade"""
        import random
        
        # Dados base para simulação
        dados_base = [
            # plantio_id, area_plantada, densidade_plantio, ciclo_vida, produtividade_real
            (1, 100.0, 250000, 120, 2.5),
            (2, 150.0, 60000, 150, 3.0),
            (3, 80.0, 120000, 180, 1.8),
            (4, 180.0, 200000, 90, 2.0),
            (5, 250.0, 150000, 130, 2.5),
            (6, 120.0, 180000, 110, 2.8),
            (7, 200.0, 80000, 160, 3.2),
            (8, 90.0, 220000, 100, 2.2),
            (9, 300.0, 70000, 140, 3.5),
            (10, 160.0, 160000, 125, 2.7)
        ]
        
        registros = []
        
        for plantio_id, area, densidade, ciclo, produtividade in dados_base:
            # Simular variações baseadas em condições
            variacao = random.uniform(0.8, 1.2)
            produtividade_final = produtividade * variacao
            
            # Simular condições ambientais
            media_umidade = random.uniform(55.0, 85.0)
            media_temperatura = random.uniform(20.0, 30.0)
            media_ph = random.uniform(5.5, 7.0)
            media_nitrogenio = random.uniform(20.0, 40.0)
            media_fosforo = random.uniform(15.0, 35.0)
            media_potassio = random.uniform(25.0, 45.0)
            media_temp_clima = random.uniform(22.0, 28.0)
            media_umidade_clima = random.uniform(60.0, 80.0)
            media_precipitacao = random.uniform(10.0, 30.0)
            total_leituras = random.randint(800, 1200)
            
            # Condições ideais baseadas no tipo de cultura
            ph_min = random.uniform(5.5, 6.5)
            ph_max = ph_min + random.uniform(0.5, 1.5)
            umidade_min = random.uniform(55.0, 70.0)
            umidade_max = umidade_min + random.uniform(15.0, 25.0)
            temp_min = random.uniform(18.0, 25.0)
            temp_max = temp_min + random.uniform(8.0, 15.0)
            
            registros.append({
                'plantio_id': plantio_id,
                'producao_real': produtividade_final * area,
                'produtividade_real': produtividade_final,
                'area_plantada': area,
                'densidade_plantio': densidade,
                'ciclo_vida': ciclo,
                'ph_ideal_min': ph_min,
                'ph_ideal_max': ph_max,
                'umidade_ideal_min': umidade_min,
                'umidade_ideal_max': umidade_max,
                'temperatura_ideal_min': temp_min,
                'temperatura_ideal_max': temp_max,
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
            })
        
        return pd.DataFrame(registros)
    
    def carregar_dados_irrigacao(self) -> pd.DataFrame:
        """Carrega dados para modelo de irrigação"""
        query = """
        SELECT 
            l.leitura_id,
            l.valor as umidade_solo,
            l.temperatura_ambiente,
            l.umidade_ambiente,
            dc.temperatura as temp_clima,
            dc.umidade_relativa as umidade_clima,
            dc.precipitacao,
            dc.radiacao_solar,
            dc.velocidade_vento,
            CASE 
                WHEN l.valor < 30 THEN 'baixa'
                WHEN l.valor < 60 THEN 'media'
                ELSE 'alta'
            END as necessidade_irrigacao
        FROM LEITURA l
        JOIN SENSOR s ON l.sensor_id = s.sensor_id
        JOIN TALHAO t ON s.talhao_id = t.talhao_id
        JOIN TIPO_SENSOR ts ON s.tipo_sensor_id = ts.tipo_sensor_id
        LEFT JOIN DADOS_CLIMA dc ON t.talhao_id = dc.talhao_id 
            AND DATE(l.data_hora) = DATE(dc.data_hora)
        WHERE ts.nome LIKE '%Umidade%'
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Se não há dados suficientes, gerar dados simulados
        if len(df) < 10:
            logger.info("Gerando dados simulados de irrigação para demonstração...")
            df = self._gerar_dados_simulados_irrigacao()
        
        logger.info(f"Carregados {len(df)} registros para modelo de irrigação")
        return df
    
    def _gerar_dados_simulados_irrigacao(self) -> pd.DataFrame:
        """Gera dados simulados para demonstração do modelo de irrigação"""
        import random
        
        registros = []
        
        for i in range(100):  # 100 registros simulados
            # Simular condições variadas
            umidade_solo = random.uniform(20.0, 90.0)
            temperatura_ambiente = random.uniform(15.0, 35.0)
            umidade_ambiente = random.uniform(40.0, 90.0)
            temp_clima = random.uniform(18.0, 32.0)
            umidade_clima = random.uniform(45.0, 85.0)
            precipitacao = random.uniform(0.0, 50.0)
            radiacao_solar = random.uniform(0.0, 1200.0)
            velocidade_vento = random.uniform(0.0, 15.0)
            
            # Determinar necessidade baseada nas condições
            if umidade_solo < 30:
                necessidade = 'alta'
            elif umidade_solo < 60:
                necessidade = 'media'
            else:
                necessidade = 'baixa'
            
            registros.append({
                'leitura_id': i + 1,
                'umidade_solo': umidade_solo,
                'temperatura_ambiente': temperatura_ambiente,
                'umidade_ambiente': umidade_ambiente,
                'temp_clima': temp_clima,
                'umidade_clima': umidade_clima,
                'precipitacao': precipitacao,
                'radiacao_solar': radiacao_solar,
                'velocidade_vento': velocidade_vento,
                'necessidade_irrigacao': necessidade
            })
        
        return pd.DataFrame(registros)
    
    def carregar_dados_anomalias(self) -> pd.DataFrame:
        """Carrega dados para detecção de anomalias"""
        query = """
        SELECT 
            l.leitura_id,
            l.valor,
            l.unidade_medida,
            l.temperatura_ambiente,
            l.umidade_ambiente,
            ts.nome as tipo_sensor,
            t.nome as talhao,
            c.nome as cultura,
            CASE 
                WHEN l.valor < 0 OR l.valor > 1000 THEN 1
                ELSE 0
            END as is_anomalia
        FROM LEITURA l
        JOIN SENSOR s ON l.sensor_id = s.sensor_id
        JOIN TIPO_SENSOR ts ON s.tipo_sensor_id = ts.tipo_sensor_id
        JOIN TALHAO t ON s.talhao_id = t.talhao_id
        LEFT JOIN PLANTIO p ON t.talhao_id = p.talhao_id
        LEFT JOIN CULTURA c ON p.cultura_id = c.cultura_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Se não há dados suficientes, gerar dados simulados
        if len(df) < 10:
            logger.info("Gerando dados simulados de anomalias para demonstração...")
            df = self._gerar_dados_simulados_anomalias()
        
        logger.info(f"Carregados {len(df)} registros para detecção de anomalias")
        return df
    
    def _gerar_dados_simulados_anomalias(self) -> pd.DataFrame:
        """Gera dados simulados para demonstração da detecção de anomalias"""
        import random
        
        registros = []
        
        for i in range(200):  # 200 registros simulados
            # Simular dados normais (80%) e anômalos (20%)
            if random.random() < 0.8:
                # Dados normais
                valor = random.uniform(10.0, 100.0)
                is_anomalia = 0
            else:
                # Dados anômalos
                if random.random() < 0.5:
                    valor = random.uniform(-50.0, -1.0)  # Valores negativos
                else:
                    valor = random.uniform(1001.0, 2000.0)  # Valores muito altos
                is_anomalia = 1
            
            temperatura_ambiente = random.uniform(20.0, 30.0)
            umidade_ambiente = random.uniform(50.0, 80.0)
            
            registros.append({
                'leitura_id': i + 1,
                'valor': valor,
                'unidade_medida': 'unidade',
                'temperatura_ambiente': temperatura_ambiente,
                'umidade_ambiente': umidade_ambiente,
                'tipo_sensor': 'Sensor Simulado',
                'talhao': 'Talhão Simulado',
                'cultura': 'Cultura Simulada',
                'is_anomalia': is_anomalia
            })
        
        return pd.DataFrame(registros)
    
    def preparar_dados_produtividade(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados para modelo de produtividade"""
        # Selecionar features
        features = [
            'area_plantada', 'densidade_plantio', 'ciclo_vida',
            'ph_ideal_min', 'ph_ideal_max', 'umidade_ideal_min', 'umidade_ideal_max',
            'temperatura_ideal_min', 'temperatura_ideal_max', 'media_umidade',
            'media_temperatura', 'media_ph', 'media_nitrogenio', 'media_fosforo',
            'media_potassio', 'media_temp_clima', 'media_umidade_clima',
            'media_precipitacao', 'total_leituras'
        ]
        
        X = df[features].fillna(df[features].mean())
        y = df['produtividade_real'].fillna(df['produtividade_real'].mean())
        
        return X.values, y.values
    
    def preparar_dados_irrigacao(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados para modelo de irrigação"""
        features = [
            'umidade_solo', 'temperatura_ambiente', 'umidade_ambiente',
            'temp_clima', 'umidade_clima', 'precipitacao', 'radiacao_solar',
            'velocidade_vento'
        ]
        
        X = df[features].fillna(df[features].mean())
        
        # Codificar target
        le = LabelEncoder()
        y = le.fit_transform(df['necessidade_irrigacao'])
        self.label_encoders['irrigacao'] = le
        
        return X.values, y
    
    def preparar_dados_anomalias(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados para detecção de anomalias"""
        features = ['valor', 'temperatura_ambiente', 'umidade_ambiente']
        
        X = df[features].fillna(df[features].mean())
        y = df['is_anomalia'].values
        
        return X.values, y
    
    def treinar_modelo_produtividade(self) -> Dict:
        """Treina modelo de predição de produtividade"""
        logger.info("Treinando modelo de produtividade...")
        
        # Carregar dados
        df = self.carregar_dados_produtividade()
        X, y = self.preparar_dados_produtividade(df)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Pipeline com pré-processamento
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Treinar modelo
        pipeline.fit(X_train, y_train)
        
        # Avaliar
        y_pred = pipeline.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Feature importance
        feature_names = [
            'area_plantada', 'densidade_plantio', 'ciclo_vida',
            'ph_ideal_min', 'ph_ideal_max', 'umidade_ideal_min', 'umidade_ideal_max',
            'temperatura_ideal_min', 'temperatura_ideal_max', 'media_umidade',
            'media_temperatura', 'media_ph', 'media_nitrogenio', 'media_fosforo',
            'media_potassio', 'media_temp_clima', 'media_umidade_clima',
            'media_precipitacao', 'total_leituras'
        ]
        
        feature_importance = dict(zip(feature_names, pipeline.named_steps['regressor'].feature_importances_))
        
        # Salvar modelo
        self.models['produtividade'] = pipeline
        self.feature_importance['produtividade'] = feature_importance
        
        resultados = {
            'modelo': 'RandomForest',
            'mse': mse,
            'r2': r2,
            'feature_importance': feature_importance,
            'n_amostras': len(X),
            'n_features': X.shape[1]
        }
        
        logger.info(f"Modelo de produtividade treinado - R²: {r2:.3f}, MSE: {mse:.3f}")
        return resultados
    
    def treinar_modelo_irrigacao(self) -> Dict:
        """Treina modelo de recomendação de irrigação"""
        logger.info("Treinando modelo de irrigação...")
        
        # Carregar dados
        df = self.carregar_dados_irrigacao()
        X, y = self.preparar_dados_irrigacao(df)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # Treinar modelo
        pipeline.fit(X_train, y_train)
        
        # Avaliar
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Feature importance
        feature_names = [
            'umidade_solo', 'temperatura_ambiente', 'umidade_ambiente',
            'temp_clima', 'umidade_clima', 'precipitacao', 'radiacao_solar',
            'velocidade_vento'
        ]
        
        feature_importance = dict(zip(feature_names, pipeline.named_steps['classifier'].feature_importances_))
        
        # Salvar modelo
        self.models['irrigacao'] = pipeline
        self.feature_importance['irrigacao'] = feature_importance
        
        resultados = {
            'modelo': 'RandomForest',
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'n_amostras': len(X),
            'n_features': X.shape[1],
            'classes': self.label_encoders['irrigacao'].classes_.tolist()
        }
        
        logger.info(f"Modelo de irrigação treinado - Accuracy: {accuracy:.3f}")
        return resultados
    
    def treinar_modelo_anomalias(self) -> Dict:
        """Treina modelo de detecção de anomalias"""
        logger.info("Treinando modelo de detecção de anomalias...")
        
        # Carregar dados
        df = self.carregar_dados_anomalias()
        X, y = self.preparar_dados_anomalias(df)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # Treinar modelo
        pipeline.fit(X_train, y_train)
        
        # Avaliar
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Feature importance
        feature_names = ['valor', 'temperatura_ambiente', 'umidade_ambiente']
        feature_importance = dict(zip(feature_names, pipeline.named_steps['classifier'].feature_importances_))
        
        # Salvar modelo
        self.models['anomalias'] = pipeline
        self.feature_importance['anomalias'] = feature_importance
        
        resultados = {
            'modelo': 'RandomForest',
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'n_amostras': len(X),
            'n_features': X.shape[1],
            'n_anomalias': sum(y)
        }
        
        logger.info(f"Modelo de anomalias treinado - Accuracy: {accuracy:.3f}")
        return resultados
    
    def predizer_produtividade(self, features: Dict) -> Dict:
        """Faz predição de produtividade"""
        if 'produtividade' not in self.models:
            raise ValueError("Modelo de produtividade não treinado")
        
        # Preparar features
        feature_names = [
            'area_plantada', 'densidade_plantio', 'ciclo_vida',
            'ph_ideal_min', 'ph_ideal_max', 'umidade_ideal_min', 'umidade_ideal_max',
            'temperatura_ideal_min', 'temperatura_ideal_max', 'media_umidade',
            'media_temperatura', 'media_ph', 'media_nitrogenio', 'media_fosforo',
            'media_potassio', 'media_temp_clima', 'media_umidade_clima',
            'media_precipitacao', 'total_leituras'
        ]
        
        X = np.array([[features.get(f, 0) for f in feature_names]])
        
        # Predição
        predicao = self.models['produtividade'].predict(X)[0]
        
        return {
            'produtividade_prevista': float(predicao),
            'unidade': 'toneladas/hectare',
            'confianca': 0.85  # Placeholder
        }
    
    def predizer_irrigacao(self, features: Dict) -> Dict:
        """Faz predição de necessidade de irrigação"""
        if 'irrigacao' not in self.models:
            raise ValueError("Modelo de irrigação não treinado")
        
        # Preparar features
        feature_names = [
            'umidade_solo', 'temperatura_ambiente', 'umidade_ambiente',
            'temp_clima', 'umidade_clima', 'precipitacao', 'radiacao_solar',
            'velocidade_vento'
        ]
        
        X = np.array([[features.get(f, 0) for f in feature_names]])
        
        # Predição
        predicao = self.models['irrigacao'].predict(X)[0]
        probabilidade = self.models['irrigacao'].predict_proba(X)[0]
        
        classe = self.label_encoders['irrigacao'].inverse_transform([predicao])[0]
        
        return {
            'necessidade_irrigacao': classe,
            'probabilidade': float(max(probabilidade)),
            'probabilidades': dict(zip(self.label_encoders['irrigacao'].classes_, probabilidade))
        }
    
    def detectar_anomalias(self, features: Dict) -> Dict:
        """Detecta anomalias nos dados dos sensores"""
        if 'anomalias' not in self.models:
            raise ValueError("Modelo de anomalias não treinado")
        
        # Preparar features
        feature_names = ['valor', 'temperatura_ambiente', 'umidade_ambiente']
        X = np.array([[features.get(f, 0) for f in feature_names]])
        
        # Predição
        predicao = self.models['anomalias'].predict(X)[0]
        probabilidade = self.models['anomalias'].predict_proba(X)[0]
        
        return {
            'is_anomalia': bool(predicao),
            'probabilidade_anomalia': float(probabilidade[1]),
            'severidade': 'alta' if probabilidade[1] > 0.8 else 'media' if probabilidade[1] > 0.5 else 'baixa'
        }
    
    def salvar_modelos(self, path: str = 'models/'):
        """Salva todos os modelos treinados"""
        import os
        os.makedirs(path, exist_ok=True)
        
        for nome, modelo in self.models.items():
            joblib.dump(modelo, f"{path}{nome}_model.pkl")
        
        # Salvar encoders e feature importance
        with open(f"{path}label_encoders.json", 'w') as f:
            json.dump({k: v.classes_.tolist() for k, v in self.label_encoders.items()}, f)
        
        with open(f"{path}feature_importance.json", 'w') as f:
            json.dump(self.feature_importance, f)
        
        logger.info(f"Modelos salvos em {path}")
    
    def carregar_modelos(self, path: str = 'models/'):
        """Carrega modelos salvos"""
        for nome in ['produtividade', 'irrigacao', 'anomalias']:
            try:
                self.models[nome] = joblib.load(f"{path}{nome}_model.pkl")
            except FileNotFoundError:
                logger.warning(f"Modelo {nome} não encontrado")
        
        # Carregar encoders
        try:
            with open(f"{path}label_encoders.json", 'r') as f:
                encoders_data = json.load(f)
                for k, v in encoders_data.items():
                    le = LabelEncoder()
                    le.classes_ = np.array(v)
                    self.label_encoders[k] = le
        except FileNotFoundError:
            logger.warning("Encoders não encontrados")
        
        # Carregar feature importance
        try:
            with open(f"{path}feature_importance.json", 'r') as f:
                self.feature_importance = json.load(f)
        except FileNotFoundError:
            logger.warning("Feature importance não encontrado")
        
        logger.info("Modelos carregados com sucesso")
    
    def gerar_relatorio_modelos(self) -> Dict:
        """Gera relatório completo dos modelos"""
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'modelos_treinados': list(self.models.keys()),
            'metricas': {},
            'feature_importance': self.feature_importance
        }
        
        return relatorio

def main():
    """Função principal para treinar todos os modelos"""
    logger.info("=== TREINAMENTO DOS MODELOS FARM TECH ===")
    
    # Inicializar
    ml_models = FarmTechMLModels()
    
    if not ml_models.conectar_banco():
        logger.error("Não foi possível conectar ao banco")
        return
    
    try:
        # Treinar modelos
        resultados_produtividade = ml_models.treinar_modelo_produtividade()
        resultados_irrigacao = ml_models.treinar_modelo_irrigacao()
        resultados_anomalias = ml_models.treinar_modelo_anomalias()
        
        # Salvar modelos
        ml_models.salvar_modelos()
        
        # Gerar relatório
        relatorio = ml_models.gerar_relatorio_modelos()
        
        logger.info("=== TREINAMENTO CONCLUÍDO ===")
        logger.info(f"Modelo Produtividade - R²: {resultados_produtividade['r2']:.3f}")
        logger.info(f"Modelo Irrigação - Accuracy: {resultados_irrigacao['accuracy']:.3f}")
        logger.info(f"Modelo Anomalias - Accuracy: {resultados_anomalias['accuracy']:.3f}")
        
    except Exception as e:
        logger.error(f"Erro durante treinamento: {e}")
    
    finally:
        ml_models.conn.close()

if __name__ == "__main__":
    main() 