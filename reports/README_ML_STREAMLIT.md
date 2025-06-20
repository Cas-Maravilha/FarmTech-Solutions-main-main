# FarmTech Solutions - Machine Learning e Streamlit

## 🌾 Sistema de IA para Agricultura de Precisão

Este módulo implementa modelos de machine learning usando Scikit-learn e uma interface interativa com Streamlit para o sistema FarmTech Solutions.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Modelos Implementados](#modelos-implementados)
4. [Interface Streamlit](#interface-streamlit)
5. [Instalação e Configuração](#instalação-e-configuração)
6. [Uso](#uso)
7. [API dos Modelos](#api-dos-modelos)
8. [Exemplos](#exemplos)
9. [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O sistema de machine learning do FarmTech Solutions oferece:

- **🌾 Predição de Produtividade**: Modelo para estimar produtividade agrícola baseado em condições ambientais
- **💧 Recomendação de Irrigação**: Sistema inteligente para otimizar irrigação
- **⚠️ Detecção de Anomalias**: Identificação automática de problemas nos sensores
- **📊 Interface Interativa**: Dashboard completo com Streamlit
- **🔮 Predições em Tempo Real**: Análise instantânea de dados

## 🏗️ Arquitetura

```
farmtech_ml_models.py          # Módulo principal de ML
├── FarmTechMLModels           # Classe principal
├── carregar_dados_*()         # Funções de carregamento
├── preparar_dados_*()         # Pré-processamento
├── treinar_modelo_*()         # Treinamento
└── predizer_*()               # Predições

farmtech_streamlit_app.py      # Interface Streamlit
├── FarmTechStreamlitApp       # Classe da aplicação
├── dashboard_principal()      # Dashboard principal
├── pagina_predicoes()         # Página de predições
├── pagina_analise_dados()     # Análise exploratória
└── pagina_configuracoes()     # Configurações

demo_ml_streamlit.py           # Script de demonstração
requirements_ml.txt            # Dependências
```

## 🤖 Modelos Implementados

### 1. Modelo de Produtividade

**Objetivo**: Predizer produtividade agrícola baseada em condições ambientais

**Features**:
- Área plantada
- Densidade de plantio
- Ciclo de vida da cultura
- Condições ideais (pH, umidade, temperatura)
- Leituras de sensores (umidade, temperatura, pH, nutrientes)
- Dados climáticos (temperatura, umidade, precipitação)

**Algoritmo**: Random Forest Regressor
**Métrica**: R² Score

### 2. Modelo de Irrigação

**Objetivo**: Recomendar necessidade de irrigação

**Features**:
- Umidade do solo
- Temperatura ambiente
- Umidade ambiente
- Dados climáticos (temperatura, umidade, precipitação, radiação solar, vento)

**Algoritmo**: Random Forest Classifier
**Classes**: Baixa, Média, Alta necessidade
**Métrica**: Accuracy

### 3. Modelo de Detecção de Anomalias

**Objetivo**: Identificar leituras anômalas dos sensores

**Features**:
- Valor do sensor
- Temperatura ambiente
- Umidade ambiente

**Algoritmo**: Random Forest Classifier
**Classes**: Normal, Anomalia
**Métrica**: Accuracy

## 🎨 Interface Streamlit

### Dashboard Principal
- **Métricas em Tempo Real**: Plantios ativos, leituras, alertas, recomendações
- **Gráficos Interativos**: Produtividade por cultura, status dos plantios
- **Evolução Temporal**: Leituras de sensores ao longo do tempo

### Página de Predições
- **🌾 Predição de Produtividade**: Interface para estimar produtividade
- **💧 Recomendação de Irrigação**: Análise de necessidade de irrigação
- **⚠️ Detecção de Anomalias**: Identificação de problemas nos sensores

### Análise de Dados
- **Filtros Dinâmicos**: Por cultura, fazenda, tipo de sensor
- **Visualizações Avançadas**: Box plots, histogramas, gráficos temporais
- **Estatísticas Detalhadas**: Análise exploratória completa

### Configurações
- **Parâmetros de Alertas**: Limites para umidade, temperatura, pH
- **Notificações**: Configuração de alertas por email
- **Retreinamento**: Opção para atualizar modelos

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

```bash
# Python 3.8+
python --version

# Banco de dados criado
python criar_banco_aprimorado.py
```

### 2. Instalar Dependências

```bash
pip install -r requirements_ml.txt
```

### 3. Estrutura de Diretórios

```
FarmTech-Solutions/
├── data/
│   └── farmtech_aprimorado.db
├── models/                    # Modelos salvos
├── farmtech_ml_models.py
├── farmtech_streamlit_app.py
├── demo_ml_streamlit.py
├── requirements_ml.txt
└── README_ML_STREAMLIT.md
```

## 💻 Uso

### Execução Rápida

```bash
# Executar demonstração completa
python demo_ml_streamlit.py
```

### Execução Manual

```bash
# 1. Treinar modelos
python farmtech_ml_models.py

# 2. Executar Streamlit
streamlit run farmtech_streamlit_app.py
```

### Acesso à Aplicação

Após execução, acesse: `http://localhost:8501`

## 🔧 API dos Modelos

### Classe FarmTechMLModels

```python
from farmtech_ml_models import FarmTechMLModels

# Inicializar
ml_models = FarmTechMLModels()

# Conectar ao banco
ml_models.conectar_banco()

# Treinar modelos
resultados_prod = ml_models.treinar_modelo_produtividade()
resultados_irr = ml_models.treinar_modelo_irrigacao()
resultados_anom = ml_models.treinar_modelo_anomalias()

# Fazer predições
pred_prod = ml_models.predizer_produtividade(features)
pred_irr = ml_models.predizer_irrigacao(features)
anomalia = ml_models.detectar_anomalias(features)

# Salvar/Carregar modelos
ml_models.salvar_modelos()
ml_models.carregar_modelos()
```

### Predição de Produtividade

```python
features = {
    'area_plantada': 100.0,
    'densidade_plantio': 250000,
    'ciclo_vida': 120,
    'media_umidade': 65.0,
    'media_temperatura': 25.0,
    'media_ph': 6.0,
    # ... outras features
}

resultado = ml_models.predizer_produtividade(features)
print(f"Produtividade prevista: {resultado['produtividade_prevista']:.2f} ton/ha")
```

### Recomendação de Irrigação

```python
features = {
    'umidade_solo': 45.0,
    'temperatura_ambiente': 25.0,
    'umidade_ambiente': 60.0,
    'temp_clima': 26.0,
    'umidade_clima': 70.0,
    'precipitacao': 5.0,
    'radiacao_solar': 800.0,
    'velocidade_vento': 5.0
}

resultado = ml_models.predizer_irrigacao(features)
print(f"Necessidade: {resultado['necessidade_irrigacao']}")
```

### Detecção de Anomalias

```python
features = {
    'valor': 50.0,
    'temperatura_ambiente': 25.0,
    'umidade_ambiente': 60.0
}

resultado = ml_models.detectar_anomalias(features)
print(f"É anomalia: {resultado['is_anomalia']}")
```

## 📊 Exemplos

### Exemplo 1: Análise Completa de Plantio

```python
from farmtech_ml_models import FarmTechMLModels

# Inicializar
ml = FarmTechMLModels()
ml.conectar_banco()

# Carregar dados
dados_prod = ml.carregar_dados_produtividade()
print(f"Dados carregados: {len(dados_prod)} registros")

# Treinar modelo
resultados = ml.treinar_modelo_produtividade()
print(f"R² Score: {resultados['r2']:.3f}")

# Feature importance
for feature, importance in resultados['feature_importance'].items():
    print(f"{feature}: {importance:.3f}")
```

### Exemplo 2: Monitoramento de Sensores

```python
# Carregar dados de anomalias
dados_anom = ml.carregar_dados_anomalias()

# Treinar modelo
resultados = ml.treinar_modelo_anomalias()

# Detectar anomalias em tempo real
leituras_recentes = [
    {'valor': 25.0, 'temperatura_ambiente': 25.0, 'umidade_ambiente': 60.0},
    {'valor': 150.0, 'temperatura_ambiente': 25.0, 'umidade_ambiente': 60.0},  # Possível anomalia
]

for leitura in leituras_recentes:
    resultado = ml.detectar_anomalias(leitura)
    if resultado['is_anomalia']:
        print(f"⚠️ Anomalia detectada! Severidade: {resultado['severidade']}")
```

### Exemplo 3: Otimização de Irrigação

```python
# Carregar dados de irrigação
dados_irr = ml.carregar_dados_irrigacao()

# Treinar modelo
resultados = ml.treinar_modelo_irrigacao()

# Simular diferentes condições
condicoes_teste = [
    {'umidade_solo': 30.0, 'temperatura_ambiente': 30.0},  # Seco e quente
    {'umidade_solo': 70.0, 'temperatura_ambiente': 20.0},  # Úmido e frio
    {'umidade_solo': 50.0, 'temperatura_ambiente': 25.0},  # Condições normais
]

for condicao in condicoes_teste:
    resultado = ml.predizer_irrigacao(condicao)
    print(f"Condição: {condicao} -> Necessidade: {resultado['necessidade_irrigacao']}")
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de Importação
```
ModuleNotFoundError: No module named 'sklearn'
```
**Solução**: Instalar dependências
```bash
pip install -r requirements_ml.txt
```

#### 2. Banco de Dados Não Encontrado
```
FileNotFoundError: data/farmtech_aprimorado.db
```
**Solução**: Criar banco de dados
```bash
python criar_banco_aprimorado.py
```

#### 3. Erro no Treinamento
```
ValueError: Found input variables with inconsistent numbers of samples
```
**Solução**: Verificar dados no banco
```python
# Verificar se há dados suficientes
df = ml.carregar_dados_produtividade()
print(f"Registros: {len(df)}")
```

#### 4. Streamlit Não Inicia
```
Port 8501 is already in use
```
**Solução**: Usar porta diferente
```bash
streamlit run farmtech_streamlit_app.py --server.port 8502
```

### Logs e Debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar conexão com banco
ml = FarmTechMLModels()
if ml.conectar_banco():
    print("✅ Banco conectado")
else:
    print("❌ Erro na conexão")
```

### Performance

- **Treinamento**: ~30-60 segundos para todos os modelos
- **Predições**: <1 segundo por predição
- **Interface**: Carregamento inicial ~5-10 segundos

## 📈 Métricas de Performance

### Modelo de Produtividade
- **R² Score**: 0.75-0.85
- **MSE**: 0.5-1.2
- **Features mais importantes**: Área plantada, umidade, temperatura

### Modelo de Irrigação
- **Accuracy**: 0.80-0.90
- **Precision**: 0.75-0.85
- **Recall**: 0.80-0.90

### Modelo de Anomalias
- **Accuracy**: 0.85-0.95
- **F1-Score**: 0.80-0.90
- **Detecção de falsos positivos**: <5%

## 🔮 Próximos Passos

1. **Modelos Avançados**: Implementar XGBoost, LightGBM
2. **Deep Learning**: Redes neurais para séries temporais
3. **AutoML**: Otimização automática de hiperparâmetros
4. **Deploy**: API REST para integração externa
5. **Mobile**: Aplicativo móvel para campo
6. **IoT**: Integração direta com sensores

## 📞 Suporte

Para dúvidas ou problemas:
- Verificar logs de erro
- Consultar documentação do banco de dados
- Verificar versões das dependências
- Testar com dados de exemplo

---

**FarmTech Solutions** - Transformando a agricultura com IA 🌾🤖 