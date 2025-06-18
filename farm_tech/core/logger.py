#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema de Logging
Configuração centralizada de logging
"""

import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(
    level: str = 'INFO',
    log_file: str = 'logs/farmtech.log',
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Configura o sistema de logging"""
    
    # Criar diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Logger principal
    logger = logging.getLogger('farmtech')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remover handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Obtém um logger específico"""
    return logging.getLogger(f'farmtech.{name}')

# Loggers específicos
def get_api_logger() -> logging.Logger:
    """Logger para API"""
    return get_logger('api')

def get_sensor_logger() -> logging.Logger:
    """Logger para sensores"""
    return get_logger('sensor')

def get_ml_logger() -> logging.Logger:
    """Logger para ML"""
    return get_logger('ml')

def get_notification_logger() -> logging.Logger:
    """Logger para notificações"""
    return get_logger('notification')

def get_database_logger() -> logging.Logger:
    """Logger para banco de dados"""
    return get_logger('database') 