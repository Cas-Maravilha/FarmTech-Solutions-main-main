# Dashboard Streamlit - FarmTech Solutions

## Visão Geral

O Dashboard Streamlit do FarmTech Solutions oferece uma **interface interativa e moderna** para visualização em tempo real dos dados do sistema de irrigação inteligente. Desenvolvido com Streamlit e Plotly, proporciona uma experiência de usuário intuitiva e responsiva.

---

## 🎯 Funcionalidades Implementadas

### 1. **Interface Interativa**
- ✅ **Layout responsivo** e moderno
- ✅ **Sidebar configurável** com filtros
- ✅ **Atualização automática** de dados
- ✅ **Tema personalizado** com cores do FarmTech

### 2. **Visualizações Avançadas**
- ✅ **Gráficos Plotly** interativos
- ✅ **Múltiplos subplots** para diferentes sensores
- ✅ **Linhas de referência** para valores ideais
- ✅ **Análise de tendências** em tempo real

### 3. **Métricas em Tempo Real**
- ✅ **Cards de métricas** com indicadores
- ✅ **Alertas visuais** por prioridade
- ✅ **Status dos sensores** com cores
- ✅ **Análise de eficiência** do sistema

### 4. **Integração com ML**
- ✅ **Predições de irrigação** visualizadas
- ✅ **Confiança dos modelos** ML
- ✅ **Recomendações** baseadas em ML
- ✅ **Agenda otimizada** por algoritmos

---

## 🏗️ Arquitetura do Dashboard

### Estrutura de Arquivos

```
farm_tech/dashboard/
├── streamlit_app.py          # Dashboard principal
├── advanced_dashboard.py     # Dashboard avançado
└── static/
    └── config.toml          # Configuração Streamlit

streamlit_demo.py            # Demonstração funcional
.streamlit/
└── config.toml             # Configuração global
```

### Componentes Principais

```python
class FarmTechDashboard:
    """Dashboard principal do FarmTech Solutions"""
    
    def __init__(self):
        self.api_url = "http://localhost:5000/api"
        self.data_cache = {}
        self.last_update = None
    
    def load_sample_data(self):
        """Carregar dados de exemplo"""
    
    def create_sensor_charts(self, df):
        """Criar gráficos dos sensores"""
    
    def get_irrigation_predictions(self):
        """Obter predições de irrigação"""
```

---

## 📊 Visualizações Implementadas

### 1. **Gráficos de Sensores**

#### Monitoramento Multi-Sensor
```python
def create_sensor_charts(self, df):
    """Criar gráficos dos sensores"""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Umidade do Solo (%)', 'pH do Solo', 'Nutrientes (ppm)'),
        vertical_spacing=0.1
    )
    
    # Adicionar dados de cada sensor
    for i, sensor_type in enumerate(['umidade', 'ph', 'nutrientes']):
        sensor_data = df[df['sensor_type'] == sensor_type]
        
        fig.add_trace(
            go.Scatter(
                x=sensor_data['timestamp'],
                y=sensor_data['value'],
                mode='lines+markers',
                name=sensor_type.title(),
                line=dict(color=colors[i], width=2)
            ),
            row=i+1, col=1
        )
```

#### Características dos Gráficos
- **Múltiplos subplots** para diferentes sensores
- **Linhas de referência** para valores ideais
- **Cores diferenciadas** por tipo de sensor
- **Marcadores** para pontos de dados
- **Zoom e pan** interativos

### 2. **Análise de Tendências**

#### Cards de Status
```python
def create_trend_analysis(self, df):
    """Criar análise de tendências"""
    for sensor_type in ['umidade', 'ph', 'nutrientes']:
        # Calcular tendência
        change_percent = ((recent_avg - older_avg) / older_avg) * 100
        
        # Determinar status
        if sensor_type == 'umidade':
            if current_value < 30:
                status = 'CRÍTICO'
                color = 'red'
            elif current_value < 40:
                status = 'ATENÇÃO'
                color = 'orange'
            else:
                status = 'NORMAL'
                color = 'green'
```

#### Indicadores Visuais
- **Cards coloridos** por status (verde, laranja, vermelho)
- **Percentual de mudança** em tempo real
- **Tendências** (aumentando/diminuindo)
- **Alertas visuais** para valores críticos

### 3. **Predições de ML**

#### Gráfico de Probabilidades
```python
def create_prediction_chart(self, predictions):
    """Criar gráfico de predições"""
    fig = go.Figure(data=[
        go.Bar(
            x=[f"Sensor {sid}" for sid in sensor_ids],
            y=probabilities,
            marker_color=colors,
            text=[f"{prob:.1f}%" for prob in probabilities],
            textposition='auto',
        )
    ])
```

