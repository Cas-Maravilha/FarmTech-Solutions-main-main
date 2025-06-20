#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Módulo de Análise Estatística
Script para analisar e visualizar dados agrícolas
"""

import os
import json
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    filename='farmtech.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AnalisadorDados:
    """Realiza análises estatísticas e visualizações dos dados agrícolas"""

    def __init__(self):
        """Inicializa o analisador de dados"""
        self.dados = None
        self.df = None

        # Criar diretório de saída se não existir
        if not os.path.exists('analises'):
            os.makedirs('analises')

    def carregar_dados(self, fonte='dados_fazenda.csv'):
        """Carrega dados de um arquivo CSV ou JSON"""
        try:
            if fonte.endswith('.csv'):
                self.df = pd.read_csv(fonte)
            elif fonte.endswith('.json'):
                with open(fonte, 'r', encoding='utf-8') as arquivo:
                    self.dados = json.load(arquivo)
                self.df = pd.DataFrame(self.dados)
            else:
                raise ValueError("Formato de arquivo não suportado. Use CSV ou JSON.")

            # Validação básica das colunas esperadas
            colunas_esperadas = ['nome', 'area', 'linhas', 'produto', 'dosagem_por_metro', 'total_produto']
            for coluna in colunas_esperadas:
                if coluna not in self.df.columns:
                    raise ValueError(f"Coluna '{coluna}' não encontrada no arquivo.")

            logging.info(f"Dados carregados com sucesso do arquivo {fonte}")
            print(f"Dados carregados com sucesso: {len(self.df)} registros.")
            return True

        except Exception as e:
            logging.error(f"Erro ao carregar dados: {str(e)}")
            print(f"Erro ao carregar dados: {str(e)}")
            return False

    def estatisticas_descritivas(self):
        """Calcula estatísticas descritivas básicas"""
        if self.df is None:
            print("Nenhum dado carregado para análise.")
            return None

        try:
            # Estatísticas gerais
            estatisticas = {
                'Número de registros': len(self.df),
                'Número de culturas únicas': self.df['nome'].nunique(),
                'Área total (ha)': self.df['area'].sum(),
                'Área média (ha)': self.df['area'].mean(),
                'Desvio padrão da área': self.df['area'].std(),
                'Total de produto (ml)': self.df['total_produto'].sum(),
                'Dosagem média (ml/m)': self.df['dosagem_por_metro'].mean(),
                'Número médio de linhas': self.df['linhas'].mean()
            }

            # Estatísticas por cultura
            por_cultura = self.df.groupby('nome').agg({
                'area': ['sum', 'mean', 'std', 'count'],
                'linhas': ['mean', 'sum'],
                'dosagem_por_metro': ['mean', 'std'],
                'total_produto': ['sum', 'mean']
            })

            # Corrigir nomes das colunas para melhor legibilidade
            por_cultura.columns = ['_'.join(col).strip() for col in por_cultura.columns.values]

            return {
                'geral': estatisticas,
                'por_cultura': por_cultura
            }

        except Exception as e:
            logging.error(f"Erro ao calcular estatísticas: {str(e)}")
            print(f"Erro ao calcular estatísticas: {str(e)}")
            return None

    def detectar_outliers(self, metodo='iqr'):
        """Detecta valores atípicos nos dados numéricos"""
        if self.df is None:
            print("Nenhum dado carregado para análise.")
            return None

        try:
            colunas_numericas = ['area', 'linhas', 'dosagem_por_metro', 'total_produto']
            resultado = {}

            for coluna in colunas_numericas:
                if metodo == 'iqr':
                    # Método IQR (Amplitude Interquartil)
                    Q1 = np.percentile(self.df[coluna], 25)
                    Q3 = np.percentile(self.df[coluna], 75)
                    IQR = Q3 - Q1

                    limite_inferior = Q1 - 1.5 * IQR
                    limite_superior = Q3 + 1.5 * IQR

                    outliers = self.df[(self.df[coluna] < limite_inferior) |
                                       (self.df[coluna] > limite_superior)]
                elif metodo == 'zscore':
                    # Método Z-score
                    z_scores = np.abs((self.df[coluna] - self.df[coluna].mean()) / self.df[coluna].std())
                    outliers = self.df[z_scores > 3]  # Z-score > 3 é considerado outlier
                else:
                    raise ValueError("Método de detecção de outliers não suportado.")

                resultado[coluna] = {
                    'numero_outliers': len(outliers),
                    'percentual_outliers': len(outliers) / len(self.df) * 100,
                    'indices_outliers': outliers.index.tolist(),
                    'valores_outliers': outliers[coluna].tolist()
                }

            return resultado

        except Exception as e:
            logging.error(f"Erro ao detectar outliers: {str(e)}")
            print(f"Erro ao detectar outliers: {str(e)}")
            return None

    def plotar_grafico_barras(self, coluna_x, coluna_y, titulo=None, xlabel=None, ylabel=None):
        """Plota um gráfico de barras com os dados"""
        if self.df is None:
            print("Nenhum dado carregado para análise.")
            return

        try:
            plt.figure(figsize=(10, 6))

            # Se coluna_x for categórica, agrupamos os dados
            if coluna_x in ['nome', 'produto']:
                dados_agrupados = self.df.groupby(coluna_x)[coluna_y].sum()
                sns.barplot(x=dados_agrupados.index, y=dados_agrupados.values)
            else:
                sns.barplot(x=coluna_x, y=coluna_y, data=self.df)

            # Configurar títulos e rótulos
            plt.title(titulo or f"{coluna_y} por {coluna_x}")
            plt.xlabel(xlabel or coluna_x)
            plt.ylabel(ylabel or coluna_y)
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Salvar o gráfico
            nome_arquivo = f"analises/grafico_barras_{coluna_x}_{coluna_y}.png"
            plt.savefig(nome_arquivo)
            plt.close()

            print(f"Gráfico salvo em: {nome_arquivo}")
            return nome_arquivo

        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de barras: {str(e)}")
            print(f"Erro ao plotar gráfico de barras: {str(e)}")

    def plotar_grafico_dispersao(self, coluna_x, coluna_y, coluna_cor=None, titulo=None):
        """Plota um gráfico de dispersão com os dados"""
        if self.df is None:
            print("Nenhum dado carregado para análise.")
            return

        try:
            plt.figure(figsize=(10, 6))

            if coluna_cor:
                g = sns.scatterplot(x=coluna_x, y=coluna_y, hue=coluna_cor, data=self.df)
                plt.legend(title=coluna_cor)
            else:
                g = sns.scatterplot(x=coluna_x, y=coluna_y, data=self.df)

            # Adicionar linha de tendência (regressão)
            sns.regplot(x=coluna_x, y=coluna_y, data=self.df, scatter=False, ax=g.axes)

            # Configurar títulos e rótulos
            plt.title(titulo or f"Relação entre {coluna_x} e {coluna_y}")
            plt.tight_layout()

            # Calcular correlação
            correlacao = self.df[[coluna_x, coluna_y]].corr().iloc[0, 1]
            plt.annotate(f"Correlação: {correlacao:.2f}",
                         xy=(0.05, 0.95),
                         xycoords='axes fraction',
                         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

            # Salvar o gráfico
            nome_arquivo = f"analises/grafico_dispersao_{coluna_x}_{coluna_y}.png"
            plt.savefig(nome_arquivo)
            plt.close()

            print(f"Gráfico salvo em: {nome_arquivo}")
            return nome_arquivo

        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de dispersão: {str(e)}")
            print(f"Erro ao plotar gráfico de dispersão: {str(e)}")

    def plotar_grafico_boxplot(self, coluna_y, coluna_grupo=None, titulo=None):
        """Plota um boxplot para identificar a distribuição e outliers"""
        if self.df is None:
            print("Nenhum dado carregado para análise.")
            return

        try:
            plt.figure(figsize=(10, 6))

            if coluna_grupo:
                sns.boxplot(x=coluna_grupo, y=coluna_y, data=self.df)
                plt.title(titulo or f"Distribuição de {coluna_y} por {coluna_grupo}")
            else:
                sns.boxplot(y=coluna_y, data=self.df)
                plt.title(titulo or f"Distribuição de {coluna_y}")

            plt.tight_layout()

            # Salvar o gráfico
            nome_arquivo = f"analises/grafico_boxplot_{coluna_y}.png"
            plt.savefig(nome_arquivo)
            plt.close()

            print(f"Gráfico salvo em: {nome_arquivo}")
            return nome_arquivo

        except Exception as e:
            logging.error(f"Erro ao plotar boxplot: {str(e)}")
            print(f"Erro ao plotar boxplot: {str(e)}")

    def gerar_relatorio_completo(self, nome_arquivo=None):
        """Gera um relatório completo com estatísticas e gráficos"""
        if self.df is None:
            print("Nenhum dado carregado para análise.")
            return

        if nome_arquivo is None:
            nome_arquivo = f"analises/relatorio_analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        try:
            # Obter estatísticas
            estatisticas = self.estatisticas_descritivas()
            outliers = self.detectar_outliers()

            # Gerar gráficos
            grafico_area = self.plotar_grafico_barras('nome', 'area',
                                                       "Área por Cultura", "Cultura", "Área (ha)")
            grafico_produto = self.plotar_grafico_barras('nome', 'total_produto',
                                                        "Total de Produto por Cultura", "Cultura", "Total (ml)")
            grafico_dispersao = self.plotar_grafico_dispersao('area', 'total_produto', 'nome',
                                                             "Relação entre Área e Total de Produto")
            grafico_boxplot_area = self.plotar_grafico_boxplot('area', 'nome',
                                                               "Distribuição da Área por Cultura")
            grafico_boxplot_dosagem = self.plotar_grafico_boxplot('dosagem_por_metro', 'nome',
                                                                "Distribuição da Dosagem por Cultura")

            # Iniciar conteúdo HTML
            conteudo_html = f"""
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Relatório de Análise - FarmTech Solutions</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2, h3 {{ color: #336699; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .grafico {{ margin: 20px 0; text-align: center; }}
                    .grafico img {{ max-width: 100%; height: auto; }}
                    .cabecalho {{ background-color: #336699; color: white; padding: 10px; margin-bottom: 20px; }}
                    .info {{ margin-bottom: 10px; }}
                    .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="cabecalho">
                        <h1>Relatório de Análise de Dados Agrícolas</h1>
                        <p>FarmTech Solutions - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>

                    <h2>1. Visão Geral dos Dados</h2>
                    <div class="info">
                        <p><strong>Número de registros:</strong> {estatisticas['geral']['Número de registros']}</p>
                        <p><strong>Número de culturas únicas:</strong> {estatisticas['geral']['Número de culturas únicas']}</p>
                        <p><strong>Área total:</strong> {estatisticas['geral']['Área total (ha)']:.2f} hectares</p>
                        <p><strong>Total de produto:</strong> {estatisticas['geral']['Total de produto (ml)']:.2f} ml</p>
                    </div>

                    <h2>2. Estatísticas Gerais</h2>
                    <table>
                        <tr>
                            <th>Métrica</th>
                            <th>Valor</th>
                        </tr>
            """

            # Adicionar estatísticas gerais
            for metrica, valor in estatisticas['geral'].items():
                conteudo_html += f"""
                        <tr>
                            <td>{metrica}</td>
                            <td>{valor:.2f if isinstance(valor, float) else valor}</td>
                        </tr>
                """

            conteudo_html += """
                    </table>

                    <h2>3. Estatísticas por Cultura</h2>
                    <table>
                        <tr>
                            <th>Cultura</th>
                            <th>Área Total (ha)</th>
                            <th>Área Média (ha)</th>
                            <th>Desvio Padrão da Área</th>
                            <th>Número de Registros</th>
                            <th>Dosagem Média (ml/m)</th>
                            <th>Total de Produto (ml)</th>
                        </tr>
            """

            # Adicionar estatísticas por cultura
            for cultura, dados in estatisticas['por_cultura'].iterrows():
                conteudo_html += f"""
                        <tr>
                            <td>{cultura}</td>
                            <td>{dados['area_sum']:.2f}</td>
                            <td>{dados['area_mean']:.2f}</td>
                            <td>{dados['area_std'] if not pd.isna(dados['area_std']) else 'N/A'}</td>
                            <td>{int(dados['area_count'])}</td>
                            <td>{dados['dosagem_por_metro_mean']:.2f}</td>
                            <td>{dados['total_produto_sum']:.2f}</td>
                        </tr>
                """

            conteudo_html += """
                    </table>

                    <h2>4. Detecção de Valores Atípicos (Outliers)</h2>
                    <table>
                        <tr>
                            <th>Variável</th>
                            <th>Número de Outliers</th>
                            <th>Percentual (%)</th>
                        </tr>
            """

            # Adicionar informações de outliers
            for variavel, dados in outliers.items():
                conteudo_html += f"""
                        <tr>
                            <td>{variavel}</td>
                            <td>{dados['numero_outliers']}</td>
                            <td>{dados['percentual_outliers']:.2f}%</td>
                        </tr>
                """

            conteudo_html += """
                    </table>

                    <h2>5. Visualizações</h2>

                    <h3>5.1. Área por Cultura</h3>
                    <div class="grafico">
                        <img src="{0}" alt="Área por Cultura">
                    </div>

                    <h3>5.2. Total de Produto por Cultura</h3>
                    <div class="grafico">
                        <img src="{1}" alt="Total de Produto por Cultura">
                    </div>

                    <h3>5.3. Relação entre Área e Total de Produto</h3>
                    <div class="grafico">
                        <img src="{2}" alt="Relação entre Área e Total de Produto">
                    </div>

                    <h3>5.4. Distribuição da Área por Cultura</h3>
                    <div class="grafico">
                        <img src="{3}" alt="Distribuição da Área por Cultura">
                    </div>

                    <h3>5.5. Distribuição da Dosagem por Cultura</h3>
                    <div class="grafico">
                        <img src="{4}" alt="Distribuição da Dosagem por Cultura">
                    </div>

                    <h2>6. Conclusões e Recomendações</h2>
                    <div class="info">
                        <p>Com base na análise dos dados, podemos observar:</p>
                        <ul>
                            <li>A cultura com maior área total é a {self.df.groupby('nome')['area'].sum().idxmax()} com {self.df.groupby('nome')['area'].sum().max():.2f} hectares.</li>
                            <li>A cultura que utiliza mais produto é a {self.df.groupby('nome')['total_produto'].sum().idxmax()} com {self.df.groupby('nome')['total_produto'].sum().max():.2f} ml.</li>
                            <li>A correlação entre área e total de produto é de {self.df[['area', 'total_produto']].corr().iloc[0, 1]:.2f}.</li>
                        </ul>

                        <p><strong>Recomendações:</strong></p>
                        <ul>
                            <li>Monitorar o consumo de produto por área para otimizar a utilização de recursos.</li>
                            <li>Verificar dosagens discrepantes que possam indicar erros de aplicação ou registro.</li>
                            <li>Comparar o desempenho das culturas em relação à eficiência do uso de produtos.</li>
                        </ul>
                    </div>

                    <div class="footer">
                        <p>Relatório gerado automaticamente pelo sistema FarmTech Solutions</p>
                        <p>&copy; {datetime.now().year} FarmTech Solutions - Todos os direitos reservados</p>
                    </div>
                </div>
            </body>
            </html>
            """.format(
                os.path.basename(grafico_area),
                os.path.basename(grafico_produto),
                os.path.basename(grafico_dispersao),
                os.path.basename(grafico_boxplot_area),
                os.path.basename(grafico_boxplot_dosagem)
            )

            # Salvar o relatório HTML
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(conteudo_html)

            print(f"\nRelatório de análise completo gerado com sucesso: {nome_arquivo}")
            logging.info(f"Relatório de análise gerado: {nome_arquivo}")

            return nome_arquivo

        except Exception as e:
            logging.error(f"Erro ao gerar relatório completo: {str(e)}")
            print(f"Erro ao gerar relatório completo: {str(e)}")
            return None

def main():
    """Função principal para executar a análise"""
    print("\n" + "="*50)
    print("     FARMTECH SOLUTIONS - ANÁLISE DE DADOS AGRÍCOLAS     ")
    print("="*50)

    analisador = AnalisadorDados()

    # Tentar carregar dados de ambas as fontes
    if os.path.exists('dados_fazenda.csv'):
        fonte = 'dados_fazenda.csv'
    elif os.path.exists('dados_fazenda.json'):
        fonte = 'dados_fazenda.json'
    else:
        print("Nenhum arquivo de dados encontrado.")
        return

    if analisador.carregar_dados(fonte):
        # Menu de opções
        while True:
            print("\nOpções de Análise:")
            print("1. Estatísticas descritivas")
            print("2. Detectar outliers (valores atípicos)")
            print("3. Gráfico de barras")
            print("4. Gráfico de dispersão")
            print("5. Boxplot")
            print("6. Gerar relatório completo")
            print("0. Sair")

            opcao = input("\nEscolha uma opção: ")

            if opcao == '1':
                estatisticas = analisador.estatisticas_descritivas()
                if estatisticas:
                    print("\n=== Estatísticas Gerais ===")
                    for metrica, valor in estatisticas['geral'].items():
                        print(f"{metrica}: {valor:.2f if isinstance(valor, float) else valor}")

                    print("\n=== Estatísticas por Cultura ===")
                    print(tabulate(estatisticas['por_cultura'],
                                  headers='keys',
                                  tablefmt='grid',
                                  floatfmt='.2f'))

            elif opcao == '2':
                outliers = analisador.detectar_outliers()
                if outliers:
                    print("\n=== Detecção de Outliers ===")
                    for variavel, dados in outliers.items():
                        print(f"\nVariável: {variavel}")
                        print(f"Número de outliers: {dados['numero_outliers']}")
                        print(f"Percentual: {dados['percentual_outliers']:.2f}%")
                        if dados['numero_outliers'] > 0:
                            print("Valores atípicos:", dados['valores_outliers'])

            elif opcao == '3':
                print("\n=== Gráfico de Barras ===")
                print("Colunas disponíveis:", ", ".join(analisador.df.columns))

                coluna_x = input("Coluna para eixo X (categórica, ex: nome): ")
                coluna_y = input("Coluna para eixo Y (numérica, ex: area): ")
                titulo = input("Título do gráfico (opcional): ")

                if not titulo:
                    titulo = None

                analisador.plotar_grafico_barras(coluna_x, coluna_y, titulo)

            elif opcao == '4':
                print("\n=== Gráfico de Dispersão ===")
                print("Colunas disponíveis:", ", ".join(analisador.df.columns))

                coluna_x = input("Coluna para eixo X (numérica, ex: area): ")
                coluna_y = input("Coluna para eixo Y (numérica, ex: total_produto): ")
                coluna_cor = input("Coluna para cor dos pontos (categórica, ex: nome, opcional): ")
                titulo = input("Título do gráfico (opcional): ")

                if not coluna_cor:
                    coluna_cor = None
                if not titulo:
                    titulo = None

                analisador.plotar_grafico_dispersao(coluna_x, coluna_y, coluna_cor, titulo)

            elif opcao == '5':
                print("\n=== Boxplot ===")
                print("Colunas disponíveis:", ", ".join(analisador.df.columns))

                coluna_y = input("Coluna para análise (numérica, ex: area): ")
                coluna_grupo = input("Coluna para agrupamento (categórica, ex: nome, opcional): ")
                titulo = input("Título do gráfico (opcional): ")

                if not coluna_grupo:
                    coluna_grupo = None
                if not titulo:
                    titulo = None

                analisador.plotar_grafico_boxplot(coluna_y, coluna_grupo, titulo)

            elif opcao == '6':
                print("\n=== Gerando Relatório Completo ===")
                analisador.gerar_relatorio_completo()

            elif opcao == '0':
                print("\nSaindo da análise. Obrigado por utilizar o FarmTech Solutions!")
                break

            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
