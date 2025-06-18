"""
Sistema de Cache Avançado para FarmTech Solutions
"""

import json
import time
import threading
import hashlib
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import pickle
import os

class CacheStrategy(Enum):
    """Estratégias de cache"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"   # Time To Live

class CacheManager:
    """Gerenciador de cache avançado com múltiplas estratégias"""
    
    def __init__(self, db_path: str = "cache.db", max_memory_mb: int = 100):
        self.db_path = db_path
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.lock = threading.RLock()
        
        # Cache em memória
        self.memory_cache = {}
        self.access_times = {}
        self.access_counts = {}
        self.sizes = {}
        
        # Configurações
        self.default_ttl = 3600  # 1 hora
        self.cleanup_interval = 300  # 5 minutos
        self.max_items = 10000
        
        # Inicializar banco de dados
        self.init_cache_database()
        
        # Thread de limpeza
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        
        # Estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
    
    def init_cache_database(self):
        """Inicializar banco de dados de cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela principal de cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                key_hash VARCHAR(64) PRIMARY KEY,
                key_data TEXT NOT NULL,
                value_data BLOB,
                size_bytes INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                ttl_seconds INTEGER,
                expires_at TIMESTAMP,
                category VARCHAR(50),
                tags TEXT
            )
        ''')
        
        # Tabela de tags
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de relacionamento tag-entry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entry_tags (
                key_hash VARCHAR(64) NOT NULL,
                tag_name VARCHAR(50) NOT NULL,
                PRIMARY KEY (key_hash, tag_name),
                FOREIGN KEY (key_hash) REFERENCES cache_entries (key_hash),
                FOREIGN KEY (tag_name) REFERENCES cache_tags (tag_name)
            )
        ''')
        
        # Tabela de estatísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_name VARCHAR(50) NOT NULL,
                stat_value INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_category ON cache_entries(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_accessed ON cache_entries(accessed_at)')
        
        conn.commit()
        conn.close()
    
    def _generate_key_hash(self, key: str) -> str:
        """Gerar hash da chave"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serializar valor para armazenamento"""
        return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserializar valor do armazenamento"""
        return pickle.loads(data)
    
    def _get_value_size(self, value: Any) -> int:
        """Calcular tamanho aproximado do valor em bytes"""
        try:
            return len(pickle.dumps(value))
        except:
            return 1024  # Tamanho padrão se não conseguir calcular
    
    def set(self, key: str, value: Any, ttl: int = None, 
            category: str = None, tags: List[str] = None, 
            strategy: CacheStrategy = CacheStrategy.LRU) -> bool:
        """Armazenar valor no cache"""
        try:
            with self.lock:
                key_hash = self._generate_key_hash(key)
                serialized_value = self._serialize_value(value)
                value_size = len(serialized_value)
                
                # Verificar se há espaço suficiente
                if not self._ensure_space(value_size, strategy):
                    return False
                
                # Calcular TTL
                ttl = ttl or self.default_ttl
                expires_at = datetime.now() + timedelta(seconds=ttl)
                
                # Armazenar em memória
                self.memory_cache[key_hash] = value
                self.access_times[key_hash] = time.time()
                self.access_counts[key_hash] = 0
                self.sizes[key_hash] = value_size
                
                # Armazenar no banco
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cache_entries (
                        key_hash, key_data, value_data, size_bytes, ttl_seconds,
                        expires_at, category, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key_hash, key, serialized_value, value_size, ttl,
                    expires_at.isoformat(), category, json.dumps(tags) if tags else None
                ))
                
                # Adicionar tags
                if tags:
                    for tag in tags:
                        cursor.execute('INSERT OR IGNORE INTO cache_tags (tag_name) VALUES (?)', (tag,))
                        cursor.execute('''
                            INSERT OR REPLACE INTO cache_entry_tags (key_hash, tag_name)
                            VALUES (?, ?)
                        ''', (key_hash, tag))
                
                conn.commit()
                conn.close()
                
                self.stats['sets'] += 1
                return True
                
        except Exception as e:
            print(f"Erro ao armazenar no cache: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        try:
            with self.lock:
                key_hash = self._generate_key_hash(key)
                
                # Verificar cache em memória primeiro
                if key_hash in self.memory_cache:
                    # Verificar se não expirou
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT expires_at FROM cache_entries WHERE key_hash = ?
                    ''', (key_hash,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result and datetime.fromisoformat(result[0]) > datetime.now():
                        # Atualizar estatísticas de acesso
                        self.access_times[key_hash] = time.time()
                        self.access_counts[key_hash] = self.access_counts.get(key_hash, 0) + 1
                        
                        # Atualizar no banco
                        self._update_access_stats(key_hash)
                        
                        self.stats['hits'] += 1
                        return self.memory_cache[key_hash]
                    else:
                        # Remover se expirou
                        self.delete(key)
                
                # Tentar carregar do banco
                value = self._load_from_database(key_hash)
                if value is not None:
                    # Adicionar ao cache em memória
                    self.memory_cache[key_hash] = value
                    self.access_times[key_hash] = time.time()
                    self.access_counts[key_hash] = 1
                    
                    self.stats['hits'] += 1
                    return value
                
                self.stats['misses'] += 1
                return None
                
        except Exception as e:
            print(f"Erro ao obter do cache: {e}")
            return None
    
    def _load_from_database(self, key_hash: str) -> Optional[Any]:
        """Carregar valor do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value_data, expires_at FROM cache_entries 
                WHERE key_hash = ? AND expires_at > ?
            ''', (key_hash, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                value_data, expires_at = result
                return self._deserialize_value(value_data)
            
            return None
            
        except Exception as e:
            print(f"Erro ao carregar do banco: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Remover valor do cache"""
        try:
            with self.lock:
                key_hash = self._generate_key_hash(key)
                
                # Remover da memória
                if key_hash in self.memory_cache:
                    del self.memory_cache[key_hash]
                    del self.access_times[key_hash]
                    del self.access_counts[key_hash]
                    del self.sizes[key_hash]
                
                # Remover do banco
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cache_entry_tags WHERE key_hash = ?', (key_hash,))
                cursor.execute('DELETE FROM cache_entries WHERE key_hash = ?', (key_hash,))
                
                conn.commit()
                conn.close()
                
                self.stats['deletes'] += 1
                return True
                
        except Exception as e:
            print(f"Erro ao remover do cache: {e}")
            return False
    
    def clear(self, category: str = None, tags: List[str] = None) -> int:
        """Limpar cache por categoria ou tags"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('SELECT key_hash FROM cache_entries WHERE category = ?', (category,))
                elif tags:
                    placeholders = ','.join(['?' for _ in tags])
                    cursor.execute(f'''
                        SELECT DISTINCT cet.key_hash 
                        FROM cache_entry_tags cet 
                        WHERE cet.tag_name IN ({placeholders})
                    ''', tags)
                else:
                    cursor.execute('SELECT key_hash FROM cache_entries')
                
                keys_to_delete = [row[0] for row in cursor.fetchall()]
                
                # Remover da memória
                for key_hash in keys_to_delete:
                    if key_hash in self.memory_cache:
                        del self.memory_cache[key_hash]
                        del self.access_times[key_hash]
                        del self.access_counts[key_hash]
                        del self.sizes[key_hash]
                
                # Remover do banco
                if category:
                    cursor.execute('DELETE FROM cache_entries WHERE category = ?', (category,))
                elif tags:
                    placeholders = ','.join(['?' for _ in tags])
                    cursor.execute(f'''
                        DELETE FROM cache_entries 
                        WHERE key_hash IN (
                            SELECT DISTINCT cet.key_hash 
                            FROM cache_entry_tags cet 
                            WHERE cet.tag_name IN ({placeholders})
                        )
                    ''', tags)
                    cursor.execute(f'''
                        DELETE FROM cache_entry_tags 
                        WHERE tag_name IN ({placeholders})
                    ''', tags)
                else:
                    cursor.execute('DELETE FROM cache_entries')
                    cursor.execute('DELETE FROM cache_entry_tags')
                
                conn.commit()
                conn.close()
                
                return len(keys_to_delete)
                
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Verificar se chave existe no cache"""
        return self.get(key) is not None
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Obter múltiplos valores"""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def set_many(self, data: Dict[str, Any], **kwargs) -> int:
        """Armazenar múltiplos valores"""
        success_count = 0
        for key, value in data.items():
            if self.set(key, value, **kwargs):
                success_count += 1
        return success_count
    
    def _ensure_space(self, required_size: int, strategy: CacheStrategy) -> bool:
        """Garantir espaço suficiente no cache"""
        current_size = sum(self.sizes.values())
        
        if current_size + required_size <= self.max_memory_bytes:
            return True
        
        # Evict items based on strategy
        items_to_evict = []
        
        if strategy == CacheStrategy.LRU:
            # Least Recently Used
            items_to_evict = sorted(
                self.access_times.items(),
                key=lambda x: x[1]
            )
        elif strategy == CacheStrategy.LFU:
            # Least Frequently Used
            items_to_evict = sorted(
                self.access_counts.items(),
                key=lambda x: x[1]
            )
        elif strategy == CacheStrategy.FIFO:
            # First In First Out (usando access_times como proxy)
            items_to_evict = sorted(
                self.access_times.items(),
                key=lambda x: x[1]
            )
        
        # Evict items until we have enough space
        freed_space = 0
        for key_hash, _ in items_to_evict:
            if key_hash in self.sizes:
                freed_space += self.sizes[key_hash]
                self._evict_item(key_hash)
                
                if current_size - freed_space + required_size <= self.max_memory_bytes:
                    break
        
        return current_size - freed_space + required_size <= self.max_memory_bytes
    
    def _evict_item(self, key_hash: str):
        """Evict item do cache"""
        try:
            # Remover da memória
            if key_hash in self.memory_cache:
                del self.memory_cache[key_hash]
                del self.access_times[key_hash]
                del self.access_counts[key_hash]
                del self.sizes[key_hash]
            
            # Remover do banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cache_entries WHERE key_hash = ?', (key_hash,))
            conn.commit()
            conn.close()
            
            self.stats['evictions'] += 1
            
        except Exception as e:
            print(f"Erro ao evict item: {e}")
    
    def _update_access_stats(self, key_hash: str):
        """Atualizar estatísticas de acesso no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cache_entries 
                SET accessed_at = ?, access_count = access_count + 1
                WHERE key_hash = ?
            ''', (datetime.now().isoformat(), key_hash))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def _cleanup_worker(self):
        """Worker para limpeza automática"""
        while True:
            try:
                with self.lock:
                    # Remover itens expirados
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT key_hash FROM cache_entries 
                        WHERE expires_at <= ?
                    ''', (datetime.now().isoformat(),))
                    
                    expired_keys = [row[0] for row in cursor.fetchall()]
                    
                    for key_hash in expired_keys:
                        self._evict_item(key_hash)
                    
                    conn.close()
                
                # Executar a cada cleanup_interval segundos
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                print(f"Erro no cleanup worker: {e}")
                time.sleep(60)  # Tentar novamente em 1 minuto
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        with self.lock:
            total_size = sum(self.sizes.values())
            hit_rate = 0
            if self.stats['hits'] + self.stats['misses'] > 0:
                hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
            
            return {
                'memory_usage_mb': total_size / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'items_in_memory': len(self.memory_cache),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'evictions': self.stats['evictions']
            }
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidar cache por tags"""
        return self.clear(tags=tags)

# Instância global do cache
cache_manager = CacheManager()

# Funções de conveniência
def cache_get(key: str) -> Optional[Any]:
    """Obter valor do cache"""
    return cache_manager.get(key)

def cache_set(key: str, value: Any, **kwargs) -> bool:
    """Armazenar valor no cache"""
    return cache_manager.set(key, value, **kwargs)

def cache_delete(key: str) -> bool:
    """Remover valor do cache"""
    return cache_manager.delete(key)

def cache_clear(**kwargs) -> int:
    """Limpar cache"""
    return cache_manager.clear(**kwargs)

def cache_exists(key: str) -> bool:
    """Verificar se chave existe"""
    return cache_manager.exists(key)

def cache_invalidate_by_tags(tags: List[str]) -> int:
    """Invalidar cache por tags"""
    return cache_manager.invalidate_by_tags(tags) 