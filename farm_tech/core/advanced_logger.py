"""
Sistema de Logs Avançado para FarmTech Solutions
"""

import logging
import logging.handlers
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import os
import traceback
import threading
from enum import Enum
import hashlib

class LogLevel(Enum):
    """Níveis de log"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class LogCategory(Enum):
    """Categorias de log"""
    SYSTEM = "system"
    SENSOR = "sensor"
    USER = "user"
    API = "api"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DATABASE = "database"
    NOTIFICATION = "notification"

class AdvancedLogger:
    """Sistema de logs avançado com persistência em banco de dados"""
    
    def __init__(self, db_path: str = "farmtech.db", log_dir: str = "logs"):
        self.db_path = db_path
        self.log_dir = log_dir
        self.lock = threading.Lock()
        
        # Criar diretório de logs
        os.makedirs(log_dir, exist_ok=True)
        
        # Inicializar banco de dados
        self.init_log_database()
        
        # Configurar loggers
        self.setup_loggers()
        
        # Cache de logs recentes
        self.recent_logs = []
        self.max_cache_size = 1000
        
        # Thread para limpeza automática
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_logs, daemon=True)
        self.cleanup_thread.start()
    
    def init_log_database(self):
        """Inicializar tabelas de log no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela principal de logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR(10) NOT NULL,
                category VARCHAR(20) NOT NULL,
                module VARCHAR(50),
                function_name VARCHAR(100),
                line_number INTEGER,
                message TEXT NOT NULL,
                details TEXT,
                user_id INTEGER,
                session_id VARCHAR(100),
                ip_address VARCHAR(45),
                user_agent TEXT,
                request_id VARCHAR(100),
                execution_time REAL,
                memory_usage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de métricas de performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_logs (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metric_name VARCHAR(50) NOT NULL,
                metric_value REAL NOT NULL,
                unit VARCHAR(20),
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de alertas de log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                alert_type VARCHAR(50) NOT NULL,
                severity VARCHAR(10) NOT NULL,
                message TEXT NOT NULL,
                threshold_value REAL,
                current_value REAL,
                is_resolved BOOLEAN DEFAULT 0,
                resolved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_category ON system_logs(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_user_id ON system_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_perf_metric ON performance_logs(metric_name)')
        
        conn.commit()
        conn.close()
    
    def setup_loggers(self):
        """Configurar loggers para diferentes categorias"""
        self.loggers = {}
        
        for category in LogCategory:
            logger = logging.getLogger(f'farmtech.{category.value}')
            logger.setLevel(logging.DEBUG)
            
            # Evitar duplicação de handlers
            if logger.handlers:
                continue
            
            # Handler para arquivo
            file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self.log_dir, f'{category.value}.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            # Handler para arquivo de erro
            error_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self.log_dir, f'{category.value}_error.log'),
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            error_handler.setLevel(logging.ERROR)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            error_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(error_handler)
            
            self.loggers[category] = logger
    
    def log(self, level: LogLevel, category: LogCategory, message: str, 
            details: Optional[Dict[str, Any]] = None, **kwargs):
        """Registrar log com detalhes adicionais"""
        try:
            with self.lock:
                # Obter informações do contexto
                frame = traceback.extract_stack()[-2]
                module = frame.filename.split('/')[-1].split('.')[0]
                function_name = frame.name
                line_number = frame.lineno
                
                # Preparar dados do log
                log_data = {
                    'level': level.name,
                    'category': category.value,
                    'module': module,
                    'function_name': function_name,
                    'line_number': line_number,
                    'message': message,
                    'details': json.dumps(details) if details else None,
                    'timestamp': datetime.now().isoformat(),
                    **kwargs
                }
                
                # Salvar no banco de dados
                self._save_to_database(log_data)
                
                # Adicionar ao cache
                self._add_to_cache(log_data)
                
                # Registrar no logger apropriado
                logger = self.loggers.get(category)
                if logger:
                    log_message = f"{message}"
                    if details:
                        log_message += f" | Details: {json.dumps(details)}"
                    
                    logger.log(level.value, log_message)
                
                # Verificar alertas
                self._check_alerts(log_data)
                
        except Exception as e:
            # Fallback para logging básico em caso de erro
            print(f"Erro no sistema de logs: {e}")
    
    def _save_to_database(self, log_data: Dict[str, Any]):
        """Salvar log no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_logs (
                    timestamp, level, category, module, function_name, line_number,
                    message, details, user_id, session_id, ip_address, user_agent,
                    request_id, execution_time, memory_usage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_data['timestamp'],
                log_data['level'],
                log_data['category'],
                log_data['module'],
                log_data['function_name'],
                log_data['line_number'],
                log_data['message'],
                log_data['details'],
                log_data.get('user_id'),
                log_data.get('session_id'),
                log_data.get('ip_address'),
                log_data.get('user_agent'),
                log_data.get('request_id'),
                log_data.get('execution_time'),
                log_data.get('memory_usage')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao salvar log no banco: {e}")
    
    def _add_to_cache(self, log_data: Dict[str, Any]):
        """Adicionar log ao cache"""
        self.recent_logs.append(log_data)
        
        # Manter tamanho do cache
        if len(self.recent_logs) > self.max_cache_size:
            self.recent_logs.pop(0)
    
    def _check_alerts(self, log_data: Dict[str, Any]):
        """Verificar se deve gerar alertas baseado no log"""
        # Alertas para erros críticos
        if log_data['level'] == 'CRITICAL':
            self._create_log_alert(
                'critical_error',
                'CRITICAL',
                f"Erro crítico detectado: {log_data['message']}",
                current_value=1
            )
        
        # Alertas para muitos erros em sequência
        recent_errors = [log for log in self.recent_logs[-10:] 
                        if log['level'] in ['ERROR', 'CRITICAL']]
        
        if len(recent_errors) >= 5:
            self._create_log_alert(
                'error_spike',
                'WARNING',
                f"Muitos erros detectados: {len(recent_errors)} erros nas últimas 10 entradas",
                current_value=len(recent_errors)
            )
    
    def _create_log_alert(self, alert_type: str, severity: str, message: str, 
                         threshold_value: float = None, current_value: float = None):
        """Criar alerta de log"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO log_alerts (
                    alert_type, severity, message, threshold_value, current_value
                ) VALUES (?, ?, ?, ?, ?)
            ''', (alert_type, severity, message, threshold_value, current_value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao criar alerta de log: {e}")
    
    def log_performance(self, metric_name: str, metric_value: float, 
                       unit: str = None, context: str = None):
        """Registrar métrica de performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_logs (
                    metric_name, metric_value, unit, context
                ) VALUES (?, ?, ?, ?)
            ''', (metric_name, metric_value, unit, context))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao registrar métrica de performance: {e}")
    
    def get_logs(self, level: str = None, category: str = None, 
                user_id: int = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Obter logs do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM system_logs WHERE 1=1"
            params = []
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converter para dicionários
            columns = [description[0] for description in cursor.description]
            logs = []
            
            for row in rows:
                log_dict = dict(zip(columns, row))
                if log_dict['details']:
                    try:
                        log_dict['details'] = json.loads(log_dict['details'])
                    except:
                        pass
                logs.append(log_dict)
            
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Erro ao obter logs: {e}")
            return []
    
    def get_performance_metrics(self, metric_name: str = None, 
                              hours: int = 24) -> List[Dict[str, Any]]:
        """Obter métricas de performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM performance_logs 
                WHERE timestamp >= datetime('now', '-{} hours')
            '''.format(hours)
            
            params = []
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            metrics = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            return metrics
            
        except Exception as e:
            print(f"Erro ao obter métricas: {e}")
            return []
    
    def get_log_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Obter estatísticas dos logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de logs por nível
            cursor.execute('''
                SELECT level, COUNT(*) as count 
                FROM system_logs 
                WHERE timestamp >= datetime('now', '-{} hours')
                GROUP BY level
            '''.format(hours))
            
            level_stats = dict(cursor.fetchall())
            
            # Total de logs por categoria
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM system_logs 
                WHERE timestamp >= datetime('now', '-{} hours')
                GROUP BY category
            '''.format(hours))
            
            category_stats = dict(cursor.fetchall())
            
            # Total geral
            cursor.execute('''
                SELECT COUNT(*) FROM system_logs 
                WHERE timestamp >= datetime('now', '-{} hours')
            '''.format(hours))
            
            total_logs = cursor.fetchone()[0]
            
            # Alertas ativos
            cursor.execute('''
                SELECT COUNT(*) FROM log_alerts 
                WHERE is_resolved = 0
            ''')
            
            active_alerts = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_logs': total_logs,
                'level_distribution': level_stats,
                'category_distribution': category_stats,
                'active_alerts': active_alerts,
                'period_hours': hours
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def _cleanup_old_logs(self):
        """Limpar logs antigos periodicamente"""
        while True:
            try:
                # Manter logs por 30 dias
                cutoff_date = datetime.now() - timedelta(days=30)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Limpar logs antigos
                cursor.execute('''
                    DELETE FROM system_logs 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Limpar métricas antigas (7 dias)
                cutoff_metrics = datetime.now() - timedelta(days=7)
                cursor.execute('''
                    DELETE FROM performance_logs 
                    WHERE timestamp < ?
                ''', (cutoff_metrics.isoformat(),))
                
                # Limpar alertas resolvidos antigos (7 dias)
                cursor.execute('''
                    DELETE FROM log_alerts 
                    WHERE is_resolved = 1 AND resolved_at < ?
                ''', (cutoff_metrics.isoformat(),))
                
                conn.commit()
                conn.close()
                
                # Executar a cada 6 horas
                import time
                time.sleep(6 * 60 * 60)
                
            except Exception as e:
                print(f"Erro na limpeza de logs: {e}")
                import time
                time.sleep(60 * 60)  # Tentar novamente em 1 hora

# Instância global do logger
advanced_logger = AdvancedLogger()

# Funções de conveniência
def log_info(category: LogCategory, message: str, **kwargs):
    """Log de informação"""
    advanced_logger.log(LogLevel.INFO, category, message, **kwargs)

def log_warning(category: LogCategory, message: str, **kwargs):
    """Log de aviso"""
    advanced_logger.log(LogLevel.WARNING, category, message, **kwargs)

def log_error(category: LogCategory, message: str, **kwargs):
    """Log de erro"""
    advanced_logger.log(LogLevel.ERROR, category, message, **kwargs)

def log_critical(category: LogCategory, message: str, **kwargs):
    """Log crítico"""
    advanced_logger.log(LogLevel.CRITICAL, category, message, **kwargs)

def log_debug(category: LogCategory, message: str, **kwargs):
    """Log de debug"""
    advanced_logger.log(LogLevel.DEBUG, category, message, **kwargs)

def log_performance(metric_name: str, metric_value: float, **kwargs):
    """Log de performance"""
    advanced_logger.log_performance(metric_name, metric_value, **kwargs) 