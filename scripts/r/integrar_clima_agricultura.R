#!/usr/bin/env Rscript

# FarmTech Solutions - Integração Clima-Agricultura
# Script para integrar dados climáticos com informações agrícolas
# e gerar recomendações específicas para cada cultura

# Instalar pacotes necessários se não estiverem disponíveis
if (!require("jsonlite")) install.packages("jsonlite")
if (!require("dplyr")) install.packages("dplyr")
if (!require("crayon")) install.packages("crayon")

# Carregar bibliotecas
suppressMessages(library(jsonlite))
suppressMessages(library(dplyr))
suppressMessages(library(crayon))

# Diretório com informações climáticas (se existir)
dir_clima <- "relatorios_clima"

# Função para carregar dados agrícolas de CSV
carregar_dados_agricolas <- function(arquivo = "dados_fazenda.csv") {
  if (!file.exists(arquivo)) {
    cat(crayon::red(paste("Erro: Arquivo", arquivo, "não encontrado.\n")))
    return(NULL)
  }

  tryCatch({
    dados <- read.csv(arquivo, stringsAsFactors = FALSE)
    return(dados)
  }, error = function(e) {
    cat(crayon::red(paste("Erro ao carregar arquivo CSV:", e$message, "\n")))
    return(NULL)
  })
}

# Função para carregar dados agrícolas de JSON
carregar_dados_json <- function(arquivo = "dados_fazenda.json") {
  if (!file.exists(arquivo)) {
    cat(crayon::red(paste("Erro: Arquivo", arquivo, "não encontrado.\n")))
    return(NULL)
  }

  tryCatch({
    dados <- fromJSON(arquivo)
    return(dados)
  }, error = function(e) {
    cat(crayon::red(paste("Erro ao carregar arquivo JSON:", e$message, "\n")))
    return(NULL)
  })
}

# Função para obter última previsão climática salva
obter_ultimo_relatorio_clima <- function() {
  if (!dir.exists(dir_clima)) {
    cat(crayon::yellow("Nenhum diretório de relatórios climáticos encontrado.\n"))
    return(NULL)
  }

  arquivos <- list.files(dir_clima, pattern = "clima_.+\\.txt$", full.names = TRUE)
  if (length(arquivos) == 0) {
    cat(crayon::yellow("Nenhum relatório climático encontrado.\n"))
    return(NULL)
  }

  # Ordenar por data de modificação e pegar o mais recente
  info_arquivos <- file.info(arquivos)
  arquivo_mais_recente <- rownames(info_arquivos)[which.max(info_arquivos$mtime)]

  # Extrair informações básicas do relatório climático
  linhas <- readLines(arquivo_mais_recente)

  # Extrair dados básicos
  dados_clima <- list()

  # Cidade e país
  linha_cidade <- grep("Cidade:", linhas, value = TRUE)
  if (length(linha_cidade) > 0) {
    partes <- strsplit(linha_cidade, " - País: ")[[1]]
    dados_clima$cidade <- gsub("Cidade: ", "", partes[1])
    dados_clima$pais <- partes[2]
  }

  # Data/hora
  linha_data <- grep("Data/Hora:", linhas, value = TRUE)
  if (length(linha_data) > 0) {
    dados_clima$data_hora <- gsub("Data/Hora: ", "", linha_data)
  }

  # Temperatura
  linha_temp <- grep("- Temperatura:", linhas, value = TRUE)
  if (length(linha_temp) > 0) {
    dados_clima$temperatura <- as.numeric(gsub("- Temperatura: ([0-9.]+) °C", "\\1", linha_temp))
  }

  # Umidade
  linha_umidade <- grep("- Umidade:", linhas, value = TRUE)
  if (length(linha_umidade) > 0) {
    dados_clima$umidade <- as.numeric(gsub("- Umidade: ([0-9.]+) %", "\\1", linha_umidade))
  }

  # Condição
  linha_condicao <- grep("- Condição:", linhas, value = TRUE)
  if (length(linha_condicao) > 0) {
    dados_clima$condicao <- gsub("- Condição: ", "", linha_condicao)
  }

  # Vento
  linha_vento <- grep("- Vento:", linhas, value = TRUE)
  if (length(linha_vento) > 0) {
    partes_vento <- strsplit(gsub("- Vento: ", "", linha_vento), " km/h, ")[[1]]
    dados_clima$vento_velocidade <- as.numeric(partes_vento[1])
    dados_clima$vento_direcao <- partes_vento[2]
  }

  # Precipitação
  linha_precipitacao <- grep("- Precipitação", linhas, value = TRUE)
  if (length(linha_precipitacao) > 0) {
    dados_clima$precipitacao <- as.numeric(gsub("- Precipitação \\(última hora\\): ([0-9.]+) mm", "\\1", linha_precipitacao))
  } else {
    dados_clima$precipitacao <- 0
  }

  # Nome do arquivo para referência
  dados_clima$arquivo <- arquivo_mais_recente

  return(dados_clima)
}

