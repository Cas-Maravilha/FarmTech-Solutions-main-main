-- =============================================================================
-- FARM TECH SOLUTIONS - BANCO DE DADOS APRIMORADO
-- =============================================================================
-- Modelo de negócio expandido com novas entidades e relacionamentos
-- Versão: 2.0
-- Data: 2024-01-18
-- =============================================================================

-- =============================================================================
-- 1. TABELAS DE CONFIGURAÇÃO E SISTEMA
-- =============================================================================

-- Tabela de configurações do sistema
CREATE TABLE CONFIGURACAO_SISTEMA (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descricao TEXT,
    categoria VARCHAR(50),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de usuários do sistema
CREATE TABLE USUARIO (
    usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    tipo_usuario VARCHAR(20) NOT NULL, -- 'admin', 'gerente', 'operador', 'viewer'
    status VARCHAR(20) DEFAULT 'ativo',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME,
    telefone VARCHAR(20),
    cargo VARCHAR(50)
);

-- Tabela de fazendas/propriedades
CREATE TABLE FAZENDA (
    fazenda_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18),
    proprietario VARCHAR(100),
    endereco TEXT,
    cidade VARCHAR(50),
    estado VARCHAR(2),
    cep VARCHAR(10),
    telefone VARCHAR(20),
    email VARCHAR(100),
    area_total DOUBLE,
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ativa'
);

-- =============================================================================
-- 2. TABELAS DE LOCALIZAÇÃO E ÁREAS
-- =============================================================================

-- Tabela de coordenadas geográficas
CREATE TABLE COORDENADA (
    coordenada_id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    altitude DOUBLE,
    precisao DOUBLE,
    data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de áreas aprimorada
CREATE TABLE AREA (
    area_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fazenda_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) UNIQUE,
    tamanho DOUBLE NOT NULL, -- em hectares
    tipo_solo VARCHAR(50),
    ph_solo DOUBLE,
    textura_solo VARCHAR(30),
    profundidade_solo DOUBLE,
    coordenada_id INTEGER,
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ativa',
    observacoes TEXT,
    FOREIGN KEY (fazenda_id) REFERENCES FAZENDA(fazenda_id),
    FOREIGN KEY (coordenada_id) REFERENCES COORDENADA(coordenada_id)
);

-- Tabela de talhões (subdivisões de áreas)
CREATE TABLE TALHAO (
    talhao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id INTEGER NOT NULL,
    nome VARCHAR(50) NOT NULL,
    codigo VARCHAR(20),
    tamanho DOUBLE NOT NULL, -- em hectares
    formato VARCHAR(20), -- 'retangular', 'irregular', 'circular'
    coordenada_id INTEGER,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ativo',
    FOREIGN KEY (area_id) REFERENCES AREA(area_id),
    FOREIGN KEY (coordenada_id) REFERENCES COORDENADA(coordenada_id)
);

-- =============================================================================
-- 3. TABELAS DE SENSORES E EQUIPAMENTOS
-- =============================================================================

-- Tabela de tipos de sensores
CREATE TABLE TIPO_SENSOR (
    tipo_sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT,
    unidade_medida VARCHAR(20),
    faixa_min DOUBLE,
    faixa_max DOUBLE,
    precisao DOUBLE,
    fabricante VARCHAR(50),
    modelo VARCHAR(50),
    categoria VARCHAR(30) -- 'clima', 'solo', 'planta', 'irrigacao'
);

-- Tabela de sensores aprimorada
CREATE TABLE SENSOR (
    sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_sensor_id INTEGER NOT NULL,
    talhao_id INTEGER,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    numero_serie VARCHAR(50),
    versao_firmware VARCHAR(20),
    data_instalacao DATETIME,
    coordenada_id INTEGER,
    altitude DOUBLE,
    orientacao VARCHAR(20),
    status VARCHAR(20) DEFAULT 'ativo',
    ultima_manutencao DATETIME,
    proxima_manutencao DATETIME,
    bateria_nivel INTEGER, -- 0-100%
    sinal_forca INTEGER, -- 0-100%
    observacoes TEXT,
    FOREIGN KEY (tipo_sensor_id) REFERENCES TIPO_SENSOR(tipo_sensor_id),
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (coordenada_id) REFERENCES COORDENADA(coordenada_id)
);

