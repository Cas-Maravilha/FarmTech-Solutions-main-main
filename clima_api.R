#!/usr/bin/env Rscript

# FarmTech Solutions - Módulo Climático em R
# Script para obter, processar e exibir dados meteorológicos
# usando a API pública do OpenWeatherMap

# Instalar pacotes necessários se não estiverem disponíveis
if (!require("httr")) install.packages("httr")
if (!require("jsonlite")) install.packages("jsonlite")
if (!require("dplyr")) install.packages("dplyr")
if (!require("lubridate")) install.packages("lubridate")
if (!require("crayon")) install.packages("crayon")

# Carregar bibliotecas
suppressMessages(library(httr))
suppressMessages(library(jsonlite))
suppressMessages(library(dplyr))
suppressMessages(library(lubridate))
suppressMessages(library(crayon))

# Função para imprimir título formatado
imprimir_titulo <- function(texto) {
  cat("\n", paste(rep("=", 70), collapse = ""), "\n", sep = "")
  cat(paste0(crayon::bold(crayon::blue(sprintf("%s%s%s", paste(rep(" ", (70 - nchar(texto)) / 2), collapse = ""),
                                           texto,
                                           paste(rep(" ", (70 - nchar(texto)) / 2), collapse = "")))), "\n"))
  cat(paste(rep("=", 70), collapse = ""), "\n", sep = "")
}

# Função para imprimir subtítulo formatado
imprimir_subtitulo <- function(texto) {
  cat("\n", paste(rep("-", 70), collapse = ""), "\n", sep = "")
  cat(paste0(crayon::bold(crayon::yellow(sprintf("%s%s%s", paste(rep(" ", (70 - nchar(texto)) / 2), collapse = ""),
                                           texto,
                                           paste(rep(" ", (70 - nchar(texto)) / 2), collapse = "")))), "\n"))
  cat(paste(rep("-", 70), collapse = ""), "\n", sep = "")
}

# Função para converter temperatura de Kelvin para Celsius
kelvin_para_celsius <- function(kelvin) {
  celsius <- kelvin - 273.15
  return(round(celsius, 1))
}

# Função para converter velocidade do vento de m/s para km/h
ms_para_kmh <- function(velocidade_ms) {
  kmh <- velocidade_ms * 3.6
  return(round(kmh, 1))
}

# Função para formatar timestamp em data/hora legível
formatar_timestamp <- function(timestamp) {
  data_hora <- as.POSIXct(timestamp, origin = "1970-01-01")
  return(format(data_hora, "%d/%m/%Y %H:%M"))
}

# Função para obter direção do vento a partir do ângulo
obter_direcao_vento <- function(angulo) {
  direcoes <- c("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N")

  idx <- round(angulo / 22.5) + 1
  return(direcoes[idx])
}

# Função para obter descrição em português do clima
traduzir_descricao_clima <- function(descricao_en) {
  traducoes <- list(
    "clear sky" = "céu limpo",
    "few clouds" = "poucas nuvens",
    "scattered clouds" = "nuvens dispersas",
    "broken clouds" = "nuvens fragmentadas",
    "overcast clouds" = "nublado",
    "light rain" = "chuva leve",
    "moderate rain" = "chuva moderada",
    "heavy rain" = "chuva forte",
    "thunderstorm" = "tempestade",
    "snow" = "neve",
    "mist" = "névoa",
    "fog" = "neblina",
    "drizzle" = "garoa",
    "shower rain" = "aguaceiro"
  )

  # Converter para minúsculas para corresponder às chaves
  descricao_lower <- tolower(descricao_en)

  # Verificar se há tradução exata
  if (descricao_lower %in% names(traducoes)) {
    return(traducoes[[descricao_lower]])
  }

  # Verificar se começa com alguma das chaves
  for (key in names(traducoes)) {
    if (startsWith(descricao_lower, key)) {
      return(traducoes[[key]])
    }
  }

  # Se não encontrar tradução, retorna o original
  return(descricao_en)
}

