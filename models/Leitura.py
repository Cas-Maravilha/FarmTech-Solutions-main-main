"""
Classe para representar a entidade LEITURA no sistema de sensoriamento agrícola
FarmTech Solutions
"""

from datetime import datetime
import pandas as pd
from models.Sensor import Sensor

class Leitura:
    """Classe que representa uma leitura de sensor."""

    def __init__(self, id=None, sensor_id=None, data_hora=None, valor=0.0,
                 unidade_medida="", status_leitura="Normal"):
        """
        Inicializa uma leitura de sensor.

        Args:
            id (int): Identificador único da leitura
            sensor_id (int): ID do sensor que gerou a leitura
            data_hora (datetime): Data e hora da leitura
            valor (float): Valor registrado pelo sensor
            unidade_medida (str): Unidade de medida do valor
            status_leitura (str): Status da leitura (Normal, Alerta, Crítico, Erro)
        """
        self.id = id
        self.sensor_id = sensor_id
        self.data_hora = data_hora or datetime.now()
        self.valor = float(valor) if valor is not None else 0.0
        self.unidade_medida = unidade_medida
        self.status_leitura = status_leitura

    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'valor': self.valor,
            'unidade_medida': self.unidade_medida,
            'status_leitura': self.status_leitura
        }

    @classmethod
    def from_dict(cls, data):
        """
        Cria um objeto Leitura a partir de um dicionário.

        Args:
            data (dict): Dicionário com os dados da leitura

        Returns:
            Leitura: Nova instância de Leitura com os dados fornecidos
        """
        if not data:
            return None

        data_hora = None
        if 'data_hora' in data and data['data_hora']:
            if isinstance(data['data_hora'], str):
                data_hora = datetime.fromisoformat(data['data_hora'].replace('Z', '+00:00'))
            elif isinstance(data['data_hora'], datetime):
                data_hora = data['data_hora']

        return cls(
            id=data.get('id') or data.get('leitura_id'),
            sensor_id=data.get('sensor_id'),
            data_hora=data_hora,
            valor=data.get('valor'),
            unidade_medida=data.get('unidade_medida', ''),
            status_leitura=data.get('status_leitura', 'Normal')
        )

    @classmethod
    def from_tuple(cls, data, columns=None):
        """
        Cria um objeto Leitura a partir de uma tupla de dados.

        Args:
            data (tuple): Tupla com os dados da leitura
            columns (list): Lista de nomes das colunas na mesma ordem da tupla

        Returns:
            Leitura: Nova instância de Leitura com os dados fornecidos
        """
        if not data:
            return None

        if not columns:
            # Assume ordem padrão das colunas
            columns = ['leitura_id', 'sensor_id', 'data_hora', 'valor', 'unidade_medida', 'status_leitura']

        data_dict = dict(zip(columns, data))
        return cls.from_dict(data_dict)

    @classmethod
    def from_dataframe(cls, df):
        """
        Cria uma lista de objetos Leitura a partir de um DataFrame pandas.

        Args:
            df (pandas.DataFrame): DataFrame com os dados das leituras

        Returns:
            list: Lista de instâncias de Leitura
        """
        if df is None or df.empty:
            return []

        leituras = []
        for _, row in df.iterrows():
            leitura = cls.from_dict(row.to_dict())
            if leitura:
                leituras.append(leitura)

        return leituras

    @staticmethod
    def classificar_leitura(tipo_sensor, valor):
        """
        Classifica o status de uma leitura com base no tipo de sensor e valor.

        Args:
            tipo_sensor (str): Tipo do sensor (S1, S2 ou S3)
            valor (float): Valor da leitura

        Returns:
            str: Status da leitura (Normal, Alerta, Crítico, Erro)
        """
        if valor is None:
            return 'Erro'

        if tipo_sensor == 'S1':  # Umidade
            if valor < 0 or valor > 100:
                return 'Erro'
            elif valor < 30:
                return 'Crítico'  # Muito seco
            elif valor < 50:
                return 'Alerta'   # Seco
            elif valor > 90:
                return 'Alerta'   # Muito úmido
            else:
                return 'Normal'

        elif tipo_sensor == 'S2':  # pH
            if valor < 0 or valor > 14:
                return 'Erro'
            elif valor < 5.0:
                return 'Crítico'  # Muito ácido
            elif valor < 5.5:
                return 'Alerta'   # Ácido
            elif valor > 8.0:
                return 'Crítico'  # Muito alcalino
            elif valor > 7.0:
                return 'Alerta'   # Alcalino
            else:
                return 'Normal'

        elif tipo_sensor == 'S3':  # Nutrientes (NPK)
            if valor < 0:
                return 'Erro'
            elif valor < 10:
                return 'Crítico'  # Deficiência severa
            elif valor < 20:
                return 'Alerta'   # Deficiência
            elif valor > 50:
                return 'Alerta'   # Excesso
            else:
                return 'Normal'

        return 'Normal'

    def obter_unidade_medida_automatica(self, db_manager=None):
        """
        Obtém a unidade de medida com base no tipo de sensor associado.

        Args:
            db_manager (DatabaseManager): Gerenciador de banco de dados para consultar o sensor

        Returns:
            str: Unidade de medida
        """
        # Se já tem unidade de medida, retorna
        if self.unidade_medida:
            return self.unidade_medida

        # Se não tem sensor_id, não é possível determinar
        if not self.sensor_id:
            return ''

        # Se tem db_manager, consulta o tipo de sensor no banco
        if db_manager and db_manager.connection:
            query = "SELECT tipo_sensor FROM SENSOR WHERE sensor_id = %s"
            result = db_manager.execute_query(query, (self.sensor_id,), fetch=True)

            if result and result[0]:
                tipo_sensor = result[0][0]
                self.unidade_medida = Sensor.get_unidade_medida(tipo_sensor)
                return self.unidade_medida

        return ''
