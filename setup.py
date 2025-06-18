#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Setup de Instalação
Script para instalação das dependências e configuração do sistema
"""

import os
import sys
import subprocess
import platform
import time

def verificar_python():
    """Verifica a versão do Python"""
    versao = platform.python_version()
    print(f"Versão do Python: {versao}")

    partes = versao.split('.')
    if int(partes[0]) < 3 or (int(partes[0]) == 3 and int(partes[1]) < 8):
        print("AVISO: Este sistema requer Python 3.8 ou superior.")
        return False
    return True

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("Instalando dependências...")

    # Lista mínima de dependências necessárias
    dependencias_minimas = [
        'pandas',
        'tabulate'
    ]

    # Instalar individualmente
    for pacote in dependencias_minimas:
        print(f"Instalando {pacote}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
            print(f"{pacote} instalado com sucesso.")
        except subprocess.CalledProcessError:
            print(f"Falha ao instalar {pacote}. Por favor, instale manualmente: pip install {pacote}")

    # Tentar instalar o restante das dependências pelo requirements.txt
    if os.path.exists('requirements.txt'):
        print("Instalando dependências adicionais do requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Todas as dependências instaladas com sucesso.")
        except subprocess.CalledProcessError:
            print("Falha ao instalar todas as dependências. Algumas funcionalidades podem não estar disponíveis.")

    return True

def verificar_arquivos():
    """Verifica a presença dos arquivos necessários"""
    arquivos_essenciais = [
        'farmtech.py',
        'farmtech_main.py',
        'README.md'
    ]

    arquivos_opcionais = [
        'analise_dados.py',
        'corrigir_dados.py',
        'exportar_dados.py'
    ]

    print("\nVerificando arquivos do sistema...")

    # Verificar arquivos essenciais
    arquivos_faltantes = [arquivo for arquivo in arquivos_essenciais if not os.path.exists(arquivo)]
    if arquivos_faltantes:
        print("ERRO: Os seguintes arquivos essenciais estão faltando:")
        for arquivo in arquivos_faltantes:
            print(f"  - {arquivo}")
        return False

    # Verificar arquivos opcionais
    arquivos_opcionais_faltantes = [arquivo for arquivo in arquivos_opcionais if not os.path.exists(arquivo)]
    if arquivos_opcionais_faltantes:
        print("AVISO: Os seguintes arquivos opcionais estão faltando:")
        for arquivo in arquivos_opcionais_faltantes:
            print(f"  - {arquivo}")
        print("Algumas funcionalidades do sistema poderão não estar disponíveis.")

    return True

def criar_diretorios():
    """Cria os diretórios necessários para o funcionamento do sistema"""
    diretorios = ['backups', 'relatorios', 'exportacoes', 'analises']

    print("\nCriando diretórios do sistema...")
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"  - Diretório '{diretorio}' criado com sucesso.")
        else:
            print(f"  - Diretório '{diretorio}' já existe.")

    return True

def criar_arquivo_exemplo():
    """Cria um arquivo de exemplo se não existir nenhum dado"""
    if not os.path.exists('dados_fazenda.csv') and not os.path.exists('dados_fazenda.json'):
        print("\nCriando arquivo de dados de exemplo...")

        conteudo_csv = """nome,area,linhas,produto,dosagem_por_metro,total_produto
Soja,100.0,2,fertilizante,500.0,100000.0
Café,400.0,4,fosfato,500.0,800000.0
Milho,250.0,3,nitrogênio,400.0,300000.0
"""

        with open('dados_fazenda.csv', 'w', encoding='utf-8') as f:
            f.write(conteudo_csv)

        print("Arquivo de dados de exemplo 'dados_fazenda.csv' criado com sucesso.")

    return True

def main():
    """Função principal de configuração"""
    print("="*70)
    print("          FARMTECH SOLUTIONS - CONFIGURAÇÃO DO SISTEMA          ")
    print("="*70)
    print("\nIniciando configuração do sistema...\n")

    # Verificar versão do Python
    if not verificar_python():
        print("\nAVISO: A versão do Python pode causar problemas de compatibilidade.")
        continuar = input("Deseja continuar mesmo assim? (s/n): ")
        if continuar.lower() != 's':
            print("Configuração cancelada.")
            return

    # Instalar dependências
    if not instalar_dependencias():
        print("\nAVISO: Problemas ao instalar dependências.")
        continuar = input("Deseja continuar mesmo assim? (s/n): ")
        if continuar.lower() != 's':
            print("Configuração cancelada.")
            return

    # Verificar arquivos
    if not verificar_arquivos():
        print("\nErro: Arquivos essenciais faltando. Verifique a instalação.")
        return

    # Criar diretórios
    criar_diretorios()

    # Criar arquivo de exemplo
    criar_arquivo_exemplo()

    print("\nConfiguração concluída com sucesso!")
    print("\nVocê pode iniciar o sistema com o comando:")
    print(f"  {sys.executable} farmtech_main.py")

    # Perguntar se deseja iniciar o sistema
    iniciar = input("\nDeseja iniciar o sistema agora? (s/n): ")
    if iniciar.lower() == 's':
        print("\nIniciando sistema...")
        time.sleep(1)
        try:
            subprocess.check_call([sys.executable, "farmtech_main.py"])
        except subprocess.CalledProcessError:
            print("Erro ao iniciar o sistema. Tente executar manualmente.")

if __name__ == "__main__":
    main()