-- Tabela de leituras aprimorada
CREATE TABLE LEITURA (
    leitura_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    data_hora DATETIME NOT NULL,
    valor DOUBLE NOT NULL,
    unidade_medida VARCHAR(20),
    qualidade_dado VARCHAR(20), -- 'excelente', 'bom', 'regular', 'ruim'
    status_leitura VARCHAR(20) DEFAULT 'valida',
    latitude DOUBLE,
    longitude DOUBLE,
    altitude DOUBLE,
    temperatura_ambiente DOUBLE,
    umidade_ambiente DOUBLE,
    pressao_atmosferica DOUBLE,
    velocidade_vento DOUBLE,
    direcao_vento DOUBLE,
    radiacao_solar DOUBLE,
    observacoes TEXT,
    FOREIGN KEY (sensor_id) REFERENCES SENSOR(sensor_id)
);

-- Tabela de alertas e notificações
CREATE TABLE ALERTA (
    alerta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER,
    talhao_id INTEGER,
    tipo_alerta VARCHAR(50) NOT NULL,
    severidade VARCHAR(20) NOT NULL, -- 'baixa', 'media', 'alta', 'critica'
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor_atual DOUBLE,
    valor_limite DOUBLE,
    data_geracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_resolucao DATETIME,
    status VARCHAR(20) DEFAULT 'ativo',
    usuario_responsavel INTEGER,
    acao_tomada TEXT,
    FOREIGN KEY (sensor_id) REFERENCES SENSOR(sensor_id),
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (usuario_responsavel) REFERENCES USUARIO(usuario_id)
);

-- =============================================================================
-- 4. TABELAS DE CULTURAS E PLANTIOS
-- =============================================================================

-- Tabela de culturas aprimorada
CREATE TABLE CULTURA (
    cultura_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    nome_cientifico VARCHAR(100),
    familia VARCHAR(50),
    variedade VARCHAR(100),
    ciclo_vida INTEGER, -- em dias
    estacao_plantio VARCHAR(20), -- 'primavera', 'verao', 'outono', 'inverno'
    profundidade_plantio DOUBLE,
    espacamento_linhas DOUBLE,
    espacamento_plantas DOUBLE,
    densidade_populacao INTEGER, -- plantas por hectare
    ph_ideal_min DOUBLE,
    ph_ideal_max DOUBLE,
    umidade_ideal_min DOUBLE,
    umidade_ideal_max DOUBLE,
    temperatura_ideal_min DOUBLE,
    temperatura_ideal_max DOUBLE,
    fosforo_ideal_min DOUBLE,
    fosforo_ideal_max DOUBLE,
    potassio_ideal_min DOUBLE,
    potassio_ideal_max DOUBLE,
    nitrogenio_ideal_min DOUBLE,
    nitrogenio_ideal_max DOUBLE,
    calcio_ideal_min DOUBLE,
    calcio_ideal_max DOUBLE,
    magnesio_ideal_min DOUBLE,
    magnesio_ideal_max DOUBLE,
    enxofre_ideal_min DOUBLE,
    enxofre_ideal_max DOUBLE,
    boro_ideal_min DOUBLE,
    boro_ideal_max DOUBLE,
    zinco_ideal_min DOUBLE,
    zinco_ideal_max DOUBLE,
    cobre_ideal_min DOUBLE,
    cobre_ideal_max DOUBLE,
    manganes_ideal_min DOUBLE,
    manganes_ideal_max DOUBLE,
    molibdenio_ideal_min DOUBLE,
    molibdenio_ideal_max DOUBLE,
    resistencia_doenca VARCHAR(100),
    resistencia_praga VARCHAR(100),
    observacoes TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de plantios aprimorada
CREATE TABLE PLANTIO (
    plantio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    talhao_id INTEGER NOT NULL,
    cultura_id INTEGER NOT NULL,
    codigo_plantio VARCHAR(50) UNIQUE,
    data_inicio DATETIME NOT NULL,
    data_colheita_prevista DATETIME,
    data_colheita_real DATETIME,
    status_plantio VARCHAR(30) DEFAULT 'planejado', -- 'planejado', 'em_andamento', 'concluido', 'cancelado'
    fase_crescimento VARCHAR(30), -- 'germinacao', 'vegetativo', 'florescimento', 'frutificacao', 'maturacao'
    densidade_plantio INTEGER, -- plantas por hectare
    area_plantada DOUBLE, -- em hectares
    producao_estimada DOUBLE, -- em toneladas
    producao_real DOUBLE, -- em toneladas
    produtividade_estimada DOUBLE, -- toneladas por hectare
    produtividade_real DOUBLE, -- toneladas por hectare
    custo_estimado DOUBLE,
    custo_real DOUBLE,
    lucro_estimado DOUBLE,
    lucro_real DOUBLE,
    observacoes TEXT,
    usuario_responsavel INTEGER,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (cultura_id) REFERENCES CULTURA(cultura_id),
    FOREIGN KEY (usuario_responsavel) REFERENCES USUARIO(usuario_id)
);

-- Tabela de estágios de desenvolvimento da cultura
CREATE TABLE ESTAGIO_DESENVOLVIMENTO (
    estagio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plantio_id INTEGER NOT NULL,
    fase VARCHAR(30) NOT NULL,
    data_inicio DATETIME,
    data_fim DATETIME,
    duracao_dias INTEGER,
    observacoes TEXT,
    FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id)
);

