#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Exportação de Dados
Script para exportar dados de culturas em diversos formatos
"""

import os
import json
import csv
import pandas as pd
import logging
from datetime import datetime
import sqlite3
import openpyxl
from tabulate import tabulate

# Configuração de logging
logging.basicConfig(
    filename='farmtech.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExportadorDados:
    """Classe para exportar dados de culturas em diferentes formatos"""

    def __init__(self):
        """Inicializa o exportador de dados"""
        # Garantir que o diretório de exportação exista
        if not os.path.exists('exportacoes'):
            os.makedirs('exportacoes')

        self.df = None
        self.carregar_dados()

    def carregar_dados(self):
        """Carrega os dados para exportação"""
        try:
            # Tentar carregar do CSV primeiro (prioridade)
            if os.path.exists('dados_fazenda.csv'):
                self.df = pd.read_csv('dados_fazenda.csv')
                logging.info("Dados carregados do CSV para exportação")
                print("Dados carregados do CSV com sucesso!")

            # Se não existir CSV, tentar JSON
            elif os.path.exists('dados_fazenda.json'):
                with open('dados_fazenda.json', 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                self.df = pd.DataFrame(dados)
                logging.info("Dados carregados do JSON para exportação")
                print("Dados carregados do JSON com sucesso!")

            else:
                logging.error("Nenhum arquivo de dados encontrado para exportação")
                print("Erro: Nenhum arquivo de dados encontrado (CSV ou JSON)")
                return False

            return True

        except Exception as e:
            logging.error(f"Erro ao carregar dados para exportação: {str(e)}")
            print(f"Erro ao carregar dados: {str(e)}")
            return False

    def exportar_excel(self, arquivo_saida=None):
        """Exporta os dados para formato Excel (XLSX)"""
        if self.df is None:
            print("Nenhum dado disponível para exportação")
            return False

        if arquivo_saida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_saida = f"exportacoes/dados_fazenda_{timestamp}.xlsx"

        try:
            # Criar um escritor do Excel
            writer = pd.ExcelWriter(arquivo_saida, engine='openpyxl')

            # Exportar o DataFrame principal
            self.df.to_excel(writer, sheet_name='Dados_Brutos', index=False)

            # Criar uma planilha com estatísticas
            estatisticas = pd.DataFrame({
                'Métrica': [
                    'Total de Culturas',
                    'Total de Registros',
                    'Área Total (ha)',
                    'Área Média (ha)',
                    'Total de Produto (ml)',
                    'Dosagem Média (ml/m)',
                    'Número Médio de Linhas'
                ],
                'Valor': [
                    self.df['nome'].nunique(),
                    len(self.df),
                    self.df['area'].sum(),
                    self.df['area'].mean(),
                    self.df['total_produto'].sum(),
                    self.df['dosagem_por_metro'].mean(),
                    self.df['linhas'].mean()
                ]
            })
            estatisticas.to_excel(writer, sheet_name='Estatísticas', index=False)

            # Criar uma planilha com dados agrupados por cultura
            por_cultura = self.df.groupby('nome').agg({
                'area': ['sum', 'mean', 'count'],
                'linhas': 'mean',
                'dosagem_por_metro': 'mean',
                'total_produto': 'sum'
            })
            por_cultura.columns = ['_'.join(col).strip() for col in por_cultura.columns.values]
            por_cultura.reset_index(inplace=True)
            por_cultura.to_excel(writer, sheet_name='Por_Cultura', index=False)

            # Salvar o arquivo Excel
            writer.close()

            logging.info(f"Dados exportados para Excel: {arquivo_saida}")
            print(f"Dados exportados com sucesso para Excel: {arquivo_saida}")
            return True

        except Exception as e:
            logging.error(f"Erro ao exportar para Excel: {str(e)}")
            print(f"Erro ao exportar para Excel: {str(e)}")
            return False

    def exportar_sql(self, arquivo_saida=None):
        """Exporta os dados para um banco de dados SQLite"""
        if self.df is None:
            print("Nenhum dado disponível para exportação")
            return False

        if arquivo_saida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_saida = f"exportacoes/fazenda_{timestamp}.db"

        try:
            # Criar conexão com o banco de dados
            conn = sqlite3.connect(arquivo_saida)

            # Exportar o DataFrame para uma tabela
            self.df.to_sql('culturas', conn, if_exists='replace', index=False)

            # Criar tabela de estatísticas
            cursor = conn.cursor()

            # Criar visualização para dados agrupados por cultura
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS culturas_por_nome AS
            SELECT
                nome,
                COUNT(*) as total_registros,
                SUM(area) as area_total,
                AVG(area) as area_media,
                AVG(linhas) as linhas_media,
                AVG(dosagem_por_metro) as dosagem_media,
                SUM(total_produto) as produto_total
            FROM culturas
            GROUP BY nome;
            """)

            # Commit e fechar conexão
            conn.commit()
            conn.close()

            logging.info(f"Dados exportados para SQLite: {arquivo_saida}")
            print(f"Dados exportados com sucesso para SQLite: {arquivo_saida}")

            # Mostrar exemplos de consultas SQL
            print("\nExemplos de consultas SQL que podem ser executadas no banco:")
            print("1. SELECT * FROM culturas;  -- Todos os dados")
            print("2. SELECT * FROM culturas_por_nome;  -- Dados agrupados por cultura")
            print("3. SELECT nome, area, total_produto FROM culturas WHERE area > 100;  -- Filtro por área")

            return True

        except Exception as e:
            logging.error(f"Erro ao exportar para SQLite: {str(e)}")
            print(f"Erro ao exportar para SQLite: {str(e)}")
            return False

    def exportar_html(self, arquivo_saida=None):
        """Exporta os dados para um relatório HTML"""
        if self.df is None:
            print("Nenhum dado disponível para exportação")
            return False

        if arquivo_saida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_saida = f"exportacoes/relatorio_{timestamp}.html"

        try:
            # Criar conteúdo HTML
            html = f"""<!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Relatório de Dados Agrícolas - FarmTech</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2, h3 {{ color: #336699; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .cabecalho {{ background-color: #336699; color: white; padding: 10px; margin-bottom: 20px; }}
                    .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="cabecalho">
                        <h1>Relatório de Dados Agrícolas</h1>
                        <p>FarmTech Solutions - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>

                    <h2>Resumo dos Dados</h2>
                    <p>Total de registros: {len(self.df)}</p>
                    <p>Culturas: {', '.join(self.df['nome'].unique())}</p>
                    <p>Área total: {self.df['area'].sum():.2f} hectares</p>
                    <p>Total de produto utilizado: {self.df['total_produto'].sum():.2f} ml</p>

                    <h2>Dados por Cultura</h2>
                    <table>
                        <tr>
                            <th>Cultura</th>
                            <th>Registros</th>
                            <th>Área Total (ha)</th>
                            <th>Área Média (ha)</th>
                            <th>Linhas Médias</th>
                            <th>Dosagem Média (ml/m)</th>
                            <th>Total Produto (ml)</th>
                        </tr>
            """

            # Agrupar dados por cultura
            por_cultura = self.df.groupby('nome').agg({
                'nome': 'count',
                'area': ['sum', 'mean'],
                'linhas': 'mean',
                'dosagem_por_metro': 'mean',
                'total_produto': 'sum'
            })

            por_cultura.columns = ['_'.join(col).strip() for col in por_cultura.columns.values]
            por_cultura.reset_index(inplace=True)

            # Adicionar linhas da tabela
            for _, row in por_cultura.iterrows():
                html += f"""
                        <tr>
                            <td>{row['nome']}</td>
                            <td>{row['nome_count']}</td>
                            <td>{row['area_sum']:.2f}</td>
                            <td>{row['area_mean']:.2f}</td>
                            <td>{row['linhas_mean']:.2f}</td>
                            <td>{row['dosagem_por_metro_mean']:.2f}</td>
                            <td>{row['total_produto_sum']:.2f}</td>
                        </tr>
                """

            # Adicionar tabela de dados completos
            html += """
                    </table>

                    <h2>Dados Completos</h2>
                    <table>
                        <tr>
                            <th>#</th>
                            <th>Cultura</th>
                            <th>Área (ha)</th>
                            <th>Linhas</th>
                            <th>Produto</th>
                            <th>Dosagem (ml/m)</th>
                            <th>Total (ml)</th>
                        </tr>
            """

            # Adicionar todas as linhas de dados
            for i, row in self.df.iterrows():
                html += f"""
                        <tr>
                            <td>{i+1}</td>
                            <td>{row['nome']}</td>
                            <td>{row['area']:.2f}</td>
                            <td>{row['linhas']}</td>
                            <td>{row['produto']}</td>
                            <td>{row['dosagem_por_metro']:.2f}</td>
                            <td>{row['total_produto']:.2f}</td>
                        </tr>
                """

            # Finalizar HTML
            html += """
                    </table>

                    <div class="footer">
                        <p>Relatório gerado automaticamente pelo sistema FarmTech Solutions</p>
                        <p>&copy; 2025 FarmTech Solutions - Todos os direitos reservados</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Salvar o arquivo HTML
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(html)

            logging.info(f"Relatório HTML exportado: {arquivo_saida}")
            print(f"Relatório HTML exportado com sucesso: {arquivo_saida}")
            return True

        except Exception as e:
            logging.error(f"Erro ao exportar relatório HTML: {str(e)}")
            print(f"Erro ao exportar relatório HTML: {str(e)}")
            return False

    def exportar_para_r(self, arquivo_saida=None):
        """Exporta os dados para um script R"""
        if self.df is None:
            print("Nenhum dado disponível para exportação")
            return False

        if arquivo_saida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_saida = f"exportacoes/analise_r_{timestamp}.R"

        try:
            # Primeiro, exportar os dados como CSV para o R ler
            csv_para_r = f"exportacoes/dados_r_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.df.to_csv(csv_para_r, index=False, encoding='utf-8')

            # Criar o script R
            script_r = f"""# Script de análise para dados agrícolas - FarmTech Solutions
# Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M')}

# Carregar bibliotecas necessárias
if (!require("tidyverse")) install.packages("tidyverse")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("scales")) install.packages("scales")
library(tidyverse)
library(ggplot2)
library(scales)

# Configurar tema para gráficos
theme_set(theme_minimal() +
          theme(plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
                axis.title = element_text(size = 12),
                axis.text = element_text(size = 10)))

# Ler dados
dados <- read.csv("{os.path.basename(csv_para_r)}")
cat("\\nDados carregados com sucesso: ", nrow(dados), "registros\\n")

# Verificar estrutura dos dados
str(dados)

# Estatísticas básicas
cat("\\nEstatísticas Gerais:\\n")
cat("\\nMédia de Área:", mean(dados$area), "hectares\\n")
cat("Desvio Padrão da Área:", sd(dados$area), "hectares\\n")
cat("Média de Dosagem:", mean(dados$dosagem_por_metro), "ml/m\\n")
cat("Total de Produto Utilizado:", sum(dados$total_produto), "ml\\n")

# Análise por cultura
cat("\\nEstatísticas por Cultura:\\n")
estatisticas_cultura <- dados %>%
  group_by(nome) %>%
  summarise(
    registros = n(),
    area_total = sum(area),
    area_media = mean(area),
    area_sd = sd(area),
    linhas_media = mean(linhas),
    dosagem_media = mean(dosagem_por_metro),
    total_produto = sum(total_produto)
  )
