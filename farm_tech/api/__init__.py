#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - API REST
Módulo para endpoints da API REST
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    CORS(app)
    
    # Registrar blueprints
    from .routes import sensors_bp, readings_bp, recommendations_bp, areas_bp
    
    app.register_blueprint(sensors_bp, url_prefix='/api/sensores')
    app.register_blueprint(readings_bp, url_prefix='/api/leituras')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recomendacoes')
    app.register_blueprint(areas_bp, url_prefix='/api/areas')
    
    return app

__all__ = ['create_app'] 