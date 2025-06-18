"""
Aplicação Flask para FarmTech Solutions API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

from .sensor_routes import register_sensor_routes
from .area_routes import register_area_routes
from .reading_routes import register_reading_routes
from .recommendation_routes import register_recommendation_routes
from .irrigation_routes import register_irrigation_routes

def create_app():
    """Criar aplicação Flask"""
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5001"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'farmtech-secret-key-2024')
    app.config['JSON_SORT_KEYS'] = False
    
    # Registrar blueprints
    register_sensor_routes(app)
    register_area_routes(app)
    register_reading_routes(app)
    register_recommendation_routes(app)
    register_irrigation_routes(app)
    
    # Rota de health check
    @app.route('/api/health')
    def health_check():
        """Health check da API"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'service': 'FarmTech API'
        })
    
    # Rota de informações da API
    @app.route('/api/info')
    def api_info():
        """Informações da API"""
        return jsonify({
            'name': 'FarmTech Solutions API',
            'version': '1.0.0',
            'description': 'API para sistema de monitoramento agrícola inteligente',
            'features': [
                'Gestão de sensores e áreas',
                'Coleta de dados em tempo real',
                'Recomendações baseadas em ML',
                'Sistema de irrigação inteligente',
                'Predições usando Scikit-learn'
            ],
            'endpoints': {
                'sensors': '/api/sensores',
                'areas': '/api/areas',
                'readings': '/api/leituras',
                'recommendations': '/api/recomendacoes',
                'irrigation': '/api/irrigation'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    # Handler de erros
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint não encontrado',
            'message': 'A rota solicitada não existe',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Método não permitido',
            'message': 'O método HTTP não é suportado para este endpoint',
            'timestamp': datetime.now().isoformat()
        }), 405
    
    return app

def run_api_server(host='0.0.0.0', port=5000, debug=False):
    """Executar servidor da API"""
    app = create_app()
    
    print(f"🚀 Iniciando FarmTech API em http://{host}:{port}")
    print(f"📚 Documentação: http://{host}:{port}/api/info")
    print(f"❤️  Health Check: http://{host}:{port}/api/health")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api_server() 