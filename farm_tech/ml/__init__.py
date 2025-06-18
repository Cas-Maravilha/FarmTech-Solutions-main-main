#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Machine Learning
Módulo para algoritmos de ML e predições
"""

from .predictor import MLPredictor
from .models import IrrigationPredictor, NutrientPredictor, DiseasePredictor

__all__ = [
    'MLPredictor',
    'IrrigationPredictor',
    'NutrientPredictor',
    'DiseasePredictor'
] 