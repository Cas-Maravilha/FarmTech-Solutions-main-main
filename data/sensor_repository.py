#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Repositório de Dados de Sensoriamento
Classes para acessar e manipular dados de sensores, leituras e recomendações
"""

import os
import json
import csv
import sqlite3
from datetime import datetime, date, timedelta
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

# Importar os modelos de dados
from models.sensor_models import (
    Sensor, Leitura, Area, Plantio, Recomendacao, Aplicacao,
    TipoSensor, StatusSensor, StatusLeitura, StatusPlantio,
    PrioridadeRecomendacao, StatusRecomendacao
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sensor_repository')

# Caminho do banco de dados SQLite
DB_PATH = 'data/farmtech.db'

class DatabaseManager:
    """Gerencia a conexão com o banco de dados"""

    def __init__(self, db_path=DB_PATH):
        """Inicializa o gerenciador de banco de dados"""
        self.db_path = db_path
        self._ensure_tables()

    def _get_connection(self):
        """Obtém uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
        return conn

    def _ensure_tables(self):
        """Garante que as tabelas necessárias existam no banco de dados"""
        # Criar diretório do banco de dados se não existir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        # Criar tabela AREA
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS area (
            area_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tamanho_hectares REAL NOT NULL,
            latitude REAL,
            longitude REAL,
            tipo_solo TEXT,
            declividade REAL
        )
        ''')

        # Criar tabela SENSOR
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor (
            sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_sensor TEXT NOT NULL,
            modelo TEXT,
            latitude REAL,
            longitude REAL,
            data_instalacao DATE NOT NULL,
            ultima_manutencao DATE,
            status TEXT DEFAULT 'ativo',
            area_id INTEGER,
            FOREIGN KEY (area_id) REFERENCES area(area_id)
        )
        ''')

        # Criar tabela LEITURA
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leitura (
            leitura_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL,
            data_hora TIMESTAMP NOT NULL,
            valor REAL NOT NULL,
            unidade_medida TEXT NOT NULL,
            status_leitura TEXT DEFAULT 'válida',
            observacao TEXT,
            FOREIGN KEY (sensor_id) REFERENCES sensor(sensor_id)
        )
        ''')

        # Criar tabela CULTURA
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cultura (
            cultura_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            variedade TEXT,
            data_plantio DATE,
            ciclo_dias INTEGER,
            umidade_ideal_min REAL,
            umidade_ideal_max REAL,
            ph_ideal_min REAL,
            ph_ideal_max REAL,
            fosforo_ideal_min REAL,
            fosforo_ideal_max REAL,
            potassio_ideal_min REAL,
            potassio_ideal_max REAL
        )
        ''')

        # Criar tabela PLANTIO
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plantio (
            plantio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cultura_id INTEGER NOT NULL,
            area_id INTEGER NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim_prevista DATE,
            data_fim_real DATE,
            status TEXT DEFAULT 'ativo',
            producao_estimada REAL,
            producao_real REAL,
            FOREIGN KEY (cultura_id) REFERENCES cultura(cultura_id),
            FOREIGN KEY (area_id) REFERENCES area(area_id)
        )
        ''')

        # Criar tabela RECOMENDACAO
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recomendacao (
            recomendacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plantio_id INTEGER NOT NULL,
            tipo_recurso TEXT NOT NULL,
            quantidade REAL NOT NULL,
            unidade_medida TEXT NOT NULL,
            data_hora_geracao TIMESTAMP NOT NULL,
            data_prevista_aplicacao DATE,
            prioridade TEXT DEFAULT 'média',
            status TEXT DEFAULT 'pendente',
            justificativa TEXT,
            FOREIGN KEY (plantio_id) REFERENCES plantio(plantio_id)
        )
        ''')

        # Criar tabela APLICACAO
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS aplicacao (
            aplicacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plantio_id INTEGER NOT NULL,
            tipo_recurso TEXT NOT NULL,
            quantidade REAL NOT NULL,
            unidade_medida TEXT NOT NULL,
            data_hora TIMESTAMP NOT NULL,
            metodo_aplicacao TEXT,
            responsavel TEXT,
            recomendacao_id INTEGER,
            FOREIGN KEY (plantio_id) REFERENCES plantio(plantio_id),
            FOREIGN KEY (recomendacao_id) REFERENCES recomendacao(recomendacao_id)
        )
        ''')

        conn.commit()
        conn.close()

        logger.info("Tabelas verificadas e criadas se necessário")


class SensorRepository:
    """Repositório para acesso aos dados de sensores"""

    def __init__(self, db_manager=None):
        """Inicializa o repositório de sensores"""
        self.db_manager = db_manager or DatabaseManager()

    def adicionar_sensor(self, sensor: Sensor) -> int:
        """Adiciona um novo sensor ao banco de dados"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        tipo_sensor = sensor.tipo_sensor.value if isinstance(sensor.tipo_sensor, TipoSensor) else sensor.tipo_sensor
        status = sensor.status.value if isinstance(sensor.status, StatusSensor) else sensor.status

        cursor.execute('''
        INSERT INTO sensor (tipo_sensor, modelo, latitude, longitude,
                           data_instalacao, ultima_manutencao, status, area_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tipo_sensor,
            sensor.modelo,
            sensor.latitude,
            sensor.longitude,
            sensor.data_instalacao.isoformat() if isinstance(sensor.data_instalacao, date) else sensor.data_instalacao,
            sensor.ultima_manutencao.isoformat() if isinstance(sensor.ultima_manutencao, date) else sensor.ultima_manutencao,
            status,
            sensor.area_id
        ))

        sensor_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Sensor adicionado com ID: {sensor_id}")
        return sensor_id

    def atualizar_sensor(self, sensor: Sensor) -> bool:
        """Atualiza um sensor existente no banco de dados"""
        if sensor.sensor_id is None:
            logger.error("Tentativa de atualizar sensor sem ID")
            return False

        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        tipo_sensor = sensor.tipo_sensor.value if isinstance(sensor.tipo_sensor, TipoSensor) else sensor.tipo_sensor
        status = sensor.status.value if isinstance(sensor.status, StatusSensor) else sensor.status

        cursor.execute('''
        UPDATE sensor
        SET tipo_sensor = ?,
            modelo = ?,
            latitude = ?,
            longitude = ?,
            data_instalacao = ?,
            ultima_manutencao = ?,
            status = ?,
            area_id = ?
        WHERE sensor_id = ?
        ''', (
            tipo_sensor,
            sensor.modelo,
            sensor.latitude,
            sensor.longitude,
            sensor.data_instalacao.isoformat() if isinstance(sensor.data_instalacao, date) else sensor.data_instalacao,
            sensor.ultima_manutencao.isoformat() if isinstance(sensor.ultima_manutencao, date) else sensor.ultima_manutencao,
            status,
            sensor.area_id,
            sensor.sensor_id
        ))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            logger.info(f"Sensor atualizado: ID {sensor.sensor_id}")
        else:
            logger.warning(f"Sensor não encontrado para atualização: ID {sensor.sensor_id}")

        return success

    def remover_sensor(self, sensor_id: int) -> bool:
        """Remove um sensor do banco de dados"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        # Primeiro remover as leituras associadas
        cursor.execute('DELETE FROM leitura WHERE sensor_id = ?', (sensor_id,))

        # Depois remover o sensor
        cursor.execute('DELETE FROM sensor WHERE sensor_id = ?', (sensor_id,))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            logger.info(f"Sensor removido: ID {sensor_id}")
        else:
            logger.warning(f"Sensor não encontrado para remoção: ID {sensor_id}")

        return success

    def obter_sensor(self, sensor_id: int) -> Optional[Sensor]:
        """Obtém um sensor pelo ID"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM sensor WHERE sensor_id = ?', (sensor_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            # Converter row para dicionário
            sensor_dict = {column: row[column] for column in row.keys()}
            return Sensor.from_dict(sensor_dict)

        return None

    def listar_sensores(self, area_id: Optional[int] = None, tipo_sensor: Optional[str] = None,
                       status: Optional[str] = None) -> List[Sensor]:
        """Lista sensores com opção de filtro por área, tipo e status"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM sensor'
        params = []

        # Adicionar filtros
        filters = []
        if area_id is not None:
            filters.append('area_id = ?')
            params.append(area_id)

        if tipo_sensor is not None:
            filters.append('tipo_sensor = ?')
            params.append(tipo_sensor)

        if status is not None:
            filters.append('status = ?')
            params.append(status)

        if filters:
            query += ' WHERE ' + ' AND '.join(filters)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        conn.close()

        # Converter rows para objetos Sensor
        sensores = []
        for row in rows:
            sensor_dict = {column: row[column] for column in row.keys()}
            sensores.append(Sensor.from_dict(sensor_dict))

        return sensores


class LeituraRepository:
    """Repositório para acesso aos dados de leituras"""

    def __init__(self, db_manager=None):
        """Inicializa o repositório de leituras"""
        self.db_manager = db_manager or DatabaseManager()

    def adicionar_leitura(self, leitura: Leitura) -> int:
        """Adiciona uma nova leitura ao banco de dados"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        status_leitura = leitura.status_leitura.value if isinstance(leitura.status_leitura, StatusLeitura) else leitura.status_leitura

        cursor.execute('''
        INSERT INTO leitura (sensor_id, data_hora, valor, unidade_medida, status_leitura, observacao)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            leitura.sensor_id,
            leitura.data_hora.isoformat() if isinstance(leitura.data_hora, datetime) else leitura.data_hora,
            leitura.valor,
            leitura.unidade_medida,
            status_leitura,
            leitura.observacao
        ))

        leitura_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Leitura adicionada com ID: {leitura_id}")
        return leitura_id

    def obter_leitura(self, leitura_id: int) -> Optional[Leitura]:
        """Obtém uma leitura pelo ID"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM leitura WHERE leitura_id = ?', (leitura_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            # Converter row para dicionário
            leitura_dict = {column: row[column] for column in row.keys()}
            return Leitura.from_dict(leitura_dict)

        return None

    def listar_leituras(self, sensor_id: Optional[int] = None,
                        data_inicio: Optional[datetime] = None,
                        data_fim: Optional[datetime] = None,
                        limit: Optional[int] = None) -> List[Leitura]:
        """Lista leituras com opção de filtro por sensor e período"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM leitura'
        params = []

        # Adicionar filtros
        filters = []
        if sensor_id is not None:
            filters.append('sensor_id = ?')
            params.append(sensor_id)

        if data_inicio is not None:
            filters.append('data_hora >= ?')
            params.append(data_inicio.isoformat() if isinstance(data_inicio, datetime) else data_inicio)

        if data_fim is not None:
            filters.append('data_hora <= ?')
            params.append(data_fim.isoformat() if isinstance(data_fim, datetime) else data_fim)

        if filters:
            query += ' WHERE ' + ' AND '.join(filters)

        query += ' ORDER BY data_hora DESC'

        if limit is not None:
            query += f' LIMIT {limit}'

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        conn.close()

        # Converter rows para objetos Leitura
        leituras = []
        for row in rows:
            leitura_dict = {column: row[column] for column in row.keys()}
            leituras.append(Leitura.from_dict(leitura_dict))

        return leituras

    def obter_estatisticas_leituras(self, sensor_id: int,
                                   data_inicio: Optional[datetime] = None,
                                   data_fim: Optional[datetime] = None) -> Dict[str, float]:
        """Obtém estatísticas (média, máximo, mínimo) de leituras de um sensor"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        query = '''
        SELECT
            AVG(valor) as media,
            MAX(valor) as maximo,
            MIN(valor) as minimo,
            COUNT(leitura_id) as total
        FROM leitura
        WHERE sensor_id = ?
        '''

        params = [sensor_id]

        if data_inicio is not None:
            query += ' AND data_hora >= ?'
            params.append(data_inicio.isoformat() if isinstance(data_inicio, datetime) else data_inicio)

        if data_fim is not None:
            query += ' AND data_hora <= ?'
            params.append(data_fim.isoformat() if isinstance(data_fim, datetime) else data_fim)

        cursor.execute(query, tuple(params))
        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                'media': row['media'],
                'maximo': row['maximo'],
                'minimo': row['minimo'],
                'total': row['total']
            }

        return {
            'media': None,
            'maximo': None,
            'minimo': None,
            'total': 0
        }


class AreaRepository:
    """Repositório para acesso aos dados de áreas"""

    def __init__(self, db_manager=None):
        """Inicializa o repositório de áreas"""
        self.db_manager = db_manager or DatabaseManager()

    def adicionar_area(self, area: Area) -> int:
        """Adiciona uma nova área ao banco de dados"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO area (nome, tamanho_hectares, latitude, longitude, tipo_solo, declividade)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            area.nome,
            area.tamanho_hectares,
            area.latitude,
            area.longitude,
            area.tipo_solo,
            area.declividade
        ))

        area_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Área adicionada com ID: {area_id}")
        return area_id

    def atualizar_area(self, area: Area) -> bool:
        """Atualiza uma área existente no banco de dados"""
        if area.area_id is None:
            logger.error("Tentativa de atualizar área sem ID")
            return False

        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE area
        SET nome = ?,
            tamanho_hectares = ?,
            latitude = ?,
            longitude = ?,
            tipo_solo = ?,
            declividade = ?
        WHERE area_id = ?
        ''', (
            area.nome,
            area.tamanho_hectares,
            area.latitude,
            area.longitude,
            area.tipo_solo,
            area.declividade,
            area.area_id
        ))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            logger.info(f"Área atualizada: ID {area.area_id}")
        else:
            logger.warning(f"Área não encontrada para atualização: ID {area.area_id}")

        return success

    def remover_area(self, area_id: int) -> bool:
        """Remove uma área do banco de dados"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        # Verificar se existem sensores ou plantios associados
        cursor.execute('SELECT COUNT(*) FROM sensor WHERE area_id = ?', (area_id,))
        sensores_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM plantio WHERE area_id = ?', (area_id,))
        plantios_count = cursor.fetchone()[0]

        if sensores_count > 0 or plantios_count > 0:
            logger.warning(f"Não é possível remover área ID {area_id}: existem sensores ou plantios associados")
            conn.close()
            return False

        # Se não houver dependências, remover a área
        cursor.execute('DELETE FROM area WHERE area_id = ?', (area_id,))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            logger.info(f"Área removida: ID {area_id}")
        else:
            logger.warning(f"Área não encontrada para remoção: ID {area_id}")

        return success

    def obter_area(self, area_id: int) -> Optional[Area]:
        """Obtém uma área pelo ID"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM area WHERE area_id = ?', (area_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            # Converter row para dicionário
            area_dict = {column: row[column] for column in row.keys()}
            return Area.from_dict(area_dict)

        return None

    def listar_areas(self) -> List[Area]:
        """Lista todas as áreas"""
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM area')
        rows = cursor.fetchall()

        conn.close()

        # Converter rows para objetos Area
        areas = []
        for row in rows:
            area_dict = {column: row[column] for column in row.keys()}
            areas.append(Area.from_dict(area_dict))

        return areas


# Repositórios adicionais seriam implementados de forma similar
# PlantioRepository, RecomendacaoRepository, AplicacaoRepository
