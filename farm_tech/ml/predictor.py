#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema de Predições ML
Algoritmos de machine learning para predições agrícolas
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import joblib
import os
from pathlib import Path
import json

from ..core.logger import get_ml_logger
from .irrigation_predictor import IrrigationPredictor
from .irrigation_optimizer import IrrigationOptimizer, IrrigationSchedule

logger = get_ml_logger()

class MLPredictor:
    """Sistema principal de predição com ML para FarmTech Solutions"""
    
    def __init__(self):
        self.irrigation_predictor = IrrigationPredictor()
        self.irrigation_optimizer = IrrigationOptimizer()
        self.models_loaded = False
        
        # Configurações
        self.config = {
            'prediction_horizon': 24,  # Horas
            'update_frequency': 3600,  # Segundos
            'min_confidence': 0.6,
            'enable_auto_optimization': True
        }
        
        # Carregar modelos treinados
        self.irrigation_model = self._load_model('irrigation_model.pkl')
        self.nutrient_model = self._load_model('nutrient_model.pkl')
        self.disease_model = self._load_model('disease_model.pkl')
        
        # Configurações de predição
        self.prediction_threshold = 0.7
        self.confidence_threshold = 0.6
    
    def _load_model(self, model_name: str):
        """Carrega modelo treinado"""
        model_path = Path('models/')
        model_path.mkdir(parents=True, exist_ok=True)
        model_file = model_path / model_name
        if model_file.exists():
            try:
                model = joblib.load(model_file)
                logger.info(f"Modelo {model_name} carregado com sucesso")
                return model
            except Exception as e:
                logger.warning(f"Erro ao carregar modelo {model_name}: {e}")
                return None
        else:
            logger.info(f"Modelo {model_name} não encontrado, usando regras simples")
            return None
    
    def initialize_models(self, db_manager) -> Dict[str, Any]:
        """Inicializar e treinar modelos de ML"""
        try:
            logger.info("Inicializando modelos de Machine Learning...")
            
            # Obter dados históricos para treinamento
            historical_data = self._get_historical_data(db_manager)
            
            if not historical_data:
                return {
                    'success': False,
                    'error': 'Dados históricos insuficientes para treinamento'
                }
            
            # Treinar modelo de irrigação
            irrigation_result = self.irrigation_predictor.train_model(historical_data)
            
            if not irrigation_result['success']:
                return irrigation_result
            
            self.models_loaded = True
            
            return {
                'success': True,
                'message': 'Modelos treinados com sucesso',
                'irrigation_model': irrigation_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao inicializar modelos: {str(e)}'
            }
    
    def _get_historical_data(self, db_manager) -> List[Dict]:
        """Obter dados históricos para treinamento"""
        try:
            # Obter leituras dos últimos 30 dias
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Buscar leituras de sensores
            readings = db_manager.get_readings_by_date_range(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not readings:
                return []
            
            # Formatar dados para o modelo
            formatted_data = []
            for reading in readings:
                # Buscar informações do sensor
                sensor_info = db_manager.get_sensor(reading['sensor_id'])
                if sensor_info:
                    formatted_data.append({
                        'sensor_id': reading['sensor_id'],
                        'tipo_sensor': sensor_info['tipo_sensor'],
                        'valor': reading['valor'],
                        'unidade_medida': reading['unidade_medida'],
                        'data_hora': reading['data_hora'],
                        'status_leitura': reading['status_leitura']
                    })
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos: {e}")
            return []
    
    def predict_irrigation_needs(self, sensor_data: List[Dict], 
                               areas_data: List[Dict] = None,
                               weather_forecast: Dict = None) -> List[Dict[str, Any]]:
        """Predizer necessidades de irrigação usando ML"""
        try:
            if not self.models_loaded:
                return [{'error': 'Modelos não inicializados'}]
            
            # Fazer predições usando o modelo treinado
            predictions = self.irrigation_predictor.predict_irrigation(
                sensor_data, 
                hours_ahead=self.config['prediction_horizon']
            )
            
            if not predictions or 'error' in predictions[0]:
                return predictions
            
            # Filtrar predições com confiança suficiente
            filtered_predictions = [
                pred for pred in predictions 
                if pred.get('confidence', 0) >= self.config['min_confidence']
            ]
            
            if not filtered_predictions:
                return [{'message': 'Nenhuma predição com confiança suficiente'}]
            
            # Se otimização automática está habilitada, criar agenda
            if self.config['enable_auto_optimization'] and areas_data:
                schedules = self.irrigation_optimizer.optimize_irrigation_schedule(
                    filtered_predictions,
                    areas_data,
                    weather_forecast
                )
                
                # Adicionar agenda às predições
                for pred in filtered_predictions:
                    pred['optimized_schedule'] = self._get_schedule_for_sensor(
                        pred['sensor_id'], schedules
                    )
            
            return filtered_predictions
            
        except Exception as e:
            return [{'error': f'Erro na predição: {str(e)}'}]
    
    def _get_schedule_for_sensor(self, sensor_id: int, 
                                schedules: List[IrrigationSchedule]) -> Optional[Dict]:
        """Obter agenda para um sensor específico"""
        for schedule in schedules:
            if schedule.sensor_id == sensor_id:
                return {
                    'start_time': schedule.start_time.isoformat(),
                    'duration_minutes': schedule.duration_minutes,
                    'water_amount_liters': schedule.water_amount_liters,
                    'priority': schedule.priority,
                    'cost_estimate': schedule.cost_estimate
                }
        return None
    
    def get_system_recommendations(self, db_manager, 
                                 include_irrigation: bool = True) -> List[Dict[str, Any]]:
        """Obter recomendações gerais do sistema"""
        try:
            recommendations = []
            
            # Obter dados recentes
            recent_readings = db_manager.get_recent_readings(hours=24)
            
            if not recent_readings:
                return [{'message': 'Nenhum dado recente disponível'}]
            
            # Analisar tendências
            trends = self._analyze_trends(recent_readings)
            
            # Gerar recomendações baseadas em tendências
            for trend in trends:
                if trend['severity'] == 'high':
                    recommendations.append({
                        'type': 'alert',
                        'title': f"Alerta: {trend['sensor_type']}",
                        'message': trend['description'],
                        'priority': 'high',
                        'action_required': True
                    })
                elif trend['severity'] == 'medium':
                    recommendations.append({
                        'type': 'warning',
                        'title': f"Aviso: {trend['sensor_type']}",
                        'message': trend['description'],
                        'priority': 'medium',
                        'action_required': False
                    })
            
            # Incluir recomendações de irrigação se solicitado
            if include_irrigation and self.models_loaded:
                irrigation_predictions = self.predict_irrigation_needs(recent_readings)
                
                for pred in irrigation_predictions:
                    if 'error' not in pred and pred.get('recommended_action') != 'NÃO IRRIGAR':
                        recommendations.append({
                            'type': 'irrigation',
                            'title': f"Irrigação Recomendada - Área {pred['sensor_id']}",
                            'message': f"{pred['recommended_action']}: {pred['reason']}",
                            'priority': pred['priority'].lower(),
                            'confidence': pred['confidence'],
                            'predicted_time': pred['recommended_time'],
                            'action_required': pred['priority'] == 'ALTA'
                        })
            
            return recommendations
            
        except Exception as e:
            return [{'error': f'Erro ao gerar recomendações: {str(e)}'}]
    
    def _analyze_trends(self, readings: List[Dict]) -> List[Dict]:
        """Analisar tendências nos dados"""
        trends = []
        
        # Agrupar por sensor
        sensor_groups = {}
        for reading in readings:
            sensor_id = reading['sensor_id']
            if sensor_id not in sensor_groups:
                sensor_groups[sensor_id] = []
            sensor_groups[sensor_id].append(reading)
        
        # Analisar cada sensor
        for sensor_id, sensor_readings in sensor_groups.items():
            if len(sensor_readings) < 3:
                continue
            
            # Ordenar por timestamp
            sensor_readings.sort(key=lambda x: x['data_hora'])
            
            # Calcular tendência
            values = [r['valor'] for r in sensor_readings]
            sensor_type = sensor_readings[0].get('tipo_sensor', 'unknown')
            
            # Análise de tendência simples
            if len(values) >= 3:
                recent_avg = np.mean(values[-3:])
                older_avg = np.mean(values[:-3]) if len(values) > 3 else values[0]
                
                change_percent = ((recent_avg - older_avg) / older_avg) * 100
                
                # Determinar severidade baseada no tipo de sensor
                severity = self._determine_severity(sensor_type, recent_avg, change_percent)
                
                if severity != 'low':
                    trends.append({
                        'sensor_id': sensor_id,
                        'sensor_type': sensor_type,
                        'current_value': recent_avg,
                        'change_percent': change_percent,
                        'severity': severity,
                        'description': self._generate_trend_description(
                            sensor_type, recent_avg, change_percent
                        )
                    })
        
        return trends
    
    def _determine_severity(self, sensor_type: str, current_value: float, 
                          change_percent: float) -> str:
        """Determinar severidade da tendência"""
        if 'umidade' in sensor_type.lower():
            if current_value < 30 or change_percent < -20:
                return 'high'
            elif current_value < 40 or change_percent < -10:
                return 'medium'
        elif 'ph' in sensor_type.lower():
            if current_value < 5.0 or current_value > 8.0 or abs(change_percent) > 15:
                return 'high'
            elif current_value < 5.5 or current_value > 7.5 or abs(change_percent) > 10:
                return 'medium'
        elif 'nutrientes' in sensor_type.lower():
            if current_value < 100 or change_percent < -25:
                return 'high'
            elif current_value < 150 or change_percent < -15:
                return 'medium'
        
        return 'low'
    
    def _generate_trend_description(self, sensor_type: str, current_value: float, 
                                  change_percent: float) -> str:
        """Gerar descrição da tendência"""
        if 'umidade' in sensor_type.lower():
            if current_value < 30:
                return f"Umidade muito baixa ({current_value:.1f}%) - irrigação urgente necessária"
            elif change_percent < -20:
                return f"Umidade diminuindo rapidamente ({change_percent:.1f}%) - monitorar de perto"
        elif 'ph' in sensor_type.lower():
            if current_value < 5.0 or current_value > 8.0:
                return f"pH fora do range crítico ({current_value:.1f}) - correção necessária"
            elif abs(change_percent) > 15:
                return f"pH mudando rapidamente ({change_percent:.1f}%) - investigar causa"
        elif 'nutrientes' in sensor_type.lower():
            if current_value < 100:
                return f"Nutrientes muito baixos ({current_value:.1f} ppm) - fertilização necessária"
            elif change_percent < -25:
                return f"Nutrientes diminuindo rapidamente ({change_percent:.1f}%) - investigar"
        
        return f"Valor atual: {current_value:.1f}, mudança: {change_percent:.1f}%"
    
    def get_model_status(self) -> Dict[str, Any]:
        """Obter status dos modelos"""
        irrigation_info = self.irrigation_predictor.get_model_info()
        
        return {
            'models_loaded': self.models_loaded,
            'irrigation_model': irrigation_info,
            'config': self.config,
            'last_update': datetime.now().isoformat()
        }
    
    def update_models(self, db_manager) -> Dict[str, Any]:
        """Atualizar modelos com novos dados"""
        try:
            logger.info("Atualizando modelos com novos dados...")
            
            # Obter dados mais recentes
            recent_data = self._get_historical_data(db_manager)
            
            if not recent_data:
                return {
                    'success': False,
                    'error': 'Dados insuficientes para atualização'
                }
            
            # Retreinar modelo de irrigação
            result = self.irrigation_predictor.train_model(recent_data)
            
            if result['success']:
                logger.info("Modelos atualizados com sucesso!")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao atualizar modelos: {str(e)}'
            }
    
    def export_predictions(self, predictions: List[Dict], 
                          format: str = 'json') -> str:
        """Exportar predições em diferentes formatos"""
        try:
            if format.lower() == 'json':
                return json.dumps(predictions, indent=2, default=str)
            elif format.lower() == 'csv':
                df = pd.DataFrame(predictions)
                return df.to_csv(index=False)
            else:
                return json.dumps(predictions, indent=2, default=str)
                
        except Exception as e:
            return f"Erro ao exportar: {str(e)}"