# Função para obter dados meteorológicos por nome da cidade
obter_dados_clima_por_cidade <- function(cidade, pais = "br", api_key = NULL) {

  # Se não for fornecida uma API key, use uma chamada para dados de amostra
  if (is.null(api_key)) {
    # Simular dados de API apenas para demonstração
    cat(crayon::yellow("AVISO: Usando dados simulados para demonstração. Para dados reais, forneça uma API Key.\n"))
    return(gerar_dados_clima_simulados(cidade, pais))
  }

  # Construir URL da API
  url <- sprintf("https://api.openweathermap.org/data/2.5/weather?q=%s,%s&appid=%s",
                 URLencode(cidade), pais, api_key)

  # Fazer requisição à API
  resposta <- tryCatch({
    GET(url)
  }, error = function(e) {
    cat(crayon::red(paste("Erro ao conectar com a API:", e$message, "\n")))
    return(NULL)
  })

  # Verificar se a requisição foi bem-sucedida
  if (is.null(resposta) || status_code(resposta) != 200) {
    cat(crayon::red(paste("Erro na requisição. Código de status:", status_code(resposta), "\n")))
    conteudo <- content(resposta, "text", encoding = "UTF-8")
    dados_json <- fromJSON(conteudo)
    cat(crayon::red(paste("Mensagem de erro:", dados_json$message, "\n")))
    return(NULL)
  }

  # Converter resposta para JSON
  conteudo <- content(resposta, "text", encoding = "UTF-8")
  dados_json <- fromJSON(conteudo)

  return(dados_json)
}

# Função para gerar dados de clima simulados (quando não há API key)
gerar_dados_clima_simulados <- function(cidade, pais) {
  # Data atual
  agora <- Sys.time()

  # Cidades e suas condições climáticas típicas (para demonstração)
  dados_cidades <- list(
    "São Paulo" = list(temp = 25, umidade = 70, pressao = 1012, vento_vel = 3.5, vento_dir = 120,
                       clima = "poucas nuvens", sensacao = 26),
    "Rio de Janeiro" = list(temp = 30, umidade = 75, pressao = 1010, vento_vel = 4.2, vento_dir = 90,
                            clima = "céu limpo", sensacao = 32),
    "Brasília" = list(temp = 28, umidade = 45, pressao = 1015, vento_vel = 2.8, vento_dir = 45,
                      clima = "céu limpo", sensacao = 27),
    "Curitiba" = list(temp = 18, umidade = 80, pressao = 1018, vento_vel = 5.0, vento_dir = 135,
                      clima = "nublado", sensacao = 16),
    "Salvador" = list(temp = 32, umidade = 85, pressao = 1009, vento_vel = 3.0, vento_dir = 60,
                      clima = "chuva leve", sensacao = 34),
    "Manaus" = list(temp = 33, umidade = 90, pressao = 1008, vento_vel = 2.0, vento_dir = 30,
                    clima = "tempestade", sensacao = 36),
    "Porto Alegre" = list(temp = 22, umidade = 75, pressao = 1014, vento_vel = 6.0, vento_dir = 180,
                          clima = "nuvens dispersas", sensacao = 21)
  )

  # Se a cidade não estiver na lista, use dados aleatórios
  if (!cidade %in% names(dados_cidades)) {
    # Gerar dados aleatórios
    return(list(
      name = cidade,
      sys = list(country = toupper(pais)),
      dt = as.numeric(as.POSIXct(agora)),
      main = list(
        temp = runif(1, 273.15, 303.15),  # 0°C a 30°C em Kelvin
        feels_like = runif(1, 273.15, 303.15),
        pressure = runif(1, 1000, 1020),
        humidity = runif(1, 40, 95)
      ),
      wind = list(
        speed = runif(1, 1, 8),
        deg = runif(1, 0, 359)
      ),
      weather = list(
        list(
          main = sample(c("Clear", "Clouds", "Rain", "Thunderstorm"), 1),
          description = sample(c("clear sky", "few clouds", "scattered clouds",
                                 "light rain", "moderate rain", "heavy rain"), 1)
        )
      ),
      clouds = list(all = runif(1, 0, 100)),
      rain = if (runif(1) > 0.5) list(`1h` = runif(1, 0, 10)) else NULL
    ))
  }

  # Usar dados da cidade específica
  dados_cidade <- dados_cidades[[cidade]]

  return(list(
    name = cidade,
    sys = list(country = toupper(pais)),
    dt = as.numeric(as.POSIXct(agora)),
    main = list(
      temp = dados_cidade$temp + 273.15,  # Converter para Kelvin
      feels_like = dados_cidade$sensacao + 273.15,
      pressure = dados_cidade$pressao,
      humidity = dados_cidade$umidade
    ),
    wind = list(
      speed = dados_cidade$vento_vel,
      deg = dados_cidade$vento_dir
    ),
    weather = list(
      list(
        main = "Weather",
        description = dados_cidade$clima
      )
    ),
    clouds = list(all = if (dados_cidade$clima %in% c("céu limpo")) 0 else runif(1, 10, 100)),
    rain = if (grepl("chuva|tempestade", dados_cidade$clima))
      list(`1h` = runif(1, 1, 10)) else NULL
  ))
}