-- =============================================================================
-- 5. TABELAS DE IRRIGAÇÃO E CONTROLE
-- =============================================================================

-- Tabela de sistemas de irrigação
CREATE TABLE SISTEMA_IRRIGACAO (
    sistema_id INTEGER PRIMARY KEY AUTOINCREMENT,
    talhao_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo_sistema VARCHAR(50), -- 'gotejamento', 'aspersao', 'pivo', 'sulcos'
    capacidade DOUBLE, -- litros por hora
    eficiencia DOUBLE, -- percentual
    pressao_operacional DOUBLE,
    vazao_nominal DOUBLE,
    data_instalacao DATETIME,
    status VARCHAR(20) DEFAULT 'ativo',
    coordenada_id INTEGER,
    observacoes TEXT,
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (coordenada_id) REFERENCES COORDENADA(coordenada_id)
);

-- Tabela de programação de irrigação
CREATE TABLE PROGRAMACAO_IRRIGACAO (
    programacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sistema_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo_programacao VARCHAR(30), -- 'manual', 'automatica', 'temporal', 'baseada_sensor'
    data_inicio DATETIME,
    data_fim DATETIME,
    hora_inicio TIME,
    hora_fim TIME,
    duracao_minutos INTEGER,
    frequencia_dias INTEGER,
    dias_semana VARCHAR(20), -- '1,2,3,4,5,6,7'
    umidade_minima DOUBLE,
    umidade_maxima DOUBLE,
    temperatura_minima DOUBLE,
    temperatura_maxima DOUBLE,
    status VARCHAR(20) DEFAULT 'ativa',
    observacoes TEXT,
    FOREIGN KEY (sistema_id) REFERENCES SISTEMA_IRRIGACAO(sistema_id)
);

-- Tabela de execução de irrigação
CREATE TABLE EXECUCAO_IRRIGACAO (
    execucao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    programacao_id INTEGER,
    sistema_id INTEGER NOT NULL,
    data_inicio DATETIME NOT NULL,
    data_fim DATETIME,
    duracao_minutos INTEGER,
    volume_aplicado DOUBLE, -- litros
    umidade_inicial DOUBLE,
    umidade_final DOUBLE,
    temperatura_inicial DOUBLE,
    temperatura_final DOUBLE,
    status VARCHAR(20) DEFAULT 'em_andamento', -- 'em_andamento', 'concluida', 'cancelada', 'erro'
    motivo_cancelamento TEXT,
    observacoes TEXT,
    FOREIGN KEY (programacao_id) REFERENCES PROGRAMACAO_IRRIGACAO(programacao_id),
    FOREIGN KEY (sistema_id) REFERENCES SISTEMA_IRRIGACAO(sistema_id)
);