print(estatisticas_cultura)

# Gráficos

# 1. Área por Cultura
p1 <- ggplot(dados, aes(x = reorder(nome, -area), y = area, fill = nome)) +
  geom_bar(stat = "identity") +
  labs(title = "Área Total por Cultura",
       x = "Cultura",
       y = "Área (hectares)") +
  scale_y_continuous(labels = comma) +
  theme(legend.position = "none")

# 2. Distribuição de Área por Cultura
p2 <- ggplot(dados, aes(x = nome, y = area, fill = nome)) +
  geom_boxplot() +
  labs(title = "Distribuição de Área por Cultura",
       x = "Cultura",
       y = "Área (hectares)") +
  theme(legend.position = "none")

# 3. Total de Produto por Cultura
p3 <- ggplot(estatisticas_cultura, aes(x = reorder(nome, -total_produto), y = total_produto, fill = nome)) +
  geom_bar(stat = "identity") +
  labs(title = "Total de Produto por Cultura",
       x = "Cultura",
       y = "Total de Produto (ml)") +
  scale_y_continuous(labels = comma) +
  theme(legend.position = "none")

# 4. Relação entre Área e Produto
p4 <- ggplot(dados, aes(x = area, y = total_produto, color = nome)) +
  geom_point(size = 3, alpha = 0.7) +
  geom_smooth(method = "lm", se = TRUE, color = "black") +
  labs(title = "Relação entre Área e Total de Produto",
       x = "Área (hectares)",
       y = "Total de Produto (ml)") +
  scale_x_continuous(labels = comma) +
  scale_y_continuous(labels = comma)

