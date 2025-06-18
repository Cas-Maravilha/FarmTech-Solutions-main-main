#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Dashboard Web
Interface web para visualização e controle do sistema
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from ..core.config import Config
from ..core.services import SensorService, RecommendationService
from ..data.repositories import SensorRepository, ReadingRepository, AreaRepository
from ..data.database import DatabaseManager
from ..ml.predictor import MLPredictor
from ..notifications.alert_manager import AlertManager
from ..core.logger import get_api_logger

logger = get_api_logger()

def create_dashboard_app(config: Config):
    """Cria aplicação do dashboard"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.API_SECRET_KEY
    
    # Configurar SocketIO para atualizações em tempo real
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Inicializar componentes
    db_manager = DatabaseManager(config.get_database_config())
    sensor_repo = SensorRepository(db_manager)
    reading_repo = ReadingRepository(db_manager)
    area_repo = AreaRepository(db_manager)
    
    ml_predictor = MLPredictor(config.get_ml_config()['model_path'])
    alert_manager = AlertManager(config.get_notification_config())
    
    sensor_service = SensorService(sensor_repo, reading_repo)
    recommendation_service = RecommendationService(sensor_service, ml_predictor)
    
    @app.route('/')
    def dashboard():
        """Página principal do dashboard"""
        try:
            # Obter dados para o dashboard
            areas = area_repo.get_all_areas()
            sensors = sensor_repo.get_all_sensors()
            
            # Estatísticas gerais
            total_areas = len(areas)
            total_sensors = len(sensors)
            active_sensors = len([s for s in sensors if s.status == 'ativo'])
            
            # Alertas ativos
            active_alerts = alert_manager.get_active_alerts()
            
            dashboard_data = {
                'total_areas': total_areas,
                'total_sensors': total_sensors,
                'active_sensors': active_sensors,
                'active_alerts': len(active_alerts),
                'areas': [area.to_dict() for area in areas],
                'sensors': [sensor.to_dict() for sensor in sensors[:10]]  # Primeiros 10
            }
            
            return render_template('dashboard.html', data=dashboard_data)
            
        except Exception as e:
            logger.error(f"Erro ao carregar dashboard: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/sensors')
    def sensors_page():
        """Página de sensores"""
        try:
            area_id = request.args.get('area_id', type=int)
            tipo_sensor = request.args.get('tipo_sensor')
            status = request.args.get('status')
            
            sensors = sensor_repo.get_all_sensors(
                area_id=area_id,
                tipo_sensor=tipo_sensor,
                status=status
            )
            
            areas = area_repo.get_all_areas()
            
            return render_template('sensors.html', 
                                 sensors=sensors, 
                                 areas=areas,
                                 filters={'area_id': area_id, 'tipo_sensor': tipo_sensor, 'status': status})
            
        except Exception as e:
            logger.error(f"Erro ao carregar página de sensores: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/sensor/<int:sensor_id>')
    def sensor_detail(sensor_id):
        """Página de detalhes do sensor"""
        try:
            sensor = sensor_repo.get_sensor(sensor_id)
            if not sensor:
                return render_template('error.html', error="Sensor não encontrado")
            
            # Estatísticas do sensor
            stats = sensor_service.get_sensor_statistics(sensor_id, days=7)
            
            # Tendência
            trend = sensor_service.analyze_trend(sensor_id, days=30)
            
            # Últimas leituras
            recent_readings = reading_repo.get_readings(sensor_id=sensor_id, limit=50)
            
            return render_template('sensor_detail.html',
                                 sensor=sensor,
                                 stats=stats,
                                 trend=trend,
                                 readings=recent_readings)
            
        except Exception as e:
            logger.error(f"Erro ao carregar detalhes do sensor {sensor_id}: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/areas')
    def areas_page():
        """Página de áreas"""
        try:
            areas = area_repo.get_all_areas()
            
            # Adicionar estatísticas para cada área
            for area in areas:
                sensors = sensor_repo.get_sensors_by_area(area.area_id)
                area.sensor_count = len(sensors)
                area.active_sensors = len([s for s in sensors if s.status == 'ativo'])
            
            return render_template('areas.html', areas=areas)
            
        except Exception as e:
            logger.error(f"Erro ao carregar página de áreas: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/area/<int:area_id>')
    def area_detail(area_id):
        """Página de detalhes da área"""
        try:
            area = area_repo.get_area(area_id)
            if not area:
                return render_template('error.html', error="Área não encontrada")
            
            sensors = sensor_repo.get_sensors_by_area(area_id)
            
            # Estatísticas da área
            area_stats = {
                'total_sensors': len(sensors),
                'active_sensors': len([s for s in sensors if s.status == 'ativo']),
                'sensor_types': {}
            }
            
            for sensor in sensors:
                sensor_type = sensor.tipo_sensor
                if sensor_type not in area_stats['sensor_types']:
                    area_stats['sensor_types'][sensor_type] = 0
                area_stats['sensor_types'][sensor_type] += 1
            
            return render_template('area_detail.html',
                                 area=area,
                                 sensors=sensors,
                                 stats=area_stats)
            
        except Exception as e:
            logger.error(f"Erro ao carregar detalhes da área {area_id}: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/alerts')
    def alerts_page():
        """Página de alertas"""
        try:
            level_filter = request.args.get('level')
            days = request.args.get('days', 7, type=int)
            
            if level_filter:
                level = AlertLevel(level_filter)
                active_alerts = alert_manager.get_active_alerts(level=level)
                alert_history = alert_manager.get_alert_history(days=days, level=level)
            else:
                active_alerts = alert_manager.get_active_alerts()
                alert_history = alert_manager.get_alert_history(days=days)
            
            return render_template('alerts.html',
                                 active_alerts=active_alerts,
                                 alert_history=alert_history,
                                 filters={'level': level_filter, 'days': days})
            
        except Exception as e:
            logger.error(f"Erro ao carregar página de alertas: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/recommendations')
    def recommendations_page():
        """Página de recomendações"""
        try:
            plantio_id = request.args.get('plantio_id', 1, type=int)
            
            # Gerar recomendações
            recommendations = recommendation_service.generate_all_recommendations(plantio_id)
            
            return render_template('recommendations.html',
                                 recommendations=recommendations,
                                 plantio_id=plantio_id)
            
        except Exception as e:
            logger.error(f"Erro ao carregar página de recomendações: {e}")
            return render_template('error.html', error=str(e))
    
    # API endpoints para o dashboard
    @app.route('/api/dashboard/stats')
    def dashboard_stats():
        """Estatísticas do dashboard em tempo real"""
        try:
            areas = area_repo.get_all_areas()
            sensors = sensor_repo.get_all_sensors()
            
            # Calcular estatísticas
            stats = {
                'total_areas': len(areas),
                'total_sensors': len(sensors),
                'active_sensors': len([s for s in sensors if s.status == 'ativo']),
                'inactive_sensors': len([s for s in sensors if s.status == 'inativo']),
                'maintenance_sensors': len([s for s in sensors if s.status == 'manutencao']),
                'active_alerts': len(alert_manager.get_active_alerts()),
                'critical_alerts': len(alert_manager.get_active_alerts(level=AlertLevel.CRITICAL))
            }
            
            return jsonify({'success': True, 'data': stats})
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do dashboard: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/sensor/<int:sensor_id>/readings')
    def sensor_readings(sensor_id):
        """Leituras de um sensor"""
        try:
            days = request.args.get('days', 7, type=int)
            limit = request.args.get('limit', 100, type=int)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            readings = reading_repo.get_readings(
                sensor_id=sensor_id,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            return jsonify({
                'success': True,
                'data': [reading.to_dict() for reading in readings]
            })
            
        except Exception as e:
            logger.error(f"Erro ao obter leituras do sensor {sensor_id}: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/alerts/active')
    def active_alerts():
        """Alertas ativos"""
        try:
            level_filter = request.args.get('level')
            
            if level_filter:
                level = AlertLevel(level_filter)
                alerts = alert_manager.get_active_alerts(level=level)
            else:
                alerts = alert_manager.get_active_alerts()
            
            return jsonify({
                'success': True,
                'data': [alert.__dict__ for alert in alerts]
            })
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas ativos: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        """Cliente conectado"""
        logger.info("Cliente conectado ao dashboard")
        emit('connected', {'message': 'Conectado ao FarmTech Dashboard'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Cliente desconectado"""
        logger.info("Cliente desconectado do dashboard")
    
    @socketio.on('request_sensor_data')
    def handle_sensor_data_request(data):
        """Solicitação de dados do sensor"""
        try:
            sensor_id = data.get('sensor_id')
            if sensor_id:
                # Obter dados do sensor
                sensor = sensor_repo.get_sensor(sensor_id)
                if sensor:
                    latest_reading = reading_repo.get_latest_reading(sensor_id)
                    
                    emit('sensor_data', {
                        'sensor_id': sensor_id,
                        'sensor': sensor.to_dict(),
                        'latest_reading': latest_reading.to_dict() if latest_reading else None
                    })
                    
        except Exception as e:
            logger.error(f"Erro ao processar solicitação de dados do sensor: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('request_alerts')
    def handle_alerts_request():
        """Solicitação de alertas"""
        try:
            alerts = alert_manager.get_active_alerts()
            emit('alerts_update', {
                'alerts': [alert.__dict__ for alert in alerts],
                'count': len(alerts)
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar solicitação de alertas: {e}")
            emit('error', {'message': str(e)})
    
    return app, socketio 