# Função para determinar recomendações específicas por cultura
gerar_recomendacoes_por_cultura <- function(cultura, area, produto, dados_clima) {
  # Se não temos dados climáticos, retornar mensagem genérica
  if (is.null(dados_clima)) {
    return(list(
      irrigacao = "Sem dados climáticos disponíveis para recomendação",
      aplicacao = "Sem dados climáticos disponíveis para recomendação",
      colheita = "Sem dados climáticos disponíveis para recomendação",
      alerta = "Recomenda-se verificar previsão meteorológica antes de realizar operações"
    ))
  }

  # Valores padrão
  recomendacoes <- list(
    irrigacao = "",
    aplicacao = "",
    colheita = "",
    alerta = ""
  )

  # Converter cultura para minúsculas para comparação
  cultura_lower <- tolower(cultura)

  # Variáveis do clima
  temp <- dados_clima$temperatura
  umidade <- dados_clima$umidade
  condicao <- tolower(dados_clima$condicao)
  precipitacao <- dados_clima$precipitacao
  vento_vel <- dados_clima$vento_velocidade

  # Verificar condições críticas (independente da cultura)
  if (grepl("chuva|tempestade", condicao) || precipitacao > 0) {
    recomendacoes$alerta <- "ALERTA: Condições chuvosas detectadas"
    recomendacoes$irrigacao <- "Não irrigar"
    recomendacoes$aplicacao <- "Não aplicar produtos químicos durante chuva"
  }

  if (vento_vel > 15) {
    recomendacoes$alerta <- paste(recomendacoes$alerta, "| ALERTA: Ventos fortes")
    recomendacoes$aplicacao <- "Não aplicar produtos. Risco de deriva."
  }

  # Recomendações específicas por cultura
  if (grepl("soja", cultura_lower)) {
    # Recomendações para soja
    if (umidade < 50 && temp > 25) {
      recomendacoes$irrigacao <- "Irrigação imediata recomendada. Condições secas podem afetar o desenvolvimento."
    } else if (precipitacao > 3) {
      recomendacoes$irrigacao <- "Irrigação não necessária nos próximos 2-3 dias"
    }

    if (temp > 30) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Alerta de temperatura alta para soja")
    }

    if (grepl("fertilizante", tolower(produto))) {
      if (umidade > 70) {
        recomendacoes$aplicacao <- "Condições úmidas podem aumentar a eficiência do fertilizante"
      } else {
        recomendacoes$aplicacao <- "Em condições secas, aplicar fertilizante mais próximo às raízes"
      }
    }
  }

  else if (grepl("milho", cultura_lower)) {
    # Recomendações para milho
    if (umidade < 45 && temp > 28) {
      recomendacoes$irrigacao <- "Irrigação urgente. Milho em condições muito secas."
    } else if (precipitacao > 4) {
      recomendacoes$irrigacao <- "Irrigação não necessária nos próximos 3-4 dias"
    }

    if (temp > 35) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Alerta de temperatura extrema para milho")
    }

    if (grepl("nitrogênio", tolower(produto))) {
      recomendacoes$aplicacao <- "Aplicar nitrogênio preferencialmente em solo úmido"
    }
  }

  else if (grepl("café", cultura_lower)) {
    # Recomendações para café
    if (umidade < 50 && temp > 25) {
      recomendacoes$irrigacao <- "Irrigação recomendada. Café requer umidade consistente."
    }

    if (temp < 10) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Alerta de temperatura baixa para café")
    }

    if (precipitacao > 0 && grepl("floração", condicao)) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Chuva durante floração pode afetar polinização")
    }
  }

  else if (grepl("algodão", cultura_lower)) {
    # Recomendações para algodão
    if (umidade > 85) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Alta umidade pode favorecer doenças fúngicas em algodão")
    }

    if (precipitacao > 5 && temp > 25) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Condições favoráveis para pragas em algodão")
    }
  }

  else if (grepl("feijão", cultura_lower)) {
    # Recomendações para feijão
    if (umidade < 40) {
      recomendacoes$irrigacao <- "Irrigação necessária. Feijão sensível à seca."
    }

    if (temp > 30) {
      recomendacoes$alerta <- paste(recomendacoes$alerta, "| Temperatura alta pode afetar floração do feijão")
    }
  }

  # Recomendações genéricas para outras culturas
  else {
    if (umidade < 50 && temp > 25) {
      recomendacoes$irrigacao <- "Considere irrigação suplementar"
    } else if (precipitacao > 5) {
      recomendacoes$irrigacao <- "Irrigação provavelmente não necessária"
    }
  }

  # Recomendações de colheita genéricas
  if (umidade > 80 || grepl("chuva|tempestade", condicao)) {
    recomendacoes$colheita <- "Condições desfavoráveis para colheita. Alta umidade."
  } else if (vento_vel > 25) {
    recomendacoes$colheita <- "Ventos fortes podem dificultar operações de colheita"
  } else if (umidade < 70 && !grepl("chuva|tempestade", condicao)) {
    recomendacoes$colheita <- "Condições favoráveis para colheita"
  }

  # Definir valores padrão se estiverem vazios
  if (recomendacoes$irrigacao == "") {
    recomendacoes$irrigacao <- "Verifique umidade do solo para determinar necessidade de irrigação"
  }

  if (recomendacoes$aplicacao == "") {
    if (vento_vel < 10 && !grepl("chuva|tempestade", condicao)) {
      recomendacoes$aplicacao <- "Condições adequadas para aplicação de produtos"
    } else {
      recomendacoes$aplicacao <- "Avaliar condições locais antes de aplicar produtos"
    }
  }

  if (recomendacoes$colheita == "") {
    recomendacoes$colheita <- "Sem recomendações específicas para colheita"
  }

  if (recomendacoes$alerta == "") {
    recomendacoes$alerta <- "Sem alertas especiais para esta cultura"
  }

  return(recomendacoes)
}