# 5. Dosagem por Cultura
p5 <- ggplot(dados, aes(x = reorder(nome, -dosagem_por_metro), y = dosagem_por_metro, fill = nome)) +
  geom_violin(alpha = 0.7) +
  geom_boxplot(width = 0.1, fill = "white", alpha = 0.7) +
  labs(title = "Distribuição da Dosagem por Cultura",
       x = "Cultura",
       y = "Dosagem (ml/m)") +
  theme(legend.position = "none")

# Criar diretório para salvar gráficos
dir.create("graficos_r", showWarnings = FALSE)

# Salvar gráficos
ggsave("graficos_r/area_por_cultura.png", p1, width = 10, height = 6, dpi = 300)
ggsave("graficos_r/distribuicao_area.png", p2, width = 10, height = 6, dpi = 300)
ggsave("graficos_r/total_produto.png", p3, width = 10, height = 6, dpi = 300)
ggsave("graficos_r/relacao_area_produto.png", p4, width = 10, height = 6, dpi = 300)
ggsave("graficos_r/dosagem_por_cultura.png", p5, width = 10, height = 6, dpi = 300)

# Calcular correlação entre área e total de produto
corr <- cor(dados$area, dados$total_produto)
cat("\\nCorrelação entre Área e Total de Produto:", corr, "\\n")

# Identificação de outliers
calcular_outliers <- function(x) {
  Q1 <- quantile(x, 0.25)
  Q3 <- quantile(x, 0.75)
  IQR <- Q3 - Q1
  limite_inferior <- Q1 - 1.5 * IQR
  limite_superior <- Q3 + 1.5 * IQR
  outliers <- x < limite_inferior | x > limite_superior
  return(sum(outliers))
}

cat("\\nDetecção de Outliers:\\n")
cat("Outliers na área:", calcular_outliers(dados$area), "\\n")
cat("Outliers na dosagem:", calcular_outliers(dados$dosagem_por_metro), "\\n")
cat("Outliers no total de produto:", calcular_outliers(dados$total_produto), "\\n")

# Exportar estatísticas para CSV
write.csv(estatisticas_cultura, "graficos_r/estatisticas_cultura.csv", row.names = FALSE)

