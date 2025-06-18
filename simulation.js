// FarmTech Solutions - Simulação de Sensores
// Script para simular dados dos sensores no Wokwi

// Elementos da simulação
const esp32 = document.querySelector('wokwi-esp32-devkit-v1');
const lcd = document.querySelector('wokwi-lcd-i2c');
const dht22 = document.querySelector('wokwi-dht22');
const soilMoisture = document.querySelector('wokwi-soil-moisture-sensor');
const relay = document.querySelector('wokwi-relay-module');

// Variáveis de simulação
let temperatura = 25.0;
let umidadeAr = 60.0;
let umidadeSolo = 45.0;
let irrigacaoAtiva = false;
let statusSistema = "OK";

// Configurações de simulação
const config = {
  intervaloLeitura: 5000,    // 5 segundos
  intervaloDisplay: 2000,    // 2 segundos
  variacaoTemp: 2.0,         // Variação máxima de temperatura
  variacaoUmidade: 5.0,      // Variação máxima de umidade
  tempMax: 35.0,
  tempMin: 10.0,
  umidadeSoloMin: 30,
  umidadeSoloMax: 80
};

// Função para gerar dados simulados realistas
function gerarDadosSimulados() {
  // Simular variação de temperatura (ciclo diário)
  const hora = new Date().getHours();
  const tempBase = 20 + 10 * Math.sin((hora - 6) * Math.PI / 12);
  temperatura = tempBase + (Math.random() - 0.5) * config.variacaoTemp;
  
  // Simular umidade do ar (inversamente proporcional à temperatura)
  umidadeAr = 80 - (temperatura - 15) * 2 + (Math.random() - 0.5) * config.variacaoUmidade;
  umidadeAr = Math.max(20, Math.min(95, umidadeAr));
  
  // Simular umidade do solo (afetada pela irrigação)
  if (irrigacaoAtiva) {
    umidadeSolo += Math.random() * 3; // Aumenta quando irrigação está ativa
  } else {
    umidadeSolo -= Math.random() * 2; // Diminui naturalmente
  }
  umidadeSolo = Math.max(10, Math.min(95, umidadeSolo));
  
  // Atualizar sensores simulados
  if (dht22) {
    dht22.setTemperature(temperatura);
    dht22.setHumidity(umidadeAr);
  }
  
  if (soilMoisture) {
    // Converter porcentagem para valor analógico (0-4095)
    const valorAnalogico = Math.round((100 - umidadeSolo) * 40.95);
    soilMoisture.setMoisture(valorAnalogico);
  }
  
  // Análise de status
  analisarStatus();
  
  console.log(`Dados simulados - Temp: ${temperatura.toFixed(1)}°C, Umid Ar: ${umidadeAr.toFixed(1)}%, Solo: ${umidadeSolo.toFixed(1)}%, Irrigação: ${irrigacaoAtiva}`);
}

// Função para analisar status do sistema
function analisarStatus() {
  if (temperatura > config.tempMax) {
    statusSistema = "ALERTA: TEMP ALTA";
  } else if (temperatura < config.tempMin) {
    statusSistema = "ALERTA: TEMP BAIXA";
  } else if (umidadeSolo < config.umidadeSoloMin) {
    statusSistema = "ALERTA: SOLO SECO";
  } else if (umidadeSolo > config.umidadeSoloMax) {
    statusSistema = "ALERTA: SOLO MUITO UMIDO";
  } else {
    statusSistema = "OK";
  }
}

// Função para controlar irrigação
function controlarIrrigacao() {
  if (umidadeSolo < config.umidadeSoloMin && !irrigacaoAtiva) {
    irrigacaoAtiva = true;
    if (relay) {
      relay.setRelayState(true);
    }
    console.log("IRRIGAÇÃO ATIVADA");
  } else if (umidadeSolo > config.umidadeSoloMax && irrigacaoAtiva) {
    irrigacaoAtiva = false;
    if (relay) {
      relay.setRelayState(false);
    }
    console.log("IRRIGAÇÃO DESATIVADA");
  }
}

// Função para atualizar display LCD
function atualizarDisplay() {
  if (!lcd) return;
  
  // Limpar display
  lcd.clear();
  
  // Linha 1: Título do sistema
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Monitor");
  
  // Linha 2: Temperatura e Umidade do Ar
  lcd.setCursor(0, 1);
  lcd.print(`T:${temperatura.toFixed(1)}C U:${umidadeAr.toFixed(0)}%`);
  
  // Linha 3: Umidade do Solo e Status da Irrigação
  lcd.setCursor(0, 2);
  const statusIrrigacao = irrigacaoAtiva ? "IRRIG" : "    ";
  lcd.print(`Solo:${umidadeSolo.toFixed(0)}% ${statusIrrigacao}`);
  
  // Linha 4: Status do sistema
  lcd.setCursor(0, 3);
  if (statusSistema.length > 20) {
    lcd.print(statusSistema.substring(0, 20));
  } else {
    lcd.print(statusSistema);
  }
  
  // Indicador visual de irrigação
  if (irrigacaoAtiva) {
    lcd.setCursor(19, 2);
    lcd.print("*");
  }
}

