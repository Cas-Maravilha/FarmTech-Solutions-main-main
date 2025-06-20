# FarmTech Solutions - Guia de Troubleshooting

## Problemas Comuns e Soluções

### 1. Problemas de Conexão com Banco de Dados

#### Erro: "Database connection failed"
**Sintomas:**
- Erro ao iniciar a aplicação
- Mensagens de erro relacionadas a conexão SQLite/MySQL
- Timeout em operações de banco

**Causas Possíveis:**
- Arquivo de banco não existe
- Permissões incorretas
- Configuração de conexão incorreta
- Banco de dados corrompido

**Soluções:**

1. **Verificar se o banco existe:**
```bash
# Para SQLite
ls -la data/farmtech.db

# Para MySQL
mysql -u username -p -e "SHOW DATABASES;"
```

2. **Criar banco se não existir:**
```bash
# Executar script de criação
python demo_sensores.py --criar-banco

# Ou manualmente para SQLite
sqlite3 data/farmtech.db < criar_banco_dados.sql
```

3. **Verificar permissões:**
```bash
# Para SQLite
chmod 644 data/farmtech.db
chmod 755 data/

# Para MySQL
GRANT ALL PRIVILEGES ON farmtech.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

4. **Verificar configuração:**
```python
# Em db_manager.py, verificar:
DB_PATH = 'data/farmtech.db'  # Caminho correto?
```

#### Erro: "Table doesn't exist"
**Solução:**
```bash
# Recriar todas as tabelas
python demo_sensores.py --criar-banco --dados-exemplo
```

### 2. Problemas com Sensores

#### Erro: "Sensor not found"
**Sintomas:**
- Erro 404 ao acessar sensor
- Mensagem "Sensor ID X não encontrado"

**Soluções:**

1. **Verificar se o sensor existe:**
```bash
# Listar todos os sensores
curl -X GET http://localhost:5000/api/sensores
```

2. **Criar dados de exemplo:**
```bash
python demo_sensores.py --dados-exemplo
```

3. **Verificar banco de dados:**
```sql
SELECT * FROM sensor WHERE sensor_id = 1;
```

#### Erro: "Invalid sensor data"
**Sintomas:**
- Erro ao registrar leitura
- Valores fora do range esperado

**Soluções:**

1. **Verificar range de valores:**
```python
# Valores típicos por tipo de sensor
UMIDADE: 0-100%
PH: 0-14
NUTRIENTES: 0-1000 ppm
```

2. **Validar dados antes de enviar:**
```python
# Exemplo de validação
if not (0 <= valor <= 100):
    raise ValueError("Valor de umidade deve estar entre 0 e 100")
```

### 3. Problemas com a API

#### Erro: "Connection refused"
**Sintomas:**
- Não consegue conectar na API
- Timeout em requisições

**Soluções:**

1. **Verificar se a API está rodando:**
```bash
# Verificar processo
ps aux | grep python
netstat -tlnp | grep 5000
```

2. **Iniciar a API:**
```bash
python api.py
```

3. **Verificar firewall:**
```bash
# Windows
netsh advfirewall firewall add rule name="FarmTech API" dir=in action=allow protocol=TCP localport=5000

# Linux
sudo ufw allow 5000
```

4. **Verificar dependências:**
```bash
pip install -r requirements.txt
```

#### Erro: "CORS error"
**Sintomas:**
- Erro no browser sobre CORS
- Requisições bloqueadas

**Soluções:**

1. **Verificar configuração CORS:**
```python
# Em api.py
from flask_cors import CORS
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
```

2. **Configurar proxy no frontend:**
```javascript
// package.json
{
  "proxy": "http://localhost:5000"
}
```

### 4. Problemas de Performance

#### Erro: "Slow response times"
**Sintomas:**
- API lenta
- Timeout em consultas
- Alto uso de CPU/memória

**Soluções:**

1. **Otimizar queries:**
```sql
-- Adicionar índices
CREATE INDEX idx_leitura_sensor_data ON leitura(sensor_id, data_hora);
CREATE INDEX idx_sensor_area ON sensor(area_id);
```

2. **Implementar cache:**
```python
# Exemplo com cache simples
from functools import lru_cache

@lru_cache(maxsize=128)
def obter_sensor(sensor_id):
    # Implementação
    pass
```

3. **Limitar resultados:**
```python
# Sempre usar LIMIT em consultas
leituras = leitura_repository.listar_leituras(limit=100)
```

4. **Monitorar performance:**
```python
import time

start_time = time.time()
# Operação
end_time = time.time()
logger.info(f"Operação levou {end_time - start_time:.2f} segundos")
```

### 5. Problemas de Dados

#### Erro: "Invalid data format"
**Sintomas:**
- Erro ao processar dados
- Valores inesperados
- Falha na validação

**Soluções:**

1. **Validar formato de data:**
```python
# Usar formato ISO
data_hora = "2024-01-15T10:30:00"
```

2. **Verificar tipos de dados:**
```python
# Exemplo de validação
if not isinstance(valor, (int, float)):
    raise ValueError("Valor deve ser numérico")
