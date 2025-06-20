# Sistema de Irrigação Inteligente - FarmTech Solutions

## Visão Geral

O Sistema de Irrigação Inteligente do FarmTech Solutions utiliza **Scikit-learn** para criar modelos preditivos avançados que otimizam automaticamente a irrigação baseada em dados coletados dos sensores. O sistema analisa padrões históricos de umidade, pH e nutrientes para predizer necessidades futuras de irrigação e criar agendas otimizadas.

---

## 🎯 Funcionalidades Principais

### 1. **Predição Inteligente de Irrigação**
- **Modelos ML** treinados com dados históricos
- **Análise de tendências** em tempo real
- **Predição de necessidades** até 24 horas à frente
- **Sistema de confiança** para cada predição

### 2. **Otimização Automática de Agenda**
- **Algoritmos de otimização** baseados em restrições
- **Consideração de recursos** (água, energia, custos)
- **Integração com previsão do tempo**
- **Priorização inteligente** por urgência

### 3. **Análise por Tipo de Cultura**
- **Regras específicas** para milho, soja, trigo
- **Ranges ideais** de umidade, pH e nutrientes
- **Sensibilidade** configurável por cultura
- **Recomendações personalizadas**

---

## 🏗️ Arquitetura do Sistema

### Módulos Principais

```
farm_tech/ml/
├── irrigation_predictor.py    # Preditor ML principal
├── irrigation_optimizer.py    # Otimizador de agenda
└── predictor.py              # Sistema integrado
```

### Fluxo de Dados

```
Sensores → Coleta → Processamento → ML Model → Predição → Otimização → Agenda
   ↓         ↓          ↓           ↓         ↓          ↓          ↓
Dados    Features   Análise     Treinamento  Resultado  Restrições  Execução
```

---

## 🤖 Algoritmos de Machine Learning

### 1. **Preparação de Features**

#### Features Temporais
- **Hora do dia** (seno/cosseno para ciclicidade)
- **Dia da semana** e **mês**
- **Dia do ano** (sazonalidade)

#### Features de Lag
- **Valores anteriores** (1, 2, 3, 6, 12, 24 horas)
- **Diferenças** entre leituras consecutivas
- **Médias móveis** (3, 6, 12, 24 períodos)

#### Features Contextuais
- **Tipo de sensor** (umidade, pH, nutrientes)
- **Área de cultivo** e **cultura**
- **Condições meteorológicas**

### 2. **Modelos Utilizados**

#### Random Forest
```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
```

#### Gradient Boosting
```python
GradientBoostingRegressor(
    n_estimators=100,
    max_depth=6,
    random_state=42
)
```

#### Linear Regression
```python
LinearRegression()
```

### 3. **Validação e Métricas**

- **Validação cruzada** (5 folds)
- **R² Score** para regressão
- **Mean Absolute Error (MAE)**
- **Root Mean Square Error (RMSE)**

---

## 📊 Sistema de Predição

### Criação da Variável Alvo

```python
def create_target_variable(self, features_df, target_horizon=24):
    """Criar target para predição de irrigação"""
    
    # Para umidade: irrigar se < 40% ou tendência decrescente
    if sensor_type == 'umidade':
        irrigation_need = (valor < 40) or (tendencia < -2)
    
    # Para pH: irrigar se fora do range 5.5-7.5
    elif sensor_type == 'ph':
        irrigation_need = (valor < 5.5) or (valor > 7.5)
    
    # Para nutrientes: irrigar se < 150 ppm
    elif sensor_type == 'nutrientes':
        irrigation_need = valor < 150
```

### Interpretação de Predições

| Probabilidade | Ação | Prioridade | Descrição |
|---------------|------|------------|-----------|
| > 0.7 | IRRIGAR IMEDIATAMENTE | ALTA | Alta confiança de necessidade |
| 0.5 - 0.7 | IRRIGAR EM BREVE | MÉDIA | Probabilidade moderada |
| 0.3 - 0.5 | MONITORAR | BAIXA | Baixa probabilidade |
| < 0.3 | NÃO IRRIGAR | NENHUMA | Baixa confiança |

