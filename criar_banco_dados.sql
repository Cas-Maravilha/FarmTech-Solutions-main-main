-- Script SQL para criação do banco de dados do Sistema de Sensoriamento Agrícola
-- FarmTech Solutions

-- Criação da tabela AREA
CREATE TABLE AREA (
    area_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    tamanho DOUBLE NOT NULL,
    localizacao VARCHAR(100),
    tipo_solo VARCHAR(50),
    data_registro DATE
);

-- Criação da tabela SENSOR
CREATE TABLE SENSOR (
    sensor_id INT PRIMARY KEY AUTO_INCREMENT,
    tipo_sensor VARCHAR(2) NOT NULL,
    numero_serie VARCHAR(50) NOT NULL,
    data_instalacao DATE,
    localizacao VARCHAR(100),
    status VARCHAR(20),
    ultima_manutencao DATE,
    area_id INT,
    FOREIGN KEY (area_id) REFERENCES AREA(area_id)
);

-- Criação da tabela LEITURA
CREATE TABLE LEITURA (
    leitura_id INT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT NOT NULL,
    data_hora DATETIME NOT NULL,
    valor DOUBLE NOT NULL,
    unidade_medida VARCHAR(10),
    status_leitura VARCHAR(20),
    FOREIGN KEY (sensor_id) REFERENCES SENSOR(sensor_id)
);

-- Criação da tabela CULTURA
CREATE TABLE CULTURA (
    cultura_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    variedade VARCHAR(50),
    ciclo_vida INT,
    ph_ideal_min DOUBLE,
    ph_ideal_max DOUBLE,
    umidade_ideal_min DOUBLE,
    umidade_ideal_max DOUBLE,
    fosforo_ideal_min DOUBLE,
    fosforo_ideal_max DOUBLE,
    potassio_ideal_min DOUBLE,
    potassio_ideal_max DOUBLE
);

-- Criação da tabela PLANTIO
CREATE TABLE PLANTIO (
    plantio_id INT PRIMARY KEY AUTO_INCREMENT,
    cultura_id INT NOT NULL,
    area_id INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_colheita_prevista DATE,
    data_colheita_real DATE,
    status_plantio VARCHAR(20),
    producao_estimada DOUBLE,
    producao_real DOUBLE,
    FOREIGN KEY (cultura_id) REFERENCES CULTURA(cultura_id),
    FOREIGN KEY (area_id) REFERENCES AREA(area_id)
);

-- Criação da tabela RECOMENDACAO
CREATE TABLE RECOMENDACAO (
    recomendacao_id INT PRIMARY KEY AUTO_INCREMENT,
    plantio_id INT NOT NULL,
    tipo_recomendacao VARCHAR(30) NOT NULL,
    quantidade_recomendada DOUBLE NOT NULL,
    unidade_medida VARCHAR(10),
    data_hora_geracao DATETIME NOT NULL,
    prazo_aplicacao DATETIME,
    prioridade VARCHAR(10),
    status_recomendacao VARCHAR(20),
    leitura_id INT,
    FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id),
    FOREIGN KEY (leitura_id) REFERENCES LEITURA(leitura_id)
);

-- Criação da tabela APLICACAO
CREATE TABLE APLICACAO (
    aplicacao_id INT PRIMARY KEY AUTO_INCREMENT,
    plantio_id INT NOT NULL,
    tipo_aplicacao VARCHAR(30) NOT NULL,
    quantidade DOUBLE NOT NULL,
    unidade_medida VARCHAR(10),
    data_hora DATETIME NOT NULL,
    responsavel VARCHAR(50),
    recomendacao_id INT,
    FOREIGN KEY (plantio_id) REFERENCES PLANTIO(plantio_id),
    FOREIGN KEY (recomendacao_id) REFERENCES RECOMENDACAO(recomendacao_id)
);

-- Inserção de dados iniciais para testes

-- Inserir áreas de exemplo
INSERT INTO AREA (nome, tamanho, localizacao, tipo_solo, data_registro) VALUES
('Setor Norte', 150.5, 'Quadrante N-12', 'Argiloso', '2023-01-15'),
('Setor Sul', 200.0, 'Quadrante S-08', 'Arenoso', '2023-01-15'),
('Setor Leste', 175.25, 'Quadrante L-05', 'Areno-argiloso', '2023-02-10');

-- Inserir culturas de exemplo
INSERT INTO CULTURA (nome, variedade, ciclo_vida, ph_ideal_min, ph_ideal_max, umidade_ideal_min, umidade_ideal_max, fosforo_ideal_min, fosforo_ideal_max, potassio_ideal_min, potassio_ideal_max) VALUES
('Soja', 'Intacta RR2 PRO', 120, 5.5, 7.0, 60.0, 85.0, 15.0, 30.0, 20.0, 40.0),
('Milho', 'DKB 390', 150, 5.8, 7.5, 65.0, 90.0, 20.0, 35.0, 25.0, 45.0),
('Algodão', 'FM 985 GLTP', 180, 5.5, 8.0, 55.0, 80.0, 18.0, 32.0, 22.0, 42.0);

-- Inserir sensores de exemplo
INSERT INTO SENSOR (tipo_sensor, numero_serie, data_instalacao, localizacao, status, ultima_manutencao, area_id) VALUES
('S1', 'UM2023001', '2023-03-01', 'Ponto A1', 'Ativo', '2023-08-15', 1),
('S1', 'UM2023002', '2023-03-01', 'Ponto B2', 'Ativo', '2023-08-15', 2),
('S2', 'PH2023001', '2023-03-02', 'Ponto A2', 'Ativo', '2023-08-16', 1),
('S2', 'PH2023002', '2023-03-02', 'Ponto B3', 'Ativo', '2023-08-16', 2),
('S3', 'NK2023001', '2023-03-03', 'Ponto A3', 'Ativo', '2023-08-17', 1),
('S3', 'NK2023002', '2023-03-03', 'Ponto B4', 'Ativo', '2023-08-17', 2);

-- Inserir plantios de exemplo
INSERT INTO PLANTIO (cultura_id, area_id, data_inicio, data_colheita_prevista, status_plantio, producao_estimada) VALUES
(1, 1, '2023-10-01', '2024-02-01', 'Em andamento', 540.5),
(2, 2, '2023-09-15', '2024-02-15', 'Em andamento', 1200.0),
(3, 3, '2023-09-01', '2024-03-01', 'Em andamento', 450.0);
