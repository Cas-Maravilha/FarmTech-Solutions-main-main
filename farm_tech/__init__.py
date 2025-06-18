#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema de Sensoriamento Agrícola
Pacote principal com estrutura modular aprimorada
"""

__version__ = "2.0.0"
__author__ = "FarmTech Solutions Team"
__description__ = "Sistema de sensoriamento agrícola com IA e recomendações inteligentes"

from .core.config import Config
from .core.logger import setup_logging

# Configuração global
config = Config()
logger = setup_logging()

# Importações principais
from .api import create_app
from .core.services import SensorService, RecommendationService
from .ml.predictor import MLPredictor
from .notifications.alert_manager import AlertManager

__all__ = [
    'create_app',
    'SensorService', 
    'RecommendationService',
    'MLPredictor',
    'AlertManager',
    'config',
    'logger'
] 