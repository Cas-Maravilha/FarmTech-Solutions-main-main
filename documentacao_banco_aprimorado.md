# FarmTech Solutions - Banco de Dados Aprimorado

## Visão Geral

O banco de dados aprimorado da FarmTech Solutions representa uma evolução significativa do modelo de negócio, incorporando novas entidades, relacionamentos mais robustos e funcionalidades avançadas para gestão agrícola inteligente.

## Arquitetura do Banco

### 1. Estrutura Modular

O banco está organizado em módulos funcionais:

```
📁 CONFIGURAÇÃO E SISTEMA
├── CONFIGURACAO_SISTEMA
├── USUARIO
└── FAZENDA

📁 LOCALIZAÇÃO E ÁREAS
├── COORDENADA
├── AREA
└── TALHAO

📁 SENSORES E EQUIPAMENTOS
├── TIPO_SENSOR
├── SENSOR
├── LEITURA
└── ALERTA

📁 CULTURAS E PLANTIOS
├── CULTURA
├── PLANTIO
└── ESTAGIO_DESENVOLVIMENTO

📁 IRRIGAÇÃO E CONTROLE
├── SISTEMA_IRRIGACAO
├── PROGRAMACAO_IRRIGACAO
└── EXECUCAO_IRRIGACAO

📁 RECOMENDAÇÕES E APLICAÇÕES
├── TIPO_RECOMENDACAO
├── RECOMENDACAO
└── APLICACAO

📁 CLIMA E PREVISÃO
├── DADOS_CLIMA
└── PREVISAO_CLIMA

📁 RELATÓRIOS E ANALYTICS
├── RELATORIO
├── METRICA
└── VALOR_METRICA

📁 AUDITORIA E LOGS
├── LOG_AUDITORIA
└── LOG_SISTEMA
```

## Principais Melhorias

### 1. Gestão de Usuários e Permissões

**Tabela USUARIO**
- Controle de acesso com diferentes níveis (admin, gerente, operador, viewer)
- Autenticação segura com hash de senhas
- Rastreamento de atividades e último login

### 2. Hierarquia Geográfica Completa

**FAZENDA → AREA → TALHAO**
- Suporte a múltiplas fazendas
- Coordenadas geográficas precisas
- Características detalhadas do solo por área

### 3. Sensores Inteligentes

**Tabela SENSOR Aprimorada**
- Tipos de sensores padronizados
- Monitoramento de bateria e sinal
- Programação de manutenção
- Versão de firmware

**Tabela LEITURA Aprimorada**
- Qualidade dos dados
- Condições ambientais durante leitura
- Coordenadas GPS da leitura

### 4. Gestão de Culturas Detalhada

**Tabela CULTURA Expandida**
- Parâmetros ideais para 12 nutrientes
- Resistência a pragas e doenças
- Características agronômicas completas

**Tabela PLANTIO Aprimorada**
- Fases de crescimento
- Métricas de produtividade
- Controle de custos e lucros
- Responsabilidade por usuário

### 5. Sistema de Irrigação Inteligente

**Novas Tabelas**
- `SISTEMA_IRRIGACAO`: Configuração dos sistemas
- `PROGRAMACAO_IRRIGACAO`: Agendamento inteligente
- `EXECUCAO_IRRIGACAO`: Controle de execução

### 6. Recomendações Baseadas em IA

**Tabela RECOMENDACAO Aprimorada**
- Tipos padronizados de recomendação
- Sistema de prioridades
- Aprovação e rastreamento
- ROI estimado

### 7. Monitoramento Climático

**Novas Tabelas**
- `DADOS_CLIMA`: Dados meteorológicos
- `PREVISAO_CLIMA`: Previsões integradas

### 8. Analytics e Métricas

**Novas Tabelas**
- `METRICA`: Definição de KPIs
- `VALOR_METRICA`: Valores calculados
- `RELATORIO`: Geração automática

### 9. Auditoria e Compliance

**Novas Tabelas**
- `LOG_AUDITORIA`: Rastreamento de mudanças
- `LOG_SISTEMA`: Logs de sistema

## Relacionamentos Principais

### Hierarquia Geográfica
```
FAZENDA (1) → (N) AREA (1) → (N) TALHAO (1) → (N) SENSOR
```