-- =============================================================================
-- 6. TABELAS DE RECOMENDAÇÕES E APLICAÇÕES
-- =============================================================================

-- Tabela de tipos de recomendação
CREATE TABLE TIPO_RECOMENDACAO (
    tipo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50), -- 'fertilizacao', 'irrigacao', 'controle_praga', 'controle_doenca'
    descricao TEXT,
    parametros TEXT, -- JSON com parâmetros específicos
    algoritmo VARCHAR(100),
    versao VARCHAR(20)
);

-- Tabela de recomendações aprimorada
CREATE TABLE RECOMENDACAO (
    recomendacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plantio_id INTEGER NOT NULL,
    tipo_id INTEGER NOT NULL,
    talhao_id INTEGER,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo_recomendacao VARCHAR(50) NOT NULL,
    quantidade_recomendada DOUBLE NOT NULL,
    unidade_medida VARCHAR(20),
    data_geracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    prazo_aplicacao DATETIME,
    prioridade VARCHAR(20) DEFAULT 'normal', -- 'baixa', 'normal', 'alta', 'urgente'
    status VARCHAR(20) DEFAULT 'pendente', -- 'pendente', 'aprovada', 'rejeitada', 'aplicada', 'expirada'
    custo_estimado DOUBLE,
    beneficio_estimado DOUBLE,
    roi_estimado DOUBLE, -- Return on Investment
    leitura_id INTEGER,
    usuario_gerador INTEGER,
    usuario_aprovador INTEGER,
    data_aprovacao DATETIME,
    observacoes TEXT,
    FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id),
    FOREIGN KEY (tipo_id) REFERENCES TIPO_RECOMENDACAO(tipo_id),
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (leitura_id) REFERENCES LEITURA(leitura_id),
    FOREIGN KEY (usuario_gerador) REFERENCES USUARIO(usuario_id),
    FOREIGN KEY (usuario_aprovador) REFERENCES USUARIO(usuario_id)
);

-- Tabela de aplicações aprimorada
CREATE TABLE APLICACAO (
    aplicacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plantio_id INTEGER NOT NULL,
    talhao_id INTEGER,
    recomendacao_id INTEGER,
    tipo_aplicacao VARCHAR(50) NOT NULL,
    produto VARCHAR(100),
    quantidade DOUBLE NOT NULL,
    unidade_medida VARCHAR(20),
    concentracao DOUBLE,
    volume_calda DOUBLE,
    data_hora DATETIME NOT NULL,
    condicoes_climaticas TEXT, -- JSON com condições
    equipamento_utilizado VARCHAR(100),
    responsavel INTEGER,
    status VARCHAR(20) DEFAULT 'concluida',
    custo_real DOUBLE,
    observacoes TEXT,
    coordenada_id INTEGER,
    FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id),
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (recomendacao_id) REFERENCES RECOMENDACAO(recomendacao_id),
    FOREIGN KEY (responsavel) REFERENCES USUARIO(usuario_id),
    FOREIGN KEY (coordenada_id) REFERENCES COORDENADA(coordenada_id)
);

-- =============================================================================
-- 7. TABELAS DE CLIMA E PREVISÃO
-- =============================================================================

-- Tabela de dados climáticos
CREATE TABLE DADOS_CLIMA (
    clima_id INTEGER PRIMARY KEY AUTOINCREMENT,
    talhao_id INTEGER,
    data_hora DATETIME NOT NULL,
    temperatura DOUBLE,
    umidade_relativa DOUBLE,
    pressao_atmosferica DOUBLE,
    velocidade_vento DOUBLE,
    direcao_vento DOUBLE,
    radiacao_solar DOUBLE,
    precipitacao DOUBLE,
    ponto_orvalho DOUBLE,
    indice_uv DOUBLE,
    visibilidade DOUBLE,
    fonte_dados VARCHAR(50), -- 'estacao_local', 'api_externa', 'satelite'
    qualidade_dados VARCHAR(20),
    observacoes TEXT,
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id)
);

