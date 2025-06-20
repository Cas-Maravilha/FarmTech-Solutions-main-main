# FarmTech Solutions - Sistema de Monitoramento com Display LCD

## 📋 Visão Geral

Este projeto implementa um sistema completo de monitoramento agrícola usando ESP32 com display LCD I2C para exibição de métricas em tempo real. O sistema integra sensores de temperatura, umidade e controle de irrigação automático.

## 🎯 Funcionalidades

### Display LCD I2C (20x4)
- **Linha 1**: Título do sistema "FarmTech Monitor"
- **Linha 2**: Temperatura e Umidade do Ar
- **Linha 3**: Umidade do Solo e Status da Irrigação
- **Linha 4**: Status do Sistema (OK/Alertas)

### Sensores Integrados
- **DHT22**: Temperatura e umidade do ar
- **Sensor de Umidade do Solo**: Monitoramento da umidade do solo
- **Módulo Relé**: Controle automático de irrigação

### Controle Automático
- **Irrigação Inteligente**: Ativa/desativa baseado na umidade do solo
- **Alertas em Tempo Real**: Monitoramento de condições críticas
- **Integração WiFi**: Envio de dados para servidor (opcional)

## 🔧 Componentes Utilizados

| Componente | Quantidade | Descrição |
|------------|------------|-----------|
| ESP32 DevKit V1 | 1 | Microcontrolador principal |
| Display LCD I2C 20x4 | 1 | Exibição de informações |
| Sensor DHT22 | 1 | Temperatura e umidade do ar |
| Sensor de Umidade do Solo | 1 | Monitoramento do solo |
| Módulo Relé | 1 | Controle de irrigação |
| Jumpers | 8 | Conexões |

## 🔌 Conexões

### Display LCD I2C
- **SDA** → GPIO22 (ESP32)
- **SCL** → GPIO21 (ESP32)
- **VCC** → 3.3V (ESP32)
- **GND** → GND (ESP32)

### Sensor DHT22
- **VCC** → GPIO4 (ESP32)
- **DATA** → GPIO4 (ESP32)
- **GND** → GND (ESP32)

### Sensor de Umidade do Solo
- **VCC** → GPIO5 (ESP32)
- **SIG** → GPIO5 (ESP32)
- **GND** → GND (ESP32)

### Módulo Relé
- **VCC** → GPIO18 (ESP32)
- **IN** → GPIO18 (ESP32)
- **GND** → GND (ESP32)

## 📊 Exibição no Display

### Layout Padrão
```
┌────────────────────┐
│ FarmTech Monitor   │
│ T:25.3C U:65%      │
│ Solo:45% IRRIG     │
│ OK                 │
└────────────────────┘
```

### Indicadores Visuais
- **`*`**: Indica irrigação ativa
- **Alertas**: Mensagens de status crítico
- **Atualização**: A cada 2 segundos

## ⚙️ Configurações

### Limites de Alerta
```cpp
const float TEMP_MAX = 35.0;        // Temperatura máxima
const float TEMP_MIN = 10.0;        // Temperatura mínima
const int UMIDADE_SOLO_MIN = 30;    // Umidade mínima do solo
const int UMIDADE_SOLO_MAX = 80;    // Umidade máxima do solo
```

### Intervalos de Atualização
```cpp
const unsigned long INTERVALO_LEITURA = 5000;   // 5 segundos
const unsigned long INTERVALO_DISPLAY = 2000;   // 2 segundos
```

## 🚀 Como Usar no Wokwi

### 1. Acessar o Projeto
- Abra o arquivo `wokwi-project.json` no Wokwi
- Ou use o link direto do projeto

### 2. Configurar WiFi (Opcional)
```cpp
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";
const char* serverUrl = "http://localhost:5000/api/sensors";
```

### 3. Compilar e Executar
- Clique em "Start Simulation"
- Observe o display LCD atualizando em tempo real
- Monitore o console para logs detalhados

## 📈 Funcionalidades Avançadas

