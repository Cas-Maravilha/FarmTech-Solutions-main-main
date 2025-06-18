#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Gerenciador de Banco de Dados
Sistema centralizado para gerenciamento de banco de dados
"""

import sqlite3
import mysql.connector
from mysql.connector import Error
import logging
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
import os
from pathlib import Path

from ..core.logger import get_database_logger

logger = get_database_logger()

class DatabaseManager:
    """Gerenciador centralizado de banco de dados"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_database_logger()
        self.connection = None
        self.db_type = config.get('type', 'sqlite')
        
        # Inicializar conexão
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializa conexão com banco de dados"""
        try:
            if self.db_type == 'sqlite':
                self._init_sqlite()
            elif self.db_type == 'mysql':
                self._init_mysql()
            else:
                raise ValueError(f"Tipo de banco não suportado: {self.db_type}")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar conexão com banco: {e}")
            raise
    
    def _init_sqlite(self):
        """Inicializa conexão SQLite"""
        try:
            db_path = self.config.get('url', 'data/farmtech.db')
            
            # Criar diretório se não existir
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            self.logger.info(f"Conexão SQLite estabelecida: {db_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar SQLite: {e}")
            raise
    
    def _init_mysql(self):
        """Inicializa conexão MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                database=self.config.get('database', 'farmtech'),
                user=self.config.get('user', 'root'),
                password=self.config.get('password', ''),
                autocommit=True
            )
            
            self.logger.info(f"Conexão MySQL estabelecida: {self.config.get('host')}:{self.config.get('port')}")
            
        except Error as e:
            self.logger.error(f"Erro ao conectar MySQL: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão"""
        try:
            if self.db_type == 'sqlite':
                yield self.connection
            else:
                # Para MySQL, criar nova conexão se necessário
                if not self.connection.is_connected():
                    self._init_mysql()
                yield self.connection
        except Exception as e:
            self.logger.error(f"Erro na conexão: {e}")
            raise
        finally:
            # Para SQLite, não fechar conexão (mantida aberta)
            # Para MySQL, fechar se necessário
            if self.db_type == 'mysql' and self.connection and self.connection.is_connected():
                pass  # Manter conexão aberta
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Executa query e retorna resultados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True) if self.db_type == 'mysql' else conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    
                    # Converter para lista de dicionários
                    if self.db_type == 'mysql':
                        return results
                    else:
                        return [dict(row) for row in results]
                else:
                    conn.commit()
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erro ao executar query: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Executa múltiplas queries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            self.logger.error(f"Erro ao executar múltiplas queries: {e}")
            raise
    
    def create_tables(self):
        """Cria tabelas do banco de dados"""
        try:
            tables_sql = self._get_create_tables_sql()
            
            for table_name, sql in tables_sql.items():
                try:
                    self.execute_query(sql)
                    self.logger.info(f"Tabela {table_name} criada com sucesso")
                except Exception as e:
                    self.logger.warning(f"Erro ao criar tabela {table_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    def _get_create_tables_sql(self) -> Dict[str, str]:
        """Retorna SQL para criação de tabelas"""
        if self.db_type == 'sqlite':
            return {
                'areas': '''
                    CREATE TABLE IF NOT EXISTS areas (
                        area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        tamanho REAL NOT NULL,
                        unidade_medida TEXT NOT NULL,
                        tipo_solo TEXT NOT NULL,
                        latitude REAL,
                        longitude REAL,
                        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'sensores': '''
                    CREATE TABLE IF NOT EXISTS sensores (
                        sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area_id INTEGER NOT NULL,
                        tipo_sensor TEXT NOT NULL,
                        modelo TEXT NOT NULL,
                        status TEXT DEFAULT 'ativo',
                        data_instalacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                        latitude REAL,
                        longitude REAL,
                        FOREIGN KEY (area_id) REFERENCES areas (area_id)
                    )
                ''',
                'leituras': '''
                    CREATE TABLE IF NOT EXISTS leituras (
                        leitura_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sensor_id INTEGER NOT NULL,
                        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                        valor REAL NOT NULL,
                        unidade_medida TEXT NOT NULL,
                        status_leitura TEXT DEFAULT 'valida',
                        observacao TEXT,
                        FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
                    )
                ''',
                'plantios': '''
                    CREATE TABLE IF NOT EXISTS plantios (
                        plantio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area_id INTEGER NOT NULL,
                        cultura_id INTEGER NOT NULL,
                        data_plantio DATE NOT NULL,
                        status TEXT DEFAULT 'ativo',
                        FOREIGN KEY (area_id) REFERENCES areas (area_id)
                    )
                ''',
                'recomendacoes': '''
                    CREATE TABLE IF NOT EXISTS recomendacoes (
                        recomendacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plantio_id INTEGER NOT NULL,
                        tipo_recurso TEXT NOT NULL,
                        quantidade REAL NOT NULL,
                        unidade_medida TEXT NOT NULL,
                        prioridade TEXT NOT NULL,
                        justificativa TEXT NOT NULL,
                        data_prevista_aplicacao DATE NOT NULL,
                        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'pendente',
                        FOREIGN KEY (plantio_id) REFERENCES plantios (plantio_id)
                    )
                '''
            }
        else:
            # MySQL
            return {
                'areas': '''
                    CREATE TABLE IF NOT EXISTS areas (
                        area_id INT AUTO_INCREMENT PRIMARY KEY,
                        nome VARCHAR(255) NOT NULL,
                        tamanho DECIMAL(10,2) NOT NULL,
                        unidade_medida VARCHAR(50) NOT NULL,
                        tipo_solo VARCHAR(100) NOT NULL,
                        latitude DECIMAL(10,8),
                        longitude DECIMAL(11,8),
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'sensores': '''
                    CREATE TABLE IF NOT EXISTS sensores (
                        sensor_id INT AUTO_INCREMENT PRIMARY KEY,
                        area_id INT NOT NULL,
                        tipo_sensor VARCHAR(100) NOT NULL,
                        modelo VARCHAR(100) NOT NULL,
                        status VARCHAR(50) DEFAULT 'ativo',
                        data_instalacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        latitude DECIMAL(10,8),
                        longitude DECIMAL(11,8),
                        FOREIGN KEY (area_id) REFERENCES areas (area_id)
                    )
                ''',
                'leituras': '''
                    CREATE TABLE IF NOT EXISTS leituras (
                        leitura_id INT AUTO_INCREMENT PRIMARY KEY,
                        sensor_id INT NOT NULL,
                        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        valor DECIMAL(10,4) NOT NULL,
                        unidade_medida VARCHAR(50) NOT NULL,
                        status_leitura VARCHAR(50) DEFAULT 'valida',
                        observacao TEXT,
                        FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
                    )
                ''',
                'plantios': '''
                    CREATE TABLE IF NOT EXISTS plantios (
                        plantio_id INT AUTO_INCREMENT PRIMARY KEY,
                        area_id INT NOT NULL,
                        cultura_id INT NOT NULL,
                        data_plantio DATE NOT NULL,
                        status VARCHAR(50) DEFAULT 'ativo',
                        FOREIGN KEY (area_id) REFERENCES areas (area_id)
                    )
                ''',
                'recomendacoes': '''
                    CREATE TABLE IF NOT EXISTS recomendacoes (
                        recomendacao_id INT AUTO_INCREMENT PRIMARY KEY,
                        plantio_id INT NOT NULL,
                        tipo_recurso VARCHAR(100) NOT NULL,
                        quantidade DECIMAL(10,4) NOT NULL,
                        unidade_medida VARCHAR(50) NOT NULL,
                        prioridade VARCHAR(50) NOT NULL,
                        justificativa TEXT NOT NULL,
                        data_prevista_aplicacao DATE NOT NULL,
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'pendente',
                        FOREIGN KEY (plantio_id) REFERENCES plantios (plantio_id)
                    )
                '''
            }
    
    def insert_data(self, table: str, data: Dict[str, Any]) -> int:
        """Insere dados em uma tabela"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' if self.db_type == 'sqlite' else '%s'] * len(data))
            
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            params = tuple(data.values())
            
            self.execute_query(query, params)
            
            # Obter ID do registro inserido
            if self.db_type == 'sqlite':
                return self.execute_query("SELECT last_insert_rowid() as id")[0]['id']
            else:
                return self.execute_query("SELECT LAST_INSERT_ID() as id")[0]['id']
                
        except Exception as e:
            self.logger.error(f"Erro ao inserir dados na tabela {table}: {e}")
            raise
    
    def update_data(self, table: str, data: Dict[str, Any], condition: str, params: tuple) -> int:
        """Atualiza dados em uma tabela"""
        try:
            set_clause = ', '.join([f"{k} = ?" if self.db_type == 'sqlite' else f"{k} = %s" for k in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            
            all_params = tuple(data.values()) + params
            self.execute_query(query, all_params)
            
            return 1  # Número de linhas afetadas
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados na tabela {table}: {e}")
            raise
    
    def delete_data(self, table: str, condition: str, params: tuple) -> int:
        """Remove dados de uma tabela"""
        try:
            query = f"DELETE FROM {table} WHERE {condition}"
            self.execute_query(query, params)
            
            return 1  # Número de linhas afetadas
            
        except Exception as e:
            self.logger.error(f"Erro ao remover dados da tabela {table}: {e}")
            raise
    
    def get_table_info(self, table: str) -> List[Dict[str, Any]]:
        """Obtém informações sobre uma tabela"""
        try:
            if self.db_type == 'sqlite':
                query = f"PRAGMA table_info({table})"
                return self.execute_query(query)
            else:
                query = f"DESCRIBE {table}"
                return self.execute_query(query)
                
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da tabela {table}: {e}")
            return []
    
    def backup_database(self, backup_path: str):
        """Faz backup do banco de dados"""
        try:
            if self.db_type == 'sqlite':
                import shutil
                shutil.copy2(self.config.get('url', 'data/farmtech.db'), backup_path)
                self.logger.info(f"Backup SQLite criado: {backup_path}")
            else:
                # Para MySQL, usar mysqldump
                import subprocess
                cmd = [
                    'mysqldump',
                    f'--host={self.config.get("host")}',
                    f'--port={self.config.get("port")}',
                    f'--user={self.config.get("user")}',
                    f'--password={self.config.get("password")}',
                    self.config.get('database'),
                    '>', backup_path
                ]
                subprocess.run(cmd, shell=True)
                self.logger.info(f"Backup MySQL criado: {backup_path}")
                
        except Exception as e:
            self.logger.error(f"Erro ao fazer backup: {e}")
            raise
    
    def close_connection(self):
        """Fecha conexão com banco de dados"""
        try:
            if self.connection:
                if self.db_type == 'mysql' and self.connection.is_connected():
                    self.connection.close()
                elif self.db_type == 'sqlite':
                    self.connection.close()
                    
                self.logger.info("Conexão com banco de dados fechada")
                
        except Exception as e:
            self.logger.error(f"Erro ao fechar conexão: {e}")
    
    def __del__(self):
        """Destrutor - fecha conexão automaticamente"""
        self.close_connection() 