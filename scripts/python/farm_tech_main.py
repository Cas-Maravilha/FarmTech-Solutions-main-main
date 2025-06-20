#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FarmTech Solutions - Sistema Principal
Sistema modular para monitoramento e gestão agrícola inteligente
"""

import sys
import os
import argparse
import signal
import time
from pathlib import Path
from datetime import datetime

# Adicionar o diretório farm_tech ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'farm_tech'))

from farm_tech.core.config import Config
from farm_tech.core.logger import setup_logger
from farm_tech.core.services import ServiceManager
from farm_tech.data.database import DatabaseManager
from farm_tech.core.auth import auth_manager
from farm_tech.core.advanced_logger import advanced_logger
from farm_tech.core.cache_manager import cache_manager
from farm_tech.core.monitoring import monitoring_system

class FarmTechSystem:
    """Sistema principal do FarmTech Solutions"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger()
        self.service_manager = ServiceManager()
        self.db_manager = DatabaseManager()
        self.running = False
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        self.logger.info(f"Recebido sinal {signum}, encerrando sistema...")
        self.stop()
    
    def initialize(self):
        """Inicializar o sistema"""
        try:
            self.logger.info("Inicializando FarmTech Solutions...")
            
            # Inicializar banco de dados
            self.logger.info("Inicializando banco de dados...")
            self.db_manager.initialize()
            
            # Inicializar serviços
            self.logger.info("Inicializando serviços...")
            self.service_manager.initialize()
            
            # Configurar alertas de monitoramento
            self._setup_monitoring_alerts()
            
            # Configurar cache
            self._setup_cache()
            
            self.logger.info("Sistema inicializado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sistema: {e}")
            return False
    
    def _setup_monitoring_alerts(self):
        """Configurar alertas de monitoramento"""
        try:
            # Alertas de CPU
            monitoring_system.create_alert(
                "system.cpu.usage",
                "above",
                80.0,
                "warning",
                "CPU usage is high: {current_value}% (threshold: {threshold}%)"
            )
            
            monitoring_system.create_alert(
                "system.cpu.usage",
                "above",
                95.0,
                "critical",
                "CPU usage is critical: {current_value}% (threshold: {threshold}%)"
            )
            
            # Alertas de memória
            monitoring_system.create_alert(
                "system.memory.usage",
                "above",
                85.0,
                "warning",
                "Memory usage is high: {current_value}% (threshold: {threshold}%)"
            )
            
            # Alertas de disco
            monitoring_system.create_alert(
                "system.disk.usage",
                "above",
                90.0,
                "warning",
                "Disk usage is high: {current_value}% (threshold: {threshold}%)"
            )
            
            # Alertas de cache
            monitoring_system.create_alert(
                "cache.hit_rate",
                "below",
                70.0,
                "warning",
                "Cache hit rate is low: {current_value}% (threshold: {threshold}%)"
            )
            
            self.logger.info("Alertas de monitoramento configurados")
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar alertas: {e}")
    
    def _setup_cache(self):
        """Configurar cache"""
        try:
            # Configurar cache para dados de sensores
            cache_manager.set("sensor_data_cache", {}, ttl=300, category="sensors")
            cache_manager.set("area_data_cache", {}, ttl=600, category="areas")
            cache_manager.set("user_sessions_cache", {}, ttl=3600, category="sessions")
            
            self.logger.info("Cache configurado")
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar cache: {e}")
    
    def start_api(self, host: str = "0.0.0.0", port: int = 5000):
        """Iniciar API REST"""
        try:
            from farm_tech.api.app import create_app
            
            app = create_app()
            
            self.logger.info(f"Iniciando API na porta {port}...")
            
            # Configurar métricas para API
            monitoring_system.set_gauge("app.api.active", 1)
            
            app.run(host=host, port=port, debug=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar API: {e}")
    
    def start_dashboard(self, host: str = "0.0.0.0", port: int = 5001):
        """Iniciar Dashboard Web"""
        try:
            from farm_tech.dashboard.app import create_dashboard_app
            
            app = create_dashboard_app()
            
            self.logger.info(f"Iniciando Dashboard na porta {port}...")
            
            # Configurar métricas para Dashboard
            monitoring_system.set_gauge("app.dashboard.active", 1)
            
            app.run(host=host, port=port, debug=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar Dashboard: {e}")
    
    def create_sample_data(self):
        """Criar dados de exemplo"""
        try:
            self.logger.info("Criando dados de exemplo...")
            
            # Criar áreas
            areas_data = [
                {
                    "nome": "Área A - Milho",
                    "tamanho": 50.0,
                    "unidade_medida": "hectares",
                    "tipo_solo": "argiloso",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                },
                {
                    "nome": "Área B - Soja",
                    "tamanho": 75.0,
                    "unidade_medida": "hectares",
                    "tipo_solo": "arenoso",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                },
                {
                    "nome": "Área C - Trigo",
                    "tamanho": 30.0,
                    "unidade_medida": "hectares",
                    "tipo_solo": "misturado",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }
            ]
            
            # Criar sensores
            sensors_data = [
                {
                    "area_id": 1,
                    "tipo_sensor": "umidade",
                    "modelo": "SensorHum-2024",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                },
                {
                    "area_id": 1,
                    "tipo_sensor": "ph",
                    "modelo": "SensorPH-2024",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                },
                {
                    "area_id": 2,
                    "tipo_sensor": "nutrientes",
                    "modelo": "SensorNut-2024",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }
            ]
            
            # Inserir dados
            for area_data in areas_data:
                self.db_manager.create_area(**area_data)
            
            for sensor_data in sensors_data:
                self.db_manager.create_sensor(**sensor_data)
            
            # Criar leituras de exemplo
            self._create_sample_readings()
            
            self.logger.info("Dados de exemplo criados com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar dados de exemplo: {e}")
    
    def _create_sample_readings(self):
        """Criar leituras de exemplo"""
        import random
        from datetime import datetime, timedelta
        
        # Gerar leituras para os últimos 7 dias
        for days_ago in range(7):
            date = datetime.now() - timedelta(days=days_ago)
            
            for sensor_id in range(1, 4):
                # Gerar 24 leituras por dia (uma por hora)
                for hour in range(24):
                    reading_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # Valores baseados no tipo de sensor
                    if sensor_id == 1:  # Umidade
                        valor = random.uniform(30, 80)
                        unidade_medida = "%"
                    elif sensor_id == 2:  # pH
                        valor = random.uniform(5.5, 7.5)
                        unidade_medida = "pH"
                    else:  # Nutrientes
                        valor = random.uniform(100, 300)
                        unidade_medida = "ppm"
                    
                    self.db_manager.create_reading(
                        sensor_id=sensor_id,
                        valor=valor,
                        unidade_medida=unidade_medida,
                        data_hora=reading_time.isoformat(),
                        status_leitura="valida"
                    )
    
    def run_ml_predictions(self):
        """Executar predições de ML"""
        try:
            self.logger.info("Executando predições de ML...")
            
            from farm_tech.ml.predictor import MLPredictor
            
            predictor = MLPredictor()
            
            # Obter dados recentes
            recent_readings = self.db_manager.get_recent_readings(hours=24)
            
            if recent_readings:
                # Fazer predições
                predictions = predictor.predict_irrigation_needs(recent_readings)
                
                # Salvar predições
                for prediction in predictions:
                    self.db_manager.create_recommendation(
                        area_id=prediction['area_id'],
                        tipo_recomendacao='irrigacao',
                        descricao=prediction['description'],
                        prioridade=prediction['priority'],
                        data_criacao=datetime.now().isoformat()
                    )
                
                self.logger.info(f"Predições concluídas: {len(predictions)} recomendações geradas")
            else:
                self.logger.warning("Nenhum dado recente encontrado para predições")
                
        except Exception as e:
            self.logger.error(f"Erro ao executar predições: {e}")
    
    def show_status(self):
        """Mostrar status do sistema"""
        try:
            status = monitoring_system.get_system_status()
            
            print("\n" + "="*50)
            print("FARMTECH SOLUTIONS - STATUS DO SISTEMA")
            print("="*50)
            
            # Status do sistema
            print(f"\n📊 SISTEMA:")
            print(f"   CPU: {status['system']['cpu_usage']:.1f}%")
            print(f"   Memória: {status['system']['memory_usage']:.1f}%")
            print(f"   Disco: {status['system']['disk_usage']:.1f}%")
            print(f"   Uptime: {status['system']['uptime']/3600:.1f} horas")
            
            # Alertas
            print(f"\n🚨 ALERTAS:")
            print(f"   Ativos: {status['alerts']['active_count']}")
            print(f"   Críticos: {status['alerts']['critical_count']}")
            print(f"   Avisos: {status['alerts']['warning_count']}")
            
            # Métricas da aplicação
            if status['application']:
                print(f"\n📱 APLICAÇÃO:")
                for metric, value in status['application'].items():
                    print(f"   {metric}: {value}")
            
            # Estatísticas de cache
            cache_stats = cache_manager.get_stats()
            print(f"\n💾 CACHE:")
            print(f"   Uso: {cache_stats['memory_usage_mb']:.1f} MB")
            print(f"   Itens: {cache_stats['items_in_memory']}")
            print(f"   Hit Rate: {cache_stats['hit_rate']*100:.1f}%")
            
            print("\n" + "="*50)
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar status: {e}")
    
    def stop(self):
        """Parar o sistema"""
        if self.running:
            self.logger.info("Parando FarmTech Solutions...")
            
            # Parar serviços
            self.service_manager.stop()
            
            # Salvar métricas finais
            monitoring_system.set_gauge("app.api.active", 0)
            monitoring_system.set_gauge("app.dashboard.active", 0)
            
            self.running = False
            self.logger.info("Sistema parado")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="FarmTech Solutions - Sistema Principal")
    parser.add_argument("--mode", choices=["api", "dashboard", "streamlit", "both"], 
                       default="both", help="Modo de execução")
    parser.add_argument("--host", default="0.0.0.0", help="Host para binding")
    parser.add_argument("--api-port", type=int, default=5000, help="Porta da API")
    parser.add_argument("--dashboard-port", type=int, default=5001, help="Porta do Dashboard")
    parser.add_argument("--create-data", action="store_true", help="Criar dados de exemplo")
    parser.add_argument("--run-ml", action="store_true", help="Executar predições ML")
    parser.add_argument("--status", action="store_true", help="Mostrar status do sistema")
    
    args = parser.parse_args()
    
    # Criar instância do sistema
    system = FarmTechSystem()
    
    try:
        # Inicializar sistema
        if not system.initialize():
            print("Erro ao inicializar sistema")
            sys.exit(1)
        
        # Criar dados de exemplo se solicitado
        if args.create_data:
            system.create_sample_data()
        
        # Executar ML se solicitado
        if args.run_ml:
            system.run_ml_predictions()
        
        # Mostrar status se solicitado
        if args.status:
            system.show_status()
            return
        
        # Iniciar serviços baseado no modo
        if args.mode in ["api", "both"]:
            if args.mode == "both":
                # Executar API em thread separada
                import threading
                api_thread = threading.Thread(
                    target=system.start_api, 
                    args=(args.host, args.api_port),
                    daemon=True
                )
                api_thread.start()
                print(f"API iniciada em http://{args.host}:{args.api_port}")
            else:
                system.start_api(args.host, args.api_port)
        
        if args.mode in ["dashboard", "both"]:
            if args.mode == "both":
                print(f"Dashboard iniciado em http://{args.host}:{args.dashboard_port}")
                system.start_dashboard(args.host, args.dashboard_port)
            else:
                system.start_dashboard(args.host, args.dashboard_port)
        
        system.running = True
        
        # Manter sistema rodando
        while system.running:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        system.stop()

def setup_services(db_manager):
    """Configura serviços do sistema"""
    try:
        logger.info("Configurando serviços...")
        
        # Repositórios
        sensor_repo = SensorRepository(db_manager)
        reading_repo = ReadingRepository(db_manager)
        area_repo = AreaRepository(db_manager)
        
        # Serviços
        sensor_service = SensorService(sensor_repo, reading_repo)
        
        # ML
        ml_predictor = MLPredictor(config.get_ml_config()['model_path'])
        
        # Recomendações
        recommendation_service = RecommendationService(sensor_service, ml_predictor)
        
        # Alertas
        alert_manager = AlertManager(config.get_notification_config())
        
        logger.info("Serviços configurados com sucesso")
        
        return {
            'sensor_service': sensor_service,
            'recommendation_service': recommendation_service,
            'alert_manager': alert_manager,
            'repositories': {
                'sensor': sensor_repo,
                'reading': reading_repo,
                'area': area_repo
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao configurar serviços: {e}")
        raise

def create_sample_data(services):
    """Cria dados de exemplo"""
    try:
        logger.info("Criando dados de exemplo...")
        
        area_repo = services['repositories']['area']
        sensor_repo = services['repositories']['sensor']
        reading_repo = services['repositories']['reading']
        
        # Criar áreas
        area1_id = area_repo.add_area(
            nome="Área 1 - Milho",
            tamanho=50.0,
            unidade_medida="hectares",
            tipo_solo="argiloso",
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        area2_id = area_repo.add_area(
            nome="Área 2 - Soja",
            tamanho=75.0,
            unidade_medida="hectares",
            tipo_solo="arenoso",
            latitude=-23.5600,
            longitude=-46.6400
        )
        
        # Criar sensores
        sensor1_id = sensor_repo.add_sensor(
            area_id=area1_id,
            tipo_sensor="umidade",
            modelo="SHT30",
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        sensor2_id = sensor_repo.add_sensor(
            area_id=area1_id,
            tipo_sensor="nutrientes",
            modelo="NPK-Sensor",
            latitude=-23.5506,
            longitude=-46.6334
        )
        
        sensor3_id = sensor_repo.add_sensor(
            area_id=area1_id,
            tipo_sensor="ph",
            modelo="pH-Meter",
            latitude=-23.5507,
            longitude=-46.6335
        )
        
        # Criar algumas leituras de exemplo
        from datetime import datetime, timedelta
        import random
        
        for i in range(10):
            timestamp = datetime.now() - timedelta(hours=i*2)
            
            # Leitura de umidade
            reading_repo.add_reading(
                sensor_id=sensor1_id,
                value=random.uniform(40, 80),
                unit="%",
                timestamp=timestamp,
                observation=f"Leitura automática {i+1}"
            )
            
            # Leitura de nutrientes
            reading_repo.add_reading(
                sensor_id=sensor2_id,
                value=random.uniform(100, 300),
                unit="ppm",
                timestamp=timestamp,
                observation=f"Leitura automática {i+1}"
            )
            
            # Leitura de pH
            reading_repo.add_reading(
                sensor_id=sensor3_id,
                value=random.uniform(5.5, 7.5),
                unit="pH",
                timestamp=timestamp,
                observation=f"Leitura automática {i+1}"
            )
        
        logger.info("Dados de exemplo criados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao criar dados de exemplo: {e}")
        raise

def run_api_server(host='0.0.0.0', port=5000, debug=True):
    """Executa servidor da API"""
    try:
        logger.info(f"Iniciando servidor da API em {host}:{port}")
        
        app = create_app()
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor da API: {e}")
        raise

def run_dashboard_server(host='0.0.0.0', port=5001, debug=True):
    """Executa servidor do dashboard"""
    try:
        logger.info(f"Iniciando servidor do dashboard em {host}:{port}")
        
        app, socketio = create_dashboard_app(config)
        socketio.run(app, host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor do dashboard: {e}")
        raise

def run_streamlit_dashboard():
    """Executar dashboard Streamlit"""
    try:
        import subprocess
        import sys
        
        print("🚀 Iniciando Dashboard Streamlit...")
        print("📊 Acesse: http://localhost:8501")
        
        # Verificar se o arquivo existe
        streamlit_file = "streamlit_demo.py"
        if os.path.exists(streamlit_file):
            subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_file, "--server.port", "8501"])
        else:
            print(f"❌ Arquivo {streamlit_file} não encontrado")
            print("💡 Execute: streamlit run streamlit_demo.py")
            
    except Exception as e:
        print(f"❌ Erro ao iniciar Streamlit: {e}")
        print("💡 Instale o Streamlit: pip install streamlit")

def run_both():
    """Executar API e dashboard simultaneamente"""
    import threading
    import time
    
    print("🚀 Iniciando FarmTech Solutions (API + Dashboard)...")
    
    # Iniciar API em thread separada
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Aguardar um pouco para a API inicializar
    time.sleep(2)
    
    # Iniciar dashboard
    run_dashboard_server()

def setup_database():
    """Configurar banco de dados"""
    try:
        from farm_tech.data.database import DatabaseManager
        db_manager = DatabaseManager()
        
        print("🗄️ Configurando banco de dados...")
        
        # Criar tabelas
        db_manager.create_tables()
        
        print("✅ Banco de dados configurado com sucesso!")
        
        # Criar dados de exemplo
        create_sample_data = input("Criar dados de exemplo? (s/n): ").lower().strip()
        if create_sample_data == 's':
            db_manager.create_sample_data()
            print("✅ Dados de exemplo criados!")
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco: {e}")

def create_sample_data():
    """Criar dados de exemplo"""
    try:
        from farm_tech.data.database import DatabaseManager
        db_manager = DatabaseManager()
        
        print("📊 Criando dados de exemplo...")
        db_manager.create_sample_data()
        print("✅ Dados de exemplo criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")

def run_ml_predictions():
    """Executar predições de ML"""
    try:
        from farm_tech.ml.predictor import create_ml_predictor
        from farm_tech.data.database import DatabaseManager
        
        print("🤖 Executando predições de Machine Learning...")
        
        # Criar preditor
        ml_predictor = create_ml_predictor()
        
        # Obter dados do banco
        db_manager = DatabaseManager()
        recent_data = db_manager.get_recent_readings(hours=24)
        
        if not recent_data:
            print("⚠️ Nenhum dado recente encontrado. Criando dados de exemplo...")
            db_manager.create_sample_data()
            recent_data = db_manager.get_recent_readings(hours=24)
        
        # Fazer predições
        predictions = ml_predictor.predict_irrigation_needs(recent_data)
        
        print(f"✅ {len(predictions)} predições geradas:")
        
        for i, pred in enumerate(predictions, 1):
            if 'error' not in pred:
                print(f"\n   Predição {i}:")
                print(f"   - Sensor: {pred.get('sensor_id')}")
                print(f"   - Tipo: {pred.get('sensor_type')}")
                print(f"   - Ação: {pred.get('recommended_action')}")
                print(f"   - Prioridade: {pred.get('priority')}")
                print(f"   - Confiança: {pred.get('confidence', 0):.1%}")
        
    except Exception as e:
        print(f"❌ Erro ao executar predições: {e}")

def train_ml_models():
    """Treinar modelos de ML"""
    try:
        from farm_tech.ml.predictor import create_ml_predictor
        from farm_tech.data.database import DatabaseManager
        
        print("🎓 Treinando modelos de Machine Learning...")
        
        # Criar preditor
        ml_predictor = create_ml_predictor()
        
        # Obter dados do banco
        db_manager = DatabaseManager()
        
        # Inicializar/trainar modelos
        result = ml_predictor.initialize_models(db_manager)
        
        if result['success']:
            print("✅ Modelos treinados com sucesso!")
            print(f"   Melhor R²: {result.get('irrigation_model', {}).get('best_score', 'N/A')}")
        else:
            print(f"❌ Erro no treinamento: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ Erro ao treinar modelos: {e}")

def show_system_status():
    """Mostrar status do sistema"""
    try:
        from farm_tech.data.database import DatabaseManager
        from farm_tech.ml.predictor import create_ml_predictor
        
        print("📊 Status do Sistema FarmTech Solutions")
        print("=" * 50)
        
        # Status do banco de dados
        db_manager = DatabaseManager()
        
        try:
            sensors = db_manager.get_all_sensors()
            readings = db_manager.get_recent_readings(hours=24)
            areas = db_manager.get_all_areas()
            
            print(f"🗄️ Banco de Dados:")
            print(f"   - Sensores: {len(sensors)}")
            print(f"   - Leituras (24h): {len(readings)}")
            print(f"   - Áreas: {len(areas)}")
            
        except Exception as e:
            print(f"   ❌ Erro ao conectar com banco: {e}")
        
        # Status dos modelos ML
        try:
            ml_predictor = create_ml_predictor()
            status = ml_predictor.get_model_status()
            
            print(f"\n🤖 Modelos de ML:")
            print(f"   - Modelos carregados: {'Sim' if status['models_loaded'] else 'Não'}")
            if status['models_loaded']:
                print(f"   - Features: {status['irrigation_model']['feature_count']}")
                print(f"   - Última atualização: {status['last_update']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar modelos: {e}")
        
        # Status dos serviços
        print(f"\n🔧 Serviços:")
        print(f"   - API: Disponível em http://localhost:5000")
        print(f"   - Dashboard: Disponível em http://localhost:5001")
        print(f"   - Streamlit: Disponível em http://localhost:8501")
        print(f"   - Documentação: IRRIGACAO_INTELIGENTE.md")
        
        print(f"\n📈 Métricas:")
        print(f"   - Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   - Versão: 1.0.0")
        print(f"   - Status: Operacional")
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def run_irrigation_demo():
    """Executar demonstração de irrigação"""
    try:
        print("🚰 Executando demonstração de irrigação inteligente...")
        
        # Verificar se o arquivo de demonstração existe
        demo_file = "demo_irrigacao_simples.py"
        if os.path.exists(demo_file):
            os.system(f"python {demo_file}")
        else:
            print("❌ Arquivo de demonstração não encontrado")
            print("💡 Execute: python demo_irrigacao_simples.py")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")

def show_help():
    """Mostrar ajuda detalhada"""
    print("🌾 FarmTech Solutions - Sistema de Irrigação Inteligente")
    print("=" * 60)
    print("\n📋 Comandos disponíveis:")
    print("\n🚀 Execução:")
    print("   --mode api          Executar apenas a API")
    print("   --mode dashboard    Executar apenas o dashboard")
    print("   --mode streamlit    Executar dashboard Streamlit")
    print("   --mode both         Executar API + dashboard")
    print("   --demo              Executar demonstração de irrigação")
    
    print("\n🗄️ Banco de Dados:")
    print("   --setup-db          Configurar banco de dados")
    print("   --create-data       Criar dados de exemplo")
    
    print("\n🤖 Machine Learning:")
    print("   --train-ml          Treinar modelos de ML")
    print("   --predict           Executar predições")
    
    print("\n📊 Sistema:")
    print("   --status            Mostrar status do sistema")
    print("   --help              Mostrar esta ajuda")
    
    print("\n💡 Exemplos de uso:")
    print("   python farm_tech_main.py --mode streamlit")
    print("   python farm_tech_main.py --mode both")
    print("   python farm_tech_main.py --setup-db")
    print("   python farm_tech_main.py --train-ml")
    print("   python farm_tech_main.py --demo")
    
    print("\n📚 Documentação:")
    print("   • IRRIGACAO_INTELIGENTE.md - Sistema de irrigação")
    print("   • API_DOCUMENTATION.md - Endpoints da API")
    print("   • IMPLEMENTACAO_SCIKIT_LEARN.md - ML com Scikit-learn")
    
    print("\n🔧 Dependências:")
    print("   pip install flask flask-cors scikit-learn pandas numpy streamlit plotly")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='FarmTech Solutions - Sistema Principal')
    parser.add_argument('--mode', choices=['api', 'dashboard', 'streamlit', 'both'], 
                       help='Modo de execução')
    parser.add_argument('--setup-db', action='store_true', 
                       help='Configurar banco de dados')
    parser.add_argument('--create-data', action='store_true', 
                       help='Criar dados de exemplo')
    parser.add_argument('--train-ml', action='store_true', 
                       help='Treinar modelos de ML')
    parser.add_argument('--predict', action='store_true', 
                       help='Executar predições')
    parser.add_argument('--status', action='store_true', 
                       help='Mostrar status do sistema')
    parser.add_argument('--demo', action='store_true', 
                       help='Executar demonstração de irrigação')
    parser.add_argument('--help', action='store_true', 
                       help='Mostrar ajuda detalhada')
    
    args = parser.parse_args()
    
    # Verificar se nenhum argumento foi fornecido
    if len(sys.argv) == 1:
        show_help()
        return
    
    # Processar argumentos
    if args.help:
        show_help()
    elif args.setup_db:
        setup_database()
    elif args.create_data:
        create_sample_data()
    elif args.train_ml:
        train_ml_models()
    elif args.predict:
        run_ml_predictions()
    elif args.status:
        show_system_status()
    elif args.demo:
        run_irrigation_demo()
    elif args.mode == 'api':
        run_api_server()
    elif args.mode == 'dashboard':
        run_dashboard_server()
    elif args.mode == 'streamlit':
        run_streamlit_dashboard()
    elif args.mode == 'both':
        run_both()
    else:
        print("❌ Argumento inválido. Use --help para ver as opções disponíveis.")

if __name__ == "__main__":
    main() 