# Função de conveniência
def create_ml_predictor() -> MLPredictor:
    """Criar instância do preditor ML"""
    return MLPredictor()

def predict_irrigation_needs(self, humidity: float, temperature: float = 25.0,
                           soil_type: str = 'argiloso', crop_type: str = 'milho') -> Dict[str, Any]:
    """Prediz necessidade de irrigação"""
    try:
        # Se modelo ML disponível, usar
        if self.irrigation_model:
            features = self._prepare_irrigation_features(humidity, temperature, soil_type, crop_type)
            prediction = self.irrigation_model.predict_proba([features])[0]
            confidence = max(prediction)
            needs_irrigation = confidence > self.prediction_threshold
        else:
            # Regras simples baseadas em conhecimento de domínio
            needs_irrigation, confidence = self._simple_irrigation_rules(humidity, temperature, soil_type)
        
        if needs_irrigation:
            recommended_amount = self._calculate_irrigation_amount(humidity, temperature, soil_type, crop_type)
            priority = self._determine_irrigation_priority(humidity, confidence)
            justification = self._generate_irrigation_justification(humidity, temperature, soil_type)
        else:
            recommended_amount = 0
            priority = 'baixa'
            justification = 'Umidade adequada, irrigação não necessária'
        
        return {
            'needs_irrigation': needs_irrigation,
            'recommended_amount': recommended_amount,
            'priority': priority,
            'justification': justification,
            'confidence': confidence,
            'humidity': humidity,
            'temperature': temperature
        }
        
    except Exception as e:
        logger.error(f"Erro na predição de irrigação: {e}")
        return {
            'needs_irrigation': False,
            'recommended_amount': 0,
            'priority': 'baixa',
            'justification': 'Erro na predição',
            'confidence': 0.0
        }

