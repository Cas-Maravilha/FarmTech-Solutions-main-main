#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Modelos de Dados para Sensoriamento
Classes para representar sensores, leituras e recomendações
"""

from datetime import datetime
from enum import Enum


class TipoSensor(Enum):
    """Tipos de sensores disponíveis no sistema"""
    UMIDADE = 'S1'
    PH = 'S2'
    NUTRIENTES = 'S3'


class StatusSensor(Enum):
    """Status possíveis para um sensor"""
    ATIVO = 'ativo'
    INATIVO = 'inativo'
    MANUTENCAO = 'manutenção'
    ERRO = 'erro'


class StatusLeitura(Enum):
    """Status possíveis para uma leitura de sensor"""
    VALIDA = 'válida'
    INVALIDA = 'inválida'
    ALERTA = 'alerta'
    ERRO = 'erro'


class Sensor:
    """Representa um sensor físico instalado na lavoura"""

    def __init__(self, sensor_id=None, tipo_sensor=None, modelo=None,
                 latitude=None, longitude=None, data_instalacao=None,
                 ultima_manutencao=None, status=StatusSensor.ATIVO, area_id=None):
        """Inicializa um sensor com seus atributos"""
        self.sensor_id = sensor_id
        self.tipo_sensor = tipo_sensor
        self.modelo = modelo
        self.latitude = latitude
        self.longitude = longitude
        self.data_instalacao = data_instalacao or datetime.now().date()
        self.ultima_manutencao = ultima_manutencao
        self.status = status
        self.area_id = area_id

    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'sensor_id': self.sensor_id,
            'tipo_sensor': self.tipo_sensor.value if isinstance(self.tipo_sensor, TipoSensor) else self.tipo_sensor,
            'modelo': self.modelo,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'data_instalacao': self.data_instalacao.isoformat() if self.data_instalacao else None,
            'ultima_manutencao': self.ultima_manutencao.isoformat() if self.ultima_manutencao else None,
            'status': self.status.value if isinstance(self.status, StatusSensor) else self.status,
            'area_id': self.area_id
        }

    @classmethod
    def from_dict(cls, data):
        """Cria um objeto Sensor a partir de um dicionário"""
        if not data:
            return None

        # Converte strings de enumeração para objetos Enum
        tipo_sensor = data.get('tipo_sensor')
        if tipo_sensor and isinstance(tipo_sensor, str):
            try:
                tipo_sensor = TipoSensor(tipo_sensor)
            except ValueError:
                pass

        status = data.get('status')
        if status and isinstance(status, str):
            try:
                status = StatusSensor(status)
            except ValueError:
                pass

        # Converte strings de data para objetos date
        data_instalacao = data.get('data_instalacao')
        if data_instalacao and isinstance(data_instalacao, str):
            try:
                data_instalacao = datetime.fromisoformat(data_instalacao).date()
            except ValueError:
                data_instalacao = None

        ultima_manutencao = data.get('ultima_manutencao')
        if ultima_manutencao and isinstance(ultima_manutencao, str):
            try:
                ultima_manutencao = datetime.fromisoformat(ultima_manutencao).date()
            except ValueError:
                ultima_manutencao = None

        return cls(
            sensor_id=data.get('sensor_id'),
            tipo_sensor=tipo_sensor,
            modelo=data.get('modelo'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            data_instalacao=data_instalacao,
            ultima_manutencao=ultima_manutencao,
            status=status,
            area_id=data.get('area_id')
        )


class Leitura:
    """Representa uma leitura de um sensor"""

    def __init__(self, leitura_id=None, sensor_id=None, data_hora=None,
                 valor=None, unidade_medida=None, status_leitura=StatusLeitura.VALIDA,
                 observacao=None):
        """Inicializa uma leitura com seus atributos"""
        self.leitura_id = leitura_id
        self.sensor_id = sensor_id
        self.data_hora = data_hora or datetime.now()
        self.valor = valor
        self.unidade_medida = unidade_medida
        self.status_leitura = status_leitura
        self.observacao = observacao

    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'leitura_id': self.leitura_id,
            'sensor_id': self.sensor_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'valor': self.valor,
            'unidade_medida': self.unidade_medida,
            'status_leitura': self.status_leitura.value if isinstance(self.status_leitura, StatusLeitura) else self.status_leitura,
            'observacao': self.observacao
        }

    @classmethod
    def from_dict(cls, data):
        """Cria um objeto Leitura a partir de um dicionário"""
        if not data:
            return None

        # Converte string de status para objeto Enum
        status_leitura = data.get('status_leitura')
        if status_leitura and isinstance(status_leitura, str):
            try:
                status_leitura = StatusLeitura(status_leitura)
            except ValueError:
                pass

        # Converte string de data/hora para objeto datetime
        data_hora = data.get('data_hora')
        if data_hora and isinstance(data_hora, str):
            try:
                data_hora = datetime.fromisoformat(data_hora)
            except ValueError:
                data_hora = None

        return cls(
            leitura_id=data.get('leitura_id'),
            sensor_id=data.get('sensor_id'),
            data_hora=data_hora,
            valor=data.get('valor'),
            unidade_medida=data.get('unidade_medida'),
            status_leitura=status_leitura,
            observacao=data.get('observacao')
        )


class Area:
    """Representa uma área de plantio"""

    def __init__(self, area_id=None, nome=None, tamanho_hectares=None,
                 latitude=None, longitude=None, tipo_solo=None, declividade=None):
        """Inicializa uma área com seus atributos"""
        self.area_id = area_id
        self.nome = nome
        self.tamanho_hectares = tamanho_hectares
        self.latitude = latitude
        self.longitude = longitude
        self.tipo_solo = tipo_solo
        self.declividade = declividade

    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'area_id': self.area_id,
            'nome': self.nome,
            'tamanho_hectares': self.tamanho_hectares,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'tipo_solo': self.tipo_solo,
            'declividade': self.declividade
        }

    @classmethod
    def from_dict(cls, data):
        """Cria um objeto Area a partir de um dicionário"""
        if not data:
            return None

        return cls(
            area_id=data.get('area_id'),
            nome=data.get('nome'),
            tamanho_hectares=data.get('tamanho_hectares'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            tipo_solo=data.get('tipo_solo'),
            declividade=data.get('declividade')
        )


class StatusPlantio(Enum):
    """Status possíveis para um plantio"""
    ATIVO = 'ativo'
    CONCLUIDO = 'concluído'
    PERDIDO = 'perdido'
    PLANEJADO = 'planejado'


class Plantio:
    """Representa um plantio específico em uma área"""

    def __init__(self, plantio_id=None, cultura_id=None, area_id=None,
                 data_inicio=None, data_fim_prevista=None, data_fim_real=None,
                 status=StatusPlantio.ATIVO, producao_estimada=None, producao_real=None):
        """Inicializa um plantio com seus atributos"""
        self.plantio_id = plantio_id
        self.cultura_id = cultura_id
        self.area_id = area_id
        self.data_inicio = data_inicio or datetime.now().date()
        self.data_fim_prevista = data_fim_prevista
        self.data_fim_real = data_fim_real
        self.status = status
        self.producao_estimada = producao_estimada
        self.producao_real = producao_real

    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'plantio_id': self.plantio_id,
            'cultura_id': self.cultura_id,
            'area_id': self.area_id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim_prevista': self.data_fim_prevista.isoformat() if self.data_fim_prevista else None,
            'data_fim_real': self.data_fim_real.isoformat() if self.data_fim_real else None,
            'status': self.status.value if isinstance(self.status, StatusPlantio) else self.status,
            'producao_estimada': self.producao_estimada,
            'producao_real': self.producao_real
        }

    @classmethod
    def from_dict(cls, data):
        """Cria um objeto Plantio a partir de um dicionário"""
        if not data:
            return None

        # Converte string de status para objeto Enum
        status = data.get('status')
        if status and isinstance(status, str):
            try:
                status = StatusPlantio(status)
            except ValueError:
                pass

        # Converte strings de data para objetos date
        data_inicio = data.get('data_inicio')
        if data_inicio and isinstance(data_inicio, str):
            try:
                data_inicio = datetime.fromisoformat(data_inicio).date()
            except ValueError:
                data_inicio = None

        data_fim_prevista = data.get('data_fim_prevista')
        if data_fim_prevista and isinstance(data_fim_prevista, str):
            try:
                data_fim_prevista = datetime.fromisoformat(data_fim_prevista).date()
            except ValueError:
                data_fim_prevista = None

        data_fim_real = data.get('data_fim_real')
        if data_fim_real and isinstance(data_fim_real, str):
            try:
                data_fim_real = datetime.fromisoformat(data_fim_real).date()
            except ValueError:
                data_fim_real = None

        return cls(
            plantio_id=data.get('plantio_id'),
            cultura_id=data.get('cultura_id'),
            area_id=data.get('area_id'),
            data_inicio=data_inicio,
            data_fim_prevista=data_fim_prevista,
            data_fim_real=data_fim_real,
            status=status,
            producao_estimada=data.get('producao_estimada'),
            producao_real=data.get('producao_real')
        )


class PrioridadeRecomendacao(Enum):
    """Níveis de prioridade para recomendações"""
    ALTA = 'alta'
    MEDIA = 'média'
    BAIXA = 'baixa'


class StatusRecomendacao(Enum):
    """Status possíveis para uma recomendação"""
    PENDENTE = 'pendente'
    APLICADA = 'aplicada'
    CANCELADA = 'cancelada'
    PROGRAMADA = 'programada'


class Recomendacao:
    """Representa uma recomendação gerada pelo sistema"""

    def __init__(self, recomendacao_id=None, plantio_id=None, tipo_recurso=None,
                 quantidade=None, unidade_medida=None, data_hora_geracao=None,
                 data_prevista_aplicacao=None, prioridade=PrioridadeRecomendacao.MEDIA,
                 status=StatusRecomendacao.PENDENTE, justificativa=None):
        """Inicializa uma recomendação com seus atributos"""
        self.recomendacao_id = recomendacao_id
        self.plantio_id = plantio_id
        self.tipo_recurso = tipo_recurso
        self.quantidade = quantidade
        self.unidade_medida = unidade_medida
        self.data_hora_geracao = data_hora_geracao or datetime.now()
        self.data_prevista_aplicacao = data_prevista_aplicacao
        self.prioridade = prioridade
        self.status = status
        self.justificativa = justificativa

    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'recomendacao_id': self.recomendacao_id,
            'plantio_id': self.plantio_id,
            'tipo_recurso': self.tipo_recurso,
            'quantidade': self.quantidade,
            'unidade_medida': self.unidade_medida,
            'data_hora_geracao': self.data_hora_geracao.isoformat() if self.data_hora_geracao else None,
            'data_prevista_aplicacao': self.data_prevista_aplicacao.isoformat() if self.data_prevista_aplicacao else None,
            'prioridade': self.prioridade.value if isinstance(self.prioridade, PrioridadeRecomendacao) else self.prioridade,
            'status': self.status.value if isinstance(self.status, StatusRecomendacao) else self.status,
            'justificativa': self.justificativa
        }

    @classmethod
    def from_dict(cls, data):
        """Cria um objeto Recomendacao a partir de um dicionário"""
        if not data:
            return None

        # Converte strings de enumeração para objetos Enum
        prioridade = data.get('prioridade')
        if prioridade and isinstance(prioridade, str):
            try:
                prioridade = PrioridadeRecomendacao(prioridade)
            except ValueError:
                pass

        status = data.get('status')
        if status and isinstance(status, str):
            try:
                status = StatusRecomendacao(status)
            except ValueError:
                pass

        # Converte strings de data/hora para objetos datetime/date
        data_hora_geracao = data.get('data_hora_geracao')
        if data_hora_geracao and isinstance(data_hora_geracao, str):
            try:
                data_hora_geracao = datetime.fromisoformat(data_hora_geracao)
            except ValueError:
                data_hora_geracao = None

        data_prevista_aplicacao = data.get('data_prevista_aplicacao')
        if data_prevista_aplicacao and isinstance(data_prevista_aplicacao, str):
            try:
                data_prevista_aplicacao = datetime.fromisoformat(data_prevista_aplicacao).date()
            except ValueError:
                data_prevista_aplicacao = None

        return cls(
            recomendacao_id=data.get('recomendacao_id'),
            plantio_id=data.get('plantio_id'),
            tipo_recurso=data.get('tipo_recurso'),
            quantidade=data.get('quantidade'),
            unidade_medida=data.get('unidade_medida'),
            data_hora_geracao=data_hora_geracao,
            data_prevista_aplicacao=data_prevista_aplicacao,
            prioridade=prioridade,
            status=status,
            justificativa=data.get('justificativa')
        )


class Aplicacao:
    """Representa uma aplicação de recurso em um plantio"""

    def __init__(self, aplicacao_id=None, plantio_id=None, tipo_recurso=None,
                 quantidade=None, unidade_medida=None, data_hora=None,
                 metodo_aplicacao=None, responsavel=None, recomendacao_id=None):
        """Inicializa uma aplicação com seus atributos"""
        self.aplicacao_id = aplicacao_id
        self.plantio_id = plantio_id
        self.tipo_recurso = tipo_recurso
        self.quantidade = quantidade
        self.unidade_medida = unidade_medida
        self.data_hora = data_hora or datetime.now()
        self.metodo_aplicacao = metodo_aplicacao
        self.responsavel = responsavel
        self.recomendacao_id = recomendacao_id

    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'aplicacao_id': self.aplicacao_id,
            'plantio_id': self.plantio_id,
            'tipo_recurso': self.tipo_recurso,
            'quantidade': self.quantidade,
            'unidade_medida': self.unidade_medida,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'metodo_aplicacao': self.metodo_aplicacao,
            'responsavel': self.responsavel,
            'recomendacao_id': self.recomendacao_id
        }

    @classmethod
    def from_dict(cls, data):
        """Cria um objeto Aplicacao a partir de um dicionário"""
        if not data:
            return None

        # Converte string de data/hora para objeto datetime
        data_hora = data.get('data_hora')
        if data_hora and isinstance(data_hora, str):
            try:
                data_hora = datetime.fromisoformat(data_hora)
            except ValueError:
                data_hora = None

        return cls(
            aplicacao_id=data.get('aplicacao_id'),
            plantio_id=data.get('plantio_id'),
            tipo_recurso=data.get('tipo_recurso'),
            quantidade=data.get('quantidade'),
            unidade_medida=data.get('unidade_medida'),
            data_hora=data_hora,
            metodo_aplicacao=data.get('metodo_aplicacao'),
            responsavel=data.get('responsavel'),
            recomendacao_id=data.get('recomendacao_id')
        )