### Gestão de Plantio
```
TALHAO (1) → (N) PLANTIO (N) → (1) CULTURA
PLANTIO (1) → (N) ESTAGIO_DESENVOLVIMENTO
```

### Monitoramento
```
SENSOR (1) → (N) LEITURA
SENSOR (1) → (N) ALERTA
TALHAO (1) → (N) ALERTA
```

### Recomendações
```
PLANTIO (1) → (N) RECOMENDACAO (N) → (1) TIPO_RECOMENDACAO
RECOMENDACAO (1) → (N) APLICACAO
```

## Funcionalidades Avançadas

### 1. Triggers Automáticos

```sql
-- Atualização automática de data_atualizacao
CREATE TRIGGER trigger_plantio_update
AFTER UPDATE ON PLANTIO
BEGIN
    UPDATE PLANTIO SET data_atualizacao = CURRENT_TIMESTAMP 
    WHERE plantio_id = NEW.plantio_id;
END;

-- Auditoria automática
CREATE TRIGGER trigger_plantio_audit
AFTER UPDATE ON PLANTIO
BEGIN
    INSERT INTO LOG_AUDITORIA (acao, tabela_afetada, registro_id, dados_anteriores, dados_novos)
    VALUES ('UPDATE', 'PLANTIO', NEW.plantio_id, 
            json_object('plantio_id', OLD.plantio_id, 'status_plantio', OLD.status_plantio),
            json_object('plantio_id', NEW.plantio_id, 'status_plantio', NEW.status_plantio));
END;
```

### 2. Views para Consultas Frequentes

```sql
-- Resumo de plantios
CREATE VIEW vw_resumo_plantios AS
SELECT 
    p.plantio_id, p.codigo_plantio, f.nome as fazenda,
    a.nome as area, t.nome as talhao, c.nome as cultura,
    p.status_plantio, p.area_plantada, p.producao_estimada,
    p.produtividade_estimada, p.custo_estimado, p.lucro_estimado
FROM PLANTIO p
JOIN TALHAO t ON p.talhao_id = t.talhao_id
JOIN AREA a ON t.area_id = a.area_id
JOIN FAZENDA f ON a.fazenda_id = f.fazenda_id
JOIN CULTURA c ON p.cultura_id = c.cultura_id;

-- Alertas ativos
CREATE VIEW vw_alertas_ativos AS
SELECT 
    a.alerta_id, a.tipo_alerta, a.severidade, a.titulo,
    f.nome as fazenda, ar.nome as area, t.nome as talhao
FROM ALERTA a
LEFT JOIN SENSOR s ON a.sensor_id = s.sensor_id
LEFT JOIN TALHAO t ON a.talhao_id = t.talhao_id
LEFT JOIN AREA ar ON t.area_id = ar.area_id
LEFT JOIN FAZENDA f ON ar.fazenda_id = f.fazenda_id
WHERE a.status = 'ativo';
```

### 3. Índices Otimizados

```sql
-- Índices para performance
CREATE INDEX idx_leitura_sensor_data ON LEITURA(sensor_id, data_hora);
CREATE INDEX idx_plantio_talhao ON PLANTIO(talhao_id);
CREATE INDEX idx_alerta_status ON ALERTA(status);
CREATE INDEX idx_recomendacao_plantio ON RECOMENDACAO(plantio_id);
```

## Dados de Exemplo

### Configurações do Sistema
- Nome: FarmTech Solutions
- Versão: 2.0
- Timezone: America/Sao_Paulo
- Parâmetros de alerta configuráveis

### Tipos de Sensores
1. **Sensor de Umidade do Solo** (0-100%)
2. **Sensor de Temperatura** (-40°C a 80°C)
3. **Sensor de pH** (0-14 pH)
4. **Sensor de Condutividade Elétrica** (0-10 mS/cm)
5. **Sensores de Nutrientes** (N, P, K, Ca, Mg, S, B, Zn, Cu, Mn, Mo)
6. **Sensor de Radiação Solar** (0-1500 W/m²)
7. **Sensor de Velocidade do Vento** (0-50 m/s)
8. **Sensor de Precipitação** (0-1000 mm)