```

3. **Limpar dados:**
```python
# Remover valores nulos
leituras = [l for l in leituras if l.valor is not None]
```

#### Erro: "Data inconsistency"
**Sintomas:**
- Dados duplicados
- Referências quebradas
- Inconsistências no banco

**Soluções:**

1. **Verificar integridade:**
```sql
-- Verificar foreign keys
SELECT * FROM leitura l 
LEFT JOIN sensor s ON l.sensor_id = s.sensor_id 
WHERE s.sensor_id IS NULL;
```

2. **Limpar dados duplicados:**
```sql
-- Remover leituras duplicadas
DELETE FROM leitura 
WHERE leitura_id NOT IN (
    SELECT MIN(leitura_id) 
    FROM leitura 
    GROUP BY sensor_id, data_hora, valor
);
```

3. **Recriar dados de exemplo:**
```bash
python demo_sensores.py --criar-banco --dados-exemplo
```

### 6. Problemas de Logs

#### Erro: "Log file not found"
**Sintomas:**
- Logs não aparecem
- Erro ao escrever logs

**Soluções:**

1. **Verificar configuração de logging:**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('farmtech.log'),
        logging.StreamHandler()
    ]
)
```

2. **Verificar permissões:**
```bash
# Criar arquivo de log se não existir
touch farmtech.log
chmod 644 farmtech.log
```

3. **Verificar espaço em disco:**
```bash
df -h
du -sh farmtech.log
```

### 7. Problemas de Recomendações

#### Erro: "No recommendations generated"
**Sintomas:**
- Sistema não gera recomendações
- Recomendações vazias

**Soluções:**

1. **Verificar dados de entrada:**
```bash
# Verificar se há leituras suficientes
curl -X GET "http://localhost:5000/api/sensores/1/estatisticas?periodo_dias=7"
```

2. **Verificar thresholds:**
```python
# Verificar valores mínimos para recomendações
UMIDADE_MIN_LEITURAS = 3
NUTRIENTES_MIN_LEITURAS = 3
PH_MIN_LEITURAS = 3
```

3. **Gerar dados de teste:**
```bash
python demo_sensores.py --dados-exemplo
```

### 8. Problemas de Integração

#### Erro: "External API connection failed"
**Sintomas:**
- Falha na integração com APIs externas
- Timeout em chamadas externas

**Soluções:**

1. **Verificar conectividade:**
```bash
# Testar conexão
curl -I https://api.externa.com
ping api.externa.com
```

2. **Implementar retry:**
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
```

3. **Usar timeout:**
```python
import requests

response = requests.get(url, timeout=10)
```

## Comandos Úteis de Diagnóstico

### Verificar Status do Sistema
```bash
# Verificar se todos os serviços estão rodando
ps aux | grep python

# Verificar portas em uso
netstat -tlnp | grep 5000

# Verificar logs
tail -f farmtech.log

# Verificar uso de recursos
top -p $(pgrep -f "python.*api.py")
```

### Verificar Banco de Dados
```bash
# SQLite
sqlite3 data/farmtech.db ".tables"
sqlite3 data/farmtech.db "SELECT COUNT(*) FROM sensor;"
sqlite3 data/farmtech.db "SELECT COUNT(*) FROM leitura;"

# MySQL
mysql -u username -p farmtech -e "SHOW TABLES;"
mysql -u username -p farmtech -e "SELECT COUNT(*) FROM sensor;"
```

### Testar API
```bash
# Health check
curl -X GET http://localhost:5000/api/health

# Listar sensores
curl -X GET http://localhost:5000/api/sensores

# Testar recomendação
curl -X GET "http://localhost:5000/api/recomendacoes/irrigacao/1"
```

## Logs de Erro Comuns

### Erro de Importação
```
ImportError: No module named 'flask'
```
**Solução:** `pip install flask flask-cors`

### Erro de Permissão
```
PermissionError: [Errno 13] Permission denied
```
**Solução:** Verificar permissões de arquivo/diretório

### Erro de Conexão
```
sqlite3.OperationalError: no such table
```
**Solução:** Executar script de criação do banco

### Erro de Validação
```
ValueError: Invalid sensor data
```
**Solução:** Verificar formato e range dos dados

## Contato para Suporte

Para problemas não resolvidos por este guia:

1. **Verificar logs:** `tail -f farmtech.log`
2. **Coletar informações do sistema:** `python -c "import sys; print(sys.version)"`
3. **Documentar passos para reproduzir o problema**
4. **Entrar em contato com a equipe de desenvolvimento**

## Manutenção Preventiva

### Diária
- Verificar logs de erro
- Monitorar uso de recursos
- Verificar conectividade dos sensores

### Semanal
- Backup do banco de dados
- Análise de performance
- Verificação de integridade dos dados

### Mensal
- Atualização de dependências
- Revisão de configurações
- Análise de tendências de uso 