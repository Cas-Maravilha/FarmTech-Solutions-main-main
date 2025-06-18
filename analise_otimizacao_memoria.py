#!/usr/bin/env python3
"""
Analisador de Otimização de Memória - FarmTech Solutions ESP32
Compara o uso de memória entre versões do código e calcula economias
"""

import os
import re
import json
from datetime import datetime

class AnalisadorOtimizacao:
    def __init__(self):
        self.resultados = {
            'timestamp': datetime.now().isoformat(),
            'versao_original': {},
            'versao_otimizada': {},
            'economias': {},
            'recomendacoes': []
        }
    
    def analisar_tipos_dados(self, codigo):
        """Analisa tipos de dados usados no código"""
        padroes = {
            'int': r'\bint\s+\w+\s*[=;]',
            'float': r'\bfloat\s+\w+\s*[=;]',
            'uint8_t': r'\buint8_t\s+\w+\s*[=;]',
            'uint16_t': r'\buint16_t\s+\w+\s*[=;]',
            'uint32_t': r'\buint32_t\s+\w+\s*[=;]',
            'String': r'\bString\s+\w+\s*[=;]',
            'const char*': r'\bconst char\*\s+\w+\s*[=;]',
            'bool': r'\bbool\s+\w+\s*[=;]'
        }
        
        contadores = {}
        for tipo, padrao in padroes.items():
            matches = re.findall(padrao, codigo)
            contadores[tipo] = len(matches)
        
        return contadores
    
    def analisar_estruturas(self, codigo):
        """Analisa estruturas de dados"""
        # Procurar por struct
        structs = re.findall(r'struct\s+(\w+)\s*\{([^}]+)\}', codigo, re.DOTALL)
        
        estruturas = {}
        for nome, conteudo in structs:
            tamanho_estimado = self.calcular_tamanho_estrutura(conteudo)
            estruturas[nome] = {
                'tamanho_bytes': tamanho_estimado,
                'campos': self.extrair_campos_estrutura(conteudo)
            }
        
        return estruturas
    
    def calcular_tamanho_estrutura(self, conteudo):
        """Calcula tamanho estimado de uma estrutura"""
        tamanho = 0
        linhas = conteudo.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if ';' in linha and not linha.startswith('//'):
                if 'float' in linha:
                    tamanho += 4
                elif 'int' in linha and 'uint8_t' not in linha and 'uint16_t' not in linha:
                    tamanho += 4
                elif 'uint8_t' in linha:
                    tamanho += 1
                elif 'uint16_t' in linha:
                    tamanho += 2
                elif 'uint32_t' in linha:
                    tamanho += 4
                elif 'bool' in linha:
                    tamanho += 1
                elif 'String' in linha:
                    tamanho += 4  # Ponteiro
        
        return tamanho
    
    def extrair_campos_estrutura(self, conteudo):
        """Extrai campos de uma estrutura"""
        campos = []
        linhas = conteudo.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if ';' in linha and not linha.startswith('//'):
                # Extrair tipo e nome do campo
                match = re.search(r'(\w+(?:\s+\w+)*)\s+(\w+)\s*;', linha)
                if match:
                    tipo = match.group(1).strip()
                    nome = match.group(2).strip()
                    campos.append({'tipo': tipo, 'nome': nome})
        
        return campos
    
    def analisar_strings(self, codigo):
        """Analisa uso de strings"""
        # Strings com F()
        strings_f = len(re.findall(r'F\("([^"]+)"\)', codigo))
        
        # Strings com String
        strings_string = len(re.findall(r'String\s+\w+\s*=', codigo))
        
        # Strings com const char*
        strings_const = len(re.findall(r'const char\*\s+\w+\s*=', codigo))
        
        return {
            'strings_f': strings_f,
            'strings_string': strings_string,
            'strings_const': strings_const
        }
    
    def analisar_json(self, codigo):
        """Analisa uso de JSON"""
        # Procurar por StaticJsonDocument
        matches = re.findall(r'StaticJsonDocument<(\d+)>', codigo)
        tamanhos = [int(match) for match in matches]
        
        return {
            'documentos': len(tamanhos),
            'tamanhos': tamanhos,
            'total_bytes': sum(tamanhos)
        }
    
    def analisar_codigo(self, arquivo, versao):
        """Analisa um arquivo de código"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            analise = {
                'arquivo': arquivo,
                'tamanho_arquivo': len(codigo),
                'linhas': len(codigo.split('\n')),
                'tipos_dados': self.analisar_tipos_dados(codigo),
                'estruturas': self.analisar_estruturas(codigo),
                'strings': self.analisar_strings(codigo),
                'json': self.analisar_json(codigo)
            }
            
            # Calcular uso estimado de memória
            analise['memoria_estimada'] = self.calcular_memoria_estimada(analise)
            
            return analise
            
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {arquivo}")
            return None
        except Exception as e:
            print(f"Erro ao analisar {arquivo}: {e}")
            return None
    
    def calcular_memoria_estimada(self, analise):
        """Calcula uso estimado de memória"""
        memoria = 0
        
        # Memória por tipos de dados
        tipos_memoria = {
            'int': 4,
            'float': 4,
            'uint8_t': 1,
            'uint16_t': 2,
            'uint32_t': 4,
            'String': 4,  # Ponteiro
            'const char*': 4,  # Ponteiro
            'bool': 1
        }
        
        for tipo, quantidade in analise['tipos_dados'].items():
            if tipo in tipos_memoria:
                memoria += quantidade * tipos_memoria[tipo]
        
        # Memória das estruturas
        for nome, struct in analise['estruturas'].items():
            memoria += struct['tamanho_bytes']
        
        # Memória JSON
        memoria += analise['json']['total_bytes']
        
        # Memória strings (estimativa)
        memoria += analise['strings']['strings_string'] * 20  # String média
        memoria += analise['strings']['strings_const'] * 4   # Ponteiro
        
        return memoria
    
    def comparar_versoes(self, arquivo_original, arquivo_otimizado):
        """Compara duas versões do código"""
        print("=== ANÁLISE DE OTIMIZAÇÃO DE MEMÓRIA ===\n")
        
        # Analisar versão original
        print("Analisando versão original...")
        self.resultados['versao_original'] = self.analisar_codigo(arquivo_original, 'original')
        
        # Analisar versão otimizada
        print("Analisando versão otimizada...")
        self.resultados['versao_otimizada'] = self.analisar_codigo(arquivo_otimizado, 'otimizada')
        
        if not self.resultados['versao_original'] or not self.resultados['versao_otimizada']:
            print("Erro: Não foi possível analisar um dos arquivos")
            return
        
        # Calcular economias
        self.calcular_economias()
        
        # Gerar recomendações
        self.gerar_recomendacoes()
        
        # Exibir resultados
        self.exibir_resultados()
        
        # Salvar relatório
        self.salvar_relatorio()
    
    def calcular_economias(self):
        """Calcula economias entre as versões"""
        orig = self.resultados['versao_original']
        otim = self.resultados['versao_otimizada']
        
        economias = {}
        
        # Economia de memória total
        memoria_orig = orig['memoria_estimada']
        memoria_otim = otim['memoria_estimada']
        economia_memoria = memoria_orig - memoria_otim
        percentual_economia = (economia_memoria / memoria_orig) * 100
        
        economias['memoria'] = {
            'original': memoria_orig,
            'otimizada': memoria_otim,
            'economia_bytes': economia_memoria,
            'economia_percentual': percentual_economia
        }
        
        # Economia por tipo de dado
        for tipo in orig['tipos_dados']:
            if tipo in otim['tipos_dados']:
                qtd_orig = orig['tipos_dados'][tipo]
                qtd_otim = otim['tipos_dados'][tipo]
                if qtd_orig != qtd_otim:
                    economias[f'tipo_{tipo}'] = {
                        'original': qtd_orig,
                        'otimizada': qtd_otim,
                        'diferenca': qtd_orig - qtd_otim
                    }
        
        # Economia JSON
        json_orig = orig['json']['total_bytes']
        json_otim = otim['json']['total_bytes']
        economias['json'] = {
            'original': json_orig,
            'otimizada': json_otim,
            'economia_bytes': json_orig - json_otim
        }
        
        self.resultados['economias'] = economias
    
    def gerar_recomendacoes(self):
        """Gera recomendações de otimização"""
        orig = self.resultados['versao_original']
        otim = self.resultados['versao_otimizada']
        recs = []
        
        # Verificar uso de int vs uint8_t/uint16_t
        if orig['tipos_dados'].get('int', 0) > otim['tipos_dados'].get('int', 0):
            recs.append("✅ Substituição de 'int' por tipos menores (uint8_t, uint16_t)")
        
        # Verificar uso de String vs const char*
        if orig['strings']['strings_string'] > otim['strings']['strings_string']:
            recs.append("✅ Substituição de 'String' por 'const char*'")
        
        # Verificar uso de F()
        if otim['strings']['strings_f'] > 0:
            recs.append("✅ Uso da macro F() para strings constantes")
        
        # Verificar JSON
        if orig['json']['total_bytes'] > otim['json']['total_bytes']:
            recs.append("✅ Redução do tamanho de StaticJsonDocument")
        
        # Verificar estruturas
        for nome, struct_orig in orig['estruturas'].items():
            if nome in otim['estruturas']:
                struct_otim = otim['estruturas'][nome]
                if struct_orig['tamanho_bytes'] > struct_otim['tamanho_bytes']:
                    recs.append(f"✅ Otimização da estrutura '{nome}'")
        
        self.resultados['recomendacoes'] = recs
    
    def exibir_resultados(self):
        """Exibe resultados da análise"""
        print("\n" + "="*60)
        print("RESULTADOS DA ANÁLISE DE OTIMIZAÇÃO")
        print("="*60)
        
        # Resumo geral
        eco = self.resultados['economias']['memoria']
        print(f"\n📊 RESUMO GERAL:")
        print(f"   Memória Original: {eco['original']:,} bytes")
        print(f"   Memória Otimizada: {eco['otimizada']:,} bytes")
        print(f"   Economia: {eco['economia_bytes']:,} bytes ({eco['economia_percentual']:.1f}%)")
        
        # Tipos de dados
        print(f"\n🔧 TIPOS DE DADOS:")
        orig = self.resultados['versao_original']['tipos_dados']
        otim = self.resultados['versao_otimizada']['tipos_dados']
        
        for tipo in sorted(set(orig.keys()) | set(otim.keys())):
            qtd_orig = orig.get(tipo, 0)
            qtd_otim = otim.get(tipo, 0)
            if qtd_orig != qtd_otim:
                print(f"   {tipo}: {qtd_orig} → {qtd_otim} ({qtd_orig - qtd_otim:+d})")
        
        # Estruturas
        print(f"\n🏗️  ESTRUTURAS DE DADOS:")
        orig_structs = self.resultados['versao_original']['estruturas']
        otim_structs = self.resultados['versao_otimizada']['estruturas']
        
        for nome in sorted(set(orig_structs.keys()) | set(otim_structs.keys())):
            if nome in orig_structs and nome in otim_structs:
                tam_orig = orig_structs[nome]['tamanho_bytes']
                tam_otim = otim_structs[nome]['tamanho_bytes']
                if tam_orig != tam_otim:
                    economia = tam_orig - tam_otim
                    print(f"   {nome}: {tam_orig} → {tam_otim} bytes ({economia:+d} bytes)")
        
        # JSON
        json_eco = self.resultados['economias']['json']
        print(f"\n📄 JSON:")
        print(f"   Total Original: {json_eco['original']} bytes")
        print(f"   Total Otimizado: {json_eco['otimizada']} bytes")
        print(f"   Economia: {json_eco['economia_bytes']} bytes")
        
        # Strings
        print(f"\n📝 STRINGS:")
        orig_str = self.resultados['versao_original']['strings']
        otim_str = self.resultados['versao_otimizada']['strings']
        print(f"   String: {orig_str['strings_string']} → {otim_str['strings_string']}")
        print(f"   const char*: {orig_str['strings_const']} → {otim_str['strings_const']}")
        print(f"   F(): {orig_str['strings_f']} → {otim_str['strings_f']}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES IMPLEMENTADAS:")
        for rec in self.resultados['recomendacoes']:
            print(f"   {rec}")
        
        print("\n" + "="*60)
    
    def salvar_relatorio(self):
        """Salva relatório em JSON"""
        nome_arquivo = f"relatorio_otimizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo: {nome_arquivo}")

def main():
    """Função principal"""
    analisador = AnalisadorOtimizacao()
    
    # Verificar se os arquivos existem
    arquivos_teste = [
        'farmtech_esp32_serial_plotter.ino',
        'farmtech_otimizado.ino'
    ]
    
    arquivos_existentes = []
    for arquivo in arquivos_teste:
        if os.path.exists(arquivo):
            arquivos_existentes.append(arquivo)
    
    if len(arquivos_existentes) < 2:
        print("❌ Arquivos necessários não encontrados!")
        print("Arquivos necessários:")
        for arquivo in arquivos_teste:
            print(f"   - {arquivo}")
        return
    
    # Usar os arquivos encontrados
    arquivo_original = arquivos_existentes[0]
    arquivo_otimizado = arquivos_existentes[1]
    
    print(f"🔍 Analisando otimizações entre:")
    print(f"   Original: {arquivo_original}")
    print(f"   Otimizado: {arquivo_otimizado}")
    
    # Executar análise
    analisador.comparar_versoes(arquivo_original, arquivo_otimizado)

if __name__ == "__main__":
    main() 