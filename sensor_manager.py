"""
Módulo para gerenciamento de sensores e leituras
FarmTech Solutions - Sistema de Sensoriamento Agrícola
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import random
import json
import os

from db_manager import DatabaseManager
from models.Sensor import Sensor
from models.Leitura import Leitura
from models.Area import Area

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='farm_tech_sensors.log'
)
logger = logging.getLogger('sensor_manager')

class SensorManager:
    """Classe para gerenciar os sensores e suas leituras."""

    def __init__(self, db_manager=None):
        """
        Inicializa o gerenciador de sensores.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados
        """
        self.db_manager = db_manager

    def obter_todos_sensores(self):
        """
        Obtém todos os sensores cadastrados.

        Returns:
            list: Lista de objetos Sensor
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return []

        query = """
        SELECT sensor_id, tipo_sensor, numero_serie, data_instalacao,
               localizacao, status, ultima_manutencao, area_id
        FROM SENSOR
        ORDER BY sensor_id
        """

        result = self.db_manager.query_to_dataframe(query)
        if result is None:
            return []

        return Sensor.from_dataframe(result)

    def obter_sensor_por_id(self, sensor_id):
        """
        Obtém um sensor pelo seu ID.

        Args:
            sensor_id (int): ID do sensor

        Returns:
            Sensor: Objeto Sensor ou None se não encontrado
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return None

        query = """
        SELECT sensor_id, tipo_sensor, numero_serie, data_instalacao,
               localizacao, status, ultima_manutencao, area_id
        FROM SENSOR
        WHERE sensor_id = %s
        """

        result = self.db_manager.execute_query(query, (sensor_id,), fetch=True)
        if not result:
            return None

        columns = ['sensor_id', 'tipo_sensor', 'numero_serie', 'data_instalacao',
                  'localizacao', 'status', 'ultima_manutencao', 'area_id']

        return Sensor.from_tuple(result[0], columns)

    def obter_sensores_por_area(self, area_id):
        """
        Obtém todos os sensores de uma área específica.

        Args:
            area_id (int): ID da área

        Returns:
            list: Lista de objetos Sensor
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return []

        query = """
        SELECT sensor_id, tipo_sensor, numero_serie, data_instalacao,
               localizacao, status, ultima_manutencao, area_id
        FROM SENSOR
        WHERE area_id = %s
        ORDER BY sensor_id
        """

        result = self.db_manager.query_to_dataframe(query, (area_id,))
        if result is None:
            return []

        return Sensor.from_dataframe(result)

    def obter_sensores_por_tipo(self, tipo_sensor):
        """
        Obtém todos os sensores de um tipo específico.

        Args:
            tipo_sensor (str): Tipo de sensor (S1, S2 ou S3)

        Returns:
            list: Lista de objetos Sensor
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return []

        query = """
        SELECT sensor_id, tipo_sensor, numero_serie, data_instalacao,
               localizacao, status, ultima_manutencao, area_id
        FROM SENSOR
        WHERE tipo_sensor = %s
        ORDER BY sensor_id
        """

        result = self.db_manager.query_to_dataframe(query, (tipo_sensor,))
        if result is None:
            return []

        return Sensor.from_dataframe(result)

    def adicionar_sensor(self, sensor):
        """
        Adiciona um novo sensor ao banco de dados.

        Args:
            sensor (Sensor): Objeto Sensor a ser adicionado

        Returns:
            int: ID do sensor adicionado ou None se falhou
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return None

        query = """
        INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao,
                           localizacao, status, ultima_manutencao, area_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            sensor.tipo_sensor,
            sensor.numero_serie,
            sensor.data_instalacao,
            sensor.localizacao,
            sensor.status,
            sensor.ultima_manutencao,
            sensor.area_id
        )

        # Executa a inserção
        self.db_manager.execute_query(query, params)

        # Obtém o ID gerado
        id_query = "SELECT LAST_INSERT_ID()"
        result = self.db_manager.execute_query(id_query, fetch=True)

        if result and result[0]:
            return result[0][0]
        return None

    def atualizar_sensor(self, sensor):
        """
        Atualiza um sensor existente no banco de dados.

        Args:
            sensor (Sensor): Objeto Sensor com os dados atualizados

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return False

        query = """
        UPDATE SENSOR
        SET tipo_sensor = %s,
            numero_serie = %s,
            data_instalacao = %s,
            localizacao = %s,
            status = %s,
            ultima_manutencao = %s,
            area_id = %s
        WHERE sensor_id = %s
        """

        params = (
            sensor.tipo_sensor,
            sensor.numero_serie,
            sensor.data_instalacao,
            sensor.localizacao,
            sensor.status,
            sensor.ultima_manutencao,
            sensor.area_id,
            sensor.id
        )

        rows_affected = self.db_manager.execute_query(query, params)
        return rows_affected is not None and rows_affected > 0

    def excluir_sensor(self, sensor_id):
        """
        Exclui um sensor do banco de dados.

        Args:
            sensor_id (int): ID do sensor a ser excluído

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return False

        # Verifica se há leituras associadas
        check_query = "SELECT COUNT(*) FROM LEITURA WHERE sensor_id = %s"
        result = self.db_manager.execute_query(check_query, (sensor_id,), fetch=True)

        if result[0][0] > 0:
            # Primeiro exclui as leituras
            delete_leituras = "DELETE FROM LEITURA WHERE sensor_id = %s"
            self.db_manager.execute_query(delete_leituras, (sensor_id,))

        # Agora exclui o sensor
        query = "DELETE FROM SENSOR WHERE sensor_id = %s"
        rows_affected = self.db_manager.execute_query(query, (sensor_id,))

        return rows_affected is not None and rows_affected > 0

    def registrar_leitura(self, leitura):
        """
        Registra uma nova leitura de sensor no banco de dados.

        Args:
            leitura (Leitura): Objeto Leitura a ser registrado

        Returns:
            int: ID da leitura registrada ou None se falhou
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return None

        # Se não tiver unidade de medida, tenta obter automaticamente
        if not leitura.unidade_medida:
            leitura.obter_unidade_medida_automatica(self.db_manager)

        # Se não tiver status, classifica com base no valor
        if leitura.status_leitura == 'Normal':
            sensor = self.obter_sensor_por_id(leitura.sensor_id)
            if sensor:
                leitura.status_leitura = Leitura.classificar_leitura(
                    sensor.tipo_sensor, leitura.valor)

        query = """
        INSERT INTO LEITURA (sensor_id, data_hora, valor, unidade_medida, status_leitura)
        VALUES (%s, %s, %s, %s, %s)
        """

        params = (
            leitura.sensor_id,
            leitura.data_hora,
            leitura.valor,
            leitura.unidade_medida,
            leitura.status_leitura
        )

        # Executa a inserção
        self.db_manager.execute_query(query, params)

        # Obtém o ID gerado
        id_query = "SELECT LAST_INSERT_ID()"
        result = self.db_manager.execute_query(id_query, fetch=True)

        if result and result[0]:
            return result[0][0]
        return None

    def obter_leituras_por_sensor(self, sensor_id, data_inicio=None, data_fim=None, limit=100):
        """
        Obtém as leituras de um sensor específico em um intervalo de datas.

        Args:
            sensor_id (int): ID do sensor
            data_inicio (datetime): Data inicial do período
            data_fim (datetime): Data final do período
            limit (int): Número máximo de leituras a retornar

        Returns:
            list: Lista de objetos Leitura
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return []

        query = """
        SELECT leitura_id, sensor_id, data_hora, valor, unidade_medida, status_leitura
        FROM LEITURA
        WHERE sensor_id = %s
        """

        params = [sensor_id]

        if data_inicio:
            query += " AND data_hora >= %s"
            params.append(data_inicio)

        if data_fim:
            query += " AND data_hora <= %s"
            params.append(data_fim)

        query += " ORDER BY data_hora DESC LIMIT %s"
        params.append(limit)

        result = self.db_manager.query_to_dataframe(query, tuple(params))
        if result is None:
            return []

        return Leitura.from_dataframe(result)

    def obter_leituras_por_area(self, area_id, tipo_sensor=None, data_inicio=None, data_fim=None, limit=100):
        """
        Obtém as leituras de todos os sensores de uma área específica.

        Args:
            area_id (int): ID da área
            tipo_sensor (str): Filtro opcional por tipo de sensor
            data_inicio (datetime): Data inicial do período
            data_fim (datetime): Data final do período
            limit (int): Número máximo de leituras a retornar

        Returns:
            list: Lista de objetos Leitura
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return []

        query = """
        SELECT l.leitura_id, l.sensor_id, l.data_hora, l.valor, l.unidade_medida, l.status_leitura
        FROM LEITURA l
        JOIN SENSOR s ON l.sensor_id = s.sensor_id
        WHERE s.area_id = %s
        """

        params = [area_id]

        if tipo_sensor:
            query += " AND s.tipo_sensor = %s"
            params.append(tipo_sensor)

        if data_inicio:
            query += " AND l.data_hora >= %s"
            params.append(data_inicio)

        if data_fim:
            query += " AND l.data_hora <= %s"
            params.append(data_fim)

        query += " ORDER BY l.data_hora DESC LIMIT %s"
        params.append(limit)

        result = self.db_manager.query_to_dataframe(query, tuple(params))
        if result is None:
            return []

        return Leitura.from_dataframe(result)

    def gerar_leituras_simuladas(self, sensor_id=None, area_id=None, num_leituras=24,
                               intervalo_horas=1, data_base=None):
        """
        Gera leituras simuladas para os sensores especificados.

        Args:
            sensor_id (int): ID de um sensor específico (opcional)
            area_id (int): ID de uma área para gerar para todos seus sensores (opcional)
            num_leituras (int): Número de leituras a gerar por sensor
            intervalo_horas (int): Intervalo em horas entre leituras
            data_base (datetime): Data/hora base para as leituras (opcional, padrão é now())

        Returns:
            int: Número de leituras geradas
        """
        sensores = []

        if sensor_id:
            sensor = self.obter_sensor_por_id(sensor_id)
            if sensor:
                sensores = [sensor]
        elif area_id:
            sensores = self.obter_sensores_por_area(area_id)
        else:
            sensores = self.obter_todos_sensores()

        if not sensores:
            logger.warning("Nenhum sensor encontrado para gerar leituras simuladas")
            return 0

        data_base = data_base or datetime.now()
        total_leituras = 0

        for sensor in sensores:
            for i in range(num_leituras):
                # Calcula a data/hora da leitura
                data_hora = data_base - timedelta(hours=i * intervalo_horas)

                # Gera valor conforme o tipo de sensor
                if sensor.tipo_sensor == 'S1':  # Umidade
                    valor = round(random.uniform(40, 85), 1)  # Entre 40% e 85%
                    unidade = '%'
                elif sensor.tipo_sensor == 'S2':  # pH
                    valor = round(random.uniform(5.0, 7.5), 2)  # Entre 5.0 e 7.5
                    unidade = 'pH'
                elif sensor.tipo_sensor == 'S3':  # Nutrientes
                    valor = round(random.uniform(15, 40), 1)  # Entre 15 e 40 ppm
                    unidade = 'ppm'
                else:
                    continue

                # Cria a leitura
                leitura = Leitura(
                    sensor_id=sensor.id,
                    data_hora=data_hora,
                    valor=valor,
                    unidade_medida=unidade
                )

                # Registra a leitura
                if self.registrar_leitura(leitura):
                    total_leituras += 1

        logger.info(f"Geradas {total_leituras} leituras simuladas")
        return total_leituras

    def analisar_leituras_por_sensor(self, sensor_id, data_inicio=None, data_fim=None):
        """
        Realiza uma análise estatística das leituras de um sensor.

        Args:
            sensor_id (int): ID do sensor
            data_inicio (datetime): Data inicial do período
            data_fim (datetime): Data final do período

        Returns:
            dict: Dicionário com as estatísticas calculadas
        """
        leituras = self.obter_leituras_por_sensor(sensor_id, data_inicio, data_fim, limit=1000)

        if not leituras:
            return {
                'sensor_id': sensor_id,
                'quantidade': 0,
                'estatisticas': None
            }

        # Extrair valores e converter para DataFrame
        dados = {
            'valor': [l.valor for l in leituras],
            'data_hora': [l.data_hora for l in leituras],
            'status': [l.status_leitura for l in leituras]
        }

        df = pd.DataFrame(dados)

        # Estatísticas básicas
        estatisticas = {
            'media': df['valor'].mean(),
            'mediana': df['valor'].median(),
            'min': df['valor'].min(),
            'max': df['valor'].max(),
            'desvio_padrao': df['valor'].std(),
            'quantidade': len(df),
            'unidade_medida': leituras[0].unidade_medida if leituras else '',
            'alertas': df[df['status'] == 'Alerta'].shape[0],
            'criticos': df[df['status'] == 'Crítico'].shape[0],
            'erros': df[df['status'] == 'Erro'].shape[0]
        }

        return {
            'sensor_id': sensor_id,
            'quantidade': len(leituras),
            'estatisticas': estatisticas
        }

    def criar_grafico_leituras(self, sensor_id=None, area_id=None, tipo_sensor=None,
                             data_inicio=None, data_fim=None, salvar_arquivo=None):
        """
        Cria um gráfico com as leituras de sensores.

        Args:
            sensor_id (int): ID de um sensor específico (opcional)
            area_id (int): ID de uma área para incluir todos seus sensores (opcional)
            tipo_sensor (str): Filtro por tipo de sensor (opcional)
            data_inicio (datetime): Data inicial do período
            data_fim (datetime): Data final do período
            salvar_arquivo (str): Caminho para salvar o gráfico (opcional)

        Returns:
            matplotlib.figure.Figure: Figura do gráfico criado
        """
        # Obtém os dados
        leituras = []

        if sensor_id:
            sensor = self.obter_sensor_por_id(sensor_id)
            if sensor:
                leituras = self.obter_leituras_por_sensor(sensor_id, data_inicio, data_fim, limit=1000)
                titulo = f"Leituras do Sensor {sensor.numero_serie} ({sensor.tipo_sensor_descricao})"
        elif area_id:
            leituras = self.obter_leituras_por_area(area_id, tipo_sensor, data_inicio, data_fim, limit=1000)
            area = self.obter_area_por_id(area_id)
            area_nome = area.nome if area else f"Área {area_id}"
            titulo = f"Leituras da {area_nome}"
            if tipo_sensor:
                titulo += f" - Sensores {tipo_sensor}"
        else:
            logger.warning("Especifique sensor_id ou area_id para criar o gráfico")
            return None

        if not leituras:
            logger.warning("Nenhuma leitura encontrada para criar o gráfico")
            return None

        # Prepara dados para o gráfico
        dados = {}
        for leitura in leituras:
            sensor_key = f"Sensor {leitura.sensor_id}"
            if sensor_key not in dados:
                dados[sensor_key] = {
                    'datas': [],
                    'valores': [],
                    'status': []
                }

            dados[sensor_key]['datas'].append(leitura.data_hora)
            dados[sensor_key]['valores'].append(leitura.valor)
            dados[sensor_key]['status'].append(leitura.status_leitura)

        # Cria o gráfico
        plt.figure(figsize=(12, 6))

        for sensor_key, sensor_dados in dados.items():
            plt.plot(sensor_dados['datas'], sensor_dados['valores'],
                    marker='o', linestyle='-', label=sensor_key)

        plt.title(titulo)
        plt.xlabel('Data/Hora')
        plt.ylabel(f'Valor ({leituras[0].unidade_medida})')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        if salvar_arquivo:
            plt.savefig(salvar_arquivo)

        return plt.gcf()

    def obter_area_por_id(self, area_id):
        """
        Obtém uma área pelo seu ID.

        Args:
            area_id (int): ID da área

        Returns:
            Area: Objeto Area ou None se não encontrado
        """
        if not self.db_manager or not self.db_manager.connection:
            logger.error("Conexão com o banco de dados não estabelecida")
            return None

        query = """
        SELECT area_id, nome, tamanho, localizacao, tipo_solo, data_registro
        FROM AREA
        WHERE area_id = %s
        """

        result = self.db_manager.execute_query(query, (area_id,), fetch=True)
        if not result:
            return None

        columns = ['area_id', 'nome', 'tamanho', 'localizacao', 'tipo_solo', 'data_registro']

        return Area.from_tuple(result[0], columns)
