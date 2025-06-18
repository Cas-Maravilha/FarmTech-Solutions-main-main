# FarmTech Solutions - Serial Plotter Demo

## 🌾 Monitoramento Visual em Tempo Real

Este documento demonstra o uso do **Serial Plotter** do Arduino IDE para monitoramento visual das variáveis do sistema FarmTech Solutions em tempo real.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Configuração do Serial Plotter](#configuração-do-serial-plotter)
3. [Demonstração dos Prints](#demonstração-dos-prints)
4. [Interpretação dos Dados](#interpretação-dos-dados)
5. [Comandos Disponíveis](#comandos-disponíveis)
6. [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O **Serial Plotter** é uma ferramenta visual do Arduino IDE que permite monitorar variáveis em tempo real através de gráficos. No FarmTech Solutions, utilizamos esta funcionalidade para:

- 📊 **Visualizar tendências** das variáveis ambientais
- 🔍 **Monitorar o controle PID** de irrigação
- ⚠️ **Detectar anomalias** nos sensores
- 📈 **Analisar performance** do sistema

## ⚙️ Configuração do Serial Plotter

### 1. Hardware Necessário
```
- ESP32 DevKit V1
- Sensor DHT22 (Temperatura e Umidade)
- Sensor de Umidade do Solo
- Display LCD I2C 20x4
- Módulo Relé (Controle de Irrigação)
```

### 2. Conexões
```
DHT22:
- VCC → 3.3V
- GND → GND
- DATA → GPIO 4

Sensor Solo:
- VCC → 3.3V
- GND → GND
- DATA → GPIO 5

Relé:
- VCC → 3.3V
- GND → GND
- IN → GPIO 18

LCD I2C:
- VCC → 3.3V
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22
```

### 3. Configuração do Arduino IDE
1. Abra o Arduino IDE
2. Carregue o código `farmtech_esp32_serial_plotter_demo.ino`
3. Configure a porta COM correta
4. Faça upload do código
5. Abra o **Serial Monitor** (Ctrl+Shift+M)
6. Abra o **Serial Plotter** (Ferramentas → Serial Plotter)

## 📊 Demonstração dos Prints

### 1. **Inicialização do Sistema**

```
==========================================
    FARM TECH SOLUTIONS - SERIAL PLOTTER
==========================================
Sistema de Monitoramento Agrícola
ESP32 com Visualização em Tempo Real
==========================================

=== CONFIGURAÇÃO DO SERIAL PLOTTER ===
Formato dos dados:
Tempo,Temperatura,Umidade_Ar,Umidade_Solo,Setpoint,Erro,Irrigacao,Status
Unidades: s,°C,%,%,%,%,0/1,0-4

Legenda dos Status:
0 = OK (Sistema Normal)
1 = ALERTA: Temperatura Alta
2 = ALERTA: Temperatura Baixa
3 = ALERTA: Solo Seco
4 = ALERTA: Solo Muito Úmido

=== INÍCIO DOS DADOS ===
Tempo,Temp,Umid_Ar,Umid_Solo,Setpoint,Erro,Irrigacao,Status
```

**Explicação:**
- **Cabeçalho**: Identifica o sistema e versão
- **Formato**: Define as colunas dos dados
- **Unidades**: Especifica as unidades de cada variável
- **Legenda**: Explica os códigos de status
- **Início**: Marca o início dos dados para o plotter

### 2. **Leitura dos Sensores**

```
🔍 === LEITURA DOS SENSORES ===
🌡️  Temperatura: 25.67°C
💨 Umidade do Ar: 68.45%
🌱 Umidade do Solo: 45% (Raw: 2250)
🎯 Setpoint: 50.0%
📊 Erro: 5.0%
💧 Irrigação: INATIVA
=====================================
```

**Explicação:**
- **🌡️ Temperatura**: Leitura do sensor DHT22 em °C
- **💨 Umidade do Ar**: Umidade relativa do ar em %
- **🌱 Umidade do Solo**: Umidade do solo em % (com valor raw do ADC)
- **🎯 Setpoint**: Valor desejado para umidade do solo
- **📊 Erro**: Diferença entre setpoint e valor atual
- **💧 Irrigação**: Status atual do sistema de irrigação

### 3. **Análise de Dados**

```
🔍 === ANÁLISE DE DADOS ===
✅ Condições normais
📋 Status Final: OK
===============================
```

**Explicação:**
- **Análise**: Verifica se as variáveis estão dentro dos limites
- **Status**: Determina o estado geral do sistema
- **Alertas**: Identifica condições críticas

### 4. **Controle PID**

```
🎛️  === CONTROLE PID ===
📊 Erro: 5.00
📈 Proporcional: 2.50
📉 Integral: 0.25
📊 Derivativo: 0.05
🎯 Saída PID: 2.80
💧 Irrigação: INATIVA
=========================
```

**Explicação:**
- **📊 Erro**: Diferença entre setpoint e valor atual
- **📈 Proporcional**: Termo P do controle PID
- **📉 Integral**: Termo I do controle PID (acumulado)
- **📊 Derivativo**: Termo D do controle PID (taxa de variação)
- **🎯 Saída PID**: Resultado do cálculo PID
- **💧 Irrigação**: Decisão de ativar/desativar irrigação

### 5. **Dados para Serial Plotter**

```
120,25.67,68.45,45,50.0,5.0,0,0
121,25.68,68.42,46,50.0,4.0,0,0
122,25.70,68.40,47,50.0,3.0,0,0
123,25.72,68.38,48,50.0,2.0,0,0
124,25.75,68.35,49,50.0,1.0,0,0
125,25.78,68.32,50,50.0,0.0,0,0
126,25.80,68.30,51,50.0,-1.0,0,0
```

**Formato CSV:**
```
Tempo,Temperatura,Umidade_Ar,Umidade_Solo,Setpoint,Erro,Irrigacao,Status
```

**Explicação das Colunas:**
1. **Tempo**: Segundos desde o início (s)
2. **Temperatura**: Temperatura ambiente (°C)
3. **Umidade_Ar**: Umidade relativa do ar (%)
4. **Umidade_Solo**: Umidade do solo (%)
5. **Setpoint**: Valor desejado para umidade (%)
6. **Erro**: Diferença entre setpoint e valor atual (%)
7. **Irrigacao**: Status da irrigação (0=Inativa, 1=Ativa)
8. **Status**: Estado do sistema (0=OK, 1-4=Alertas)

## 📈 Interpretação dos Dados

### Gráfico de Temperatura
```
🌡️  Temperatura (°C)
    |
35  |                    ⚠️  ALERTA TEMP ALTA
    |                /\
30  |               /  \
    |              /    \
25  |             /      \____
    |            /            \
20  |           /              \
    |          /                \
15  |         /                  \
    |        /                    \
10  |       /                      \  ⚠️  ALERTA TEMP BAIXA
    |      /                        \
5   |     /                          \
    |    /                            \
0   |___/______________________________\___
    0   10   20   30   40   50   60   Tempo (s)
```

### Gráfico de Umidade do Solo
```
🌱 Umidade do Solo (%)
    |
100 |                                    ⚠️  MUITO ÚMIDO
    |                                /\
80  |                               /  \
    |                              /    \
60  |                             /      \
    |                            /        \
40  |                           /          \
    |                          /            \
20  |                         /              \
    |                        /                \
0   |_______________________/                  \  ⚠️  SOLO SECO
    0   10   20   30   40   50   60   Tempo (s)
```

### Gráfico de Controle PID
```
🎛️  Controle PID
    |
10  |                    💧 IRRIGAÇÃO ATIVA
    |                /\
5   |               /  \
    |              /    \
0   |_____________/      \____
    |                        \
-5  |                         \  💧 IRRIGAÇÃO DESATIVA
    |                          \
-10 |                           \_____________
    0   10   20   30   40   50   60   Tempo (s)
```

## 🎮 Comandos Disponíveis

### Via Serial Monitor

```
SETPOINT:60.0    → Define setpoint de umidade para 60%
STATUS           → Exibe status atual do sistema
INFO             → Informações detalhadas do hardware
STATS            → Estatísticas de funcionamento
HELP             → Lista todos os comandos
RESET            → Reseta contadores PID
```

### Exemplo de Interação

```
> SETPOINT:65.0
✅ Setpoint alterado para: 65.0%

> STATUS
📊 === STATUS ATUAL DO SISTEMA ===
🌡️  Temperatura: 25.67°C
💨 Umidade do Ar: 68.45%
🌱 Umidade do Solo: 45%
🎯 Setpoint: 65.0%
📊 Erro: 20.0%
💧 Irrigação: ATIVA
📋 Status: OK
⏱️  Uptime: 125 segundos
=====================================

> STATS
📈 === ESTATÍSTICAS DO SISTEMA ===
⏱️  Tempo de funcionamento: 125 segundos
📊 Total de leituras: 25
💧 Ativações de irrigação: 3
📊 Frequência de leitura: 1.0 Hz
💧 Frequência de irrigação: 86.4/h
===================================
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. **Serial Plotter não mostra dados**
```
❌ Problema: Nenhum gráfico aparece
✅ Solução: 
- Verifique se o Serial Plotter está aberto
- Confirme que a velocidade está em 115200 baud
- Aguarde alguns segundos para os dados aparecerem
```

#### 2. **Dados incorretos ou NaN**
```
❌ Problema: Valores NaN ou muito altos/baixos
✅ Solução:
- Verifique as conexões dos sensores
- Confirme a alimentação 3.3V
- Teste os sensores individualmente
```

#### 3. **Gráfico muito lento**
```
❌ Problema: Atualização lenta do gráfico
✅ Solução:
- Reduza INTERVALO_SERIAL_PLOTTER para 500ms
- Feche outros programas que usam a porta serial
- Reinicie o Arduino IDE
```

#### 4. **Erro de comunicação**
```
❌ Problema: "Failed to connect to ESP32"
✅ Solução:
- Pressione o botão BOOT do ESP32 durante upload
- Verifique se o driver USB está instalado
- Tente uma porta USB diferente
```

### Configurações Recomendadas

```cpp
// Para melhor visualização
const unsigned long INTERVALO_SERIAL_PLOTTER = 500;  // 500ms
const bool ENABLE_CSV_FORMAT = true;
const bool ENABLE_DEBUG_PRINTS = false;  // Desabilita prints extras
```

## 📊 Análise Avançada

### Padrões de Comportamento

#### 1. **Sistema Estável**
```
- Temperatura: Variação < 2°C
- Umidade Solo: Oscilação em torno do setpoint
- Irrigação: Ciclos regulares
- Status: Principalmente 0 (OK)
```

#### 2. **Sistema Instável**
```
- Temperatura: Variações bruscas
- Umidade Solo: Oscilações amplas
- Irrigação: Ativações frequentes
- Status: Muitos alertas (1-4)
```

#### 3. **Falha de Sensor**
```
- Valores constantes ou NaN
- Sem variação temporal
- Status de erro persistente
```

### Otimização de Parâmetros

#### Ajuste PID
```cpp
// Para resposta mais rápida
const float KP = 1.0;   // Aumentar proporcional
const float KI = 0.05;  // Reduzir integral
const float KD = 0.1;   // Aumentar derivativo

// Para resposta mais suave
const float KP = 0.3;   // Reduzir proporcional
const float KI = 0.2;   // Aumentar integral
const float KD = 0.02;  // Reduzir derivativo
```

## 🎯 Conclusão

O **Serial Plotter** é uma ferramenta essencial para:

✅ **Monitoramento visual** em tempo real
✅ **Análise de tendências** das variáveis
✅ **Debugging** do controle PID
✅ **Detecção de anomalias** nos sensores
✅ **Otimização** dos parâmetros do sistema

**FarmTech Solutions** - Monitoramento inteligente para agricultura de precisão! 🌾📊 