### Simulação Realista
O script `simulation.js` inclui:
- **Variação de temperatura**: Ciclo diário realista
- **Eventos climáticos**: Chuva, calor, seca
- **Controle automático**: Irrigação baseada em dados
- **Alertas inteligentes**: Status baseado em limites

### Debug e Controle
```javascript
// Forçar valores específicos
farmTechDebug.setTemperatura(30);
farmTechDebug.setUmidadeSolo(25);
farmTechDebug.forcarIrrigacao(true);

// Simular eventos
farmTechDebug.simularChuva();
farmTechDebug.simularCalor();

// Ver status
farmTechDebug.status();
```

## 🔍 Monitoramento

### Dados Exibidos
- **Temperatura**: 0-50°C (precisão: 0.1°C)
- **Umidade do Ar**: 0-100% (precisão: 1%)
- **Umidade do Solo**: 0-100% (precisão: 1%)
- **Status da Irrigação**: Ativa/Inativa
- **Status do Sistema**: OK/Alertas

### Alertas Automáticos
- **Temperatura Alta**: > 35°C
- **Temperatura Baixa**: < 10°C
- **Solo Seco**: < 30%
- **Solo Muito Úmido**: > 80%

## 📱 Integração com Sistema Principal

### Envio de Dados
```json
{
  "sensor_id": "ESP32_FARMTECH_001",
  "temperatura": 25.3,
  "umidade_ar": 65.0,
  "umidade_solo": 45.0,
  "irrigacao_ativa": true,
  "status": "OK",
  "timestamp": 1234567890
}
```

### API Endpoint
- **URL**: `http://localhost:5000/api/sensors`
- **Método**: POST
- **Content-Type**: application/json

## 🛠️ Personalização

### Modificar Layout do Display
```cpp
void atualizarDisplay() {
  lcd.clear();
  
  // Personalizar layout aqui
  lcd.setCursor(0, 0);
  lcd.print("Seu Título");
  
  // Adicionar mais informações
  lcd.setCursor(0, 1);
  lcd.printf("Temp: %.1f°C", temperatura);
}
```

### Adicionar Novos Sensores
```cpp
// Definir novo sensor
#define NOVO_SENSOR_PIN 23

// Ler dados
int valorNovoSensor = analogRead(NOVO_SENSOR_PIN);

// Exibir no display
lcd.setCursor(0, 3);
lcd.printf("Novo: %d", valorNovoSensor);
```

## 🔧 Troubleshooting

### Display Não Funciona
1. Verificar endereço I2C (padrão: 0x27)
2. Confirmar conexões SDA/SCL
3. Verificar alimentação 3.3V

### Sensores Não Respondem
1. Verificar pinos de conexão
2. Confirmar alimentação
3. Verificar bibliotecas instaladas

### WiFi Não Conecta
1. Verificar credenciais
2. Confirmar rede disponível
3. Verificar força do sinal

## 📚 Bibliotecas Necessárias

```cpp
#include <Wire.h>                    // Comunicação I2C
#include <LiquidCrystal_I2C.h>       // Display LCD I2C
#include <DHT.h>                     // Sensor DHT22
#include <WiFi.h>                    // WiFi (ESP32)
#include <HTTPClient.h>              // Cliente HTTP
#include <ArduinoJson.h>             // Manipulação JSON
```

## 🎯 Próximos Passos

### Melhorias Sugeridas
1. **Display Colorido**: Implementar display OLED colorido
2. **Interface Web**: Dashboard web local
3. **Armazenamento**: SD card para logs
4. **GPS**: Localização da estação
5. **Bateria**: Sistema autônomo com energia solar

### Integração com FarmTech
1. **API Completa**: Integração com backend Python
2. **Dashboard**: Visualização em tempo real
3. **Alertas**: Notificações push/email
4. **Machine Learning**: Predições baseadas em dados históricos

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs no console
2. Usar funções de debug
3. Consultar documentação
4. Verificar conexões físicas

---

**FarmTech Solutions** - Sistema de Monitoramento Agrícola Inteligente 🌱 