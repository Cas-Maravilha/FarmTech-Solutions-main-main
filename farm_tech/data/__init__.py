#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Data Layer
Módulo para acesso e manipulação de dados
"""

from .database import DatabaseManager
from .repositories import SensorRepository, ReadingRepository, AreaRepository

__all__ = [
    'DatabaseManager',
    'SensorRepository',
    'ReadingRepository', 
    'AreaRepository'
] 