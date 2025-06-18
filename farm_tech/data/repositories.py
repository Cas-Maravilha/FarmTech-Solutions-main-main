#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Repositórios de Dados
Camada de acesso a dados com repositórios especializados
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json

from .database import DatabaseManager
from ..core.logger import get_database_logger

logger = get_database_logger()

@dataclass
class Sensor:
    """Modelo de dados para sensor"""
    sensor_id: int
    area_id: int
    tipo_sensor: str
    modelo: str
    status: str
    data_instalacao: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'sensor_id': self.sensor_id,
            'area_id': self.area_id,
            'tipo_sensor': self.tipo_sensor,
            'modelo': self.modelo,
            'status': self.status,
            'data_instalacao': self.data_instalacao.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude
        }

@dataclass
class Reading:
    """Modelo de dados para leitura"""
    leitura_id: int
    sensor_id: int
    data_hora: datetime
    valor: float
    unidade_medida: str
    status_leitura: str
    observacao: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'leitura_id': self.leitura_id,
            'sensor_id': self.sensor_id,
            'data_hora': self.data_hora.isoformat(),
            'valor': self.valor,
            'unidade_medida': self.unidade_medida,
            'status_leitura': self.status_leitura,
            'observacao': self.observacao
        }

@dataclass
class Area:
    """Modelo de dados para área"""
    area_id: int
    nome: str
    tamanho: float
    unidade_medida: str
    tipo_solo: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_cadastro: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'area_id': self.area_id,
            'nome': self.nome,
            'tamanho': self.tamanho,
            'unidade_medida': self.unidade_medida,
            'tipo_solo': self.tipo_solo,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

