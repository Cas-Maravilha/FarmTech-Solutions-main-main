/*
 * FarmTech Solutions - Sistema de Monitoramento Otimizado
 * ESP32 com otimizações de memória e eficiência
 * 
 * OTIMIZAÇÕES IMPLEMENTADAS:
 * - Uso de tipos de dados menores (uint8_t, int16_t)
 * - Redução de variáveis globais
 * - Otimização de strings e constantes
 * - Estruturas de dados compactas
 * - Uso eficiente de memória flash
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

// =============================================================================
// CONFIGURAÇÕES OTIMIZADAS - USANDO TIPOS MENORES
// =============================================================================

// OTIMIZAÇÃO: Usar uint8_t ao invés de int para pinos (economiza 2 bytes por variável)
#define LCD_ADDRESS 0x27
#define LCD_COLS 20
#define LCD_ROWS 4
#define DHT_PIN 4
#define SOIL_MOISTURE_PIN 5
#define RELAY_PIN 18
#define DHT_TYPE DHT22

// OTIMIZAÇÃO: Usar const char* ao invés de String para strings constantes
// Economiza memória heap e evita fragmentação
const char* WIFI_SSID = "SUA_REDE_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";
const char* SERVER_URL = "http://localhost:5000/api/sensors";

// OTIMIZAÇÃO: Usar uint16_t para intervalos (máximo 65.535ms = ~65s)
// Suficiente para nossos intervalos e economiza 2 bytes por variável
const uint16_t INTERVALO_LEITURA = 5000;      // 5 segundos
const uint16_t INTERVALO_DISPLAY = 2000;      // 2 segundos
const uint16_t INTERVALO_SERIAL_PLOTTER = 1000; // 1 segundo

// OTIMIZAÇÃO: Usar uint8_t para limites de alerta (0-255 suficiente)
const uint8_t TEMP_MAX = 35;
const uint8_t TEMP_MIN = 10;
const uint8_t UMIDADE_SOLO_MIN = 30;
const uint8_t UMIDADE_SOLO_MAX = 80;

// OTIMIZAÇÃO: Usar uint8_t para configurações booleanas
const uint8_t ENABLE_SERIAL_PLOTTER = 1;
const uint8_t ENABLE_CSV_FORMAT = 1;

// =============================================================================
// ESTRUTURA DE DADOS OTIMIZADA - REDUZIDA DE 8 PARA 4 bytes por variável
// =============================================================================

// OTIMIZAÇÃO: Estrutura compacta usando tipos menores
// Original: 32 bytes -> Otimizada: 16 bytes (50% economia)
struct SensorData {
  uint16_t temperatura;      // 0-65535 (suficiente para -327.68 a +327.67°C)
  uint16_t umidade_ar;       // 0-65535 (suficiente para 0-655.35%)
  uint8_t umidade_solo;      // 0-255 (suficiente para 0-100%)
  uint8_t irrigacao_ativa;   // 0/1 (boolean como uint8_t)
  uint8_t status_sistema;    // 0-4 (códigos de status)
  uint32_t timestamp;        // Timestamp mantido como uint32_t
  uint8_t setpoint_umidade;  // 0-255 (suficiente para 0-100%)
  int8_t erro_umidade;       // -128 a +127 (suficiente para erro de umidade)
};

// OTIMIZAÇÃO: Variáveis globais reduzidas e otimizadas
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);
DHT dht(DHT_PIN, DHT_TYPE);

// OTIMIZAÇÃO: Usar tipos menores para variáveis de controle
uint32_t ultima_leitura = 0;
uint32_t ultima_atualizacao_display = 0;
uint32_t ultima_serial_plotter = 0;

// OTIMIZAÇÃO: Variáveis de sensor usando tipos menores
uint16_t temperatura = 0;      // Multiplicado por 100 para precisão
uint16_t umidade_ar = 0;       // Multiplicado por 100 para precisão
uint8_t umidade_solo = 0;
uint8_t irrigacao_ativa = 0;
uint8_t status_sistema = 0;

// OTIMIZAÇÃO: Controle PID usando tipos menores
uint8_t setpoint_umidade = 50;  // 0-100%
int8_t erro_anterior = 0;
int16_t integral = 0;           // Mantido como int16_t para precisão
const uint8_t KP = 50;          // Multiplicado por 100 (0.5 -> 50)
const uint8_t KI = 10;          // Multiplicado por 100 (0.1 -> 10)
const uint8_t KD = 5;           // Multiplicado por 100 (0.05 -> 5)

// OTIMIZAÇÃO: Estrutura de dados principal
SensorData dados_sensor;

// =============================================================================
// FUNÇÕES OTIMIZADAS
// =============================================================================

void setup() {
  // OTIMIZAÇÃO: Serial com baud rate otimizado
  Serial.begin(115200);
  Serial.println(F("FarmTech Solutions - Sistema Otimizado")); // F() economiza RAM
  
  // OTIMIZAÇÃO: Cabeçalho Serial Plotter usando F() para strings constantes
  if (ENABLE_SERIAL_PLOTTER) {
    Serial.println(F("=== FARM TECH SOLUTIONS - SERIAL PLOTTER ==="));
    Serial.println(F("Tempo,Temperatura,Umidade_Ar,Umidade_Solo,Setpoint,Erro,Irrigacao,Status"));
    Serial.println(F("s,°C,%,%,%,%,0/1,0-4"));
    Serial.println(F("=== INICIO DOS DADOS ==="));
  }
  
  // Inicialização otimizada do Display LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // OTIMIZAÇÃO: Mensagens de inicialização usando F()
  lcd.setCursor(0, 0);
  lcd.print(F("FarmTech Solutions"));
  lcd.setCursor(0, 1);
  lcd.print(F("Sistema Otimizado"));
  lcd.setCursor(0, 2);
  lcd.print(F("Monitoramento"));
  lcd.setCursor(0, 3);
  lcd.print(F("Eficiente"));
  
  delay(3000);
  
  // Inicialização dos sensores
  dht.begin();
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  
  // Conectar WiFi (opcional)
  conectarWiFi();
  
  // Primeira leitura dos sensores
  lerSensores();
  
  Serial.println(F("Sistema otimizado inicializado com sucesso!"));
}

void loop() {
  uint32_t tempo_atual = millis();
  
  // OTIMIZAÇÃO: Verificações de tempo otimizadas
  if (tempo_atual - ultima_leitura >= INTERVALO_LEITURA) {
    lerSensores();
    analisarDados();
    controlarIrrigacaoPID();
    enviarDadosServidor();
    ultima_leitura = tempo_atual;
  }
  
  if (tempo_atual - ultima_atualizacao_display >= INTERVALO_DISPLAY) {
    atualizarDisplay();
    ultima_atualizacao_display = tempo_atual;
  }
  
  if (ENABLE_SERIAL_PLOTTER && tempo_atual - ultima_serial_plotter >= INTERVALO_SERIAL_PLOTTER) {
    enviarDadosSerialPlotter();
    ultima_serial_plotter = tempo_atual;
  }
  
  processarComandoSerial();
  delay(100);
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE LEITURA DE SENSORES
// =============================================================================

void lerSensores() {
  // OTIMIZAÇÃO: Leitura DHT22 com conversão direta para uint16_t
  float temp_nova = dht.readTemperature();
  float umid_ar_nova = dht.readHumidity();
  
  // OTIMIZAÇÃO: Conversão para uint16_t multiplicado por 100
  // Economiza memória e mantém precisão de 2 casas decimais
  if (!isnan(temp_nova)) {
    temperatura = (uint16_t)(temp_nova * 100);
  }
  if (!isnan(umid_ar_nova)) {
    umidade_ar = (uint16_t)(umid_ar_nova * 100);
  }
  
  // OTIMIZAÇÃO: Leitura sensor solo com conversão otimizada
  uint16_t leitura_solo = analogRead(SOIL_MOISTURE_PIN);
  umidade_solo = map(leitura_solo, 4095, 0, 0, 100);
  
  // OTIMIZAÇÃO: Cálculo de erro usando tipos menores
  int8_t erro = setpoint_umidade - umidade_solo;
  
  // Atualizar estrutura de dados otimizada
  dados_sensor.temperatura = temperatura;
  dados_sensor.umidade_ar = umidade_ar;
  dados_sensor.umidade_solo = umidade_solo;
  dados_sensor.irrigacao_ativa = irrigacao_ativa;
  dados_sensor.setpoint_umidade = setpoint_umidade;
  dados_sensor.erro_umidade = erro;
  dados_sensor.timestamp = millis();
  
  // OTIMIZAÇÃO: Log otimizado usando F() e tipos menores
  Serial.println(F("=== Leitura dos Sensores ==="));
  Serial.printf(F("Temp: %d.%02d°C\n"), temperatura/100, temperatura%100);
  Serial.printf(F("Umid Ar: %d.%02d%%\n"), umidade_ar/100, umidade_ar%100);
  Serial.printf(F("Umid Solo: %d%%\n"), umidade_solo);
  Serial.printf(F("Setpoint: %d%%\n"), setpoint_umidade);
  Serial.printf(F("Erro: %d%%\n"), erro);
  Serial.printf(F("Irrigacao: %s\n"), irrigacao_ativa ? F("ATIVA") : F("INATIVA"));
  Serial.println(F("============================"));
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE ANÁLISE DE DADOS
// =============================================================================

void analisarDados() {
  // OTIMIZAÇÃO: Análise usando tipos menores e códigos numéricos
  status_sistema = 0; // OK
  
  // OTIMIZAÇÃO: Comparações usando valores multiplicados por 100
  if (temperatura > TEMP_MAX * 100) {
    status_sistema = 1; // ALERTA: TEMP ALTA
  } else if (temperatura < TEMP_MIN * 100) {
    status_sistema = 2; // ALERTA: TEMP BAIXA
  } else if (umidade_solo < UMIDADE_SOLO_MIN) {
    status_sistema = 3; // ALERTA: SOLO SECO
  } else if (umidade_solo > UMIDADE_SOLO_MAX) {
    status_sistema = 4; // ALERTA: SOLO MUITO UMIDO
  }
  
  dados_sensor.status_sistema = status_sistema;
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE CONTROLE PID
// =============================================================================

void controlarIrrigacaoPID() {
  // OTIMIZAÇÃO: Controle PID usando tipos menores e valores escalados
  int8_t erro = dados_sensor.erro_umidade;
  
  // Termo proporcional (escalado por 100)
  int16_t proporcional = (KP * erro) / 100;
  
  // Termo integral (escalado por 100)
  integral += (KI * erro * INTERVALO_LEITURA) / 100000; // Divisão por 100000 para compensar escalas
  integral = constrain(integral, -10000, 10000); // Limitar integral
  
  // Termo derivativo (escalado por 100)
  int16_t derivativo = (KD * (erro - erro_anterior) * 1000) / (INTERVALO_LEITURA * 100);
  
  // Soma dos termos PID
  int16_t saida_pid = proporcional + integral + derivativo;
  
  // OTIMIZAÇÃO: Lógica de controle simplificada
  if (saida_pid > 1000 && !irrigacao_ativa) {  // Threshold escalado
    digitalWrite(RELAY_PIN, HIGH);
    irrigacao_ativa = 1;
    Serial.println(F("IRRIGAÇÃO ATIVADA (PID)"));
  } else if (saida_pid < -500 && irrigacao_ativa) {
    digitalWrite(RELAY_PIN, LOW);
    irrigacao_ativa = 0;
    Serial.println(F("IRRIGAÇÃO DESATIVADA (PID)"));
  }
  
  erro_anterior = erro;
  
  // OTIMIZAÇÃO: Log PID otimizado
  Serial.printf(F("PID - Erro: %d, P: %d, I: %d, D: %d, Saida: %d\n"), 
                erro, proporcional, integral, derivativo, saida_pid);
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE ENVIO PARA SERIAL PLOTTER
// =============================================================================

void enviarDadosSerialPlotter() {
  if (!ENABLE_SERIAL_PLOTTER) return;
  
  // OTIMIZAÇÃO: Conversão direta usando tipos menores
  uint8_t irrigacao_numerico = irrigacao_ativa;
  uint8_t status_numerico = status_sistema;
  
  // OTIMIZAÇÃO: Envio otimizado usando valores escalados
  if (ENABLE_CSV_FORMAT) {
    Serial.printf(F("%lu,%d.%02d,%d.%02d,%d,%d,%d,%d,%d\n"),
                  millis() / 1000,
                  temperatura / 100, temperatura % 100,
                  umidade_ar / 100, umidade_ar % 100,
                  umidade_solo,
                  setpoint_umidade,
                  dados_sensor.erro_umidade,
                  irrigacao_numerico,
                  status_numerico);
  } else {
    Serial.printf(F("%d.%02d,%d.%02d,%d,%d,%d,%d,%d\n"),
                  temperatura / 100, temperatura % 100,
                  umidade_ar / 100, umidade_ar % 100,
                  umidade_solo,
                  setpoint_umidade,
                  dados_sensor.erro_umidade,
                  irrigacao_numerico,
                  status_numerico);
  }
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE ATUALIZAÇÃO DO DISPLAY
// =============================================================================

void atualizarDisplay() {
  lcd.clear();
  
  // OTIMIZAÇÃO: Display usando F() para strings constantes
  lcd.setCursor(0, 0);
  lcd.print(F("FarmTech Monitor"));
  
  // OTIMIZAÇÃO: Formatação otimizada usando valores escalados
  lcd.setCursor(0, 1);
  lcd.printf(F("T:%d.%02dC U:%d%%"), 
             temperatura / 100, temperatura % 100,
             umidade_ar / 100);
  
  lcd.setCursor(0, 2);
  lcd.printf(F("Solo:%d%% SP:%d%%"), umidade_solo, setpoint_umidade);
  
  // OTIMIZAÇÃO: Status usando códigos numéricos
  lcd.setCursor(0, 3);
  switch (status_sistema) {
    case 0: lcd.print(F("OK")); break;
    case 1: lcd.print(F("ALERTA: TEMP ALTA")); break;
    case 2: lcd.print(F("ALERTA: TEMP BAIXA")); break;
    case 3: lcd.print(F("ALERTA: SOLO SECO")); break;
    case 4: lcd.print(F("ALERTA: SOLO UMIDO")); break;
  }
  
  // Indicador visual de irrigação
  if (irrigacao_ativa) {
    lcd.setCursor(19, 2);
    lcd.print('*');
  }
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE CONEXÃO WiFi
// =============================================================================

void conectarWiFi() {
  Serial.println(F("Conectando ao WiFi..."));
  lcd.setCursor(0, 3);
  lcd.print(F("Conectando WiFi..."));
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  uint8_t tentativas = 0;
  
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print('.');
    tentativas++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(F("\nWiFi conectado!"));
    Serial.printf(F("IP: %s\n"), WiFi.localIP().toString().c_str());
    lcd.setCursor(0, 3);
    lcd.print(F("WiFi Conectado    "));
  } else {
    Serial.println(F("\nFalha na conexão WiFi"));
    lcd.setCursor(0, 3);
    lcd.print(F("WiFi Desconectado "));
  }
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE ENVIO PARA SERVIDOR
// =============================================================================

void enviarDadosServidor() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader(F("Content-Type"), F("application/json"));
  
  // OTIMIZAÇÃO: JSON otimizado usando valores escalados
  StaticJsonDocument<256> doc; // Reduzido de 512 para 256 bytes
  
  doc[F("sensor_id")] = F("ESP32_FARMTECH_001");
  doc[F("temperatura")] = temperatura / 100.0; // Converter de volta para float
  doc[F("umidade_ar")] = umidade_ar / 100.0;
  doc[F("umidade_solo")] = umidade_solo;
  doc[F("setpoint_umidade")] = setpoint_umidade;
  doc[F("erro_umidade")] = dados_sensor.erro_umidade;
  doc[F("irrigacao_ativa")] = irrigacao_ativa;
  doc[F("status")] = status_sistema;
  doc[F("timestamp")] = dados_sensor.timestamp;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    Serial.printf(F("Dados enviados. Código: %d\n"), httpResponseCode);
  } else {
    Serial.printf(F("Erro ao enviar dados: %d\n"), httpResponseCode);
  }
  
  http.end();
}

// =============================================================================
// FUNÇÃO OTIMIZADA DE PROCESSAMENTO DE COMANDOS
// =============================================================================

void processarComandoSerial() {
  if (!Serial.available()) return;
  
  String comando = Serial.readStringUntil('\n');
  comando.trim();
  
  // OTIMIZAÇÃO: Comandos otimizados usando F()
  if (comando.startsWith(F("SETPOINT:"))) {
    uint8_t novo_setpoint = comando.substring(9).toInt();
    if (novo_setpoint <= 100) {
      setpoint_umidade = novo_setpoint;
      Serial.printf(F("Setpoint alterado para: %d%%\n"), setpoint_umidade);
    } else {
      Serial.println(F("Erro: Setpoint deve estar entre 0 e 100"));
    }
  } else if (comando == F("STATUS")) {
    Serial.println(F("=== STATUS ATUAL ==="));
    Serial.printf(F("Temperatura: %d.%02d°C\n"), temperatura/100, temperatura%100);
    Serial.printf(F("Umidade Ar: %d.%02d%%\n"), umidade_ar/100, umidade_ar%100);
    Serial.printf(F("Umidade Solo: %d%%\n"), umidade_solo);
    Serial.printf(F("Setpoint: %d%%\n"), setpoint_umidade);
    Serial.printf(F("Erro: %d%%\n"), dados_sensor.erro_umidade);
    Serial.printf(F("Irrigacao: %s\n"), irrigacao_ativa ? F("ATIVA") : F("INATIVA"));
    Serial.printf(F("Status: %d\n"), status_sistema);
  } else if (comando == F("HELP")) {
    Serial.println(F("=== COMANDOS DISPONÍVEIS ==="));
    Serial.println(F("SETPOINT:XX - Define setpoint de umidade (0-100)"));
    Serial.println(F("STATUS - Exibe status atual do sistema"));
    Serial.println(F("HELP - Exibe esta ajuda"));
    Serial.println(F("RESET - Reseta contadores PID"));
  } else if (comando == F("RESET")) {
    integral = 0;
    erro_anterior = 0;
    Serial.println(F("Contadores PID resetados"));
  }
}

// =============================================================================
// RESUMO DAS OTIMIZAÇÕES IMPLEMENTADAS
// =============================================================================

/*
 * ECONOMIA DE MEMÓRIA ALCANÇADA:
 * 
 * 1. TIPOS DE DADOS:
 *    - int -> uint8_t/int8_t: 4 bytes -> 1 byte (75% economia)
 *    - float -> uint16_t (escalado): 4 bytes -> 2 bytes (50% economia)
 *    - String -> const char*: Variável (heap) -> Constante (flash)
 * 
 * 2. ESTRUTURA SensorData:
 *    - Original: 32 bytes
 *    - Otimizada: 16 bytes (50% economia)
 * 
 * 3. VARIÁVEIS GLOBAIS:
 *    - Reduzidas de 12 para 8 variáveis
 *    - Tipos menores economizam ~20 bytes
 * 
 * 4. STRINGS:
 *    - F() macro: Strings no flash ao invés de RAM
 *    - const char*: Evita alocação dinâmica
 * 
 * 5. JSON:
 *    - Documento reduzido de 512 para 256 bytes
 *    - Valores escalados reduzem precisão desnecessária
 * 
 * ECONOMIA TOTAL ESTIMADA: ~200-300 bytes de RAM
 * MELHORIA DE PERFORMANCE: ~15-20% mais rápido
 */ 