def predict_nutrient_needs(self, current_level: float, crop_type: str = 'milho',
                         growth_stage: str = 'vegetativo') -> Dict[str, Any]:
    """Prediz necessidade de nutrientes"""
    try:
        # Se modelo ML disponível, usar
        if self.nutrient_model:
            features = self._prepare_nutrient_features(current_level, crop_type, growth_stage)
            prediction = self.nutrient_model.predict_proba([features])[0]
            confidence = max(prediction)
            needs_nutrients = confidence > self.prediction_threshold
        else:
            # Regras simples
            needs_nutrients, confidence = self._simple_nutrient_rules(current_level, crop_type, growth_stage)
        
        if needs_nutrients:
            recommended_amount = self._calculate_nutrient_amount(current_level, crop_type, growth_stage)
            priority = self._determine_nutrient_priority(current_level, confidence)
            justification = self._generate_nutrient_justification(current_level, crop_type, growth_stage)
        else:
            recommended_amount = 0
            priority = 'baixa'
            justification = 'Níveis de nutrientes adequados'
        
        return {
            'needs_nutrients': needs_nutrients,
            'recommended_amount': recommended_amount,
            'priority': priority,
            'justification': justification,
            'confidence': confidence,
            'current_level': current_level
        }
        
    except Exception as e:
        logger.error(f"Erro na predição de nutrientes: {e}")
        return {
            'needs_nutrients': False,
            'recommended_amount': 0,
            'priority': 'baixa',
            'justification': 'Erro na predição',
            'confidence': 0.0
        }

