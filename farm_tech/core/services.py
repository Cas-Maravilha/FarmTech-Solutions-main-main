#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Serviços de Negócio
Serviços principais com lógica de negócio aprimorada
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from ..data.repositories import SensorRepository, ReadingRepository, AreaRepository
from ..ml.predictor import MLPredictor
from ..notifications.alert_manager import AlertManager
from .logger import get_sensor_logger, get_ml_logger

logger = get_sensor_logger()

@dataclass
class Recommendation:
    """Estrutura para recomendações"""
    plantio_id: int
    tipo_recurso: str
    quantidade: float
    unidade_medida: str
    prioridade: str
    justificativa: str
    data_prevista_aplicacao: datetime
    confianca: float = 0.0

class SensorService:
    """Serviço aprimorado para gerenciamento de sensores"""
    
    def __init__(self, sensor_repo: SensorRepository, reading_repo: ReadingRepository):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo
        self.logger = get_sensor_logger()
    
    def register_reading(self, sensor_id: int, value: float, unit: str, 
                        timestamp: Optional[datetime] = None, 
                        observation: Optional[str] = None) -> int:
        """Registra uma nova leitura com validação"""
        try:
            # Validar sensor
            sensor = self.sensor_repo.get_sensor(sensor_id)
            if not sensor:
                raise ValueError(f"Sensor {sensor_id} não encontrado")
            
            # Validar valor baseado no tipo de sensor
            self._validate_sensor_value(sensor.tipo_sensor, value)
            
            # Registrar leitura
            reading_id = self.reading_repo.add_reading(
                sensor_id=sensor_id,
                value=value,
                unit=unit,
                timestamp=timestamp or datetime.now(),
                observation=observation
            )
            
            self.logger.info(f"Leitura registrada: ID {reading_id}, Sensor {sensor_id}, Valor {value} {unit}")
            return reading_id
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar leitura: {e}")
            raise
    
    def get_sensor_statistics(self, sensor_id: int, days: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas detalhadas do sensor"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            readings = self.reading_repo.get_readings(
                sensor_id=sensor_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not readings:
                return {
                    'sensor_id': sensor_id,
                    'total_readings': 0,
                    'message': 'Nenhuma leitura encontrada'
                }
            
            values = [r.value for r in readings]
            
            return {
                'sensor_id': sensor_id,
                'total_readings': len(readings),
                'average': sum(values) / len(values),
                'maximum': max(values),
                'minimum': min(values),
                'last_reading': readings[0].to_dict() if readings else None,
                'period_days': days
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            raise
    
    def analyze_trend(self, sensor_id: int, days: int = 30) -> Dict[str, Any]:
        """Analisa tendência do sensor"""
        try:
            readings = self.reading_repo.get_readings(
                sensor_id=sensor_id,
                days=days
            )
            
            if len(readings) < 2:
                return {
                    'sensor_id': sensor_id,
                    'trend': 'insufficient_data',
                    'message': 'Dados insuficientes para análise'
                }
            
            # Calcular tendência
            first_value = readings[-1].value
            last_value = readings[0].value
            
            if first_value == 0:
                change_percent = 100 if last_value > 0 else 0
            else:
                change_percent = ((last_value - first_value) / first_value) * 100
            
            # Determinar tendência
            if change_percent > 5:
                trend = 'increasing'
            elif change_percent < -5:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'sensor_id': sensor_id,
                'trend': trend,
                'change_percent': round(change_percent, 2),
                'first_value': first_value,
                'last_value': last_value,
                'readings_count': len(readings)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar tendência: {e}")
            raise
    
    def _validate_sensor_value(self, sensor_type: str, value: float):
        """Valida valor do sensor baseado no tipo"""
        if sensor_type == 'umidade':
            if not (0 <= value <= 100):
                raise ValueError("Umidade deve estar entre 0 e 100%")
        elif sensor_type == 'ph':
            if not (0 <= value <= 14):
                raise ValueError("pH deve estar entre 0 e 14")
        elif sensor_type == 'nutrientes':
            if not (0 <= value <= 1000):
                raise ValueError("Nutrientes devem estar entre 0 e 1000 ppm")

class RecommendationService:
    """Serviço aprimorado para geração de recomendações"""
    
    def __init__(self, sensor_service: SensorService, ml_predictor: MLPredictor):
        self.sensor_service = sensor_service
        self.ml_predictor = ml_predictor
        self.logger = get_ml_logger()
    
    def generate_irrigation_recommendation(self, plantio_id: int, sensor_id: int) -> Optional[Recommendation]:
        """Gera recomendação de irrigação usando ML"""
        try:
            # Obter dados do sensor
            stats = self.sensor_service.get_sensor_statistics(sensor_id, days=3)
            
            if stats.get('total_readings', 0) < 3:
                return None
            
            current_humidity = stats['last_reading']['value']
            
            # Usar ML para predição
            prediction = self.ml_predictor.predict_irrigation_needs(
                humidity=current_humidity,
                temperature=25.0,  # TODO: obter temperatura real
                soil_type='argiloso',  # TODO: obter tipo de solo real
                crop_type='milho'  # TODO: obter tipo de cultura real
            )
            
            if prediction['needs_irrigation']:
                return Recommendation(
                    plantio_id=plantio_id,
                    tipo_recurso='água',
                    quantidade=prediction['recommended_amount'],
                    unidade_medida='L/m²',
                    prioridade=prediction['priority'],
                    justificativa=prediction['justification'],
                    data_prevista_aplicacao=datetime.now() + timedelta(days=1),
                    confianca=prediction['confidence']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendação de irrigação: {e}")
            raise
    
    def generate_nutrient_recommendation(self, plantio_id: int, sensor_id: int) -> Optional[Recommendation]:
        """Gera recomendação de nutrientes usando ML"""
        try:
            # Obter dados do sensor
            stats = self.sensor_service.get_sensor_statistics(sensor_id, days=7)
            
            if stats.get('total_readings', 0) < 3:
                return None
            
            current_nutrients = stats['last_reading']['value']
            
            # Usar ML para predição
            prediction = self.ml_predictor.predict_nutrient_needs(
                current_level=current_nutrients,
                crop_type='milho',  # TODO: obter tipo de cultura real
                growth_stage='vegetativo'  # TODO: obter estágio de crescimento real
            )
            
            if prediction['needs_nutrients']:
                return Recommendation(
                    plantio_id=plantio_id,
                    tipo_recurso='NPK',
                    quantidade=prediction['recommended_amount'],
                    unidade_medida='kg/ha',
                    prioridade=prediction['priority'],
                    justificativa=prediction['justification'],
                    data_prevista_aplicacao=datetime.now() + timedelta(days=2),
                    confianca=prediction['confidence']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendação de nutrientes: {e}")
            raise
    
    def generate_all_recommendations(self, plantio_id: int) -> List[Recommendation]:
        """Gera todas as recomendações para um plantio"""
        recommendations = []
        
        try:
            # Recomendação de irrigação (sensor 1)
            irrigation_rec = self.generate_irrigation_recommendation(plantio_id, 1)
            if irrigation_rec:
                recommendations.append(irrigation_rec)
            
            # Recomendação de nutrientes (sensor 2)
            nutrient_rec = self.generate_nutrient_recommendation(plantio_id, 2)
            if nutrient_rec:
                recommendations.append(nutrient_rec)
            
            # TODO: Adicionar outras recomendações (pH, etc.)
            
            self.logger.info(f"Geradas {len(recommendations)} recomendações para plantio {plantio_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {e}")
            raise 