cat("\\nAnálise concluída! Gráficos e estatísticas foram salvos no diretório 'graficos_r'\\n")
"""

            # Salvar o script R
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(script_r)

            logging.info(f"Script R exportado: {arquivo_saida}")
            print(f"Script R exportado com sucesso: {arquivo_saida}")
            print(f"Dados para o script exportados em: {csv_para_r}")
            print("\nPara executar a análise em R:")
            print(f"1. Abra o R ou RStudio")
            print(f"2. Defina o diretório de trabalho para a pasta 'exportacoes'")
            print(f"3. Execute o script com: source('{os.path.basename(arquivo_saida)}')")

            return True

        except Exception as e:
            logging.error(f"Erro ao exportar script R: {str(e)}")
            print(f"Erro ao exportar script R: {str(e)}")
            return False

    def exportar_texto(self, arquivo_saida=None):
        """Exporta os dados para um arquivo de texto formatado"""
        if self.df is None:
            print("Nenhum dado disponível para exportação")
            return False

        if arquivo_saida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_saida = f"exportacoes/relatorio_texto_{timestamp}.txt"

        try:
            # Abrir arquivo para escrita
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("="*70 + "\n")
                f.write(f"{'RELATÓRIO DE DADOS AGRÍCOLAS - FARMTECH SOLUTIONS':^70}\n")
                f.write(f"{'Gerado em: ' + datetime.now().strftime('%d/%m/%Y %H:%M'):^70}\n")
                f.write("="*70 + "\n\n")

                # Resumo
                f.write("RESUMO DOS DADOS\n")
                f.write("-"*70 + "\n")
                f.write(f"Total de registros: {len(self.df)}\n")
                f.write(f"Número de culturas: {self.df['nome'].nunique()}\n")
                f.write(f"Área total: {self.df['area'].sum():.2f} hectares\n")
                f.write(f"Total de produto utilizado: {self.df['total_produto'].sum():.2f} ml\n")
                f.write(f"Média de dosagem: {self.df['dosagem_por_metro'].mean():.2f} ml/m\n\n")

                # Estatísticas por cultura
                f.write("ESTATÍSTICAS POR CULTURA\n")
                f.write("-"*70 + "\n")

                por_cultura = self.df.groupby('nome').agg({
                    'area': ['sum', 'mean', 'count'],
                    'linhas': 'mean',
                    'dosagem_por_metro': 'mean',
                    'total_produto': 'sum'
                })

                por_cultura.columns = ['_'.join(col).strip() for col in por_cultura.columns.values]
                por_cultura.reset_index(inplace=True)

                # Gerar tabela formatada com tabulate
                tabela = tabulate(
                    por_cultura,
                    headers=[
                        'Cultura',
                        'Área Total (ha)',
                        'Área Média (ha)',
                        'Registros',
                        'Linhas Médias',
                        'Dosagem Média (ml/m)',
                        'Total Produto (ml)'
                    ],
                    tablefmt="grid",
                    floatfmt=".2f"
                )

                f.write(tabela + "\n\n")

                # Dados completos
                f.write("DADOS COMPLETOS\n")
                f.write("-"*70 + "\n")

                # Preparar dados para tabulate
                dados_tabela = []
                for i, row in self.df.iterrows():
                    dados_tabela.append([
                        i+1,
                        row['nome'],
                        f"{row['area']:.2f}",
                        row['linhas'],
                        row['produto'],
                        f"{row['dosagem_por_metro']:.2f}",
                        f"{row['total_produto']:.2f}"
                    ])

                tabela_completa = tabulate(
                    dados_tabela,
                    headers=['#', 'Cultura', 'Área (ha)', 'Linhas', 'Produto', 'Dosagem (ml/m)', 'Total (ml)'],
                    tablefmt="grid"
                )

                f.write(tabela_completa + "\n\n")

                # Rodapé
                f.write("-"*70 + "\n")
                f.write("Relatório gerado automaticamente pelo sistema FarmTech Solutions\n")
                f.write("© 2025 FarmTech Solutions - Todos os direitos reservados\n")

            logging.info(f"Relatório de texto exportado: {arquivo_saida}")
            print(f"Relatório de texto exportado com sucesso: {arquivo_saida}")
            return True

        except Exception as e:
            logging.error(f"Erro ao exportar relatório de texto: {str(e)}")
            print(f"Erro ao exportar relatório de texto: {str(e)}")
            return False

def main():
    """Função principal"""
    print("\n" + "="*50)
    print("     FARMTECH SOLUTIONS - EXPORTAÇÃO DE DADOS     ")
    print("="*50)

    exportador = ExportadorDados()

    if exportador.df is None:
        print("Não foi possível carregar os dados para exportação. Encerrando programa.")
        return

    while True:
        print("\nMenu de Exportação:")
        print("1. Exportar para Excel (XLSX)")
        print("2. Exportar para banco de dados SQLite")
        print("3. Exportar para relatório HTML")
        print("4. Exportar para script de análise R")
        print("5. Exportar para relatório de texto")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            exportador.exportar_excel()
        elif opcao == '2':
            exportador.exportar_sql()
        elif opcao == '3':
            exportador.exportar_html()
        elif opcao == '4':
            exportador.exportar_para_r()
        elif opcao == '5':
            exportador.exportar_texto()
        elif opcao == '0':
            print("\nSaindo do programa. Obrigado por utilizar o FarmTech Solutions!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
