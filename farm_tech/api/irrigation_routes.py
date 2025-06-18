"""
Rotas da API para Sistema de Irrigação Inteligente
FarmTech Solutions - API Module
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

from ..ml.predictor import create_ml_predictor
from ..core.auth import login_required, permission_required
from ..core.logger import log_info, log_error

# Criar blueprint
irrigation_bp = Blueprint('irrigation', __name__, url_prefix='/api/irrigation')

# Instância do preditor ML
ml_predictor = create_ml_predictor()

@irrigation_bp.route('/predict', methods=['POST'])
@login_required
@permission_required('view_sensors')
def predict_irrigation():
    """Predizer necessidades de irrigação"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        sensor_data = data.get('sensor_data', [])
        areas_data = data.get('areas_data', [])
        weather_forecast = data.get('weather_forecast')
        hours_ahead = data.get('hours_ahead', 24)
        
        if not sensor_data:
            return jsonify({'error': 'Dados de sensores necessários'}), 400
        
        # Fazer predição
        predictions = ml_predictor.predict_irrigation_needs(
            sensor_data, areas_data, weather_forecast
        )
        
        # Log da predição
        log_info('irrigation', f"Predição de irrigação realizada: {len(predictions)} resultados")
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat(),
            'hours_ahead': hours_ahead
        })
        
    except Exception as e:
        log_error('irrigation', f"Erro na predição de irrigação: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/schedule', methods=['POST'])
@login_required
@permission_required('manage_sensors')
def create_irrigation_schedule():
    """Criar agenda de irrigação otimizada"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        predictions = data.get('predictions', [])
        areas_data = data.get('areas_data', [])
        weather_forecast = data.get('weather_forecast')
        water_availability = data.get('water_availability', 1000)
        
        if not predictions:
            return jsonify({'error': 'Predições necessárias'}), 400
        
        # Criar agenda otimizada
        from ..ml.irrigation_optimizer import create_irrigation_optimizer
        optimizer = create_irrigation_optimizer()
        
        schedules = optimizer.optimize_irrigation_schedule(
            predictions, areas_data, weather_forecast, water_availability
        )
        
        # Gerar relatório
        report = optimizer.generate_irrigation_report(schedules)
        
        # Log da agenda
        log_info('irrigation', f"Agenda de irrigação criada: {len(schedules)} eventos")
        
        return jsonify({
            'success': True,
            'schedules': [
                {
                    'area_id': s.area_id,
                    'sensor_id': s.sensor_id,
                    'start_time': s.start_time.isoformat(),
                    'duration_minutes': s.duration_minutes,
                    'water_amount_liters': s.water_amount_liters,
                    'priority': s.priority,
                    'reason': s.reason,
                    'confidence': s.confidence,
                    'cost_estimate': s.cost_estimate
                }
                for s in schedules
            ],
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('irrigation', f"Erro ao criar agenda de irrigação: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/recommendations', methods=['GET'])
@login_required
@permission_required('view_sensors')
def get_irrigation_recommendations():
    """Obter recomendações de irrigação"""
    try:
        # Obter parâmetros
        include_irrigation = request.args.get('include_irrigation', 'true').lower() == 'true'
        
        # Obter recomendações do sistema
        from ..data.database import DatabaseManager
        db_manager = DatabaseManager()
        
        recommendations = ml_predictor.get_system_recommendations(
            db_manager, include_irrigation
        )
        
        # Filtrar apenas recomendações de irrigação se solicitado
        if include_irrigation:
            recommendations = [r for r in recommendations if r.get('type') == 'irrigation']
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('irrigation', f"Erro ao obter recomendações: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/model/status', methods=['GET'])
@login_required
@permission_required('view_sensors')
def get_model_status():
    """Obter status dos modelos de ML"""
    try:
        status = ml_predictor.get_model_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('irrigation', f"Erro ao obter status do modelo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/model/train', methods=['POST'])
@login_required
@permission_required('manage_sensors')
def train_irrigation_model():
    """Treinar modelo de irrigação"""
    try:
        data = request.get_json() or {}
        force_retrain = data.get('force_retrain', False)
        
        # Verificar se modelo já está treinado
        status = ml_predictor.get_model_status()
        if status['models_loaded'] and not force_retrain:
            return jsonify({
                'success': True,
                'message': 'Modelo já treinado',
                'status': status
            })
        
        # Inicializar/trainar modelo
        from ..data.database import DatabaseManager
        db_manager = DatabaseManager()
        
        result = ml_predictor.initialize_models(db_manager)
        
        if result['success']:
            log_info('irrigation', "Modelo de irrigação treinado com sucesso")
        else:
            log_error('irrigation', f"Erro no treinamento: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        log_error('irrigation', f"Erro no treinamento do modelo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/model/update', methods=['POST'])
@login_required
@permission_required('manage_sensors')
def update_irrigation_model():
    """Atualizar modelo de irrigação com novos dados"""
    try:
        # Atualizar modelo
        from ..data.database import DatabaseManager
        db_manager = DatabaseManager()
        
        result = ml_predictor.update_models(db_manager)
        
        if result['success']:
            log_info('irrigation', "Modelo de irrigação atualizado com sucesso")
        else:
            log_error('irrigation', f"Erro na atualização: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        log_error('irrigation', f"Erro na atualização do modelo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/history', methods=['GET'])
@login_required
@permission_required('view_sensors')
def get_irrigation_history():
    """Obter histórico de irrigação"""
    try:
        # Parâmetros
        days = int(request.args.get('days', 7))
        area_id = request.args.get('area_id')
        
        # Obter dados do banco
        from ..data.database import DatabaseManager
        db_manager = DatabaseManager()
        
        # Buscar recomendações de irrigação
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Aqui você implementaria a busca no banco de dados
        # Por enquanto, retornar dados simulados
        history = [
            {
                'id': 1,
                'area_id': 1,
                'sensor_id': 1,
                'recommended_action': 'IRRIGAR IMEDIATAMENTE',
                'priority': 'ALTA',
                'confidence': 0.85,
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'status': 'executed'
            },
            {
                'id': 2,
                'area_id': 2,
                'sensor_id': 2,
                'recommended_action': 'MONITORAR',
                'priority': 'BAIXA',
                'confidence': 0.45,
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'status': 'pending'
            }
        ]
        
        # Filtrar por área se especificado
        if area_id:
            history = [h for h in history if h['area_id'] == int(area_id)]
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'period_days': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('irrigation', f"Erro ao obter histórico: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/export', methods=['POST'])
@login_required
@permission_required('view_sensors')
def export_irrigation_data():
    """Exportar dados de irrigação"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        predictions = data.get('predictions', [])
        format_type = data.get('format', 'json')
        
        if not predictions:
            return jsonify({'error': 'Dados para exportação necessários'}), 400
        
        # Exportar dados
        exported_data = ml_predictor.export_predictions(predictions, format_type)
        
        # Determinar content type
        if format_type.lower() == 'csv':
            content_type = 'text/csv'
            filename = f'irrigation_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:
            content_type = 'application/json'
            filename = f'irrigation_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # Log da exportação
        log_info('irrigation', f"Dados de irrigação exportados: {filename}")
        
        return jsonify({
            'success': True,
            'data': exported_data,
            'format': format_type,
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('irrigation', f"Erro na exportação: {str(e)}")
        return jsonify({'error': str(e)}), 500

@irrigation_bp.route('/config', methods=['GET', 'PUT'])
@login_required
@permission_required('manage_sensors')
def manage_irrigation_config():
    """Gerenciar configurações de irrigação"""
    try:
        if request.method == 'GET':
            # Retornar configurações atuais
            config = ml_predictor.config
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        
        elif request.method == 'PUT':
            # Atualizar configurações
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Dados não fornecidos'}), 400
            
            # Atualizar configurações permitidas
            allowed_configs = ['prediction_horizon', 'min_confidence', 'enable_auto_optimization']
            
            for key, value in data.items():
                if key in allowed_configs:
                    ml_predictor.config[key] = value
            
            log_info('irrigation', f"Configurações de irrigação atualizadas: {list(data.keys())}")
            
            return jsonify({
                'success': True,
                'message': 'Configurações atualizadas',
                'config': ml_predictor.config,
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        log_error('irrigation', f"Erro ao gerenciar configurações: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Registrar blueprint
def register_irrigation_routes(app):
    """Registrar rotas de irrigação na aplicação"""
    app.register_blueprint(irrigation_bp) 