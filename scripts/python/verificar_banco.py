#!/usr/bin/env python3
import sqlite3

try:
    conn = sqlite3.connect('data/farmtech.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    
    print(f'Tabelas encontradas: {len(tables)}')
    for table in tables:
        print(f'- {table[0]}')
    
    # Verificar dados
    cursor.execute('SELECT COUNT(*) FROM AREA')
    areas = cursor.fetchone()[0]
    print(f'\nÁreas: {areas}')
    
    cursor.execute('SELECT COUNT(*) FROM SENSOR')
    sensores = cursor.fetchone()[0]
    print(f'Sensores: {sensores}')
    
    cursor.execute('SELECT COUNT(*) FROM CULTURA')
    culturas = cursor.fetchone()[0]
    print(f'Culturas: {culturas}')
    
    conn.close()
    print('\n✓ Banco de dados configurado corretamente!')
    
except Exception as e:
    print(f'Erro: {e}') 