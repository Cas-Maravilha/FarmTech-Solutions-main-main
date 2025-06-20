/*
 * FarmTech Solutions - Sistema de Monitoramento com Display LCD
 * ESP32 com display LCD I2C para exibição de métricas em tempo real
 * 
 * Componentes:
 * - ESP32 DevKit V1
 * - Display LCD I2C 20x4
 * - Sensor DHT22 (Temperatura e Umidade)
 * - Sensor de Umidade do Solo
 * - Módulo Relé (Controle de Irrigação)
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
const unsigned long INTERVALO_LEITURA = 5000;      // 5 segundos
const unsigned long INTERVALO_DISPLAY = 2000;      // 2 segundos

// Configurações de alertas
const float TEMP_MAX = 35.0;
const float TEMP_MIN = 10.0;
const int UMIDADE_SOLO_MIN = 30;
const int UMIDADE_SOLO_MAX = 80;

// Estrutura para dados do sensor
struct SensorData {
  float temperatura;
  float umidade_ar;
  int umidade_solo;
  bool irrigacao_ativa;
  String status;
  unsigned long timestamp;
};

SensorData dados_sensor;

void setup() {
  // Inicialização do Serial
  Serial.begin(115200);
  Serial.println("FarmTech Solutions - Sistema de Monitoramento");
  
  // Inicialização do Display LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Mensagem de inicialização
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Solutions");
  lcd.setCursor(0, 1);
  lcd.print("Inicializando...");
  lcd.setCursor(0, 2);
  lcd.print("Sistema de Monitoramento");
  lcd.setCursor(0, 3);
  lcd.print("LCD I2C Ativo");
  
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
}

void loop() {
  unsigned long tempo_atual = millis();
  
  // Leitura dos sensores a cada 5 segundos
  if (tempo_atual - ultima_leitura >= INTERVALO_LEITURA) {
    lerSensores();
    analisarDados();
    controlarIrrigacao();
    enviarDadosServidor(); // Opcional
    ultima_leitura = tempo_atual;
  }
  
  // Atualização do display a cada 2 segundos
  if (tempo_atual - ultima_atualizacao_display >= INTERVALO_DISPLAY) {
    atualizarDisplay();
    ultima_atualizacao_display = tempo_atual;
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
  
  // Atualizar estrutura de dados
  dados_sensor.temperatura = temperatura;
  dados_sensor.umidade_ar = umidade_ar;
  dados_sensor.umidade_solo = umidade_solo;
  dados_sensor.irrigacao_ativa = irrigacao_ativa;
  dados_sensor.timestamp = millis();
  
  // Log dos dados
  Serial.println("=== Leitura dos Sensores ===");
  Serial.printf("Temperatura: %.1f°C\n", temperatura);
  Serial.printf("Umidade do Ar: %.1f%%\n", umidade_ar);
  Serial.printf("Umidade do Solo: %d%%\n", umidade_solo);
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

void controlarIrrigacao() {
  // Lógica de controle de irrigação
  if (umidade_solo < UMIDADE_SOLO_MIN && !irrigacao_ativa) {
    // Ativar irrigação
    digitalWrite(RELAY_PIN, HIGH);
    irrigacao_ativa = true;
    Serial.println("IRRIGAÇÃO ATIVADA");
  } else if (umidade_solo > UMIDADE_SOLO_MAX && irrigacao_ativa) {
    // Desativar irrigação
    digitalWrite(RELAY_PIN, LOW);
    irrigacao_ativa = false;
    Serial.println("IRRIGAÇÃO DESATIVADA");
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
  
  // Linha 3: Umidade do Solo e Status da Irrigação
  lcd.setCursor(0, 2);
  lcd.printf("Solo:%d%% %s", umidade_solo, irrigacao_ativa ? "IRRIG" : "    ");
  
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

// Função para exibir menu de configuração (opcional)
void exibirMenuConfiguracao() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("=== CONFIGURACAO ===");
  lcd.setCursor(0, 1);
  lcd.print("1. Ajustar Limites");
  lcd.setCursor(0, 2);
  lcd.print("2. Testar Sensores");
  lcd.setCursor(0, 3);
  lcd.print("3. Reset Sistema");
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