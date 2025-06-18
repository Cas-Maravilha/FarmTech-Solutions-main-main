#!/usr/bin/env python3
"""
Script para integração do Sistema de Sensoriamento Agrícola com o Sistema FarmTech existente
FarmTech Solutions
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime, timedelta
import logging
import argparse

# Configura o logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integrar_sistemas')

# Importa os módulos do sistema de sensores
try:
    from db_manager import DatabaseManager
    from sensor_manager import SensorManager
    from models.Sensor import Sensor
    from models.Leitura import Leitura
    from models.Area import Area
except ImportError as e:
    logger.error(f"Erro ao importar módulos do Sistema de Sensores: {e}")
    logger.error("Verifique se você está executando o script do diretório correto.")
    sys.exit(1)

# Tentativa de importar os módulos do sistema FarmTech existente
try:
    sys.path.append('.')  # Adiciona o diretório atual ao path
    import farmtech
    import analise_dados
    import exportar_dados
    FARMTECH_DISPONIVEL = True
    logger.info("Módulos do sistema FarmTech carregados com sucesso.")
except ImportError as e:
    logger.warning(f"Módulos do sistema FarmTech não encontrados: {e}")
    logger.warning("A integração será limitada.")
    FARMTECH_DISPONIVEL = False

def extrair_dados_farmtech(arquivo_dados=None):
    """
    Extrai dados do sistema FarmTech existente.

    Args:
        arquivo_dados (str): Caminho para o arquivo de dados do sistema FarmTech

    Returns:
        dict: Dicionário com os dados extraídos
    """
    dados = {
        'areas': [],
        'culturas': [],
        'aplicacoes': []
    }

    if not FARMTECH_DISPONIVEL and not arquivo_dados:
        logger.warning("Sistema FarmTech não disponível e nenhum arquivo de dados fornecido.")
        return dados

    try:
        if FARMTECH_DISPONIVEL:
            # Usa funções do sistema FarmTech para obter dados
            logger.info("Extraindo dados do sistema FarmTech...")

            # Obtém dados de áreas
            areas_farmtech = farmtech.carregar_vetores('areas')
            for area in areas_farmtech:
                dados['areas'].append({
                    'nome': area.get('nome', ''),
                    'tamanho': area.get('area', 0.0),
                    'localizacao': area.get('localizacao', ''),
                    'tipo_solo': area.get('tipo_solo', '')
                })

            # Obtém dados de culturas
            culturas_farmtech = farmtech.carregar_vetores('culturas')
            for cultura in culturas_farmtech:
                dados['culturas'].append({
                    'nome': cultura.get('nome', ''),
                    'variedade': cultura.get('variedade', ''),
                    'ciclo_vida': cultura.get('ciclo', 0)
                })

            # Obtém dados de aplicações
            aplicacoes_farmtech = farmtech.carregar_vetores('aplicacoes')
            for aplicacao in aplicacoes_farmtech:
                dados['aplicacoes'].append({
                    'tipo_aplicacao': aplicacao.get('produto', ''),
                    'quantidade': aplicacao.get('dosagem_total', 0.0),
                    'data_hora': aplicacao.get('data', datetime.now()),
                    'area_nome': aplicacao.get('area_nome', '')
                })

        elif arquivo_dados:
            # Lê dados do arquivo fornecido
            logger.info(f"Extraindo dados do arquivo: {arquivo_dados}")

            # Determina o formato do arquivo
            formato = arquivo_dados.split('.')[-1].lower()

            if formato == 'csv':
                # Lê dados de CSV
                df = pd.read_csv(arquivo_dados)

                # Processa os dados conforme a estrutura
                if 'nome' in df.columns and 'area' in df.columns:
                    for _, row in df.iterrows():
                        dados['areas'].append({
                            'nome': row.get('nome', ''),
                            'tamanho': row.get('area', 0.0),
                            'localizacao': row.get('localizacao', ''),
                            'tipo_solo': row.get('tipo_solo', '')
                        })

            elif formato == 'json':
                # Lê dados de JSON
                with open(arquivo_dados, 'r') as f:
                    dados_json = json.load(f)

                # Processa os dados conforme a estrutura
                if isinstance(dados_json, dict):
                    dados = dados_json
                elif isinstance(dados_json, list):
                    # Tenta determinar o tipo de dados na lista
                    if dados_json and 'nome' in dados_json[0] and 'area' in dados_json[0]:
                        dados['areas'] = dados_json

            else:
                logger.warning(f"Formato de arquivo não suportado: {formato}")

        logger.info(f"Extraídos {len(dados['areas'])} áreas, {len(dados['culturas'])} culturas e {len(dados['aplicacoes'])} aplicações.")
        return dados

    except Exception as e:
        logger.error(f"Erro ao extrair dados do sistema FarmTech: {e}")
        return dados

def importar_dados_para_sistema_sensores(dados_farmtech, db_manager):
    """
    Importa dados do sistema FarmTech para o sistema de sensores.

    Args:
        dados_farmtech (dict): Dicionário com os dados do sistema FarmTech
        db_manager (DatabaseManager): Gerenciador de banco de dados do sistema de sensores

    Returns:
        bool: True se a importação foi bem-sucedida, False caso contrário
    """
    if not db_manager or not db_manager.connection:
        logger.error("Conexão com o banco de dados não estabelecida")
        return False

    try:
        # Importa áreas
        if dados_farmtech['areas']:
            logger.info(f"Importando {len(dados_farmtech['areas'])} áreas...")

            for area_data in dados_farmtech['areas']:
                # Verifica se a área já existe
                query = "SELECT COUNT(*) FROM AREA WHERE nome = %s"
                result = db_manager.execute_query(query, (area_data['nome'],), fetch=True)

                if result and result[0][0] == 0:
                    # Insere a área
                    query = """
                    INSERT INTO AREA (nome, tamanho, localizacao, tipo_solo, data_registro)
                    VALUES (%s, %s, %s, %s, %s)
                    """

                    params = (
                        area_data['nome'],
                        area_data['tamanho'],
                        area_data.get('localizacao', ''),
                        area_data.get('tipo_solo', ''),
                        datetime.now().date()
                    )

                    db_manager.execute_query(query, params)

        # Importa culturas
        if dados_farmtech['culturas']:
            logger.info(f"Importando {len(dados_farmtech['culturas'])} culturas...")

            for cultura_data in dados_farmtech['culturas']:
                # Verifica se a cultura já existe
                query = "SELECT COUNT(*) FROM CULTURA WHERE nome = %s AND variedade = %s"
                result = db_manager.execute_query(
                    query,
                    (cultura_data['nome'], cultura_data.get('variedade', '')),
                    fetch=True
                )

                if result and result[0][0] == 0:
                    # Insere a cultura
                    query = """
                    INSERT INTO CULTURA (nome, variedade, ciclo_vida)
                    VALUES (%s, %s, %s)
                    """

                    params = (
                        cultura_data['nome'],
                        cultura_data.get('variedade', ''),
                        cultura_data.get('ciclo_vida', 0)
                    )

                    db_manager.execute_query(query, params)

        # Importa aplicações (requer mapeamento de áreas e culturas)
        if dados_farmtech['aplicacoes']:
            logger.info(f"Importando {len(dados_farmtech['aplicacoes'])} aplicações...")

            for aplicacao_data in dados_farmtech['aplicacoes']:
                # Encontra o ID da área pelo nome
                area_nome = aplicacao_data.get('area_nome', '')
                if area_nome:
                    query = "SELECT area_id FROM AREA WHERE nome = %s"
                    result = db_manager.execute_query(query, (area_nome,), fetch=True)

                    if result and result[0]:
                        area_id = result[0][0]

                        # Verifica se há plantios ativos nesta área
                        query = """
                        SELECT plantio_id FROM PLANTIO
                        WHERE area_id = %s AND status_plantio = 'Em andamento'
                        LIMIT 1
                        """
                        result = db_manager.execute_query(query, (area_id,), fetch=True)

                        if result and result[0]:
                            plantio_id = result[0][0]

                            # Insere a aplicação
                            query = """
                            INSERT INTO APLICACAO (plantio_id, tipo_aplicacao, quantidade,
                                                  unidade_medida, data_hora, responsavel)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """

                            params = (
                                plantio_id,
                                aplicacao_data.get('tipo_aplicacao', ''),
                                aplicacao_data.get('quantidade', 0.0),
                                aplicacao_data.get('unidade_medida', ''),
                                aplicacao_data.get('data_hora', datetime.now()),
                                'Sistema FarmTech'
                            )

                            db_manager.execute_query(query, params)

        logger.info("Importação de dados concluída com sucesso.")
        return True

    except Exception as e:
        logger.error(f"Erro ao importar dados para o sistema de sensores: {e}")
        return False

def exportar_dados_para_sistema_farmtech(sensor_manager, arquivo_saida=None):
    """
    Exporta dados do sistema de sensores para o sistema FarmTech.

    Args:
        sensor_manager (SensorManager): Gerenciador de sensores
        arquivo_saida (str): Caminho para o arquivo de saída (opcional)

    Returns:
        bool: True se a exportação foi bem-sucedida, False caso contrário
    """
    try:
        # Obtém dados do sistema de sensores
        logger.info("Obtendo dados do sistema de sensores...")

        # Obtém todas as áreas
        areas = []
        query = """
        SELECT area_id, nome, tamanho, localizacao, tipo_solo, data_registro
        FROM AREA
        """
        areas_df = sensor_manager.db_manager.query_to_dataframe(query)

        if areas_df is not None and not areas_df.empty:
            for _, row in areas_df.iterrows():
                areas.append({
                    'id': row['area_id'],
                    'nome': row['nome'],
                    'area': row['tamanho'],
                    'localizacao': row['localizacao'],
                    'tipo_solo': row['tipo_solo'],
                    'data_registro': row['data_registro'].isoformat() if isinstance(row['data_registro'], datetime.date) else row['data_registro']
                })

        # Obtém todos os sensores
        sensores = []
        query = """
        SELECT sensor_id, tipo_sensor, numero_serie, data_instalacao,
               localizacao, status, ultima_manutencao, area_id
        FROM SENSOR
        """
        sensores_df = sensor_manager.db_manager.query_to_dataframe(query)

        if sensores_df is not None and not sensores_df.empty:
            for _, row in sensores_df.iterrows():
                sensores.append({
                    'id': row['sensor_id'],
                    'tipo': row['tipo_sensor'],
                    'numero_serie': row['numero_serie'],
                    'data_instalacao': row['data_instalacao'].isoformat() if isinstance(row['data_instalacao'], datetime.date) else row['data_instalacao'],
                    'localizacao': row['localizacao'],
                    'status': row['status'],
                    'area_id': row['area_id']
                })

        # Obtém leituras recentes (últimas 24 horas)
        leituras = []
        data_limite = datetime.now() - timedelta(hours=24)
        query = """
        SELECT l.leitura_id, l.sensor_id, l.data_hora, l.valor, l.unidade_medida,
               l.status_leitura, s.tipo_sensor, a.nome as area_nome
        FROM LEITURA l
        JOIN SENSOR s ON l.sensor_id = s.sensor_id
        JOIN AREA a ON s.area_id = a.area_id
        WHERE l.data_hora >= %s
        ORDER BY l.data_hora DESC
        """
        leituras_df = sensor_manager.db_manager.query_to_dataframe(query, (data_limite,))

        if leituras_df is not None and not leituras_df.empty:
            for _, row in leituras_df.iterrows():
                leituras.append({
                    'id': row['leitura_id'],
                    'sensor_id': row['sensor_id'],
                    'tipo_sensor': row['tipo_sensor'],
                    'data_hora': row['data_hora'].isoformat() if isinstance(row['data_hora'], datetime) else row['data_hora'],
                    'valor': row['valor'],
                    'unidade': row['unidade_medida'],
                    'status': row['status_leitura'],
                    'area_nome': row['area_nome']
                })

        # Prepara dados para exportação
        dados_exportacao = {
            'areas': areas,
            'sensores': sensores,
            'leituras': leituras,
            'data_exportacao': datetime.now().isoformat(),
            'origem': 'Sistema de Sensoriamento Agrícola'
        }

        # Exporta os dados
        if FARMTECH_DISPONIVEL:
            logger.info("Exportando dados para o sistema FarmTech...")
            # Usa o módulo de exportação do sistema FarmTech
            nome_arquivo = arquivo_saida or f"dados_sensores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            exportar_dados.exportar_json(dados_exportacao, nome_arquivo)
            logger.info(f"Dados exportados para: {nome_arquivo}")

            # Tenta importar os dados diretamente no sistema
            try:
                farmtech.importar_dados_externos(dados_exportacao)
                logger.info("Dados importados diretamente no sistema FarmTech.")
            except Exception as e:
                logger.warning(f"Não foi possível importar dados diretamente: {e}")
        else:
            # Exporta para arquivo JSON
            nome_arquivo = arquivo_saida or f"dados_sensores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(nome_arquivo, 'w') as f:
                json.dump(dados_exportacao, f, indent=4)
            logger.info(f"Dados exportados para arquivo: {nome_arquivo}")

        return True

    except Exception as e:
        logger.error(f"Erro ao exportar dados do sistema de sensores: {e}")
        return False

def executar_analise_cruzada(sensor_manager, arquivo_saida=None):
    """
    Executa análise cruzada entre dados do sistema FarmTech e dados de sensores.

    Args:
        sensor_manager (SensorManager): Gerenciador de sensores
        arquivo_saida (str): Caminho para o arquivo de saída (opcional)

    Returns:
        bool: True se a análise foi bem-sucedida, False caso contrário
    """
    if not FARMTECH_DISPONIVEL:
        logger.warning("Sistema FarmTech não disponível para análise cruzada.")
        return False

    try:
        logger.info("Executando análise cruzada...")

        # Obtém dados de aplicações do sistema FarmTech
        aplicacoes_farmtech = farmtech.carregar_vetores('aplicacoes')

        # Obtém leituras dos sensores
        # Agrupa por área e calcula médias
        query = """
        SELECT a.area_id, a.nome as area_nome, s.tipo_sensor,
               AVG(l.valor) as valor_medio, l.unidade_medida
        FROM LEITURA l
        JOIN SENSOR s ON l.sensor_id = s.sensor_id
        JOIN AREA a ON s.area_id = a.area_id
        WHERE l.data_hora >= %s
        GROUP BY a.area_id, s.tipo_sensor, l.unidade_medida
        """

        data_limite = datetime.now() - timedelta(days=30)
        leituras_df = sensor_manager.db_manager.query_to_dataframe(query, (data_limite,))

        if leituras_df is None or leituras_df.empty:
            logger.warning("Nenhuma leitura encontrada para análise cruzada.")
            return False

        # Prepara dados para análise
        dados_analise = {}

        # Organiza leituras por área
        for _, row in leituras_df.iterrows():
            area_nome = row['area_nome']
            tipo_sensor = row['tipo_sensor']
            valor_medio = row['valor_medio']

            if area_nome not in dados_analise:
                dados_analise[area_nome] = {}

            if tipo_sensor == 'S1':
                dados_analise[area_nome]['umidade_media'] = valor_medio
            elif tipo_sensor == 'S2':
                dados_analise[area_nome]['ph_medio'] = valor_medio
            elif tipo_sensor == 'S3':
                dados_analise[area_nome]['nutrientes_medio'] = valor_medio

        # Adiciona dados de aplicações
        for aplicacao in aplicacoes_farmtech:
            area_nome = aplicacao.get('area_nome', '')
            if area_nome in dados_analise:
                if 'aplicacoes' not in dados_analise[area_nome]:
                    dados_analise[area_nome]['aplicacoes'] = []

                dados_analise[area_nome]['aplicacoes'].append({
                    'produto': aplicacao.get('produto', ''),
                    'dosagem': aplicacao.get('dosagem_total', 0.0),
                    'data': aplicacao.get('data', '')
                })

        # Realiza análise
        resultados_analise = []

        for area_nome, dados in dados_analise.items():
            resultado = {
                'area': area_nome,
                'umidade': dados.get('umidade_media', 'N/A'),
                'ph': dados.get('ph_medio', 'N/A'),
                'nutrientes': dados.get('nutrientes_medio', 'N/A'),
                'aplicacoes_recentes': len(dados.get('aplicacoes', [])),
                'recomendacoes': []
            }

            # Gera recomendações simples com base nos dados
            if 'umidade_media' in dados and dados['umidade_media'] < 50:
                resultado['recomendacoes'].append(
                    f"Aumentar irrigação na área {area_nome} - Umidade média: {dados['umidade_media']:.1f}%"
                )

            if 'ph_medio' in dados:
                if dados['ph_medio'] < 5.5:
                    resultado['recomendacoes'].append(
                        f"Aplicar calcário na área {area_nome} - pH médio: {dados['ph_medio']:.1f}"
                    )
                elif dados['ph_medio'] > 7.5:
                    resultado['recomendacoes'].append(
                        f"Aplicar enxofre na área {area_nome} - pH médio: {dados['ph_medio']:.1f}"
                    )

            if 'nutrientes_medio' in dados and dados['nutrientes_medio'] < 20:
                resultado['recomendacoes'].append(
                    f"Aplicar NPK na área {area_nome} - Nível de nutrientes: {dados['nutrientes_medio']:.1f} ppm"
                )

            resultados_analise.append(resultado)

        # Gera saída
        if arquivo_saida:
            with open(arquivo_saida, 'w') as f:
                json.dump(resultados_analise, f, indent=4)
            logger.info(f"Análise cruzada exportada para: {arquivo_saida}")

        # Exibe resultados
        print("\n=== ANÁLISE CRUZADA DE DADOS ===")
        for resultado in resultados_analise:
            print(f"\nÁrea: {resultado['area']}")
            print(f"Umidade média: {resultado['umidade'] if resultado['umidade'] != 'N/A' else 'N/A'}")
            print(f"pH médio: {resultado['ph'] if resultado['ph'] != 'N/A' else 'N/A'}")
            print(f"Nutrientes médios: {resultado['nutrientes'] if resultado['nutrientes'] != 'N/A' else 'N/A'}")
            print(f"Aplicações recentes: {resultado['aplicacoes_recentes']}")

            if resultado['recomendacoes']:
                print("\nRecomendações:")
                for rec in resultado['recomendacoes']:
                    print(f"- {rec}")
            else:
                print("\nNenhuma recomendação necessária.")

        # Se disponível, usa o módulo de análise do FarmTech
        if FARMTECH_DISPONIVEL:
            try:
                analise_dados.analisar_correlacao_com_dados_externos(resultados_analise)
            except Exception as e:
                logger.warning(f"Erro ao executar análise de correlação: {e}")

        return True

    except Exception as e:
        logger.error(f"Erro ao executar análise cruzada: {e}")
        return False

def main():
    """Função principal do script de integração."""
    # Parse de argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Integração do Sistema de Sensores com o Sistema FarmTech')
    parser.add_argument('--importar', action='store_true', help='Importar dados do FarmTech para o sistema de sensores')
    parser.add_argument('--exportar', action='store_true', help='Exportar dados do sistema de sensores para o FarmTech')
    parser.add_argument('--analise-cruzada', action='store_true', help='Executar análise cruzada entre os sistemas')
    parser.add_argument('--arquivo-entrada', type=str, help='Arquivo de dados de entrada (para importação)')
    parser.add_argument('--arquivo-saida', type=str, help='Arquivo de saída (para exportação)')
    parser.add_argument('--db-type', type=str, default='sqlite', choices=['sqlite', 'mysql'], help='Tipo de banco de dados')
    parser.add_argument('--db-file', type=str, default='farmtech_sensors.db', help='Arquivo do banco SQLite')

    args = parser.parse_args()

    # Se nenhum argumento for especificado, exibe a ajuda
    if not (args.importar or args.exportar or args.analise_cruzada):
        parser.print_help()
        return

    # Inicializa o gerenciador de banco de dados
    db_manager = DatabaseManager(db_type=args.db_type, sqlite_file=args.db_file)
    if not db_manager.connect():
        logger.error("Falha ao conectar ao banco de dados.")
        return

    # Inicializa o gerenciador de sensores
    sensor_manager = SensorManager(db_manager)

    try:
        # Importar dados
        if args.importar:
            dados_farmtech = extrair_dados_farmtech(args.arquivo_entrada)
            importar_dados_para_sistema_sensores(dados_farmtech, db_manager)

        # Exportar dados
        if args.exportar:
            exportar_dados_para_sistema_farmtech(sensor_manager, args.arquivo_saida)

        # Análise cruzada
        if args.analise_cruzada:
            executar_analise_cruzada(sensor_manager, args.arquivo_saida)

    finally:
        # Fecha a conexão com o banco de dados
        db_manager.disconnect()

    print("\nProcesso de integração concluído.")

if __name__ == "__main__":
    main()
