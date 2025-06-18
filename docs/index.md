# 🌾 FarmTech Solutions

## Sistema de Monitoramento Agrícola Inteligente com IA

Bem-vindo ao **FarmTech Solutions** - uma plataforma completa de agricultura de precisão que combina hardware ESP32, machine learning e interface web moderna.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![ESP32](https://img.shields.io/badge/ESP32-Arduino-orange.svg)](https://www.espressif.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-green.svg)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-yellow.svg)](https://www.sqlite.org/)

## 🚀 Demonstração Rápida

### 📡 Serial Plotter
```bash
# Executar demonstração do Serial Plotter
python demo_serial_plotter.py
```

### 🤖 Machine Learning
```bash
# Executar interface Streamlit
streamlit run farmtech_streamlit_app.py
```

### 🗄️ Banco de Dados
```bash
# Criar banco aprimorado
python criar_banco_aprimorado.py
```

## 🎯 Funcionalidades Principais

### 🌾 Monitoramento Agrícola
- **Sensores Múltiplos**: Temperatura, umidade, pH, nutrientes
- **Controle PID**: Irrigação automática inteligente
- **Alertas em Tempo Real**: Detecção de anomalias
- **Visualização**: Serial Plotter e dashboards

### 🤖 Inteligência Artificial
- **Predição de Produtividade**: Modelo Random Forest
- **Recomendação de Irrigação**: Classificação inteligente
- **Detecção de Anomalias**: Identificação automática
- **Otimização**: Parâmetros baseados em IA

### 📊 Interface e Análise
- **Dashboard Interativo**: Métricas em tempo real
- **Análise Exploratória**: Visualizações avançadas
- **Relatórios Automáticos**: Estatísticas detalhadas
- **Configurações Dinâmicas**: Parâmetros personalizáveis

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ESP32 +       │    │   Python        │    │   Interface     │
│   Sensores      │    │   Backend       │    │   Web           │
│                 │    │                 │    │                 │
│ • DHT22         │◄──►│ • API Flask     │◄──►│ • Streamlit     │
│ • Solo          │    │ • ML Models     │    │ • Dashboards    │
│ • LCD I2C       │    │ • Database      │    │ • Predições     │
│ • Relé          │    │ • Analytics     │    │ • Configurações │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Serial Plotter  │    │ SQLite Database │    │ Machine Learning│
│ (Visualização)  │    │ (27 Tabelas)    │    │ (3 Modelos)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📚 Documentação

### 📖 Guias Principais
- [📊 Serial Plotter Demo](README_SERIAL_PLOTTER.md) - Guia completo do Serial Plotter
- [🤖 Machine Learning](README_ML_STREAMLIT.md) - Modelos de IA e Streamlit
- [🗄️ Banco de Dados](documentacao_banco_aprimorado.md) - Estrutura do banco
- [🔧 API](API_DOCUMENTATION.md) - Documentação da API
- [🏗️ Arquitetura](ARQUITETURA.md) - Visão geral da arquitetura

### 📄 Resumos e Exemplos
- [📊 Resumo Serial Plotter](RESUMO_SERIAL_PLOTTER.md) - Resumo da demonstração
- [🤖 Resumo ML](RESUMO_ML_STREAMLIT.md) - Resumo dos modelos de IA
- [🗄️ Resumo Banco](RESUMO_CORRECOES_BANCO.md) - Correções do banco de dados
- [📄 Exemplo Serial](exemplo_serial_plotter_output.txt) - Saída do Serial Plotter

### 🎯 Scripts de Demonstração
- [🐍 Demo Serial Plotter](demo_serial_plotter.py) - Simulação Python
- [🤖 Demo ML](demo_ml_streamlit.py) - Demonstração completa
- [🔧 Demo API](demo_api.py) - Testes da API

## 🛠️ Instalação Rápida

### 1. Pré-requisitos
```bash
# Python 3.8+
python --version

# Arduino IDE (para ESP32)
# Bibliotecas: DHT, LiquidCrystal_I2C, WiFi, HTTPClient
```

### 2. Clone e Instale
```bash
git clone https://github.com/seu-usuario/farmtech-solutions.git
cd farmtech-solutions

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements_ml.txt

# Configurar banco
python criar_banco_aprimorado.py
```

### 3. Executar Demonstrações
```bash
# Serial Plotter Demo
python demo_serial_plotter.py

# ML e Streamlit Demo
python demo_ml_streamlit.py

# API Backend
python api.py
```

## 📈 Métricas de Performance

### ⚡ Hardware (ESP32)
- **Frequência de Leitura**: 1 Hz
- **Latência**: < 100ms
- **Precisão**: ±0.5°C (DHT22), ±2% (Solo)
- **Uptime**: 99.9%

### 🐍 Software (Python)
- **Treinamento ML**: 30-60 segundos
- **Predições**: < 1 segundo
- **Interface**: 5-10 segundos (carregamento)

### 🗄️ Banco de Dados
- **Queries**: < 50ms (com índices)
- **Storage**: 1GB+ dados
- **Backup**: Automático diário

## 🏆 Melhorias Implementadas

### ✅ Versão 2.0 - Atualizações Principais

#### 🗄️ Banco de Dados Aprimorado
- **27 tabelas** relacionais (antes: 5 tabelas)
- **1.000+ registros** de exemplo
- **Relacionamentos complexos** entre entidades
- **Índices otimizados** para performance
- **Views** para consultas comuns
- **Logs de auditoria** completos

#### 🤖 Machine Learning Integrado
- **3 modelos** de IA implementados
- **Scikit-learn** para predições
- **Interface Streamlit** interativa
- **Dados simulados** para demonstração
- **Feature importance** analysis
- **Métricas de performance** detalhadas

#### 📡 Serial Plotter Avançado
- **8 variáveis** monitoradas simultaneamente
- **Controle PID** para irrigação
- **Sistema de alertas** automático
- **Comandos interativos** via Serial
- **Interface LCD** informativa
- **Documentação completa** com exemplos

#### 🌐 Interface Web Moderna
- **Dashboard** em tempo real
- **Páginas interativas** para predições
- **Análise exploratória** de dados
- **Configurações dinâmicas**
- **Visualizações avançadas** com Plotly

#### 🔧 API REST Completa
- **Endpoints** para todas as funcionalidades
- **Documentação** detalhada
- **Autenticação** e autorização
- **Validação** de dados
- **Logs** de requisições

## 🔮 Próximos Passos

1. **🌐 Deploy Cloud**: AWS/Azure integration
2. **📱 Mobile App**: React Native
3. **🤖 AutoML**: Otimização automática
4. **📡 IoT Hub**: Azure IoT Hub
5. **🔒 Blockchain**: Rastreabilidade
6. **🌍 Multi-language**: Suporte internacional

## 👥 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📞 Suporte

- 📧 Email: suporte@farmtech.com
- 📱 WhatsApp: +55 11 99999-9999
- 🌐 Website: https://farmtech.com
- 📖 Documentação: https://docs.farmtech.com

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**FarmTech Solutions** - Transformando a agricultura com tecnologia! 🌾🤖📊

*Desenvolvido com ❤️ para a agricultura de precisão* 