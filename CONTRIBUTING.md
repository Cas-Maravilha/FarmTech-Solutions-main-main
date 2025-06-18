# Guia de Contribuição - FarmTech Solutions

Obrigado por considerar contribuir com o **FarmTech Solutions**! Este documento fornece diretrizes e informações para contribuidores.

## 🎯 Como Contribuir

### 📋 Tipos de Contribuição

Aceitamos vários tipos de contribuições:

- 🐛 **Bug Reports**: Reportar problemas encontrados
- 💡 **Feature Requests**: Sugerir novas funcionalidades
- 📝 **Documentation**: Melhorar documentação
- 🔧 **Code**: Implementar melhorias ou correções
- 🧪 **Testing**: Adicionar ou melhorar testes
- 🌐 **Translation**: Traduzir para outros idiomas

## 🚀 Primeiros Passos

### 1. Configurar o Ambiente

```bash
# 1. Fork o repositório
# 2. Clone seu fork
git clone https://github.com/seu-usuario/farmtech-solutions.git
cd farmtech-solutions

# 3. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 4. Instalar dependências
pip install -r requirements.txt
pip install -r requirements_ml.txt

# 5. Configurar banco de dados
python criar_banco_aprimorado.py
```

### 2. Verificar Instalação

```bash
# Testar se tudo está funcionando
python verificar_banco_aprimorado.py
python demo_serial_plotter.py
streamlit run farmtech_streamlit_app.py
```

## 📝 Padrões de Código

### Python

Seguimos os padrões PEP 8 para Python:

```python
# ✅ Bom
def calcular_produtividade(area, temperatura, umidade):
    """Calcula a produtividade baseada em parâmetros ambientais."""
    if area <= 0:
        raise ValueError("Área deve ser maior que zero")
    
    return area * temperatura * umidade * 0.001

# ❌ Evitar
def calc_prod(area,temp,umid):
    if area<=0:
        raise ValueError("erro")
    return area*temp*umid*0.001
```

### Nomenclatura

- **Funções e variáveis**: `snake_case`
- **Classes**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Módulos**: `snake_case`

### Documentação

```python
def predizer_irrigacao(features):
    """
    Prediz a necessidade de irrigação baseada em features ambientais.
    
    Args:
        features (pd.DataFrame): DataFrame com features de entrada
            - umidade_solo (float): Umidade do solo em %
            - temperatura (float): Temperatura em °C
            - umidade_ar (float): Umidade do ar em %
            
    Returns:
        dict: Dicionário com predição e confiança
            - necessidade_irrigacao (str): 'Baixa', 'Média' ou 'Alta'
            - confianca (float): Confiança da predição (0-1)
            
    Raises:
        ValueError: Se features estiverem vazias ou inválidas
    """
    pass
```

## 🔧 Fluxo de Desenvolvimento

### 1. Criar Branch

```bash
# Sempre crie uma branch para suas mudanças
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
# ou
git checkout -b docs/melhorar-documentacao
```

### 2. Fazer Mudanças

```bash
# Faça suas mudanças no código
# Teste localmente antes de commitar

# Adicionar arquivos
git add .

# Fazer commit com mensagem descritiva
git commit -m "feat: adiciona predição de produtividade

- Implementa modelo Random Forest para produtividade
- Adiciona validação de dados de entrada
- Inclui testes unitários para o novo modelo
- Atualiza documentação da API"
```

### 3. Padrões de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, ponto e vírgula, etc.
- `refactor`: Refatoração de código
- `test`: Adicionar ou corrigir testes
- `chore`: Mudanças em build, config, etc.

**Exemplos:**
```bash
git commit -m "feat(ml): adiciona modelo de detecção de anomalias"
git commit -m "fix(api): corrige endpoint de sensores"
git commit -m "docs: atualiza README com instruções de instalação"
git commit -m "test: adiciona testes para predição de irrigação"
```

### 4. Push e Pull Request

```bash
# Push para seu fork
git push origin feature/nova-funcionalidade

# Criar Pull Request no GitHub
# Preencher template do PR
```

