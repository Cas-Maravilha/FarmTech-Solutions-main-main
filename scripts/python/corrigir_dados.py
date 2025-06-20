#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Correção de Dados
Script para corrigir inconsistências nos dados de culturas agrícolas
"""

import os
import json
import csv
import logging
import pandas as pd
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    filename='farmtech.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CorretorDados:
    """Classe para corrigir inconsistências nos dados agrícolas"""

    def __init__(self):
        """Inicializa o corretor de dados"""
        # Garantir que o diretório de backup exista
        if not os.path.exists('backups'):
            os.makedirs('backups')

    def criar_backup(self, arquivo):
        """Cria um backup do arquivo original antes de modificá-lo"""
        if os.path.exists(arquivo):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_base = os.path.basename(arquivo)
            nome_backup = f"backups/{os.path.splitext(nome_base)[0]}_{timestamp}{os.path.splitext(nome_base)[1]}"

            try:
                # Copiar o arquivo para o backup
                with open(arquivo, 'rb') as f_orig:
                    with open(nome_backup, 'wb') as f_backup:
                        f_backup.write(f_orig.read())

                logging.info(f"Backup criado: {nome_backup}")
                print(f"Backup criado: {nome_backup}")
                return True
            except Exception as e:
                logging.error(f"Erro ao criar backup: {str(e)}")
                print(f"Erro ao criar backup: {str(e)}")
                return False
        else:
            logging.warning(f"Arquivo {arquivo} não encontrado para backup")
            return False

    def corrigir_csv(self, arquivo_entrada='dados_fazenda.csv', arquivo_saida=None):
        """Corrige problemas no arquivo CSV"""
        if arquivo_saida is None:
            arquivo_saida = arquivo_entrada

        # Criar backup antes de modificar
        if arquivo_saida == arquivo_entrada:
            self.criar_backup(arquivo_entrada)

        try:
            # Tentar ler com pandas para identificar problemas
            print(f"Lendo arquivo CSV: {arquivo_entrada}")

            # Primeiro, verificar a codificação do arquivo
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(arquivo_entrada, encoding=encoding)
                    print(f"Arquivo lido com sucesso usando codificação {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logging.warning(f"Erro ao ler com {encoding}: {str(e)}")
                    continue

            if df is None:
                raise ValueError("Não foi possível ler o arquivo com nenhuma codificação testada")

            # Normalizar nomes de colunas
            colunas_padrao = ['nome', 'area', 'linhas', 'produto', 'dosagem_por_metro', 'total_produto']

            # Verificar se todas as colunas esperadas existem
            colunas_faltantes = [col for col in colunas_padrao if col not in df.columns]
            if colunas_faltantes:
                logging.warning(f"Colunas faltantes: {colunas_faltantes}")
                print(f"Aviso: Colunas faltantes: {colunas_faltantes}")

            # Corrigir caracteres especiais em nomes
            df['nome'] = df['nome'].apply(lambda x: str(x).replace('�', 'é').strip())

            # Garantir tipos de dados corretos
            df['area'] = pd.to_numeric(df['area'], errors='coerce')
            df['linhas'] = pd.to_numeric(df['linhas'], errors='coerce').astype('Int64')
            df['dosagem_por_metro'] = pd.to_numeric(df['dosagem_por_metro'], errors='coerce')
            df['total_produto'] = pd.to_numeric(df['total_produto'], errors='coerce')

            # Substituir valores NaN por valores padrão
            df['nome'] = df['nome'].fillna('Desconhecido')
            df['area'] = df['area'].fillna(0)
            df['linhas'] = df['linhas'].fillna(0)
            df['produto'] = df['produto'].fillna('Não especificado')
            df['dosagem_por_metro'] = df['dosagem_por_metro'].fillna(0)

            # Verificar se o total_produto está consistente (area * linhas * dosagem)
            df['total_calculado'] = df['area'] * df['linhas'] * df['dosagem_por_metro']

            # Identificar inconsistências no total_produto
            inconsistencias = df[abs(df['total_calculado'] - df['total_produto']) > 0.01]
            if not inconsistencias.empty:
                logging.warning(f"Encontradas {len(inconsistencias)} inconsistências de cálculo")
                print(f"Aviso: Encontradas {len(inconsistencias)} inconsistências de cálculo")

                # Corrigir totais inconsistentes
                print("Corrigindo totais inconsistentes...")
                df['total_produto'] = df['total_calculado']

            # Remover a coluna de total calculado
            df = df.drop('total_calculado', axis=1)

            # Verificar se há registros com valores negativos
            valores_negativos = df[(df['area'] < 0) | (df['linhas'] < 0) | (df['dosagem_por_metro'] < 0) | (df['total_produto'] < 0)]
            if not valores_negativos.empty:
                logging.warning(f"Encontrados {len(valores_negativos)} registros com valores negativos")
                print(f"Aviso: Encontrados {len(valores_negativos)} registros com valores negativos")

                # Remover valores negativos (alternativa: converter para positivos)
                print("Removendo registros com valores negativos...")
                df = df[(df['area'] >= 0) & (df['linhas'] >= 0) & (df['dosagem_por_metro'] >= 0) & (df['total_produto'] >= 0)]

            # Remover duplicatas
            duplicatas = df.duplicated().sum()
            if duplicatas > 0:
                logging.warning(f"Encontradas {duplicatas} linhas duplicadas")
                print(f"Aviso: Encontradas {duplicatas} linhas duplicadas")
                df = df.drop_duplicates()

            # Salvar os dados corrigidos
            print(f"Salvando dados corrigidos em {arquivo_saida}")
            df.to_csv(arquivo_saida, index=False, encoding='utf-8')

            logging.info(f"Arquivo CSV corrigido e salvo em {arquivo_saida}")
            print(f"Arquivo CSV corrigido com sucesso e salvo em {arquivo_saida}")

            # Resumo das correções
            print("\nResumo das correções:")
            print(f"- Arquivo processado: {arquivo_entrada}")
            print(f"- Registros originais: desconhecido")
            print(f"- Registros finais: {len(df)}")
            print(f"- Inconsistências corrigidas: {len(inconsistencias) if 'inconsistencias' in locals() else 0}")
            print(f"- Valores negativos tratados: {len(valores_negativos) if 'valores_negativos' in locals() else 0}")
            print(f"- Duplicatas removidas: {duplicatas}")

            return True

        except Exception as e:
            logging.error(f"Erro ao corrigir arquivo CSV: {str(e)}")
            print(f"Erro ao corrigir arquivo CSV: {str(e)}")
            return False

    def corrigir_json(self, arquivo_entrada='dados_fazenda.json', arquivo_saida=None):
        """Corrige problemas no arquivo JSON"""
        if arquivo_saida is None:
            arquivo_saida = arquivo_entrada

        # Criar backup antes de modificar
        if arquivo_saida == arquivo_entrada:
            self.criar_backup(arquivo_entrada)

        try:
            # Ler o arquivo JSON
            print(f"Lendo arquivo JSON: {arquivo_entrada}")

            # Tentar diferentes codificações
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            dados = None

            for encoding in encodings:
                try:
                    with open(arquivo_entrada, 'r', encoding=encoding) as f:
                        dados = json.load(f)
                    print(f"Arquivo lido com sucesso usando codificação {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except json.JSONDecodeError as e:
                    logging.warning(f"Erro de JSON com {encoding}: {str(e)}")
                    continue
                except Exception as e:
                    logging.warning(f"Erro ao ler com {encoding}: {str(e)}")
                    continue

            if dados is None:
                raise ValueError("Não foi possível ler o arquivo JSON com nenhuma codificação testada")

            # Converter para DataFrame para facilitar as correções
            df = pd.DataFrame(dados)

            # Verificar colunas
            colunas_padrao = ['nome', 'area', 'linhas', 'produto', 'dosagem_por_metro', 'total_produto']
            colunas_faltantes = [col for col in colunas_padrao if col not in df.columns]
            if colunas_faltantes:
                logging.warning(f"Colunas faltantes no JSON: {colunas_faltantes}")
                print(f"Aviso: Colunas faltantes no JSON: {colunas_faltantes}")

                # Adicionar colunas faltantes
                for col in colunas_faltantes:
                    if col == 'nome':
                        df[col] = 'Desconhecido'
                    elif col == 'produto':
                        df[col] = 'Não especificado'
                    else:
                        df[col] = 0

            # Corrigir caracteres especiais
            df['nome'] = df['nome'].apply(lambda x: str(x).replace('�', 'é').strip())

            # Garantir tipos de dados corretos
            df['area'] = pd.to_numeric(df['area'], errors='coerce')
            df['linhas'] = pd.to_numeric(df['linhas'], errors='coerce').astype('Int64')
            df['dosagem_por_metro'] = pd.to_numeric(df['dosagem_por_metro'], errors='coerce')
            df['total_produto'] = pd.to_numeric(df['total_produto'], errors='coerce')

            # Verificar se o total_produto está consistente
            df['total_calculado'] = df['area'] * df['linhas'] * df['dosagem_por_metro']

            # Identificar inconsistências no total_produto
            inconsistencias = df[abs(df['total_calculado'] - df['total_produto']) > 0.01]
            if not inconsistencias.empty:
                logging.warning(f"Encontradas {len(inconsistencias)} inconsistências de cálculo no JSON")
                print(f"Aviso: Encontradas {len(inconsistencias)} inconsistências de cálculo no JSON")

                # Corrigir totais inconsistentes
                print("Corrigindo totais inconsistentes...")
                df['total_produto'] = df['total_calculado']

            # Remover a coluna de total calculado
            df = df.drop('total_calculado', axis=1)

            # Verificar valores negativos
            valores_negativos = df[(df['area'] < 0) | (df['linhas'] < 0) | (df['dosagem_por_metro'] < 0) | (df['total_produto'] < 0)]
            if not valores_negativos.empty:
                logging.warning(f"Encontrados {len(valores_negativos)} registros com valores negativos no JSON")
                print(f"Aviso: Encontrados {len(valores_negativos)} registros com valores negativos no JSON")

                df = df[(df['area'] >= 0) & (df['linhas'] >= 0) & (df['dosagem_por_metro'] >= 0) & (df['total_produto'] >= 0)]

            # Remover duplicatas
            duplicatas = df.duplicated().sum()
            if duplicatas > 0:
                logging.warning(f"Encontradas {duplicatas} linhas duplicadas no JSON")
                print(f"Aviso: Encontradas {duplicatas} linhas duplicadas no JSON")
                df = df.drop_duplicates()

            # Converter DataFrame de volta para lista de dicionários
            dados_corrigidos = df.to_dict(orient='records')

            # Salvar os dados corrigidos
            print(f"Salvando dados JSON corrigidos em {arquivo_saida}")
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(dados_corrigidos, f, indent=4, ensure_ascii=False)

            logging.info(f"Arquivo JSON corrigido e salvo em {arquivo_saida}")
            print(f"Arquivo JSON corrigido com sucesso e salvo em {arquivo_saida}")

            # Resumo das correções
            print("\nResumo das correções no JSON:")
            print(f"- Arquivo processado: {arquivo_entrada}")
            print(f"- Registros originais: {len(dados)}")
            print(f"- Registros finais: {len(dados_corrigidos)}")
            print(f"- Inconsistências corrigidas: {len(inconsistencias) if 'inconsistencias' in locals() else 0}")
            print(f"- Valores negativos tratados: {len(valores_negativos) if 'valores_negativos' in locals() else 0}")
            print(f"- Duplicatas removidas: {duplicatas}")

            return True

        except Exception as e:
            logging.error(f"Erro ao corrigir arquivo JSON: {str(e)}")
            print(f"Erro ao corrigir arquivo JSON: {str(e)}")
            return False

    def sincronizar_dados(self):
        """Sincroniza os dados entre os arquivos CSV e JSON"""
        try:
            print("Sincronizando dados entre arquivos CSV e JSON...")

            # Verificar se ambos os arquivos existem
            csv_existe = os.path.exists('dados_fazenda.csv')
            json_existe = os.path.exists('dados_fazenda.json')

            if not csv_existe and not json_existe:
                logging.error("Nenhum arquivo de dados encontrado para sincronização")
                print("Erro: Nenhum arquivo de dados encontrado")
                return False

            # Priorizar dados do CSV se ambos existirem (geralmente mais atualizado)
            if csv_existe:
                # Ler CSV
                df_csv = pd.read_csv('dados_fazenda.csv')

                # Salvar como JSON
                dados_json = df_csv.to_dict(orient='records')
                with open('dados_fazenda.json', 'w', encoding='utf-8') as f:
                    json.dump(dados_json, f, indent=4, ensure_ascii=False)

                print("Dados CSV convertidos para JSON com sucesso")
                logging.info("Dados sincronizados de CSV para JSON")

            elif json_existe:
                # Ler JSON
                with open('dados_fazenda.json', 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)

                # Converter para DataFrame e salvar como CSV
                df_json = pd.DataFrame(dados_json)
                df_json.to_csv('dados_fazenda.csv', index=False, encoding='utf-8')

                print("Dados JSON convertidos para CSV com sucesso")
                logging.info("Dados sincronizados de JSON para CSV")

            return True

        except Exception as e:
            logging.error(f"Erro ao sincronizar dados: {str(e)}")
            print(f"Erro ao sincronizar dados: {str(e)}")
            return False

def main():
    """Função principal"""
    print("\n" + "="*50)
    print("        FARMTECH SOLUTIONS - CORREÇÃO DE DADOS        ")
    print("="*50)

    corretor = CorretorDados()

    while True:
        print("\nMenu de Correção de Dados:")
        print("1. Corrigir e normalizar arquivo CSV")
        print("2. Corrigir e normalizar arquivo JSON")
        print("3. Sincronizar dados entre CSV e JSON")
        print("4. Corrigir e normalizar ambos os formatos")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            corretor.corrigir_csv()
        elif opcao == '2':
            corretor.corrigir_json()
        elif opcao == '3':
            corretor.sincronizar_dados()
        elif opcao == '4':
            print("\nCorrigindo ambos os formatos...")
            csv_ok = corretor.corrigir_csv()
            json_ok = corretor.corrigir_json()

            if csv_ok and json_ok:
                corretor.sincronizar_dados()
                print("Todos os dados foram corrigidos e sincronizados com sucesso!")
            else:
                print("Alguns erros ocorreram durante o processo. Consulte o log para mais detalhes.")
        elif opcao == '0':
            print("\nSaindo do programa. Obrigado por utilizar o FarmTech Solutions!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
