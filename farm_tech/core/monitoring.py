"""
Sistema de Monitoramento e Métricas para FarmTech Solutions
"""

import time
import threading
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import os

class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    """Estrutura de métrica"""
    name: str
    value: float
    type: MetricType
    unit: str = ""
    labels: Dict[str, str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.labels is None:
            self.labels = {}

class MonitoringSystem:
    """Sistema de monitoramento e métricas"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        
        # Métricas em memória
        self.metrics = {}
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.summaries = {}
        
        # Alertas
        self.alerts = {}
        self.alert_handlers = {}
        
        # Configurações
        self.collection_interval = 60  # 1 minuto
        self.retention_days = 30
        
        # Inicializar banco de dados
        self.init_monitoring_database()
        
        # Threads de coleta
        self.collection_thread = threading.Thread(target=self._collection_worker, daemon=True)
        self.collection_thread.start()
        
        # Registrar métricas do sistema
        self._register_system_metrics()
    
    def init_monitoring_database(self):
        """Inicializar banco de dados de monitoramento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de métricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                value REAL NOT NULL,
                type VARCHAR(20) NOT NULL,
                unit VARCHAR(20),
                labels TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name VARCHAR(100) NOT NULL,
                alert_type VARCHAR(20) NOT NULL,
                threshold REAL NOT NULL,
                current_value REAL NOT NULL,
                severity VARCHAR(10) NOT NULL,
                message TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de configurações de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_configs (
                config_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name VARCHAR(100) NOT NULL,
                alert_type VARCHAR(20) NOT NULL,
                threshold REAL NOT NULL,
                severity VARCHAR(10) NOT NULL,
                message_template TEXT NOT NULL,
                is_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                perf_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name VARCHAR(100) NOT NULL,
                avg_value REAL NOT NULL,
                min_value REAL NOT NULL,
                max_value REAL NOT NULL,
                count INTEGER NOT NULL,
                period_start TIMESTAMP NOT NULL,
                period_end TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_metric ON monitoring_alerts(metric_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_active ON monitoring_alerts(is_active)')
        
        conn.commit()
        conn.close()
    
    def _register_system_metrics(self):
        """Registrar métricas do sistema"""
        # CPU
        self.register_gauge("system.cpu.usage", "CPU Usage", "%")
        self.register_gauge("system.cpu.count", "CPU Count", "cores")
        
        # Memory
        self.register_gauge("system.memory.usage", "Memory Usage", "%")
        self.register_gauge("system.memory.available", "Available Memory", "MB")
        self.register_gauge("system.memory.total", "Total Memory", "MB")
        
        # Disk
        self.register_gauge("system.disk.usage", "Disk Usage", "%")
        self.register_gauge("system.disk.available", "Available Disk", "GB")
        
        # Network
        self.register_counter("system.network.bytes_sent", "Network Bytes Sent", "bytes")
        self.register_counter("system.network.bytes_recv", "Network Bytes Received", "bytes")
        
        # Application
        self.register_gauge("app.active_connections", "Active Connections", "connections")
        self.register_gauge("app.request_rate", "Request Rate", "requests/sec")
        self.register_histogram("app.response_time", "Response Time", "ms")
        
        # Database
        self.register_gauge("db.connections", "Database Connections", "connections")
        self.register_histogram("db.query_time", "Database Query Time", "ms")
        
        # Cache
        self.register_gauge("cache.hit_rate", "Cache Hit Rate", "%")
        self.register_gauge("cache.size", "Cache Size", "MB")
    
    def register_counter(self, name: str, description: str, unit: str = ""):
        """Registrar contador"""
        self.counters[name] = {
            'description': description,
            'unit': unit,
            'value': 0
        }
    
    def register_gauge(self, name: str, description: str, unit: str = ""):
        """Registrar gauge"""
        self.gauges[name] = {
            'description': description,
            'unit': unit,
            'value': 0
        }
    
    def register_histogram(self, name: str, description: str, unit: str = ""):
        """Registrar histograma"""
        self.histograms[name] = {
            'description': description,
            'unit': unit,
            'values': [],
            'buckets': {}
        }
    
    def register_summary(self, name: str, description: str, unit: str = ""):
        """Registrar summary"""
        self.summaries[name] = {
            'description': description,
            'unit': unit,
            'values': [],
            'quantiles': {}
        }
    
    def increment_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Incrementar contador"""
        if name in self.counters:
            with self.lock:
                self.counters[name]['value'] += value
                self._record_metric(name, self.counters[name]['value'], MetricType.COUNTER, 
                                  self.counters[name]['unit'], labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Definir valor do gauge"""
        if name in self.gauges:
            with self.lock:
                self.gauges[name]['value'] = value
                self._record_metric(name, value, MetricType.GAUGE, 
                                  self.gauges[name]['unit'], labels)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observar valor no histograma"""
        if name in self.histograms:
            with self.lock:
                self.histograms[name]['values'].append(value)
                
                # Manter apenas os últimos 1000 valores
                if len(self.histograms[name]['values']) > 1000:
                    self.histograms[name]['values'] = self.histograms[name]['values'][-1000:]
                
                self._record_metric(name, value, MetricType.HISTOGRAM, 
                                  self.histograms[name]['unit'], labels)
    
    def observe_summary(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observar valor no summary"""
        if name in self.summaries:
            with self.lock:
                self.summaries[name]['values'].append(value)
                
                # Manter apenas os últimos 1000 valores
                if len(self.summaries[name]['values']) > 1000:
                    self.summaries[name]['values'] = self.summaries[name]['values'][-1000:]
                
                self._record_metric(name, value, MetricType.SUMMARY, 
                                  self.summaries[name]['unit'], labels)
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, 
                      unit: str = "", labels: Dict[str, str] = None):
        """Registrar métrica no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO metrics (name, value, type, unit, labels)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, value, metric_type.value, unit, json.dumps(labels) if labels else None))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao registrar métrica: {e}")
    
    def _collection_worker(self):
        """Worker para coleta de métricas do sistema"""
        while True:
            try:
                self._collect_system_metrics()
                self._check_alerts()
                self._aggregate_performance_metrics()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                print(f"Erro no collection worker: {e}")
                time.sleep(60)
    
    def _collect_system_metrics(self):
        """Coletar métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            self.set_gauge("system.cpu.usage", cpu_percent)
            self.set_gauge("system.cpu.count", cpu_count)
            
            # Memory
            memory = psutil.virtual_memory()
            self.set_gauge("system.memory.usage", memory.percent)
            self.set_gauge("system.memory.available", memory.available / (1024 * 1024))
            self.set_gauge("system.memory.total", memory.total / (1024 * 1024))
            
            # Disk
            disk = psutil.disk_usage('/')
            self.set_gauge("system.disk.usage", (disk.used / disk.total) * 100)
            self.set_gauge("system.disk.available", disk.free / (1024 * 1024 * 1024))
            
            # Network
            net_io = psutil.net_io_counters()
            self.increment_counter("system.network.bytes_sent", net_io.bytes_sent)
            self.increment_counter("system.network.bytes_recv", net_io.bytes_recv)
            
        except Exception as e:
            print(f"Erro ao coletar métricas do sistema: {e}")
    
    def create_alert(self, metric_name: str, alert_type: str, threshold: float, 
                    severity: str, message_template: str):
        """Criar configuração de alerta"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO alert_configs 
                (metric_name, alert_type, threshold, severity, message_template)
                VALUES (?, ?, ?, ?, ?)
            ''', (metric_name, alert_type, threshold, severity, message_template))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao criar alerta: {e}")
    
    def _check_alerts(self):
        """Verificar alertas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter configurações de alerta
            cursor.execute('SELECT * FROM alert_configs WHERE is_enabled = 1')
            alert_configs = cursor.fetchall()
            
            for config in alert_configs:
                config_id, metric_name, alert_type, threshold, severity, message_template, is_enabled, created_at = config
                
                # Obter valor atual da métrica
                current_value = self._get_current_metric_value(metric_name)
                
                if current_value is not None:
                    should_alert = False
                    
                    if alert_type == 'above' and current_value > threshold:
                        should_alert = True
                    elif alert_type == 'below' and current_value < threshold:
                        should_alert = True
                    elif alert_type == 'equals' and current_value == threshold:
                        should_alert = True
                    
                    if should_alert:
                        self._trigger_alert(metric_name, alert_type, threshold, 
                                          current_value, severity, message_template)
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao verificar alertas: {e}")
    
    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Obter valor atual da métrica"""
        # Verificar em memória primeiro
        if metric_name in self.gauges:
            return self.gauges[metric_name]['value']
        elif metric_name in self.counters:
            return self.counters[metric_name]['value']
        
        # Verificar no banco de dados
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value FROM metrics 
                WHERE name = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (metric_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"Erro ao obter valor da métrica: {e}")
            return None
    
    def _trigger_alert(self, metric_name: str, alert_type: str, threshold: float,
                      current_value: float, severity: str, message_template: str):
        """Disparar alerta"""
        try:
            # Verificar se já existe alerta ativo
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT alert_id FROM monitoring_alerts 
                WHERE metric_name = ? AND is_active = 1
            ''', (metric_name,))
            
            if cursor.fetchone():
                # Alerta já existe, não criar duplicata
                conn.close()
                return
            
            # Criar novo alerta
            message = message_template.format(
                metric_name=metric_name,
                current_value=current_value,
                threshold=threshold,
                alert_type=alert_type
            )
            
            cursor.execute('''
                INSERT INTO monitoring_alerts 
                (metric_name, alert_type, threshold, current_value, severity, message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (metric_name, alert_type, threshold, current_value, severity, message))
            
            conn.commit()
            conn.close()
            
            # Executar handler de alerta se existir
            if metric_name in self.alert_handlers:
                self.alert_handlers[metric_name](severity, message, current_value)
            
        except Exception as e:
            print(f"Erro ao disparar alerta: {e}")
    
    def _aggregate_performance_metrics(self):
        """Agregar métricas de performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Agregar métricas da última hora
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            cursor.execute('''
                SELECT name, 
                       AVG(value) as avg_value,
                       MIN(value) as min_value,
                       MAX(value) as max_value,
                       COUNT(*) as count
                FROM metrics 
                WHERE timestamp >= ?
                GROUP BY name
            ''', (one_hour_ago.isoformat(),))
            
            aggregations = cursor.fetchall()
            
            for name, avg_val, min_val, max_val, count in aggregations:
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (metric_name, avg_value, min_value, max_value, count, period_start, period_end)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, avg_val, min_val, max_val, count, 
                     one_hour_ago.isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao agregar métricas: {e}")
    
    def get_metrics(self, metric_name: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Obter métricas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if metric_name:
                cursor.execute('''
                    SELECT * FROM metrics 
                    WHERE name = ? AND timestamp >= datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                '''.format(hours), (metric_name,))
            else:
                cursor.execute('''
                    SELECT * FROM metrics 
                    WHERE timestamp >= datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                '''.format(hours))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            metrics = []
            for row in rows:
                metric_dict = dict(zip(columns, row))
                if metric_dict['labels']:
                    try:
                        metric_dict['labels'] = json.loads(metric_dict['labels'])
                    except:
                        pass
                metrics.append(metric_dict)
            
            conn.close()
            return metrics
            
        except Exception as e:
            print(f"Erro ao obter métricas: {e}")
            return []
    
    def get_alerts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obter alertas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute('SELECT * FROM monitoring_alerts WHERE is_active = 1 ORDER BY triggered_at DESC')
            else:
                cursor.execute('SELECT * FROM monitoring_alerts ORDER BY triggered_at DESC')
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            alerts = [dict(zip(columns, row)) for row in rows]
            conn.close()
            
            return alerts
            
        except Exception as e:
            print(f"Erro ao obter alertas: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obter status do sistema"""
        try:
            # Métricas do sistema
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Alertas ativos
            active_alerts = self.get_alerts(active_only=True)
            
            # Métricas da aplicação
            app_metrics = {}
            for name, gauge in self.gauges.items():
                if name.startswith('app.'):
                    app_metrics[name] = gauge['value']
            
            return {
                'system': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': (disk.used / disk.total) * 100,
                    'uptime': time.time() - psutil.boot_time()
                },
                'application': app_metrics,
                'alerts': {
                    'active_count': len(active_alerts),
                    'critical_count': len([a for a in active_alerts if a['severity'] == 'critical']),
                    'warning_count': len([a for a in active_alerts if a['severity'] == 'warning'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao obter status do sistema: {e}")
            return {}

# Instância global do sistema de monitoramento
monitoring_system = MonitoringSystem()

# Funções de conveniência
def increment_counter(name: str, value: float = 1, **kwargs):
    """Incrementar contador"""
    monitoring_system.increment_counter(name, value, **kwargs)

def set_gauge(name: str, value: float, **kwargs):
    """Definir gauge"""
    monitoring_system.set_gauge(name, value, **kwargs)

def observe_histogram(name: str, value: float, **kwargs):
    """Observar histograma"""
    monitoring_system.observe_histogram(name, value, **kwargs)

def create_alert(metric_name: str, alert_type: str, threshold: float, 
                severity: str, message_template: str):
    """Criar alerta"""
    monitoring_system.create_alert(metric_name, alert_type, threshold, severity, message_template)

def get_system_status():
    """Obter status do sistema"""
    return monitoring_system.get_system_status() 