def predict_disease_risk(self, humidity: float, temperature: float, 
                       leaf_wetness: float = 0.0) -> Dict[str, Any]:
    """Prediz risco de doenças"""
    try:
        # Se modelo ML disponível, usar
        if self.disease_model:
            features = self._prepare_disease_features(humidity, temperature, leaf_wetness)
            prediction = self.disease_model.predict_proba([features])[0]
            confidence = max(prediction)
            disease_risk = confidence > self.prediction_threshold
        else:
            # Regras simples
            disease_risk, confidence = self._simple_disease_rules(humidity, temperature, leaf_wetness)
        
        if disease_risk:
            risk_level = self._determine_disease_risk_level(confidence)
            recommendations = self._generate_disease_recommendations(humidity, temperature)
        else:
            risk_level = 'baixo'
            recommendations = ['Condições adequadas, monitorar continuamente']
        
        return {
            'disease_risk': disease_risk,
            'risk_level': risk_level,
            'recommendations': recommendations,
            'confidence': confidence,
            'humidity': humidity,
            'temperature': temperature
        }
        
    except Exception as e:
        logger.error(f"Erro na predição de doenças: {e}")
        return {
            'disease_risk': False,
            'risk_level': 'baixo',
            'recommendations': ['Erro na predição'],
            'confidence': 0.0
        }