#### Recomendações Interativas
- **Barras coloridas** por prioridade
- **Percentual de probabilidade** de irrigação
- **Recomendações detalhadas** por sensor
- **Confiança do modelo** ML

---

## 🎨 Interface do Usuário

### 1. **Layout Responsivo**

#### Header Principal
```python
st.markdown('<h1 class="main-header">🌾 FarmTech Solutions</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center;">Dashboard de Irrigação Inteligente</h2>', unsafe_allow_html=True)
```

#### Sidebar Configurável
```python
st.sidebar.title("⚙️ Configurações")

selected_area = st.sidebar.selectbox(
    "Selecionar Área",
    ["Todas as Áreas", "Área A - Milho", "Área B - Soja", "Área C - Trigo"]
)

time_period = st.sidebar.selectbox(
    "Período de Análise",
    ["Últimas 24 horas", "Últimos 3 dias", "Últimos 7 dias", "Últimos 30 dias"]
)
```

### 2. **CSS Personalizado**

#### Estilos Modernos
```css
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    background: linear-gradient(90deg, #1f77b4, #ff7f0e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.metric-card {
    background: linear-gradient(135deg, #f0f2f6 0%, #e0e6ed 100%);
    padding: 1.5rem;
    border-radius: 1rem;
    border-left: 4px solid #1f77b4;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}
```

### 3. **Métricas em Tempo Real**

#### Cards de Métricas
```python
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Sensores Ativos",
        value="3",
        delta="0"
    )

with col2:
    st.metric(
        label="Áreas Monitoradas",
        value="3",
        delta="0"
    )

with col3:
    st.metric(
        label="Água Necessária",
        value="450L",
        delta="+450L"
    )

with col4:
    st.metric(
        label="Custo Estimado",
        value="R$ 5,25",
        delta="+R$ 5,25"
    )
```

---

## 🔧 Configuração e Uso

### 1. **Instalação de Dependências**

```bash
pip install streamlit plotly pandas numpy
```

### 2. **Execução do Dashboard**

```bash
# Executar dashboard Streamlit
python farm_tech_main.py --mode streamlit

# Ou diretamente
streamlit run streamlit_demo.py --server.port 8501
```

### 3. **Configuração Avançada**

#### Arquivo .streamlit/config.toml
```toml
[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### 4. **Acesso ao Dashboard**

- **URL**: http://localhost:8501
- **Porta padrão**: 8501
- **Atualização**: Automática (configurável)
- **Responsivo**: Sim (mobile-friendly)

---

## 📈 Funcionalidades Interativas

### 1. **Filtros Dinâmicos**

#### Seleção de Área
```python
selected_area = st.sidebar.selectbox(
    "Selecionar Área",
    ["Todas as Áreas", "Área A - Milho", "Área B - Soja", "Área C - Trigo"]
)
```

#### Período de Análise
```python
time_period = st.sidebar.selectbox(
    "Período de Análise",
    ["Últimas 24 horas", "Últimos 3 dias", "Últimos 7 dias", "Últimos 30 dias"]
)
```

### 2. **Atualização Automática**

```python
auto_refresh = st.sidebar.checkbox("Atualização Automática", value=True)
refresh_interval = st.sidebar.slider("Intervalo (segundos)", 30, 300, 60)

if auto_refresh:
    time.sleep(refresh_interval)
    st.experimental_rerun()
```

### 3. **Gráficos Interativos**

#### Zoom e Pan
- **Zoom**: Clique e arraste para ampliar
- **Pan**: Clique e arraste para mover
- **Reset**: Duplo clique para resetar
- **Hover**: Informações detalhadas

#### Seleção de Dados
- **Clique**: Selecionar pontos específicos
- **Lasso**: Seleção livre de pontos
- **Box**: Seleção retangular

---

## 🤖 Integração com Machine Learning

### 1. **Visualização de Predições**

#### Gráfico de Probabilidades
```python
def create_prediction_chart(self, predictions):
    """Criar gráfico de predições"""
    sensor_ids = [p['sensor_id'] for p in predictions]
    probabilities = [p['prediction_probability'] * 100 for p in predictions]
    colors = ['red' if p['priority'] == 'ALTA' else 
             'orange' if p['priority'] == 'MÉDIA' else 'green' 
             for p in predictions]
    
    fig = go.Figure(data=[
        go.Bar(
            x=[f"Sensor {sid}" for sid in sensor_ids],
            y=probabilities,
            marker_color=colors,
            text=[f"{prob:.1f}%" for prob in probabilities],
            textposition='auto',
        )
    ])