# Função para processar e exibir dados meteorológicos
exibir_dados_meteorologicos <- function(dados) {
  # Extrair e processar dados relevantes
  cidade <- dados$name
  pais <- dados$sys$country

  # Processar dados principais
  temperatura <- kelvin_para_celsius(dados$main$temp)
  sensacao_termica <- kelvin_para_celsius(dados$main$feels_like)
  umidade <- dados$main$humidity
  pressao <- dados$main$pressure

  # Processar dados de vento
  vento_velocidade <- ms_para_kmh(dados$wind$speed)
  vento_direcao_graus <- dados$wind$deg
  vento_direcao <- obter_direcao_vento(vento_direcao_graus)

  # Processar dados de tempo
  if (length(dados$weather) > 0) {
    tempo_geral <- dados$weather[[1]]$main
    tempo_descricao <- traduzir_descricao_clima(dados$weather[[1]]$description)
  } else {
    tempo_geral <- "Desconhecido"
    tempo_descricao <- "Informação não disponível"
  }

  # Processar nuvens
  cobertura_nuvens <- if (!is.null(dados$clouds$all)) dados$clouds$all else 0

  # Processar chuva (se disponível)
  precipitacao_1h <- if (!is.null(dados$rain) && !is.null(dados$rain$`1h`)) {
    dados$rain$`1h`
  } else {
    0
  }

  # Obter data/hora da medição
  data_hora_medicao <- formatar_timestamp(dados$dt)

  # Exibir dados formatados
  imprimir_titulo(paste("DADOS METEOROLÓGICOS:", toupper(cidade), "-", pais))

  cat("\n", crayon::cyan("📅 Dados atualizados em:"), data_hora_medicao, "\n\n")

  # Temperatura
  cat(crayon::red(crayon::bold("🌡️ Temperatura: ")), crayon::red(temperatura), "°C",
      " (Sensação térmica: ", crayon::red(sensacao_termica), "°C)", "\n", sep = "")

  # Condições do tempo
  emoji_clima <- switch(tolower(tempo_geral),
                       "clear" = "☀️",
                       "clouds" = "☁️",
                       "rain" = "🌧️",
                       "drizzle" = "🌦️",
                       "thunderstorm" = "⛈️",
                       "snow" = "❄️",
                       "mist" = "🌫️",
                       "🌤️")  # Padrão

  cat(emoji_clima, " ", crayon::bold("Condição: "),
      crayon::bold(crayon::blue(tempo_descricao)), "\n", sep = "")

  # Umidade
  cat("💧 ", crayon::bold("Umidade: "),
      if (umidade > 70) crayon::blue(umidade) else crayon::yellow(umidade),
      "%\n", sep = "")

  # Pressão
  cat("🔄 ", crayon::bold("Pressão atmosférica: "), pressao, " hPa\n", sep = "")

  # Vento
  emoji_vento <- if (vento_velocidade > 20) "🌪️" else "💨"
  cor_vento <- if (vento_velocidade > 30) crayon::red else if (vento_velocidade > 15) crayon::yellow else crayon::green

  cat(emoji_vento, " ", crayon::bold("Vento: "),
      cor_vento(vento_velocidade), " km/h, direção ", vento_direcao,
      " (", vento_direcao_graus, "°)", "\n", sep = "")

  # Cobertura de nuvens
  cat("☁️ ", crayon::bold("Cobertura de nuvens: "), cobertura_nuvens, "%\n", sep = "")

  # Precipitação (se houver)
  if (precipitacao_1h > 0) {
    cat("🌧️ ", crayon::bold("Precipitação (última hora): "),
        crayon::blue(precipitacao_1h), " mm\n", sep = "")
  }

  # Recomendações agrícolas baseadas no clima
  imprimir_subtitulo("RECOMENDAÇÕES PARA ATIVIDADES AGRÍCOLAS")

  # Irrigação
  if (precipitacao_1h > 5) {
    cat(crayon::green("✓ Irrigação: Não necessária. Chuva recente suficiente.\n"))
  } else if (umidade < 50 && temperatura > 25) {
    cat(crayon::red("⚠ Irrigação: Recomendada imediatamente. Condições secas detectadas.\n"))
  } else if (umidade < 70) {
    cat(crayon::yellow("⚙ Irrigação: Considere irrigar nas próximas 24 horas.\n"))
  } else {
    cat(crayon::green("✓ Irrigação: Não necessária no momento.\n"))
  }

  # Aplicação de produtos
  if (vento_velocidade > 15) {
    cat(crayon::red("⚠ Aplicação de produtos: Não recomendada. Ventos fortes podem causar deriva.\n"))
  } else if (grepl("chuva|tempestade", tempo_descricao) || precipitacao_1h > 0) {
    cat(crayon::red("⚠ Aplicação de produtos: Não recomendada. Risco de lavagem pela chuva.\n"))
  } else {
    cat(crayon::green("✓ Aplicação de produtos: Condições favoráveis.\n"))
  }

  # Colheita
  if (grepl("chuva|tempestade", tempo_descricao) || precipitacao_1h > 0 || umidade > 85) {
    cat(crayon::red("⚠ Colheita: Não recomendada. Umidade elevada pode afetar a qualidade.\n"))
  } else {
    cat(crayon::green("✓ Colheita: Condições favoráveis.\n"))
  }

  # Preparo do solo
  if (grepl("chuva forte|tempestade", tempo_descricao) || precipitacao_1h > 10) {
    cat(crayon::red("⚠ Preparo do solo: Não recomendado. Solo excessivamente úmido.\n"))
  } else if (umidade < 30) {
    cat(crayon::yellow("⚙ Preparo do solo: Solo muito seco. Pode dificultar operações.\n"))
  } else {
    cat(crayon::green("✓ Preparo do solo: Condições favoráveis.\n"))
  }

  cat("\n", crayon::silver("Nota: As recomendações são baseadas apenas em dados meteorológicos e devem ser\nconsideradas juntamente com as condições específicas da lavoura e do solo.\n"), sep = "")
}

