# FarmTech Solutions - Estrutura Modular Aprimorada

## Visão Geral

O FarmTech Solutions foi reestruturado com uma arquitetura modular moderna, seguindo princípios de Clean Architecture e Separation of Concerns. A nova estrutura oferece melhor organização, manutenibilidade e escalabilidade.

## Estrutura de Diretórios

```
farm_tech/
├── api/                 # API REST endpoints
│   ├── __init__.py
│   ├── routes.py        # Blueprints e rotas da API
│   └── middleware.py    # Middlewares (auth, logging, etc.)
├── core/               # Lógica de negócio
│   ├── __init__.py
│   ├── config.py       # Configuração centralizada
│   ├── logger.py       # Sistema de logging
│   └── services.py     # Serviços de negócio
├── data/               # Camada de dados
│   ├── __init__.py
│   ├── database.py     # Gerenciador de banco de dados
│   └── repositories.py # Repositórios de dados
├── ml/                 # Algoritmos de ML para predições
│   ├── __init__.py
│   ├── predictor.py    # Sistema de predições
│   └── models.py       # Modelos específicos de ML
├── notifications/      # Sistema de alertas
│   ├── __init__.py
│   ├── alert_manager.py # Gerenciador de alertas
│   └── notifiers.py    # Canais de notificação
└── dashboard/          # Interface web
    ├── __init__.py
    ├── app.py          # Aplicação do dashboard
    └── views.py        # Views e templates
```

## Módulos Principais

### 1. API (`farm_tech/api/`)

**Responsabilidades:**
- Endpoints REST da API
- Validação de requisições
- Serialização de respostas
- Middlewares de autenticação e logging

**Principais Componentes:**
- `create_app()`: Factory para criação da aplicação Flask
- Blueprints para diferentes recursos (sensores, leituras, recomendações)
- Middlewares para CORS, rate limiting, logging

**Exemplo de Uso:**
```python
from farm_tech.api import create_app

app = create_app()
app.run(host='0.0.0.0', port=5000)
```

### 2. Core (`farm_tech/core/`)

**Responsabilidades:**
- Lógica de negócio central
- Configuração do sistema
- Serviços principais
- Sistema de logging

**Principais Componentes:**
- `Config`: Configuração centralizada com suporte a variáveis de ambiente
- `SensorService`: Serviço para gerenciamento de sensores
- `RecommendationService`: Serviço para geração de recomendações
- `setup_logging()`: Sistema de logging configurável

**Exemplo de Uso:**
```python
from farm_tech.core import Config, SensorService

config = Config()
sensor_service = SensorService(sensor_repo, reading_repo)
```

### 3. Data (`farm_tech/data/`)

**Responsabilidades:**
- Acesso a dados
- Gerenciamento de banco de dados
- Repositórios de dados
- Migrações e backup

**Principais Componentes:**
- `DatabaseManager`: Gerenciador de conexões e operações de banco
- `SensorRepository`: Repositório para operações com sensores
- `ReadingRepository`: Repositório para operações com leituras
- `AreaRepository`: Repositório para operações com áreas

**Exemplo de Uso:**
```python
from farm_tech.data import DatabaseManager, SensorRepository

db_manager = DatabaseManager(config.get_database_config())
sensor_repo = SensorRepository(db_manager)
```

### 4. ML (`farm_tech/ml/`)

**Responsabilidades:**
- Algoritmos de machine learning
- Predições inteligentes
- Modelos treinados
- Análise de dados

**Principais Componentes:**
- `MLPredictor`: Sistema principal de predições
- `IrrigationPredictor`: Modelo específico para irrigação
- `NutrientPredictor`: Modelo específico para nutrientes
- `DiseasePredictor`: Modelo específico para doenças

**Exemplo de Uso:**
```python
from farm_tech.ml import MLPredictor

predictor = MLPredictor('models/')
prediction = predictor.predict_irrigation_needs(
    humidity=45.0, 
    temperature=28.0,
    soil_type='argiloso'
)
```

### 5. Notifications (`farm_tech/notifications/`)

**Responsabilidades:**
- Sistema de alertas
- Notificações em tempo real
- Múltiplos canais de comunicação
- Gerenciamento de alertas

**Principais Componentes:**
- `AlertManager`: Gerenciador central de alertas
- `EmailNotifier`: Notificações por email
- `SMSNotifier`: Notificações por SMS
- `PushNotifier`: Notificações push