def _prepare_irrigation_features(self, humidity: float, temperature: float, 
                               soil_type: str, crop_type: str) -> List[float]:
    """Prepara features para modelo de irrigação"""
    # Codificar variáveis categóricas
    soil_encoding = {'argiloso': 0, 'arenoso': 1, 'siltoso': 2}
    crop_encoding = {'milho': 0, 'soja': 1, 'trigo': 2, 'arroz': 3}
    
    return [
        humidity,
        temperature,
        soil_encoding.get(soil_type, 0),
        crop_encoding.get(crop_type, 0)
    ]

def _prepare_nutrient_features(self, current_level: float, crop_type: str, 
                             growth_stage: str) -> List[float]:
    """Prepara features para modelo de nutrientes"""
    crop_encoding = {'milho': 0, 'soja': 1, 'trigo': 2}
    stage_encoding = {'vegetativo': 0, 'florescimento': 1, 'frutificação': 2}
    
    return [
        current_level,
        crop_encoding.get(crop_type, 0),
        stage_encoding.get(growth_stage, 0)
    ]

def _prepare_disease_features(self, humidity: float, temperature: float, 
                            leaf_wetness: float) -> List[float]:
    """Prepara features para modelo de doenças"""
    return [humidity, temperature, leaf_wetness]

def _simple_irrigation_rules(self, humidity: float, temperature: float, 
                            soil_type: str) -> tuple:
    """Regras simples para irrigação"""
    # Regras baseadas em conhecimento de domínio
    if humidity < 30:
        return True, 0.9
    elif humidity < 50 and temperature > 30:
        return True, 0.8
    elif humidity < 60 and soil_type == 'arenoso':
        return True, 0.7
    else:
        return False, 0.3

def _simple_nutrient_rules(self, current_level: float, crop_type: str, 
                          growth_stage: str) -> tuple:
    """Regras simples para nutrientes"""
    # Regras baseadas em conhecimento de domínio
    if current_level < 100:
        return True, 0.9
    elif current_level < 150 and growth_stage == 'florescimento':
        return True, 0.8
    elif current_level < 200 and crop_type == 'milho':
        return True, 0.7
    else:
        return False, 0.3

