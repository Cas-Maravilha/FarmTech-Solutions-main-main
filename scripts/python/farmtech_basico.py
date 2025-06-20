#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema de Gestão de Dados Agrícolas (Versão Básica)
Aplicativo para gerenciamento de dados de culturas em fazendas
Versão simplificada sem dependências externas
"""

import os
import csv
import json
from datetime import datetime

class FarmTechBasico:
    """Sistema de gerenciamento de dados agrícolas da FarmTech Solutions (versão básica)"""

    def __init__(self):
        """Inicializa o aplicativo com vetores vazios"""
        # Vetores para armazenar dados
        self.nomes = []
        self.areas = []
        self.linhas = []
        self.produtos = []
        self.dosagens = []
        self.totais_produto = []

        # Tentar carregar dados dos arquivos
        self.carregar_dados()

    def carregar_dados(self):
        """Tenta carregar dados de arquivos existentes"""
        try:
            # Tenta carregar do CSV primeiro
            if os.path.exists('dados_fazenda.csv'):
                with open('dados_fazenda.csv', 'r', encoding='utf-8') as arquivo:
                    leitor = csv.reader(arquivo)
                    next(leitor)  # Pula o cabeçalho

                    # Limpa os vetores
                    self.nomes = []
                    self.areas = []
                    self.linhas = []
                    self.produtos = []
                    self.dosagens = []
                    self.totais_produto = []

                    for linha in leitor:
                        if len(linha) >= 6:  # Certifica-se que temos todas as colunas
                            self.nomes.append(linha[0])
                            self.areas.append(float(linha[1]))
                            self.linhas.append(int(linha[2]))
                            self.produtos.append(linha[3])
                            self.dosagens.append(float(linha[4]))
                            self.totais_produto.append(float(linha[5]))

                print(f"Dados carregados com sucesso: {len(self.nomes)} culturas encontradas")
                return

            # Tenta carregar do JSON se CSV não existir
            if os.path.exists('dados_fazenda.json'):
                with open('dados_fazenda.json', 'r', encoding='utf-8') as arquivo:
                    dados = json.load(arquivo)

                    # Limpa os vetores
                    self.nomes = []
                    self.areas = []
                    self.linhas = []
                    self.produtos = []
                    self.dosagens = []
                    self.totais_produto = []

                    for item in dados:
                        self.nomes.append(item['nome'])
                        self.areas.append(float(item['area']))
                        self.linhas.append(int(item['linhas']))
                        self.produtos.append(item['produto'])
                        self.dosagens.append(float(item['dosagem_por_metro']))
                        self.totais_produto.append(float(item['total_produto']))

                print(f"Dados carregados com sucesso: {len(self.nomes)} culturas encontradas")
                return

        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")

    def salvar_dados(self):
        """Salva os dados atuais nos formatos CSV e JSON"""
        try:
            # Cria backup dos dados antigos se existirem
            if os.path.exists('dados_fazenda.csv'):
                data_atual = datetime.now().strftime('%Y%m%d')
                os.rename('dados_fazenda.csv', f'backup_{data_atual}.csv')
                print(f"Backup dos dados antigos criado em backup_{data_atual}.csv")

            # Salvar em CSV
            with open('dados_fazenda.csv', 'w', encoding='utf-8', newline='') as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(['nome', 'area', 'linhas', 'produto', 'dosagem_por_metro', 'total_produto'])

                for i in range(len(self.nomes)):
                    escritor.writerow([
                        self.nomes[i],
                        self.areas[i],
                        self.linhas[i],
                        self.produtos[i],
                        self.dosagens[i],
                        self.totais_produto[i]
                    ])

            # Salvar em JSON
            dados_json = []
            for i in range(len(self.nomes)):
                dados_json.append({
                    'nome': self.nomes[i],
                    'area': self.areas[i],
                    'linhas': self.linhas[i],
                    'produto': self.produtos[i],
                    'dosagem_por_metro': self.dosagens[i],
                    'total_produto': self.totais_produto[i]
                })

            with open('dados_fazenda.json', 'w', encoding='utf-8') as arquivo:
                json.dump(dados_json, arquivo, indent=4, ensure_ascii=False)

            print("Dados salvos com sucesso!")

        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")

    def exibir_dados(self):
        """Mostra os dados atuais na tela de forma formatada"""
        if not self.nomes:
            print("Não há dados para exibir.")
            return

        # Cabeçalho
        cabecalho = ["#", "Cultura", "Área (ha)", "Linhas", "Produto", "Dosagem (ml/m)", "Total (ml)"]
        linha_cabecalho = f"{cabecalho[0]:<3} {cabecalho[1]:<10} {cabecalho[2]:<10} {cabecalho[3]:<8} {cabecalho[4]:<12} {cabecalho[5]:<15} {cabecalho[6]:<15}"

        print("\nDados Atuais:")
        print("="*70)
        print(linha_cabecalho)
        print("-"*70)

        # Dados
        for i in range(len(self.nomes)):
            linha = f"{i+1:<3} {self.nomes[i]:<10} {self.areas[i]:<10.2f} {self.linhas[i]:<8} {self.produtos[i]:<12} {self.dosagens[i]:<15.2f} {self.totais_produto[i]:<15.2f}"
            print(linha)

        print("="*70)

        # Exibir estatísticas
        if len(self.areas) > 0:
            print("\nEstatísticas:")
            print("-"*70)
            print(f"Total de culturas: {len(self.nomes)}")
            print(f"Área total: {sum(self.areas):.2f} hectares")
            print(f"Total de produto utilizado: {sum(self.totais_produto):.2f} ml")
            print(f"Média de área por cultura: {sum(self.areas)/len(self.areas):.2f} hectares")
            print(f"Média de dosagem: {sum(self.dosagens)/len(self.dosagens):.2f} ml/metro")

    def adicionar_dados(self):
        """Adiciona novos dados aos vetores"""
        print("\n=== Adicionar Nova Cultura ===")

        try:
            nome = input("Nome da cultura: ")
            area = float(input("Área (hectares): "))
            linhas = int(input("Número de linhas: "))
            produto = input("Produto utilizado: ")
            dosagem = float(input("Dosagem por metro (ml): "))

            # Cálculo automático do total de produto
            total_produto = area * linhas * dosagem

            # Adiciona aos vetores
            self.nomes.append(nome)
            self.areas.append(area)
            self.linhas.append(linhas)
            self.produtos.append(produto)
            self.dosagens.append(dosagem)
            self.totais_produto.append(total_produto)

            print(f"\nCultura '{nome}' adicionada com sucesso!")
            print(f"Total calculado de produto: {total_produto:.2f} ml")

            # Salva automaticamente após adicionar
            self.salvar_dados()

        except ValueError:
            print("Erro: Por favor, insira valores numéricos para área, linhas e dosagem.")
        except Exception as e:
            print(f"Erro ao adicionar dados: {str(e)}")

    def atualizar_dados(self):
        """Atualiza dados em uma posição específica"""
        self.exibir_dados()

        if not self.nomes:
            return

        try:
            indice = int(input("\nDigite o número (#) da cultura que deseja atualizar: ")) - 1

            if indice < 0 or indice >= len(self.nomes):
                print("Índice inválido!")
                return

            print(f"\nAtualizando dados para: {self.nomes[indice]}")
            print("Deixe em branco para manter o valor atual")

            # Nome
            entrada = input(f"Nome ({self.nomes[indice]}): ")
            if entrada.strip():
                self.nomes[indice] = entrada

            # Área
            entrada = input(f"Área ({self.areas[indice]} hectares): ")
            if entrada.strip():
                self.areas[indice] = float(entrada)

            # Linhas
            entrada = input(f"Linhas ({self.linhas[indice]}): ")
            if entrada.strip():
                self.linhas[indice] = int(entrada)

            # Produto
            entrada = input(f"Produto ({self.produtos[indice]}): ")
            if entrada.strip():
                self.produtos[indice] = entrada

            # Dosagem
            entrada = input(f"Dosagem ({self.dosagens[indice]} ml/metro): ")
            if entrada.strip():
                self.dosagens[indice] = float(entrada)

            # Recalcular o total de produto
            self.totais_produto[indice] = self.areas[indice] * self.linhas[indice] * self.dosagens[indice]

            print(f"\nDados de '{self.nomes[indice]}' atualizados com sucesso!")
            print(f"Total calculado de produto: {self.totais_produto[indice]:.2f} ml")

            # Salva automaticamente após atualizar
            self.salvar_dados()

        except ValueError:
            print("Erro: Por favor, insira um número válido para o índice.")
        except Exception as e:
            print(f"Erro ao atualizar dados: {str(e)}")

    def deletar_dados(self):
        """Remove dados de uma posição específica dos vetores"""
        self.exibir_dados()

        if not self.nomes:
            return

        try:
            indice = int(input("\nDigite o número (#) da cultura que deseja remover: ")) - 1

            if indice < 0 or indice >= len(self.nomes):
                print("Índice inválido!")
                return

            nome_cultura = self.nomes[indice]

            # Confirmação
            confirmacao = input(f"Tem certeza que deseja remover '{nome_cultura}'? (s/n): ")
            if confirmacao.lower() != 's':
                print("Operação cancelada.")
                return

            # Remove o item de todos os vetores
            self.nomes.pop(indice)
            self.areas.pop(indice)
            self.linhas.pop(indice)
            self.produtos.pop(indice)
            self.dosagens.pop(indice)
            self.totais_produto.pop(indice)

            print(f"\nCultura '{nome_cultura}' removida com sucesso!")

            # Salva automaticamente após deletar
            self.salvar_dados()

        except ValueError:
            print("Erro: Por favor, insira um número válido para o índice.")
        except Exception as e:
            print(f"Erro ao deletar dados: {str(e)}")

    def exportar_relatorio(self):
        """Exporta um relatório básico em formato de texto"""
        if not self.nomes:
            print("Não há dados para exportar.")
            return

        try:
            # Cria diretório de relatórios se não existir
            if not os.path.exists('relatorios'):
                os.makedirs('relatorios')

            data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f'relatorios/relatorio_{data_atual}.txt'

            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write("======================================================\n")
                arquivo.write("             RELATÓRIO FARMTECH SOLUTIONS             \n")
                arquivo.write("======================================================\n")
                arquivo.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

                # Estatísticas gerais
                arquivo.write("ESTATÍSTICAS GERAIS\n")
                arquivo.write("------------------------------------------------------\n")
                arquivo.write(f"Total de culturas: {len(self.nomes)}\n")
                arquivo.write(f"Área total: {sum(self.areas):.2f} hectares\n")
                arquivo.write(f"Total de produto utilizado: {sum(self.totais_produto):.2f} ml\n")
                arquivo.write(f"Média de área por cultura: {sum(self.areas)/len(self.areas):.2f} hectares\n")
                arquivo.write(f"Média de dosagem: {sum(self.dosagens)/len(self.dosagens):.2f} ml/metro\n\n")

                # Dados detalhados
                arquivo.write("DADOS DETALHADOS\n")
                arquivo.write("------------------------------------------------------\n")

                # Cabeçalho da tabela
                arquivo.write(f"{'#':<3} {'Cultura':<10} {'Área (ha)':<10} {'Linhas':<8} {'Produto':<12} {'Dosagem (ml/m)':<15} {'Total (ml)':<15}\n")
                arquivo.write("-"*70 + "\n")

                # Dados
                for i in range(len(self.nomes)):
                    linha = f"{i+1:<3} {self.nomes[i]:<10} {self.areas[i]:<10.2f} {self.linhas[i]:<8} {self.produtos[i]:<12} {self.dosagens[i]:<15.2f} {self.totais_produto[i]:<15.2f}"
                    arquivo.write(linha + "\n")

                arquivo.write("\n")

                # Dados por cultura
                arquivo.write("ANÁLISE POR CULTURA\n")
                arquivo.write("------------------------------------------------------\n")

                for i in range(len(self.nomes)):
                    arquivo.write(f"Cultura: {self.nomes[i]}\n")
                    arquivo.write(f"  Área: {self.areas[i]:.2f} hectares\n")
                    arquivo.write(f"  Linhas: {self.linhas[i]}\n")
                    arquivo.write(f"  Produto: {self.produtos[i]}\n")
                    arquivo.write(f"  Dosagem: {self.dosagens[i]:.2f} ml/metro\n")
                    arquivo.write(f"  Total de produto: {self.totais_produto[i]:.2f} ml\n")
                    arquivo.write(f"  Eficiência: {self.totais_produto[i]/self.areas[i]:.2f} ml/hectare\n")
                    arquivo.write("------------------------------------------------------\n")

            print(f"\nRelatório exportado com sucesso para: {nome_arquivo}")

        except Exception as e:
            print(f"Erro ao exportar relatório: {str(e)}")

    def menu_principal(self):
        """Exibe o menu principal e gerencia as opções"""
        while True:
            print("\n" + "="*50)
            print("          FARMTECH SOLUTIONS - GESTÃO AGRÍCOLA          ")
            print("="*50)
            print("Menu Principal:")
            print("1. Entrada de dados (adicionar nova cultura)")
            print("2. Saída de dados (visualizar dados atuais)")
            print("3. Atualização de dados (modificar cultura existente)")
            print("4. Deleção de dados (remover cultura)")
            print("5. Exportar relatório básico")
            print("0. Sair do programa")

            opcao = input("\nEscolha uma opção: ")

            if opcao == '1':
                self.adicionar_dados()
            elif opcao == '2':
                self.exibir_dados()
            elif opcao == '3':
                self.atualizar_dados()
            elif opcao == '4':
                self.deletar_dados()
            elif opcao == '5':
                self.exportar_relatorio()
            elif opcao == '0':
                print("\nSaindo do programa. Obrigado por utilizar o FarmTech Solutions!")
                break
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    print("Iniciando FarmTech Solutions (Versão Básica)...")
    app = FarmTechBasico()
    app.menu_principal()