---

## ⚙️ Sistema de Otimização

### Restrições Consideradas

#### Recursos
- **Disponibilidade de água** (litros/dia)
- **Capacidade do sistema** (vazão)
- **Custos** (água + energia)

#### Temporais
- **Intervalo mínimo** entre irrigações (4 horas)
- **Horários ideais** (6h e 18h)
- **Previsão do tempo**

#### Operacionais
- **Prioridade** por urgência
- **Eficiência** por área
- **Manutenção** do sistema

### Algoritmo de Otimização

```python
def optimize_irrigation_schedule(self, predictions, areas_data, weather_forecast):
    """Otimizar agenda de irrigação"""
    
    # 1. Calcular necessidade por área
    area_needs = self._calculate_area_need(predictions)
    
    # 2. Determinar horários ideais
    optimal_times = self._find_optimal_time(weather_forecast)
    
    # 3. Aplicar restrições globais
    schedules = self._global_optimization(schedules, water_availability)
    
    # 4. Gerar agenda final
    return optimized_schedules
```

---

## 🌱 Regras por Cultura

### Milho
```python
crop_rules = {
    'milho': {
        'optimal_moisture': (60, 80),    # 60-80%
        'optimal_ph': (6.0, 7.0),        # 6.0-7.0
        'optimal_nutrients': (150, 250), # 150-250 ppm
        'water_needs': 8.0,              # 8mm/dia
        'sensitivity': 'medium'
    }
}
```

### Soja
```python
crop_rules = {
    'soja': {
        'optimal_moisture': (70, 85),    # 70-85%
        'optimal_ph': (6.0, 6.8),        # 6.0-6.8
        'optimal_nutrients': (120, 200), # 120-200 ppm
        'water_needs': 6.0,              # 6mm/dia
        'sensitivity': 'high'
    }
}
```

### Trigo
```python
crop_rules = {
    'trigo': {
        'optimal_moisture': (65, 75),    # 65-75%
        'optimal_ph': (6.0, 7.5),        # 6.0-7.5
        'optimal_nutrients': (100, 180), # 100-180 ppm
        'water_needs': 5.0,              # 5mm/dia
        'sensitivity': 'medium'
    }
}
```

---

## 🔌 API de Irrigação

### Endpoints Disponíveis

#### 1. Predição de Irrigação
```http
POST /api/irrigation/predict
Content-Type: application/json

{
    "sensor_data": [...],
    "areas_data": [...],
    "weather_forecast": {...},
    "hours_ahead": 24
}
```

#### 2. Criação de Agenda
```http
POST /api/irrigation/schedule
Content-Type: application/json

{
    "predictions": [...],
    "areas_data": [...],
    "weather_forecast": {...},
    "water_availability": 1000
}
```

#### 3. Recomendações
```http
GET /api/irrigation/recommendations?include_irrigation=true
```

#### 4. Status do Modelo
```http
GET /api/irrigation/model/status
```

#### 5. Treinamento
```http
POST /api/irrigation/model/train
Content-Type: application/json

{
    "force_retrain": false
}
```

### Exemplo de Uso

```python
import requests

# Fazer predição
response = requests.post('http://localhost:5000/api/irrigation/predict', json={
    'sensor_data': sensor_readings,
    'areas_data': areas_info,
    'weather_forecast': weather_data
})

predictions = response.json()['predictions']

# Criar agenda otimizada
schedule_response = requests.post('http://localhost:5000/api/irrigation/schedule', json={
    'predictions': predictions,
    'areas_data': areas_info,
    'water_availability': 1000
})

schedule = schedule_response.json()['schedules']
```

---

## 📈 Métricas e Performance

### Indicadores de Qualidade

#### Acurácia do Modelo
- **R² Score**: > 0.8 (excelente)
- **MAE**: < 0.15 (baixo erro)
- **RMSE**: < 0.20 (precisão)

