#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema de Gerenciamento de Alertas
Sistema centralizado para gerenciamento de alertas e notificações
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import os

from ..core.logger import get_notification_logger

logger = get_notification_logger()

class AlertLevel(Enum):
    """Níveis de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(Enum):
    """Tipos de alerta"""
    SENSOR_OFFLINE = "sensor_offline"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    PREDICTION_ALERT = "prediction_alert"
    SYSTEM_ERROR = "system_error"
    MAINTENANCE_DUE = "maintenance_due"

@dataclass
class Alert:
    """Estrutura de alerta"""
    id: str
    type: AlertType
    level: AlertLevel
    title: str
    message: str
    sensor_id: Optional[int] = None
    area_id: Optional[int] = None
    plantio_id: Optional[int] = None
    timestamp: datetime = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class AlertManager:
    """Gerenciador central de alertas"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_notification_logger()
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.notifiers = []
        
        # Configurar notificadores
        self._setup_notifiers()
        
        # Carregar alertas salvos
        self._load_alerts()
    
    def _setup_notifiers(self):
        """Configura os notificadores disponíveis"""
        try:
            # Email notifier
            if self.config.get('email', {}).get('enabled', False):
                from .notifiers import EmailNotifier
                self.notifiers.append(EmailNotifier(self.config['email']))
            
            # SMS notifier
            if self.config.get('sms', {}).get('enabled', False):
                from .notifiers import SMSNotifier
                self.notifiers.append(SMSNotifier(self.config['sms']))
            
            # Push notifier
            from .notifiers import PushNotifier
            self.notifiers.append(PushNotifier())
            
            self.logger.info(f"Configurados {len(self.notifiers)} notificadores")
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar notificadores: {e}")
    
    def create_alert(self, alert_type: AlertType, level: AlertLevel, title: str, 
                    message: str, sensor_id: Optional[int] = None, 
                    area_id: Optional[int] = None, plantio_id: Optional[int] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """Cria um novo alerta"""
        try:
            alert_id = f"{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alerts)}"
            
            alert = Alert(
                id=alert_id,
                type=alert_type,
                level=level,
                title=title,
                message=message,
                sensor_id=sensor_id,
                area_id=area_id,
                plantio_id=plantio_id,
                metadata=metadata or {}
            )
            
            # Adicionar à lista de alertas ativos
            self.alerts.append(alert)
            
            # Salvar alerta
            self._save_alerts()
            
            # Enviar notificações
            self._send_notifications(alert)
            
            self.logger.info(f"Alerta criado: {alert_id} - {title}")
            return alert
            
        except Exception as e:
            self.logger.error(f"Erro ao criar alerta: {e}")
            raise
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Reconhece um alerta"""
        try:
            alert = self._find_alert(alert_id)
            if alert:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                
                # Mover para histórico se necessário
                if alert.level in [AlertLevel.INFO, AlertLevel.WARNING]:
                    self._move_to_history(alert)
                
                self._save_alerts()
                self.logger.info(f"Alerta {alert_id} reconhecido por {acknowledged_by}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao reconhecer alerta: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resolve um alerta"""
        try:
            alert = self._find_alert(alert_id)
            if alert:
                alert.metadata['resolved_by'] = resolved_by
                alert.metadata['resolved_at'] = datetime.now().isoformat()
                alert.metadata['resolution_notes'] = resolution_notes
                
                # Mover para histórico
                self._move_to_history(alert)
                
                self._save_alerts()
                self.logger.info(f"Alerta {alert_id} resolvido por {resolved_by}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao resolver alerta: {e}")
            return False
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None, 
                         alert_type: Optional[AlertType] = None) -> List[Alert]:
        """Obtém alertas ativos filtrados"""
        try:
            filtered_alerts = self.alerts
            
            if level:
                filtered_alerts = [a for a in filtered_alerts if a.level == level]
            
            if alert_type:
                filtered_alerts = [a for a in filtered_alerts if a.type == alert_type]
            
            return filtered_alerts
            
        except Exception as e:
            self.logger.error(f"Erro ao obter alertas ativos: {e}")
            return []
    
    def get_alert_history(self, days: int = 30, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Obtém histórico de alertas"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_history = [
                a for a in self.alert_history 
                if a.timestamp >= cutoff_date
            ]
            
            if level:
                filtered_history = [a for a in filtered_history if a.level == level]
            
            return filtered_history
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de alertas: {e}")
            return []
    
    def check_sensor_thresholds(self, sensor_id: int, sensor_type: str, value: float):
        """Verifica se valores do sensor excedem thresholds"""
        try:
            alert_config = self.config.get('alert_config', {})
            
            if sensor_type == 'umidade':
                min_threshold = alert_config.get('umidade', {}).get('min', 30.0)
                max_threshold = alert_config.get('umidade', {}).get('max', 80.0)
                
                if value < min_threshold:
                    self.create_alert(
                        AlertType.THRESHOLD_EXCEEDED,
                        AlertLevel.WARNING,
                        f"Umidade Baixa - Sensor {sensor_id}",
                        f"Umidade do solo está muito baixa: {value}% (mínimo: {min_threshold}%)",
                        sensor_id=sensor_id,
                        metadata={'current_value': value, 'threshold': min_threshold}
                    )
                elif value > max_threshold:
                    self.create_alert(
                        AlertType.THRESHOLD_EXCEEDED,
                        AlertLevel.WARNING,
                        f"Umidade Alta - Sensor {sensor_id}",
                        f"Umidade do solo está muito alta: {value}% (máximo: {max_threshold}%)",
                        sensor_id=sensor_id,
                        metadata={'current_value': value, 'threshold': max_threshold}
                    )
            
            elif sensor_type == 'ph':
                min_threshold = alert_config.get('ph', {}).get('min', 5.5)
                max_threshold = alert_config.get('ph', {}).get('max', 7.5)
                
                if value < min_threshold:
                    self.create_alert(
                        AlertType.THRESHOLD_EXCEEDED,
                        AlertLevel.WARNING,
                        f"pH Baixo - Sensor {sensor_id}",
                        f"pH do solo está muito baixo: {value} (mínimo: {min_threshold})",
                        sensor_id=sensor_id,
                        metadata={'current_value': value, 'threshold': min_threshold}
                    )
                elif value > max_threshold:
                    self.create_alert(
                        AlertType.THRESHOLD_EXCEEDED,
                        AlertLevel.WARNING,
                        f"pH Alto - Sensor {sensor_id}",
                        f"pH do solo está muito alto: {value} (máximo: {max_threshold})",
                        sensor_id=sensor_id,
                        metadata={'current_value': value, 'threshold': max_threshold}
                    )
            
            elif sensor_type == 'nutrientes':
                min_threshold = alert_config.get('nutrientes', {}).get('min', 100.0)
                
                if value < min_threshold:
                    self.create_alert(
                        AlertType.THRESHOLD_EXCEEDED,
                        AlertLevel.WARNING,
                        f"Nutrientes Baixos - Sensor {sensor_id}",
                        f"Nível de nutrientes está muito baixo: {value} ppm (mínimo: {min_threshold} ppm)",
                        sensor_id=sensor_id,
                        metadata={'current_value': value, 'threshold': min_threshold}
                    )
                    
        except Exception as e:
            self.logger.error(f"Erro ao verificar thresholds do sensor: {e}")
    
    def _find_alert(self, alert_id: str) -> Optional[Alert]:
        """Encontra um alerta pelo ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def _move_to_history(self, alert: Alert):
        """Move alerta para histórico"""
        if alert in self.alerts:
            self.alerts.remove(alert)
            self.alert_history.append(alert)
    
    def _send_notifications(self, alert: Alert):
        """Envia notificações para todos os notificadores"""
        try:
            for notifier in self.notifiers:
                try:
                    notifier.send_notification(alert)
                except Exception as e:
                    self.logger.error(f"Erro ao enviar notificação via {notifier.__class__.__name__}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificações: {e}")
    
    def _save_alerts(self):
        """Salva alertas em arquivo"""
        try:
            alerts_file = 'data/alerts.json'
            os.makedirs(os.path.dirname(alerts_file), exist_ok=True)
            
            alerts_data = {
                'active_alerts': [self._alert_to_dict(a) for a in self.alerts],
                'alert_history': [self._alert_to_dict(a) for a in self.alert_history[-100:]]  # Últimos 100
            }
            
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar alertas: {e}")
    
    def _load_alerts(self):
        """Carrega alertas do arquivo"""
        try:
            alerts_file = 'data/alerts.json'
            if os.path.exists(alerts_file):
                with open(alerts_file, 'r', encoding='utf-8') as f:
                    alerts_data = json.load(f)
                
                # Carregar alertas ativos
                for alert_dict in alerts_data.get('active_alerts', []):
                    alert = self._dict_to_alert(alert_dict)
                    if alert:
                        self.alerts.append(alert)
                
                # Carregar histórico
                for alert_dict in alerts_data.get('alert_history', []):
                    alert = self._dict_to_alert(alert_dict)
                    if alert:
                        self.alert_history.append(alert)
                
                self.logger.info(f"Carregados {len(self.alerts)} alertas ativos e {len(self.alert_history)} do histórico")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar alertas: {e}")
    
    def _alert_to_dict(self, alert: Alert) -> Dict[str, Any]:
        """Converte alerta para dicionário"""
        return {
            'id': alert.id,
            'type': alert.type.value,
            'level': alert.level.value,
            'title': alert.title,
            'message': alert.message,
            'sensor_id': alert.sensor_id,
            'area_id': alert.area_id,
            'plantio_id': alert.plantio_id,
            'timestamp': alert.timestamp.isoformat(),
            'acknowledged': alert.acknowledged,
            'acknowledged_by': alert.acknowledged_by,
            'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            'metadata': alert.metadata
        }
    
    def _dict_to_alert(self, alert_dict: Dict[str, Any]) -> Optional[Alert]:
        """Converte dicionário para alerta"""
        try:
            return Alert(
                id=alert_dict['id'],
                type=AlertType(alert_dict['type']),
                level=AlertLevel(alert_dict['level']),
                title=alert_dict['title'],
                message=alert_dict['message'],
                sensor_id=alert_dict.get('sensor_id'),
                area_id=alert_dict.get('area_id'),
                plantio_id=alert_dict.get('plantio_id'),
                timestamp=datetime.fromisoformat(alert_dict['timestamp']),
                acknowledged=alert_dict.get('acknowledged', False),
                acknowledged_by=alert_dict.get('acknowledged_by'),
                acknowledged_at=datetime.fromisoformat(alert_dict['acknowledged_at']) if alert_dict.get('acknowledged_at') else None,
                metadata=alert_dict.get('metadata', {})
            )
        except Exception as e:
            self.logger.error(f"Erro ao converter dicionário para alerta: {e}")
            return None 