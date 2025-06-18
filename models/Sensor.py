"""
Classe para representar a entidade SENSOR no sistema de sensoriamento agrícola
FarmTech Solutions
"""

from datetime import date
import pandas as pd

class Sensor:
    """Classe que representa um sensor de monitoramento agrícola."""

    TIPOS_SENSOR = {
        'S1': 'Umidade',
        'S2': 'pH',
        'S3': 'Nutrientes (NPK)'
    }

    def __init__(self, id=None, tipo_sensor="", numero_serie="", data_instalacao=None,
                 localizacao="", status="Inativo", ultima_manutencao=None, area_id=None):
        """
        Inicializa um sensor.

        Args:
            id (int): Identificador único do sensor
            tipo_sensor (str): Tipo do sensor (S1, S2 ou S3)
            numero_serie (str): Número de série do sensor
            data_instalacao (date): Data de instalação do sensor
            localizacao (str): Localização específica do sensor
            status (str): Status atual do sensor (Ativo, Inativo, Manutenção)
            ultima_manutencao (date): Data da última manutenção
            area_id (int): ID da área onde o sensor está instalado
        """
        self.id = id
        self.tipo_sensor = tipo_sensor
        self.numero_serie = numero_serie
        self.data_instalacao = data_instalacao or date.today()
        self.localizacao = localizacao
        self.status = status
        self.ultima_manutencao = ultima_manutencao
        self.area_id = area_id

    @property
    def tipo_sensor_descricao(self):
        """Retorna a descrição do tipo de sensor."""
        return self.TIPOS_SENSOR.get(self.tipo_sensor, 'Desconhecido')

    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'id': self.id,
            'tipo_sensor': self.tipo_sensor,
            'numero_serie': self.numero_serie,
            'data_instalacao': self.data_instalacao.isoformat() if self.data_instalacao else None,
            'localizacao': self.localizacao,
            'status': self.status,
            'ultima_manutencao': self.ultima_manutencao.isoformat() if self.ultima_manutencao else None,
            'area_id': self.area_id,
            'tipo_sensor_descricao': self.tipo_sensor_descricao
        }

    @classmethod
    def from_dict(cls, data):
        """
        Cria um objeto Sensor a partir de um dicionário.

        Args:
            data (dict): Dicionário com os dados do sensor

        Returns:
            Sensor: Nova instância de Sensor com os dados fornecidos
        """
        if not data:
            return None

        data_instalacao = None
        if 'data_instalacao' in data and data['data_instalacao']:
            if isinstance(data['data_instalacao'], str):
                data_instalacao = date.fromisoformat(data['data_instalacao'])
            elif isinstance(data['data_instalacao'], date):
                data_instalacao = data['data_instalacao']

        ultima_manutencao = None
        if 'ultima_manutencao' in data and data['ultima_manutencao']:
            if isinstance(data['ultima_manutencao'], str):
                ultima_manutencao = date.fromisoformat(data['ultima_manutencao'])
            elif isinstance(data['ultima_manutencao'], date):
                ultima_manutencao = data['ultima_manutencao']

        return cls(
            id=data.get('id') or data.get('sensor_id'),
            tipo_sensor=data.get('tipo_sensor', ''),
            numero_serie=data.get('numero_serie', ''),
            data_instalacao=data_instalacao,
            localizacao=data.get('localizacao', ''),
            status=data.get('status', 'Inativo'),
            ultima_manutencao=ultima_manutencao,
            area_id=data.get('area_id')
        )

    @classmethod
    def from_tuple(cls, data, columns=None):
        """
        Cria um objeto Sensor a partir de uma tupla de dados.

        Args:
            data (tuple): Tupla com os dados do sensor
            columns (list): Lista de nomes das colunas na mesma ordem da tupla

        Returns:
            Sensor: Nova instância de Sensor com os dados fornecidos
        """
        if not data:
            return None

        if not columns:
            # Assume ordem padrão das colunas
            columns = ['sensor_id', 'tipo_sensor', 'numero_serie', 'data_instalacao',
                       'localizacao', 'status', 'ultima_manutencao', 'area_id']

        data_dict = dict(zip(columns, data))
        return cls.from_dict(data_dict)

    @classmethod
    def from_dataframe(cls, df):
        """
        Cria uma lista de objetos Sensor a partir de um DataFrame pandas.

        Args:
            df (pandas.DataFrame): DataFrame com os dados dos sensores

        Returns:
            list: Lista de instâncias de Sensor
        """
        if df is None or df.empty:
            return []

        sensores = []
        for _, row in df.iterrows():
            sensor = cls.from_dict(row.to_dict())
            if sensor:
                sensores.append(sensor)

        return sensores

    @staticmethod
    def get_unidade_medida(tipo_sensor):
        """
        Retorna a unidade de medida para um tipo de sensor.

        Args:
            tipo_sensor (str): Tipo do sensor (S1, S2 ou S3)

        Returns:
            str: Unidade de medida
        """
        unidades = {
            'S1': '%',    # Porcentagem para umidade
            'S2': 'pH',   # Escala de pH
            'S3': 'ppm'   # Partes por milhão para nutrientes
        }
        return unidades.get(tipo_sensor, '')
