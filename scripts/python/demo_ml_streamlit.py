#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Demonstração de Machine Learning e Streamlit
Script para treinar modelos e executar a aplicação interativa
"""

import subprocess
import sys
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def instalar_dependencias():
    """Instala as dependências necessárias"""
    logger.info("Instalando dependências...")
    
    try:
        # Instalar dependências básicas
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_ml.txt"])
        logger.info("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao instalar dependências: {e}")
        return False

def verificar_banco_dados():
    """Verifica se o banco de dados existe"""
    db_path = "data/farmtech_aprimorado.db"
    
    if os.path.exists(db_path):
        logger.info(f"✅ Banco de dados encontrado: {db_path}")
        return True
    else:
        logger.error(f"❌ Banco de dados não encontrado: {db_path}")
        logger.info("Execute primeiro: python criar_banco_aprimorado.py")
        return False

def treinar_modelos():
    """Treina os modelos de machine learning"""
    logger.info("Treinando modelos de machine learning...")
    
    try:
        # Importar e executar treinamento
        from farmtech_ml_models import FarmTechMLModels
        
        ml_models = FarmTechMLModels()
        
        if not ml_models.conectar_banco():
            logger.error("❌ Não foi possível conectar ao banco")
            return False
        
        # Treinar modelos
        logger.info("🌾 Treinando modelo de produtividade...")
        resultados_produtividade = ml_models.treinar_modelo_produtividade()
        
        logger.info("💧 Treinando modelo de irrigação...")
        resultados_irrigacao = ml_models.treinar_modelo_irrigacao()
        
        logger.info("⚠️ Treinando modelo de detecção de anomalias...")
        resultados_anomalias = ml_models.treinar_modelo_anomalias()
        
        # Salvar modelos
        ml_models.salvar_modelos()
        
        # Exibir resultados
        logger.info("=== RESULTADOS DO TREINAMENTO ===")
        logger.info(f"🌾 Produtividade - R²: {resultados_produtividade['r2']:.3f}")
        logger.info(f"💧 Irrigação - Accuracy: {resultados_irrigacao['accuracy']:.3f}")
        logger.info(f"⚠️ Anomalias - Accuracy: {resultados_anomalias['accuracy']:.3f}")
        
        ml_models.conn.close()
        logger.info("✅ Modelos treinados e salvos com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no treinamento: {e}")
        return False

def executar_streamlit():
    """Executa a aplicação Streamlit"""
    logger.info("🚀 Iniciando aplicação Streamlit...")
    
    try:
        # Comando para executar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "farmtech_streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ]
        
        logger.info("Aplicação disponível em: http://localhost:8501")
        logger.info("Pressione Ctrl+C para parar a aplicação")
        
        # Executar Streamlit
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        logger.info("🛑 Aplicação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao executar Streamlit: {e}")

def main():
    """Função principal"""
    logger.info("=== FARM TECH SOLUTIONS - DEMO ML & STREAMLIT ===")
    
    # Verificar dependências
    logger.info("1. Verificando dependências...")
    if not instalar_dependencias():
        return
    
    # Verificar banco de dados
    logger.info("2. Verificando banco de dados...")
    if not verificar_banco_dados():
        return
    
    # Treinar modelos
    logger.info("3. Treinando modelos...")
    if not treinar_modelos():
        logger.error("❌ Falha no treinamento dos modelos")
        return
    
    # Executar Streamlit
    logger.info("4. Iniciando aplicação...")
    executar_streamlit()

if __name__ == "__main__":
    main() 