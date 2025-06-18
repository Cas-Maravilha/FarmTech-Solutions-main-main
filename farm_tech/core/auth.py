"""
Sistema de Autenticação e Autorização para FarmTech Solutions
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Optional, Dict, Any
import sqlite3
import os

class AuthManager:
    """Gerenciador de autenticação e autorização"""
    
    def __init__(self, db_path: str = "farmtech.db"):
        self.db_path = db_path
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'farmtech-secret-key-2024')
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)
        self.init_auth_tables()
    
    def init_auth_tables(self):
        """Inicializar tabelas de autenticação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Tabela de sessões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tabela de permissões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de permissões de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                user_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by INTEGER,
                PRIMARY KEY (user_id, permission_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (permission_id) REFERENCES permissions (permission_id),
                FOREIGN KEY (granted_by) REFERENCES users (user_id)
            )
        ''')
        
        # Inserir permissões padrão
        default_permissions = [
            ('view_dashboard', 'Visualizar dashboard'),
            ('view_sensors', 'Visualizar sensores'),
            ('manage_sensors', 'Gerenciar sensores'),
            ('view_areas', 'Visualizar áreas'),
            ('manage_areas', 'Gerenciar áreas'),
            ('view_alerts', 'Visualizar alertas'),
            ('manage_alerts', 'Gerenciar alertas'),
            ('view_reports', 'Visualizar relatórios'),
            ('manage_users', 'Gerenciar usuários'),
            ('system_admin', 'Administrador do sistema')
        ]
        
        for perm_name, perm_desc in default_permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO permissions (name, description)
                VALUES (?, ?)
            ''', (perm_name, perm_desc))
        
        # Criar usuário admin padrão se não existir
        admin_password = self.hash_password('admin123')
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@farmtech.com', admin_password, 'Administrador', 'admin'))
        
        # Conceder todas as permissões ao admin
        admin_user_id = cursor.execute('SELECT user_id FROM users WHERE username = ?', ('admin',)).fetchone()[0]
        
        for perm_name, _ in default_permissions:
            perm_id = cursor.execute('SELECT permission_id FROM permissions WHERE name = ?', (perm_name,)).fetchone()[0]
            cursor.execute('''
                INSERT OR IGNORE INTO user_permissions (user_id, permission_id, granted_by)
                VALUES (?, ?, ?)
            ''', (admin_user_id, perm_id, admin_user_id))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash de senha usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar senha"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str, full_name: str, role: str = 'user') -> Dict[str, Any]:
        """Criar novo usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se usuário já existe
            cursor.execute('SELECT user_id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                return {'success': False, 'error': 'Usuário ou email já existe'}
            
            # Hash da senha
            password_hash = self.hash_password(password)
            
            # Inserir usuário
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, role))
            
            user_id = cursor.lastrowid
            
            # Conceder permissões básicas
            basic_permissions = ['view_dashboard', 'view_sensors', 'view_areas', 'view_alerts']
            for perm_name in basic_permissions:
                perm_id = cursor.execute('SELECT permission_id FROM permissions WHERE name = ?', (perm_name,)).fetchone()[0]
                cursor.execute('''
                    INSERT INTO user_permissions (user_id, permission_id, granted_by)
                    VALUES (?, ?, ?)
                ''', (user_id, perm_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute('''
                SELECT user_id, username, email, password_hash, full_name, role, 
                       is_active, failed_attempts, locked_until
                FROM users WHERE username = ? OR email = ?
            ''', (username, username))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            user_id, username, email, password_hash, full_name, role, is_active, failed_attempts, locked_until = user_data
            
            # Verificar se conta está ativa
            if not is_active:
                return None
            
            # Verificar se conta está bloqueada
            if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                return None
            
            # Verificar senha
            if not self.verify_password(password, password_hash):
                # Incrementar tentativas falhadas
                cursor.execute('''
                    UPDATE users SET failed_attempts = failed_attempts + 1
                    WHERE user_id = ?
                ''', (user_id,))
                
                # Bloquear conta após 5 tentativas
                if failed_attempts >= 4:
                    lock_until = datetime.now() + timedelta(minutes=30)
                    cursor.execute('''
                        UPDATE users SET locked_until = ? WHERE user_id = ?
                    ''', (lock_until.isoformat(), user_id))
                
                conn.commit()
                conn.close()
                return None
            
            # Reset de tentativas falhadas
            cursor.execute('''
                UPDATE users SET failed_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'role': role
            }
            
        except Exception as e:
            return None
    
    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Criar token JWT"""
        payload = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_permissions(self, user_id: int) -> list:
        """Obter permissões do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.name FROM permissions p
                JOIN user_permissions up ON p.permission_id = up.permission_id
                WHERE up.user_id = ?
            ''', (user_id,))
            
            permissions = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return permissions
            
        except Exception:
            return []
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """Verificar se usuário tem permissão específica"""
        permissions = self.get_user_permissions(user_id)
        return permission in permissions or 'system_admin' in permissions
    
    def require_auth(self, f):
        """Decorator para requerer autenticação"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Obter token do header Authorization
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            
            # Obter token do cookie
            if not token:
                token = request.cookies.get('auth_token')
            
            if not token:
                return jsonify({'error': 'Token de autenticação necessário'}), 401
            
            # Verificar token
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Token inválido ou expirado'}), 401
            
            # Adicionar dados do usuário ao request
            request.user = payload
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_permission(self, permission: str):
        """Decorator para requerer permissão específica"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'user'):
                    return jsonify({'error': 'Autenticação necessária'}), 401
                
                if not self.has_permission(request.user['user_id'], permission):
                    return jsonify({'error': 'Permissão negada'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_role(self, role: str):
        """Decorator para requerer role específica"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'user'):
                    return jsonify({'error': 'Autenticação necessária'}), 401
                
                if request.user['role'] != role and request.user['role'] != 'admin':
                    return jsonify({'error': 'Role insuficiente'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Instância global do AuthManager
auth_manager = AuthManager()

# Funções de conveniência
def login_required(f):
    """Decorator para requerer login"""
    return auth_manager.require_auth(f)

def permission_required(permission: str):
    """Decorator para requerer permissão"""
    return auth_manager.require_permission(permission)

def role_required(role: str):
    """Decorator para requerer role"""
    return auth_manager.require_role(role) 