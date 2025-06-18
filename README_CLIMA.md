# Módulo Climático FarmTech (R)

![FarmTech Logo](https://via.placeholder.com/150x60/336699/FFFFFF?text=FarmTech)

## Descrição

Este módulo é uma extensão do sistema FarmTech Solutions, desenvolvido em R para conectar-se a APIs meteorológicas públicas, coletar, processar e exibir informações meteorológicas relevantes para a gestão agrícola.

A integração entre dados climáticos e informações de culturas permite a geração de recomendações personalizadas para cada tipo de plantio, melhorando a tomada de decisões operacionais na fazenda.

## Recursos

- Conexão a APIs meteorológicas públicas (OpenWeatherMap)
- Simulação de dados climáticos para fins de teste/demonstração
- Geração de relatórios meteorológicos formatados
- Recomendações específicas por cultura baseadas em condições climáticas
- Integração com o sistema de gestão agrícola FarmTech
- Exportação de relatórios integrados

## Requisitos

- R 4.0 ou superior
- Pacotes R: httr, jsonlite, dplyr, lubridate, crayon

## Instalação

### Instalação Automática

Para instalar R e todas as dependências necessárias, execute o script de instalação como administrador:

```bash
sudo ./instalar_ambiente_r.sh
```

### Instalação Manual

1. Instale o R a partir do site oficial: [R Project](https://www.r-project.org/)
2. Instale os pacotes necessários:

```r
install.packages(c("httr", "jsonlite", "dplyr", "lubridate", "crayon"))
```

## Uso

### Obtendo Dados Meteorológicos

```bash
./clima_api.R
```

O script solicitará:
- Nome da cidade
- Código do país (opcional, padrão: BR)
- Chave da API (opcional para demonstração)

Os dados meteorológicos serão exibidos no terminal e você terá a opção de salvar um relatório.

### Integrando Dados Climáticos com Informações Agrícolas

```bash
./integrar_clima_agricultura.R
```

Este script carrega automaticamente:
- Dados agrícolas do arquivo `dados_fazenda.csv` ou `dados_fazenda.json`
- O relatório meteorológico mais recente (se disponível)

Em seguida, gera recomendações específicas para cada cultura com base nas condições climáticas.

## Exemplo de Saída

### Dados Meteorológicos

```
======================================================================
              DADOS METEOROLÓGICOS: SÃO PAULO - BR
======================================================================

📅 Dados atualizados em: 20/04/2025 12:45

🌡️ Temperatura: 25.0°C (Sensação térmica: 26.0°C)
☀️ Condição: céu limpo
💧 Umidade: 70%
🔄 Pressão atmosférica: 1012 hPa
💨 Vento: 12.6 km/h, direção ESE (120°)
☁️ Cobertura de nuvens: 0%

----------------------------------------------------------------------
       RECOMENDAÇÕES PARA ATIVIDADES AGRÍCOLAS
----------------------------------------------------------------------
✓ Irrigação: Não necessária no momento.
✓ Aplicação de produtos: Condições favoráveis.
✓ Colheita: Condições favoráveis.
✓ Preparo do solo: Condições favoráveis.
```

### Recomendações por Cultura

```
RECOMENDAÇÕES ESPECÍFICAS POR CULTURA
================================================================================
CULTURA      ÁREA (ha)   PRODUTO      RECOMENDAÇÕES
--------------------------------------------------------------------------------
Soja         100.00      fertilizante
  → Irrigação:    Verifique umidade do solo para determinar necessidade de irrigação
  → Aplicação:    Condições adequadas para aplicação de produtos
  → Colheita:     Condições favoráveis para colheita
--------------------------------------------------------------------------------
Café         400.00      fosfato
  → Irrigação:    Verifique umidade do solo para determinar necessidade de irrigação
  → Aplicação:    Condições adequadas para aplicação de produtos
  → Colheita:     Condições favoráveis para colheita
  → ALERTA:       Temperatura acima de 25°C, monitorar necessidade hídrica
--------------------------------------------------------------------------------
```

## Integração com o Sistema FarmTech

Este módulo em R foi projetado para complementar o sistema principal FarmTech Solutions, desenvolvido em Python. A combinação de ambas as tecnologias permite:

1. **Gestão de dados agrícolas** (Python)
2. **Análise estatística avançada** (Python)
3. **Obtenção e processamento de dados climáticos** (R)
4. **Recomendações específicas por cultura** (R)

## Licença

Copyright © 2025 FarmTech Solutions. Todos os direitos reservados.
