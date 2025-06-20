#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Script de Inicialização da API
Script para iniciar a API com verificações de ambiente e configurações
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('start_api')

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 6):
        logger.error("Python 3.6+ é necessário")
        return False
    logger.info(f"Python {sys.version} - OK")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'flask',
        'flask_cors',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✓ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} - FALTANDO")
    
    if missing_packages:
        logger.error(f"Pacotes faltando: {', '.join(missing_packages)}")
        logger.info("Execute: pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """Verifica se o banco de dados existe e está acessível"""
    db_path = Path('data/farmtech.db')
    
    if not db_path.exists():
        logger.warning("Banco de dados não encontrado")
        logger.info("Criando banco de dados...")
        
        try:
            # Criar diretório data se não existir
            db_path.parent.mkdir(exist_ok=True)
            
            # Executar script de criação do banco
            result = subprocess.run([
                sys.executable, 'demo_sensores.py', '--criar-banco'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Banco de dados criado com sucesso")
                return True
            else:
                logger.error(f"Erro ao criar banco: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao criar banco de dados: {e}")
            return False
    else:
        logger.info("✓ Banco de dados encontrado")
        return True

def check_data_directory():
    """Verifica se o diretório de dados existe"""
    data_dir = Path('data')
    
    if not data_dir.exists():
        logger.info("Criando diretório data...")
        data_dir.mkdir(exist_ok=True)
    
    logger.info("✓ Diretório data - OK")
    return True

def generate_sample_data():
    """Gera dados de exemplo se necessário"""
    try:
        # Verificar se há sensores no banco
        import sqlite3
        conn = sqlite3.connect('data/farmtech.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor")
        sensor_count = cursor.fetchone()[0]
        conn.close()
        
        if sensor_count == 0:
            logger.info("Gerando dados de exemplo...")
            result = subprocess.run([
                sys.executable, 'demo_sensores.py', '--dados-exemplo'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Dados de exemplo gerados")
            else:
                logger.warning("Erro ao gerar dados de exemplo")
        else:
            logger.info(f"✓ {sensor_count} sensores encontrados no banco")
            
    except Exception as e:
        logger.warning(f"Erro ao verificar dados: {e}")

def check_port_availability(port=5000):
    """Verifica se a porta está disponível"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            logger.info(f"✓ Porta {port} disponível")
            return True
    except OSError:
        logger.error(f"✗ Porta {port} já está em uso")
        return False

def start_api():
    """Inicia a API Flask"""
    logger.info("Iniciando FarmTech Solutions API...")
    
    try:
        # Importar e executar a API
        from api import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("API interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar API: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    logger.info("=== FarmTech Solutions - Verificação de Ambiente ===")
    
    # Verificações
    checks = [
        ("Versão do Python", check_python_version),
        ("Dependências", check_dependencies),
        ("Diretório de dados", check_data_directory),
        ("Banco de dados", check_database),
        ("Porta disponível", lambda: check_port_availability(5000))
    ]
    
    all_ok = True
    for check_name, check_func in checks:
        logger.info(f"\n--- Verificando {check_name} ---")
        if not check_func():
            all_ok = False
    
    if not all_ok:
        logger.error("\n❌ Verificações falharam. Corrija os problemas antes de continuar.")
        return False
    
    # Gerar dados de exemplo se necessário
    logger.info("\n--- Gerando dados de exemplo ---")
    generate_sample_data()
    
    # Iniciar API
    logger.info("\n=== Iniciando API ===")
    return start_api()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 