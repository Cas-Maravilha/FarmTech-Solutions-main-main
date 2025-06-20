#!/usr/bin/env python3
"""
Verificador de Otimizações - FarmTech Solutions ESP32
Valida e verifica as otimizações implementadas no código
"""

import re
import os
from datetime import datetime

class VerificadorOtimizacoes:
    def __init__(self):
        self.resultados = {
            'timestamp': datetime.now().isoformat(),
            'arquivo_analisado': '',
            'otimizacoes_encontradas': [],
            'problemas_identificados': [],
            'pontuacao': 0,
            'max_pontos': 100
        }
    
    def verificar_tipos_dados(self, codigo):
        """Verifica otimização de tipos de dados"""
        print("🔍 Verificando tipos de dados...")
        
        # Contar tipos otimizados
        tipos_otimizados = {
            'uint8_t': len(re.findall(r'\buint8_t\s+\w+\s*[=;]', codigo)),
            'uint16_t': len(re.findall(r'\buint16_t\s+\w+\s*[=;]', codigo)),
            'uint32_t': len(re.findall(r'\buint32_t\s+\w+\s*[=;]', codigo)),
            'int8_t': len(re.findall(r'\bint8_t\s+\w+\s*[=;]', codigo)),
            'int16_t': len(re.findall(r'\bint16_t\s+\w+\s*[=;]', codigo))
        }
        
        # Contar tipos não otimizados
        tipos_nao_otimizados = {
            'int': len(re.findall(r'\bint\s+\w+\s*[=;]', codigo)),
            'float': len(re.findall(r'\bfloat\s+\w+\s*[=;]', codigo)),
            'long': len(re.findall(r'\blong\s+\w+\s*[=;]', codigo))
        }
        
        total_otimizados = sum(tipos_otimizados.values())
        total_nao_otimizados = sum(tipos_nao_otimizados.values())
        
        print(f"   ✅ Tipos otimizados encontrados: {total_otimizados}")
        print(f"   ⚠️  Tipos não otimizados: {total_nao_otimizados}")
        
        # Calcular pontuação
        if total_otimizados > 0:
            pontuacao = min(25, (total_otimizados / (total_otimizados + total_nao_otimizados)) * 25)
        else:
            pontuacao = 0
        
        # Adicionar otimizações encontradas
        for tipo, qtd in tipos_otimizados.items():
            if qtd > 0:
                self.resultados['otimizacoes_encontradas'].append(
                    f"Uso de {tipo} ({qtd} variáveis)"
                )
        
        # Adicionar problemas
        for tipo, qtd in tipos_nao_otimizados.items():
            if qtd > 0:
                self.resultados['problemas_identificados'].append(
                    f"Uso de {tipo} ({qtd} variáveis) - pode ser otimizado"
                )
        
        return pontuacao
    
    def verificar_strings(self, codigo):
        """Verifica otimização de strings"""
        print("🔍 Verificando otimização de strings...")
        
        # Contar strings otimizadas
        strings_f = len(re.findall(r'F\("([^"]+)"\)', codigo))
        strings_const = len(re.findall(r'const char\*\s+\w+\s*=', codigo))
        
        # Contar strings não otimizadas
        strings_string = len(re.findall(r'String\s+\w+\s*=', codigo))
        strings_concat = len(re.findall(r'String\s*\+\s*String', codigo))
        
        print(f"   ✅ Strings F(): {strings_f}")
        print(f"   ✅ Strings const char*: {strings_const}")
        print(f"   ⚠️  Strings String: {strings_string}")
        print(f"   ⚠️  Concatenações String: {strings_concat}")
        
        # Calcular pontuação
        total_otimizadas = strings_f + strings_const
        total_nao_otimizadas = strings_string + strings_concat
        
        if total_otimizadas > 0:
            pontuacao = min(25, (total_otimizadas / (total_otimizadas + total_nao_otimizadas + 1)) * 25)
        else:
            pontuacao = 0
        
        # Adicionar otimizações
        if strings_f > 0:
            self.resultados['otimizacoes_encontradas'].append(
                f"Uso da macro F() ({strings_f} ocorrências)"
            )
        if strings_const > 0:
            self.resultados['otimizacoes_encontradas'].append(
                f"Uso de const char* ({strings_const} variáveis)"
            )
        
        # Adicionar problemas
        if strings_string > 0:
            self.resultados['problemas_identificados'].append(
                f"Uso de String ({strings_string} variáveis) - considere const char*"
            )
        if strings_concat > 0:
            self.resultados['problemas_identificados'].append(
                f"Concatenação de String ({strings_concat} ocorrências) - use printf"
            )
        
        return pontuacao
    
    def verificar_estruturas(self, codigo):
        """Verifica otimização de estruturas"""
        print("🔍 Verificando estruturas de dados...")
        
        # Encontrar estruturas
        structs = re.findall(r'struct\s+(\w+)\s*\{([^}]+)\}', codigo, re.DOTALL)
        
        pontuacao_total = 0
        estruturas_analisadas = 0
        
        for nome, conteudo in structs:
            print(f"   📋 Estrutura: {nome}")
            
            # Analisar campos
            campos = self.analisar_campos_estrutura(conteudo)
            tamanho_estimado = self.calcular_tamanho_estrutura(campos)
            
            print(f"      Tamanho estimado: {tamanho_estimado} bytes")
            print(f"      Campos: {len(campos)}")
            
            # Verificar otimizações nos campos
            campos_otimizados = 0
            for campo in campos:
                if campo['tipo'] in ['uint8_t', 'uint16_t', 'int8_t', 'int16_t']:
                    campos_otimizados += 1
                    print(f"      ✅ {campo['nome']}: {campo['tipo']}")
                else:
                    print(f"      ⚠️  {campo['nome']}: {campo['tipo']}")
            
            # Calcular pontuação da estrutura
            if len(campos) > 0:
                pontuacao_estrutura = (campos_otimizados / len(campos)) * 20
                pontuacao_total += pontuacao_estrutura
                estruturas_analisadas += 1
            
            # Adicionar otimizações
            if campos_otimizados > 0:
                self.resultados['otimizacoes_encontradas'].append(
                    f"Estrutura {nome}: {campos_otimizados}/{len(campos)} campos otimizados"
                )
        
        if estruturas_analisadas > 0:
            return pontuacao_total / estruturas_analisadas
        else:
            return 0
    
    def analisar_campos_estrutura(self, conteudo):
        """Analisa campos de uma estrutura"""
        campos = []
        linhas = conteudo.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if ';' in linha and not linha.startswith('//'):
                match = re.search(r'(\w+(?:\s+\w+)*)\s+(\w+)\s*;', linha)
                if match:
                    tipo = match.group(1).strip()
                    nome = match.group(2).strip()
                    campos.append({'tipo': tipo, 'nome': nome})
        
        return campos
    
    def calcular_tamanho_estrutura(self, campos):
        """Calcula tamanho estimado de uma estrutura"""
        tamanho = 0
        tipos_tamanho = {
            'uint8_t': 1, 'int8_t': 1,
            'uint16_t': 2, 'int16_t': 2,
            'uint32_t': 4, 'int32_t': 4,
            'int': 4, 'float': 4, 'bool': 1
        }
        
        for campo in campos:
            tipo = campo['tipo']
            if tipo in tipos_tamanho:
                tamanho += tipos_tamanho[tipo]
            else:
                tamanho += 4  # Tamanho padrão
        
        return tamanho
    
    def verificar_json(self, codigo):
        """Verifica otimização de JSON"""
        print("🔍 Verificando otimização de JSON...")
        
        # Encontrar StaticJsonDocument
        matches = re.findall(r'StaticJsonDocument<(\d+)>', codigo)
        
        if not matches:
            print("   ℹ️  Nenhum StaticJsonDocument encontrado")
            return 0
        
        tamanhos = [int(match) for match in matches]
        tamanho_menor = min(tamanhos)
        tamanho_maior = max(tamanhos)
        
        print(f"   📄 Tamanhos encontrados: {tamanhos}")
        print(f"   📄 Menor tamanho: {tamanho_menor} bytes")
        print(f"   📄 Maior tamanho: {tamanho_maior} bytes")
        
        # Calcular pontuação baseada no tamanho menor
        if tamanho_menor <= 256:
            pontuacao = 15
        elif tamanho_menor <= 512:
            pontuacao = 10
        else:
            pontuacao = 5
        
        # Adicionar otimizações
        if tamanho_menor <= 256:
            self.resultados['otimizacoes_encontradas'].append(
                f"JSON otimizado: {tamanho_menor} bytes"
            )
        else:
            self.resultados['problemas_identificados'].append(
                f"JSON pode ser otimizado: {tamanho_menor} bytes"
            )
        
        return pontuacao
    
    def verificar_comentarios_otimizacao(self, codigo):
        """Verifica comentários sobre otimizações"""
        print("🔍 Verificando comentários de otimização...")
        
        # Procurar por comentários relacionados a otimização
        comentarios_otimizacao = [
            r'//.*otimiza[çc][ãa]o',
            r'//.*economia',
            r'//.*mem[oó]ria',
            r'//.*OTIMIZAÇÃO',
            r'//.*ECONOMIA',
            r'//.*uint8_t',
            r'//.*uint16_t',
            r'//.*F\(',
            r'//.*const char\*'
        ]
        
        comentarios_encontrados = 0
        for padrao in comentarios_otimizacao:
            matches = re.findall(padrao, codigo, re.IGNORECASE)
            comentarios_encontrados += len(matches)
        
        print(f"   📝 Comentários de otimização: {comentarios_encontrados}")
        
        # Calcular pontuação
        if comentarios_encontrados >= 10:
            pontuacao = 15
        elif comentarios_encontrados >= 5:
            pontuacao = 10
        elif comentarios_encontrados >= 1:
            pontuacao = 5
        else:
            pontuacao = 0
        
        if comentarios_encontrados > 0:
            self.resultados['otimizacoes_encontradas'].append(
                f"Comentários explicativos: {comentarios_encontrados} encontrados"
            )
        else:
            self.resultados['problemas_identificados'].append(
                "Faltam comentários explicando as otimizações"
            )
        
        return pontuacao
    
    def verificar_arquivo(self, arquivo):
        """Verifica um arquivo de código"""
        print(f"\n🔍 ANALISANDO ARQUIVO: {arquivo}")
        print("="*60)
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            self.resultados['arquivo_analisado'] = arquivo
            
            # Executar verificações
            pontuacao_tipos = self.verificar_tipos_dados(codigo)
            pontuacao_strings = self.verificar_strings(codigo)
            pontuacao_estruturas = self.verificar_estruturas(codigo)
            pontuacao_json = self.verificar_json(codigo)
            pontuacao_comentarios = self.verificar_comentarios_otimizacao(codigo)
            
            # Calcular pontuação total
            pontuacao_total = (
                pontuacao_tipos +
                pontuacao_strings +
                pontuacao_estruturas +
                pontuacao_json +
                pontuacao_comentarios
            )
            
            self.resultados['pontuacao'] = pontuacao_total
            
            # Exibir resultados
            self.exibir_resultados()
            
            return self.resultados
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return None
        except Exception as e:
            print(f"❌ Erro ao analisar arquivo: {e}")
            return None
    
    def exibir_resultados(self):
        """Exibe resultados da verificação"""
        print("\n" + "="*60)
        print("RESULTADOS DA VERIFICAÇÃO DE OTIMIZAÇÕES")
        print("="*60)
        
        # Pontuação
        pontuacao = self.resultados['pontuacao']
        max_pontos = self.resultados['max_pontos']
        percentual = (pontuacao / max_pontos) * 100
        
        print(f"\n📊 PONTUAÇÃO: {pontuacao}/{max_pontos} ({percentual:.1f}%)")
        
        # Classificação
        if percentual >= 90:
            classificacao = "🏆 EXCELENTE"
        elif percentual >= 80:
            classificacao = "🥇 MUITO BOM"
        elif percentual >= 70:
            classificacao = "🥈 BOM"
        elif percentual >= 60:
            classificacao = "🥉 REGULAR"
        else:
            classificacao = "⚠️  PRECISA MELHORAR"
        
        print(f"🏅 CLASSIFICAÇÃO: {classificacao}")
        
        # Otimizações encontradas
        if self.resultados['otimizacoes_encontradas']:
            print(f"\n✅ OTIMIZAÇÕES ENCONTRADAS ({len(self.resultados['otimizacoes_encontradas'])}):")
            for i, otimizacao in enumerate(self.resultados['otimizacoes_encontradas'], 1):
                print(f"   {i}. {otimizacao}")
        else:
            print(f"\n❌ NENHUMA OTIMIZAÇÃO ENCONTRADA")
        
        # Problemas identificados
        if self.resultados['problemas_identificados']:
            print(f"\n⚠️  PROBLEMAS IDENTIFICADOS ({len(self.resultados['problemas_identificados'])}):")
            for i, problema in enumerate(self.resultados['problemas_identificados'], 1):
                print(f"   {i}. {problema}")
        else:
            print(f"\n✅ NENHUM PROBLEMA IDENTIFICADO")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if percentual < 80:
            print("   - Revise os tipos de dados usados")
            print("   - Substitua String por const char* quando possível")
            print("   - Use a macro F() para strings constantes")
            print("   - Otimize estruturas de dados")
            print("   - Reduza o tamanho de StaticJsonDocument")
            print("   - Adicione comentários explicando as otimizações")
        else:
            print("   - Continue mantendo as boas práticas")
            print("   - Considere otimizações adicionais se necessário")
        
        print("\n" + "="*60)

def main():
    """Função principal"""
    verificador = VerificadorOtimizacoes()
    
    # Arquivos para verificar
    arquivos = [
        'farmtech_otimizado.ino',
        'farmtech_esp32_serial_plotter.ino'
    ]
    
    # Verificar arquivos existentes
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            print(f"\n🎯 Verificando: {arquivo}")
            resultado = verificador.verificar_arquivo(arquivo)
            
            if resultado:
                # Salvar resultado
                nome_relatorio = f"verificacao_{arquivo.replace('.ino', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import json
                with open(nome_relatorio, 'w', encoding='utf-8') as f:
                    json.dump(resultado, f, indent=2, ensure_ascii=False)
                print(f"📄 Relatório salvo: {nome_relatorio}")
        else:
            print(f"❌ Arquivo não encontrado: {arquivo}")

if __name__ == "__main__":
    main() 