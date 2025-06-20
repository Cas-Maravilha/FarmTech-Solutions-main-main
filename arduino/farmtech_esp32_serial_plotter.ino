/*
 * FarmTech Solutions - Sistema de Monitoramento com Serial Plotter
 * ESP32 com display LCD I2C e Serial Plotter para análise visual
 * 
 * Componentes:
 * - ESP32 DevKit V1
 * - Display LCD I2C 20x4
 * - Sensor DHT22 (Temperatura e Umidade)
 * - Sensor de Umidade do Solo
 * - Módulo Relé (Controle de Irrigação)
 * 
 * Serial Plotter: Monitoramento em tempo real das variáveis
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configurações do Display LCD I2C
#define LCD_ADDRESS 0x27
#define LCD_COLS 20
#define LCD_ROWS 4
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);

// Configurações dos Sensores
#define DHT_PIN 4
#define SOIL_MOISTURE_PIN 5
#define RELAY_PIN 18
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

// Configurações WiFi (opcional para envio de dados)
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";
const char* serverUrl = "http://localhost:5000/api/sensors";

// Variáveis para armazenar dados dos sensores
float temperatura = 0.0;
float umidade_ar = 0.0;
int umidade_solo = 0;
bool irrigacao_ativa = false;
String status_sistema = "OK";

// Configurações de tempo
unsigned long ultima_leitura = 0;
unsigned long ultima_atualizacao_display = 0;
unsigned long ultima_serial_plotter = 0;
const unsigned long INTERVALO_LEITURA = 5000;      // 5 segundos
const unsigned long INTERVALO_DISPLAY = 2000;      // 2 segundos
const unsigned long INTERVALO_SERIAL_PLOTTER = 1000; // 1 segundo para plotter

// Configurações de alertas
const float TEMP_MAX = 35.0;
const float TEMP_MIN = 10.0;
const int UMIDADE_SOLO_MIN = 30;
const int UMIDADE_SOLO_MAX = 80;

// Configurações do Serial Plotter
const bool ENABLE_SERIAL_PLOTTER = true;
const bool ENABLE_CSV_FORMAT = true;  // Formato CSV para análise posterior

// Estrutura para dados do sensor
struct SensorData {
  float temperatura;
  float umidade_ar;
  int umidade_solo;
  bool irrigacao_ativa;
  String status;
  unsigned long timestamp;
  float setpoint_umidade_solo;  // Valor desejado para umidade do solo
  float erro_umidade_solo;      // Erro entre valor atual e desejado
};

SensorData dados_sensor;

// Variáveis para controle PID (simples)
float setpoint_umidade = 50.0;  // Umidade desejada do solo (50%)
float erro_anterior = 0.0;
float integral = 0.0;
const float KP = 0.5;  // Proporcional
const float KI = 0.1;  // Integral
const float KD = 0.05; // Derivativo

void setup() {
  // Inicialização do Serial
  Serial.begin(115200);
  Serial.println("FarmTech Solutions - Sistema de Monitoramento com Serial Plotter");
  
  // Cabeçalho para Serial Plotter
  if (ENABLE_SERIAL_PLOTTER) {
    Serial.println("=== FARM TECH SOLUTIONS - SERIAL PLOTTER ===");
    Serial.println("Tempo,Temperatura,Umidade_Ar,Umidade_Solo,Setpoint_Umidade,Erro_Umidade,Irrigacao_Status,Status_Sistema");
    Serial.println("s,°C,%,%,%,%,0/1,0-4");
    Serial.println("=== INICIO DOS DADOS ===");
  }
  
  // Inicialização do Display LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Mensagem de inicialização
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Solutions");
  lcd.setCursor(0, 1);
  lcd.print("Serial Plotter");
  lcd.setCursor(0, 2);
  lcd.print("Monitoramento");
  lcd.setCursor(0, 3);
  lcd.print("Tempo Real");
  
  delay(3000);
  
  // Inicialização dos sensores
  dht.begin();
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Desliga irrigação inicialmente
  
  // Conectar WiFi (opcional)
  conectarWiFi();
  
  // Primeira leitura dos sensores
  lerSensores();
  
  Serial.println("Sistema inicializado com sucesso!");
  Serial.println("Serial Plotter ativo - Abra o Serial Plotter no Arduino IDE");
  Serial.println("Formato: Tempo,Temp,Umid_Ar,Umid_Solo,Setpoint,Erro,Irrigacao,Status");
}

void loop() {
  unsigned long tempo_atual = millis();
  
  // Leitura dos sensores a cada 5 segundos
  if (tempo_atual - ultima_leitura >= INTERVALO_LEITURA) {
    lerSensores();
    analisarDados();
    controlarIrrigacaoPID();
    enviarDadosServidor(); // Opcional
    ultima_leitura = tempo_atual;
  }
  
  // Atualização do display a cada 2 segundos
  if (tempo_atual - ultima_atualizacao_display >= INTERVALO_DISPLAY) {
    atualizarDisplay();
    ultima_atualizacao_display = tempo_atual;
  }
  
  // Envio de dados para Serial Plotter a cada 1 segundo
  if (ENABLE_SERIAL_PLOTTER && tempo_atual - ultima_serial_plotter >= INTERVALO_SERIAL_PLOTTER) {
    enviarDadosSerialPlotter();
    ultima_serial_plotter = tempo_atual;
  }
  
  delay(100); // Pequena pausa para estabilidade
}

void lerSensores() {
  // Leitura do sensor DHT22 (Temperatura e Umidade do Ar)
  float temp_nova = dht.readTemperature();
  float umid_ar_nova = dht.readHumidity();
  
  if (!isnan(temp_nova)) {
    temperatura = temp_nova;
  }
  if (!isnan(umid_ar_nova)) {
    umidade_ar = umid_ar_nova;
  }
  
  // Leitura do sensor de umidade do solo
  int leitura_solo = analogRead(SOIL_MOISTURE_PIN);
  umidade_solo = map(leitura_solo, 4095, 0, 0, 100); // Conversão para porcentagem
  
  // Calcular erro para controle PID
  dados_sensor.erro_umidade_solo = setpoint_umidade - umidade_solo;
  
  // Atualizar estrutura de dados
  dados_sensor.temperatura = temperatura;
  dados_sensor.umidade_ar = umidade_ar;
  dados_sensor.umidade_solo = umidade_solo;
  dados_sensor.irrigacao_ativa = irrigacao_ativa;
  dados_sensor.setpoint_umidade_solo = setpoint_umidade;
  dados_sensor.erro_umidade_solo = dados_sensor.erro_umidade_solo;
  dados_sensor.timestamp = millis();
  
  // Log dos dados
  Serial.println("=== Leitura dos Sensores ===");
  Serial.printf("Temperatura: %.1f°C\n", temperatura);
  Serial.printf("Umidade do Ar: %.1f%%\n", umidade_ar);
  Serial.printf("Umidade do Solo: %d%%\n", umidade_solo);
  Serial.printf("Setpoint Umidade: %.1f%%\n", setpoint_umidade);
  Serial.printf("Erro: %.1f%%\n", dados_sensor.erro_umidade_solo);
  Serial.printf("Irrigação: %s\n", irrigacao_ativa ? "ATIVA" : "INATIVA");
  Serial.println("============================");
}

void analisarDados() {
  // Análise de alertas e status
  status_sistema = "OK";
  
  if (temperatura > TEMP_MAX) {
    status_sistema = "ALERTA: TEMP ALTA";
  } else if (temperatura < TEMP_MIN) {
    status_sistema = "ALERTA: TEMP BAIXA";
  } else if (umidade_solo < UMIDADE_SOLO_MIN) {
    status_sistema = "ALERTA: SOLO SECO";
  } else if (umidade_solo > UMIDADE_SOLO_MAX) {
    status_sistema = "ALERTA: SOLO MUITO UMIDO";
  }
  
  dados_sensor.status = status_sistema;
}

void controlarIrrigacaoPID() {
  // Controle PID simples para irrigação
  float erro = dados_sensor.erro_umidade_solo;
  
  // Termo proporcional
  float proporcional = KP * erro;
  
  // Termo integral
  integral += KI * erro * (INTERVALO_LEITURA / 1000.0);
  integral = constrain(integral, -100, 100); // Limitar integral
  
  // Termo derivativo
  float derivativo = KD * (erro - erro_anterior) / (INTERVALO_LEITURA / 1000.0);
  
  // Soma dos termos PID
  float saida_pid = proporcional + integral + derivativo;
  
  // Aplicar lógica de controle
  if (saida_pid > 10 && !irrigacao_ativa) {  // Threshold para ativar
    digitalWrite(RELAY_PIN, HIGH);
    irrigacao_ativa = true;
    Serial.println("IRRIGAÇÃO ATIVADA (PID)");
  } else if (saida_pid < -5 && irrigacao_ativa) {  // Threshold para desativar
    digitalWrite(RELAY_PIN, LOW);
    irrigacao_ativa = false;
    Serial.println("IRRIGAÇÃO DESATIVADA (PID)");
  }
  
  erro_anterior = erro;
  
  // Log do controle PID
  Serial.printf("PID - Erro: %.1f, P: %.1f, I: %.1f, D: %.1f, Saída: %.1f\n", 
                erro, proporcional, integral, derivativo, saida_pid);
}

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
  
  // Enviar dados formatados para Serial Plotter
  if (ENABLE_CSV_FORMAT) {
    // Formato CSV para análise posterior
    Serial.printf("%lu,%.2f,%.2f,%d,%.1f,%.1f,%d,%d\n",
                  millis() / 1000,  // Tempo em segundos
                  temperatura,      // Temperatura
                  umidade_ar,       // Umidade do ar
                  umidade_solo,     // Umidade do solo
                  setpoint_umidade, // Setpoint
                  dados_sensor.erro_umidade_solo, // Erro
                  irrigacao_numerico, // Status irrigação
                  status_numerico);   // Status sistema
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

void atualizarDisplay() {
  lcd.clear();
  
  // Linha 1: Título do sistema
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Monitor");
  
  // Linha 2: Temperatura e Umidade do Ar
  lcd.setCursor(0, 1);
  lcd.printf("T:%.1fC U:%.0f%%", temperatura, umidade_ar);
  
  // Linha 3: Umidade do Solo e Setpoint
  lcd.setCursor(0, 2);
  lcd.printf("Solo:%d%% SP:%.0f%%", umidade_solo, setpoint_umidade);
  
  // Linha 4: Status do sistema
  lcd.setCursor(0, 3);
  if (status_sistema.length() > 20) {
    lcd.print(status_sistema.substring(0, 20));
  } else {
    lcd.print(status_sistema);
  }
  
  // Indicador visual de irrigação (piscar quando ativa)
  if (irrigacao_ativa) {
    lcd.setCursor(19, 2);
    lcd.print("*");
  }
}

void conectarWiFi() {
  Serial.println("Conectando ao WiFi...");
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
    Serial.println("\nWiFi conectado!");
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    lcd.setCursor(0, 3);
    lcd.print("WiFi Conectado    ");
  } else {
    Serial.println("\nFalha na conexão WiFi");
    lcd.setCursor(0, 3);
    lcd.print("WiFi Desconectado ");
  }
}

void enviarDadosServidor() {
  if (WiFi.status() != WL_CONNECTED) {
    return; // Não enviar se não estiver conectado
  }
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  // Criar JSON com os dados
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
    Serial.printf("Dados enviados. Código: %d\n", httpResponseCode);
  } else {
    Serial.printf("Erro ao enviar dados: %d\n", httpResponseCode);
  }
  
  http.end();
}

// Função para exibir informações detalhadas
void exibirInfoDetalhada() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("=== INFO DETALHADA ===");
  lcd.setCursor(0, 1);
  lcd.printf("Temp: %.2f C", temperatura);
  lcd.setCursor(0, 2);
  lcd.printf("Umid Ar: %.1f%%", umidade_ar);
  lcd.setCursor(0, 3);
  lcd.printf("Umid Solo: %d%%", umidade_solo);
  
  delay(3000);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("=== STATUS SISTEMA ===");
  lcd.setCursor(0, 1);
  lcd.printf("Irrigacao: %s", irrigacao_ativa ? "ATIVA" : "INATIVA");
  lcd.setCursor(0, 2);
  lcd.printf("Status: %s", status_sistema.c_str());
  lcd.setCursor(0, 3);
  lcd.printf("Uptime: %lu s", millis() / 1000);
  
  delay(3000);
}

// Função para configurar setpoint via Serial
void processarComandoSerial() {
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    
    if (comando.startsWith("SETPOINT:")) {
      float novo_setpoint = comando.substring(9).toFloat();
      if (novo_setpoint >= 0 && novo_setpoint <= 100) {
        setpoint_umidade = novo_setpoint;
        Serial.printf("Setpoint alterado para: %.1f%%\n", setpoint_umidade);
      } else {
        Serial.println("Erro: Setpoint deve estar entre 0 e 100");
      }
    } else if (comando == "STATUS") {
      Serial.println("=== STATUS ATUAL ===");
      Serial.printf("Temperatura: %.1f°C\n", temperatura);
      Serial.printf("Umidade Ar: %.1f%%\n", umidade_ar);
      Serial.printf("Umidade Solo: %d%%\n", umidade_solo);
      Serial.printf("Setpoint: %.1f%%\n", setpoint_umidade);
      Serial.printf("Erro: %.1f%%\n", dados_sensor.erro_umidade_solo);
      Serial.printf("Irrigação: %s\n", irrigacao_ativa ? "ATIVA" : "INATIVA");
      Serial.printf("Status: %s\n", status_sistema.c_str());
    } else if (comando == "HELP") {
      Serial.println("=== COMANDOS DISPONÍVEIS ===");
      Serial.println("SETPOINT:XX.X - Define setpoint de umidade (0-100)");
      Serial.println("STATUS - Exibe status atual do sistema");
      Serial.println("HELP - Exibe esta ajuda");
      Serial.println("RESET - Reseta contadores PID");
    } else if (comando == "RESET") {
      integral = 0.0;
      erro_anterior = 0.0;
      Serial.println("Contadores PID resetados");
    }
  }
} 