// Função para exibir informações detalhadas no console
function exibirInfoDetalhada() {
  console.log("=== FARM TECH SOLUTIONS - INFO DETALHADA ===");
  console.log(`Temperatura: ${temperatura.toFixed(2)}°C`);
  console.log(`Umidade do Ar: ${umidadeAr.toFixed(1)}%`);
  console.log(`Umidade do Solo: ${umidadeSolo.toFixed(1)}%`);
  console.log(`Irrigação: ${irrigacaoAtiva ? "ATIVA" : "INATIVA"}`);
  console.log(`Status: ${statusSistema}`);
  console.log(`Uptime: ${Math.floor(Date.now() / 1000)}s`);
  console.log("=============================================");
}

// Função para simular eventos de alerta
function simularEventos() {
  // Simular chuva (aumenta umidade do solo rapidamente)
  if (Math.random() < 0.01) { // 1% de chance a cada ciclo
    console.log("🌧️ Simulando chuva...");
    umidadeSolo = Math.min(95, umidadeSolo + 20);
    umidadeAr = Math.min(95, umidadeAr + 15);
  }
  
  // Simular onda de calor
  if (Math.random() < 0.005) { // 0.5% de chance a cada ciclo
    console.log("🔥 Simulando onda de calor...");
    temperatura = Math.min(40, temperatura + 8);
    umidadeAr = Math.max(20, umidadeAr - 10);
  }
  
  // Simular seca
  if (Math.random() < 0.005) { // 0.5% de chance a cada ciclo
    console.log("☀️ Simulando período de seca...");
    umidadeSolo = Math.max(10, umidadeSolo - 15);
    umidadeAr = Math.max(20, umidadeAr - 5);
  }
}

// Função principal de simulação
function executarSimulacao() {
  // Gerar dados simulados
  gerarDadosSimulados();
  
  // Simular eventos aleatórios
  simularEventos();
  
  // Controlar irrigação
  controlarIrrigacao();
  
  // Exibir informações detalhadas a cada 30 segundos
  if (Date.now() % 30000 < 1000) {
    exibirInfoDetalhada();
  }
}

// Função para inicializar a simulação
function inicializarSimulacao() {
  console.log("🚀 Iniciando simulação FarmTech Solutions...");
  console.log("📊 Sistema de monitoramento com display LCD I2C");
  console.log("🌱 Sensores: DHT22, Umidade do Solo, Controle de Irrigação");
  
  // Configurar intervalos
  setInterval(executarSimulacao, config.intervaloLeitura);
  setInterval(atualizarDisplay, config.intervaloDisplay);
  
  // Primeira execução
  executarSimulacao();
  atualizarDisplay();
  
  console.log("✅ Simulação iniciada com sucesso!");
}

// Aguardar carregamento da página e iniciar simulação
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(inicializarSimulacao, 2000); // Aguardar 2 segundos para carregar componentes
});

// Funções de utilidade para debug
window.farmTechDebug = {
  // Forçar valores específicos
  setTemperatura: (temp) => {
    temperatura = parseFloat(temp);
    console.log(`Temperatura forçada para: ${temperatura}°C`);
  },
  
  setUmidadeAr: (umid) => {
    umidadeAr = parseFloat(umid);
    console.log(`Umidade do ar forçada para: ${umidadeAr}%`);
  },
  
  setUmidadeSolo: (umid) => {
    umidadeSolo = parseFloat(umid);
    console.log(`Umidade do solo forçada para: ${umidadeSolo}%`);
  },
  
  forcarIrrigacao: (ativa) => {
    irrigacaoAtiva = ativa;
    if (relay) {
      relay.setRelayState(ativa);
    }
    console.log(`Irrigação forçada para: ${ativa ? "ATIVA" : "INATIVA"}`);
  },
  
  // Exibir status atual
  status: () => {
    exibirInfoDetalhada();
  },
  
  // Simular eventos específicos
  simularChuva: () => {
    umidadeSolo = Math.min(95, umidadeSolo + 20);
    umidadeAr = Math.min(95, umidadeAr + 15);
    console.log("🌧️ Chuva simulada!");
  },
  
  simularCalor: () => {
    temperatura = Math.min(40, temperatura + 8);
    umidadeAr = Math.max(20, umidadeAr - 10);
    console.log("🔥 Onda de calor simulada!");
  }
};

console.log("🔧 Funções de debug disponíveis em window.farmTechDebug");
console.log("📝 Use farmTechDebug.status() para ver informações detalhadas"); 