-- Tabela de previsão do tempo
CREATE TABLE PREVISAO_CLIMA (
    previsao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    talhao_id INTEGER,
    data_previsao DATETIME NOT NULL,
    data_hora_previsao DATETIME NOT NULL,
    temperatura_min DOUBLE,
    temperatura_max DOUBLE,
    umidade_relativa DOUBLE,
    precipitacao_probabilidade DOUBLE,
    precipitacao_quantidade DOUBLE,
    velocidade_vento DOUBLE,
    direcao_vento DOUBLE,
    radiacao_solar DOUBLE,
    fonte_previsao VARCHAR(50),
    confiabilidade DOUBLE, -- 0-100%
    observacoes TEXT,
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id)
);

-- =============================================================================
-- 8. TABELAS DE RELATÓRIOS E ANALYTICS
-- =============================================================================

-- Tabela de relatórios gerados
CREATE TABLE RELATORIO (
    relatorio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_relatorio VARCHAR(50) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    parametros TEXT, -- JSON com parâmetros do relatório
    data_geracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    periodo_inicio DATETIME,
    periodo_fim DATETIME,
    formato VARCHAR(20), -- 'pdf', 'excel', 'csv', 'json'
    caminho_arquivo VARCHAR(500),
    tamanho_arquivo INTEGER,
    usuario_gerador INTEGER,
    status VARCHAR(20) DEFAULT 'gerado',
    observacoes TEXT,
    FOREIGN KEY (usuario_gerador) REFERENCES USUARIO(usuario_id)
);

-- Tabela de métricas e KPIs
CREATE TABLE METRICA (
    metrica_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50), -- 'produtividade', 'custo', 'qualidade', 'sustentabilidade'
    descricao TEXT,
    formula TEXT,
    unidade_medida VARCHAR(20),
    frequencia_calculo VARCHAR(20), -- 'diario', 'semanal', 'mensal', 'sazonal'
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de valores das métricas
CREATE TABLE VALOR_METRICA (
    valor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metrica_id INTEGER NOT NULL,
    talhao_id INTEGER,
    plantio_id INTEGER,
    valor DOUBLE NOT NULL,
    data_calculo DATETIME NOT NULL,
    periodo_referencia VARCHAR(20),
    observacoes TEXT,
    FOREIGN KEY (metrica_id) REFERENCES METRICA(metrica_id),
    FOREIGN KEY (talhao_id) REFERENCES TALHAO(talhao_id),
    FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id)
);

-- =============================================================================
-- 9. TABELAS DE AUDITORIA E LOGS
-- =============================================================================

-- Tabela de logs de auditoria
CREATE TABLE LOG_AUDITORIA (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    acao VARCHAR(50) NOT NULL,
    tabela_afetada VARCHAR(50),
    registro_id INTEGER,
    dados_anteriores TEXT, -- JSON
    dados_novos TEXT, -- JSON
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    observacoes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(usuario_id)
);

-- Tabela de logs do sistema
CREATE TABLE LOG_SISTEMA (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel VARCHAR(20) NOT NULL, -- 'debug', 'info', 'warning', 'error', 'critical'
    modulo VARCHAR(50),
    mensagem TEXT NOT NULL,
    dados_adicionais TEXT, -- JSON
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER,
    ip_address VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(usuario_id)
);

-- =============================================================================
-- 10. ÍNDICES PARA OTIMIZAÇÃO
-- =============================================================================

