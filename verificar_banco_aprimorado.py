#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Verificação do Banco de Dados Aprimorado
Script para verificar e analisar o banco de dados aprimorado
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('verificar_banco_aprimorado')

class VerificadorBancoAprimorado:
    def __init__(self, db_path='data/farmtech_aprimorado.db'):
        self.db_path = db_path
        self.conn = None
    
    def conectar(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Conectado ao banco: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return False
    
    def verificar_tabelas(self):
        """Verifica todas as tabelas do banco"""
        try:
            cursor = self.conn.cursor()
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Tabelas encontradas: {len(tabelas)}")
            
            # Verificar cada tabela
            for tabela in sorted(tabelas):
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                logger.info(f"  {tabela}: {count} registros")
            
            return tabelas
            
        except Exception as e:
            logger.error(f"Erro ao verificar tabelas: {e}")
            return []
    
    def analisar_relacionamentos(self):
        """Analisa os relacionamentos entre tabelas"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar foreign keys
            cursor.execute("PRAGMA foreign_key_list(PLANTIO)")
            fks_plantio = cursor.fetchall()
            
            cursor.execute("PRAGMA foreign_key_list(SENSOR)")
            fks_sensor = cursor.fetchall()
            
            cursor.execute("PRAGMA foreign_key_list(LEITURA)")
            fks_leitura = cursor.fetchall()
            
            logger.info("Relacionamentos principais:")
            logger.info(f"  PLANTIO: {len(fks_plantio)} foreign keys")
            logger.info(f"  SENSOR: {len(fks_sensor)} foreign keys")
            logger.info(f"  LEITURA: {len(fks_leitura)} foreign keys")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao analisar relacionamentos: {e}")
            return False
    
    def analisar_dados_plantio(self):
        """Analisa dados de plantio"""
        try:
            query = """
            SELECT 
                p.codigo_plantio,
                f.nome as fazenda,
                a.nome as area,
                t.nome as talhao,
                c.nome as cultura,
                c.variedade,
                p.data_inicio,
                p.status_plantio,
                p.fase_crescimento,
                p.area_plantada,
                p.producao_estimada,
                p.produtividade_estimada
            FROM PLANTIO p
            JOIN TALHAO t ON p.talhao_id = t.talhao_id
            JOIN AREA a ON t.area_id = a.area_id
            JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
            JOIN CULTURA c ON p.cultura_id = c.cultura_id
            ORDER BY p.data_inicio DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Dados de plantio: {len(df)} registros")
            logger.info("\nResumo por cultura:")
            for cultura in df['cultura'].unique():
                subset = df[df['cultura'] == cultura]
                area_total = subset['area_plantada'].sum()
                prod_estimada = subset['producao_estimada'].sum()
                logger.info(f"  {cultura}: {len(subset)} plantios, {area_total:.1f} ha, {prod_estimada:.1f} t")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao analisar dados de plantio: {e}")
            return None
    
    def analisar_sensores(self):
        """Analisa dados de sensores"""
        try:
            query = """
            SELECT 
                s.codigo,
                ts.nome as tipo_sensor,
                f.nome as fazenda,
                a.nome as area,
                t.nome as talhao,
                s.status,
                s.bateria_nivel,
                s.sinal_forca,
                s.ultima_manutencao,
                s.proxima_manutencao,
                (SELECT COUNT(*) FROM LEITURA l WHERE l.sensor_id = s.sensor_id) as total_leituras,
                (SELECT MAX(data_hora) FROM LEITURA l WHERE l.sensor_id = s.sensor_id) as ultima_leitura
            FROM SENSOR s
            JOIN TIPO_SENSOR ts ON s.tipo_sensor_id = ts.tipo_sensor_id
            LEFT JOIN TALHAO t ON s.talhao_id = t.talhao_id
            LEFT JOIN AREA a ON t.area_id = a.area_id
            LEFT JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
            ORDER BY s.codigo
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Sensores: {len(df)} registros")
            logger.info("\nStatus dos sensores:")
            for status in df['status'].unique():
                count = len(df[df['status'] == status])
                logger.info(f"  {status}: {count} sensores")
            
            logger.info("\nTipos de sensores:")
            for tipo in df['tipo_sensor'].unique():
                count = len(df[df['tipo_sensor'] == tipo])
                logger.info(f"  {tipo}: {count} sensores")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao analisar sensores: {e}")
            return None
    
    def analisar_leituras(self):
        """Analisa dados de leituras"""
        try:
            query = """
            SELECT 
                l.data_hora,
                l.valor,
                l.unidade_medida,
                l.qualidade_dado,
                ts.nome as tipo_sensor,
                f.nome as fazenda,
                a.nome as area,
                t.nome as talhao
            FROM LEITURA l
            JOIN SENSOR s ON l.sensor_id = s.sensor_id
            JOIN TIPO_SENSOR ts ON s.tipo_sensor_id = ts.tipo_sensor_id
            LEFT JOIN TALHAO t ON s.talhao_id = t.talhao_id
            LEFT JOIN AREA a ON t.area_id = a.area_id
            LEFT JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
            WHERE l.data_hora >= datetime('now', '-7 days')
            ORDER BY l.data_hora DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Leituras dos últimos 7 dias: {len(df)} registros")
            
            if len(df) > 0:
                logger.info("\nEstatísticas por tipo de sensor:")
                for tipo in df['tipo_sensor'].unique():
                    subset = df[df['tipo_sensor'] == tipo]
                    logger.info(f"  {tipo}: {len(subset)} leituras, média: {subset['valor'].mean():.2f}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao analisar leituras: {e}")
            return None
    
    def analisar_recomendacoes(self):
        """Analisa dados de recomendações"""
        try:
            query = """
            SELECT 
                r.titulo,
                r.tipo_recomendacao,
                r.prioridade,
                r.status,
                r.data_geracao,
                r.prazo_aplicacao,
                f.nome as fazenda,
                a.nome as area,
                t.nome as talhao,
                c.nome as cultura
            FROM RECOMENDACAO r
            JOIN PLANTIO p ON r.plantio_id = p.plantio_id
            JOIN TALHAO t ON r.talhao_id = t.talhao_id
            JOIN AREA a ON t.area_id = a.area_id
            JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
            JOIN CULTURA c ON p.cultura_id = c.cultura_id
            ORDER BY r.data_geracao DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Recomendações: {len(df)} registros")
            
            if len(df) > 0:
                logger.info("\nStatus das recomendações:")
                for status in df['status'].unique():
                    count = len(df[df['status'] == status])
                    logger.info(f"  {status}: {count} recomendações")
                
                logger.info("\nTipos de recomendação:")
                for tipo in df['tipo_recomendacao'].unique():
                    count = len(df[df['tipo_recomendacao'] == tipo])
                    logger.info(f"  {tipo}: {count} recomendações")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao analisar recomendações: {e}")
            return None
    
    def analisar_alertas(self):
        """Analisa dados de alertas"""
        try:
            query = """
            SELECT 
                a.titulo,
                a.severidade,
                a.status,
                a.data_geracao,
                a.data_resolucao,
                f.nome as fazenda,
                a.nome as area,
                t.nome as talhao
            FROM ALERTA a
            LEFT JOIN SENSOR s ON a.sensor_id = s.sensor_id
            LEFT JOIN TALHAO t ON a.talhao_id = t.talhao_id OR (s.talhao_id = t.talhao_id)
            LEFT JOIN AREA a ON t.area_id = a.area_id
            LEFT JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
            ORDER BY a.data_geracao DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Alertas: {len(df)} registros")
            
            if len(df) > 0:
                logger.info("\nStatus dos alertas:")
                for status in df['status'].unique():
                    count = len(df[df['status'] == status])
                    logger.info(f"  {status}: {count} alertas")
                
                logger.info("\nSeveridade dos alertas:")
                for sev in df['severidade'].unique():
                    count = len(df[df['severidade'] == sev])
                    logger.info(f"  {sev}: {count} alertas")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao analisar alertas: {e}")
            return None
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo do banco"""
        try:
            relatorio = {
                'data_analise': datetime.now().isoformat(),
                'banco': self.db_path,
                'tabelas': {},
                'resumo': {}
            }
            
            # Verificar tabelas
            tabelas = self.verificar_tabelas()
            
            # Analisar dados principais
            df_plantio = self.analisar_dados_plantio()
            df_sensores = self.analisar_sensores()
            df_leituras = self.analisar_leituras()
            df_recomendacoes = self.analisar_recomendacoes()
            df_alertas = self.analisar_alertas()
            
            # Resumo geral
            relatorio['resumo'] = {
                'total_tabelas': len(tabelas),
                'total_plantios': len(df_plantio) if df_plantio is not None else 0,
                'total_sensores': len(df_sensores) if df_sensores is not None else 0,
                'total_leituras_7dias': len(df_leituras) if df_leituras is not None else 0,
                'total_recomendacoes': len(df_recomendacoes) if df_recomendacoes is not None else 0,
                'total_alertas': len(df_alertas) if df_alertas is not None else 0
            }
            
            # Salvar relatório
            with open('relatorio_analise_banco_aprimorado.json', 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info("Relatório completo gerado: relatorio_analise_banco_aprimorado.json")
            return relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório completo: {e}")
            return None
    
    def testar_consultas_complexas(self):
        """Testa consultas complexas do sistema"""
        try:
            cursor = self.conn.cursor()
            
            logger.info("=== TESTANDO CONSULTAS COMPLEXAS ===")
            
            # 1. Produtividade por fazenda
            query1 = """
            SELECT 
                f.nome as fazenda,
                COUNT(p.plantio_id) as total_plantios,
                SUM(p.area_plantada) as area_total,
                SUM(p.producao_estimada) as producao_estimada,
                AVG(p.produtividade_estimada) as produtividade_media
            FROM FAZENDA f
            JOIN AREA a ON f.fazenda_id = a.fazenda_id
            JOIN TALHAO t ON a.area_id = t.area_id
            JOIN PLANTIO p ON t.talhao_id = p.talhao_id
            GROUP BY f.fazenda_id, f.nome
            ORDER BY produtividade_media DESC
            """
            
            cursor.execute(query1)
            resultados1 = cursor.fetchall()
            logger.info(f"Produtividade por fazenda: {len(resultados1)} registros")
            
            # 2. Sensores por área
            query2 = """
            SELECT 
                f.nome as fazenda,
                a.nome as area,
                COUNT(s.sensor_id) as total_sensores,
                AVG(s.bateria_nivel) as bateria_media,
                AVG(s.sinal_forca) as sinal_medio
            FROM FAZENDA f
            JOIN AREA a ON f.fazenda_id = a.fazenda_id
            JOIN TALHAO t ON a.area_id = t.area_id
            LEFT JOIN SENSOR s ON t.talhao_id = s.talhao_id
            GROUP BY f.fazenda_id, a.area_id, f.nome, a.nome
            ORDER BY total_sensores DESC
            """
            
            cursor.execute(query2)
            resultados2 = cursor.fetchall()
            logger.info(f"Sensores por área: {len(resultados2)} registros")
            
            # 3. Alertas por severidade
            query3 = """
            SELECT 
                a.severidade,
                COUNT(*) as total_alertas,
                COUNT(CASE WHEN a.status = 'ativo' THEN 1 END) as alertas_ativos,
                COUNT(CASE WHEN a.status = 'resolvido' THEN 1 END) as alertas_resolvidos
            FROM ALERTA a
            GROUP BY a.severidade
            ORDER BY total_alertas DESC
            """
            
            cursor.execute(query3)
            resultados3 = cursor.fetchall()
            logger.info(f"Alertas por severidade: {len(resultados3)} registros")
            
            # 4. Recomendações por tipo
            query4 = """
            SELECT 
                r.tipo_recomendacao,
                COUNT(*) as total_recomendacoes,
                COUNT(CASE WHEN r.status = 'pendente' THEN 1 END) as pendentes,
                COUNT(CASE WHEN r.status = 'aprovada' THEN 1 END) as aprovadas,
                COUNT(CASE WHEN r.status = 'aplicada' THEN 1 END) as aplicadas
            FROM RECOMENDACAO r
            GROUP BY r.tipo_recomendacao
            ORDER BY total_recomendacoes DESC
            """
            
            cursor.execute(query4)
            resultados4 = cursor.fetchall()
            logger.info(f"Recomendações por tipo: {len(resultados4)} registros")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao testar consultas: {e}")
            return False
    
    def fechar(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco fechada")

def main():
    """Função principal"""
    logger.info("=== VERIFICAÇÃO DO BANCO DE DADOS APRIMORADO ===")
    
    # Criar instância do verificador
    verificador = VerificadorBancoAprimorado()
    
    try:
        # Conectar ao banco
        if not verificador.conectar():
            return False
        
        # Verificar tabelas
        verificador.verificar_tabelas()
        
        # Analisar relacionamentos
        verificador.analisar_relacionamentos()
        
        # Analisar dados principais
        verificador.analisar_dados_plantio()
        verificador.analisar_sensores()
        verificador.analisar_leituras()
        verificador.analisar_recomendacoes()
        verificador.analisar_alertas()
        
        # Testar consultas complexas
        verificador.testar_consultas_complexas()
        
        # Gerar relatório completo
        verificador.gerar_relatorio_completo()
        
        logger.info("=== VERIFICAÇÃO CONCLUÍDA COM SUCESSO! ===")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante verificação: {e}")
        return False
    
    finally:
        verificador.fechar()

if __name__ == "__main__":
    main() 