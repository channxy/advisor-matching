import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
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
    Handles dynamic Excel columns and properly updates database
    """
    
    def __init__(self, model_save_path: str = "models/"):
        self.model_save_path = model_save_path
        self.ai_service = AIServiceGateway()
        
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
    
    def _detect_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """Dynamically detect column mappings for different Excel formats"""
        column_mapping = {
            'advisor_id': None,
            'case_id': None,
            'topic': None,
            'subtopic': None,
            'query_title': None,
            'query_description': None,
            'business_function': None,
            'department': None,
            'country': None,
            'complexity': None,
            'status': None,
            'date_created': None,
            'date_submitted': None,
            'date_completion': None,
            'all_text_columns': []
        }
        
        # Detect advisor ID column
        advisor_candidates = ['current case owner', 'advisor', 'assigned to', 'owner', 'case owner']
        for col in df.columns:
            col_lower = col.lower()
            if any(candidate in col_lower for candidate in advisor_candidates):
                column_mapping['advisor_id'] = col
                break
        
        # Detect case ID column
        case_candidates = ['case id', 'case_id', 'id', 'ticket', 'reference']
        for col in df.columns:
            col_lower = col.lower()
            if any(candidate in col_lower for candidate in case_candidates):
                column_mapping['case_id'] = col
                break
        
        # Detect topic/subtopic columns
        topic_candidates = ['topic', 'category', 'type', 'area']
        subtopic_candidates = ['subtopic', 'sub-topic', 'sub category', 'subcategory']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(candidate in col_lower for candidate in topic_candidates):
                column_mapping['topic'] = col
            elif any(candidate in col_lower for candidate in subtopic_candidates):
                column_mapping['subtopic'] = col
        
        # Detect query columns
        query_candidates = ['query', 'title', 'description', 'summary', 'question']
        for col in df.columns:
            col_lower = col.lower()
            if any(candidate in col_lower for candidate in query_candidates):
                if 'title' in col_lower:
                    column_mapping['query_title'] = col
                elif 'description' in col_lower or 'query' in col_lower:
                    column_mapping['query_description'] = col
                else:
                    column_mapping['all_text_columns'].append(col)
        
        # Detect business function and department
        for col in df.columns:
            col_lower = col.lower()
            if 'business function' in col_lower:
                column_mapping['business_function'] = col
            elif 'department' in col_lower:
                column_mapping['department'] = col
            elif 'country' in col_lower:
                column_mapping['country'] = col
            elif 'complexity' in col_lower:
                column_mapping['complexity'] = col
            elif 'status' in col_lower:
                column_mapping['status'] = col
        
        # Detect date columns
        for col in df.columns:
            col_lower = col.lower()
            if 'date' in col_lower:
                if 'created' in col_lower or 'opened' in col_lower:
                    column_mapping['date_created'] = col
                elif 'submitted' in col_lower:
                    column_mapping['date_submitted'] = col
                elif 'completion' in col_lower or 'closed' in col_lower:
                    column_mapping['date_completion'] = col
        
        # Add all text-like columns for comprehensive profile building
        for col in df.columns:
            col_lower = col.lower()
            if col not in column_mapping.values() and col not in column_mapping['all_text_columns']:
                # Check if column contains text data
                if df[col].dtype == 'object' and df[col].notna().sum() > 0:
                    sample_values = df[col].dropna().head(5).astype(str)
                    if any(len(val) > 10 for val in sample_values):  # Likely text data
                        column_mapping['all_text_columns'].append(col)
        
        logger.info(f"Detected column mapping: {column_mapping}")
        return column_mapping
    
    def _process_excel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Excel data with dynamic column detection"""
        df_processed = df.copy()
        
        # Handle missing values
        df_processed = df_processed.fillna('')
        
        # Detect column mapping
        column_mapping = self._detect_column_mapping(df_processed)
        
        # Create combined text field from all relevant columns
        text_columns = []
        
        # Add detected query columns
        if column_mapping['query_title']:
            text_columns.append(column_mapping['query_title'])
        if column_mapping['query_description']:
            text_columns.append(column_mapping['query_description'])
        
        # Add topic/subtopic
        if column_mapping['topic']:
            text_columns.append(column_mapping['topic'])
        if column_mapping['subtopic']:
            text_columns.append(column_mapping['subtopic'])
        
        # Add business function and department
        if column_mapping['business_function']:
            text_columns.append(column_mapping['business_function'])
        if column_mapping['department']:
            text_columns.append(column_mapping['department'])
        
        # Add all other text columns
        text_columns.extend(column_mapping['all_text_columns'])
        
        # Combine into single text field
        if text_columns:
            df_processed['combined_query_text'] = df_processed[text_columns].apply(
                lambda row: ' '.join(str(val) for val in row if val and str(val).strip()), axis=1
            )
        else:
            df_processed['combined_query_text'] = ''
        
        # Store column mapping for later use
        df_processed.attrs['column_mapping'] = column_mapping
        
        return df_processed
    
    async def train_model(self, df: pd.DataFrame, db: Session) -> Dict:
        """Train the AI gateway-powered model with database updates"""
        try:
            if self.ai_gateway_available:
                logger.info("Training AI Gateway enhanced model")
            else:
                logger.info("Training model with offline fallback (AI Gateway not available)")
            
            # Process Excel data
            processed_data = self._process_excel_data(df)
            
            # Update database with cases and advisor profiles
            cases_created, advisors_updated = await self._update_database_from_excel(processed_data, db)
            
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
                'cases_created': cases_created,
                'advisors_updated': advisors_updated,
                'ai_gateway_used': self.ai_gateway_available
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                'success': False,
                'message': f'Training failed: {str(e)}'
            }
    
    async def _update_database_from_excel(self, df: pd.DataFrame, db: Session) -> Tuple[int, int]:
        """Update database with cases and advisor profiles from Excel data"""
        try:
            column_mapping = df.attrs['column_mapping']
            cases_created = 0
            advisors_updated = 0
            
            # Clear existing assignments and cases (keep advisors)
            db.query(Assignment).delete()
            db.query(Case).delete()
            db.commit()
            
            # Process each row
            for idx, row in df.iterrows():
                # Create case
                case = self._create_case_from_row(row, column_mapping, db)
                if case:
                    cases_created += 1
                
                # Update advisor profile
                advisor_id = self._get_value_from_row(row, column_mapping, 'advisor_id')
                if advisor_id:
                    advisor = self._update_advisor_profile(row, column_mapping, advisor_id, db)
                    if advisor:
                        advisors_updated += 1
                
                # Create assignment if both case and advisor exist
                if case and advisor_id:
                    self._create_assignment(case, advisor_id, db)
            
            db.commit()
            logger.info(f"Database updated: {cases_created} cases created, {advisors_updated} advisors updated")
            return cases_created, advisors_updated
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
            db.rollback()
            return 0, 0
    
    def _get_value_from_row(self, row: pd.Series, column_mapping: Dict, key: str) -> str:
        """Get value from row using column mapping"""
        column_name = column_mapping.get(key)
        if column_name and column_name in row.index:
            value = str(row[column_name]).strip()
            return value if value and value != 'nan' else ''
        return ''
    
    def _create_case_from_row(self, row: pd.Series, column_mapping: Dict, db: Session) -> Optional[Case]:
        """Create case from Excel row"""
        try:
            # Generate case ID if not available
            case_id = self._get_value_from_row(row, column_mapping, 'case_id')
            if not case_id:
                case_id = f"CASE_{datetime.now().timestamp()}_{row.name}"
            
            # Check if case already exists
            existing_case = db.query(Case).filter(Case.case_id == case_id).first()
            if existing_case:
                return existing_case
            
            # Create new case
            case = Case(
                case_id=case_id,
                topic=self._get_value_from_row(row, column_mapping, 'topic'),
                subtopic=self._get_value_from_row(row, column_mapping, 'subtopic'),
                query=self._get_value_from_row(row, column_mapping, 'query_description') or 
                      self._get_value_from_row(row, column_mapping, 'query_title'),
                casetype=self._get_value_from_row(row, column_mapping, 'topic'),
                transaction_type=self._get_value_from_row(row, column_mapping, 'business_function'),
                business_function=self._get_value_from_row(row, column_mapping, 'business_function'),
                country=self._get_value_from_row(row, column_mapping, 'country'),
                complexity=self._calculate_complexity(row, column_mapping),
                status=self._determine_status(row, column_mapping)
            )
            
            # Set dates
            date_created = self._parse_date(row, column_mapping, 'date_created')
            date_submitted = self._parse_date(row, column_mapping, 'date_submitted')
            date_completion = self._parse_date(row, column_mapping, 'date_completion')
            
            if date_created:
                case.date_created = date_created
            if date_submitted:
                case.date_submitted = date_submitted
            if date_completion:
                case.date_resolved = date_completion
            
            # Calculate resolution time
            if date_created and date_completion:
                try:
                    resolution_time = (date_completion - date_created).days
                    if resolution_time > 0:
                        case.resolution_time = resolution_time
                except:
                    pass
            
            db.add(case)
            return case
            
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            return None
    
    def _calculate_complexity(self, row: pd.Series, column_mapping: Dict) -> float:
        """Calculate complexity score"""
        complexity_col = column_mapping.get('complexity')
        if complexity_col and complexity_col in row.index:
            try:
                return float(row[complexity_col])
            except:
                pass
        
        # Default complexity based on text length
        text_length = len(str(row.get('combined_query_text', '')))
        if text_length > 500:
            return 8.0
        elif text_length > 200:
            return 6.0
        elif text_length > 100:
            return 4.0
        else:
            return 2.0
    
    def _determine_status(self, row: pd.Series, column_mapping: Dict) -> str:
        """Determine case status"""
        status_col = column_mapping.get('status')
        if status_col and status_col in row.index:
            status = str(row[status_col]).lower()
            if any(keyword in status for keyword in ['resolved', 'completed', 'closed', 'done']):
                return 'resolved'
            elif any(keyword in status for keyword in ['pending', 'open', 'active']):
                return 'pending'
        
        # Default based on completion date
        date_completion = self._parse_date(row, column_mapping, 'date_completion')
        return 'resolved' if date_completion else 'pending'
    
    def _parse_date(self, row: pd.Series, column_mapping: Dict, date_key: str) -> Optional[datetime]:
        """Parse date from row"""
        date_col = column_mapping.get(date_key)
        if date_col and date_col in row.index:
            try:
                return pd.to_datetime(row[date_col])
            except:
                pass
        return None
    
    def _update_advisor_profile(self, row: pd.Series, column_mapping: Dict, advisor_id: str, db: Session) -> Optional[Advisor]:
        """Update advisor profile from Excel row"""
        try:
            # Get or create advisor
            advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
            if not advisor:
                advisor = Advisor(
                    advisor_id=advisor_id,
                    advisor_name=advisor_id,
                    department=self._get_value_from_row(row, column_mapping, 'department'),
                    business_function=self._get_value_from_row(row, column_mapping, 'business_function'),
                    country=self._get_value_from_row(row, column_mapping, 'country')
                )
                db.add(advisor)
            
            # Update expertise tags
            current_expertise = set()
            if advisor.expertise_tags:
                try:
                    # Parse existing expertise tags
                    existing_tags = advisor.expertise_tags.split(',')
                    current_expertise = set(tag.strip() for tag in existing_tags if tag.strip())
                except:
                    current_expertise = set()
            
            # Add topic and subtopic
            topic = self._get_value_from_row(row, column_mapping, 'topic')
            subtopic = self._get_value_from_row(row, column_mapping, 'subtopic')
            business_function = self._get_value_from_row(row, column_mapping, 'business_function')
            
            if topic:
                current_expertise.add(topic)
            if subtopic:
                current_expertise.add(subtopic)
            if business_function:
                current_expertise.add(business_function)
            
            # Store as comma-separated string
            advisor.expertise_tags = ','.join(list(current_expertise)[:10])  # Limit to 10
            
            # Update department and business function if not set
            if not advisor.department:
                advisor.department = self._get_value_from_row(row, column_mapping, 'department')
            if not advisor.business_function:
                advisor.business_function = self._get_value_from_row(row, column_mapping, 'business_function')
            if not advisor.country:
                advisor.country = self._get_value_from_row(row, column_mapping, 'country')
            
            return advisor
            
        except Exception as e:
            logger.error(f"Error updating advisor profile: {e}")
            return None
    
    def _create_assignment(self, case: Case, advisor_id: str, db: Session):
        """Create assignment linking case to advisor"""
        try:
            advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
            if advisor:
                assignment = Assignment(
                    case_id=case.id,
                    advisor_id=advisor.id,
                    assigned_at=datetime.now(),
                    status='assigned'
                )
                db.add(assignment)
        except Exception as e:
            logger.error(f"Error creating assignment: {e}")
    
    async def _train_department_classifier(self, df: pd.DataFrame) -> Dict:
        """Train improved department classifier"""
        try:
            column_mapping = df.attrs['column_mapping']
            department_col = column_mapping.get('department')
            
            if not department_col or department_col not in df.columns:
                return {'test_score': 0.0, 'train_score': 0.0, 'cv_mean': 0.0, 'cv_std': 0.0}
            
            # Prepare features
            X = self._extract_improved_features(df, column_mapping)
            y = df[department_col].fillna('Unknown')
            
            # Remove rows with no department
            valid_mask = y != 'Unknown'
            X = X[valid_mask]
            y = y[valid_mask]
            
            if len(X) < 10:
                return {'test_score': 0.0, 'train_score': 0.0, 'cv_mean': 0.0, 'cv_std': 0.0}
            
            # Encode target
            y_encoded = self.department_encoder.fit_transform(y)
            
            # Use GradientBoosting for better performance
            self.department_classifier = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            self.department_classifier.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.department_classifier.score(X_train, y_train)
            test_score = self.department_classifier.score(X_test, y_test)
            
            # Cross-validation
            cv_scores = cross_val_score(self.department_classifier, X, y_encoded, cv=3)
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Feature importance
            feature_names = ['business_function_encoded', 'country_encoded', 'complexity_score', 'text_length']
            feature_importance = dict(zip(feature_names, self.department_classifier.feature_importances_))
            
            logger.info(f"Department classifier trained - Test: {test_score:.3f}, CV: {cv_mean:.3f} ± {cv_std:.3f}")
            
            return {
                'test_score': test_score,
                'train_score': train_score,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error training department classifier: {e}")
            return {'test_score': 0.0, 'train_score': 0.0, 'cv_mean': 0.0, 'cv_std': 0.0}
    
    def _extract_improved_features(self, df: pd.DataFrame, column_mapping: Dict) -> np.ndarray:
        """Extract improved features for department classification"""
        features = []
        
        for _, row in df.iterrows():
            feature_vector = []
            
            # Business function encoding
            business_func = self._get_value_from_row(row, column_mapping, 'business_function')
            if hasattr(self.business_function_encoder, 'classes_'):
                if business_func in self.business_function_encoder.classes_:
                    feature_vector.append(self.business_function_encoder.transform([business_func])[0])
                else:
                    feature_vector.append(0)
            else:
                self.business_function_encoder.fit([business_func])
                feature_vector.append(0)
            
            # Country encoding
            country = self._get_value_from_row(row, column_mapping, 'country')
            if hasattr(self.country_encoder, 'classes_'):
                if country in self.country_encoder.classes_:
                    feature_vector.append(self.country_encoder.transform([country])[0])
                else:
                    feature_vector.append(0)
            else:
                self.country_encoder.fit([country])
                feature_vector.append(0)
            
            # Complexity score
            complexity = self._calculate_complexity(row, column_mapping)
            feature_vector.append(complexity)
            
            # Text length
            text_length = len(str(row.get('combined_query_text', '')))
            feature_vector.append(min(text_length / 100, 10))  # Normalize to 0-10
            
            features.append(feature_vector)
        
        return np.array(features)
    
    async def _generate_advisor_embeddings(self, df: pd.DataFrame, db: Session) -> Dict:
        """Generate advisor profile embeddings using AI Gateway"""
        try:
            column_mapping = df.attrs['column_mapping']
            advisor_col = column_mapping.get('advisor_id')
            
            if not advisor_col:
                return {'advisors_processed': 0}
            
            # Group by advisor
            advisor_groups = df.groupby(advisor_col)
            
            for advisor_id, advisor_data in advisor_groups:
                if not advisor_id or advisor_id == '' or pd.isna(advisor_id):
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
            column_mapping = df.attrs['column_mapping']
            advisor_col = column_mapping.get('advisor_id')
            
            if not advisor_col:
                return {'advisors_processed': 0}
            
            # Group by advisor
            advisor_groups = df.groupby(advisor_col)
            
            for advisor_id, advisor_data in advisor_groups:
                if not advisor_id or advisor_id == '' or pd.isna(advisor_id):
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
            
            features = np.array([[business_func_encoded, country_encoded, complexity, 5.0]])  # Default text length
            
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
                    'name': advisor.advisor_name,
                    'department': advisor.department,
                    'business_function': advisor.business_function,
                    'country': advisor.country,
                    'expertise_tags': advisor.expertise_tags.split(',') if advisor.expertise_tags else [],
                    'total_cases_handled': advisor.total_cases_handled,
                    'successful_cases': int(advisor.total_cases_handled * advisor.success_rate / 100) if advisor.success_rate else 0
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
                'ai_gateway_available': self.ai_gateway_available,
                'model_last_updated': self.model_metrics.get('last_trained', 'Never')
            }
            
        except Exception as e:
            logger.error(f"Error getting embedding stats: {e}")
            return {}
