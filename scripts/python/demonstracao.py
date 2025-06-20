#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Script de Demonstração
Este script executa uma demonstração automática das principais funcionalidades do sistema
"""

import os
import time
import subprocess
import sys
import random
from datetime import datetime

def esperar(segundos=2):
    """Espera um número específico de segundos"""
    time.sleep(segundos)

def limpar_tela():
    """Limpa a tela do terminal"""
    # Utiliza comando adequado para o sistema operacional
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS
        os.system('clear')

def imprimir_titulo(titulo):
    """Imprime um título formatado"""
    print("\n" + "="*70)
    print(f"{titulo:^70}")
    print("="*70)

def imprimir_subtitulo(subtitulo):
    """Imprime um subtítulo formatado"""
    print("\n" + "-"*70)
    print(f"{subtitulo:^70}")
    print("-"*70)

def demonstrar_dados_base():
    """Demonstra os dados base do sistema"""
    limpar_tela()
    imprimir_titulo("DEMONSTRAÇÃO FARMTECH - DADOS BASE")

    # Verificar se o arquivo CSV existe
    if not os.path.exists('dados_fazenda.csv'):
        print("Criando arquivo de dados de exemplo...")
        # Criar dados de exemplo
        conteudo = """nome,area,linhas,produto,dosagem_por_metro,total_produto
