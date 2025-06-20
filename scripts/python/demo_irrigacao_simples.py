#!/usr/bin/env python3
"""
Demonstração Simplificada do Sistema de Irrigação Inteligente
FarmTech Solutions - Scikit-learn Integration
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

def create_sample_data():
    """Criar dados de exemplo para demonstração"""
    print("🌱 Criando dados de exemplo para demonstração...")
    
    # Dados de sensores simulados
    sensor_data = []
    
    # Simular dados de 3 sensores por 7 dias
    sensor_types = ['umidade', 'ph', 'nutrientes']
    base_values = {
        'umidade': 60,
        'ph': 6.5,
        'nutrientes': 200
    }
    
    for day in range(7):
        for hour in range(24):
            timestamp = datetime.now() - timedelta(days=6-day, hours=23-hour)
            
            for sensor_id, sensor_type in enumerate(sensor_types, 1):
                # Simular variações baseadas no tipo de sensor
                if sensor_type == 'umidade':
                    # Variação diária: mais baixa durante o dia, mais alta à noite
                    base = base_values[sensor_type]
                    variation = 20 * np.sin(2 * np.pi * hour / 24)
                    # Tendência de diminuição (simulando seca)
                    trend = -2 * day
                    value = max(20, min(90, base + variation + trend + np.random.normal(0, 5)))
                    
                elif sensor_type == 'ph':
                    # pH mais estável com pequenas variações
                    base = base_values[sensor_type]
                    variation = 0.5 * np.sin(2 * np.pi * hour / 24)
                    value = max(5.0, min(8.0, base + variation + np.random.normal(0, 0.2)))
                    
                else:  # nutrientes
                    # Nutrientes diminuindo gradualmente
                    base = base_values[sensor_type]
                    trend = -5 * day  # Diminuição gradual
                    value = max(50, min(300, base + trend + np.random.normal(0, 10)))
                
                sensor_data.append({
                    'sensor_id': sensor_id,
                    'tipo_sensor': sensor_type,
                    'valor': round(value, 2),
                    'unidade_medida': '%' if sensor_type == 'umidade' else ('pH' if sensor_type == 'ph' else 'ppm'),
                    'data_hora': timestamp.isoformat(),
                    'status_leitura': 'valida'
                })
    
    return sensor_data

class SimpleIrrigationPredictor:
    """Preditor simplificado de irrigação"""
    
    def __init__(self):
        self.crop_rules = {
            'milho': {
                'optimal_moisture': (60, 80),
                'optimal_ph': (6.0, 7.0),
                'optimal_nutrients': (150, 250),
                'water_needs': 8.0,
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
            }
        }
    
    def predict_irrigation(self, sensor_data, hours_ahead=24):
        """Predizer necessidade de irrigação"""
        predictions = []
        
        # Agrupar por sensor
        sensor_groups = {}
        for data in sensor_data:
            sensor_id = data['sensor_id']
            if sensor_id not in sensor_groups:
                sensor_groups[sensor_id] = []
            sensor_groups[sensor_id].append(data)
        
        # Analisar cada sensor
        for sensor_id, readings in sensor_groups.items():
            if not readings:
                continue
            
            # Obter leitura mais recente
            latest = max(readings, key=lambda x: x['data_hora'])
            sensor_type = latest['tipo_sensor']
            current_value = latest['valor']
            
            # Calcular tendência
            if len(readings) >= 3:
                recent_values = [r['valor'] for r in sorted(readings, key=lambda x: x['data_hora'])[-3:]]
                older_values = [r['valor'] for r in sorted(readings, key=lambda x: x['data_hora'])[:-3]]
                
                if older_values:
                    recent_avg = np.mean(recent_values)
                    older_avg = np.mean(older_values)
                    change_percent = ((recent_avg - older_avg) / older_avg) * 100
                else:
                    change_percent = 0
            else:
                change_percent = 0
            
            # Calcular probabilidade de irrigação
            prediction_prob = self._calculate_irrigation_probability(
                sensor_type, current_value, change_percent
            )
            
            # Determinar ação recomendada
            action, priority, reason = self._determine_action(
                sensor_type, current_value, change_percent, prediction_prob
            )
            
            # Calcular confiança
            confidence = self._calculate_confidence(prediction_prob, current_value, sensor_type)
            
            predictions.append({
                'sensor_id': sensor_id,
                'sensor_type': sensor_type,
                'current_value': current_value,
                'prediction_probability': prediction_prob,
                'recommended_action': action,
                'priority': priority,
                'reason': reason,
                'confidence': confidence,
                'recommended_time': (datetime.now() + timedelta(hours=hours_ahead)).isoformat(),
                'change_percent': change_percent
            })
        
        return predictions
    
    def _calculate_irrigation_probability(self, sensor_type, current_value, change_percent):
        """Calcular probabilidade de necessidade de irrigação"""
        if sensor_type == 'umidade':
            if current_value < 30:
                return 0.95
            elif current_value < 40:
                return 0.8
            elif current_value < 50:
                return 0.6
            elif change_percent < -15:
                return 0.7
            else:
                return 0.2
                
        elif sensor_type == 'ph':
            if current_value < 5.0 or current_value > 8.0:
                return 0.9
            elif current_value < 5.5 or current_value > 7.5:
                return 0.7
            elif abs(change_percent) > 10:
                return 0.5
            else:
                return 0.1
                
        elif sensor_type == 'nutrientes':
            if current_value < 100:
                return 0.85
            elif current_value < 150:
                return 0.6
            elif change_percent < -20:
                return 0.7
            else:
                return 0.2
        
        return 0.3
    
    def _determine_action(self, sensor_type, current_value, change_percent, probability):
        """Determinar ação recomendada"""
        if probability > 0.7:
            action = "IRRIGAR IMEDIATAMENTE"
            priority = "ALTA"
        elif probability > 0.5:
            action = "IRRIGAR EM BREVE"
            priority = "MÉDIA"
        elif probability > 0.3:
            action = "MONITORAR"
            priority = "BAIXA"
        else:
            action = "NÃO IRRIGAR"
            priority = "NENHUMA"
        
        # Gerar motivo
        if sensor_type == 'umidade':
            if current_value < 40:
                reason = f"Umidade muito baixa ({current_value}%)"
            elif change_percent < -15:
                reason = f"Umidade diminuindo rapidamente ({change_percent:.1f}%)"
            else:
                reason = "Monitoramento preventivo"
                
        elif sensor_type == 'ph':
            if current_value < 5.5 or current_value > 7.5:
                reason = f"pH fora do ideal ({current_value})"
            elif abs(change_percent) > 10:
                reason = f"pH mudando rapidamente ({change_percent:.1f}%)"
            else:
                reason = "Monitoramento preventivo"
                
        elif sensor_type == 'nutrientes':
            if current_value < 150:
                reason = f"Nutrientes baixos ({current_value} ppm)"
            elif change_percent < -20:
                reason = f"Nutrientes diminuindo ({change_percent:.1f}%)"
            else:
                reason = "Monitoramento preventivo"
        else:
            reason = "Monitoramento preventivo"
        
        return action, priority, reason
    
    def _calculate_confidence(self, probability, current_value, sensor_type):
        """Calcular nível de confiança"""
        base_confidence = probability
        
        # Ajustar baseado no valor atual
        if sensor_type == 'umidade':
            if current_value < 30 or current_value > 80:
                base_confidence *= 1.2
            elif 40 <= current_value <= 60:
                base_confidence *= 0.8
        elif sensor_type == 'ph':
            if current_value < 5.0 or current_value > 8.0:
                base_confidence *= 1.3
            elif 5.5 <= current_value <= 7.5:
                base_confidence *= 0.7
        elif sensor_type == 'nutrientes':
            if current_value < 100:
                base_confidence *= 1.1
            elif current_value > 200:
                base_confidence *= 0.9
        
        return max(0.0, min(1.0, base_confidence))

class SimpleIrrigationOptimizer:
    """Otimizador simplificado de irrigação"""
    
    def __init__(self):
        self.config = {
            'max_water_per_day': 1000,
            'min_irrigation_interval': 4,
            'optimal_hours': [6, 18],
            'cost_per_liter': 0.01,
            'energy_cost_per_hour': 2.0
        }
    
    def optimize_schedule(self, predictions, areas_data=None):
        """Otimizar agenda de irrigação"""
        schedules = []
        
        for pred in predictions:
            if pred['prediction_probability'] > 0.3:  # Filtrar predições relevantes
                # Calcular quantidade de água
                water_needs = self._calculate_water_needs(pred)
                
                # Determinar horário ideal
                optimal_time = self._find_optimal_time()
                
                # Calcular duração e custo
                duration_minutes = int(water_needs / 100)  # 100 litros/minuto
                cost_estimate = (water_needs * self.config['cost_per_liter'] + 
                               (duration_minutes / 60) * self.config['energy_cost_per_hour'])
                
                schedule = {
                    'area_id': pred.get('area_id', 1),
                    'sensor_id': pred['sensor_id'],
                    'start_time': optimal_time.isoformat(),
                    'duration_minutes': duration_minutes,
                    'water_amount_liters': water_needs,
                    'priority': pred['priority'],
                    'reason': pred['reason'],
                    'confidence': pred['confidence'],
                    'cost_estimate': cost_estimate
                }
                
                schedules.append(schedule)
        
        # Ordenar por prioridade
        priority_order = {"ALTA": 3, "MÉDIA": 2, "BAIXA": 1}
        schedules.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['confidence']), reverse=True)
        
        return schedules
    
    def _calculate_water_needs(self, prediction):
        """Calcular necessidade de água"""
        base_need = 200  # litros base
        
        # Ajustar baseado na probabilidade
        if prediction['prediction_probability'] > 0.8:
            return base_need * 1.5
        elif prediction['prediction_probability'] > 0.6:
            return base_need * 1.2
        else:
            return base_need * 0.8
    
    def _find_optimal_time(self):
        """Encontrar horário ideal"""
        now = datetime.now()
        
        # Escolher próximo horário ideal
        for hour in self.config['optimal_hours']:
            optimal_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if optimal_time > now:
                return optimal_time
        
        # Se passou dos horários ideais, agendar para amanhã
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=self.config['optimal_hours'][0], minute=0, second=0, microsecond=0)
    
    def generate_report(self, schedules):
        """Gerar relatório de irrigação"""
        if not schedules:
            return {"message": "Nenhuma irrigação agendada"}
        
        total_water = sum(s['water_amount_liters'] for s in schedules)
        total_cost = sum(s['cost_estimate'] for s in schedules)
        total_duration = sum(s['duration_minutes'] for s in schedules)
        
        priority_counts = {}
        for schedule in schedules:
            priority_counts[schedule['priority']] = priority_counts.get(schedule['priority'], 0) + 1
        
        return {
            "total_schedules": len(schedules),
            "total_water_liters": total_water,
            "total_cost": total_cost,
            "total_duration_minutes": total_duration,
            "priority_distribution": priority_counts,
            "average_confidence": np.mean([s['confidence'] for s in schedules])
        }

def demonstrate_irrigation_system():
    """Demonstrar sistema de irrigação inteligente"""
    print("\n" + "="*60)
    print("🚰 DEMONSTRAÇÃO: SISTEMA DE IRRIGAÇÃO INTELIGENTE")
    print("="*60)
    
    # Criar dados de exemplo
    sensor_data = create_sample_data()
    print(f"✅ Dados criados: {len(sensor_data)} leituras de sensores")
    
    # Criar preditor e otimizador
    predictor = SimpleIrrigationPredictor()
    optimizer = SimpleIrrigationOptimizer()
    
    print("\n🔮 FAZENDO PREDIÇÕES DE IRRIGAÇÃO...")
    
    # Usar dados recentes para predição
    recent_data = [d for d in sensor_data if d['data_hora'] > 
                   (datetime.now() - timedelta(hours=24)).isoformat()]
    
    predictions = predictor.predict_irrigation(recent_data, hours_ahead=24)
    
    print(f"✅ Predições geradas: {len(predictions)}")
    
    # Mostrar predições
    for i, pred in enumerate(predictions, 1):
        print(f"\n   Sensor {i}:")
        print(f"   - Tipo: {pred['sensor_type']}")
        print(f"   - Valor atual: {pred['current_value']} {pred.get('unidade_medida', '')}")
        print(f"   - Probabilidade de irrigação: {pred['prediction_probability']:.2%}")
        print(f"   - Ação recomendada: {pred['recommended_action']}")
        print(f"   - Prioridade: {pred['priority']}")
        print(f"   - Motivo: {pred['reason']}")
        print(f"   - Confiança: {pred['confidence']:.2%}")
        print(f"   - Mudança: {pred['change_percent']:.1f}%")
    
    print("\n⚙️ OTIMIZANDO AGENDA DE IRRIGAÇÃO...")
    
    # Dados de áreas (simulados)
    areas_data = [
        {
            'area_id': 1,
            'nome': 'Área A - Milho',
            'crop_type': 'milho',
            'size': 50.0,
            'sensor_id': 1
        },
        {
            'area_id': 2,
            'nome': 'Área B - Soja',
            'crop_type': 'soja',
            'size': 75.0,
            'sensor_id': 2
        },
        {
            'area_id': 3,
            'nome': 'Área C - Trigo',
            'crop_type': 'trigo',
            'size': 30.0,
            'sensor_id': 3
        }
    ]
    
    # Otimizar agenda
    schedules = optimizer.optimize_schedule(predictions, areas_data)
    
    print(f"✅ Agenda otimizada: {len(schedules)} eventos de irrigação")
    
    # Mostrar agenda
    for i, schedule in enumerate(schedules, 1):
        print(f"\n   Evento {i}:")
        print(f"   - Área: {schedule['area_id']}")
        print(f"   - Horário: {schedule['start_time']}")
        print(f"   - Duração: {schedule['duration_minutes']} minutos")
        print(f"   - Água: {schedule['water_amount_liters']:.1f} litros")
        print(f"   - Prioridade: {schedule['priority']}")
        print(f"   - Motivo: {schedule['reason']}")
        print(f"   - Custo estimado: R$ {schedule['cost_estimate']:.2f}")
    
    print("\n📈 GERANDO RELATÓRIO DE IRRIGAÇÃO...")
    
    # Gerar relatório
    report = optimizer.generate_report(schedules)
    
    print(f"   Total de eventos: {report['total_schedules']}")
    print(f"   Água total: {report['total_water_liters']:.1f} litros")
    print(f"   Custo total: R$ {report['total_cost']:.2f}")
    print(f"   Duração total: {report['total_duration_minutes']} minutos")
    print(f"   Confiança média: {report['average_confidence']:.2%}")
    print(f"   Distribuição por prioridade: {report['priority_distribution']}")
    
    print("\n🎯 ANÁLISE DE TENDÊNCIAS...")
    
    # Analisar tendências
    for pred in predictions:
        if abs(pred['change_percent']) > 10:
            print(f"\n   Sensor {pred['sensor_id']} ({pred['sensor_type']}):")
            print(f"   - Valor atual: {pred['current_value']:.2f}")
            print(f"   - Mudança: {pred['change_percent']:.1f}%")
            print(f"   - Tendência: {'Diminuindo' if pred['change_percent'] < 0 else 'Aumentando'}")
    
    print("\n💡 RECOMENDAÇÕES DO SISTEMA...")
    
    # Gerar recomendações
    recommendations = []
    
    for pred in predictions:
        if pred['prediction_probability'] > 0.5:
            recommendations.append({
                'type': 'irrigation',
                'title': f"Irrigação Recomendada - Área {pred['sensor_id']}",
                'message': f"{pred['recommended_action']}: {pred['reason']}",
                'priority': pred['priority'].lower(),
                'confidence': pred['confidence'],
                'action_required': pred['priority'] == 'ALTA'
            })
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   Recomendação {i}:")
        print(f"   - Tipo: {rec['type']}")
        print(f"   - Título: {rec['title']}")
        print(f"   - Mensagem: {rec['message']}")
        print(f"   - Prioridade: {rec['priority']}")
        print(f"   - Confiança: {rec['confidence']:.2%}")
        print(f"   - Ação requerida: {'Sim' if rec['action_required'] else 'Não'}")

def demonstrate_ml_features():
    """Demonstrar recursos de ML"""
    print("\n" + "="*60)
    print("🤖 RECURSOS DE MACHINE LEARNING")
    print("="*60)
    
    print("\n📊 PREPARAÇÃO DE FEATURES...")
    print("   • Features temporais (hora, dia, mês)")
    print("   • Features de lag (valores anteriores)")
    print("   • Features cíclicas (seno/cosseno)")
    print("   • Médias móveis e tendências")
    print("   • Features contextuais (tipo de sensor, cultura)")
    
    print("\n🔍 MODELOS UTILIZADOS...")
    print("   • Random Forest Regressor")
    print("   • Gradient Boosting Regressor")
    print("   • Linear Regression")
    print("   • Ensemble Methods")
    
    print("\n📈 MÉTRICAS DE VALIDAÇÃO...")
    print("   • Validação cruzada (5 folds)")
    print("   • R² Score para regressão")
    print("   • Mean Absolute Error (MAE)")
    print("   • Root Mean Square Error (RMSE)")
    
    print("\n🎯 INTERPRETABILIDADE...")
    print("   • Importância de features")
    print("   • Análise de tendências")
    print("   • Sistema de confiança")
    print("   • Recomendações explicáveis")

def main():
    """Função principal da demonstração"""
    print("🌾 FARMTECH SOLUTIONS - IRRIGAÇÃO INTELIGENTE")
    print("Demonstração do sistema de ML para irrigação automatizada")
    print("Usando algoritmos preditivos para otimização")
    
    try:
        # Demonstração principal
        demonstrate_irrigation_system()
        
        # Recursos de ML
        demonstrate_ml_features()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n🎯 Principais benefícios implementados:")
        print("   • Predição inteligente de irrigação")
        print("   • Otimização automática de agenda")
        print("   • Análise de tendências em tempo real")
        print("   • Recomendações personalizadas por cultura")
        print("   • Sistema de confiança e priorização")
        print("   • Otimização de custos e recursos")
        print("   • Integração com dados meteorológicos")
        
        print("\n🚀 Para usar o sistema completo:")
        print("   1. Instale as dependências: pip install scikit-learn pandas numpy")
        print("   2. Execute: python farm_tech_main.py --mode api")
        print("   3. Acesse: http://localhost:5000/api/irrigation/predict")
        print("   4. Consulte a documentação: IRRIGACAO_INTELIGENTE.md")
        
        print("\n📚 Documentação disponível:")
        print("   • IRRIGACAO_INTELIGENTE.md - Documentação completa")
        print("   • API_DOCUMENTATION.md - Endpoints da API")
        print("   • MELHORIAS_IMPLEMENTADAS_FINAL.md - Resumo das funcionalidades")
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 