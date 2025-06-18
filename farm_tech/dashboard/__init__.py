#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Dashboard
Módulo para interface web e visualizações
"""

from .app import create_dashboard_app
from .views import DashboardView, SensorView, AnalyticsView

__all__ = [
    'create_dashboard_app',
    'DashboardView',
    'SensorView',
    'AnalyticsView'
] 