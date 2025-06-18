#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Modelos de ML Específicos
Modelos especializados para diferentes tipos de predições
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Dict, Any, List, Tuple
import joblib
from pathlib import Path

from ..core.logger import get_ml_logger

logger = get_ml_logger()

class IrrigationPredictor:
    """Modelo especializado para predição de irrigação"""
    
    def __init__(self, model_path: str = 'models/'):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = StandardScaler()
        self.logger = get_ml_logger()
    
    def train(self, data: pd.DataFrame):
        """Treina o modelo de irrigação"""
        try:
            # Preparar dados
            X = data[['humidity', 'temperature', 'soil_type', 'crop_type']]
            y = data['needs_irrigation']
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            self.logger.info(f"Modelo de irrigação treinado - Acurácia: {accuracy:.3f}")
            self.logger.info(f"Precisão: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
            # Salvar modelo
            self.save_model()
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo de irrigação: {e}")
            raise
    
    def predict(self, humidity: float, temperature: float, 
               soil_type: str, crop_type: str) -> Dict[str, Any]:
        """Faz predição de irrigação"""
        try:
            if self.model is None:
                self.load_model()
            
            # Preparar features
            features = np.array([[
                humidity, temperature, 
                self._encode_soil_type(soil_type),
                self._encode_crop_type(crop_type)
            ]])
            
            # Escalar features
            features_scaled = self.scaler.transform(features)
            
            # Fazer predição
            prediction = self.model.predict_proba(features_scaled)[0]
            needs_irrigation = prediction[1] > 0.5
            confidence = max(prediction)
            
            return {
                'needs_irrigation': needs_irrigation,
                'confidence': confidence,
                'probability': prediction[1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de irrigação: {e}")
            raise
    
    def _encode_soil_type(self, soil_type: str) -> int:
        """Codifica tipo de solo"""
        encoding = {'argiloso': 0, 'arenoso': 1, 'siltoso': 2}
        return encoding.get(soil_type, 0)
    
    def _encode_crop_type(self, crop_type: str) -> int:
        """Codifica tipo de cultura"""
        encoding = {'milho': 0, 'soja': 1, 'trigo': 2, 'arroz': 3}
        return encoding.get(crop_type, 0)
    
    def save_model(self):
        """Salva o modelo treinado"""
        try:
            model_file = self.model_path / 'irrigation_model.pkl'
            scaler_file = self.model_path / 'irrigation_scaler.pkl'
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            
            self.logger.info("Modelo de irrigação salvo com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo de irrigação: {e}")
            raise
    
    def load_model(self):
        """Carrega o modelo treinado"""
        try:
            model_file = self.model_path / 'irrigation_model.pkl'
            scaler_file = self.model_path / 'irrigation_scaler.pkl'
            
            if model_file.exists() and scaler_file.exists():
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.logger.info("Modelo de irrigação carregado com sucesso")
            else:
                self.logger.warning("Modelo de irrigação não encontrado")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo de irrigação: {e}")
            raise

class NutrientPredictor:
    """Modelo especializado para predição de nutrientes"""
    
    def __init__(self, model_path: str = 'models/'):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = StandardScaler()
        self.logger = get_ml_logger()
    
    def train(self, data: pd.DataFrame):
        """Treina o modelo de nutrientes"""
        try:
            # Preparar dados
            X = data[['current_level', 'crop_type', 'growth_stage', 'days_since_last_application']]
            y = data['needs_nutrients']
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            self.logger.info(f"Modelo de nutrientes treinado - Acurácia: {accuracy:.3f}")
            self.logger.info(f"Precisão: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
            # Salvar modelo
            self.save_model()
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo de nutrientes: {e}")
            raise
    
    def predict(self, current_level: float, crop_type: str, 
               growth_stage: str, days_since_last: int = 30) -> Dict[str, Any]:
        """Faz predição de nutrientes"""
        try:
            if self.model is None:
                self.load_model()
            
            # Preparar features
            features = np.array([[
                current_level,
                self._encode_crop_type(crop_type),
                self._encode_growth_stage(growth_stage),
                days_since_last
            ]])
            
            # Escalar features
            features_scaled = self.scaler.transform(features)
            
            # Fazer predição
            prediction = self.model.predict_proba(features_scaled)[0]
            needs_nutrients = prediction[1] > 0.5
            confidence = max(prediction)
            
            return {
                'needs_nutrients': needs_nutrients,
                'confidence': confidence,
                'probability': prediction[1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de nutrientes: {e}")
            raise
    
    def _encode_crop_type(self, crop_type: str) -> int:
        """Codifica tipo de cultura"""
        encoding = {'milho': 0, 'soja': 1, 'trigo': 2, 'arroz': 3}
        return encoding.get(crop_type, 0)
    
    def _encode_growth_stage(self, growth_stage: str) -> int:
        """Codifica estágio de crescimento"""
        encoding = {'vegetativo': 0, 'florescimento': 1, 'frutificação': 2, 'maturacao': 3}
        return encoding.get(growth_stage, 0)
    
    def save_model(self):
        """Salva o modelo treinado"""
        try:
            model_file = self.model_path / 'nutrient_model.pkl'
            scaler_file = self.model_path / 'nutrient_scaler.pkl'
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            
            self.logger.info("Modelo de nutrientes salvo com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo de nutrientes: {e}")
            raise
    
    def load_model(self):
        """Carrega o modelo treinado"""
        try:
            model_file = self.model_path / 'nutrient_model.pkl'
            scaler_file = self.model_path / 'nutrient_scaler.pkl'
            
            if model_file.exists() and scaler_file.exists():
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.logger.info("Modelo de nutrientes carregado com sucesso")
            else:
                self.logger.warning("Modelo de nutrientes não encontrado")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo de nutrientes: {e}")
            raise

class DiseasePredictor:
    """Modelo especializado para predição de doenças"""
    
    def __init__(self, model_path: str = 'models/'):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = StandardScaler()
        self.logger = get_ml_logger()
    
    def train(self, data: pd.DataFrame):
        """Treina o modelo de doenças"""
        try:
            # Preparar dados
            X = data[['humidity', 'temperature', 'leaf_wetness', 'rainfall', 'wind_speed']]
            y = data['disease_risk']
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            self.logger.info(f"Modelo de doenças treinado - Acurácia: {accuracy:.3f}")
            self.logger.info(f"Precisão: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
            # Salvar modelo
            self.save_model()
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo de doenças: {e}")
            raise
    
    def predict(self, humidity: float, temperature: float, leaf_wetness: float = 0.0,
               rainfall: float = 0.0, wind_speed: float = 0.0) -> Dict[str, Any]:
        """Faz predição de doenças"""
        try:
            if self.model is None:
                self.load_model()
            
            # Preparar features
            features = np.array([[
                humidity, temperature, leaf_wetness, rainfall, wind_speed
            ]])
            
            # Escalar features
            features_scaled = self.scaler.transform(features)
            
            # Fazer predição
            prediction = self.model.predict_proba(features_scaled)[0]
            disease_risk = prediction[1] > 0.5
            confidence = max(prediction)
            
            return {
                'disease_risk': disease_risk,
                'confidence': confidence,
                'probability': prediction[1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de doenças: {e}")
            raise
    
    def save_model(self):
        """Salva o modelo treinado"""
        try:
            model_file = self.model_path / 'disease_model.pkl'
            scaler_file = self.model_path / 'disease_scaler.pkl'
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            
            self.logger.info("Modelo de doenças salvo com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo de doenças: {e}")
            raise
    
    def load_model(self):
        """Carrega o modelo treinado"""
        try:
            model_file = self.model_path / 'disease_model.pkl'
            scaler_file = self.model_path / 'disease_scaler.pkl'
            
            if model_file.exists() and scaler_file.exists():
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.logger.info("Modelo de doenças carregado com sucesso")
            else:
                self.logger.warning("Modelo de doenças não encontrado")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo de doenças: {e}")
            raise 