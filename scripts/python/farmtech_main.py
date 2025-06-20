#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema Integrado de Gestão Agrícola
Programa principal que integra todas as funcionalidades do sistema
"""

import os
import logging
import subprocess
import importlib
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    filename='farmtech.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Lista de dependências necessárias
DEPENDENCIAS = [
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'tabulate',
    'openpyxl'
]

def verificar_instalar_dependencias():
    """Verifica e instala as dependências necessárias"""
    import sys

    print("Verificando dependências...")
    dependencias_faltantes = []

    for pacote in DEPENDENCIAS:
        try:
            importlib.import_module(pacote)
        except ImportError:
            dependencias_faltantes.append(pacote)

    if dependencias_faltantes:
        print(f"Dependências faltantes: {', '.join(dependencias_faltantes)}")
        resposta = input("Deseja instalar as dependências faltantes? (s/n): ")

        if resposta.lower() == 's':
            print("Instalando dependências...")
            for pacote in dependencias_faltantes:
                print(f"Instalando {pacote}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
                    print(f"{pacote} instalado com sucesso!")
                except Exception as e:
                    print(f"Erro ao instalar {pacote}: {str(e)}")
                    print(f"Por favor, instale {pacote} manualmente com: pip install {pacote}")
        else:
            print("Algumas funcionalidades podem não estar disponíveis sem as dependências necessárias.")

class FarmTechSystem:
    """Sistema integrado de gestão agrícola FarmTech"""

    def __init__(self):
        """Inicializa o sistema integrado"""
        self.versao = "1.0.0"
        logging.info(f"Iniciando sistema FarmTech v{self.versao}")

        # Verificar diretórios
        self.verificar_diretorios()

        # Verificar módulos
        self.modulos_disponiveis = self.verificar_modulos()

    def verificar_diretorios(self):
        """Verifica e cria diretórios necessários"""
        diretorios = ['backups', 'relatorios', 'exportacoes', 'analises']
        for diretorio in diretorios:
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)
                logging.info(f"Diretório criado: {diretorio}")

    def verificar_modulos(self):
        """Verifica quais módulos estão disponíveis"""
        modulos = {
            'farmtech': False,
            'analise_dados': False,
            'corrigir_dados': False,
            'exportar_dados': False
        }

        # Verificar cada módulo
        for modulo in modulos.keys():
            if os.path.exists(f"{modulo}.py"):
                try:
                    # Tentar importar o módulo
                    importlib.import_module(modulo)
                    modulos[modulo] = True
                    logging.info(f"Módulo disponível: {modulo}")
                except ImportError as e:
                    logging.warning(f"Módulo {modulo} encontrado mas não pode ser importado: {str(e)}")
                    print(f"AVISO: Módulo {modulo} encontrado mas não pode ser importado.")
            else:
                logging.warning(f"Módulo não encontrado: {modulo}")

        return modulos

    def exibir_cabecalho(self):
        """Exibe o cabeçalho do sistema"""
        print("\n" + "="*70)
        print(f"{'FARMTECH SOLUTIONS - SISTEMA INTEGRADO DE GESTÃO AGRÍCOLA':^70}")
        print(f"{'Versão ' + self.versao:^70}")
        print(f"{'Data: ' + datetime.now().strftime('%d/%m/%Y'):^70}")
        print("="*70)

    def menu_principal(self):
        """Exibe o menu principal do sistema integrado"""
        while True:
            self.exibir_cabecalho()
            print("\nMENU PRINCIPAL:")

            # Opções disponíveis com base nos módulos presentes
            if self.modulos_disponiveis['farmtech']:
                print("1. Gestão de Dados Agrícolas")
            else:
                print("1. Gestão de Dados Agrícolas [Não disponível]")

            if self.modulos_disponiveis['analise_dados']:
                print("2. Análise de Dados")
            else:
                print("2. Análise de Dados [Não disponível]")

            if self.modulos_disponiveis['corrigir_dados']:
                print("3. Correção e Validação de Dados")
            else:
                print("3. Correção e Validação de Dados [Não disponível]")

            if self.modulos_disponiveis['exportar_dados']:
                print("4. Exportação de Dados")
            else:
                print("4. Exportação de Dados [Não disponível]")

            print("5. Sobre o Sistema")
            print("9. Executar Setup (Instalar dependências)")
            print("0. Sair")

            opcao = input("\nEscolha uma opção: ")

            if opcao == '1' and self.modulos_disponiveis['farmtech']:
                # Módulo de gestão de dados
                from farmtech import FarmTechApp
                app = FarmTechApp()
                app.menu_principal()
            elif opcao == '2' and self.modulos_disponiveis['analise_dados']:
                # Módulo de análise de dados
                import analise_dados
                analise_dados.main()
            elif opcao == '3' and self.modulos_disponiveis['corrigir_dados']:
                # Módulo de correção de dados
                import corrigir_dados
                corrigir_dados.main()
            elif opcao == '4' and self.modulos_disponiveis['exportar_dados']:
                # Módulo de exportação
                import exportar_dados
                exportar_dados.main()
            elif opcao == '5':
                self.sobre_sistema()
            elif opcao == '9':
                # Executar setup
                self.executar_setup()
                # Atualizar módulos disponíveis
                self.modulos_disponiveis = self.verificar_modulos()
            elif opcao == '0':
                print("\nEncerrando o sistema FarmTech. Obrigado por utilizar nossos serviços!")
                logging.info("Sistema encerrado pelo usuário")
                break
            elif opcao in ['1', '2', '3', '4'] and not self.modulos_disponiveis.get(list(self.modulos_disponiveis.keys())[int(opcao)-1], False):
                print("\nEsta funcionalidade não está disponível no momento.")
                print("Verifique se o módulo correspondente está presente e se todas as dependências estão instaladas.")
                input("Pressione ENTER para continuar...")
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")

    def executar_setup(self):
        """Executa o script de setup"""
        print("\nExecutando setup do sistema...")

        if os.path.exists('setup.py'):
            import setup
            setup.main()
        else:
            print("Arquivo setup.py não encontrado.")
            verificar_instalar_dependencias()

        input("\nPressione ENTER para continuar...")

    def sobre_sistema(self):
        """Exibe informações sobre o sistema"""
        self.exibir_cabecalho()
        print("\nSOBRE O SISTEMA FARMTECH")
        print("-"*70)
        print("FarmTech Solutions - Sistema Integrado de Gestão Agrícola")
        print(f"Versão: {self.versao}")
        print("Copyright © 2025 FarmTech Solutions. Todos os direitos reservados.")
        print("\nDescrição:")
        print("O Sistema FarmTech é uma plataforma completa de gestão agrícola")
        print("que permite o gerenciamento e análise de dados de culturas,")
        print("com funcionalidades de entrada, processamento, análise e exportação")
        print("de informações para otimizar o planejamento e a produtividade.")
        print("\nMódulos disponíveis:")
        for modulo, disponivel in self.modulos_disponiveis.items():
            status = "Disponível" if disponivel else "Não disponível"
            if modulo == 'farmtech':
                print(f"- Gestão de Dados: {status}")
            elif modulo == 'analise_dados':
                print(f"- Análise de Dados: {status}")
            elif modulo == 'corrigir_dados':
                print(f"- Correção e Validação: {status}")
            elif modulo == 'exportar_dados':
                print(f"- Exportação: {status}")

        print("\nContato:")
        print("FarmTech Solutions")
        print("contato@farmtech.com.br")
        print("www.farmtech.com.br")
        print("-"*70)

        input("\nPressione ENTER para voltar ao menu principal...")

def verificar_atualizacoes():
    """Verifica se existem atualizações para o sistema"""
    print("Verificando atualizações...")
    # Simulação de verificação de atualizações
    print("Sistema atualizado. Utilizando a versão mais recente.")

def criar_arquivo_exemplo():
    """Cria um arquivo de dados de exemplo se não existir nenhum"""
    if not os.path.exists('dados_fazenda.csv') and not os.path.exists('dados_fazenda.json'):
        print("Criando arquivo de dados de exemplo...")

        conteudo = """nome,area,linhas,produto,dosagem_por_metro,total_produto
Soja,100.0,2,fertilizante,500.0,100000.0
Café,400.0,4,fosfato,500.0,800000.0
Milho,250.0,3,nitrogênio,400.0,300000.0
"""

        with open('dados_fazenda.csv', 'w', encoding='utf-8') as f:
            f.write(conteudo)

        print("Arquivo de dados de exemplo criado: dados_fazenda.csv")

def main():
    """Função principal"""
    try:
        # Verificar atualizações
        verificar_atualizacoes()

        # Verificar dependências
        verificar_instalar_dependencias()

        # Criar arquivo de exemplo
        criar_arquivo_exemplo()

        # Iniciar sistema
        print("Iniciando Sistema FarmTech...")
        sistema = FarmTechSystem()
        sistema.menu_principal()
    except KeyboardInterrupt:
        print("\n\nOperação interrompida pelo usuário.")
        logging.info("Sistema interrompido pelo usuário (KeyboardInterrupt)")
    except Exception as e:
        print(f"\nErro não esperado: {str(e)}")
        logging.error(f"Erro não esperado: {str(e)}")
    finally:
        print("\nEncerrando sistema FarmTech.")
        logging.info("Sistema encerrado")

if __name__ == "__main__":
    main()
