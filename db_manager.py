"""
Módulo de gerenciamento de conexão com o banco de dados para o Sistema de Sensoriamento Agrícola
FarmTech Solutions
"""

import os
import mysql.connector
from mysql.connector import Error
import sqlite3
import pandas as pd
from datetime import datetime
import logging

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='farm_tech_db.log'
)
logger = logging.getLogger('db_manager')

class DatabaseManager:
    """Classe para gerenciar a conexão com o banco de dados."""

    def __init__(self, db_type='mysql', host=None, user=None, password=None, database=None, sqlite_file=None):
        """
        Inicializa o gerenciador de banco de dados.

        Args:
            db_type (str): Tipo de banco de dados ('mysql' ou 'sqlite')
            host (str): Endereço do servidor MySQL
            user (str): Usuário do MySQL
            password (str): Senha do MySQL
            database (str): Nome do banco de dados MySQL
            sqlite_file (str): Caminho para o arquivo SQLite
        """
        self.db_type = db_type
        self.connection = None

        if db_type == 'mysql':
            self.host = host or 'localhost'
            self.user = user or 'farmtech'
            self.password = password or 'farmtech123'
            self.database = database or 'farmtech_sensors'
        elif db_type == 'sqlite':
            self.sqlite_file = sqlite_file or 'farmtech_sensors.db'
        else:
            raise ValueError("Tipo de banco de dados não suportado. Use 'mysql' ou 'sqlite'.")

    def connect(self):
        """Estabelece conexão com o banco de dados."""
        try:
            if self.db_type == 'mysql':
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                if self.connection.is_connected():
                    logger.info('Conexão MySQL estabelecida com sucesso.')
            else:  # sqlite
                self.connection = sqlite3.connect(self.sqlite_file)
                logger.info('Conexão SQLite estabelecida com sucesso.')

            return True

        except Error as e:
            logger.error(f'Erro ao conectar ao banco de dados: {e}')
            return False

    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            if self.db_type == 'mysql' and self.connection.is_connected():
                self.connection.close()
                logger.info('Conexão MySQL fechada.')
            elif self.db_type == 'sqlite':
                self.connection.close()
                logger.info('Conexão SQLite fechada.')

    def execute_query(self, query, params=None, fetch=False):
        """
        Executa uma consulta SQL.

        Args:
            query (str): Consulta SQL a ser executada
            params (tuple, list, dict): Parâmetros para a consulta
            fetch (bool): Se True, retorna os resultados da consulta

        Returns:
            list: Resultados da consulta se fetch=True, None caso contrário
        """
        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows

        except Error as e:
            logger.error(f'Erro ao executar consulta: {e}')
            if self.db_type == 'mysql' and self.connection.is_connected():
                self.connection.rollback()
            return None

    def execute_many(self, query, params_list):
        """
        Executa uma consulta SQL múltiplas vezes com diferentes conjuntos de parâmetros.

        Args:
            query (str): Consulta SQL a ser executada
            params_list (list): Lista de conjuntos de parâmetros

        Returns:
            int: Número de linhas afetadas
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows

        except Error as e:
            logger.error(f'Erro ao executar consulta múltipla: {e}')
            if self.db_type == 'mysql' and self.connection.is_connected():
                self.connection.rollback()
            return None

    def query_to_dataframe(self, query, params=None):
        """
        Executa uma consulta SQL e retorna os resultados como um DataFrame pandas.

        Args:
            query (str): Consulta SQL a ser executada
            params (tuple, list, dict): Parâmetros para a consulta

        Returns:
            pandas.DataFrame: DataFrame com os resultados da consulta
        """
        try:
            if self.db_type == 'mysql':
                if params:
                    return pd.read_sql(query, self.connection, params=params)
                else:
                    return pd.read_sql(query, self.connection)
            else:  # sqlite
                if params:
                    return pd.read_sql_query(query, self.connection, params=params)
                else:
                    return pd.read_sql_query(query, self.connection)

        except Error as e:
            logger.error(f'Erro ao executar consulta para DataFrame: {e}')
            return None

    def initialize_database(self, sql_script_path):
        """
        Inicializa o banco de dados executando um script SQL.

        Args:
            sql_script_path (str): Caminho para o arquivo de script SQL

        Returns:
            bool: True se a inicialização foi bem-sucedida, False caso contrário
        """
        try:
            if not os.path.exists(sql_script_path):
                logger.error(f'Arquivo de script SQL não encontrado: {sql_script_path}')
                return False

            with open(sql_script_path, 'r') as f:
                sql_script = f.read()

            # Divide o script em comandos individuais
            # Isso é uma simplificação e pode não funcionar para todos os scripts SQL
            sql_commands = sql_script.split(';')

            for command in sql_commands:
                command = command.strip()
                if command:
                    self.execute_query(command)

            logger.info('Banco de dados inicializado com sucesso.')
            return True

        except Exception as e:
            logger.error(f'Erro ao inicializar banco de dados: {e}')
            return False