# Função para exibir tabela de recomendações
exibir_tabela_recomendacoes <- function(dados_agricolas, dados_clima) {
  if (is.null(dados_agricolas) || nrow(dados_agricolas) == 0) {
    cat(crayon::red("Sem dados agrícolas para analisar.\n"))
    return()
  }

  if (is.null(dados_clima)) {
    cat(crayon::yellow("\nNenhum dado climático disponível. As recomendações serão limitadas.\n"))
  } else {
    cat(crayon::cyan(paste("\nDados climáticos de:", dados_clima$cidade, "em", dados_clima$data_hora, "\n")))
    cat(crayon::cyan(paste("Temperatura:", dados_clima$temperatura, "°C, Umidade:", dados_clima$umidade, "%\n")))
    cat(crayon::cyan(paste("Condição:", dados_clima$condicao, "\n")))
  }

  cat("\n", crayon::bold("RECOMENDAÇÕES ESPECÍFICAS POR CULTURA\n"))
  cat(crayon::bold(paste(rep("=", 80), collapse = "")), "\n")

  # Cabeçalho da tabela
  cat(crayon::bold(sprintf("%-12s %-10s %-12s %-40s\n", "CULTURA", "ÁREA (ha)", "PRODUTO", "RECOMENDAÇÕES")))
  cat(crayon::bold(paste(rep("-", 80), collapse = "")), "\n")

  # Processar cada cultura
  for (i in 1:nrow(dados_agricolas)) {
    cultura <- dados_agricolas$nome[i]
    area <- dados_agricolas$area[i]
    produto <- dados_agricolas$produto[i]

    # Obter recomendações para esta cultura
    recomendacoes <- gerar_recomendacoes_por_cultura(cultura, area, produto, dados_clima)

    # Exibir linha da tabela com informações básicas
    cat(crayon::yellow(sprintf("%-12s ", cultura)),
        sprintf("%-10.2f ", area),
        sprintf("%-12s ", produto), "\n")

    # Exibir recomendações para esta cultura
    cat("  → ", crayon::bold("Irrigação:    "), crayon::blue(recomendacoes$irrigacao), "\n", sep = "")
    cat("  → ", crayon::bold("Aplicação:    "), crayon::magenta(recomendacoes$aplicacao), "\n", sep = "")
    cat("  → ", crayon::bold("Colheita:     "), crayon::green(recomendacoes$colheita), "\n", sep = "")

    # Alertas (se houver)
    if (recomendacoes$alerta != "Sem alertas especiais para esta cultura") {
      cat("  → ", crayon::bold("ALERTA:       "), crayon::red(recomendacoes$alerta), "\n", sep = "")
    }

    # Separador entre culturas
    cat(crayon::bold(paste(rep("-", 80), collapse = "")), "\n")
  }
}

