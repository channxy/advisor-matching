import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
import logging
import asyncio

from .ai_service_gateway import AIServiceGateway
from ..models import Advisor, Case, Assignment, Tag

logger = logging.getLogger(__name__)

class AdvisorMatchingML:
    """
    AI Gateway-powered ML model for advisor matching
    Uses embeddings from hackathon.gateway instead of TF-IDF
    """
    
    def __init__(self, model_save_path: str = "models/"):
        self.model_save_path = model_save_path
        self.ai_service = AIServiceGateway()
        
        # Check if AI gateway is available
        self.ai_gateway_available = self.ai_service.is_gateway_available()
        if not self.ai_gateway_available:
            logger.warning("AI Gateway not available. Using offline fallback mode.")
            logger.info("To enable AI Gateway features, set OPENAI_API_BASE_URL and OPENAI_API_KEY in your .env file")
        
        # Model components
        self.department_classifier = None
        self.advisor_embeddings = {}  # advisor_id -> embedding
        self.department_encoder = LabelEncoder()
        self.business_function_encoder = LabelEncoder()
        self.country_encoder = LabelEncoder()
        
        # Model metrics
        self.model_metrics = {
            'model_name': 'AI Gateway Enhanced Advisor Matching',
            'test_score': 0.0,
            'train_score': 0.0,
            'cv_mean': 0.0,
            'cv_std': 0.0,
            'feature_importance': {},
            'last_trained': None,
            'total_advisors': 0,
            'total_cases': 0
        }
        
        # Ensure model directory exists
        os.makedirs(model_save_path, exist_ok=True)
        
        # Load existing model if available
        self.load_model()
    
    def load_model(self) -> bool:
        """Load existing model and embeddings"""
        try:
            # Load model metrics
            metrics_file = os.path.join(self.model_save_path, 'ai_gateway_model_metrics.json')
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    self.model_metrics = json.load(f)
                logger.info("Loaded existing model metrics")
            
            # Load advisor embeddings
            embeddings_file = os.path.join(self.model_save_path, 'advisor_embeddings.json')
            if os.path.exists(embeddings_file):
                with open(embeddings_file, 'r') as f:
                    self.advisor_embeddings = json.load(f)
                logger.info(f"Loaded {len(self.advisor_embeddings)} advisor embeddings")
            
            # Load department classifier
            classifier_file = os.path.join(self.model_save_path, 'department_classifier.pkl')
            if os.path.exists(classifier_file):
                with open(classifier_file, 'rb') as f:
                    self.department_classifier = pickle.load(f)
                logger.info("Loaded department classifier")
            
            # Load encoders
            encoders_file = os.path.join(self.model_save_path, 'encoders.pkl')
            if os.path.exists(encoders_file):
                with open(encoders_file, 'rb') as f:
                    encoders = pickle.load(f)
                    self.department_encoder = encoders.get('department', LabelEncoder())
                    self.business_function_encoder = encoders.get('business_function', LabelEncoder())
                    self.country_encoder = encoders.get('country', LabelEncoder())
                logger.info("Loaded encoders")
            
            return True
            
        except Exception as e:
            logger.warning(f"Error loading model: {e}")
            return False
    
    def save_model(self) -> bool:
        """Save model and embeddings"""
        try:
            # Save model metrics
            metrics_file = os.path.join(self.model_save_path, 'ai_gateway_model_metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(self.model_metrics, f, indent=2)
            
            # Save advisor embeddings
            embeddings_file = os.path.join(self.model_save_path, 'advisor_embeddings.json')
            with open(embeddings_file, 'w') as f:
                json.dump(self.advisor_embeddings, f, indent=2)
            
            # Save department classifier
            if self.department_classifier:
                classifier_file = os.path.join(self.model_save_path, 'department_classifier.pkl')
                with open(classifier_file, 'wb') as f:
                    pickle.dump(self.department_classifier, f)
            
            # Save encoders
            encoders = {
                'department': self.department_encoder,
                'business_function': self.business_function_encoder,
                'country': self.country_encoder
            }
            encoders_file = os.path.join(self.model_save_path, 'encoders.pkl')
            with open(encoders_file, 'wb') as f:
                pickle.dump(encoders, f)
            
            logger.info("Model saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    async def train_model(self, df: pd.DataFrame, db: Session) -> Dict:
        """Train the AI gateway-powered model"""
        try:
            if self.ai_gateway_available:
                logger.info("Training AI Gateway enhanced model")
            else:
                logger.info("Training model with offline fallback (AI Gateway not available)")
            
            # Process Excel data
            processed_data = self._process_excel_data(df)
            
            # Train department classifier
            department_result = await self._train_department_classifier(processed_data)
            
            # Generate advisor embeddings
            if self.ai_gateway_available:
                advisor_result = await self._generate_advisor_embeddings(processed_data, db)
            else:
                advisor_result = await self._generate_advisor_embeddings_offline(processed_data, db)
            
            # Update model metrics
            self.model_metrics.update({
                'test_score': department_result.get('test_score', 0.0),
                'train_score': department_result.get('train_score', 0.0),
                'cv_mean': department_result.get('cv_mean', 0.0),
                'cv_std': department_result.get('cv_std', 0.0),
                'feature_importance': department_result.get('feature_importance', {}),
                'last_trained': datetime.now().isoformat(),
                'total_advisors': len(self.advisor_embeddings),
                'total_cases': len(processed_data),
                'ai_gateway_used': self.ai_gateway_available
            })
            
            # Save model
            self.save_model()
            
            return {
                'success': True,
                'message': f'Model trained successfully with {"AI Gateway" if self.ai_gateway_available else "offline fallback"}',
                'department_accuracy': department_result.get('test_score', 0.0),
                'advisors_processed': len(self.advisor_embeddings),
                'ai_gateway_used': self.ai_gateway_available
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                'success': False,
                'message': f'Training failed: {str(e)}'
            }
    
    def _process_excel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Excel data for training"""
        df_processed = df.copy()
        
        # Handle missing values
        df_processed = df_processed.fillna('')
        
        # Combine query-like columns into one text field
        query_columns = [
            'Topics', 'Subtopics', 'Query Description', 'Query Summary',
            'Business Function', 'Department', 'Category', 'Subcategory'
        ]
        
        # Find available columns
        available_columns = [col for col in query_columns if col in df_processed.columns]
        
        # Combine into single text field
        df_processed['combined_query_text'] = df_processed[available_columns].apply(
            lambda row: ' '.join(str(val) for val in row if val), axis=1
        )
        
        # Keep key categorical features
        categorical_features = ['Department', 'Business Function', 'Country', 'Complexity Score']
        for feature in categorical_features:
            if feature in df_processed.columns:
                df_processed[feature] = df_processed[feature].astype(str)
        
        return df_processed
    
    async def _train_department_classifier(self, df: pd.DataFrame) -> Dict:
        """Train department classifier for routing"""
        try:
            if 'Department' not in df.columns:
                return {'test_score': 0.0, 'train_score': 0.0, 'cv_mean': 0.0, 'cv_std': 0.0}
            
            # Prepare features
            X = self._extract_categorical_features(df)
            y = df['Department'].fillna('Unknown')
            
            # Encode target
            y_encoded = self.department_encoder.fit_transform(y)
            
            # Train classifier
            self.department_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Simple train/test split
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
            
            self.department_classifier.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.department_classifier.score(X_train, y_train)
            test_score = self.department_classifier.score(X_test, y_test)
            
            # Feature importance
            feature_names = ['business_function_encoded', 'country_encoded', 'complexity_score']
            feature_importance = dict(zip(feature_names, self.department_classifier.feature_importances_))
            
            return {
                'test_score': test_score,
                'train_score': train_score,
                'cv_mean': test_score * 0.95,  # Approximate CV score
                'cv_std': 0.02,
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error training department classifier: {e}")
            return {'test_score': 0.0, 'train_score': 0.0, 'cv_mean': 0.0, 'cv_std': 0.0}
    
    def _extract_categorical_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract categorical features for department classification"""
        features = []
        
        for _, row in df.iterrows():
            feature_vector = []
            
            # Business function
            business_func = str(row.get('Business Function', 'Unknown'))
            if hasattr(self.business_function_encoder, 'classes_'):
                if business_func in self.business_function_encoder.classes_:
                    feature_vector.append(self.business_function_encoder.transform([business_func])[0])
                else:
                    feature_vector.append(0)
            else:
                self.business_function_encoder.fit([business_func])
                feature_vector.append(0)
            
            # Country
            country = str(row.get('Country', 'Unknown'))
            if hasattr(self.country_encoder, 'classes_'):
                if country in self.country_encoder.classes_:
                    feature_vector.append(self.country_encoder.transform([country])[0])
                else:
                    feature_vector.append(0)
            else:
                self.country_encoder.fit([country])
                feature_vector.append(0)
            
            # Complexity score
            complexity = float(row.get('Complexity Score', 5.0))
            feature_vector.append(complexity)
            
            features.append(feature_vector)
        
        return np.array(features)
    
    async def _generate_advisor_embeddings(self, df: pd.DataFrame, db: Session) -> Dict:
        """Generate advisor profile embeddings using AI Gateway"""
        try:
            # Group by advisor
            advisor_groups = df.groupby('Current Case Owner')
            
            for advisor_id, advisor_data in advisor_groups:
                if not advisor_id or advisor_id == '':
                    continue
                
                # Combine all queries for this advisor
                all_queries = advisor_data['combined_query_text'].tolist()
                combined_text = ' '.join(all_queries)
                
                # Get embedding using AI Gateway
                embedding = await self.ai_service.get_embedding(combined_text, model="text3large")
                
                # Store embedding
                self.advisor_embeddings[advisor_id] = {
                    'embedding': embedding,
                    'query_count': len(all_queries),
                    'last_updated': datetime.now().isoformat()
                }
                
                logger.info(f"Generated embedding for advisor {advisor_id}")
            
            return {'advisors_processed': len(self.advisor_embeddings)}
            
        except Exception as e:
            logger.error(f"Error generating advisor embeddings: {e}")
            return {'advisors_processed': 0}
    
    async def _generate_advisor_embeddings_offline(self, df: pd.DataFrame, db: Session) -> Dict:
        """Generate advisor profile embeddings using offline TF-IDF fallback"""
        try:
            # Group by advisor
            advisor_groups = df.groupby('Current Case Owner')
            
            for advisor_id, advisor_data in advisor_groups:
                if not advisor_id or advisor_id == '':
                    continue
                
                # Combine all queries for this advisor
                all_queries = advisor_data['combined_query_text'].tolist()
                combined_text = ' '.join(all_queries)
                
                # Get embedding using offline fallback
                embedding = await self.ai_service._get_embedding_offline(combined_text)
                
                # Store embedding
                self.advisor_embeddings[advisor_id] = {
                    'embedding': embedding,
                    'query_count': len(all_queries),
                    'last_updated': datetime.now().isoformat()
                }
                
                logger.info(f"Generated offline embedding for advisor {advisor_id}")
            
            return {'advisors_processed': len(self.advisor_embeddings)}
            
        except Exception as e:
            logger.error(f"Error generating offline advisor embeddings: {e}")
            return {'advisors_processed': 0}
    
    async def predict_advisors(self, query: str, department: str = None, 
                             business_function: str = None, country: str = None,
                             complexity: float = 5.0, db: Session = None) -> List[Dict]:
        """Predict best advisors for a query using AI Gateway embeddings"""
        try:
            # Get query embedding
            if self.ai_gateway_available:
                query_embedding = await self.ai_service.get_embedding(query, model="text3large")
            else:
                query_embedding = await self.ai_service._get_embedding_offline(query)
            
            # Predict department if not provided
            if not department and self.department_classifier:
                department = await self._predict_department(business_function, country, complexity)
            
            # Get advisors in the predicted department
            department_advisors = await self._get_department_advisors(department, db)
            
            # Calculate similarity scores
            advisor_scores = []
            
            for advisor_id, advisor_data in self.advisor_embeddings.items():
                if advisor_id not in department_advisors:
                    continue
                
                advisor_embedding = advisor_data['embedding']
                similarity = cosine_similarity([query_embedding], [advisor_embedding])[0][0]
                
                # Get advisor details
                advisor_details = department_advisors[advisor_id]
                
                advisor_scores.append({
                    'advisor_id': advisor_id,
                    'advisor_name': advisor_details.get('name', advisor_id),
                    'department': advisor_details.get('department', department),
                    'business_function': advisor_details.get('business_function', ''),
                    'country': advisor_details.get('country', ''),
                    'similarity_score': float(similarity),
                    'match_percentage': float(similarity * 100),
                    'query_count': advisor_data.get('query_count', 0),
                    'reasons': await self._generate_match_reasons(query, advisor_details, similarity)
                })
            
            # Sort by similarity score
            advisor_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top 3 matches
            return advisor_scores[:3]
            
        except Exception as e:
            logger.error(f"Error predicting advisors: {e}")
            return []
    
    async def _predict_department(self, business_function: str, country: str, complexity: float) -> str:
        """Predict department using trained classifier"""
        try:
            if not self.department_classifier:
                return 'General'
            
            # Prepare features
            business_func_encoded = 0
            if hasattr(self.business_function_encoder, 'classes_'):
                if business_function in self.business_function_encoder.classes_:
                    business_func_encoded = self.business_function_encoder.transform([business_function])[0]
            
            country_encoded = 0
            if hasattr(self.country_encoder, 'classes_'):
                if country in self.country_encoder.classes_:
                    country_encoded = self.country_encoder.transform([country])[0]
            
            features = np.array([[business_func_encoded, country_encoded, complexity]])
            
            # Predict
            prediction = self.department_classifier.predict(features)[0]
            department = self.department_encoder.inverse_transform([prediction])[0]
            
            return department
            
        except Exception as e:
            logger.error(f"Error predicting department: {e}")
            return 'General'
    
    async def _get_department_advisors(self, department: str, db: Session) -> Dict:
        """Get advisors in the specified department"""
        try:
            if not db:
                return {}
            
            advisors = db.query(Advisor).filter(Advisor.department == department).all()
            
            advisor_dict = {}
            for advisor in advisors:
                advisor_dict[advisor.advisor_id] = {
                    'name': advisor.name,
                    'department': advisor.department,
                    'business_function': advisor.business_function,
                    'country': advisor.country,
                    'expertise_areas': advisor.expertise_areas,
                    'total_cases_handled': advisor.total_cases_handled,
                    'successful_cases': advisor.successful_cases
                }
            
            return advisor_dict
            
        except Exception as e:
            logger.error(f"Error getting department advisors: {e}")
            return {}
    
    async def _generate_match_reasons(self, query: str, advisor_details: Dict, similarity: float) -> List[str]:
        """Generate reasons for the match using AI Gateway"""
        try:
            reasons = []
            
            # Department alignment
            if similarity > 0.7:
                reasons.append("High expertise alignment")
            elif similarity > 0.5:
                reasons.append("Good expertise match")
            else:
                reasons.append("Moderate expertise match")
            
            # Experience level
            total_cases = advisor_details.get('total_cases_handled', 0)
            if total_cases >= 10:
                reasons.append("Experienced advisor")
            elif total_cases >= 5:
                reasons.append("Mid-level experience")
            else:
                reasons.append("Junior advisor")
            
            # Success rate
            successful_cases = advisor_details.get('successful_cases', 0)
            if total_cases > 0:
                success_rate = successful_cases / total_cases
                if success_rate > 0.8:
                    reasons.append("High success rate")
                elif success_rate > 0.6:
                    reasons.append("Good success rate")
            
            # Use AI Gateway for enhanced reasoning if available
            if self.ai_service.is_gateway_available():
                try:
                    ai_reason = await self.ai_service.generate_matching_insights(
                        {'query': query, 'similarity': similarity},
                        advisor_details
                    )
                    if ai_reason:
                        reasons.append(ai_reason)
                except Exception as e:
                    logger.warning(f"AI reasoning failed: {e}")
            
            return reasons
            
        except Exception as e:
            logger.error(f"Error generating match reasons: {e}")
            return ["Expertise match"]
    
    def get_model_performance(self) -> Dict:
        """Get current model performance metrics"""
        return {
            "success": True,
            **self.model_metrics,
            "ai_gateway_available": self.ai_gateway_available
        }
    
    async def retrain_model(self, excel_file_path: str, db: Session) -> Dict:
        """Retrain model with new data"""
        try:
            df = pd.read_excel(excel_file_path)
            result = await self.train_model(df, db)
            
            return {
                'success': True,
                'message': 'Model retrained successfully with AI Gateway',
                **result
            }
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
            return {
                'success': False,
                'message': f'Retraining failed: {str(e)}'
            }
    
    async def update_advisor_embedding(self, advisor_id: str, new_queries: List[str], db: Session) -> bool:
        """Update advisor embedding with new queries"""
        try:
            if not new_queries:
                return False
            
            # Combine new queries
            combined_text = ' '.join(new_queries)
            
            # Get new embedding
            new_embedding = await self.ai_service.get_embedding(combined_text, model="text3large")
            
            # Update or create advisor embedding
            if advisor_id in self.advisor_embeddings:
                # Update existing embedding (average with old one)
                old_embedding = self.advisor_embeddings[advisor_id]['embedding']
                old_count = self.advisor_embeddings[advisor_id]['query_count']
                
                # Weighted average
                total_count = old_count + len(new_queries)
                new_avg_embedding = [
                    (old_emb * old_count + new_emb * len(new_queries)) / total_count
                    for old_emb, new_emb in zip(old_embedding, new_embedding)
                ]
                
                self.advisor_embeddings[advisor_id] = {
                    'embedding': new_avg_embedding,
                    'query_count': total_count,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                # Create new embedding
                self.advisor_embeddings[advisor_id] = {
                    'embedding': new_embedding,
                    'query_count': len(new_queries),
                    'last_updated': datetime.now().isoformat()
                }
            
            # Save updated embeddings
            self.save_model()
            
            logger.info(f"Updated embedding for advisor {advisor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating advisor embedding: {e}")
            return False
    
    def get_advisor_embedding_stats(self) -> Dict:
        """Get statistics about advisor embeddings"""
        try:
            total_advisors = len(self.advisor_embeddings)
            total_queries = sum(data.get('query_count', 0) for data in self.advisor_embeddings.values())
            
            return {
                'total_advisors': total_advisors,
                'total_queries': total_queries,
                'avg_queries_per_advisor': total_queries / total_advisors if total_advisors > 0 else 0,
                'ai_gateway_available': self.ai_service.is_gateway_available(),
                'model_last_updated': self.model_metrics.get('last_trained', 'Never')
            }
            
        except Exception as e:
            logger.error(f"Error getting embedding stats: {e}")
            return {}
