"""
Sistema de Predição de Irrigação Inteligente usando Scikit-learn
FarmTech Solutions - ML Module
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_regression
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class IrrigationPredictor:
    """Sistema preditivo de irrigação usando Machine Learning"""
    
    def __init__(self, model_path: str = "models/irrigation_model.pkl"):
        self.model_path = model_path
        self.models = {}
        self.scalers = {}
        self.feature_encoders = {}
        self.feature_names = []
        self.model_metadata = {}
        
        # Configurações do modelo
        self.config = {
            'prediction_horizon': 24,  # Horas para frente
            'min_samples': 100,        # Mínimo de amostras para treinar
            'cv_folds': 5,             # Folds para validação cruzada
            'test_size': 0.2,          # Proporção de dados de teste
            'random_state': 42         # Seed para reprodutibilidade
        }
        
        # Carregar modelo se existir
        self.load_model()
    
    def prepare_features(self, sensor_data: List[Dict]) -> pd.DataFrame:
        """Preparar features para o modelo de ML"""
        try:
            # Converter para DataFrame
            df = pd.DataFrame(sensor_data)
            
            if df.empty:
                return pd.DataFrame()
            
            # Converter timestamp
            df['timestamp'] = pd.to_datetime(df['data_hora'])
            df = df.sort_values('timestamp')
            
            # Extrair features temporais
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            df['day_of_year'] = df['timestamp'].dt.dayofyear
            
            # Features cíclicas (seno e cosseno)
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
            
            # Agrupar por sensor e criar features de lag
            features_df = pd.DataFrame()
            
            for sensor_id in df['sensor_id'].unique():
                sensor_df = df[df['sensor_id'] == sensor_id].copy()
                sensor_df = sensor_df.sort_values('timestamp')
                
                # Features de lag (valores anteriores)
                for lag in [1, 2, 3, 6, 12, 24]:
                    sensor_df[f'valor_lag_{lag}'] = sensor_df['valor'].shift(lag)
                    sensor_df[f'timestamp_lag_{lag}'] = sensor_df['timestamp'].shift(lag)
                
                # Features de tendência
                sensor_df['valor_diff'] = sensor_df['valor'].diff()
                sensor_df['valor_diff_2'] = sensor_df['valor'].diff(2)
                
                # Médias móveis
                for window in [3, 6, 12, 24]:
                    sensor_df[f'valor_ma_{window}'] = sensor_df['valor'].rolling(window=window).mean()
                    sensor_df[f'valor_std_{window}'] = sensor_df['valor'].rolling(window=window).std()
                
                # Features de sazonalidade
                sensor_df['is_daytime'] = (sensor_df['hour'] >= 6) & (sensor_df['hour'] <= 18)
                sensor_df['is_weekend'] = sensor_df['day_of_week'].isin([5, 6])
                
                # Adicionar ao DataFrame principal
                features_df = pd.concat([features_df, sensor_df], ignore_index=True)
            
            # Remover linhas com valores NaN
            features_df = features_df.dropna()
            
            # Selecionar features para o modelo
            feature_columns = [
                'sensor_id', 'tipo_sensor', 'valor',
                'hour', 'day_of_week', 'month', 'day_of_year',
                'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
                'valor_diff', 'valor_diff_2',
                'is_daytime', 'is_weekend'
            ]
            
            # Adicionar features de lag
            for lag in [1, 2, 3, 6, 12, 24]:
                feature_columns.append(f'valor_lag_{lag}')
            
            # Adicionar médias móveis
            for window in [3, 6, 12, 24]:
                feature_columns.append(f'valor_ma_{window}')
                feature_columns.append(f'valor_std_{window}')
            
            # Filtrar colunas existentes
            available_columns = [col for col in feature_columns if col in features_df.columns]
            features_df = features_df[available_columns]
            
            return features_df
            
        except Exception as e:
            print(f"Erro ao preparar features: {e}")
            return pd.DataFrame()
    
    def create_target_variable(self, features_df: pd.DataFrame, 
                             target_horizon: int = 24) -> Tuple[pd.DataFrame, pd.Series]:
        """Criar variável alvo para predição de irrigação"""
        try:
            # Criar cópia para não modificar o original
            df = features_df.copy()
            
            # Para cada sensor, criar target baseado na necessidade de irrigação
            targets = []
            
            for sensor_id in df['sensor_id'].unique():
                sensor_df = df[df['sensor_id'] == sensor_id].copy()
                sensor_df = sensor_df.sort_values('timestamp')
                
                # Calcular necessidade de irrigação baseada no tipo de sensor
                if 'umidade' in sensor_df['tipo_sensor'].iloc[0].lower():
                    # Para umidade: irrigar se < 40% ou se tendência for decrescente
                    sensor_df['irrigation_need'] = np.where(
                        (sensor_df['valor'] < 40) | 
                        (sensor_df['valor_diff'] < -2),
                        1, 0
                    )
                elif 'ph' in sensor_df['tipo_sensor'].iloc[0].lower():
                    # Para pH: irrigar se fora do range ideal (5.5-7.5)
                    sensor_df['irrigation_need'] = np.where(
                        (sensor_df['valor'] < 5.5) | (sensor_df['valor'] > 7.5),
                        1, 0
                    )
                elif 'nutrientes' in sensor_df['tipo_sensor'].iloc[0].lower():
                    # Para nutrientes: irrigar se < 150 ppm
                    sensor_df['irrigation_need'] = np.where(
                        sensor_df['valor'] < 150,
                        1, 0
                    )
                else:
                    # Padrão: irrigar se valor estiver baixo
                    sensor_df['irrigation_need'] = np.where(
                        sensor_df['valor'] < sensor_df['valor'].quantile(0.3),
                        1, 0
                    )
                
                # Criar target para predição futura
                sensor_df['target_irrigation'] = sensor_df['irrigation_need'].shift(-target_horizon)
                
                targets.append(sensor_df)
            
            # Combinar todos os sensores
            combined_df = pd.concat(targets, ignore_index=True)
            
            # Remover linhas com target NaN
            combined_df = combined_df.dropna(subset=['target_irrigation'])
            
            # Separar features e target
            feature_cols = [col for col in combined_df.columns 
                          if col not in ['target_irrigation', 'irrigation_need', 'timestamp']]
            
            X = combined_df[feature_cols]
            y = combined_df['target_irrigation']
            
            return X, y
            
        except Exception as e:
            print(f"Erro ao criar target: {e}")
            return pd.DataFrame(), pd.Series()
    
    def train_model(self, sensor_data: List[Dict]) -> Dict[str, Any]:
        """Treinar modelo de predição de irrigação"""
        try:
            print("Iniciando treinamento do modelo de irrigação...")
            
            # Preparar features
            features_df = self.prepare_features(sensor_data)
            
            if features_df.empty or len(features_df) < self.config['min_samples']:
                return {
                    'success': False,
                    'error': f'Dados insuficientes. Necessário pelo menos {self.config["min_samples"]} amostras.'
                }
            
            # Criar target
            X, y = self.create_target_variable(features_df, self.config['prediction_horizon'])
            
            if X.empty or y.empty:
                return {
                    'success': False,
                    'error': 'Não foi possível criar variáveis de target.'
                }
            
            # Separar dados de treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config['test_size'], 
                random_state=self.config['random_state'], stratify=y
            )
            
            # Preparar dados categóricos
            categorical_features = ['sensor_id', 'tipo_sensor']
            numerical_features = [col for col in X.columns if col not in categorical_features]
            
            # Encoders para features categóricas
            for feature in categorical_features:
                if feature in X.columns:
                    le = LabelEncoder()
                    X_train[f'{feature}_encoded'] = le.fit_transform(X_train[feature].astype(str))
                    X_test[f'{feature}_encoded'] = le.transform(X_test[feature].astype(str))
                    self.feature_encoders[feature] = le
            
            # Remover features categóricas originais
            X_train = X_train.drop(columns=categorical_features, errors='ignore')
            X_test = X_test.drop(columns=categorical_features, errors='ignore')
            
            # Salvar nomes das features
            self.feature_names = X_train.columns.tolist()
            
            # Scaler para features numéricas
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            self.scalers['standard'] = scaler
            
            # Modelos para testar
            models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=100, 
                    max_depth=10, 
                    random_state=self.config['random_state']
                ),
                'gradient_boosting': GradientBoostingRegressor(
                    n_estimators=100, 
                    max_depth=6, 
                    random_state=self.config['random_state']
                ),
                'linear_regression': LinearRegression()
            }
            
            # Treinar e avaliar modelos
            best_model = None
            best_score = -np.inf
            results = {}
            
            for name, model in models.items():
                print(f"Treinando {name}...")
                
                # Treinar modelo
                model.fit(X_train_scaled, y_train)
                
                # Predições
                y_pred = model.predict(X_test_scaled)
                
                # Métricas
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Validação cruzada
                cv_scores = cross_val_score(
                    model, X_train_scaled, y_train, 
                    cv=self.config['cv_folds'], scoring='r2'
                )
                
                results[name] = {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std()
                }
                
                print(f"  {name}: R² = {r2:.4f}, CV = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
                
                # Selecionar melhor modelo
                if r2 > best_score:
                    best_score = r2
                    best_model = model
            
            # Salvar melhor modelo
            self.models['irrigation'] = best_model
            
            # Metadata do modelo
            self.model_metadata = {
                'best_model': list(models.keys())[list(models.values()).index(best_model)],
                'best_score': best_score,
                'feature_count': len(self.feature_names),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'training_date': datetime.now().isoformat(),
                'results': results
            }
            
            # Salvar modelo
            self.save_model()
            
            print(f"Modelo treinado com sucesso! Melhor R²: {best_score:.4f}")
            
            return {
                'success': True,
                'best_score': best_score,
                'results': results,
                'metadata': self.model_metadata
            }
            
        except Exception as e:
            print(f"Erro no treinamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict_irrigation(self, sensor_data: List[Dict], 
                         hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Predizer necessidade de irrigação"""
        try:
            if not self.models.get('irrigation'):
                return [{'error': 'Modelo não treinado'}]
            
            # Preparar features
            features_df = self.prepare_features(sensor_data)
            
            if features_df.empty:
                return [{'error': 'Dados insuficientes para predição'}]
            
            # Usar apenas os dados mais recentes
            latest_data = features_df.groupby('sensor_id').tail(1).reset_index(drop=True)
            
            # Preparar features para predição
            X_pred = self._prepare_prediction_features(latest_data)
            
            if X_pred.empty:
                return [{'error': 'Erro ao preparar features para predição'}]
            
            # Fazer predição
            model = self.models['irrigation']
            scaler = self.scalers['standard']
            
            X_pred_scaled = scaler.transform(X_pred)
            predictions = model.predict(X_pred_scaled)
            
            # Gerar recomendações
            recommendations = []
            
            for i, (_, row) in enumerate(latest_data.iterrows()):
                prediction = predictions[i]
                sensor_id = row['sensor_id']
                sensor_type = row['tipo_sensor']
                current_value = row['valor']
                
                # Interpretar predição
                if prediction > 0.7:
                    action = "IRRIGAR IMEDIATAMENTE"
                    priority = "ALTA"
                    reason = "Alta probabilidade de necessidade de irrigação"
                elif prediction > 0.5:
                    action = "IRRIGAR EM BREVE"
                    priority = "MÉDIA"
                    reason = "Probabilidade moderada de necessidade de irrigação"
                elif prediction > 0.3:
                    action = "MONITORAR"
                    priority = "BAIXA"
                    reason = "Baixa probabilidade, mas monitorar"
                else:
                    action = "NÃO IRRIGAR"
                    priority = "NENHUMA"
                    reason = "Baixa probabilidade de necessidade de irrigação"
                
                # Calcular horário recomendado
                recommended_time = datetime.now() + timedelta(hours=hours_ahead)
                
                # Criar recomendação
                recommendation = {
                    'sensor_id': int(sensor_id),
                    'sensor_type': sensor_type,
                    'current_value': float(current_value),
                    'prediction_probability': float(prediction),
                    'recommended_action': action,
                    'priority': priority,
                    'reason': reason,
                    'recommended_time': recommended_time.isoformat(),
                    'hours_ahead': hours_ahead,
                    'confidence': self._calculate_confidence(prediction, current_value, sensor_type)
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            print(f"Erro na predição: {e}")
            return [{'error': str(e)}]
    
    def _prepare_prediction_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preparar features para predição"""
        try:
            # Usar as mesmas features do treinamento
            feature_cols = [col for col in data.columns if col in self.feature_names]
            X_pred = data[feature_cols].copy()
            
            # Aplicar encoders se necessário
            for feature, encoder in self.feature_encoders.items():
                encoded_col = f'{feature}_encoded'
                if encoded_col in self.feature_names and feature in data.columns:
                    X_pred[encoded_col] = encoder.transform(data[feature].astype(str))
            
            # Garantir que todas as features estejam presentes
            for feature in self.feature_names:
                if feature not in X_pred.columns:
                    X_pred[feature] = 0  # Valor padrão
            
            # Ordenar colunas
            X_pred = X_pred[self.feature_names]
            
            return X_pred
            
        except Exception as e:
            print(f"Erro ao preparar features de predição: {e}")
            return pd.DataFrame()
    
    def _calculate_confidence(self, prediction: float, current_value: float, 
                            sensor_type: str) -> float:
        """Calcular nível de confiança da predição"""
        try:
            # Base de confiança na predição
            base_confidence = prediction
            
            # Ajustar baseado no valor atual
            if 'umidade' in sensor_type.lower():
                if current_value < 30 or current_value > 80:
                    base_confidence *= 1.2  # Aumentar confiança para valores extremos
                elif 40 <= current_value <= 60:
                    base_confidence *= 0.8  # Diminuir confiança para valores normais
            elif 'ph' in sensor_type.lower():
                if current_value < 5.0 or current_value > 8.0:
                    base_confidence *= 1.3
                elif 5.5 <= current_value <= 7.5:
                    base_confidence *= 0.7
            elif 'nutrientes' in sensor_type.lower():
                if current_value < 100:
                    base_confidence *= 1.1
                elif current_value > 200:
                    base_confidence *= 0.9
            
            # Limitar entre 0 e 1
            confidence = max(0.0, min(1.0, base_confidence))
            
            return confidence
            
        except Exception as e:
            return 0.5  # Confiança padrão em caso de erro
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obter informações do modelo"""
        return {
            'is_trained': bool(self.models.get('irrigation')),
            'metadata': self.model_metadata,
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'config': self.config
        }
    
    def save_model(self):
        """Salvar modelo treinado"""
        try:
            import os
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'feature_encoders': self.feature_encoders,
                'feature_names': self.feature_names,
                'model_metadata': self.model_metadata,
                'config': self.config
            }
            
            joblib.dump(model_data, self.model_path)
            print(f"Modelo salvo em: {self.model_path}")
            
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
    
    def load_model(self):
        """Carregar modelo treinado"""
        try:
            import os
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                
                self.models = model_data.get('models', {})
                self.scalers = model_data.get('scalers', {})
                self.feature_encoders = model_data.get('feature_encoders', {})
                self.feature_names = model_data.get('feature_names', [])
                self.model_metadata = model_data.get('model_metadata', {})
                self.config.update(model_data.get('config', {}))
                
                print(f"Modelo carregado de: {self.model_path}")
                
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")

# Função de conveniência para criar instância
def create_irrigation_predictor() -> IrrigationPredictor:
    """Criar instância do preditor de irrigação"""
    return IrrigationPredictor() 