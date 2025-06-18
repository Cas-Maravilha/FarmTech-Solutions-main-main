#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Demonstração do Serial Plotter
Script Python para simular e visualizar dados do ESP32
"""

import time
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class FarmTechSerialPlotterDemo:
    """Demonstração do Serial Plotter do FarmTech Solutions"""
    
    def __init__(self):
        self.tempo_inicio = time.time()
        self.dados = {
            'tempo': [],
            'temperatura': [],
            'umidade_ar': [],
            'umidade_solo': [],
            'setpoint': [],
            'erro': [],
            'irrigacao': [],
            'status': []
        }
        
        # Parâmetros de simulação
        self.setpoint_umidade = 50.0
        self.irrigacao_ativa = False
        self.status_sistema = 0  # 0=OK, 1-4=Alertas
        
        # Configurações de plotagem
        self.fig, self.axs = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle('FarmTech Solutions - Serial Plotter Demo', fontsize=16)
        
        # Configurar subplots
        self.configurar_subplots()
        
    def configurar_subplots(self):
        """Configura os subplots para visualização"""
        # Gráfico 1: Temperatura e Umidade do Ar
        self.axs[0, 0].set_title('🌡️ Temperatura e 💨 Umidade do Ar')
        self.axs[0, 0].set_ylabel('Temperatura (°C)')
        self.axs[0, 0].set_xlabel('Tempo (s)')
        self.axs[0, 0].grid(True, alpha=0.3)
        
        # Gráfico 2: Umidade do Solo e Setpoint
        self.axs[0, 1].set_title('🌱 Umidade do Solo e 🎯 Setpoint')
        self.axs[0, 1].set_ylabel('Umidade (%)')
        self.axs[0, 1].set_xlabel('Tempo (s)')
        self.axs[0, 1].grid(True, alpha=0.3)
        
        # Gráfico 3: Erro e Controle PID
        self.axs[1, 0].set_title('📊 Erro e 🎛️ Controle PID')
        self.axs[1, 0].set_ylabel('Erro (%)')
        self.axs[1, 0].set_xlabel('Tempo (s)')
        self.axs[1, 0].grid(True, alpha=0.3)
        
        # Gráfico 4: Status do Sistema
        self.axs[1, 1].set_title('💧 Irrigação e 📋 Status')
        self.axs[1, 1].set_ylabel('Status')
        self.axs[1, 1].set_xlabel('Tempo (s)')
        self.axs[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
    
    def simular_dados_sensores(self):
        """Simula leitura dos sensores"""
        tempo_atual = time.time() - self.tempo_inicio
        
        # Simular temperatura com variação sazonal
        temperatura_base = 25.0
        variacao_temp = 3.0 * np.sin(tempo_atual / 30.0)  # Variação de 30s
        ruido_temp = random.uniform(-0.5, 0.5)
        temperatura = temperatura_base + variacao_temp + ruido_temp
        
        # Simular umidade do ar (inversamente proporcional à temperatura)
        umidade_ar_base = 70.0
        variacao_umid = -2.0 * np.sin(tempo_atual / 30.0)
        ruido_umid = random.uniform(-1.0, 1.0)
        umidade_ar = umidade_ar_base + variacao_umid + ruido_umid
        umidade_ar = max(30.0, min(95.0, umidade_ar))
        
        # Simular umidade do solo com controle PID
        if len(self.dados['umidade_solo']) > 0:
            umidade_anterior = self.dados['umidade_solo'][-1]
        else:
            umidade_anterior = 50.0
        
        # Efeito da irrigação
        if self.irrigacao_ativa:
            variacao_solo = random.uniform(0.5, 2.0)  # Aumenta com irrigação
        else:
            variacao_solo = random.uniform(-1.0, -0.2)  # Diminui naturalmente
        
        # Efeito da temperatura (evaporação)
        efeito_temp = (temperatura - 25.0) * 0.1
        variacao_solo -= efeito_temp
        
        umidade_solo = umidade_anterior + variacao_solo
        umidade_solo = max(20.0, min(90.0, umidade_solo))
        
        # Calcular erro
        erro = self.setpoint_umidade - umidade_solo
        
        # Controle PID simples
        if abs(erro) > 5.0 and not self.irrigacao_ativa:
            self.irrigacao_ativa = True
        elif abs(erro) < 2.0 and self.irrigacao_ativa:
            self.irrigacao_ativa = False
        
        # Determinar status do sistema
        self.status_sistema = 0  # OK
        if temperatura > 35.0:
            self.status_sistema = 1  # TEMP ALTA
        elif temperatura < 10.0:
            self.status_sistema = 2  # TEMP BAIXA
        elif umidade_solo < 30.0:
            self.status_sistema = 3  # SOLO SECO
        elif umidade_solo > 80.0:
            self.status_sistema = 4  # SOLO MUITO ÚMIDO
        
        return {
            'tempo': tempo_atual,
            'temperatura': temperatura,
            'umidade_ar': umidade_ar,
            'umidade_solo': umidade_solo,
            'setpoint': self.setpoint_umidade,
            'erro': erro,
            'irrigacao': 1 if self.irrigacao_ativa else 0,
            'status': self.status_sistema
        }
    
    def adicionar_dados(self, dados):
        """Adiciona novos dados à lista"""
        for chave, valor in dados.items():
            self.dados[chave].append(valor)
        
        # Manter apenas os últimos 100 pontos
        max_pontos = 100
        for chave in self.dados:
            if len(self.dados[chave]) > max_pontos:
                self.dados[chave] = self.dados[chave][-max_pontos:]
    
    def atualizar_graficos(self, frame):
        """Atualiza os gráficos em tempo real"""
        # Simular novos dados
        dados_novos = self.simular_dados_sensores()
        self.adicionar_dados(dados_novos)
        
        # Limpar gráficos
        for ax in self.axs.flat:
            ax.clear()
        
        # Reconfigurar subplots
        self.configurar_subplots()
        
        # Plotar dados
        if len(self.dados['tempo']) > 0:
            tempo = self.dados['tempo']
            
            # Gráfico 1: Temperatura e Umidade do Ar
            ax1 = self.axs[0, 0]
            ax1.plot(tempo, self.dados['temperatura'], 'r-', label='Temperatura (°C)', linewidth=2)
            ax1_twin = ax1.twinx()
            ax1_twin.plot(tempo, self.dados['umidade_ar'], 'b-', label='Umidade Ar (%)', linewidth=2)
            ax1_twin.set_ylabel('Umidade do Ar (%)')
            ax1.legend(loc='upper left')
            ax1_twin.legend(loc='upper right')
            
            # Gráfico 2: Umidade do Solo e Setpoint
            ax2 = self.axs[0, 1]
            ax2.plot(tempo, self.dados['umidade_solo'], 'g-', label='Umidade Solo (%)', linewidth=2)
            ax2.plot(tempo, self.dados['setpoint'], 'g--', label='Setpoint (%)', linewidth=2)
            ax2.axhline(y=30, color='red', linestyle=':', alpha=0.7, label='Limite Seco')
            ax2.axhline(y=80, color='blue', linestyle=':', alpha=0.7, label='Limite Úmido')
            ax2.legend()
            
            # Gráfico 3: Erro e Controle
            ax3 = self.axs[1, 0]
            ax3.plot(tempo, self.dados['erro'], 'orange', label='Erro (%)', linewidth=2)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax3.axhline(y=5, color='red', linestyle=':', alpha=0.7, label='Limite Superior')
            ax3.axhline(y=-5, color='red', linestyle=':', alpha=0.7, label='Limite Inferior')
            ax3.legend()
            
            # Gráfico 4: Irrigação e Status
            ax4 = self.axs[1, 1]
            ax4.plot(tempo, self.dados['irrigacao'], 'purple', label='Irrigação (0/1)', linewidth=3)
            ax4.plot(tempo, self.dados['status'], 'brown', label='Status (0-4)', linewidth=2)
            ax4.set_ylim(-0.5, 4.5)
            ax4.legend()
        
        # Atualizar título com informações em tempo real
        if len(self.dados['tempo']) > 0:
            tempo_atual = self.dados['tempo'][-1]
            temp_atual = self.dados['temperatura'][-1]
            umid_solo_atual = self.dados['umidade_solo'][-1]
            status_texto = self.obter_status_texto(self.dados['status'][-1])
            
            titulo = f'FarmTech Solutions - Serial Plotter Demo | Tempo: {tempo_atual:.1f}s | Temp: {temp_atual:.1f}°C | Solo: {umid_solo_atual:.1f}% | Status: {status_texto}'
            self.fig.suptitle(titulo, fontsize=12)
        
        return self.axs.flat
    
    def obter_status_texto(self, status):
        """Converte código de status para texto"""
        status_dict = {
            0: "OK",
            1: "TEMP ALTA",
            2: "TEMP BAIXA", 
            3: "SOLO SECO",
            4: "SOLO MUITO ÚMIDO"
        }
        return status_dict.get(status, "DESCONHECIDO")
    
    def simular_serial_output(self):
        """Simula a saída do Serial Plotter"""
        print("=== FARM TECH SOLUTIONS - SERIAL PLOTTER ===")
        print("Tempo,Temperatura,Umidade_Ar,Umidade_Solo,Setpoint,Erro,Irrigacao,Status")
        print("s,°C,%,%,%,%,0/1,0-4")
        print("=== INÍCIO DOS DADOS ===")
        
        for i in range(50):  # Simular 50 leituras
            dados = self.simular_dados_sensores()
            self.adicionar_dados(dados)
            
            # Formato CSV como no ESP32
            print(f"{dados['tempo']:.1f},{dados['temperatura']:.2f},{dados['umidade_ar']:.2f},{dados['umidade_solo']:.0f},{dados['setpoint']:.1f},{dados['erro']:.1f},{dados['irrigacao']},{dados['status']}")
            
            time.sleep(0.1)  # Simular intervalo de 100ms
    
    def executar_demo_grafica(self):
        """Executa a demonstração gráfica"""
        print("🚀 Iniciando demonstração gráfica do Serial Plotter...")
        print("📊 Abrindo gráficos em tempo real...")
        print("⏱️  Simulando dados do ESP32...")
        print("💡 Pressione Ctrl+C para parar")
        
        try:
            # Configurar animação
            ani = animation.FuncAnimation(
                self.fig, 
                self.atualizar_graficos, 
                interval=100,  # 100ms entre atualizações
                blit=False
            )
            
            plt.show()
            
        except KeyboardInterrupt:
            print("\n🛑 Demonstração interrompida pelo usuário")
        except Exception as e:
            print(f"❌ Erro na demonstração: {e}")
    
    def gerar_relatorio(self):
        """Gera relatório dos dados simulados"""
        if len(self.dados['tempo']) == 0:
            print("❌ Nenhum dado disponível para relatório")
            return
        
        print("\n📊 === RELATÓRIO DA SIMULAÇÃO ===")
        print(f"⏱️  Tempo total: {self.dados['tempo'][-1]:.1f} segundos")
        print(f"📈 Total de leituras: {len(self.dados['tempo'])}")
        
        # Estatísticas de temperatura
        temp_media = np.mean(self.dados['temperatura'])
        temp_max = np.max(self.dados['temperatura'])
        temp_min = np.min(self.dados['temperatura'])
        print(f"🌡️  Temperatura - Média: {temp_media:.1f}°C, Max: {temp_max:.1f}°C, Min: {temp_min:.1f}°C")
        
        # Estatísticas de umidade do solo
        umid_media = np.mean(self.dados['umidade_solo'])
        umid_max = np.max(self.dados['umidade_solo'])
        umid_min = np.min(self.dados['umidade_solo'])
        print(f"🌱 Umidade Solo - Média: {umid_media:.1f}%, Max: {umid_max:.1f}%, Min: {umid_min:.1f}%")
        
        # Contagem de irrigações
        irrigacoes = sum(self.dados['irrigacao'])
        print(f"💧 Ativações de irrigação: {irrigacoes}")
        
        # Análise de status
        status_counts = {}
        for status in self.dados['status']:
            status_texto = self.obter_status_texto(status)
            status_counts[status_texto] = status_counts.get(status_texto, 0) + 1
        
        print("📋 Distribuição de Status:")
        for status, count in status_counts.items():
            percentual = (count / len(self.dados['status'])) * 100
            print(f"   {status}: {count} vezes ({percentual:.1f}%)")
        
        print("=====================================")

def main():
    """Função principal"""
    print("🌾 FarmTech Solutions - Serial Plotter Demo")
    print("=" * 50)
    
    demo = FarmTechSerialPlotterDemo()
    
    # Menu de opções
    while True:
        print("\n📋 Escolha uma opção:")
        print("1. 📊 Demonstração gráfica (tempo real)")
        print("2. 📄 Simular saída Serial (CSV)")
        print("3. 📈 Gerar relatório")
        print("4. 🚪 Sair")
        
        opcao = input("\nDigite sua escolha (1-4): ").strip()
        
        if opcao == "1":
            demo.executar_demo_grafica()
        elif opcao == "2":
            demo.simular_serial_output()
        elif opcao == "3":
            demo.gerar_relatorio()
        elif opcao == "4":
            print("👋 Obrigado por usar o FarmTech Serial Plotter Demo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main() 