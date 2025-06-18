#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema de Notificadores
Diferentes canais de notificação (email, SMS, push)
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import requests
import json

from .alert_manager import Alert, AlertLevel
from ..core.logger import get_notification_logger

logger = get_notification_logger()

class BaseNotifier:
    """Classe base para notificadores"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_notification_logger()
    
    def send_notification(self, alert: Alert) -> bool:
        """Envia notificação (método base)"""
        raise NotImplementedError
    
    def _should_send(self, alert: Alert) -> bool:
        """Verifica se deve enviar notificação baseado no nível"""
        # Configurar níveis mínimos para cada notificador
        min_levels = {
            'email': AlertLevel.WARNING,
            'sms': AlertLevel.CRITICAL,
            'push': AlertLevel.INFO
        }
        
        notifier_type = self.__class__.__name__.lower().replace('notifier', '')
        min_level = min_levels.get(notifier_type, AlertLevel.INFO)
        
        return alert.level.value >= min_level.value

class EmailNotifier(BaseNotifier):
    """Notificador via email"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_host = config.get('host', 'smtp.gmail.com')
        self.smtp_port = config.get('port', 587)
        self.username = config.get('user', '')
        self.password = config.get('password', '')
        self.from_email = config.get('user', '')
        self.to_emails = config.get('to_emails', [])
    
    def send_notification(self, alert: Alert) -> bool:
        """Envia notificação por email"""
        try:
            if not self._should_send(alert):
                return True
            
            if not self.to_emails:
                self.logger.warning("Nenhum email de destino configurado")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[FarmTech] {alert.title}"
            
            # Corpo da mensagem
            body = self._create_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Email enviado para {self.to_emails}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def _create_email_body(self, alert: Alert) -> str:
        """Cria corpo do email"""
        level_colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'critical': '#dc3545',
            'emergency': '#721c24'
        }
        
        color = level_colors.get(alert.level.value, '#6c757d')
        
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ border: 2px solid {color}; padding: 15px; margin: 10px 0; }}
                .level {{ color: {color}; font-weight: bold; }}
                .timestamp {{ color: #6c757d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h2 class="level">{alert.title}</h2>
                <p><strong>Nível:</strong> {alert.level.value.upper()}</p>
                <p><strong>Tipo:</strong> {alert.type.value}</p>
                <p><strong>Mensagem:</strong> {alert.message}</p>
                <p class="timestamp">Data/Hora: {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
        """
        
        if alert.sensor_id:
            body += f'<p><strong>Sensor ID:</strong> {alert.sensor_id}</p>'
        
        if alert.area_id:
            body += f'<p><strong>Área ID:</strong> {alert.area_id}</p>'
        
        if alert.plantio_id:
            body += f'<p><strong>Plantio ID:</strong> {alert.plantio_id}</p>'
        
        body += """
            </div>
            <p><em>Este é um alerta automático do sistema FarmTech Solutions.</em></p>
        </body>
        </html>
        """
        
        return body

class SMSNotifier(BaseNotifier):
    """Notificador via SMS (usando Twilio)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.account_sid = config.get('account_sid', '')
        self.auth_token = config.get('auth_token', '')
        self.from_number = config.get('from_number', '')
        self.to_numbers = config.get('to_numbers', [])
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
    
    def send_notification(self, alert: Alert) -> bool:
        """Envia notificação por SMS"""
        try:
            if not self._should_send(alert):
                return True
            
            if not self.to_numbers:
                self.logger.warning("Nenhum número de telefone configurado")
                return False
            
            # Criar mensagem
            message = self._create_sms_message(alert)
            
            # Enviar para cada número
            for to_number in self.to_numbers:
                try:
                    payload = {
                        'From': self.from_number,
                        'To': to_number,
                        'Body': message
                    }
                    
                    response = requests.post(
                        self.api_url,
                        data=payload,
                        auth=(self.account_sid, self.auth_token)
                    )
                    
                    if response.status_code == 201:
                        self.logger.info(f"SMS enviado para {to_number}")
                    else:
                        self.logger.error(f"Erro ao enviar SMS para {to_number}: {response.text}")
                        
                except Exception as e:
                    self.logger.error(f"Erro ao enviar SMS para {to_number}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar SMS: {e}")
            return False
    
    def _create_sms_message(self, alert: Alert) -> str:
        """Cria mensagem SMS"""
        message = f"[FarmTech] {alert.title}\n"
        message += f"Nível: {alert.level.value.upper()}\n"
        message += f"Mensagem: {alert.message}\n"
        
        if alert.sensor_id:
            message += f"Sensor: {alert.sensor_id}\n"
        
        message += f"Data: {alert.timestamp.strftime('%d/%m %H:%M')}"
        
        return message

class PushNotifier(BaseNotifier):
    """Notificador push (webhook/API)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config or {})
        self.webhook_url = config.get('webhook_url', '') if config else ''
        self.api_key = config.get('api_key', '') if config else ''
    
    def send_notification(self, alert: Alert) -> bool:
        """Envia notificação push"""
        try:
            if not self._should_send(alert):
                return True
            
            # Criar payload
            payload = self._create_push_payload(alert)
            
            # Enviar via webhook se configurado
            if self.webhook_url:
                return self._send_webhook(payload)
            
            # Log local se não houver webhook configurado
            self.logger.info(f"Push notification: {alert.title} - {alert.message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar push notification: {e}")
            return False
    
    def _create_push_payload(self, alert: Alert) -> Dict[str, Any]:
        """Cria payload para push notification"""
        return {
            'title': alert.title,
            'message': alert.message,
            'level': alert.level.value,
            'type': alert.type.value,
            'timestamp': alert.timestamp.isoformat(),
            'sensor_id': alert.sensor_id,
            'area_id': alert.area_id,
            'plantio_id': alert.plantio_id,
            'metadata': alert.metadata
        }
    
    def _send_webhook(self, payload: Dict[str, Any]) -> bool:
        """Envia webhook"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                self.logger.info("Webhook enviado com sucesso")
                return True
            else:
                self.logger.error(f"Erro ao enviar webhook: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar webhook: {e}")
            return False

class ConsoleNotifier(BaseNotifier):
    """Notificador para console (desenvolvimento)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config or {})
    
    def send_notification(self, alert: Alert) -> bool:
        """Exibe notificação no console"""
        try:
            level_icons = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🚨',
                'emergency': '🚨🚨'
            }
            
            icon = level_icons.get(alert.level.value, '📢')
            
            print(f"\n{icon} ALERTA FARM TECH {icon}")
            print(f"Título: {alert.title}")
            print(f"Nível: {alert.level.value.upper()}")
            print(f"Tipo: {alert.type.value}")
            print(f"Mensagem: {alert.message}")
            print(f"Data/Hora: {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            
            if alert.sensor_id:
                print(f"Sensor ID: {alert.sensor_id}")
            if alert.area_id:
                print(f"Área ID: {alert.area_id}")
            if alert.plantio_id:
                print(f"Plantio ID: {alert.plantio_id}")
            
            print("=" * 50)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exibir notificação no console: {e}")
            return False 