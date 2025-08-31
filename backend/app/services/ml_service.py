import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
# Removed sentence_transformers - using offline TF-IDF instead
import pickle
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from ..models import Advisor, Case, Assignment, Tag
import logging

# Import the improved AI Gateway-powered ML model
from .ml_model_improved import AdvisorMatchingML

logger = logging.getLogger(__name__)

class MLAdvisorService:
    def __init__(self, model_save_path: str = "models/"):
        self.model_save_path = model_save_path
        self.model = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        # Removed sentence_transformer - using offline TF-IDF instead
        
        # Initialize the new AI Gateway-powered ML model
        self.advisor_matching_ml = AdvisorMatchingML()
        
        # Ensure model directory exists
        os.makedirs(model_save_path, exist_ok=True)
        
        # Try to load existing model
        try:
            self.advisor_matching_ml.load_model()
            logger.info("Loaded existing AI Gateway ML model")
        except Exception as e:
            logger.info(f"No existing model found or error loading: {e}")
    
    async def process_excel_data(self, excel_file_path: str, db: Session) -> Dict:
        """Process Excel file and update advisor profiles"""
        logger.info(f"Processing Excel file: {excel_file_path}")
        
        try:
            # Load Excel data
            df = pd.read_excel(excel_file_path)
            logger.info(f"Loaded {len(df)} transactions from Excel")
            
            # Process each transaction
            processed_cases = []
            advisor_profiles = {}
            
            for _, row in df.iterrows():
                # Create or update case
                case = self._create_case_from_row(row, db)
                processed_cases.append(case)
                
                # Update advisor profile
                advisor_id = row.get('Current Case Owner', row.get('case_owner', ''))
                if advisor_id:
                    if advisor_id not in advisor_profiles:
                        advisor_profiles[advisor_id] = {
                            'advisor_id': advisor_id,
                            'advisor_name': row.get('Current Case Owner', advisor_id),  # Use advisor_id as name if not available
                            'department': row.get('Business Function', row.get('department', '')),
                            'business_function': row.get('Business Function', row.get('business_function', '')),
                            'country': row.get('Country', row.get('country', '')),
                            'cases': [],
                            'topics': set(),
                            'subtopics': set(),
                            'complexities': [],
                            'resolution_times': [],
                            'success_count': 0,
                            'total_count': 0
                        }
                    
                    profile = advisor_profiles[advisor_id]
                    profile['cases'].append(case)
                    profile['topics'].add(case.topic)
                    profile['subtopics'].add(case.subtopic)
                    profile['complexities'].append(case.complexity)
                    
                    if case.status.value == 'resolved':
                        profile['success_count'] += 1
                        if case.resolution_time:
                            profile['resolution_times'].append(case.resolution_time)
                    
                    profile['total_count'] += 1
            
            # Update advisor profiles in database
            self._update_advisor_profiles(advisor_profiles, db)
            
            # Train comprehensive ML model with AI Gateway
            training_result = await self._train_comprehensive_model_with_ai(df, db)
            
            return {
                'message': 'Excel data processed successfully',
                'cases_processed': len(processed_cases),
                'advisors_updated': len(advisor_profiles),
                'model_accuracy': training_result.get('accuracy', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
    
    def _create_case_from_row(self, row: pd.Series, db: Session) -> Case:
        """Create a case from Excel row data"""
        case_id = str(row.get('Case ID', row.get('case_id', '')))
        
        # Generate unique case ID if not provided
        if not case_id or case_id == '' or case_id == 'nan':
            case_id = f'CASE_{datetime.now().timestamp()}_{row.name}'
        
        # Check if case already exists
        existing_case = db.query(Case).filter(Case.case_id == case_id).first()
        if existing_case:
            return existing_case
        
        # Create new case
        case = Case(
            case_id=case_id,
            topic=str(row.get('Topics', row.get('topic', ''))),
            subtopic=str(row.get('Current Sub-Topic', row.get('subtopic', ''))),
            query=str(row.get('Please describe your query', row.get('query', ''))),
            casetype=str(row.get('Category', row.get('casetype', ''))),
            transaction_type=str(row.get('Services', row.get('transaction_type', ''))),
            business_function=str(row.get('Business Function', row.get('business_function', ''))),
            country=str(row.get('Country', row.get('country', ''))),
            complexity=float(row.get('Complexity', row.get('complexity', 50.0))),
            status='resolved' if str(row.get('Status', '')).lower() in ['resolved', 'completed'] else 'pending'
        )
        
        # Calculate resolution time if available
        if case.status == 'resolved':
            try:
                date_created = pd.to_datetime(row.get('Date Created', row.get('date_created')))
                date_resolved = pd.to_datetime(row.get('Date Submitted', row.get('date_resolved')))
                case.date_created = date_created
                case.date_resolved = date_resolved
                case.resolution_time = (date_resolved - date_created).days
            except:
                pass
        
        db.add(case)
        db.commit()
        return case
    
    def _update_advisor_profiles(self, advisor_profiles: Dict, db: Session):
        """Update advisor profiles based on transaction history"""
        for advisor_id, profile_data in advisor_profiles.items():
            # Get or create advisor
            advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
            if not advisor:
                # Create new advisor with basic info
                advisor = Advisor(
                    advisor_id=advisor_id,
                    advisor_name=profile_data.get('advisor_name', advisor_id),
                    department=profile_data.get('department', ''),
                    business_function=profile_data.get('business_function', ''),
                    country=profile_data.get('country', ''),
                    total_cases_handled=0,
                    success_rate=0.0,
                    avg_resolution_time=0.0,
                    complexity_preference=50.0,
                    expertise_tags='',
                    profile_summary=''
                )
                db.add(advisor)
                db.flush()  # Get the ID without committing
            
            # Update advisor name and basic info if not set
            if not advisor.advisor_name or advisor.advisor_name == advisor_id:
                advisor.advisor_name = profile_data.get('advisor_name', advisor_id)
            if not advisor.department:
                advisor.department = profile_data.get('department', '')
            if not advisor.business_function:
                advisor.business_function = profile_data.get('business_function', '')
            if not advisor.country:
                advisor.country = profile_data.get('country', '')
            
            # Update metrics (accumulate for existing advisors)
            advisor.total_cases_handled = profile_data['total_count']
            advisor.success_rate = (profile_data['success_count'] / profile_data['total_count'] * 100) if profile_data['total_count'] > 0 else 0
            
            if profile_data['resolution_times']:
                advisor.avg_resolution_time = np.mean(profile_data['resolution_times'])
            
            if profile_data['complexities']:
                advisor.complexity_preference = np.mean(profile_data['complexities'])
            
            # Update expertise tags (merge with existing)
            current_tags = set()
            if advisor.expertise_tags:
                current_tags = set(tag.strip() for tag in advisor.expertise_tags.split(',') if tag.strip())
            
            # Add new topics and subtopics
            topics = list(profile_data['topics'])
            subtopics = list(profile_data['subtopics'])
            new_tags = topics + subtopics
            
            for tag in new_tags:
                if tag and tag.strip():
                    current_tags.add(tag.strip())
            
            # Limit to 10 tags and update
            advisor.expertise_tags = ','.join(list(current_tags)[:10])
            
            # Generate profile summary
            advisor.profile_summary = self._generate_profile_summary(profile_data)
            
            # Update the advisor record
            db.merge(advisor)
        
        # Commit all changes at once
        db.commit()
    
    def _generate_profile_summary(self, profile_data: Dict) -> str:
        """Generate advisor profile summary"""
        total_cases = profile_data['total_count']
        success_rate = (profile_data['success_count'] / total_cases * 100) if total_cases > 0 else 0
        topics = list(profile_data['topics'])
        
        summary = f"Advisor with {total_cases} cases handled"
        if topics:
            summary += f", specializing in {', '.join(topics[:3])}"
        summary += f" with {success_rate:.1f}% success rate"
        
        return summary
    
    def _train_model(self, df: pd.DataFrame, db: Session) -> Dict:
        """Train ML model for advisor matching"""
        logger.info("Training ML model for advisor matching...")
        
        try:
            # Prepare features
            X, y = self._prepare_features(df)
            
            if len(X) == 0:
                return {'accuracy': 0.0, 'message': 'No data available for training'}
            
            # Train Random Forest model
            self.model = RandomForestClassifier(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
            
            # Simple train/test split
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            if len(X_train) == 0:
                return {'accuracy': 0.0, 'message': 'Insufficient data for training'}
            
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred) if len(y_test) > 0 else 0.0
            
            # Save model
            self._save_model(accuracy)
            
            logger.info(f"Model trained with accuracy: {accuracy:.4f}")
            return {'accuracy': accuracy}
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {'accuracy': 0.0, 'error': str(e)}
    
    async def _train_comprehensive_model_with_ai(self, df: pd.DataFrame, db: Session) -> Dict:
        """Train the comprehensive ML model on transaction data using AI Gateway"""
        try:
            logger.info("Training comprehensive ML model with AI Gateway")
            
            # Train the model using the new AI Gateway-powered ML model
            training_result = await self.advisor_matching_ml.train_model(df, db)
            
            return {
                'accuracy': training_result.get('department_accuracy', 0.0),
                'model_name': training_result.get('message', 'AI Gateway Model'),
                'cv_mean': training_result.get('cv_mean', 0.0),
                'cases_created': training_result.get('cases_created', 0),
                'advisors_updated': training_result.get('advisors_updated', 0)
            }
            
        except Exception as e:
            logger.error(f"Error training comprehensive model: {e}")
            return {'accuracy': 0.0, 'error': str(e)}
    
    def _create_query_text(self, df: pd.DataFrame) -> pd.Series:
        """Create comprehensive query text by combining relevant columns"""
        query_texts = []
        
        for _, row in df.iterrows():
            text_parts = []
            
            # Add services and topics
            if 'Services' in df.columns:
                text_parts.append(str(row['Services']))
            if 'Topics' in df.columns:
                text_parts.append(str(row['Topics']))
            if 'Current Sub-Topic' in df.columns:
                text_parts.append(str(row['Current Sub-Topic']))
            
            # Add query description
            if 'Please describe your query' in df.columns:
                query_desc = str(row['Please describe your query'])
                if query_desc and query_desc != 'nan':
                    text_parts.append(query_desc)
            
            # Add business context
            if 'Business Function' in df.columns:
                text_parts.append(str(row['Business Function']))
            if 'Department' in df.columns:
                text_parts.append(str(row['Department']))
            if 'Country' in df.columns:
                text_parts.append(str(row['Country']))
            
            query_texts.append(' '.join(text_parts))
        
        return pd.Series(query_texts)
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ML model"""
        features = []
        labels = []
        
        for _, row in df.iterrows():
            # Text features
            text = f"{row.get('Topics', '')} {row.get('Current Sub-Topic', '')} {row.get('Please describe your query', '')}"
            
            # Basic features
            complexity = float(row.get('Complexity', 50.0))
            business_function = str(row.get('Business Function', ''))
            country = str(row.get('Country', ''))
            
            # Combine features
            feature_vector = [
                complexity,
                len(text),
                hash(business_function) % 1000,  # Simple encoding
                hash(country) % 1000
            ]
            
            features.append(feature_vector)
            
            # Label (advisor ID)
            advisor_id = str(row.get('Current Case Owner', ''))
            if advisor_id:
                labels.append(advisor_id)
            else:
                labels.append('unknown')
        
        if not features:
            return np.array([]), np.array([])
        
        X = np.array(features)
        y = np.array(labels)
        
        return X, y
    
    def _save_model(self, accuracy: float):
        """Save trained model"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(self.model_save_path, f"advisor_model_{timestamp}.pkl")
        
        model_data = {
            'model': self.model,
            'accuracy': accuracy,
            'timestamp': timestamp
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved: {model_path}")
    
    def recommend_advisors(self, case_data: Dict, db: Session) -> List[Dict]:
        """Recommend advisors for a new case using the comprehensive ML model"""
        try:
            # Check if the comprehensive ML model is trained
            if not hasattr(self.advisor_matching_ml, 'model') or self.advisor_matching_ml.model is None:
                # Try to load existing model
                try:
                    self.advisor_matching_ml.load_model()
                except FileNotFoundError:
                    logger.warning("No trained model found. Using fallback recommendations.")
                    return self._fallback_recommendations(case_data, db)
            
            # Create QueryFeatures object
            query = QueryFeatures(
                topic=case_data.get('topic', ''),
                subtopic=case_data.get('subtopic', ''),
                query_text=case_data.get('query', ''),
                business_function=case_data.get('business_function', ''),
                department=case_data.get('department', ''),
                country=case_data.get('country', ''),
                category=case_data.get('category', ''),
                complexity=float(case_data.get('complexity', 50.0))
            )
            
            # Get recommendations using the comprehensive ML model
            advisor_matches = self.advisor_matching_ml.predict_advisors(query)
            
            # Convert to the expected format
            recommendations = []
            for match in advisor_matches:
                recommendations.append({
                    'advisor_id': match.advisor_id,
                    'advisor_name': match.advisor_name,
                    'confidence': match.matching_score / 100.0,  # Convert percentage to decimal
                    'expertise_tags': match.expertise_tags,
                    'success_rate': match.success_rate,
                    'total_cases': match.total_cases,
                    'matching_reasons': match.matching_reasons
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in comprehensive ML recommendations: {e}")
            return self._fallback_recommendations(case_data, db)
    
    def _prepare_case_features(self, case_data: Dict) -> np.ndarray:
        """Prepare features for a single case"""
        text = f"{case_data.get('topic', '')} {case_data.get('subtopic', '')} {case_data.get('query', '')}"
        complexity = float(case_data.get('complexity', 50.0))
        business_function = str(case_data.get('business_function', ''))
        country = str(case_data.get('country', ''))
        
        return np.array([
            complexity,
            len(text),
            hash(business_function) % 1000,
            hash(country) % 1000
        ])
    
    def _fallback_recommendations(self, case_data: Dict, db: Session) -> List[Dict]:
        """Fallback recommendations based on topic similarity"""
        topic = case_data.get('topic', '').lower()
        business_function = case_data.get('business_function', '').lower()
        
        # Find advisors with similar expertise
        advisors = db.query(Advisor).all()
        recommendations = []
        
        for advisor in advisors:
            score = 0.0
            if advisor.expertise_tags:
                tags = advisor.expertise_tags.lower()
                if topic in tags:
                    score += 0.5
                if business_function in tags:
                    score += 0.3
                score += advisor.success_rate / 100 * 0.2
            
            if score > 0:
                recommendations.append({
                    'advisor_id': advisor.advisor_id,
                    'advisor_name': advisor.advisor_name,
                    'confidence': score,
                    'expertise_tags': advisor.expertise_tags,
                    'success_rate': advisor.success_rate,
                    'total_cases': advisor.total_cases_handled
                })
        
        # Sort by confidence and return top 3
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        return recommendations[:3]
    
    def _load_latest_model(self):
        """Load the latest trained model"""
        try:
            model_files = [f for f in os.listdir(self.model_save_path) if f.endswith('.pkl')]
            if not model_files:
                return
            
            latest_file = max(model_files, key=lambda x: os.path.getctime(os.path.join(self.model_save_path, x)))
            model_path = os.path.join(self.model_save_path, latest_file)
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
            
            logger.info(f"Loaded model: {latest_file}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def update_advisor_profile(self, advisor_id: str, case_data: Dict, db: Session):
        """Update advisor profile after case completion"""
        advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
        if not advisor:
            return
        
        # Update metrics
        advisor.total_cases_handled += 1
        
        # Update expertise tags
        if advisor.expertise_tags:
            current_tags = advisor.expertise_tags.split(',')
        else:
            current_tags = []
        
        new_topics = [case_data.get('topic', ''), case_data.get('subtopic', '')]
        for topic in new_topics:
            if topic and topic not in current_tags:
                current_tags.append(topic)
        
        advisor.expertise_tags = ','.join(current_tags[:10])  # Keep top 10
        
        # Update complexity preference
        new_complexity = float(case_data.get('complexity', 50.0))
        if advisor.complexity_preference:
            advisor.complexity_preference = (advisor.complexity_preference + new_complexity) / 2
        else:
            advisor.complexity_preference = new_complexity
        
        db.commit()
        logger.info(f"Updated advisor profile: {advisor_id}")