#### Performance Operacional
- **Taxa de acerto**: > 85%
- **Falsos positivos**: < 10%
- **Falsos negativos**: < 5%

#### Eficiência de Recursos
- **Economia de água**: 20-30%
- **Redução de custos**: 15-25%
- **Melhoria de produtividade**: 10-20%

---

## 🛠️ Configuração e Uso

### 1. Instalação de Dependências

```bash
pip install scikit-learn pandas numpy joblib
```

### 2. Inicialização do Sistema

```python
from farm_tech.ml.predictor import create_ml_predictor

# Criar preditor
ml_predictor = create_ml_predictor()

# Inicializar modelos
result = ml_predictor.initialize_models(db_manager)

if result['success']:
    print("Modelos treinados com sucesso!")
```

### 3. Fazer Predições

```python
# Obter dados dos sensores
sensor_data = db_manager.get_recent_readings(hours=24)

# Fazer predição
predictions = ml_predictor.predict_irrigation_needs(
    sensor_data,
    areas_data,
    weather_forecast
)

# Processar resultados
for pred in predictions:
    print(f"Sensor {pred['sensor_id']}: {pred['recommended_action']}")
```

### 4. Executar Demonstração

```bash
python demo_irrigacao_inteligente.py
```

---

## 🔍 Monitoramento e Manutenção

### Logs do Sistema

```python
from farm_tech.core.advanced_logger import log_info, log_error

# Log de predições
log_info('irrigation', f"Predição realizada: {len(predictions)} resultados")

# Log de erros
log_error('irrigation', f"Erro na predição: {error}")
```

### Métricas de Monitoramento

- **Taxa de predições corretas**
- **Tempo de resposta** do modelo
- **Uso de recursos** (CPU, memória)
- **Qualidade dos dados** de entrada

### Atualização de Modelos

```python
# Atualizar com novos dados
result = ml_predictor.update_models(db_manager)

if result['success']:
    print("Modelo atualizado com sucesso!")
```

---

## 🎯 Benefícios do Sistema

### 1. **Eficiência Operacional**
- **Automação** completa da irrigação
- **Otimização** de recursos
- **Redução** de trabalho manual

### 2. **Economia de Recursos**
- **Menor consumo** de água
- **Redução** de custos energéticos
- **Maximização** da produtividade

### 3. **Qualidade da Produção**
- **Condições ideais** para cada cultura
- **Prevenção** de estresse hídrico
- **Melhoria** da qualidade dos produtos

### 4. **Sustentabilidade**
- **Uso racional** da água
- **Redução** do impacto ambiental
- **Agricultura** de precisão

---

## 🚀 Próximos Passos

### 1. **Integrações Avançadas**
- **APIs meteorológicas** em tempo real
- **Sistemas de irrigação** automatizados
- **Plataformas IoT** externas

### 2. **Melhorias de ML**
- **Deep Learning** para predições mais complexas
- **Ensemble methods** para maior precisão
- **Transfer learning** entre culturas

### 3. **Interface Avançada**
- **Dashboard** de monitoramento em tempo real
- **Alertas** proativos via mobile
- **Relatórios** automáticos

### 4. **Escalabilidade**
- **Deploy** em cloud
- **Processamento** distribuído
- **APIs** públicas para integração

---

## 📚 Referências

- **Scikit-learn Documentation**: https://scikit-learn.org/
- **Machine Learning for Agriculture**: Best Practices
- **Irrigation Optimization**: Scientific Papers
- **Precision Agriculture**: Industry Standards

---

## 🤝 Suporte

Para dúvidas ou suporte técnico:
- **Documentação**: `/docs/irrigation.md`
- **Issues**: GitHub Issues
- **Email**: support@farmtech.com

---

*Sistema de Irrigação Inteligente - FarmTech Solutions v1.0*
*Desenvolvido com Scikit-learn e Python* 