# Função para salvar relatório consolidado
salvar_relatorio_consolidado <- function(dados_agricolas, dados_clima) {
  if (is.null(dados_agricolas) || nrow(dados_agricolas) == 0) {
    cat(crayon::red("Sem dados agrícolas para gerar relatório.\n"))
    return(NULL)
  }

  # Criar diretório se não existir
  if (!dir.exists("relatorios")) {
    dir.create("relatorios")
  }

  # Nome do arquivo
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  nome_arquivo <- sprintf("relatorios/relatorio_integrado_%s.txt", timestamp)

  # Abrir arquivo para escrita
  sink(nome_arquivo)

  # Cabeçalho
  cat("===========================================================\n")
  cat("         RELATÓRIO INTEGRADO FARMTECH SOLUTIONS            \n")
  cat("===========================================================\n\n")

  cat("Data/Hora do relatório:", format(Sys.time(), "%d/%m/%Y %H:%M:%S"), "\n\n")

  # Dados climáticos
  cat("INFORMAÇÕES METEOROLÓGICAS\n")
  cat("-----------------------------------------------------------\n")

  if (!is.null(dados_clima)) {
    cat("Cidade:", dados_clima$cidade, "- País:", dados_clima$pais, "\n")
    cat("Dados atualizados em:", dados_clima$data_hora, "\n\n")
    cat("Temperatura:", dados_clima$temperatura, "°C\n")
    cat("Umidade:", dados_clima$umidade, "%\n")
    cat("Condição:", dados_clima$condicao, "\n")
    cat("Vento:", dados_clima$vento_velocidade, "km/h,", dados_clima$vento_direcao, "\n")

    if (dados_clima$precipitacao > 0) {
      cat("Precipitação (última hora):", dados_clima$precipitacao, "mm\n")
    }
  } else {
    cat("Nenhum dado climático disponível.\n")
  }

  # Dados agrícolas
  cat("\nDADOS AGRÍCOLAS\n")
  cat("-----------------------------------------------------------\n")
  cat("Total de culturas:", nrow(dados_agricolas), "\n")
  cat("Área total cultivada:", sum(dados_agricolas$area), "hectares\n\n")

  # Tabela de culturas
  cat(sprintf("%-12s %-12s %-8s %-12s %-12s %-12s\n",
              "Cultura", "Área (ha)", "Linhas", "Produto", "Dosagem", "Total"))
  cat(paste(rep("-", 70), collapse = ""), "\n")

  for (i in 1:nrow(dados_agricolas)) {
    cat(sprintf("%-12s %-12.2f %-8d %-12s %-12.2f %-12.2f\n",
                dados_agricolas$nome[i],
                dados_agricolas$area[i],
                dados_agricolas$linhas[i],
                dados_agricolas$produto[i],
                dados_agricolas$dosagem_por_metro[i],
                dados_agricolas$total_produto[i]))
  }

  # Recomendações por cultura
  cat("\nRECOMENDAÇÕES POR CULTURA\n")
  cat("-----------------------------------------------------------\n")

  for (i in 1:nrow(dados_agricolas)) {
    cultura <- dados_agricolas$nome[i]
    area <- dados_agricolas$area[i]
    produto <- dados_agricolas$produto[i]

    cat("\nCultura:", cultura, "\n")
    cat("Área:", area, "hectares\n")
    cat("Produto:", produto, "\n")

    # Obter recomendações
    recomendacoes <- gerar_recomendacoes_por_cultura(cultura, area, produto, dados_clima)

    cat("Recomendações:\n")
    cat("- Irrigação: ", recomendacoes$irrigacao, "\n", sep = "")
    cat("- Aplicação: ", recomendacoes$aplicacao, "\n", sep = "")
    cat("- Colheita:  ", recomendacoes$colheita, "\n", sep = "")

    if (recomendacoes$alerta != "Sem alertas especiais para esta cultura") {
      cat("- ALERTA: ", recomendacoes$alerta, "\n", sep = "")
    }
  }

  # Rodapé
  cat("\n-----------------------------------------------------------\n")
  cat("Relatório gerado automaticamente pelo Sistema FarmTech\n")
  cat("Para informações mais detalhadas, consulte a plataforma completa\n")

  # Fechar arquivo
  sink()

  return(nome_arquivo)
}