-- Índices para melhorar performance das consultas
CREATE INDEX idx_leitura_sensor_data ON LEITURA(sensor_id, data_hora);
CREATE INDEX idx_leitura_data_hora ON LEITURA(data_hora);
CREATE INDEX idx_plantio_talhao ON PLANTIO(talhao_id);
CREATE INDEX idx_plantio_cultura ON PLANTIO(cultura_id);
CREATE INDEX idx_plantio_status ON PLANTIO(status_plantio);
CREATE INDEX idx_sensor_talhao ON SENSOR(talhao_id);
CREATE INDEX idx_sensor_status ON SENSOR(status);
CREATE INDEX idx_alerta_status ON ALERTA(status);
CREATE INDEX idx_alerta_data ON ALERTA(data_geracao);
CREATE INDEX idx_recomendacao_status ON RECOMENDACAO(status);
CREATE INDEX idx_recomendacao_plantio ON RECOMENDACAO(plantio_id);
CREATE INDEX idx_aplicacao_data ON APLICACAO(data_hora);
CREATE INDEX idx_aplicacao_plantio ON APLICACAO(plantio_id);
CREATE INDEX idx_dados_clima_talhao ON DADOS_CLIMA(talhao_id, data_hora);
CREATE INDEX idx_previsao_clima_talhao ON PREVISAO_CLIMA(talhao_id, data_hora_previsao);
CREATE INDEX idx_log_auditoria_usuario ON LOG_AUDITORIA(usuario_id, data_hora);
CREATE INDEX idx_log_sistema_nivel ON LOG_SISTEMA(nivel, data_hora);

-- =============================================================================
-- 11. DADOS INICIAIS DO SISTEMA
-- =============================================================================

-- Inserir configurações do sistema
INSERT INTO CONFIGURACAO_SISTEMA (chave, valor, descricao, categoria) VALUES
('sistema.nome', 'FarmTech Solutions', 'Nome do sistema', 'sistema'),
('sistema.versao', '2.0', 'Versão atual do sistema', 'sistema'),
('sistema.timezone', 'America/Sao_Paulo', 'Fuso horário padrão', 'sistema'),
('alerta.umidade_minima', '30', 'Umidade mínima para alerta (%)', 'alertas'),
('alerta.umidade_maxima', '80', 'Umidade máxima para alerta (%)', 'alertas'),
('alerta.temperatura_minima', '10', 'Temperatura mínima para alerta (°C)', 'alertas'),
('alerta.temperatura_maxima', '35', 'Temperatura máxima para alerta (°C)', 'alertas'),
('irrigacao.intervalo_minimo', '30', 'Intervalo mínimo entre irrigações (minutos)', 'irrigacao'),
('irrigacao.duracao_maxima', '120', 'Duração máxima de irrigação (minutos)', 'irrigacao'),
('sensor.intervalo_leitura', '5', 'Intervalo entre leituras de sensores (minutos)', 'sensores');

-- Inserir tipos de sensores
INSERT INTO TIPO_SENSOR (nome, descricao, unidade_medida, faixa_min, faixa_max, categoria) VALUES
('Sensor de Umidade do Solo', 'Mede a umidade do solo', '%', 0, 100, 'solo'),
('Sensor de Temperatura', 'Mede a temperatura ambiente', '°C', -40, 80, 'clima'),
('Sensor de pH', 'Mede o pH do solo', 'pH', 0, 14, 'solo'),
('Sensor de Condutividade Elétrica', 'Mede a condutividade elétrica do solo', 'mS/cm', 0, 10, 'solo'),
('Sensor de Nitrogênio', 'Mede o teor de nitrogênio no solo', 'mg/kg', 0, 1000, 'solo'),
('Sensor de Fósforo', 'Mede o teor de fósforo no solo', 'mg/kg', 0, 500, 'solo'),
('Sensor de Potássio', 'Mede o teor de potássio no solo', 'mg/kg', 0, 1000, 'solo'),
('Sensor de Radiação Solar', 'Mede a radiação solar', 'W/m²', 0, 1500, 'clima'),
('Sensor de Velocidade do Vento', 'Mede a velocidade do vento', 'm/s', 0, 50, 'clima'),
('Sensor de Precipitação', 'Mede a quantidade de chuva', 'mm', 0, 1000, 'clima');

