"""
Classe para representar a entidade AREA no sistema de sensoriamento agrícola
FarmTech Solutions
"""

from datetime import date
import pandas as pd

class Area:
    """Classe que representa uma área de plantio."""

    def __init__(self, id=None, nome="", tamanho=0.0, localizacao="", tipo_solo="", data_registro=None):
        """
        Inicializa uma área.

        Args:
            id (int): Identificador único da área
            nome (str): Nome da área
            tamanho (float): Tamanho em hectares
            localizacao (str): Localização/coordenadas da área
            tipo_solo (str): Tipo de solo da área
            data_registro (date): Data de registro da área no sistema
        """
        self.id = id
        self.nome = nome
        self.tamanho = float(tamanho) if tamanho else 0.0
        self.localizacao = localizacao
        self.tipo_solo = tipo_solo
        self.data_registro = data_registro or date.today()

    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'tamanho': self.tamanho,
            'localizacao': self.localizacao,
            'tipo_solo': self.tipo_solo,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None
        }

    @classmethod
    def from_dict(cls, data):
        """
        Cria um objeto Area a partir de um dicionário.

        Args:
            data (dict): Dicionário com os dados da área

        Returns:
            Area: Nova instância de Area com os dados fornecidos
        """
        if not data:
            return None

        data_registro = None
        if 'data_registro' in data and data['data_registro']:
            if isinstance(data['data_registro'], str):
                data_registro = date.fromisoformat(data['data_registro'])
            elif isinstance(data['data_registro'], date):
                data_registro = data['data_registro']

        return cls(
            id=data.get('id') or data.get('area_id'),
            nome=data.get('nome', ''),
            tamanho=data.get('tamanho', 0.0),
            localizacao=data.get('localizacao', ''),
            tipo_solo=data.get('tipo_solo', ''),
            data_registro=data_registro
        )

    @classmethod
    def from_tuple(cls, data, columns=None):
        """
        Cria um objeto Area a partir de uma tupla de dados.

        Args:
            data (tuple): Tupla com os dados da área
            columns (list): Lista de nomes das colunas na mesma ordem da tupla

        Returns:
            Area: Nova instância de Area com os dados fornecidos
        """
        if not data:
            return None

        if not columns:
            # Assume ordem padrão das colunas
            columns = ['area_id', 'nome', 'tamanho', 'localizacao', 'tipo_solo', 'data_registro']

        data_dict = dict(zip(columns, data))
        return cls.from_dict(data_dict)

    @classmethod
    def from_dataframe(cls, df):
        """
        Cria uma lista de objetos Area a partir de um DataFrame pandas.

        Args:
            df (pandas.DataFrame): DataFrame com os dados das áreas

        Returns:
            list: Lista de instâncias de Area
        """
        if df is None or df.empty:
            return []

        areas = []
        for _, row in df.iterrows():
            area = cls.from_dict(row.to_dict())
            if area:
                areas.append(area)

        return areas
