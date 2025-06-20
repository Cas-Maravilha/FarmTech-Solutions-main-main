#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Criação do Banco de Dados Aprimorado
Script para criar o banco de dados SQLite com modelo de negócio expandido
Versão: 2.0
"""

import sqlite3
import os
import logging
import json
from datetime import datetime, timedelta
import hashlib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('criar_banco_aprimorado')

class BancoDadosAprimorado:
    def __init__(self, db_path='data/farmtech_aprimorado.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def conectar(self):
        """Conecta ao banco de dados"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Remover banco existente se houver
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                logger.info("Banco de dados anterior removido.")
            
            # Conectar ao banco
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Habilitar foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Conectado ao banco: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return False
    
    def criar_tabelas(self):
        """Cria todas as tabelas do banco aprimorado"""
        try:
            # Ler script SQL
            with open('banco_dados_aprimorado.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Executar script
            self.cursor.executescript(sql_script)
            self.conn.commit()
            
            logger.info("Todas as tabelas criadas com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
    
    def inserir_dados_iniciais(self):
        """Insere dados iniciais para demonstração"""
        try:
            # 1. Inserir usuários
            self._inserir_usuarios()
            
            # 2. Inserir fazendas
            self._inserir_fazendas()
            
            # 3. Inserir coordenadas
            self._inserir_coordenadas()
            
            # 4. Inserir áreas
            self._inserir_areas()
            
            # 5. Inserir talhões
            self._inserir_talhoes()
            
            # 6. Inserir sensores
            self._inserir_sensores()
            
            # 7. Inserir culturas
            self._inserir_culturas()
            
            # 8. Inserir plantios
            self._inserir_plantios()
            
            # 9. Inserir leituras de exemplo
            self._inserir_leituras_exemplo()
            
            # 10. Inserir dados climáticos
            self._inserir_dados_clima()
            
            # 11. Inserir recomendações
            self._inserir_recomendacoes()
            
            # 12. Inserir aplicações
            self._inserir_aplicacoes()
            
            # 13. Inserir alertas
            self._inserir_alertas()
            
            self.conn.commit()
            logger.info("Dados iniciais inseridos com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inserir dados iniciais: {e}")
            return False
    
    def _inserir_usuarios(self):
        """Insere usuários de exemplo"""
        usuarios = [
            ('Administrador', 'admin@farmtech.com', self._hash_senha('admin123'), 'admin', 'Ativo'),
            ('João Silva', 'joao@farmtech.com', self._hash_senha('joao123'), 'gerente', 'Ativo'),
            ('Maria Santos', 'maria@farmtech.com', self._hash_senha('maria123'), 'operador', 'Ativo'),
            ('Pedro Costa', 'pedro@farmtech.com', self._hash_senha('pedro123'), 'viewer', 'Ativo'),
            ('Ana Oliveira', 'ana@farmtech.com', self._hash_senha('ana123'), 'operador', 'Ativo')
        ]
        
        for usuario in usuarios:
            self.cursor.execute("""
                INSERT INTO USUARIO (nome, email, senha_hash, tipo_usuario, status)
                VALUES (?, ?, ?, ?, ?)
            """, usuario)
        
        logger.info(f"Inseridos {len(usuarios)} usuários")
    
    def _inserir_fazendas(self):
        """Insere fazendas de exemplo"""
        fazendas = [
            ('Fazenda São João', '12.345.678/0001-90', 'João Silva', 'Rodovia BR-163, Km 45', 'Lucas do Rio Verde', 'MT', '78450-000', '(65) 99999-9999', 'contato@fazendasaojoao.com', 2500.0),
            ('Fazenda Boa Vista', '98.765.432/0001-10', 'Maria Santos', 'Estrada Municipal, Km 12', 'Sorriso', 'MT', '78890-000', '(66) 88888-8888', 'contato@fazendaboavista.com', 1800.0),
            ('Fazenda Progresso', '11.222.333/0001-44', 'Pedro Costa', 'Rodovia MT-010, Km 78', 'Nova Mutum', 'MT', '78450-000', '(65) 77777-7777', 'contato@fazendaprogresso.com', 3200.0)
        ]
        
        for fazenda in fazendas:
            self.cursor.execute("""
                INSERT INTO FAZENDA (nome, cnpj, proprietario, endereco, cidade, estado, cep, telefone, email, area_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, fazenda)
        
        logger.info(f"Inseridas {len(fazendas)} fazendas")
    
    def _inserir_coordenadas(self):
        """Insere coordenadas geográficas de exemplo"""
        coordenadas = [
            (-13.0582, -55.9042, 350.0),  # Lucas do Rio Verde
            (-12.5500, -55.7000, 380.0),  # Sorriso
            (-13.8333, -56.0833, 420.0),  # Nova Mutum
            (-13.0582, -55.9042, 355.0),  # Área 1
            (-13.0582, -55.9042, 360.0),  # Área 2
            (-12.5500, -55.7000, 385.0),  # Área 3
            (-12.5500, -55.7000, 390.0),  # Área 4
            (-13.8333, -56.0833, 425.0),  # Área 5
            (-13.8333, -56.0833, 430.0),  # Área 6
        ]
        
        for coord in coordenadas:
            self.cursor.execute("""
                INSERT INTO COORDENADA (latitude, longitude, altitude)
                VALUES (?, ?, ?)
            """, coord)
        
        logger.info(f"Inseridas {len(coordenadas)} coordenadas")
    
    def _inserir_areas(self):
        """Insere áreas de exemplo"""
        areas = [
            (1, 'Setor Norte', 'SN-001', 500.0, 'Argiloso', 6.2, 'Argiloso', 1.2, 4),
            (1, 'Setor Sul', 'SS-001', 600.0, 'Arenoso', 5.8, 'Arenoso', 0.8, 5),
            (2, 'Setor Leste', 'SL-001', 450.0, 'Areno-argiloso', 6.5, 'Areno-argiloso', 1.0, 6),
            (2, 'Setor Oeste', 'SO-001', 550.0, 'Argiloso', 6.0, 'Argiloso', 1.1, 7),
            (3, 'Setor Central', 'SC-001', 800.0, 'Arenoso', 5.5, 'Arenoso', 0.9, 8),
            (3, 'Setor Periférico', 'SP-001', 600.0, 'Areno-argiloso', 6.3, 'Areno-argiloso', 1.0, 9)
        ]
        
        for area in areas:
            self.cursor.execute("""
                INSERT INTO AREA (fazenda_id, nome, codigo, tamanho, tipo_solo, ph_solo, textura_solo, profundidade_solo, coordenada_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, area)
        
        logger.info(f"Inseridas {len(areas)} áreas")
    
    def _inserir_talhoes(self):
        """Insere talhões de exemplo"""
        talhoes = [
            (1, 'Talhão 1A', 'T1A', 100.0, 'retangular', 4),
            (1, 'Talhão 1B', 'T1B', 120.0, 'retangular', 4),
            (1, 'Talhão 1C', 'T1C', 80.0, 'irregular', 4),
            (2, 'Talhão 2A', 'T2A', 150.0, 'retangular', 5),
            (2, 'Talhão 2B', 'T2B', 100.0, 'retangular', 5),
            (3, 'Talhão 3A', 'T3A', 200.0, 'retangular', 6),
            (4, 'Talhão 4A', 'T4A', 180.0, 'retangular', 7),
            (5, 'Talhão 5A', 'T5A', 250.0, 'retangular', 8),
            (6, 'Talhão 6A', 'T6A', 200.0, 'retangular', 9)
        ]
        
        for talhao in talhoes:
            self.cursor.execute("""
                INSERT INTO TALHAO (area_id, nome, codigo, tamanho, formato, coordenada_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, talhao)
        
        logger.info(f"Inseridos {len(talhoes)} talhões")
    
    def _inserir_sensores(self):
        """Insere sensores de exemplo"""
        sensores = [
            (1, 1, 'SENSOR-UM-001', 'UM2023001', '1.2.3', datetime.now(), 4, 350.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 85, 95),
            (2, 2, 'SENSOR-TEMP-001', 'TEMP2023001', '1.2.3', datetime.now(), 4, 350.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 90, 98),
            (3, 3, 'SENSOR-PH-001', 'PH2023001', '1.2.3', datetime.now(), 4, 350.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 88, 92),
            (4, 4, 'SENSOR-CE-001', 'CE2023001', '1.2.3', datetime.now(), 5, 380.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 92, 96),
            (5, 5, 'SENSOR-N-001', 'N2023001', '1.2.3', datetime.now(), 5, 380.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 87, 94),
            (6, 6, 'SENSOR-P-001', 'P2023001', '1.2.3', datetime.now(), 6, 420.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 89, 97),
            (7, 7, 'SENSOR-K-001', 'K2023001', '1.2.3', datetime.now(), 6, 420.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 91, 93),
            (8, 8, 'SENSOR-RAD-001', 'RAD2023001', '1.2.3', datetime.now(), 7, 425.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 86, 99),
            (9, 9, 'SENSOR-VENTO-001', 'VENTO2023001', '1.2.3', datetime.now(), 8, 430.0, 'Norte', 'ativo', datetime.now(), datetime.now() + timedelta(days=30), 93, 95)
        ]
        
        for sensor in sensores:
            self.cursor.execute("""
                INSERT INTO SENSOR (tipo_sensor_id, talhao_id, codigo, numero_serie, versao_firmware, data_instalacao, coordenada_id, altitude, orientacao, status, ultima_manutencao, proxima_manutencao, bateria_nivel, sinal_forca)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sensor)
        
        logger.info(f"Inseridos {len(sensores)} sensores")
    
    def _inserir_culturas(self):
        """Insere culturas de exemplo"""
        culturas = [
            # nome, nome_cientifico, familia, variedade, ciclo_vida, estacao_plantio, profundidade_plantio, espacamento_linhas, espacamento_plantas, densidade_populacao, ph_ideal_min, ph_ideal_max, umidade_ideal_min, umidade_ideal_max, temperatura_ideal_min, temperatura_ideal_max, fosforo_ideal_min, fosforo_ideal_max, potassio_ideal_min, potassio_ideal_max, nitrogenio_ideal_min, nitrogenio_ideal_max, calcio_ideal_min, calcio_ideal_max, magnesio_ideal_min, magnesio_ideal_max, enxofre_ideal_min, enxofre_ideal_max, boro_ideal_min, boro_ideal_max, zinco_ideal_min, zinco_ideal_max, cobre_ideal_min, cobre_ideal_max, manganes_ideal_min, manganes_ideal_max, molibdenio_ideal_min, molibdenio_ideal_max, resistencia_doenca, resistencia_praga, observacoes
            ('Soja', 'Glycine max', 'Fabaceae', 'Intacta RR2 PRO', 120, 'primavera', 3.0, 0.45, 0.05, 250000, 5.5, 7.0, 60.0, 85.0, 20.0, 35.0, 15.0, 30.0, 20.0, 40.0, 20.0, 40.0, 2.0, 5.0, 1.0, 3.0, 0.5, 2.0, 0.1, 0.5, 0.05, 0.2, 0.01, 0.1, 0.01, 0.05, 0.01, 0.05, 'Resistente a ferrugem', 'Resistente a lagartas', 'Cultura principal da safra de verão'),
            ('Milho', 'Zea mays', 'Poaceae', 'DKB 390', 150, 'primavera', 4.0, 0.70, 0.20, 60000, 5.8, 7.5, 65.0, 90.0, 18.0, 32.0, 20.0, 35.0, 25.0, 45.0, 25.0, 45.0, 2.5, 6.0, 1.5, 4.0, 0.8, 2.5, 0.15, 0.6, 0.08, 0.3, 0.02, 0.15, 0.01, 0.05, 0.01, 0.05, 'Resistente a doenças foliares', 'Resistente a percevejos', 'Cultura de alta produtividade'),
            ('Algodão', 'Gossypium hirsutum', 'Malvaceae', 'FM 985 GLTP', 180, 'primavera', 2.5, 0.90, 0.15, 120000, 5.5, 8.0, 55.0, 80.0, 22.0, 38.0, 18.0, 32.0, 22.0, 42.0, 22.0, 42.0, 2.2, 5.5, 1.2, 3.5, 0.6, 2.2, 0.12, 0.5, 0.06, 0.25, 0.015, 0.12, 0.01, 0.05, 0.01, 0.05, 'Resistente a murcha', 'Resistente a bicudo', 'Cultura de fibra de alta qualidade'),
            ('Feijão', 'Phaseolus vulgaris', 'Fabaceae', 'BRS Estilo', 90, 'primavera', 3.5, 0.50, 0.10, 200000, 5.5, 7.0, 70.0, 85.0, 18.0, 30.0, 15.0, 25.0, 20.0, 35.0, 20.0, 35.0, 2.0, 4.5, 1.0, 2.8, 0.5, 1.8, 0.08, 0.4, 0.04, 0.2, 0.01, 0.08, 0.01, 0.05, 0.01, 0.05, 'Resistente a antracnose', 'Resistente a vaquinha', 'Cultura de ciclo curto'),
            ('Arroz', 'Oryza sativa', 'Poaceae', 'BRS Catiana', 130, 'primavera', 2.0, 0.20, 0.15, 150000, 5.0, 6.5, 80.0, 95.0, 20.0, 35.0, 12.0, 25.0, 18.0, 32.0, 18.0, 32.0, 1.8, 4.0, 0.8, 2.5, 0.4, 1.5, 0.06, 0.3, 0.03, 0.15, 0.008, 0.06, 0.01, 0.05, 0.01, 0.05, 'Resistente a brusone', 'Resistente a percevejos', 'Cultura de alta demanda hídrica')
        ]
        
        for cultura in culturas:
            self.cursor.execute("""
                INSERT INTO CULTURA (
                    nome, nome_cientifico, familia, variedade, ciclo_vida, estacao_plantio, profundidade_plantio, espacamento_linhas, espacamento_plantas, densidade_populacao, ph_ideal_min, ph_ideal_max, umidade_ideal_min, umidade_ideal_max, temperatura_ideal_min, temperatura_ideal_max, fosforo_ideal_min, fosforo_ideal_max, potassio_ideal_min, potassio_ideal_max, nitrogenio_ideal_min, nitrogenio_ideal_max, calcio_ideal_min, calcio_ideal_max, magnesio_ideal_min, magnesio_ideal_max, enxofre_ideal_min, enxofre_ideal_max, boro_ideal_min, boro_ideal_max, zinco_ideal_min, zinco_ideal_max, cobre_ideal_min, cobre_ideal_max, manganes_ideal_min, manganes_ideal_max, molibdenio_ideal_min, molibdenio_ideal_max, resistencia_doenca, resistencia_praga, observacoes
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, cultura)
        
        logger.info(f"Inseridas {len(culturas)} culturas")
    
    def _inserir_plantios(self):
        """Insere plantios de exemplo"""
        plantios = [
            # talhao_id, cultura_id, codigo_plantio, data_inicio, data_colheita_prevista, data_colheita_real, status_plantio, fase_crescimento, densidade_plantio, area_plantada, producao_estimada, producao_real, produtividade_estimada, produtividade_real, custo_estimado, custo_real, lucro_estimado, lucro_real, observacoes, usuario_responsavel
            (1, 1, 'PLANTIO-2024-001', datetime(2024, 10, 1), datetime(2025, 2, 1), None, 'em_andamento', 'vegetativo', 250000, 100.0, 25.0, None, 2.5, None, 5000.0, None, 15000.0, None, 'Plantio de soja no talhão 1A', 2),
            (2, 2, 'PLANTIO-2024-002', datetime(2024, 9, 15), datetime(2025, 2, 15), None, 'em_andamento', 'vegetativo', 60000, 150.0, 30.0, None, 3.0, None, 8000.0, None, 20000.0, None, 'Plantio de milho no talhão 2A', 2),
            (3, 3, 'PLANTIO-2024-003', datetime(2024, 9, 1), datetime(2025, 3, 1), None, 'em_andamento', 'vegetativo', 120000, 80.0, 18.0, None, 1.8, None, 3000.0, None, 12000.0, None, 'Plantio de algodão no talhão 3A', 2),
            (4, 4, 'PLANTIO-2024-004', datetime(2024, 10, 15), datetime(2025, 1, 15), None, 'em_andamento', 'vegetativo', 200000, 180.0, 20.0, None, 2.0, None, 4000.0, None, 16000.0, None, 'Plantio de feijão no talhão 4A', 2),
            (5, 5, 'PLANTIO-2024-005', datetime(2024, 9, 30), datetime(2025, 2, 15), None, 'em_andamento', 'vegetativo', 150000, 250.0, 25.0, None, 2.5, None, 6000.0, None, 18000.0, None, 'Plantio de arroz no talhão 5A', 2)
        ]
        
        for plantio in plantios:
            self.cursor.execute("""
                INSERT INTO PLANTIO (talhao_id, cultura_id, codigo_plantio, data_inicio, data_colheita_prevista, data_colheita_real, status_plantio, fase_crescimento, densidade_plantio, area_plantada, producao_estimada, producao_real, produtividade_estimada, produtividade_real, custo_estimado, custo_real, lucro_estimado, lucro_real, observacoes, usuario_responsavel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, plantio)
        
        logger.info(f"Inseridos {len(plantios)} plantios")
    
    def _inserir_leituras_exemplo(self):
        """Insere leituras de exemplo dos últimos 30 dias"""
        import random
        from datetime import datetime, timedelta
        
        # Gerar leituras para os últimos 30 dias
        data_inicio = datetime.now() - timedelta(days=30)
        
        for sensor_id in range(1, 10):  # 9 sensores
            for dia in range(30):
                data_hora = data_inicio + timedelta(days=dia, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                
                # Valores baseados no tipo de sensor
                if sensor_id in [1, 4]:  # Umidade do solo
                    valor = random.uniform(25.0, 85.0)
                    unidade = '%'
                elif sensor_id in [2]:  # Temperatura
                    valor = random.uniform(15.0, 35.0)
                    unidade = '°C'
                elif sensor_id in [3]:  # pH
                    valor = random.uniform(5.0, 7.5)
                    unidade = 'pH'
                elif sensor_id in [5, 6, 7]:  # Nutrientes
                    valor = random.uniform(10.0, 50.0)
                    unidade = 'mg/kg'
                elif sensor_id in [8]:  # Radiação solar
                    valor = random.uniform(0.0, 1200.0)
                    unidade = 'W/m²'
                elif sensor_id in [9]:  # Velocidade do vento
                    valor = random.uniform(0.0, 15.0)
                    unidade = 'm/s'
                else:
                    valor = random.uniform(0.0, 100.0)
                    unidade = 'unidade'
                
                self.cursor.execute("""
                    INSERT INTO LEITURA (sensor_id, data_hora, valor, unidade_medida, qualidade_dado, temperatura_ambiente, umidade_ambiente)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sensor_id, data_hora, valor, unidade, 'excelente', 
                      random.uniform(20.0, 30.0), random.uniform(40.0, 80.0)))
        
        logger.info("Leituras de exemplo inseridas")
    
    def _inserir_dados_clima(self):
        """Insere dados climáticos de exemplo"""
        import random
        from datetime import datetime, timedelta
        
        data_inicio = datetime.now() - timedelta(days=30)
        
        for talhao_id in range(1, 10):
            for dia in range(30):
                data_hora = data_inicio + timedelta(days=dia, hours=random.randint(0, 23))
                
                self.cursor.execute("""
                    INSERT INTO DADOS_CLIMA (talhao_id, data_hora, temperatura, umidade_relativa, pressao_atmosferica, velocidade_vento, direcao_vento, radiacao_solar, precipitacao, fonte_dados)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (talhao_id, data_hora,
                      random.uniform(18.0, 32.0),
                      random.uniform(45.0, 85.0),
                      random.uniform(1000.0, 1020.0),
                      random.uniform(0.0, 12.0),
                      random.uniform(0.0, 360.0),
                      random.uniform(0.0, 1000.0),
                      random.uniform(0.0, 50.0),
                      'estacao_local'))
        
        logger.info("Dados climáticos inseridos")
    
    def _inserir_recomendacoes(self):
        """Insere recomendações de exemplo"""
        recomendacoes = [
            # plantio_id, tipo_id, talhao_id, titulo, descricao, tipo_recomendacao, quantidade_recomendada, unidade_medida, data_geracao, prazo_aplicacao, prioridade, status, custo_estimado, beneficio_estimado, roi_estimado, leitura_id, usuario_gerador, usuario_aprovador, data_aprovacao, observacoes
            (1, 1, 1, 'Aplicação de Nitrogênio', 'Recomenda-se aplicação de 50 kg/ha de N devido aos baixos teores no solo', 'Fertilização Nitrogenada', 50.0, 'kg/ha', datetime.now(), datetime.now() + timedelta(days=7), 'alta', 'pendente', 500.0, 1500.0, 200.0, 1, 2, None, None, 'Recomendação baseada em análise de solo'),
            (2, 2, 2, 'Irrigação Suplementar', 'Recomenda-se irrigação de 20mm devido ao déficit hídrico', 'Irrigação Suplementar', 20.0, 'mm', datetime.now(), datetime.now() + timedelta(days=2), 'urgente', 'aprovada', 200.0, 800.0, 300.0, 1, 2, 2, datetime.now(), 'Aprovada pelo gerente'),
            (3, 3, 3, 'Correção de pH', 'Recomenda-se aplicação de calcário para elevar o pH do solo', 'Correção de pH', 2.0, 't/ha', datetime.now(), datetime.now() + timedelta(days=14), 'normal', 'pendente', 800.0, 2000.0, 150.0, 1, 2, None, None, 'Aguardando aprovação'),
            (4, 4, 4, 'Controle de Pragas', 'Recomenda-se aplicação de inseticida para controle de lagartas', 'Controle de Pragas', 1.5, 'L/ha', datetime.now(), datetime.now() + timedelta(days=3), 'alta', 'aprovada', 300.0, 1200.0, 300.0, 1, 2, 2, datetime.now(), 'Aplicação urgente'),
            (5, 5, 5, 'Adubação Fosfatada', 'Recomenda-se aplicação de 80 kg/ha de P2O5', 'Fertilização Fosfatada', 80.0, 'kg/ha', datetime.now(), datetime.now() + timedelta(days=10), 'normal', 'pendente', 600.0, 1800.0, 200.0, 1, 2, None, None, 'Baseada em análise foliar')
        ]
        
        for rec in recomendacoes:
            self.cursor.execute("""
                INSERT INTO RECOMENDACAO (plantio_id, tipo_id, talhao_id, titulo, descricao, tipo_recomendacao, quantidade_recomendada, unidade_medida, data_geracao, prazo_aplicacao, prioridade, status, custo_estimado, beneficio_estimado, roi_estimado, leitura_id, usuario_gerador, usuario_aprovador, data_aprovacao, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rec)
        
        logger.info(f"Inseridas {len(recomendacoes)} recomendações")
    
    def _inserir_aplicacoes(self):
        """Insere aplicações de exemplo"""
        aplicacoes = [
            # plantio_id, recomendacao_id, talhao_id, tipo_aplicacao, produto, quantidade, unidade_medida, data_hora, condicoes_climaticas, equipamento_utilizado, responsavel, status, custo_real, observacoes, coordenada_id
            (2, 2, 2, 'Irrigação', 'Água', 20.0, 'mm', datetime.now() - timedelta(days=1), 'Condições adequadas', 'Aspersor móvel', 2, 'concluida', 500.0, 'Aplicação realizada com sucesso', 2),
            (4, 4, 4, 'Aplicação de Inseticida', 'Deltametrina', 1.5, 'L/ha', datetime.now() - timedelta(days=2), 'Vento calmo, umidade alta', 'Pulverizador costal', 2, 'concluida', 800.0, 'Controle efetivo de pragas', 2),
            (1, 1, 1, 'Aplicação de Nitrogênio', 'Ureia', 50.0, 'kg/ha', datetime.now() - timedelta(days=5), 'Solo úmido', 'Adubadeira', 2, 'concluida', 1200.0, 'Adubação nitrogenada aplicada', 2)
        ]
        
        for apl in aplicacoes:
            self.cursor.execute("""
                INSERT INTO APLICACAO (plantio_id, recomendacao_id, talhao_id, tipo_aplicacao, produto, quantidade, unidade_medida, data_hora, condicoes_climaticas, equipamento_utilizado, responsavel, status, custo_real, observacoes, coordenada_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, apl)
        
        logger.info(f"Inseridas {len(aplicacoes)} aplicações")
    
    def _inserir_alertas(self):
        """Insere alertas de exemplo"""
        alertas = [
            # sensor_id, talhao_id, tipo_alerta, severidade, titulo, descricao, valor_atual, valor_limite, data_geracao, data_resolucao, status, usuario_responsavel, acao_tomada
            (1, 1, 'umidade_solo', 'alta', 'Umidade do Solo Baixa', 'Umidade do solo abaixo do ideal', 25.0, 30.0, datetime.now() - timedelta(hours=2), None, 'ativo', 2, None),
            (2, 2, 'temperatura', 'media', 'Temperatura Elevada', 'Temperatura acima do ideal para a cultura', 35.5, 35.0, datetime.now() - timedelta(hours=1), None, 'ativo', 2, None),
            (3, 3, 'ph_solo', 'alta', 'pH do Solo Baixo', 'pH do solo abaixo do ideal para a cultura', 4.8, 5.5, datetime.now() - timedelta(hours=3), None, 'ativo', 2, None)
        ]
        
        for alerta in alertas:
            self.cursor.execute("""
                INSERT INTO ALERTA (sensor_id, talhao_id, tipo_alerta, severidade, titulo, descricao, valor_atual, valor_limite, data_geracao, data_resolucao, status, usuario_responsavel, acao_tomada)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, alerta)
        
        logger.info(f"Inseridos {len(alertas)} alertas")
    
    def _hash_senha(self, senha):
        """Gera hash da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_estrutura(self):
        """Verifica se todas as tabelas foram criadas corretamente"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = [row[0] for row in self.cursor.fetchall()]
            
            tabelas_esperadas = [
                'CONFIGURACAO_SISTEMA', 'USUARIO', 'FAZENDA', 'COORDENADA', 'AREA', 'TALHAO',
                'TIPO_SENSOR', 'SENSOR', 'LEITURA', 'ALERTA', 'CULTURA', 'PLANTIO',
                'ESTAGIO_DESENVOLVIMENTO', 'SISTEMA_IRRIGACAO', 'PROGRAMACAO_IRRIGACAO',
                'EXECUCAO_IRRIGACAO', 'TIPO_RECOMENDACAO', 'RECOMENDACAO', 'APLICACAO',
                'DADOS_CLIMA', 'PREVISAO_CLIMA', 'RELATORIO', 'METRICA', 'VALOR_METRICA',
                'LOG_AUDITORIA', 'LOG_SISTEMA'
            ]
            
            tabelas_faltando = set(tabelas_esperadas) - set(tabelas)
            if tabelas_faltando:
                logger.warning(f"Tabelas faltando: {tabelas_faltando}")
                return False
            
            logger.info(f"Todas as {len(tabelas)} tabelas criadas corretamente!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar estrutura: {e}")
            return False
    
    def gerar_relatorio_criacao(self):
        """Gera relatório da criação do banco"""
        try:
            # Contar registros em cada tabela
            tabelas_principais = ['USUARIO', 'FAZENDA', 'AREA', 'TALHAO', 'SENSOR', 'CULTURA', 'PLANTIO', 'LEITURA', 'RECOMENDACAO', 'APLICACAO', 'ALERTA']
            
            relatorio = {
                'data_criacao': datetime.now().isoformat(),
                'banco': self.db_path,
                'tabelas_criadas': len(tabelas_principais),
                'registros_por_tabela': {}
            }
            
            for tabela in tabelas_principais:
                self.cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = self.cursor.fetchone()[0]
                relatorio['registros_por_tabela'][tabela] = count
            
            # Salvar relatório
            with open('relatorio_banco_aprimorado.json', 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info("Relatório de criação gerado: relatorio_banco_aprimorado.json")
            return relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return None
    
    def fechar(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco fechada")

def main():
    """Função principal"""
    logger.info("=== CRIAÇÃO DO BANCO DE DADOS APRIMORADO ===")
    
    # Criar instância do banco
    banco = BancoDadosAprimorado()
    
    try:
        # Conectar ao banco
        if not banco.conectar():
            return False
        
        # Criar tabelas
        if not banco.criar_tabelas():
            return False
        
        # Verificar estrutura
        if not banco.verificar_estrutura():
            return False
        
        # Inserir dados iniciais
        if not banco.inserir_dados_iniciais():
            return False
        
        # Gerar relatório
        relatorio = banco.gerar_relatorio_criacao()
        
        logger.info("=== BANCO DE DADOS APRIMORADO CRIADO COM SUCESSO! ===")
        logger.info(f"Localização: {banco.db_path}")
        
        if relatorio:
            logger.info(f"Total de tabelas: {relatorio['tabelas_criadas']}")
            logger.info("Registros inseridos:")
            for tabela, count in relatorio['registros_por_tabela'].items():
                logger.info(f"  {tabela}: {count} registros")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante criação do banco: {e}")
        return False
    
    finally:
        banco.fechar()

if __name__ == "__main__":
    main() 