# Função principal
main <- function() {
  cat(crayon::bold(crayon::green("\nFarmTech Solutions - Módulo Climático em R\n")))

  # Verificar se há argumentos de linha de comando
  args <- commandArgs(trailingOnly = TRUE)

  # Definir cidade padrão
  cidade <- "São Paulo"

  # Se fornecido um argumento, use como nome da cidade
  if (length(args) > 0) {
    cidade <- args[1]
  } else {
    cat("Digite o nome da cidade (ou pressione Enter para usar São Paulo): ")
    entrada <- readLines("stdin", n=1)
    if (nchar(entrada) > 0) {
      cidade <- entrada
    }
  }

  # Solicitar país (opcional)
  cat("Digite o código do país (ou pressione Enter para usar BR): ")
  pais <- readLines("stdin", n=1)
  if (nchar(pais) == 0) {
    pais <- "br"
  }

  # Verificar se deseja usar API key
  cat("Deseja usar uma chave de API real? (s/n): ")
  usar_api_key <- readLines("stdin", n=1)

  api_key <- NULL
  if (tolower(usar_api_key) == "s") {
    cat("Digite sua chave de API do OpenWeatherMap: ")
    api_key <- readLines("stdin", n=1)
  }

  # Obter e exibir dados meteorológicos
  dados_clima <- obter_dados_clima_por_cidade(cidade, pais, api_key)

  if (!is.null(dados_clima)) {
    exibir_dados_meteorologicos(dados_clima)

    # Perguntar se deseja salvar relatório
    cat("\nDeseja salvar este relatório? (s/n): ")
    salvar <- readLines("stdin", n=1)

    if (tolower(salvar) == "s") {
      # Criar diretório se não existir
      if (!dir.exists("relatorios_clima")) {
        dir.create("relatorios_clima")
      }

      # Nome do arquivo com timestamp
      timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
      nome_arquivo <- sprintf("relatorios_clima/clima_%s_%s.txt",
                              gsub(" ", "_", tolower(cidade)), timestamp)

      # Redirecionar saída para um arquivo
      sink(nome_arquivo)
      cat("RELATÓRIO METEOROLÓGICO - FARMTECH SOLUTIONS\n")
      cat("=============================================\n")
      cat("Cidade:", cidade, "- País:", toupper(pais), "\n")
      cat("Data/Hora:", format(Sys.time(), "%d/%m/%Y %H:%M:%S"), "\n\n")

      # Dados básicos sem formatação colorida
      temperatura <- kelvin_para_celsius(dados_clima$main$temp)
      sensacao_termica <- kelvin_para_celsius(dados_clima$main$feels_like)
      umidade <- dados_clima$main$humidity
      pressao <- dados_clima$main$pressure
      vento_velocidade <- ms_para_kmh(dados_clima$wind$speed)
      vento_direcao <- obter_direcao_vento(dados_clima$wind$deg)
      tempo_descricao <- traduzir_descricao_clima(dados_clima$weather[[1]]$description)

      cat("CONDIÇÕES ATUAIS:\n")
      cat("- Temperatura:", temperatura, "°C\n")
      cat("- Sensação térmica:", sensacao_termica, "°C\n")
      cat("- Condição:", tempo_descricao, "\n")
      cat("- Umidade:", umidade, "%\n")
      cat("- Pressão:", pressao, "hPa\n")
      cat("- Vento:", vento_velocidade, "km/h,", vento_direcao, "\n")

      if (!is.null(dados_clima$rain) && !is.null(dados_clima$rain$`1h`)) {
        cat("- Precipitação (última hora):", dados_clima$rain$`1h`, "mm\n")
      }

      cat("\nRECOMENDAÇÕES AGRÍCOLAS:\n")

      # Recomendações sem formatação
      if (!is.null(dados_clima$rain) && !is.null(dados_clima$rain$`1h`) && dados_clima$rain$`1h` > 5) {
        cat("- Irrigação: Não necessária. Chuva recente suficiente.\n")
      } else if (umidade < 50 && temperatura > 25) {
        cat("- Irrigação: Recomendada imediatamente. Condições secas detectadas.\n")
      } else {
        cat("- Irrigação: Verificar condições do solo.\n")
      }

      cat("\nRelatório gerado automaticamente pelo Sistema FarmTech\n")
      sink()

      cat("\nRelatório salvo em:", nome_arquivo, "\n")
    }
  } else {
    cat(crayon::red("Não foi possível obter dados meteorológicos.\n"))
  }
}

# Executar função principal
main()