# Função principal
main <- function() {
  cat(crayon::bold(crayon::green("\nFarmTech Solutions - Integração Clima-Agricultura\n\n")))

  # Tentar carregar dados agrícolas
  dados_agricolas <- NULL

  if (file.exists("dados_fazenda.csv")) {
    cat("Carregando dados agrícolas do CSV...\n")
    dados_agricolas <- carregar_dados_agricolas("dados_fazenda.csv")
  } else if (file.exists("dados_fazenda.json")) {
    cat("Carregando dados agrícolas do JSON...\n")
    dados_agricolas <- carregar_dados_json("dados_fazenda.json")

    # Converter para data frame se for lista
    if (is.list(dados_agricolas) && !is.data.frame(dados_agricolas)) {
      dados_agricolas <- as.data.frame(do.call(rbind, lapply(dados_agricolas, as.data.frame)))
    }
  }

  if (is.null(dados_agricolas) || nrow(dados_agricolas) == 0) {
    cat(crayon::red("Erro: Não foi possível carregar dados agrícolas.\n"))
    cat(crayon::red("Verifique se os arquivos dados_fazenda.csv ou dados_fazenda.json existem.\n"))
    return()
  }

  cat(crayon::green(paste("Dados agrícolas carregados com sucesso:", nrow(dados_agricolas), "culturas encontradas.\n")))

  # Obter último relatório climático
  dados_clima <- obter_ultimo_relatorio_clima()

  # Exibir tabela de recomendações
  exibir_tabela_recomendacoes(dados_agricolas, dados_clima)

  # Perguntar se deseja salvar o relatório
  cat("\nDeseja salvar um relatório consolidado? (s/n): ")
  resposta <- readLines("stdin", n=1)

  if (tolower(resposta) == "s") {
    nome_arquivo <- salvar_relatorio_consolidado(dados_agricolas, dados_clima)
    if (!is.null(nome_arquivo)) {
      cat(crayon::green(paste("\nRelatório salvo com sucesso em:", nome_arquivo, "\n")))
    }
  }

  cat("\nExecute o script clima_api.R para atualizar dados meteorológicos.\n")
}

# Executar a função principal
main()
