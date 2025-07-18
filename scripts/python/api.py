#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - API Web
API REST para o sistema de sensoriamento agrícola
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Importar serviços e modelos
from services.sensor_service import SensorService, RecomendacaoService
from data.sensor_repository import SensorRepository, LeituraRepository, AreaRepository
from models.sensor_models import StatusLeitura, TipoSensor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('farmtech_api')

# Inicializar Flask app
app = Flask(__name__)
CORS(app)  # Permitir CORS para desenvolvimento

# Inicializar serviços
sensor_repository = SensorRepository()
leitura_repository = LeituraRepository()
area_repository = AreaRepository()
sensor_service = SensorService(sensor_repository, leitura_repository, area_repository)
recomendacao_service = RecomendacaoService(sensor_service)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'FarmTech Solutions API'
    })


# ============================================================================
# ENDPOINTS DE SENSORES
# ============================================================================

@app.route('/api/sensores', methods=['GET'])
def listar_sensores():
    """Lista todos os sensores com filtros opcionais"""
    try:
        area_id = request.args.get('area_id', type=int)
        tipo_sensor = request.args.get('tipo_sensor')
        status = request.args.get('status')
        
        sensores = sensor_repository.listar_sensores(
            area_id=area_id,
            tipo_sensor=tipo_sensor,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': [sensor.to_dict() for sensor in sensores],
            'count': len(sensores)
        })
    
    except Exception as e:
        logger.error(f"Erro ao listar sensores: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sensores/<int:sensor_id>', methods=['GET'])
def obter_sensor(sensor_id):
    """Obtém informações de um sensor específico"""
    try:
        sensor = sensor_repository.obter_sensor(sensor_id)
        
        if not sensor:
            return jsonify({
                'success': False,
                'error': 'Sensor não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': sensor.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Erro ao obter sensor {sensor_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sensores/<int:sensor_id>/estatisticas', methods=['GET'])
def obter_estatisticas_sensor(sensor_id):
    """Obtém estatísticas de um sensor para um período específico"""
    try:
        periodo_dias = request.args.get('periodo_dias', 7, type=int)
        
        estatisticas = sensor_service.obter_estatisticas_sensor(
            sensor_id=sensor_id,
            periodo_dias=periodo_dias
        )
        
        return jsonify({
            'success': True,
            'data': estatisticas
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do sensor {sensor_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sensores/<int:sensor_id>/tendencia', methods=['GET'])
def obter_tendencia_sensor(sensor_id):
    """Obtém análise de tendência de um sensor"""
    try:
        periodo_dias = request.args.get('periodo_dias', 30, type=int)
        
        tendencia = sensor_service.analisar_tendencia_sensor(
            sensor_id=sensor_id,
            periodo_dias=periodo_dias
        )
        
        return jsonify({
            'success': True,
            'data': tendencia
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except Exception as e:
        logger.error(f"Erro ao obter tendência do sensor {sensor_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ENDPOINTS DE LEITURAS
# ============================================================================

@app.route('/api/leituras', methods=['GET'])
def listar_leituras():
    """Lista leituras com filtros opcionais"""
    try:
        sensor_id = request.args.get('sensor_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        limit = request.args.get('limit', 100, type=int)
        
        # Converter strings de data para datetime
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
        
        leituras = leitura_repository.listar_leituras(
            sensor_id=sensor_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': [leitura.to_dict() for leitura in leituras],
            'count': len(leituras)
        })
    
    except Exception as e:
        logger.error(f"Erro ao listar leituras: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leituras', methods=['POST'])
def registrar_leitura():
    """Registra uma nova leitura de sensor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['sensor_id', 'valor', 'unidade_medida']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório não fornecido: {field}'
                }), 400
        
        # Processar data_hora se fornecida
        data_hora = data.get('data_hora')
        if data_hora and isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora)
        
        # Registrar leitura
        leitura_id = sensor_service.registrar_leitura(
            sensor_id=data['sensor_id'],
            valor=data['valor'],
            unidade_medida=data['unidade_medida'],
            data_hora=data_hora,
            observacao=data.get('observacao')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'leitura_id': leitura_id,
                'message': 'Leitura registrada com sucesso'
            }
        }), 201
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Erro ao registrar leitura: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leituras/lote', methods=['POST'])
def registrar_leituras_lote():
    """Registra múltiplas leituras em lote"""
    try:
        data = request.get_json()
        
        if not data or 'leituras' not in data:
            return jsonify({
                'success': False,
                'error': 'Lista de leituras não fornecida'
            }), 400
        
        leitura_ids = sensor_service.registrar_leitura_em_lote(data['leituras'])
        
        return jsonify({
            'success': True,
            'data': {
                'leituras_registradas': len(leitura_ids),
                'leitura_ids': leitura_ids,
                'message': f'{len(leitura_ids)} leituras registradas com sucesso'
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Erro ao registrar leituras em lote: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ENDPOINTS DE RECOMENDAÇÕES
# ============================================================================

@app.route('/api/recomendacoes/irrigacao/<int:plantio_id>', methods=['GET'])
def gerar_recomendacao_irrigacao(plantio_id):
    """Gera recomendação de irrigação para um plantio"""
    try:
        sensor_id = request.args.get('sensor_id', 1, type=int)  # Default para sensor de umidade
        
        recomendacao = recomendacao_service.gerar_recomendacao_irrigacao(
            plantio_id=plantio_id,
            sensor_id=sensor_id
        )
        
        return jsonify({
            'success': True,
            'data': recomendacao
        })
    
    except Exception as e:
        logger.error(f"Erro ao gerar recomendação de irrigação: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recomendacoes/nutrientes/<int:plantio_id>', methods=['GET'])
def gerar_recomendacao_nutrientes(plantio_id):
    """Gera recomendação de nutrientes para um plantio"""
    try:
        sensor_id = request.args.get('sensor_id', 2, type=int)  # Default para sensor de nutrientes
        
        recomendacao = recomendacao_service.gerar_recomendacao_nutrientes(
            plantio_id=plantio_id,
            sensor_id=sensor_id
        )
        
        return jsonify({
            'success': True,
            'data': recomendacao
        })
    
    except Exception as e:
        logger.error(f"Erro ao gerar recomendação de nutrientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recomendacoes/ph/<int:plantio_id>', methods=['GET'])
def gerar_recomendacao_ph(plantio_id):
    """Gera recomendação de correção de pH para um plantio"""
    try:
        sensor_id = request.args.get('sensor_id', 3, type=int)  # Default para sensor de pH
        
        recomendacao = recomendacao_service.gerar_recomendacao_ph(
            plantio_id=plantio_id,
            sensor_id=sensor_id
        )
        
        return jsonify({
            'success': True,
            'data': recomendacao
        })
    
    except Exception as e:
        logger.error(f"Erro ao gerar recomendação de pH: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recomendacoes/plantio/<int:plantio_id>', methods=['GET'])
def gerar_recomendacoes_plantio(plantio_id):
    """Gera todas as recomendações para um plantio"""
    try:
        recomendacoes = recomendacao_service.gerar_recomendacoes_para_plantio(
            plantio_id=plantio_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'plantio_id': plantio_id,
                'recomendacoes': recomendacoes,
                'total_recomendacoes': len(recomendacoes)
            }
        })
    
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações para plantio {plantio_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ENDPOINTS DE ÁREAS
# ============================================================================

@app.route('/api/areas', methods=['GET'])
def listar_areas():
    """Lista todas as áreas"""
    try:
        areas = area_repository.listar_areas()
        
        return jsonify({
            'success': True,
            'data': [area.to_dict() for area in areas],
            'count': len(areas)
        })
    
    except Exception as e:
        logger.error(f"Erro ao listar áreas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/areas/<int:area_id>', methods=['GET'])
def obter_area(area_id):
    """Obtém informações de uma área específica"""
    try:
        area = area_repository.obter_area(area_id)
        
        if not area:
            return jsonify({
                'success': False,
                'error': 'Área não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': area.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Erro ao obter área {area_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# CONFIGURAÇÃO E EXECUÇÃO
# ============================================================================

if __name__ == '__main__':
    logger.info("Iniciando FarmTech Solutions API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