```

### 2. **Recomendações Inteligentes**

#### Cards de Recomendação
```python
for pred in predictions:
    priority_class = "high" if pred['priority'] == 'ALTA' else \
                   "medium" if pred['priority'] == 'MÉDIA' else "low"
    
    st.markdown(f"""
    <div class="prediction-card alert-{priority_class}">
        <h5>Sensor {pred['sensor_id']} - {pred['sensor_type'].title()}</h5>
        <p><strong>Ação:</strong> {pred['recommended_action']}</p>
        <p><strong>Prioridade:</strong> {pred['priority']}</p>
        <p><strong>Confiança:</strong> {pred['confidence']:.1%}</p>
        <p><strong>Motivo:</strong> {pred['reason']}</p>
    </div>
    """, unsafe_allow_html=True)
```

### 3. **Agenda Otimizada**

#### Timeline de Irrigação
```python
def create_schedule_timeline(self, schedule):
    """Criar timeline da agenda de irrigação"""
    events = []
    for event in schedule:
        start_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
        end_time = start_time + timedelta(minutes=event['duration_minutes'])
        
        events.append({
            'Task': event['area_name'],
            'Start': start_time,
            'Finish': end_time,
            'Resource': event['priority']
        })
    
    df_timeline = pd.DataFrame(events)
    
    fig = px.timeline(df_timeline, x_start="Start", x_end="Finish", y="Task",
                     color="Resource", title="Agenda de Irrigação")
```

---

## 📱 Responsividade e Mobile

### 1. **Layout Adaptativo**

#### Colunas Responsivas
```python
# Métricas em colunas
col1, col2, col3, col4 = st.columns(4)

# Gráficos em colunas
col1, col2 = st.columns([2, 1])
```

### 2. **Interface Mobile-Friendly**

#### Elementos Touch-Friendly
- **Botões grandes** para toque
- **Sliders** responsivos
- **Menus** adaptáveis
- **Gráficos** com zoom touch

### 3. **Performance Otimizada**

#### Carregamento Eficiente
- **Dados em cache** para melhor performance
- **Lazy loading** de gráficos
- **Compressão** de dados
- **Atualização** incremental

---

## 🔍 Monitoramento e Debug

### 1. **Logs do Dashboard**

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_dashboard_event(event_type, details):
    """Log de eventos do dashboard"""
    logger.info(f"Dashboard Event: {event_type} - {details}")
```

### 2. **Métricas de Performance**

#### Tempo de Carregamento
- **Tempo de resposta** da API
- **Tempo de renderização** dos gráficos
- **Uso de memória** do dashboard
- **Taxa de atualização** dos dados

### 3. **Tratamento de Erros**

```python
try:
    # Carregar dados
    data = load_data()
    # Renderizar gráficos
    render_charts(data)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Tente atualizar a página ou verificar a conexão")
```

---

## 🚀 Próximos Passos

### 1. **Funcionalidades Avançadas**
- 🔄 **Alertas em tempo real** via WebSocket
- 🔄 **Notificações push** para mobile
- 🔄 **Exportação de relatórios** em PDF
- 🔄 **Integração com APIs** externas

### 2. **Melhorias de UX**
- 🔄 **Temas personalizáveis** pelo usuário
- 🔄 **Dashboard customizável** (drag & drop)
- 🔄 **Modo escuro** automático
- 🔄 **Animações** suaves

### 3. **Integrações**
- 🔄 **APIs meteorológicas** em tempo real
- 🔄 **Sistemas de IoT** externos
- 🔄 **Plataformas de analytics**
- 🔄 **APIs de mapas** para localização

### 4. **Escalabilidade**
- 🔄 **Deploy** em cloud
- 🔄 **Load balancing** para múltiplos usuários
- 🔄 **Cache distribuído** (Redis)
- 🔄 **Monitoramento** avançado

---

## 📚 Referências

- **Streamlit Documentation**: https://docs.streamlit.io/
- **Plotly Documentation**: https://plotly.com/python/
- **Pandas Documentation**: https://pandas.pydata.org/
- **FarmTech Solutions**: Documentação completa do projeto

---

## 🤝 Suporte

Para dúvidas ou suporte técnico:
- **Documentação**: `/docs/streamlit.md`
- **Issues**: GitHub Issues
- **Email**: support@farmtech.com

---

*Dashboard Streamlit - FarmTech Solutions v1.0*
*Desenvolvido com Streamlit, Plotly e Python* 