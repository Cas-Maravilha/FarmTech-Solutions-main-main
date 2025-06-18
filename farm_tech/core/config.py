#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Configuração Centralizada
Configurações do sistema centralizadas
"""

import os
from typing import Dict, Any

class Config:
    """Configuração centralizada do sistema"""
    
    def __init__(self):
        # Configurações de banco de dados
        self.DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'data/farmtech.db')
        self.DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
        self.DATABASE_PORT = int(os.getenv('DATABASE_PORT', 3306))
        self.DATABASE_NAME = os.getenv('DATABASE_NAME', 'farmtech')
        self.DATABASE_USER = os.getenv('DATABASE_USER', 'root')
        self.DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
        
        # Configurações da API
        self.API_HOST = os.getenv('API_HOST', '0.0.0.0')
        self.API_PORT = int(os.getenv('API_PORT', 5000))
        self.API_DEBUG = os.getenv('API_DEBUG', 'True').lower() == 'true'
        self.API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'dev-secret-key')
        
        # Configurações de ML
        self.ML_MODEL_PATH = os.getenv('ML_MODEL_PATH', 'models/')
        self.ML_PREDICTION_THRESHOLD = float(os.getenv('ML_PREDICTION_THRESHOLD', 0.7))
        self.ML_RETRAIN_INTERVAL = int(os.getenv('ML_RETRAIN_INTERVAL', 24))  # horas
        
        # Configurações de notificações
        self.EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
        self.EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
        self.EMAIL_USER = os.getenv('EMAIL_USER', '')
        self.EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
        
        self.SMS_ENABLED = os.getenv('SMS_ENABLED', 'False').lower() == 'true'
        self.SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'twilio')
        self.SMS_ACCOUNT_SID = os.getenv('SMS_ACCOUNT_SID', '')
        self.SMS_AUTH_TOKEN = os.getenv('SMS_AUTH_TOKEN', '')
        
        # Configurações de alertas
        self.ALERT_UMIDADE_MIN = float(os.getenv('ALERT_UMIDADE_MIN', 30.0))
        self.ALERT_UMIDADE_MAX = float(os.getenv('ALERT_UMIDADE_MAX', 80.0))
        self.ALERT_PH_MIN = float(os.getenv('ALERT_PH_MIN', 5.5))
        self.ALERT_PH_MAX = float(os.getenv('ALERT_PH_MAX', 7.5))
        self.ALERT_NUTRIENTES_MIN = float(os.getenv('ALERT_NUTRIENTES_MIN', 100.0))
        
        # Configurações de logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/farmtech.log')
        self.LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
        
        # Configurações de cache
        self.CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
        self.CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')
        self.CACHE_URL = os.getenv('CACHE_URL', 'redis://localhost:6379/0')
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hora
        
        # Configurações de segurança
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
        self.RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
        self.RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # segundos
    
    def get_database_config(self) -> Dict[str, Any]:
        """Retorna configuração do banco de dados"""
        if self.DATABASE_TYPE == 'sqlite':
            return {
                'type': 'sqlite',
                'url': self.DATABASE_URL
            }
        else:
            return {
                'type': 'mysql',
                'host': self.DATABASE_HOST,
                'port': self.DATABASE_PORT,
                'database': self.DATABASE_NAME,
                'user': self.DATABASE_USER,
                'password': self.DATABASE_PASSWORD
            }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Retorna configuração da API"""
        return {
            'host': self.API_HOST,
            'port': self.API_PORT,
            'debug': self.API_DEBUG,
            'secret_key': self.API_SECRET_KEY
        }
    
    def get_ml_config(self) -> Dict[str, Any]:
        """Retorna configuração de ML"""
        return {
            'model_path': self.ML_MODEL_PATH,
            'prediction_threshold': self.ML_PREDICTION_THRESHOLD,
            'retrain_interval': self.ML_RETRAIN_INTERVAL
        }
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Retorna configuração de notificações"""
        return {
            'email': {
                'enabled': self.EMAIL_ENABLED,
                'host': self.EMAIL_HOST,
                'port': self.EMAIL_PORT,
                'user': self.EMAIL_USER,
                'password': self.EMAIL_PASSWORD
            },
            'sms': {
                'enabled': self.SMS_ENABLED,
                'provider': self.SMS_PROVIDER,
                'account_sid': self.SMS_ACCOUNT_SID,
                'auth_token': self.SMS_AUTH_TOKEN
            }
        }
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Retorna configuração de alertas"""
        return {
            'umidade': {
                'min': self.ALERT_UMIDADE_MIN,
                'max': self.ALERT_UMIDADE_MAX
            },
            'ph': {
                'min': self.ALERT_PH_MIN,
                'max': self.ALERT_PH_MAX
            },
            'nutrientes': {
                'min': self.ALERT_NUTRIENTES_MIN
            }
        } 