**Exemplo de Uso:**
```python
from farm_tech.notifications import AlertManager

alert_manager = AlertManager(config.get_notification_config())
alert_manager.create_alert(
    AlertType.THRESHOLD_EXCEEDED,
    AlertLevel.WARNING,
    "Umidade Baixa",
    "Umidade do solo está muito baixa"
)
```

### 6. Dashboard (`farm_tech/dashboard/`)

**Responsabilidades:**
- Interface web
- Visualizações em tempo real
- Controle do sistema
- Relatórios

**Principais Componentes:**
- `create_dashboard_app()`: Factory para criação do dashboard
- WebSocket para atualizações em tempo real
- Templates HTML/CSS/JS
- Gráficos e visualizações

**Exemplo de Uso:**
```python
from farm_tech.dashboard import create_dashboard_app

app, socketio = create_dashboard_app(config)
socketio.run(app, host='0.0.0.0', port=5001)
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados
DATABASE_TYPE=sqlite
DATABASE_URL=data/farmtech.db
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=farmtech
DATABASE_USER=root
DATABASE_PASSWORD=

# API
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True
API_SECRET_KEY=your-secret-key

# ML
ML_MODEL_PATH=models/
ML_PREDICTION_THRESHOLD=0.7
ML_RETRAIN_INTERVAL=24

# Notificações
EMAIL_ENABLED=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-password

SMS_ENABLED=False
SMS_PROVIDER=twilio
SMS_ACCOUNT_SID=your-account-sid
SMS_AUTH_TOKEN=your-auth-token

# Alertas
ALERT_UMIDADE_MIN=30.0
ALERT_UMIDADE_MAX=80.0
ALERT_PH_MIN=5.5
ALERT_PH_MAX=7.5
ALERT_NUTRIENTES_MIN=100.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/farmtech.log
```

## Execução

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações
```

### Execução Básica

```bash
# Executar API e Dashboard
python farm_tech_main.py --setup

# Executar apenas API
python farm_tech_main.py --mode api

# Executar apenas Dashboard
python farm_tech_main.py --mode dashboard

# Executar com configurações customizadas
python farm_tech_main.py --host 127.0.0.1 --api-port 8000 --dashboard-port 8001 --debug
```

### Desenvolvimento

```bash
# Executar em modo desenvolvimento
python farm_tech_main.py --debug --setup

# Acessar API: http://localhost:5000
# Acessar Dashboard: http://localhost:5001
```

## Benefícios da Nova Estrutura

### 1. Modularidade
- Cada módulo tem responsabilidades bem definidas
- Fácil manutenção e evolução
- Possibilidade de desenvolvimento paralelo

### 2. Escalabilidade
- Arquitetura preparada para crescimento
- Suporte a múltiplos bancos de dados
- Sistema de cache configurável

### 3. Manutenibilidade
- Código bem organizado e documentado
- Separação clara de responsabilidades
- Testes unitários facilitados

### 4. Flexibilidade
- Configuração via variáveis de ambiente
- Múltiplos canais de notificação
- Suporte a diferentes tipos de sensores

### 5. Robustez
- Sistema de logging centralizado
- Tratamento de erros consistente
- Backup automático de dados

## Migração da Estrutura Anterior

### Arquivos Mantidos
- `api.py` → `farm_tech/api/`
- `sensor_manager.py` → `farm_tech/core/services.py`
- `db_manager.py` → `farm_tech/data/database.py`
- `models/` → `farm_tech/ml/models.py`

### Novos Recursos
- Sistema de notificações completo
- Dashboard web interativo
- Configuração centralizada
- Logging aprimorado
- Suporte a ML avançado

## Próximos Passos

1. **Implementar Templates HTML**: Criar templates para o dashboard
2. **Adicionar Autenticação**: Sistema de login e autorização
3. **Implementar Cache**: Redis para melhor performance
4. **Adicionar Testes**: Testes unitários e de integração
5. **Docker**: Containerização do sistema
6. **CI/CD**: Pipeline de deploy automatizado

## Suporte

Para dúvidas sobre a nova estrutura ou problemas de migração, consulte:
- Documentação da API: `API_DOCUMENTATION.md`
- Guia de Troubleshooting: `TROUBLESHOOTING.md`
- Arquitetura do Sistema: `ARQUITETURA.md` 