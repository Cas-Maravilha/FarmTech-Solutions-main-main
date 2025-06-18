// FarmTech Solutions - Dashboard JavaScript

// Configuração global
const CONFIG = {
    API_BASE_URL: window.location.origin + '/api',
    SOCKET_URL: window.location.origin,
    UPDATE_INTERVAL: 30000, // 30 segundos
    CHART_COLORS: {
        umidade: 'rgb(75, 192, 192)',
        ph: 'rgb(255, 99, 132)',
        nutrientes: 'rgb(54, 162, 235)',
        temperatura: 'rgb(255, 159, 64)'
    }
};

// Classe principal da aplicação
class FarmTechApp {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.initSocket();
        this.initEventListeners();
        this.startAutoUpdate();
        this.showWelcomeMessage();
    }

    // Inicializar Socket.IO
    initSocket() {
        this.socket = io(CONFIG.SOCKET_URL);
        
        this.socket.on('connect', () => {
            console.log('Conectado ao servidor FarmTech');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Desconectado do servidor');
            this.updateConnectionStatus(false);
        });

        this.socket.on('sensor_data', (data) => {
            this.handleSensorData(data);
        });

        this.socket.on('alerts_update', (data) => {
            this.handleAlertsUpdate(data);
        });

        this.socket.on('error', (error) => {
            this.showNotification('Erro de conexão: ' + error.message, 'error');
        });
    }

    // Inicializar event listeners
    initEventListeners() {
        // Filtros de sensores
        const filterForm = document.querySelector('form[method="GET"]');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => {
                this.showLoading('Aplicando filtros...');
            });
        }

        // Modais
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', () => {
                this.initModal(modal);
            });
        });

        // Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Formulários
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });
    }

    // Iniciar atualização automática
    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.requestUpdates();
        }, CONFIG.UPDATE_INTERVAL);
    }

    // Solicitar atualizações
    requestUpdates() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_alerts');
            
            // Solicitar dados de todos os sensores visíveis
            const sensorRows = document.querySelectorAll('[id^="last-reading-"]');
            sensorRows.forEach(row => {
                const sensorId = row.id.replace('last-reading-', '');
                this.socket.emit('request_sensor_data', { sensor_id: parseInt(sensorId) });
            });
        }
    }

    // Manipular dados de sensores
    handleSensorData(data) {
        const sensorId = data.sensor_id;
        
        // Atualizar valores na tabela
        this.updateSensorTableRow(sensorId, data);
        
        // Atualizar gráficos se existirem
        this.updateSensorChart(sensorId, data);
        
        // Verificar alertas
        this.checkSensorAlerts(data);
    }

    // Atualizar linha da tabela de sensores
    updateSensorTableRow(sensorId, data) {
        const lastReadingEl = document.getElementById(`last-reading-${sensorId}`);
        const currentValueEl = document.getElementById(`current-value-${sensorId}`);
        
        if (lastReadingEl && currentValueEl && data.latest_reading) {
            const reading = data.latest_reading;
            const date = new Date(reading.data_hora);
            
            lastReadingEl.textContent = date.toLocaleString('pt-BR');
            currentValueEl.textContent = `${reading.valor} ${reading.unidade_medida}`;
            
            // Adicionar animação
            currentValueEl.classList.add('fade-in');
            setTimeout(() => currentValueEl.classList.remove('fade-in'), 500);
        }
    }

    // Atualizar gráfico do sensor
    updateSensorChart(sensorId, data) {
        const chartId = `sensorChart-${sensorId}`;
        const chart = this.charts[chartId];
        
        if (chart && data.latest_reading) {
            const reading = data.latest_reading;
            const date = new Date(reading.data_hora);
            
            // Adicionar novo ponto ao gráfico
            chart.data.labels.push(date.toLocaleTimeString('pt-BR'));
            chart.data.datasets[0].data.push(reading.valor);
            
            // Manter apenas os últimos 20 pontos
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update('none');
        }
    }

    // Verificar alertas do sensor
    checkSensorAlerts(data) {
        if (data.latest_reading) {
            const reading = data.latest_reading;
            const sensorType = this.getSensorType(data.sensor_id);
            
            // Verificar thresholds baseados no tipo de sensor
            if (sensorType === 'umidade' && reading.valor < 30) {
                this.showNotification(`Umidade baixa no sensor ${data.sensor_id}: ${reading.valor}%`, 'warning');
            } else if (sensorType === 'ph' && (reading.valor < 5.5 || reading.valor > 7.5)) {
                this.showNotification(`pH fora do normal no sensor ${data.sensor_id}: ${reading.valor}`, 'warning');
            } else if (sensorType === 'nutrientes' && reading.valor < 100) {
                this.showNotification(`Nutrientes baixos no sensor ${data.sensor_id}: ${reading.valor} ppm`, 'warning');
            }
        }
    }

    // Manipular atualização de alertas
    handleAlertsUpdate(data) {
        this.updateAlertsList(data.alerts);
        this.updateAlertsCount(data.count);
    }

    // Atualizar lista de alertas
    updateAlertsList(alerts) {
        const alertsList = document.getElementById('alertsList');
        if (!alertsList) return;

        if (alerts.length === 0) {
            alertsList.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>Nenhum alerta ativo
                </div>
            `;
            return;
        }

        alertsList.innerHTML = alerts.slice(0, 5).map(alert => `
            <div class="alert alert-${this.getAlertClass(alert.level)} mb-2">
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>${alert.title}</strong><br>
                        <small>${alert.message}</small>
                    </div>
                    <small>${new Date(alert.timestamp).toLocaleString('pt-BR')}</small>
                </div>
            </div>
        `).join('');
    }

    // Atualizar contador de alertas
    updateAlertsCount(count) {
        const alertsCountEl = document.querySelector('.card.bg-warning .card-title');
        if (alertsCountEl) {
            alertsCountEl.textContent = count;
        }
    }

    // Obter classe CSS para nível de alerta
    getAlertClass(level) {
        switch(level) {
            case 'info': return 'info';
            case 'warning': return 'warning';
            case 'critical': return 'danger';
            case 'emergency': return 'danger';
            default: return 'info';
        }
    }

    // Atualizar status de conexão
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        if (statusIndicator) {
            statusIndicator.className = connected ? 'status-active' : 'status-inactive';
            statusIndicator.title = connected ? 'Conectado' : 'Desconectado';
        }
    }

    // Mostrar notificação
    showNotification(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const icon = this.getNotificationIcon(type);
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${icon} ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Remover automaticamente após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Obter ícone para notificação
    getNotificationIcon(type) {
        switch(type) {
            case 'success': return '<i class="fas fa-check-circle me-2"></i>';
            case 'warning': return '<i class="fas fa-exclamation-triangle me-2"></i>';
            case 'error': return '<i class="fas fa-times-circle me-2"></i>';
            default: return '<i class="fas fa-info-circle me-2"></i>';
        }
    }

    // Mostrar loading
    showLoading(message = 'Carregando...') {
        const loadingEl = document.getElementById('loading');
        if (loadingEl) {
            loadingEl.innerHTML = `
                <div class="text-center p-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <p class="mt-2">${message}</p>
                </div>
            `;
            loadingEl.style.display = 'block';
        }
    }

    // Esconder loading
    hideLoading() {
        const loadingEl = document.getElementById('loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }

    // Inicializar modal
    initModal(modal) {
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }

    // Manipular envio de formulário
    handleFormSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            submitBtn.disabled = true;
            
            // Reabilitar botão após 3 segundos (fallback)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 3000);
        }
    }

    // Obter tipo de sensor (simulado)
    getSensorType(sensorId) {
        // Em uma implementação real, isso viria do servidor
        const sensorTypes = {
            1: 'umidade',
            2: 'nutrientes',
            3: 'ph'
        };
        return sensorTypes[sensorId] || 'umidade';
    }

    // Mostrar mensagem de boas-vindas
    showWelcomeMessage() {
        const now = new Date();
        const hour = now.getHours();
        let greeting = '';
        
        if (hour < 12) {
            greeting = 'Bom dia';
        } else if (hour < 18) {
            greeting = 'Boa tarde';
        } else {
            greeting = 'Boa noite';
        }
        
        console.log(`${greeting}! Bem-vindo ao FarmTech Solutions Dashboard.`);
    }

    // Destruir aplicação
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        // Limpar gráficos
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
    }
}

// Utilitários
const Utils = {
    // Formatar número
    formatNumber(number, decimals = 2) {
        return Number(number).toLocaleString('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    // Formatar data
    formatDate(date) {
        return new Date(date).toLocaleDateString('pt-BR');
    },

    // Formatar data e hora
    formatDateTime(date) {
        return new Date(date).toLocaleString('pt-BR');
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.farmTechApp = new FarmTechApp();
});

// Limpar ao sair da página
window.addEventListener('beforeunload', function() {
    if (window.farmTechApp) {
        window.farmTechApp.destroy();
    }
});

// Exportar para uso global
window.FarmTechApp = FarmTechApp;
window.Utils = Utils; 