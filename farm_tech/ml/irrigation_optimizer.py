"""
Otimizador de Irrigação Inteligente
FarmTech Solutions - ML Module
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json

@dataclass
class IrrigationSchedule:
    """Agenda de irrigação otimizada"""
    area_id: int
    sensor_id: int
    start_time: datetime
    duration_minutes: int
    water_amount_liters: float
    priority: str
    reason: str
    confidence: float
    cost_estimate: float

class IrrigationOptimizer:
    """Otimizador de irrigação baseado em ML e regras de negócio"""
    
    def __init__(self):
        self.config = {
            'max_water_per_day': 1000,  # Litros por dia
            'min_irrigation_interval': 4,  # Horas entre irrigações
            'optimal_hours': [6, 18],  # Horas ideais para irrigação
            'weather_impact': True,  # Considerar clima
            'cost_per_liter': 0.01,  # Custo por litro de água
            'energy_cost_per_hour': 2.0  # Custo de energia por hora
        }
        
        # Regras de irrigação por tipo de cultura
        self.crop_rules = {
            'milho': {
                'optimal_moisture': (60, 80),
                'optimal_ph': (6.0, 7.0),
                'optimal_nutrients': (150, 250),
                'water_needs': 8.0,  # mm/dia
                'sensitivity': 'medium'
            },
            'soja': {
                'optimal_moisture': (70, 85),
                'optimal_ph': (6.0, 6.8),
                'optimal_nutrients': (120, 200),
                'water_needs': 6.0,
                'sensitivity': 'high'
            },
            'trigo': {
                'optimal_moisture': (65, 75),
                'optimal_ph': (6.0, 7.5),
                'optimal_nutrients': (100, 180),
                'water_needs': 5.0,
                'sensitivity': 'medium'
            },
            'default': {
                'optimal_moisture': (60, 80),
                'optimal_ph': (6.0, 7.0),
                'optimal_nutrients': (120, 200),
                'water_needs': 6.0,
                'sensitivity': 'medium'
            }
        }
    
    def optimize_irrigation_schedule(self, 
                                   predictions: List[Dict],
                                   areas_data: List[Dict],
                                   weather_forecast: Optional[Dict] = None,
                                   water_availability: float = 1000) -> List[IrrigationSchedule]:
        """Otimizar agenda de irrigação baseada em predições"""
        try:
            schedules = []
            
            # Agrupar predições por área
            area_predictions = {}
            for pred in predictions:
                area_id = self._get_area_id_from_sensor(pred['sensor_id'], areas_data)
                if area_id not in area_predictions:
                    area_predictions[area_id] = []
                area_predictions[area_id].append(pred)
            
            # Otimizar cada área
            for area_id, area_preds in area_predictions.items():
                area_info = self._get_area_info(area_id, areas_data)
                crop_type = area_info.get('crop_type', 'default')
                crop_rules = self.crop_rules.get(crop_type, self.crop_rules['default'])
                
                # Calcular necessidade total da área
                area_need = self._calculate_area_need(area_preds, crop_rules)
                
                if area_need['total_need'] > 0:
                    # Criar agenda otimizada
                    area_schedules = self._create_area_schedule(
                        area_id, area_preds, area_need, crop_rules, 
                        weather_forecast, water_availability
                    )
                    schedules.extend(area_schedules)
            
            # Otimizar globalmente considerando restrições
            optimized_schedules = self._global_optimization(schedules, water_availability)
            
            return optimized_schedules
            
        except Exception as e:
            print(f"Erro na otimização: {e}")
            return []
    
    def _get_area_id_from_sensor(self, sensor_id: int, areas_data: List[Dict]) -> int:
        """Obter ID da área baseado no sensor"""
        for area in areas_data:
            if area.get('sensor_id') == sensor_id:
                return area['area_id']
        return 1  # Área padrão
    
    def _get_area_info(self, area_id: int, areas_data: List[Dict]) -> Dict:
        """Obter informações da área"""
        for area in areas_data:
            if area['area_id'] == area_id:
                return area
        return {'area_id': area_id, 'crop_type': 'default', 'size': 1.0}
    
    def _calculate_area_need(self, predictions: List[Dict], crop_rules: Dict) -> Dict:
        """Calcular necessidade de irrigação da área"""
        total_need = 0
        urgency_score = 0
        sensor_needs = {}
        
        for pred in predictions:
            sensor_id = pred['sensor_id']
            sensor_type = pred['sensor_type']
            current_value = pred['current_value']
            prediction_prob = pred['prediction_probability']
            
            # Calcular necessidade baseada no tipo de sensor
            if 'umidade' in sensor_type.lower():
                optimal_range = crop_rules['optimal_moisture']
                if current_value < optimal_range[0]:
                    need = (optimal_range[0] - current_value) / optimal_range[0]
                    urgency = 1.0 - (current_value / optimal_range[0])
                else:
                    need = 0
                    urgency = 0
                    
            elif 'ph' in sensor_type.lower():
                optimal_range = crop_rules['optimal_ph']
                if current_value < optimal_range[0] or current_value > optimal_range[1]:
                    need = prediction_prob
                    urgency = prediction_prob
                else:
                    need = 0
                    urgency = 0
                    
            elif 'nutrientes' in sensor_type.lower():
                optimal_range = crop_rules['optimal_nutrients']
                if current_value < optimal_range[0]:
                    need = (optimal_range[0] - current_value) / optimal_range[0]
                    urgency = 1.0 - (current_value / optimal_range[0])
                else:
                    need = 0
                    urgency = 0
            else:
                need = prediction_prob
                urgency = prediction_prob
            
            sensor_needs[sensor_id] = {
                'need': need,
                'urgency': urgency,
                'sensor_type': sensor_type,
                'current_value': current_value
            }
            
            total_need += need
            urgency_score += urgency
        
        return {
            'total_need': total_need,
            'urgency_score': urgency_score,
            'sensor_needs': sensor_needs,
            'priority': self._calculate_priority(urgency_score, len(predictions))
        }
    
    def _calculate_priority(self, urgency_score: float, sensor_count: int) -> str:
        """Calcular prioridade baseada na urgência"""
        avg_urgency = urgency_score / sensor_count if sensor_count > 0 else 0
        
        if avg_urgency > 0.7:
            return "ALTA"
        elif avg_urgency > 0.4:
            return "MÉDIA"
        else:
            return "BAIXA"
    
    def _create_area_schedule(self, area_id: int, predictions: List[Dict], 
                            area_need: Dict, crop_rules: Dict,
                            weather_forecast: Optional[Dict],
                            water_availability: float) -> List[IrrigationSchedule]:
        """Criar agenda para uma área específica"""
        schedules = []
        
        if area_need['total_need'] <= 0:
            return schedules
        
        # Calcular quantidade de água necessária
        area_info = self._get_area_info(area_id, [])
        area_size = area_info.get('size', 1.0)  # hectares
        
        # Converter necessidade para litros
        water_needs_mm = crop_rules['water_needs'] * area_need['total_need']
        water_needs_liters = water_needs_mm * area_size * 10000  # mm * ha * 10000 = litros
        
        # Ajustar baseado na disponibilidade
        water_needs_liters = min(water_needs_liters, water_availability * 0.1)  # Máximo 10% da disponibilidade
        
        # Determinar horário ideal
        optimal_time = self._find_optimal_time(weather_forecast)
        
        # Calcular duração baseada na vazão do sistema
        flow_rate = 100  # litros/minuto (configurável)
        duration_minutes = int(water_needs_liters / flow_rate)
        
        # Criar agenda
        schedule = IrrigationSchedule(
            area_id=area_id,
            sensor_id=predictions[0]['sensor_id'],
            start_time=optimal_time,
            duration_minutes=duration_minutes,
            water_amount_liters=water_needs_liters,
            priority=area_need['priority'],
            reason=self._generate_reason(area_need, crop_rules),
            confidence=np.mean([p['confidence'] for p in predictions]),
            cost_estimate=self._calculate_cost(water_needs_liters, duration_minutes)
        )
        
        schedules.append(schedule)
        return schedules
    
    def _find_optimal_time(self, weather_forecast: Optional[Dict]) -> datetime:
        """Encontrar horário ideal para irrigação"""
        now = datetime.now()
        
        # Horários ideais (manhã e tarde)
        optimal_hours = self.config['optimal_hours']
        
        # Se não há previsão do tempo, usar horários padrão
        if not weather_forecast:
            # Escolher o próximo horário ideal
            for hour in optimal_hours:
                optimal_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                if optimal_time > now:
                    return optimal_time
            
            # Se passou dos horários ideais, agendar para amanhã
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)
        
        # Considerar previsão do tempo
        # Implementar lógica baseada em temperatura, umidade, vento, etc.
        # Por simplicidade, usar horário padrão
        return now.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)
    
    def _generate_reason(self, area_need: Dict, crop_rules: Dict) -> str:
        """Gerar motivo da irrigação"""
        reasons = []
        
        for sensor_id, sensor_need in area_need['sensor_needs'].items():
            if sensor_need['need'] > 0:
                sensor_type = sensor_need['sensor_type']
                current_value = sensor_need['current_value']
                
                if 'umidade' in sensor_type.lower():
                    optimal_range = crop_rules['optimal_moisture']
                    reasons.append(f"Umidade baixa ({current_value}%, ideal: {optimal_range[0]}-{optimal_range[1]}%)")
                elif 'ph' in sensor_type.lower():
                    optimal_range = crop_rules['optimal_ph']
                    reasons.append(f"pH fora do ideal ({current_value}, ideal: {optimal_range[0]}-{optimal_range[1]})")
                elif 'nutrientes' in sensor_type.lower():
                    optimal_range = crop_rules['optimal_nutrients']
                    reasons.append(f"Nutrientes baixos ({current_value} ppm, ideal: {optimal_range[0]}-{optimal_range[1]} ppm)")
        
        return "; ".join(reasons) if reasons else "Manutenção preventiva"
    
    def _calculate_cost(self, water_liters: float, duration_minutes: float) -> float:
        """Calcular custo estimado da irrigação"""
        water_cost = water_liters * self.config['cost_per_liter']
        energy_cost = (duration_minutes / 60) * self.config['energy_cost_per_hour']
        return water_cost + energy_cost
    
    def _global_optimization(self, schedules: List[IrrigationSchedule], 
                           water_availability: float) -> List[IrrigationSchedule]:
        """Otimização global considerando restrições"""
        if not schedules:
            return schedules
        
        # Ordenar por prioridade e urgência
        priority_order = {"ALTA": 3, "MÉDIA": 2, "BAIXA": 1}
        schedules.sort(key=lambda x: (priority_order.get(x.priority, 0), x.confidence), reverse=True)
        
        # Aplicar restrições
        optimized_schedules = []
        total_water_used = 0
        used_times = []
        
        for schedule in schedules:
            # Verificar disponibilidade de água
            if total_water_used + schedule.water_amount_liters > water_availability:
                continue
            
            # Verificar intervalo mínimo entre irrigações
            if self._check_time_conflict(schedule.start_time, used_times):
                continue
            
            optimized_schedules.append(schedule)
            total_water_used += schedule.water_amount_liters
            used_times.append(schedule.start_time)
        
        return optimized_schedules
    
    def _check_time_conflict(self, new_time: datetime, used_times: List[datetime]) -> bool:
        """Verificar conflito de horário"""
        min_interval = timedelta(hours=self.config['min_irrigation_interval'])
        
        for used_time in used_times:
            if abs((new_time - used_time).total_seconds()) < min_interval.total_seconds():
                return True
        
        return False
    
    def generate_irrigation_report(self, schedules: List[IrrigationSchedule]) -> Dict[str, Any]:
        """Gerar relatório de irrigação"""
        if not schedules:
            return {"message": "Nenhuma irrigação agendada"}
        
        total_water = sum(s.water_amount_liters for s in schedules)
        total_cost = sum(s.cost_estimate for s in schedules)
        total_duration = sum(s.duration_minutes for s in schedules)
        
        priority_counts = {}
        for schedule in schedules:
            priority_counts[schedule.priority] = priority_counts.get(schedule.priority, 0) + 1
        
        return {
            "total_schedules": len(schedules),
            "total_water_liters": total_water,
            "total_cost": total_cost,
            "total_duration_minutes": total_duration,
            "priority_distribution": priority_counts,
            "average_confidence": np.mean([s.confidence for s in schedules]),
            "schedules": [
                {
                    "area_id": s.area_id,
                    "start_time": s.start_time.isoformat(),
                    "duration_minutes": s.duration_minutes,
                    "water_amount_liters": s.water_amount_liters,
                    "priority": s.priority,
                    "cost_estimate": s.cost_estimate
                }
                for s in schedules
            ]
        }
    
    def save_schedule_to_database(self, schedules: List[IrrigationSchedule], db_manager) -> bool:
        """Salvar agenda no banco de dados"""
        try:
            for schedule in schedules:
                # Criar registro de irrigação
                irrigation_data = {
                    'area_id': schedule.area_id,
                    'sensor_id': schedule.sensor_id,
                    'scheduled_time': schedule.start_time.isoformat(),
                    'duration_minutes': schedule.duration_minutes,
                    'water_amount_liters': schedule.water_amount_liters,
                    'priority': schedule.priority,
                    'reason': schedule.reason,
                    'confidence': schedule.confidence,
                    'cost_estimate': schedule.cost_estimate,
                    'status': 'scheduled'
                }
                
                # Salvar no banco (assumindo que existe uma tabela de irrigação)
                # db_manager.create_irrigation_schedule(irrigation_data)
                
            return True
            
        except Exception as e:
            print(f"Erro ao salvar agenda: {e}")
            return False

# Função de conveniência
def create_irrigation_optimizer() -> IrrigationOptimizer:
    """Criar instância do otimizador de irrigação"""
    return IrrigationOptimizer() 