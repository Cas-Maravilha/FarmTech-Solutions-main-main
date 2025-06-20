/*
 * FarmTech Solutions - Demonstração Serial Plotter
 * ESP32 com monitoramento avançado e visualização em tempo real
 * 
 * Componentes:
 * - ESP32 DevKit V1
 * - Display LCD I2C 20x4
 * - Sensor DHT22 (Temperatura e Umidade)
 * - Sensor de Umidade do Solo
 * - Módulo Relé (Controle de Irrigação)
 * 
 * Serial Plotter: Monitoramento visual em tempo real
 * Formato: Tempo,Temp,Umid_Ar,Umid_Solo,Setpoint,Erro,Irrigacao,Status
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// =============================================================================
// CONFIGURAÇÕES DO SISTEMA
// =============================================================================

// Display LCD I2C
#define LCD_ADDRESS 0x27
#define LCD_COLS 20
#define LCD_ROWS 4
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);

// Sensores
#define DHT_PIN 4
#define SOIL_MOISTURE_PIN 5
#define RELAY_PIN 18
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

// WiFi (opcional)
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";
const char* serverUrl = "http://localhost:5000/api/sensors";

// =============================================================================
// VARIÁVEIS GLOBAIS
// =============================================================================

// Dados dos sensores
float temperatura = 0.0;
float umidade_ar = 0.0;
int umidade_solo = 0;
bool irrigacao_ativa = false;
String status_sistema = "OK";

// Controle de tempo
unsigned long ultima_leitura = 0;
unsigned long ultima_atualizacao_display = 0;
unsigned long ultima_serial_plotter = 0;
const unsigned long INTERVALO_LEITURA = 5000;      // 5 segundos
const unsigned long INTERVALO_DISPLAY = 2000;      // 2 segundos
const unsigned long INTERVALO_SERIAL_PLOTTER = 1000; // 1 segundo

// Limites de alerta
const float TEMP_MAX = 35.0;
const float TEMP_MIN = 10.0;
const int UMIDADE_SOLO_MIN = 30;
const int UMIDADE_SOLO_MAX = 80;

// Configurações Serial Plotter
const bool ENABLE_SERIAL_PLOTTER = true;
const bool ENABLE_CSV_FORMAT = true;
const bool ENABLE_DEBUG_PRINTS = true;

// Estrutura de dados
struct SensorData {
  float temperatura;
  float umidade_ar;
  int umidade_solo;
  bool irrigacao_ativa;
  String status;
  unsigned long timestamp;
  float setpoint_umidade_solo;
  float erro_umidade_solo;
  float saida_pid;
  float proporcional;
  float integral;
  float derivativo;
};

SensorData dados_sensor;

// Controle PID
float setpoint_umidade = 50.0;
float erro_anterior = 0.0;
float integral = 0.0;
const float KP = 0.5;
const float KI = 0.1;
const float KD = 0.05;

// Contadores para estatísticas
unsigned long contador_leituras = 0;
unsigned long contador_irrigacoes = 0;
unsigned long tempo_inicio = 0;

// =============================================================================
// FUNÇÃO SETUP
// =============================================================================

void setup() {
  // Inicialização do Serial
  Serial.begin(115200);
  delay(1000);
  
  // Cabeçalho inicial
  Serial.println("==========================================");
  Serial.println("    FARM TECH SOLUTIONS - SERIAL PLOTTER");
  Serial.println("==========================================");
  Serial.println("Sistema de Monitoramento Agrícola");
  Serial.println("ESP32 com Visualização em Tempo Real");
  Serial.println("==========================================");
  
  // Configuração do Serial Plotter
  if (ENABLE_SERIAL_PLOTTER) {
    Serial.println();
    Serial.println("=== CONFIGURAÇÃO DO SERIAL PLOTTER ===");
    Serial.println("Formato dos dados:");
    Serial.println("Tempo,Temperatura,Umidade_Ar,Umidade_Solo,Setpoint,Erro,Irrigacao,Status");
    Serial.println("Unidades: s,°C,%,%,%,%,0/1,0-4");
    Serial.println();
    Serial.println("Legenda dos Status:");
    Serial.println("0 = OK (Sistema Normal)");
    Serial.println("1 = ALERTA: Temperatura Alta");
    Serial.println("2 = ALERTA: Temperatura Baixa");
    Serial.println("3 = ALERTA: Solo Seco");
    Serial.println("4 = ALERTA: Solo Muito Úmido");
    Serial.println();
    Serial.println("=== INÍCIO DOS DADOS ===");
    Serial.println("Tempo,Temp,Umid_Ar,Umid_Solo,Setpoint,Erro,Irrigacao,Status");
  }
  
  // Inicialização do Display
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Mensagem de inicialização no LCD
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Solutions");
  lcd.setCursor(0, 1);
  lcd.print("Serial Plotter Demo");
  lcd.setCursor(0, 2);
  lcd.print("Monitoramento");
  lcd.setCursor(0, 3);
  lcd.print("Tempo Real");
  
  delay(3000);
  
  // Inicialização dos sensores
  dht.begin();
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  
  // Conectar WiFi
  conectarWiFi();
  
  // Primeira leitura
  lerSensores();
  tempo_inicio = millis();
  
  // Mensagem final de setup
  Serial.println("✅ Sistema inicializado com sucesso!");
  Serial.println("📊 Serial Plotter ativo - Abra o Serial Plotter no Arduino IDE");
  Serial.println("🖥️  Display LCD configurado");
  Serial.println("🌡️  Sensores DHT22 e Solo configurados");
  Serial.println("💧 Sistema de irrigação pronto");
  Serial.println("📡 WiFi configurado (opcional)");
  Serial.println();
  Serial.println("=== COMANDOS DISPONÍVEIS ===");
  Serial.println("SETPOINT:XX.X - Define setpoint de umidade (0-100)");
  Serial.println("STATUS - Exibe status atual do sistema");
  Serial.println("HELP - Exibe esta ajuda");
  Serial.println("RESET - Reseta contadores PID");
  Serial.println("INFO - Informações detalhadas");
  Serial.println("==========================================");
}

// =============================================================================
// FUNÇÃO LOOP PRINCIPAL
// =============================================================================

void loop() {
  unsigned long tempo_atual = millis();
  
  // Leitura dos sensores
  if (tempo_atual - ultima_leitura >= INTERVALO_LEITURA) {
    lerSensores();
    analisarDados();
    controlarIrrigacaoPID();
    enviarDadosServidor();
    ultima_leitura = tempo_atual;
    contador_leituras++;
  }
  
  // Atualização do display
  if (tempo_atual - ultima_atualizacao_display >= INTERVALO_DISPLAY) {
    atualizarDisplay();
    ultima_atualizacao_display = tempo_atual;
  }
  
  // Serial Plotter
  if (ENABLE_SERIAL_PLOTTER && tempo_atual - ultima_serial_plotter >= INTERVALO_SERIAL_PLOTTER) {
    enviarDadosSerialPlotter();
    ultima_serial_plotter = tempo_atual;
  }
  
  // Processar comandos Serial
  processarComandoSerial();
  
  delay(100);
}

// =============================================================================
// FUNÇÕES DE LEITURA E PROCESSAMENTO
// =============================================================================

void lerSensores() {
  if (ENABLE_DEBUG_PRINTS) {
    Serial.println();
    Serial.println("🔍 === LEITURA DOS SENSORES ===");
  }
  
  // Leitura DHT22
  float temp_nova = dht.readTemperature();
  float umid_ar_nova = dht.readHumidity();
  
  if (!isnan(temp_nova)) {
    temperatura = temp_nova;
    if (ENABLE_DEBUG_PRINTS) {
      Serial.printf("🌡️  Temperatura: %.2f°C\n", temperatura);
    }
  } else {
    if (ENABLE_DEBUG_PRINTS) {
      Serial.println("❌ Erro na leitura da temperatura");
    }
  }
  
  if (!isnan(umid_ar_nova)) {
    umidade_ar = umid_ar_nova;
    if (ENABLE_DEBUG_PRINTS) {
      Serial.printf("💨 Umidade do Ar: %.2f%%\n", umidade_ar);
    }
  } else {
    if (ENABLE_DEBUG_PRINTS) {
      Serial.println("❌ Erro na leitura da umidade do ar");
    }
  }
  
  // Leitura sensor de solo
  int leitura_solo = analogRead(SOIL_MOISTURE_PIN);
  umidade_solo = map(leitura_solo, 4095, 0, 0, 100);
  
  if (ENABLE_DEBUG_PRINTS) {
    Serial.printf("🌱 Umidade do Solo: %d%% (Raw: %d)\n", umidade_solo, leitura_solo);
  }
  
  // Calcular erro para PID
  dados_sensor.erro_umidade_solo = setpoint_umidade - umidade_solo;
  
  // Atualizar estrutura
  dados_sensor.temperatura = temperatura;
  dados_sensor.umidade_ar = umidade_ar;
  dados_sensor.umidade_solo = umidade_solo;
  dados_sensor.irrigacao_ativa = irrigacao_ativa;
  dados_sensor.setpoint_umidade_solo = setpoint_umidade;
  dados_sensor.timestamp = millis();
  
  if (ENABLE_DEBUG_PRINTS) {
    Serial.printf("🎯 Setpoint: %.1f%%\n", setpoint_umidade);
    Serial.printf("📊 Erro: %.1f%%\n", dados_sensor.erro_umidade_solo);
    Serial.printf("💧 Irrigação: %s\n", irrigacao_ativa ? "ATIVA" : "INATIVA");
    Serial.println("=====================================");
  }
}

void analisarDados() {
  if (ENABLE_DEBUG_PRINTS) {
    Serial.println("🔍 === ANÁLISE DE DADOS ===");
  }
  
  status_sistema = "OK";
  
  if (temperatura > TEMP_MAX) {
    status_sistema = "ALERTA: TEMP ALTA";
    if (ENABLE_DEBUG_PRINTS) {
      Serial.printf("⚠️  ALERTA: Temperatura alta (%.1f°C > %.1f°C)\n", temperatura, TEMP_MAX);
    }
  } else if (temperatura < TEMP_MIN) {
    status_sistema = "ALERTA: TEMP BAIXA";
    if (ENABLE_DEBUG_PRINTS) {
      Serial.printf("⚠️  ALERTA: Temperatura baixa (%.1f°C < %.1f°C)\n", temperatura, TEMP_MIN);
    }
  } else if (umidade_solo < UMIDADE_SOLO_MIN) {
    status_sistema = "ALERTA: SOLO SECO";
    if (ENABLE_DEBUG_PRINTS) {
      Serial.printf("⚠️  ALERTA: Solo seco (%d%% < %d%%)\n", umidade_solo, UMIDADE_SOLO_MIN);
    }
  } else if (umidade_solo > UMIDADE_SOLO_MAX) {
    status_sistema = "ALERTA: SOLO MUITO UMIDO";
    if (ENABLE_DEBUG_PRINTS) {
      Serial.printf("⚠️  ALERTA: Solo muito úmido (%d%% > %d%%)\n", umidade_solo, UMIDADE_SOLO_MAX);
    }
  } else {
    if (ENABLE_DEBUG_PRINTS) {
      Serial.println("✅ Condições normais");
    }
  }
  
  dados_sensor.status = status_sistema;
  
  if (ENABLE_DEBUG_PRINTS) {
    Serial.printf("📋 Status Final: %s\n", status_sistema.c_str());
    Serial.println("===============================");
  }
}

void controlarIrrigacaoPID() {
  if (ENABLE_DEBUG_PRINTS) {
    Serial.println("🎛️  === CONTROLE PID ===");
  }
  
  float erro = dados_sensor.erro_umidade_solo;
  
  // Termo proporcional
  float proporcional = KP * erro;
  
  // Termo integral
  integral += KI * erro * (INTERVALO_LEITURA / 1000.0);
  integral = constrain(integral, -100, 100);
  
  // Termo derivativo
  float derivativo = KD * (erro - erro_anterior) / (INTERVALO_LEITURA / 1000.0);
  
  // Saída PID
  float saida_pid = proporcional + integral + derivativo;
  
  // Armazenar dados para Serial Plotter
  dados_sensor.proporcional = proporcional;
  dados_sensor.integral = integral;
  dados_sensor.derivativo = derivativo;
  dados_sensor.saida_pid = saida_pid;
  
  // Lógica de controle
  bool irrigacao_anterior = irrigacao_ativa;
  
  if (saida_pid > 10 && !irrigacao_ativa) {
    digitalWrite(RELAY_PIN, HIGH);
    irrigacao_ativa = true;
    contador_irrigacoes++;
    if (ENABLE_DEBUG_PRINTS) {
      Serial.println("💧 IRRIGAÇÃO ATIVADA (PID)");
    }
  } else if (saida_pid < -5 && irrigacao_ativa) {
    digitalWrite(RELAY_PIN, LOW);
    irrigacao_ativa = false;
    if (ENABLE_DEBUG_PRINTS) {
      Serial.println("💧 IRRIGAÇÃO DESATIVADA (PID)");
    }
  }
  
  erro_anterior = erro;
  
  if (ENABLE_DEBUG_PRINTS) {
    Serial.printf("📊 Erro: %.2f\n", erro);
    Serial.printf("📈 Proporcional: %.2f\n", proporcional);
    Serial.printf("📉 Integral: %.2f\n", integral);
    Serial.printf("📊 Derivativo: %.2f\n", derivativo);
    Serial.printf("🎯 Saída PID: %.2f\n", saida_pid);
    Serial.printf("💧 Irrigação: %s\n", irrigacao_ativa ? "ATIVA" : "INATIVA");
    Serial.println("=========================");
  }
}

// =============================================================================
// SERIAL PLOTTER E COMUNICAÇÃO
// =============================================================================

void enviarDadosSerialPlotter() {
  if (!ENABLE_SERIAL_PLOTTER) return;
  
  // Converter status para valor numérico
  int status_numerico = 0;
  if (status_sistema == "OK") status_numerico = 0;
  else if (status_sistema.contains("TEMP ALTA")) status_numerico = 1;
  else if (status_sistema.contains("TEMP BAIXA")) status_numerico = 2;
  else if (status_sistema.contains("SOLO SECO")) status_numerico = 3;
  else if (status_sistema.contains("MUITO UMIDO")) status_numerico = 4;
  
  // Converter irrigação para 0/1
  int irrigacao_numerico = irrigacao_ativa ? 1 : 0;
  
  // Enviar dados formatados
  if (ENABLE_CSV_FORMAT) {
    // Formato CSV com timestamp
    Serial.printf("%lu,%.2f,%.2f,%d,%.1f,%.1f,%d,%d\n",
                  millis() / 1000,  // Tempo em segundos
                  temperatura,      // Temperatura (°C)
                  umidade_ar,       // Umidade do ar (%)
                  umidade_solo,     // Umidade do solo (%)
                  setpoint_umidade, // Setpoint (%)
                  dados_sensor.erro_umidade_solo, // Erro (%)
                  irrigacao_numerico, // Status irrigação (0/1)
                  status_numerico);   // Status sistema (0-4)
  } else {
    // Formato simples para plotter
    Serial.printf("%.2f,%.2f,%d,%.1f,%.1f,%d,%d\n",
                  temperatura,      // Temperatura
                  umidade_ar,       // Umidade do ar
                  umidade_solo,     // Umidade do solo
                  setpoint_umidade, // Setpoint
                  dados_sensor.erro_umidade_solo, // Erro
                  irrigacao_numerico, // Status irrigação
                  status_numerico);   // Status sistema
  }
}

void processarComandoSerial() {
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    
    if (comando.startsWith("SETPOINT:")) {
      float novo_setpoint = comando.substring(9).toFloat();
      if (novo_setpoint >= 0 && novo_setpoint <= 100) {
        setpoint_umidade = novo_setpoint;
        Serial.printf("✅ Setpoint alterado para: %.1f%%\n", setpoint_umidade);
      } else {
        Serial.println("❌ Erro: Setpoint deve estar entre 0 e 100");
      }
    } else if (comando == "STATUS") {
      exibirStatusDetalhado();
    } else if (comando == "HELP") {
      exibirAjuda();
    } else if (comando == "RESET") {
      integral = 0.0;
      erro_anterior = 0.0;
      Serial.println("🔄 Contadores PID resetados");
    } else if (comando == "INFO") {
      exibirInfoDetalhada();
    } else if (comando == "STATS") {
      exibirEstatisticas();
    }
  }
}

// =============================================================================
// FUNÇÕES DE EXIBIÇÃO E INTERFACE
// =============================================================================

void exibirStatusDetalhado() {
  Serial.println();
  Serial.println("📊 === STATUS ATUAL DO SISTEMA ===");
  Serial.printf("🌡️  Temperatura: %.2f°C\n", temperatura);
  Serial.printf("💨 Umidade do Ar: %.2f%%\n", umidade_ar);
  Serial.printf("🌱 Umidade do Solo: %d%%\n", umidade_solo);
  Serial.printf("🎯 Setpoint: %.1f%%\n", setpoint_umidade);
  Serial.printf("📊 Erro: %.1f%%\n", dados_sensor.erro_umidade_solo);
  Serial.printf("💧 Irrigação: %s\n", irrigacao_ativa ? "ATIVA" : "INATIVA");
  Serial.printf("📋 Status: %s\n", status_sistema.c_str());
  Serial.printf("⏱️  Uptime: %lu segundos\n", millis() / 1000);
  Serial.println("=====================================");
}

void exibirAjuda() {
  Serial.println();
  Serial.println("📖 === COMANDOS DISPONÍVEIS ===");
  Serial.println("SETPOINT:XX.X - Define setpoint de umidade (0-100)");
  Serial.println("STATUS - Exibe status atual do sistema");
  Serial.println("INFO - Informações detalhadas");
  Serial.println("STATS - Estatísticas do sistema");
  Serial.println("HELP - Exibe esta ajuda");
  Serial.println("RESET - Reseta contadores PID");
  Serial.println("===============================");
}

void exibirInfoDetalhada() {
  Serial.println();
  Serial.println("ℹ️  === INFORMAÇÕES DETALHADAS ===");
  Serial.println("Sistema: FarmTech Solutions");
  Serial.println("Hardware: ESP32 DevKit V1");
  Serial.println("Sensores: DHT22 + Sensor Solo");
  Serial.println("Display: LCD I2C 20x4");
  Serial.println("Controle: PID para Irrigação");
  Serial.println("Comunicação: Serial Plotter + WiFi");
  Serial.println();
  Serial.println("Parâmetros PID:");
  Serial.printf("KP (Proporcional): %.2f\n", KP);
  Serial.printf("KI (Integral): %.2f\n", KI);
  Serial.printf("KD (Derivativo): %.2f\n", KD);
  Serial.println();
  Serial.println("Limites de Alerta:");
  Serial.printf("Temperatura: %.1f°C - %.1f°C\n", TEMP_MIN, TEMP_MAX);
  Serial.printf("Umidade Solo: %d%% - %d%%\n", UMIDADE_SOLO_MIN, UMIDADE_SOLO_MAX);
  Serial.println("=================================");
}

void exibirEstatisticas() {
  unsigned long uptime = millis() / 1000;
  Serial.println();
  Serial.println("📈 === ESTATÍSTICAS DO SISTEMA ===");
  Serial.printf("⏱️  Tempo de funcionamento: %lu segundos\n", uptime);
  Serial.printf("📊 Total de leituras: %lu\n", contador_leituras);
  Serial.printf("💧 Ativações de irrigação: %lu\n", contador_irrigacoes);
  Serial.printf("📊 Frequência de leitura: %.1f Hz\n", (float)contador_leituras / (uptime / 5.0));
  Serial.printf("💧 Frequência de irrigação: %.1f/h\n", (float)contador_irrigacoes / (uptime / 3600.0));
  Serial.println("===================================");
}

void atualizarDisplay() {
  lcd.clear();
  
  // Linha 1: Título
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Monitor");
  
  // Linha 2: Temperatura e Umidade do Ar
  lcd.setCursor(0, 1);
  lcd.printf("T:%.1fC U:%.0f%%", temperatura, umidade_ar);
  
  // Linha 3: Umidade do Solo e Setpoint
  lcd.setCursor(0, 2);
  lcd.printf("Solo:%d%% SP:%.0f%%", umidade_solo, setpoint_umidade);
  
  // Linha 4: Status
  lcd.setCursor(0, 3);
  if (status_sistema.length() > 20) {
    lcd.print(status_sistema.substring(0, 20));
  } else {
    lcd.print(status_sistema);
  }
  
  // Indicador de irrigação
  if (irrigacao_ativa) {
    lcd.setCursor(19, 2);
    lcd.print("*");
  }
}

void conectarWiFi() {
  Serial.println("📡 Conectando ao WiFi...");
  lcd.setCursor(0, 3);
  lcd.print("Conectando WiFi...");
  
  WiFi.begin(ssid, password);
  int tentativas = 0;
  
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi conectado!");
    Serial.printf("🌐 IP: %s\n", WiFi.localIP().toString().c_str());
    lcd.setCursor(0, 3);
    lcd.print("WiFi Conectado    ");
  } else {
    Serial.println("\n❌ Falha na conexão WiFi");
    lcd.setCursor(0, 3);
    lcd.print("WiFi Desconectado ");
  }
}

void enviarDadosServidor() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<512> doc;
  doc["sensor_id"] = "ESP32_FARMTECH_001";
  doc["temperatura"] = temperatura;
  doc["umidade_ar"] = umidade_ar;
  doc["umidade_solo"] = umidade_solo;
  doc["setpoint_umidade"] = setpoint_umidade;
  doc["erro_umidade"] = dados_sensor.erro_umidade_solo;
  doc["irrigacao_ativa"] = irrigacao_ativa;
  doc["status"] = status_sistema;
  doc["timestamp"] = dados_sensor.timestamp;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    Serial.printf("📤 Dados enviados. Código: %d\n", httpResponseCode);
  } else {
    Serial.printf("❌ Erro ao enviar dados: %d\n", httpResponseCode);
  }
  
  http.end();
} 