class SensorRepository:
    """Repositório para operações com sensores"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = get_database_logger()
    
    def get_all_sensors(self, area_id: Optional[int] = None, 
                       tipo_sensor: Optional[str] = None, 
                       status: Optional[str] = None) -> List[Sensor]:
        """Obtém todos os sensores com filtros opcionais"""
        try:
            query = "SELECT * FROM sensores WHERE 1=1"
            params = []
            
            if area_id:
                query += " AND area_id = ?"
                params.append(area_id)
            
            if tipo_sensor:
                query += " AND tipo_sensor = ?"
                params.append(tipo_sensor)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY sensor_id"
            
            results = self.db.execute_query(query, tuple(params))
            
            sensors = []
            for row in results:
                sensor = Sensor(
                    sensor_id=row['sensor_id'],
                    area_id=row['area_id'],
                    tipo_sensor=row['tipo_sensor'],
                    modelo=row['modelo'],
                    status=row['status'],
                    data_instalacao=datetime.fromisoformat(row['data_instalacao']),
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude')
                )
                sensors.append(sensor)
            
            return sensors
            
        except Exception as e:
            self.logger.error(f"Erro ao obter sensores: {e}")
            raise
    
    def get_sensor(self, sensor_id: int) -> Optional[Sensor]:
        """Obtém um sensor específico"""
        try:
            query = "SELECT * FROM sensores WHERE sensor_id = ?"
            results = self.db.execute_query(query, (sensor_id,))
            
            if results:
                row = results[0]
                return Sensor(
                    sensor_id=row['sensor_id'],
                    area_id=row['area_id'],
                    tipo_sensor=row['tipo_sensor'],
                    modelo=row['modelo'],
                    status=row['status'],
                    data_instalacao=datetime.fromisoformat(row['data_instalacao']),
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude')
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter sensor {sensor_id}: {e}")
            raise
    
    def add_sensor(self, area_id: int, tipo_sensor: str, modelo: str,
                   latitude: Optional[float] = None, 
                   longitude: Optional[float] = None) -> int:
        """Adiciona um novo sensor"""
        try:
            data = {
                'area_id': area_id,
                'tipo_sensor': tipo_sensor,
                'modelo': modelo,
                'latitude': latitude,
                'longitude': longitude
            }
            
            sensor_id = self.db.insert_data('sensores', data)
            self.logger.info(f"Sensor {sensor_id} adicionado com sucesso")
            return sensor_id
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar sensor: {e}")
            raise
    
    def update_sensor_status(self, sensor_id: int, status: str) -> bool:
        """Atualiza status de um sensor"""
        try:
            data = {'status': status}
            self.db.update_data('sensores', data, 'sensor_id = ?', (sensor_id,))
            
            self.logger.info(f"Status do sensor {sensor_id} atualizado para {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status do sensor {sensor_id}: {e}")
            raise
    
    def get_sensors_by_area(self, area_id: int) -> List[Sensor]:
        """Obtém todos os sensores de uma área"""
        return self.get_all_sensors(area_id=area_id)
    
    def get_sensors_by_type(self, tipo_sensor: str) -> List[Sensor]:
        """Obtém todos os sensores de um tipo específico"""
        return self.get_all_sensors(tipo_sensor=tipo_sensor)

class ReadingRepository:
    """Repositório para operações com leituras"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = get_database_logger()
    
    def get_readings(self, sensor_id: Optional[int] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    limit: int = 100) -> List[Reading]:
        """Obtém leituras com filtros opcionais"""
        try:
            query = "SELECT * FROM leituras WHERE 1=1"
            params = []
            
            if sensor_id:
                query += " AND sensor_id = ?"
                params.append(sensor_id)
            
            if start_date:
                query += " AND data_hora >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND data_hora <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY data_hora DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            results = self.db.execute_query(query, tuple(params))
            
            readings = []
            for row in results:
                reading = Reading(
                    leitura_id=row['leitura_id'],
                    sensor_id=row['sensor_id'],
                    data_hora=datetime.fromisoformat(row['data_hora']),
                    valor=row['valor'],
                    unidade_medida=row['unidade_medida'],
                    status_leitura=row['status_leitura'],
                    observacao=row.get('observacao')
                )
                readings.append(reading)
            
            return readings
            
        except Exception as e:
            self.logger.error(f"Erro ao obter leituras: {e}")
            raise
    
    def add_reading(self, sensor_id: int, value: float, unit: str,
                   timestamp: Optional[datetime] = None,
                   observation: Optional[str] = None) -> int:
        """Adiciona uma nova leitura"""
        try:
            data = {
                'sensor_id': sensor_id,
                'valor': value,
                'unidade_medida': unit,
                'observacao': observation
            }
            
            if timestamp:
                data['data_hora'] = timestamp.isoformat()
            
            reading_id = self.db.insert_data('leituras', data)
            self.logger.info(f"Leitura {reading_id} adicionada com sucesso")
            return reading_id
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar leitura: {e}")
            raise
    
    def add_readings_batch(self, readings: List[Dict[str, Any]]) -> int:
        """Adiciona múltiplas leituras em lote"""
        try:
            query = """
                INSERT INTO leituras (sensor_id, valor, unidade_medida, observacao)
                VALUES (?, ?, ?, ?)
            """
            
            params_list = []
            for reading in readings:
                params = (
                    reading['sensor_id'],
                    reading['valor'],
                    reading['unidade_medida'],
                    reading.get('observacao')
                )
                params_list.append(params)
            
            count = self.db.execute_many(query, params_list)
            self.logger.info(f"{count} leituras adicionadas em lote")
            return count
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar leituras em lote: {e}")
            raise
    
    def get_latest_reading(self, sensor_id: int) -> Optional[Reading]:
        """Obtém a leitura mais recente de um sensor"""
        try:
            query = """
                SELECT * FROM leituras 
                WHERE sensor_id = ? 
                ORDER BY data_hora DESC 
                LIMIT 1
            """
            
            results = self.db.execute_query(query, (sensor_id,))
            
            if results:
                row = results[0]
                return Reading(
                    leitura_id=row['leitura_id'],
                    sensor_id=row['sensor_id'],
                    data_hora=datetime.fromisoformat(row['data_hora']),
                    valor=row['valor'],
                    unidade_medida=row['unidade_medida'],
                    status_leitura=row['status_leitura'],
                    observacao=row.get('observacao')
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter última leitura do sensor {sensor_id}: {e}")
            raise
    
    def get_readings_statistics(self, sensor_id: int, days: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas das leituras de um sensor"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            readings = self.get_readings(
                sensor_id=sensor_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not readings:
                return {
                    'sensor_id': sensor_id,
                    'total_readings': 0,
                    'average': 0,
                    'maximum': 0,
                    'minimum': 0,
                    'period_days': days
                }
            
            values = [r.valor for r in readings]
            
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
            self.logger.error(f"Erro ao obter estatísticas do sensor {sensor_id}: {e}")
            raise

class AreaRepository:
    """Repositório para operações com áreas"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = get_database_logger()
    
    def get_all_areas(self) -> List[Area]:
        """Obtém todas as áreas"""
        try:
            query = "SELECT * FROM areas ORDER BY area_id"
            results = self.db.execute_query(query)
            
            areas = []
            for row in results:
                area = Area(
                    area_id=row['area_id'],
                    nome=row['nome'],
                    tamanho=row['tamanho'],
                    unidade_medida=row['unidade_medida'],
                    tipo_solo=row['tipo_solo'],
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude'),
                    data_cadastro=datetime.fromisoformat(row['data_cadastro']) if row.get('data_cadastro') else None
                )
                areas.append(area)
            
            return areas
            
        except Exception as e:
            self.logger.error(f"Erro ao obter áreas: {e}")
            raise
    
    def get_area(self, area_id: int) -> Optional[Area]:
        """Obtém uma área específica"""
        try:
            query = "SELECT * FROM areas WHERE area_id = ?"
            results = self.db.execute_query(query, (area_id,))
            
            if results:
                row = results[0]
                return Area(
                    area_id=row['area_id'],
                    nome=row['nome'],
                    tamanho=row['tamanho'],
                    unidade_medida=row['unidade_medida'],
                    tipo_solo=row['tipo_solo'],
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude'),
                    data_cadastro=datetime.fromisoformat(row['data_cadastro']) if row.get('data_cadastro') else None
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter área {area_id}: {e}")
            raise
    
    def add_area(self, nome: str, tamanho: float, unidade_medida: str, 
                 tipo_solo: str, latitude: Optional[float] = None,
                 longitude: Optional[float] = None) -> int:
        """Adiciona uma nova área"""
        try:
            data = {
                'nome': nome,
                'tamanho': tamanho,
                'unidade_medida': unidade_medida,
                'tipo_solo': tipo_solo,
                'latitude': latitude,
                'longitude': longitude
            }
            
            area_id = self.db.insert_data('areas', data)
            self.logger.info(f"Área {area_id} adicionada com sucesso")
            return area_id
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar área: {e}")
            raise
    
    def update_area(self, area_id: int, **kwargs) -> bool:
        """Atualiza uma área"""
        try:
            self.db.update_data('areas', kwargs, 'area_id = ?', (area_id,))
            
            self.logger.info(f"Área {area_id} atualizada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar área {area_id}: {e}")
            raise
    
    def delete_area(self, area_id: int) -> bool:
        """Remove uma área"""
        try:
            self.db.delete_data('areas', 'area_id = ?', (area_id,))
            
            self.logger.info(f"Área {area_id} removida com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao remover área {area_id}: {e}")
            raise 