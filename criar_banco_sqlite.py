#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Criação do Banco SQLite
Script para criar o banco de dados SQLite com a sintaxe correta
"""

import sqlite3
import os
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('criar_banco_sqlite')

def criar_banco_sqlite():
    """Cria o banco de dados SQLite com a sintaxe correta"""
    
    # Caminho do banco
    db_path = 'data/farmtech.db'
    
    # Criar diretório se não existir
    os.makedirs('data', exist_ok=True)
    
    # Remover banco existente se houver
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Banco de dados anterior removido.")
    
    try:
        # Conectar ao banco (cria o arquivo se não existir)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL para criação das tabelas com sintaxe SQLite correta
        sql_commands = [
            # Tabela AREA
            """
            CREATE TABLE IF NOT EXISTS AREA (
                area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(50) NOT NULL,
                tamanho DOUBLE NOT NULL,
                localizacao VARCHAR(100),
                tipo_solo VARCHAR(50),
                data_registro DATE
            )
            """,
            
            # Tabela SENSOR
            """
            CREATE TABLE IF NOT EXISTS SENSOR (
                sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_sensor VARCHAR(2) NOT NULL,
                numero_serie VARCHAR(50) NOT NULL,
                data_instalacao DATE,
                localizacao VARCHAR(100),
                status VARCHAR(20),
                ultima_manutencao DATE,
                area_id INTEGER,
                FOREIGN KEY (area_id) REFERENCES AREA(area_id)
            )
            """,
            
            # Tabela LEITURA
            """
            CREATE TABLE IF NOT EXISTS LEITURA (
                leitura_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER NOT NULL,
                data_hora DATETIME NOT NULL,
                valor DOUBLE NOT NULL,
                unidade_medida VARCHAR(10),
                status_leitura VARCHAR(20),
                FOREIGN KEY (sensor_id) REFERENCES SENSOR(sensor_id)
            )
            """,
            
            # Tabela CULTURA
            """
            CREATE TABLE IF NOT EXISTS CULTURA (
                cultura_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(50) NOT NULL,
                variedade VARCHAR(50),
                ciclo_vida INTEGER,
                ph_ideal_min DOUBLE,
                ph_ideal_max DOUBLE,
                umidade_ideal_min DOUBLE,
                umidade_ideal_max DOUBLE,
                fosforo_ideal_min DOUBLE,
                fosforo_ideal_max DOUBLE,
                potassio_ideal_min DOUBLE,
                potassio_ideal_max DOUBLE
            )
            """,
            
            # Tabela PLANTIO
            """
            CREATE TABLE IF NOT EXISTS PLANTIO (
                plantio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cultura_id INTEGER NOT NULL,
                area_id INTEGER NOT NULL,
                data_inicio DATE NOT NULL,
                data_colheita_prevista DATE,
                data_colheita_real DATE,
                status_plantio VARCHAR(20),
                producao_estimada DOUBLE,
                producao_real DOUBLE,
                FOREIGN KEY (cultura_id) REFERENCES CULTURA(cultura_id),
                FOREIGN KEY (area_id) REFERENCES AREA(area_id)
            )
            """,
            
            # Tabela RECOMENDACAO
            """
            CREATE TABLE IF NOT EXISTS RECOMENDACAO (
                recomendacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plantio_id INTEGER NOT NULL,
                tipo_recomendacao VARCHAR(30) NOT NULL,
                quantidade_recomendada DOUBLE NOT NULL,
                unidade_medida VARCHAR(10),
                data_hora_geracao DATETIME NOT NULL,
                prazo_aplicacao DATETIME,
                prioridade VARCHAR(10),
                status_recomendacao VARCHAR(20),
                leitura_id INTEGER,
                FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id),
                FOREIGN KEY (leitura_id) REFERENCES LEITURA(leitura_id)
            )
            """,
            
            # Tabela APLICACAO
            """
            CREATE TABLE IF NOT EXISTS APLICACAO (
                aplicacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plantio_id INTEGER NOT NULL,
                tipo_aplicacao VARCHAR(30) NOT NULL,
                quantidade DOUBLE NOT NULL,
                unidade_medida VARCHAR(10),
                data_hora DATETIME NOT NULL,
                responsavel VARCHAR(50),
                recomendacao_id INTEGER,
                FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id),
                FOREIGN KEY (recomendacao_id) REFERENCES RECOMENDACAO(recomendacao_id)
            )
            """
        ]
        
        # Executar comandos SQL
        for i, sql in enumerate(sql_commands, 1):
            try:
                cursor.execute(sql)
                logger.info(f"Tabela {i} criada com sucesso")
            except sqlite3.Error as e:
                logger.error(f"Erro ao criar tabela {i}: {e}")
                raise
        
        # Inserir dados de exemplo
        dados_exemplo = [
            # Áreas
            "INSERT INTO AREA (nome, tamanho, localizacao, tipo_solo, data_registro) VALUES ('Setor Norte', 150.5, 'Quadrante N-12', 'Argiloso', '2023-01-15')",
            "INSERT INTO AREA (nome, tamanho, localizacao, tipo_solo, data_registro) VALUES ('Setor Sul', 200.0, 'Quadrante S-08', 'Arenoso', '2023-01-15')",
            "INSERT INTO AREA (nome, tamanho, localizacao, tipo_solo, data_registro) VALUES ('Setor Leste', 175.25, 'Quadrante L-05', 'Areno-argiloso', '2023-02-10')",
            
            # Culturas
            "INSERT INTO CULTURA (nome, variedade, ciclo_vida, ph_ideal_min, ph_ideal_max, umidade_ideal_min, umidade_ideal_max, fosforo_ideal_min, fosforo_ideal_max, potassio_ideal_min, potassio_ideal_max) VALUES ('Soja', 'Intacta RR2 PRO', 120, 5.5, 7.0, 60.0, 85.0, 15.0, 30.0, 20.0, 40.0)",
            "INSERT INTO CULTURA (nome, variedade, ciclo_vida, ph_ideal_min, ph_ideal_max, umidade_ideal_min, umidade_ideal_max, fosforo_ideal_min, fosforo_ideal_max, potassio_ideal_min, potassio_ideal_max) VALUES ('Milho', 'DKB 390', 150, 5.8, 7.5, 65.0, 90.0, 20.0, 35.0, 25.0, 45.0)",
            "INSERT INTO CULTURA (nome, variedade, ciclo_vida, ph_ideal_min, ph_ideal_max, umidade_ideal_min, umidade_ideal_max, fosforo_ideal_min, fosforo_ideal_max, potassio_ideal_min, potassio_ideal_max) VALUES ('Algodão', 'FM 985 GLTP', 180, 5.5, 8.0, 55.0, 80.0, 18.0, 32.0, 22.0, 42.0)",
            
            # Sensores
            "INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES ('S1', 'UM2023001', '2023-03-01', 'Ponto A1', 'Ativo', '2023-08-15', 1)",
            "INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES ('S1', 'UM2023002', '2023-03-01', 'Ponto B2', 'Ativo', '2023-08-15', 2)",
            "INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES ('S2', 'PH2023001', '2023-03-02', 'Ponto A2', 'Ativo', '2023-08-16', 1)",
            "INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES ('S2', 'PH2023002', '2023-03-02', 'Ponto B3', 'Ativo', '2023-08-16', 2)",
            "INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES ('S3', 'NK2023001', '2023-03-03', 'Ponto A3', 'Ativo', '2023-08-17', 1)",
            "INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES ('S3', 'NK2023002', '2023-03-03', 'Ponto B4', 'Ativo', '2023-08-17', 2)",
            
            # Plantios
            "INSERT INTO PLANTIO (cultura_id, area_id, data_inicio, data_colheita_prevista, status_plantio, producao_estimada) VALUES (1, 1, '2023-10-01', '2024-02-01', 'Em andamento', 540.5)",
            "INSERT INTO PLANTIO (cultura_id, area_id, data_inicio, data_colheita_prevista, status_plantio, producao_estimada) VALUES (2, 2, '2023-09-15', '2024-02-15', 'Em andamento', 1200.0)",
            "INSERT INTO PLANTIO (cultura_id, area_id, data_inicio, data_colheita_prevista, status_plantio, producao_estimada) VALUES (3, 3, '2023-09-01', '2024-03-01', 'Em andamento', 450.0)"
        ]
        
        # Inserir dados de exemplo
        for i, sql in enumerate(dados_exemplo, 1):
            try:
                cursor.execute(sql)
                logger.info(f"Dado de exemplo {i} inserido com sucesso")
            except sqlite3.Error as e:
                logger.error(f"Erro ao inserir dado {i}: {e}")
                # Não interromper se houver erro nos dados de exemplo
        
        # Commit das alterações
        conn.commit()
        conn.close()
        
        logger.info(f"Banco de dados SQLite criado com sucesso: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("Criando banco de dados SQLite...")
    if criar_banco_sqlite():
        print("✓ Banco de dados criado com sucesso!")
        print("✓ Tabelas criadas e dados de exemplo inseridos")
    else:
        print("✗ Erro ao criar banco de dados") 