## 🧪 Testes

### Executar Testes

```bash
# Instalar pytest
pip install pytest pytest-cov

# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=./ --cov-report=html

# Executar testes específicos
pytest tests/test_ml_models.py
```

### Escrever Testes

```python
# tests/test_ml_models.py
import pytest
import pandas as pd
from farmtech_ml_models import MLModels

class TestMLModels:
    def setup_method(self):
        self.ml = MLModels()
    
    def test_predizer_produtividade(self):
        """Testa predição de produtividade."""
        features = pd.DataFrame({
            'area_hectares': [10.0],
            'temperatura_media': [25.0],
            'umidade_media': [60.0]
        })
        
        resultado = self.ml.predizer_produtividade(features)
        
        assert 'produtividade_prevista' in resultado
        assert resultado['produtividade_prevista'] > 0
        assert 'confianca' in resultado
        assert 0 <= resultado['confianca'] <= 1
```

## 📚 Documentação

### Atualizar Documentação

1. **README.md**: Para mudanças principais
2. **Arquivos específicos**: Para funcionalidades específicas
3. **Docstrings**: Para funções e classes
4. **Exemplos**: Para demonstrações

### Padrões de Documentação

```markdown
# Título da Seção

## Subtítulo

### Exemplo de Código

```python
# Código de exemplo
def exemplo():
    return "funcionalidade"
```

### Lista de Funcionalidades

- ✅ Funcionalidade implementada
- 🚧 Funcionalidade em desenvolvimento
- 📋 Funcionalidade planejada
```

## 🐛 Reportando Bugs

### Template de Bug Report

```markdown
## Descrição do Bug

Descrição clara e concisa do bug.

## Passos para Reproduzir

1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

## Comportamento Esperado

O que deveria acontecer.

## Comportamento Atual

O que realmente acontece.

## Screenshots

Se aplicável, adicione screenshots.

## Ambiente

- OS: [ex: Windows 10, macOS 12.0]
- Python: [ex: 3.9.7]
- Versão: [ex: 2.0.0]

## Informações Adicionais

Qualquer outra informação relevante.
```

## 💡 Sugerindo Features

### Template de Feature Request

```markdown
## Problema

Descrição clara do problema que a feature resolveria.

## Solução Proposta

Descrição clara da solução desejada.

## Alternativas Consideradas

Outras soluções que foram consideradas.

## Informações Adicionais

Contexto adicional, screenshots, etc.
```

## 🔍 Revisão de Código

### Checklist para Pull Requests

- [ ] Código segue padrões PEP 8
- [ ] Documentação atualizada
- [ ] Testes adicionados/atualizados
- [ ] Todos os testes passam
- [ ] Código testado localmente
- [ ] Mensagens de commit seguem padrão
- [ ] Branch atualizada com main

### Checklist para Revisores

- [ ] Código está limpo e legível
- [ ] Funcionalidade implementada corretamente
- [ ] Testes adequados
- [ ] Documentação clara
- [ ] Não há regressões
- [ ] Performance adequada

## 🏷️ Labels

Usamos as seguintes labels:

- `bug`: Problemas no código
- `enhancement`: Melhorias
- `documentation`: Mudanças na documentação
- `good first issue`: Boas para iniciantes
- `help wanted`: Precisa de ajuda
- `question`: Perguntas
- `wontfix`: Não será corrigido

## 🎉 Reconhecimento

Contribuidores serão reconhecidos de várias formas:

- **README.md**: Lista de contribuidores
- **Releases**: Agradecimentos em releases
- **Documentação**: Créditos em funcionalidades
- **Comunidade**: Menção em eventos

## 📞 Suporte

Precisa de ajuda? Entre em contato:

- **Issues**: Para bugs e features
- **Discussions**: Para perguntas gerais
- **Email**: Para assuntos privados
- **Documentação**: Para dúvidas técnicas

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

---

**Obrigado por contribuir com o FarmTech Solutions!** 🌾🤖📊

*Juntos, estamos transformando a agricultura com tecnologia!* 