-- Inserir tipos de recomendação
INSERT INTO TIPO_RECOMENDACAO (nome, categoria, descricao) VALUES
('Fertilização Nitrogenada', 'fertilizacao', 'Recomendação de aplicação de fertilizante nitrogenado'),
('Fertilização Fosfatada', 'fertilizacao', 'Recomendação de aplicação de fertilizante fosfatado'),
('Fertilização Potássica', 'fertilizacao', 'Recomendação de aplicação de fertilizante potássico'),
('Correção de pH', 'fertilizacao', 'Recomendação de calagem ou gessagem'),
('Irrigação Suplementar', 'irrigacao', 'Recomendação de irrigação baseada em déficit hídrico'),
('Controle de Pragas', 'controle_praga', 'Recomendação de aplicação de inseticida'),
('Controle de Doenças', 'controle_doenca', 'Recomendação de aplicação de fungicida'),
('Adubação Orgânica', 'fertilizacao', 'Recomendação de aplicação de adubo orgânico'),
('Micronutrientes', 'fertilizacao', 'Recomendação de aplicação de micronutrientes'),
('Bioestimulantes', 'fertilizacao', 'Recomendação de aplicação de bioestimulantes');

-- Inserir métricas padrão
INSERT INTO METRICA (nome, categoria, descricao, formula, unidade_medida, frequencia_calculo) VALUES
('Produtividade', 'produtividade', 'Produção por hectare', 'producao_real / area_plantada', 't/ha', 'sazonal'),
('Eficiência Hídrica', 'sustentabilidade', 'Produção por unidade de água aplicada', 'producao_real / volume_agua_aplicada', 'kg/m³', 'sazonal'),
('Eficiência Nutricional', 'produtividade', 'Produção por unidade de nutriente aplicado', 'producao_real / quantidade_fertilizante', 'kg/kg', 'sazonal'),
('Custo por Hectare', 'custo', 'Custo total por hectare plantado', 'custo_total / area_plantada', 'R$/ha', 'sazonal'),
('Lucro por Hectare', 'custo', 'Lucro por hectare plantado', 'lucro_total / area_plantada', 'R$/ha', 'sazonal'),
('ROI', 'custo', 'Retorno sobre investimento', '(lucro_total - custo_total) / custo_total * 100', '%', 'sazonal'),
('Qualidade do Solo', 'sustentabilidade', 'Índice de qualidade do solo', 'media_indicadores_solo', 'índice', 'mensal'),
('Uso Eficiente de Água', 'sustentabilidade', 'Eficiência do sistema de irrigação', 'agua_absorvida / agua_aplicada * 100', '%', 'mensal'),
('Redução de Perdas', 'produtividade', 'Redução de perdas por pragas/doenças', '(perdas_esperadas - perdas_reais) / perdas_esperadas * 100', '%', 'sazonal'),
('Sustentabilidade Ambiental', 'sustentabilidade', 'Índice de sustentabilidade ambiental', 'media_indicadores_ambientais', 'índice', 'mensal');

-- =============================================================================
-- 12. TRIGGERS PARA AUTOMAÇÃO
-- =============================================================================

-- Trigger para atualizar data_atualizacao em PLANTIO
CREATE TRIGGER trigger_plantio_update
AFTER UPDATE ON PLANTIO
BEGIN
    UPDATE PLANTIO SET data_atualizacao = CURRENT_TIMESTAMP WHERE plantio_id = NEW.plantio_id;
END;

-- Trigger para log de auditoria em PLANTIO
CREATE TRIGGER trigger_plantio_audit
AFTER UPDATE ON PLANTIO
BEGIN
    INSERT INTO LOG_AUDITORIA (acao, tabela_afetada, registro_id, dados_anteriores, dados_novos)
    VALUES ('UPDATE', 'PLANTIO', NEW.plantio_id, 
            json_object('plantio_id', OLD.plantio_id, 'status_plantio', OLD.status_plantio, 'producao_real', OLD.producao_real),
            json_object('plantio_id', NEW.plantio_id, 'status_plantio', NEW.status_plantio, 'producao_real', NEW.producao_real));
END;

-- Trigger para log de auditoria em SENSOR
CREATE TRIGGER trigger_sensor_audit
AFTER UPDATE ON SENSOR
BEGIN
    INSERT INTO LOG_AUDITORIA (acao, tabela_afetada, registro_id, dados_anteriores, dados_novos)
    VALUES ('UPDATE', 'SENSOR', NEW.sensor_id,
            json_object('sensor_id', OLD.sensor_id, 'status', OLD.status),
            json_object('sensor_id', NEW.sensor_id, 'status', NEW.status));
