#!/usr/bin/env python3
"""
Script de demonstração do Sistema de Sensoriamento Agrícola
FarmTech Solutions
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sqlite3
import logging
import argparse

# Configura o logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('demo_sensores')

# Importa os módulos do sistema
try:
    from db_manager import DatabaseManager
    from sensor_manager import SensorManager
    from models.Sensor import Sensor
    from models.Leitura import Leitura
    from models.Area import Area
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    logger.error("Verifique se você está executando o script do diretório correto.")
    sys.exit(1)

def criar_banco_sqlite():
    """Cria o banco de dados SQLite com o esquema do sistema."""
    try:
        # Verifica se o arquivo já existe e o remove se necessário
        if os.path.exists('farmtech_sensors.db'):
            os.remove('farmtech_sensors.db')
            logger.info("Banco de dados anterior removido.")

        # Cria o banco de dados
        conn = sqlite3.connect('farmtech_sensors.db')

        # Lê o script SQL
        with open('criar_banco_dados.sql', 'r') as f:
            sql_script = f.read()

        # Divide o script em comandos individuais
        sql_commands = sql_script.split(';')

        # Executa cada comando
        cursor = conn.cursor()
        for command in sql_commands:
            command = command.strip()
            if command:
                cursor.execute(command)

        conn.commit()
        conn.close()

        logger.info("Banco de dados SQLite criado com sucesso.")
        return True

    except Exception as e:
        logger.error(f"Erro ao criar banco de dados SQLite: {e}")
        return False

def cadastrar_dados_exemplo(sensor_manager):
    """Cadastra dados de exemplo para demonstração."""
    # Já temos dados de exemplo no script SQL, então vamos apenas gerar leituras
    logger.info("Gerando leituras simuladas para os sensores existentes...")

    # Gera leituras para todos os sensores nas últimas 48 horas, com intervalo de 1 hora
    total_leituras = sensor_manager.gerar_leituras_simuladas(
        num_leituras=48,
        intervalo_horas=1,
        data_base=datetime.now()
    )

    logger.info(f"Geradas {total_leituras} leituras simuladas para demonstração.")

def executar_analises(sensor_manager):
    """Executa análises e gera gráficos com os dados dos sensores."""

    # Obtém todos os sensores
    sensores = sensor_manager.obter_todos_sensores()
    if not sensores:
        logger.warning("Nenhum sensor encontrado para análise.")
        return

    # Define o período de análise (últimas 48 horas)
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(hours=48)

    logger.info(f"Analisando dados dos sensores no período de {data_inicio} a {data_fim}...")

    # Cria diretório para salvar os gráficos
    os.makedirs('graficos', exist_ok=True)

    # Analisa e gera gráficos para cada sensor
    for sensor in sensores:
        # Realiza análise estatística
        analise = sensor_manager.analisar_leituras_por_sensor(sensor.id, data_inicio, data_fim)

        if analise['quantidade'] == 0:
            logger.warning(f"Nenhuma leitura encontrada para o sensor {sensor.id}.")
            continue

        # Exibe estatísticas
        print(f"\n=== Análise do Sensor {sensor.id} ({sensor.numero_serie}) ===")
        print(f"Tipo: {sensor.tipo_sensor} - {sensor.tipo_sensor_descricao}")
        print(f"Total de leituras: {analise['quantidade']}")

        estat = analise['estatisticas']
        if estat:
            print(f"Média: {estat['media']:.2f} {estat['unidade_medida']}")
            print(f"Mediana: {estat['mediana']:.2f} {estat['unidade_medida']}")
            print(f"Mínimo: {estat['min']:.2f} {estat['unidade_medida']}")
            print(f"Máximo: {estat['max']:.2f} {estat['unidade_medida']}")
            print(f"Desvio padrão: {estat['desvio_padrao']:.2f} {estat['unidade_medida']}")
            print(f"Alertas: {estat['alertas']}")
            print(f"Críticos: {estat['criticos']}")
            print(f"Erros: {estat['erros']}")

        # Gera gráfico
        arquivo_grafico = f"graficos/sensor_{sensor.id}_{sensor.tipo_sensor}.png"
        figura = sensor_manager.criar_grafico_leituras(
            sensor_id=sensor.id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            salvar_arquivo=arquivo_grafico
        )

        if figura:
            logger.info(f"Gráfico gerado para o sensor {sensor.id}: {arquivo_grafico}")
            plt.close(figura)

    # Análise por área
    areas = [1, 2, 3]  # IDs das áreas cadastradas no script SQL

    for area_id in areas:
        # Gera gráfico para cada tipo de sensor na área
        for tipo_sensor in ['S1', 'S2', 'S3']:
            arquivo_grafico = f"graficos/area_{area_id}_tipo_{tipo_sensor}.png"
            figura = sensor_manager.criar_grafico_leituras(
                area_id=area_id,
                tipo_sensor=tipo_sensor,
                data_inicio=data_inicio,
                data_fim=data_fim,
                salvar_arquivo=arquivo_grafico
            )

            if figura:
                logger.info(f"Gráfico gerado para a área {area_id}, sensores {tipo_sensor}: {arquivo_grafico}")
                plt.close(figura)

def main():
    """Função principal da demonstração."""
    # Parse de argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Demonstração do Sistema de Sensoriamento Agrícola')
    parser.add_argument('--criar-banco', action='store_true', help='Cria o banco de dados SQLite')
    parser.add_argument('--dados-exemplo', action='store_true', help='Cadastra dados de exemplo')
    parser.add_argument('--analises', action='store_true', help='Executa análises e gera gráficos')
    parser.add_argument('--completo', action='store_true', help='Executa a demonstração completa')

    args = parser.parse_args()

    # Se nenhum argumento for especificado, exibe a ajuda
    if not (args.criar_banco or args.dados_exemplo or args.analises or args.completo):
        parser.print_help()
        return

    # Inicializa o banco de dados SQLite se solicitado
    if args.criar_banco or args.completo:
        criar_banco_sqlite()

    # Inicializa o gerenciador de banco de dados
    db_manager = DatabaseManager(db_type='sqlite', sqlite_file='farmtech_sensors.db')
    if not db_manager.connect():
        logger.error("Falha ao conectar ao banco de dados.")
        return

    # Inicializa o gerenciador de sensores
    sensor_manager = SensorManager(db_manager)

    # Cadastra dados de exemplo se solicitado
    if args.dados_exemplo or args.completo:
        cadastrar_dados_exemplo(sensor_manager)

    # Executa análises se solicitado
    if args.analises or args.completo:
        executar_analises(sensor_manager)

    # Fecha a conexão com o banco de dados
    db_manager.disconnect()

    print("\nDemonstração concluída com sucesso!")
    print("Verifique o diretório 'graficos' para ver os gráficos gerados.")

if __name__ == "__main__":
    main()