### Culturas Suportadas
1. **Soja** - Intacta RR2 PRO
2. **Milho** - DKB 390
3. **Algodão** - FM 985 GLTP
4. **Feijão** - BRS Estilo
5. **Arroz** - BRS Catiana

### Tipos de Recomendação
1. **Fertilização Nitrogenada**
2. **Fertilização Fosfatada**
3. **Fertilização Potássica**
4. **Correção de pH**
5. **Irrigação Suplementar**
6. **Controle de Pragas**
7. **Controle de Doenças**
8. **Adubação Orgânica**
9. **Micronutrientes**
10. **Bioestimulantes**

## Métricas e KPIs

### Produtividade
- Produção por hectare (t/ha)
- Eficiência hídrica (kg/m³)
- Eficiência nutricional (kg/kg)

### Custos
- Custo por hectare (R$/ha)
- Lucro por hectare (R$/ha)
- ROI (Return on Investment)

### Sustentabilidade
- Qualidade do solo (índice)
- Uso eficiente de água (%)
- Redução de perdas (%)
- Sustentabilidade ambiental (índice)

## Segurança e Auditoria

### Controle de Acesso
- Usuários com diferentes níveis de permissão
- Senhas criptografadas com SHA-256
- Sessões com timeout configurável

### Auditoria
- Log de todas as alterações em tabelas críticas
- Rastreamento de usuário responsável
- Histórico de dados anteriores e novos

### Logs do Sistema
- Diferentes níveis de log (debug, info, warning, error, critical)
- Dados adicionais em formato JSON
- Rastreamento de IP e user agent

## Integração com APIs

### Endpoints Principais
- `/api/plantios` - Gestão de plantios
- `/api/sensores` - Monitoramento de sensores
- `/api/leituras` - Dados de leituras
- `/api/recomendacoes` - Sistema de recomendações
- `/api/alertas` - Gestão de alertas
- `/api/irrigacao` - Controle de irrigação
- `/api/relatorios` - Geração de relatórios

### Formatos Suportados
- JSON para APIs REST
- CSV para exportação
- PDF para relatórios
- Excel para análises

## Performance e Escalabilidade

### Otimizações Implementadas
- Índices em colunas frequentemente consultadas
- Views materializadas para consultas complexas
- Triggers para atualizações automáticas
- Particionamento por data para tabelas grandes

### Monitoramento
- Logs de performance
- Métricas de uso do banco
- Alertas de lentidão
- Backup automático

## Backup e Recuperação

### Estratégia de Backup
- Backup diário completo
- Backup incremental a cada hora
- Retenção de 30 dias
- Backup em localização remota

### Recuperação
- Recuperação pontual (Point-in-Time Recovery)
- Recuperação de tabelas específicas
- Validação de integridade pós-recuperação

## Migração e Atualização

### Scripts de Migração
- Migração automática de versões anteriores
- Preservação de dados existentes
- Validação de integridade
- Rollback em caso de erro

### Versionamento
- Controle de versão do esquema
- Migrações incrementais
- Compatibilidade com versões anteriores

## Documentação de API

### Autenticação
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "usuario@farmtech.com",
  "senha": "senha123"
}
```

### Exemplo de Consulta
```http
GET /api/plantios?fazenda_id=1&status=em_andamento
Authorization: Bearer <token>
```

### Exemplo de Inserção
```http
POST /api/leituras
Content-Type: application/json
Authorization: Bearer <token>

{
  "sensor_id": 1,
  "valor": 65.5,
  "unidade_medida": "%",
  "qualidade_dado": "excelente",
  "temperatura_ambiente": 25.3,
  "umidade_ambiente": 70.2
}
```

## Conclusão

O banco de dados aprimorado da FarmTech Solutions representa um sistema completo e robusto para gestão agrícola inteligente, com:

- **Escalabilidade**: Suporte a múltiplas fazendas e usuários
- **Inteligência**: Sistema de recomendações baseado em IA
- **Monitoramento**: Sensores e alertas em tempo real
- **Analytics**: Métricas e relatórios avançados
- **Segurança**: Controle de acesso e auditoria completa
- **Performance**: Otimizações para grandes volumes de dados

Este modelo de banco de dados está preparado para suportar o crescimento da FarmTech Solutions e fornecer insights valiosos para tomada de decisões agrícolas baseadas em dados. 