END;

-- =============================================================================
-- 13. VIEWS PARA CONSULTAS FREQUENTES
-- =============================================================================

-- View para resumo de plantios
CREATE VIEW vw_resumo_plantios AS
SELECT 
    p.plantio_id,
    p.codigo_plantio,
    f.nome as fazenda,
    a.nome as area,
    t.nome as talhao,
    c.nome as cultura,
    c.variedade,
    p.data_inicio,
    p.data_colheita_prevista,
    p.status_plantio,
    p.area_plantada,
    p.producao_estimada,
    p.producao_real,
    p.produtividade_estimada,
    p.produtividade_real,
    p.custo_estimado,
    p.custo_real,
    p.lucro_estimado,
    p.lucro_real
FROM PLANTIO p
JOIN TALHAO t ON p.talhao_id = t.talhao_id
JOIN AREA a ON t.area_id = a.area_id
JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
JOIN CULTURA c ON p.cultura_id = c.cultura_id;

-- View para resumo de sensores
CREATE VIEW vw_resumo_sensores AS
SELECT 
    s.sensor_id,
    s.codigo,
    ts.nome as tipo_sensor,
    f.nome as fazenda,
    a.nome as area,
    t.nome as talhao,
    s.status,
    s.ultima_manutencao,
    s.proxima_manutencao,
    s.bateria_nivel,
    s.sinal_forca,
    (SELECT COUNT(*) FROM LEITURA l WHERE l.sensor_id = s.sensor_id) as total_leituras,
    (SELECT MAX(data_hora) FROM LEITURA l WHERE l.sensor_id = s.sensor_id) as ultima_leitura
FROM SENSOR s
JOIN TIPO_SENSOR ts ON s.tipo_sensor_id = ts.tipo_sensor_id
LEFT JOIN TALHAO t ON s.talhao_id = t.talhao_id
LEFT JOIN AREA a ON t.area_id = a.area_id
LEFT JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id;

-- View para alertas ativos
CREATE VIEW vw_alertas_ativos AS
SELECT 
    a.alerta_id,
    a.tipo_alerta,
    a.severidade,
    a.titulo,
    a.descricao,
    a.data_geracao,
    f.nome as fazenda,
    ar.nome as area,
    t.nome as talhao,
    s.codigo as sensor,
    u.nome as responsavel
FROM ALERTA a
LEFT JOIN SENSOR s ON a.sensor_id = s.sensor_id
LEFT JOIN TALHAO t ON a.talhao_id = t.talhao_id OR (s.talhao_id = t.talhao_id)
LEFT JOIN AREA ar ON t.area_id = ar.area_id
LEFT JOIN FAZENDA f ON ar.fazenda_id = f.fazenda_id
LEFT JOIN USUARIO u ON a.usuario_responsavel = u.usuario_id
WHERE a.status = 'ativo';

-- View para recomendações pendentes
CREATE VIEW vw_recomendacoes_pendentes AS
SELECT 
    r.recomendacao_id,
    r.titulo,
    r.descricao,
    r.tipo_recomendacao,
    r.prioridade,
    r.data_geracao,
    r.prazo_aplicacao,
    f.nome as fazenda,
    ar.nome as area,
    t.nome as talhao,
    c.nome as cultura,
    u.nome as gerador
FROM RECOMENDACAO r
JOIN PLANTIO p ON r.plantio_id = p.plantio_id
JOIN TALHAO t ON r.talhao_id = t.talhao_id
JOIN AREA ar ON t.area_id = ar.area_id
JOIN FAZENDA f ON ar.fazenda_id = f.fazenda_id
JOIN CULTURA c ON p.cultura_id = c.cultura_id
LEFT JOIN USUARIO u ON r.usuario_gerador = u.usuario_id
WHERE r.status = 'pendente';

-- =============================================================================
-- FIM DO SCRIPT DE CRIAÇÃO DO BANCO DE DADOS APRIMORADO
-- ============================================================================= 