Soja,100.0,2,fertilizante,500.0,100000.0
Café,400.0,4,fosfato,500.0,800000.0
Milho,250.0,3,nitrogênio,400.0,300000.0
Feijão,150.0,2,potássio,300.0,90000.0
Algodão,300.0,3,ureia,450.0,405000.0
"""
        with open('dados_fazenda.csv', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("Arquivo 'dados_fazenda.csv' criado com sucesso!\n")
    else:
        print("Usando arquivo de dados existente: 'dados_fazenda.csv'\n")

    esperar()

    # Mostrar conteúdo do arquivo
    print("Conteúdo do arquivo de dados:")
    print("-"*70)
    with open('dados_fazenda.csv', 'r', encoding='utf-8') as f:
        print(f.read())

    esperar(3)

    print("\nEstes são os dados básicos que o sistema utiliza para análise e gerenciamento.")
    print("Cada linha representa uma cultura com suas características.")
    esperar(3)

def demonstrar_analise_estatistica():
    """Demonstra cálculos estatísticos básicos dos dados"""
    limpar_tela()
    imprimir_titulo("DEMONSTRAÇÃO FARMTECH - ANÁLISE ESTATÍSTICA")

    try:
        import pandas as pd
        import numpy as np

        # Carregar dados
        print("Carregando dados para análise...")
        df = pd.read_csv('dados_fazenda.csv')
        esperar()

        # Mostrar estatísticas básicas
        print("\nResumo estatístico dos dados:")
        print("-"*70)
        print(f"Total de registros: {len(df)}")
        print(f"Culturas únicas: {df['nome'].nunique()}")
        print(f"Área total: {df['area'].sum():.2f} hectares")
        print(f"Área média por cultura: {df['area'].mean():.2f} hectares")
        print(f"Total de produto utilizado: {df['total_produto'].sum():.2f} ml")
        print(f"Média de produto por cultura: {df['total_produto'].mean():.2f} ml")

        esperar(3)

        # Estatísticas por cultura
        print("\nEstatísticas por cultura:")
        print("-"*70)
        por_cultura = df.groupby('nome').agg({
            'area': ['sum', 'mean'],
            'linhas': 'mean',
            'dosagem_por_metro': 'mean',
            'total_produto': 'sum'
        })

        # Simplificar nomes das colunas
        por_cultura.columns = ['area_total', 'area_media', 'linhas_media', 'dosagem_media', 'produto_total']
        por_cultura = por_cultura.reset_index()

        # Mostrar os dados formatados
        for _, row in por_cultura.iterrows():
            print(f"Cultura: {row['nome']}")
            print(f"  - Área total: {row['area_total']:.2f} hectares")
            print(f"  - Área média: {row['area_media']:.2f} hectares")
            print(f"  - Linhas médias: {row['linhas_media']:.2f}")
            print(f"  - Dosagem média: {row['dosagem_media']:.2f} ml/m")
            print(f"  - Total de produto: {row['produto_total']:.2f} ml")
            print()

        esperar(3)

        # Correlação entre área e total de produto
        correlacao = df['area'].corr(df['total_produto'])
        print(f"\nCorrelação entre área e total de produto: {correlacao:.4f}")
        if correlacao > 0.7:
            print("Há uma forte correlação positiva entre a área e o total de produto utilizado.")

        esperar(3)

    except ImportError:
        print("Esta demonstração requer as bibliotecas pandas e numpy.")
        print("Execute 'pip install pandas numpy' para instalar as dependências necessárias.")
    except Exception as e:
        print(f"Erro durante a análise estatística: {str(e)}")

    esperar()

def demonstrar_grafico_simples():
    """Demonstra a criação de um gráfico simples"""
    limpar_tela()
    imprimir_titulo("DEMONSTRAÇÃO FARMTECH - VISUALIZAÇÃO DE DADOS")

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Configurar estilo
        plt.style.use('ggplot')

        # Carregar dados
        print("Carregando dados para visualização...")
        df = pd.read_csv('dados_fazenda.csv')
        esperar()

        print("\nCriando visualizações...")

        # Assegurar que o diretório existe
        if not os.path.exists('demo_graficos'):
            os.makedirs('demo_graficos')

        # Gráfico 1: Área por cultura
        print("\n1. Gráfico de Área por Cultura...")
        plt.figure(figsize=(10, 6))
        sns.barplot(x='nome', y='area', data=df)
        plt.title('Área por Cultura')
        plt.xlabel('Cultura')
        plt.ylabel('Área (hectares)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('demo_graficos/area_por_cultura.png')
        plt.close()

        # Gráfico 2: Total de produto por cultura
        print("2. Gráfico de Total de Produto por Cultura...")
        plt.figure(figsize=(10, 6))
        sns.barplot(x='nome', y='total_produto', data=df)
        plt.title('Total de Produto por Cultura')
        plt.xlabel('Cultura')
        plt.ylabel('Total de Produto (ml)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('demo_graficos/produto_por_cultura.png')
        plt.close()

        # Gráfico 3: Relação entre área e total de produto
        print("3. Gráfico de Relação entre Área e Total de Produto...")
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='area', y='total_produto', hue='nome', size='linhas', data=df)
        plt.title('Relação entre Área e Total de Produto')
        plt.xlabel('Área (hectares)')
        plt.ylabel('Total de Produto (ml)')
        plt.tight_layout()
        plt.savefig('demo_graficos/relacao_area_produto.png')
        plt.close()

        print("\nGráficos criados com sucesso! Salvos no diretório 'demo_graficos'.")
        print("\nOs gráficos fornecem insights visuais sobre os dados agrícolas,")
        print("permitindo identificar padrões, tendências e relações entre as variáveis.")

        esperar(3)

    except ImportError:
        print("Esta demonstração requer as bibliotecas matplotlib e seaborn.")
        print("Execute 'pip install matplotlib seaborn' para instalar as dependências necessárias.")
    except Exception as e:
        print(f"Erro durante a criação de gráficos: {str(e)}")

    esperar()

def demonstrar_correcao_dados():
    """Demonstra a correção de inconsistências nos dados"""
    limpar_tela()
    imprimir_titulo("DEMONSTRAÇÃO FARMTECH - CORREÇÃO DE DADOS")

    # Criar uma cópia com erros proposital para demonstração
    if os.path.exists('dados_fazenda.csv'):
        print("Criando uma cópia dos dados com inconsistências para demonstração...")

        # Ler dados originais
        with open('dados_fazenda.csv', 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        # Criar uma versão com erros
        arquivo_com_erros = 'dados_erros_demo.csv'
        with open(arquivo_com_erros, 'w', encoding='utf-8') as f:
            # Escrever cabeçalho
            f.write(linhas[0])

            # Adicionar linhas com erros
            for i, linha in enumerate(linhas[1:], 1):
                if i == 1:  # Primeira linha: erro no cálculo do total
                    partes = linha.strip().split(',')
                    partes[5] = str(float(partes[5]) * 0.8)  # 80% do valor correto
                    f.write(','.join(partes) + '\n')
                elif i == 2:  # Segunda linha: valor negativo na área
                    partes = linha.strip().split(',')
                    partes[1] = '-' + partes[1]  # Área negativa
                    f.write(','.join(partes) + '\n')
                else:
                    f.write(linha)

            # Adicionar linha duplicada
            if len(linhas) > 1:
                f.write(linhas[1])

        print(f"Arquivo com erros criado: {arquivo_com_erros}\n")
        esperar()

        # Mostrar problemas nos dados
        print("Problemas identificados nos dados:")
        print("-"*70)
        print("1. Inconsistência de cálculo (total_produto != area * linhas * dosagem)")
        print("2. Valores negativos na área")
        print("3. Registros duplicados")

        esperar(3)

        print("\nDetalhes dos problemas:")
        print("-"*70)
        try:
            import pandas as pd
            df = pd.read_csv(arquivo_com_erros)

            # Verificar inconsistências de cálculo
            df['total_calculado'] = df['area'] * df['linhas'] * df['dosagem_por_metro']
            inconsistencias = df[abs(df['total_calculado'] - df['total_produto']) > 0.01]
            print(f"- Inconsistências de cálculo: {len(inconsistencias)} registros")

            # Verificar valores negativos
            negativos = df[df['area'] < 0]
            print(f"- Valores negativos: {len(negativos)} registros")

            # Verificar duplicatas
            duplicatas = df.duplicated().sum()
            print(f"- Duplicatas: {duplicatas} registros")

            esperar(3)

            # Demonstrar correção
            print("\nAplicando correções automáticas...")

            # 1. Corrigir cálculos
            df['total_produto'] = df['total_calculado']
            print("✓ Cálculos corrigidos")

            # 2. Remover negativos
            df = df[df['area'] >= 0]
            print("✓ Valores negativos removidos")

            # 3. Remover duplicatas
            df = df.drop_duplicates()
            print("✓ Duplicatas removidas")

            # Remover coluna temporária
            df = df.drop('total_calculado', axis=1)

            # Salvar arquivo corrigido
            arquivo_corrigido = 'dados_corrigidos_demo.csv'
            df.to_csv(arquivo_corrigido, index=False)
            print(f"\nDados corrigidos salvos em: {arquivo_corrigido}")

            esperar(3)

            print("\nO sistema FarmTech detecta e corrige automaticamente inconsistências,")
            print("garantindo a integridade e qualidade dos dados para análises precisas.")

        except ImportError:
            print("Esta demonstração requer a biblioteca pandas.")
            print("Execute 'pip install pandas' para instalar a dependência necessária.")
        except Exception as e:
            print(f"Erro durante a demonstração de correção: {str(e)}")

    else:
        print("Arquivo de dados 'dados_fazenda.csv' não encontrado.")
        print("Execute a primeira parte da demonstração para criar os dados de exemplo.")

    esperar(3)

def demonstrar_exportacao():
    """Demonstra a exportação de dados em diferentes formatos"""
    limpar_tela()
    imprimir_titulo("DEMONSTRAÇÃO FARMTECH - EXPORTAÇÃO DE DADOS")

    if os.path.exists('dados_fazenda.csv'):
        print("Demonstrando capacidades de exportação do sistema FarmTech...")

        # Criar diretório de saída
        diretorio_saida = 'demo_exportacao'
        if not os.path.exists(diretorio_saida):
            os.makedirs(diretorio_saida)

        try:
            import pandas as pd
            from tabulate import tabulate

            # Carregar dados
            df = pd.read_csv('dados_fazenda.csv')

            # 1. Exportar para TXT
            print("\n1. Exportando para formato TXT...")
            arquivo_txt = f"{diretorio_saida}/relatorio_demo.txt"

            # Calcular estatísticas
            total_area = df['area'].sum()
            total_produto = df['total_produto'].sum()

            with open(arquivo_txt, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write(f"{'RELATÓRIO DE DADOS AGRÍCOLAS - FARMTECH SOLUTIONS':^70}\n")
                f.write(f"{'Gerado em: ' + datetime.now().strftime('%d/%m/%Y %H:%M'):^70}\n")
                f.write("="*70 + "\n\n")

                f.write("RESUMO DOS DADOS\n")
                f.write("-"*70 + "\n")
                f.write(f"Total de registros: {len(df)}\n")
                f.write(f"Número de culturas: {df['nome'].nunique()}\n")
                f.write(f"Área total: {total_area:.2f} hectares\n")
                f.write(f"Total de produto utilizado: {total_produto:.2f} ml\n\n")

                f.write("DADOS DETALHADOS\n")
                f.write("-"*70 + "\n")
                tabela = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
                f.write(tabela + "\n")

            print(f"✓ Relatório TXT gerado: {arquivo_txt}")
            esperar()

            # 2. Exportar para Excel
            try:
                print("\n2. Exportando para formato Excel (XLSX)...")
                arquivo_excel = f"{diretorio_saida}/dados_demo.xlsx"

                # Criar uma planilha com mais informações
                writer = pd.ExcelWriter(arquivo_excel, engine='openpyxl')

                # Planilha de dados brutos
                df.to_excel(writer, sheet_name='Dados_Brutos', index=False)

                # Planilha de estatísticas
                estatisticas = pd.DataFrame({
                    'Métrica': ['Total de Registros', 'Culturas Únicas', 'Área Total (ha)', 'Produto Total (ml)'],
                    'Valor': [len(df), df['nome'].nunique(), total_area, total_produto]
                })
                estatisticas.to_excel(writer, sheet_name='Estatísticas', index=False)

                # Planilha por cultura
                por_cultura = df.groupby('nome').agg({
                    'area': ['sum', 'mean'],
                    'linhas': 'mean',
                    'dosagem_por_metro': 'mean',
                    'total_produto': 'sum'
                })
                por_cultura.columns = ['area_total', 'area_media', 'linhas_media', 'dosagem_media', 'produto_total']
                por_cultura = por_cultura.reset_index()
                por_cultura.to_excel(writer, sheet_name='Por_Cultura', index=False)

                writer.close()
                print(f"✓ Arquivo Excel gerado: {arquivo_excel}")

            except ImportError:
                print("A exportação para Excel requer a biblioteca openpyxl.")
                print("Para habilitar esta funcionalidade, instale: pip install openpyxl")
            except Exception as e:
                print(f"Erro ao exportar para Excel: {str(e)}")

            esperar()

            # 3. Exportar para HTML
            print("\n3. Exportando para formato HTML...")
            arquivo_html = f"{diretorio_saida}/relatorio_demo.html"

            html = f"""<!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Relatório FarmTech - Demonstração</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #336699; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .header {{ background-color: #336699; color: white; padding: 10px; margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Relatório de Dados Agrícolas</h1>
                    <p>FarmTech Solutions - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>

                <h2>Resumo dos Dados</h2>
                <p>Total de registros: {len(df)}</p>
                <p>Número de culturas: {df['nome'].nunique()}</p>
                <p>Área total: {total_area:.2f} hectares</p>
                <p>Total de produto utilizado: {total_produto:.2f} ml</p>

                <h2>Dados Detalhados</h2>
                <table>
                    <tr>
                        {' '.join(f'<th>{col}</th>' for col in df.columns)}
                    </tr>
            """

            # Adicionar linhas da tabela
            for _, row in df.iterrows():
                html += "<tr>"
                for col in df.columns:
                    value = row[col]
                    if isinstance(value, (int, float)):
                        # Formatar números com duas casas decimais
                        html += f"<td>{value:.2f}</td>"
                    else:
                        html += f"<td>{value}</td>"
                html += "</tr>\n"

            html += """
                </table>

                <p><em>Relatório gerado pelo Sistema FarmTech</em></p>
            </body>
            </html>
            """

            with open(arquivo_html, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"✓ Relatório HTML gerado: {arquivo_html}")
            esperar()

            print("\nO sistema FarmTech oferece diversas opções de exportação,")
            print("permitindo compartilhar dados e análises em diferentes formatos")
            print("para atender às necessidades específicas dos usuários.")

        except ImportError:
            print("Esta demonstração requer as bibliotecas pandas e tabulate.")
            print("Execute 'pip install pandas tabulate' para instalar as dependências necessárias.")
        except Exception as e:
            print(f"Erro durante a demonstração de exportação: {str(e)}")

    else:
        print("Arquivo de dados 'dados_fazenda.csv' não encontrado.")
        print("Execute a primeira parte da demonstração para criar os dados de exemplo.")

    esperar(3)

def executar_demonstracao_completa():
    """Executa a demonstração completa do sistema"""
    try:
        # Introdução
        limpar_tela()
        imprimir_titulo("DEMONSTRAÇÃO DO SISTEMA FARMTECH")
        print("\nBem-vindo à demonstração do Sistema FarmTech!")
        print("Esta demonstração apresentará os principais recursos e funcionalidades")
        print("do sistema de gestão agrícola da FarmTech Solutions.")
        print("\nDurante a demonstração, você verá:")
        print("1. Dados Base do Sistema")
        print("2. Análise Estatística")
        print("3. Visualização de Dados")
        print("4. Correção de Inconsistências")
        print("5. Exportação de Dados")

        input("\nPressione ENTER para iniciar a demonstração...")

        # Executar cada parte da demonstração
        demonstrar_dados_base()
        demonstrar_analise_estatistica()
        demonstrar_grafico_simples()
        demonstrar_correcao_dados()
        demonstrar_exportacao()

        # Conclusão
        limpar_tela()
        imprimir_titulo("DEMONSTRAÇÃO CONCLUÍDA")
        print("\nVocê completou a demonstração do Sistema FarmTech!")
        print("\nFuncionalidades demonstradas:")
        print("✓ Gestão de dados agrícolas")
        print("✓ Análise estatística avançada")
        print("✓ Visualização de dados com gráficos")
        print("✓ Detecção e correção de inconsistências")
        print("✓ Exportação em múltiplos formatos")

        print("\nPara utilizar o sistema completo, execute:")
        print(f"  {sys.executable} farmtech_main.py")

        print("\nObrigado por conhecer o Sistema FarmTech!")
        print("FarmTech Solutions - Tecnologia a serviço do agronegócio")

    except KeyboardInterrupt:
        limpar_tela()
        print("\nDemonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro durante a demonstração: {str(e)}")
    finally:
        print("\nFim da demonstração.")

if __name__ == "__main__":
    executar_demonstracao_completa()