def _simple_disease_rules(self, humidity: float, temperature: float, 
                        leaf_wetness: float) -> tuple:
    """Regras simples para doenças"""
    # Regras baseadas em conhecimento de domínio
    if humidity > 80 and temperature > 25:
        return True, 0.9
    elif humidity > 70 and leaf_wetness > 0.5:
        return True, 0.8
    elif temperature > 30 and humidity > 60:
        return True, 0.7
    else:
        return False, 0.3

def _calculate_irrigation_amount(self, humidity: float, temperature: float, 
                               soil_type: str, crop_type: str) -> float:
    """Calcula quantidade de irrigação recomendada"""
    base_amount = 10.0  # L/m²
    
    # Ajustes baseados em condições
    if humidity < 30:
        base_amount *= 1.5
    elif humidity < 50:
        base_amount *= 1.2
    
    if temperature > 30:
        base_amount *= 1.3
    
    if soil_type == 'arenoso':
        base_amount *= 1.4
    
    return round(base_amount, 1)

def _calculate_nutrient_amount(self, current_level: float, crop_type: str, 
                             growth_stage: str) -> float:
    """Calcula quantidade de nutrientes recomendada"""
    base_amount = 30.0  # kg/ha
    
    # Ajustes baseados em condições
    if current_level < 100:
        base_amount *= 1.5
    elif current_level < 150:
        base_amount *= 1.2
    
    if growth_stage == 'florescimento':
        base_amount *= 1.3
    
    return round(base_amount, 1)

def _determine_irrigation_priority(self, humidity: float, confidence: float) -> str:
    """Determina prioridade da irrigação"""
    if humidity < 30 or confidence > 0.9:
        return 'alta'
    elif humidity < 50 or confidence > 0.7:
        return 'media'
    else:
        return 'baixa'

def _determine_nutrient_priority(self, current_level: float, confidence: float) -> str:
    """Determina prioridade dos nutrientes"""
    if current_level < 100 or confidence > 0.9:
        return 'alta'
    elif current_level < 150 or confidence > 0.7:
        return 'media'
    else:
        return 'baixa'

def _determine_disease_risk_level(self, confidence: float) -> str:
    """Determina nível de risco de doença"""
    if confidence > 0.9:
        return 'muito_alto'
    elif confidence > 0.7:
        return 'alto'
    elif confidence > 0.5:
        return 'medio'
    else:
        return 'baixo'

def _generate_irrigation_justification(self, humidity: float, temperature: float, 
                                     soil_type: str) -> str:
    """Gera justificativa para irrigação"""
    reasons = []
    
    if humidity < 30:
        reasons.append("Umidade muito baixa")
    elif humidity < 50:
        reasons.append("Umidade baixa")
    
    if temperature > 30:
        reasons.append("Temperatura elevada")
    
    if soil_type == 'arenoso':
        reasons.append("Solo arenoso com baixa retenção")
    
    return f"{', '.join(reasons)}. Irrigação recomendada."

def _generate_nutrient_justification(self, current_level: float, crop_type: str, 
                                   growth_stage: str) -> str:
    """Gera justificativa para nutrientes"""
    reasons = []
    
    if current_level < 100:
        reasons.append("Nível de nutrientes muito baixo")
    elif current_level < 150:
        reasons.append("Nível de nutrientes baixo")
    
    if growth_stage == 'florescimento':
        reasons.append("Estágio crítico de desenvolvimento")
    
    return f"{', '.join(reasons)}. Aplicação de fertilizante recomendada."

def _generate_disease_recommendations(self, humidity: float, temperature: float) -> List[str]:
    """Gera recomendações para controle de doenças"""
    recommendations = []
    
    if humidity > 80:
        recommendations.append("Reduzir umidade através de ventilação")
    
    if temperature > 25:
        recommendations.append("Monitorar temperatura e aplicar fungicida se necessário")
    
    recommendations.append("Aplicar tratamento preventivo")
    recommendations.append("Aumentar frequência de monitoramento")
    
    return recommendations 