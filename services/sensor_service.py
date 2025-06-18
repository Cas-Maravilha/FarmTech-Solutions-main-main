#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Serviço de Processamento de Sensores
Analisa dados de sensores e gera recomendações para culturas
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple

# Importar modelos e repositórios
from models.sensor_models import (
    Sensor, Leitura, Area, Plantio, Recomendacao, Aplicacao,
    TipoSensor, StatusLeitura, StatusPlantio,
    PrioridadeRecomendacao, StatusRecomendacao
)

from data.sensor_repository import (
    SensorRepository, LeituraRepository, AreaRepository
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sensor_service')


class SensorService:
    """Serviço para processamento de dados de sensores"""

    def __init__(self, sensor_repository=None, leitura_repository=None, area_repository=None):
        """Inicializa o serviço com os repositórios necessários"""
        self.sensor_repository = sensor_repository or SensorRepository()
        self.leitura_repository = leitura_repository or LeituraRepository()
        self.area_repository = area_repository or AreaRepository()

    def registrar_leitura(self, sensor_id: int, valor: float, unidade_medida: str,
                         data_hora: Optional[datetime] = None,
                         status_leitura: StatusLeitura = StatusLeitura.VALIDA,
                         observacao: Optional[str] = None) -> int:
        """Registra uma nova leitura de sensor"""
        # Verificar se o sensor existe
        sensor = self.sensor_repository.obter_sensor(sensor_id)
        if not sensor:
            logger.error(f"Sensor ID {sensor_id} não encontrado")
            raise ValueError(f"Sensor ID {sensor_id} não encontrado")

        # Criar objeto Leitura
        leitura = Leitura(
            sensor_id=sensor_id,
            data_hora=data_hora or datetime.now(),
            valor=valor,
            unidade_medida=unidade_medida,
            status_leitura=status_leitura,
            observacao=observacao
        )

        # Salvar leitura
        leitura_id = self.leitura_repository.adicionar_leitura(leitura)
        logger.info(f"Leitura registrada: ID {leitura_id}, Sensor {sensor_id}, Valor {valor} {unidade_medida}")

        return leitura_id

    def registrar_leitura_em_lote(self, leituras: List[Dict[str, Any]]) -> List[int]:
        """Registra várias leituras de sensores em lote"""
        leitura_ids = []

        for leitura_data in leituras:
            try:
                sensor_id = leitura_data.get('sensor_id')
                valor = leitura_data.get('valor')
                unidade_medida = leitura_data.get('unidade_medida')

                if None in (sensor_id, valor, unidade_medida):
                    logger.warning(f"Dados incompletos para leitura: {leitura_data}")
                    continue

                # Processar data_hora se fornecida
                data_hora = leitura_data.get('data_hora')
                if data_hora and isinstance(data_hora, str):
                    try:
                        data_hora = datetime.fromisoformat(data_hora)
                    except ValueError:
                        data_hora = None

                # Processar status_leitura se fornecido
                status_leitura = leitura_data.get('status_leitura', StatusLeitura.VALIDA)

                # Registrar leitura
                leitura_id = self.registrar_leitura(
                    sensor_id=sensor_id,
                    valor=valor,
                    unidade_medida=unidade_medida,
                    data_hora=data_hora,
                    status_leitura=status_leitura,
                    observacao=leitura_data.get('observacao')
                )

                leitura_ids.append(leitura_id)

            except Exception as e:
                logger.error(f"Erro ao processar leitura: {str(e)}")
                continue

        return leitura_ids

    def obter_estatisticas_sensor(self, sensor_id: int,
                                 periodo_dias: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas de um sensor para um período específico"""
        # Verificar se o sensor existe
        sensor = self.sensor_repository.obter_sensor(sensor_id)
        if not sensor:
            logger.error(f"Sensor ID {sensor_id} não encontrado")
            raise ValueError(f"Sensor ID {sensor_id} não encontrado")

        # Calcular período de datas
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)

        # Obter estatísticas
        estatisticas = self.leitura_repository.obter_estatisticas_leituras(
            sensor_id=sensor_id,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        # Obter leituras recentes
        leituras_recentes = self.leitura_repository.listar_leituras(
            sensor_id=sensor_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=100
        )

        # Adicionar informações do sensor às estatísticas
        estatisticas['sensor_id'] = sensor_id
        estatisticas['tipo_sensor'] = sensor.tipo_sensor.value if hasattr(sensor.tipo_sensor, 'value') else sensor.tipo_sensor
        estatisticas['modelo'] = sensor.modelo
        estatisticas['status'] = sensor.status.value if hasattr(sensor.status, 'value') else sensor.status
        estatisticas['area_id'] = sensor.area_id

        # Adicionar valores das leituras recentes
        if leituras_recentes:
            estatisticas['ultima_leitura'] = leituras_recentes[0].to_dict()
            estatisticas['leituras_recentes'] = [l.valor for l in leituras_recentes]
            estatisticas['timestamps_recentes'] = [l.data_hora.isoformat() if isinstance(l.data_hora, datetime) else l.data_hora for l in leituras_recentes]

        return estatisticas

    def analisar_tendencia_sensor(self, sensor_id: int,
                                 periodo_dias: int = 30) -> Dict[str, Any]:
        """Analisa a tendência de leituras de um sensor ao longo do tempo"""
        # Verificar se o sensor existe
        sensor = self.sensor_repository.obter_sensor(sensor_id)
        if not sensor:
            logger.error(f"Sensor ID {sensor_id} não encontrado")
            raise ValueError(f"Sensor ID {sensor_id} não encontrado")

        # Calcular período de datas
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)

        # Obter leituras para o período
        leituras = self.leitura_repository.listar_leituras(
            sensor_id=sensor_id,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        if not leituras:
            return {
                'sensor_id': sensor_id,
                'tendencia': 'neutra',
                'variacao_percentual': 0,
                'leituras_count': 0,
                'mensagem': 'Não há leituras suficientes para análise'
            }

        # Ordenar leituras por data
        leituras.sort(key=lambda l: l.data_hora if isinstance(l.data_hora, datetime) else datetime.fromisoformat(l.data_hora))

        # Calcular tendência
        if len(leituras) >= 2:
            primeira_leitura = leituras[0].valor
            ultima_leitura = leituras[-1].valor

            if primeira_leitura == 0:
                variacao_percentual = 100 if ultima_leitura > 0 else 0
            else:
                variacao_percentual = ((ultima_leitura - primeira_leitura) / primeira_leitura) * 100

            # Determinar tendência com base na variação
            if variacao_percentual > 5:
                tendencia = 'crescente'
            elif variacao_percentual < -5:
                tendencia = 'decrescente'
            else:
                tendencia = 'estável'
        else:
            tendencia = 'neutra'
            variacao_percentual = 0

        return {
            'sensor_id': sensor_id,
            'tendencia': tendencia,
            'variacao_percentual': round(variacao_percentual, 2),
            'leituras_count': len(leituras),
            'primeira_leitura': leituras[0].valor if leituras else None,
            'ultima_leitura': leituras[-1].valor if leituras else None,
            'periodo_dias': periodo_dias
        }


class RecomendacaoService:
    """Serviço para geração de recomendações baseadas em dados de sensores"""

    def __init__(self, sensor_service=None):
        """Inicializa o serviço de recomendações"""
        self.sensor_service = sensor_service or SensorService()

    def gerar_recomendacao_irrigacao(self, plantio_id: int, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Gera uma recomendação de irrigação com base nas leituras de umidade"""
        # Obter informações do sensor
        sensor = self.sensor_service.sensor_repository.obter_sensor(sensor_id)
        if not sensor or sensor.tipo_sensor != TipoSensor.UMIDADE:
            logger.error(f"Sensor ID {sensor_id} não encontrado ou não é um sensor de umidade")
            return None

        # Obter estatísticas recentes
        estatisticas = self.sensor_service.obter_estatisticas_sensor(sensor_id, periodo_dias=3)

        # Se não há leituras suficientes
        if estatisticas.get('total', 0) < 3:
            return {
                'plantio_id': plantio_id,
                'tipo_recurso': 'água',
                'recomendacao': None,
                'mensagem': 'Não há leituras suficientes para gerar uma recomendação'
            }

        # Analisar nível de umidade
        umidade_atual = estatisticas.get('ultima_leitura', {}).get('valor')
        if umidade_atual is None:
            return None

        # Determinar nível de umidade e recomendação
        # Assume-se que umidade é medida em percentual (0-100%)
        if umidade_atual < 30:
            quantidade = 20  # litros por m²
            prioridade = PrioridadeRecomendacao.ALTA
            justificativa = f"Umidade muito baixa ({umidade_atual}%). Irrigação urgente necessária."
        elif umidade_atual < 50:
            quantidade = 10  # litros por m²
            prioridade = PrioridadeRecomendacao.MEDIA
            justificativa = f"Umidade baixa ({umidade_atual}%). Irrigação recomendada."
        elif umidade_atual < 70:
            quantidade = 5  # litros por m²
            prioridade = PrioridadeRecomendacao.BAIXA
            justificativa = f"Umidade moderada ({umidade_atual}%). Irrigação leve recomendada."
        else:
            quantidade = 0
            prioridade = None
            justificativa = f"Umidade adequada ({umidade_atual}%). Irrigação não necessária no momento."

        if quantidade > 0:
            recomendacao = {
                'plantio_id': plantio_id,
                'tipo_recurso': 'água',
                'quantidade': quantidade,
                'unidade_medida': 'L/m²',
                'prioridade': prioridade.value if prioridade else None,
                'justificativa': justificativa,
                'data_prevista_aplicacao': (datetime.now() + timedelta(days=1)).date()
            }
        else:
            recomendacao = None

        return {
            'plantio_id': plantio_id,
            'tipo_recurso': 'água',
            'recomendacao': recomendacao,
            'mensagem': justificativa
        }

    def gerar_recomendacao_nutrientes(self, plantio_id: int, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Gera uma recomendação de aplicação de nutrientes com base nas leituras de sensor"""
        # Obter informações do sensor
        sensor = self.sensor_service.sensor_repository.obter_sensor(sensor_id)
        if not sensor or sensor.tipo_sensor != TipoSensor.NUTRIENTES:
            logger.error(f"Sensor ID {sensor_id} não encontrado ou não é um sensor de nutrientes")
            return None

        # Obter estatísticas recentes
        estatisticas = self.sensor_service.obter_estatisticas_sensor(sensor_id, periodo_dias=7)

        # Se não há leituras suficientes
        if estatisticas.get('total', 0) < 3:
            return {
                'plantio_id': plantio_id,
                'tipo_recurso': 'nutriente',
                'recomendacao': None,
                'mensagem': 'Não há leituras suficientes para gerar uma recomendação'
            }

        # Analisar nível de nutrientes
        nivel_atual = estatisticas.get('ultima_leitura', {}).get('valor')
        if nivel_atual is None:
            return None

        # Determinar nível de nutrientes e recomendação
        # Assume-se que o nível é medido em ppm (partes por milhão)
        if nivel_atual < 100:
            quantidade = 50  # kg por hectare
            prioridade = PrioridadeRecomendacao.ALTA
            justificativa = f"Nível de nutrientes muito baixo ({nivel_atual} ppm). Aplicação urgente necessária."
        elif nivel_atual < 200:
            quantidade = 30  # kg por hectare
            prioridade = PrioridadeRecomendacao.MEDIA
            justificativa = f"Nível de nutrientes baixo ({nivel_atual} ppm). Aplicação recomendada."
        elif nivel_atual < 300:
            quantidade = 15  # kg por hectare
            prioridade = PrioridadeRecomendacao.BAIXA
            justificativa = f"Nível de nutrientes moderado ({nivel_atual} ppm). Aplicação leve recomendada."
        else:
            quantidade = 0
            prioridade = None
            justificativa = f"Nível de nutrientes adequado ({nivel_atual} ppm). Aplicação não necessária no momento."

        if quantidade > 0:
            recomendacao = {
                'plantio_id': plantio_id,
                'tipo_recurso': 'NPK',
                'quantidade': quantidade,
                'unidade_medida': 'kg/ha',
                'prioridade': prioridade.value if prioridade else None,
                'justificativa': justificativa,
                'data_prevista_aplicacao': (datetime.now() + timedelta(days=2)).date()
            }
        else:
            recomendacao = None

        return {
            'plantio_id': plantio_id,
            'tipo_recurso': 'nutriente',
            'recomendacao': recomendacao,
            'mensagem': justificativa
        }

    def gerar_recomendacao_ph(self, plantio_id: int, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Gera uma recomendação de correção de pH com base nas leituras de sensor"""
        # Obter informações do sensor
        sensor = self.sensor_service.sensor_repository.obter_sensor(sensor_id)
        if not sensor or sensor.tipo_sensor != TipoSensor.PH:
            logger.error(f"Sensor ID {sensor_id} não encontrado ou não é um sensor de pH")
            return None

        # Obter estatísticas recentes
        estatisticas = self.sensor_service.obter_estatisticas_sensor(sensor_id, periodo_dias=7)

        # Se não há leituras suficientes
        if estatisticas.get('total', 0) < 3:
            return {
                'plantio_id': plantio_id,
                'tipo_recurso': 'corretivo_ph',
                'recomendacao': None,
                'mensagem': 'Não há leituras suficientes para gerar uma recomendação'
            }

        # Analisar nível de pH
        ph_atual = estatisticas.get('ultima_leitura', {}).get('valor')
        if ph_atual is None:
            return None

        # Determinar nível de pH e recomendação
        # Assume-se que o pH ideal está entre 6.0 e 7.0
        if ph_atual < 5.0:
            tipo_corretivo = 'calcário'
            quantidade = 2.0  # toneladas por hectare
            prioridade = PrioridadeRecomendacao.ALTA
            justificativa = f"pH muito ácido ({ph_atual}). Aplicação de calcário urgente necessária."
        elif ph_atual < 6.0:
            tipo_corretivo = 'calcário'
            quantidade = 1.0  # toneladas por hectare
            prioridade = PrioridadeRecomendacao.MEDIA
            justificativa = f"pH ácido ({ph_atual}). Aplicação de calcário recomendada."
        elif ph_atual > 8.0:
            tipo_corretivo = 'enxofre'
            quantidade = 1.5  # toneladas por hectare
            prioridade = PrioridadeRecomendacao.ALTA
            justificativa = f"pH muito alcalino ({ph_atual}). Aplicação de enxofre urgente necessária."
        elif ph_atual > 7.0:
            tipo_corretivo = 'enxofre'
            quantidade = 0.8  # toneladas por hectare
            prioridade = PrioridadeRecomendacao.MEDIA
            justificativa = f"pH alcalino ({ph_atual}). Aplicação de enxofre recomendada."
        else:
            tipo_corretivo = None
            quantidade = 0
            prioridade = None
            justificativa = f"pH adequado ({ph_atual}). Correção não necessária no momento."

        if quantidade > 0:
            recomendacao = {
                'plantio_id': plantio_id,
                'tipo_recurso': tipo_corretivo,
                'quantidade': quantidade,
                'unidade_medida': 't/ha',
                'prioridade': prioridade.value if prioridade else None,
                'justificativa': justificativa,
                'data_prevista_aplicacao': (datetime.now() + timedelta(days=5)).date()
            }
        else:
            recomendacao = None

        return {
            'plantio_id': plantio_id,
            'tipo_recurso': 'corretivo_ph',
            'recomendacao': recomendacao,
            'mensagem': justificativa
        }

    def gerar_recomendacoes_para_plantio(self, plantio_id: int) -> List[Dict[str, Any]]:
        """Gera recomendações para um plantio com base em todos os sensores disponíveis"""
        # TODO: Implementar a lógica para obter os sensores associados a um plantio
        # e gerar recomendações específicas para cada tipo de sensor

        # Este é um exemplo simplificado
        recomendacoes = []

        # Assumindo que temos sensores de todos os tipos para este plantio
        # Em uma implementação real, seria necessário consultar o banco de dados

        # Exemplo: sensor de umidade com ID 1
        recomendacao_irrigacao = self.gerar_recomendacao_irrigacao(plantio_id, 1)
        if recomendacao_irrigacao and recomendacao_irrigacao.get('recomendacao'):
            recomendacoes.append(recomendacao_irrigacao)

        # Exemplo: sensor de nutrientes com ID 2
        recomendacao_nutrientes = self.gerar_recomendacao_nutrientes(plantio_id, 2)
        if recomendacao_nutrientes and recomendacao_nutrientes.get('recomendacao'):
            recomendacoes.append(recomendacao_nutrientes)

        # Exemplo: sensor de pH com ID 3
        recomendacao_ph = self.gerar_recomendacao_ph(plantio_id, 3)
        if recomendacao_ph and recomendacao_ph.get('recomendacao'):
            recomendacoes.append(recomendacao_ph)

        return recomendacoes
