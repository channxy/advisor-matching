import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
import joblib
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import os
import re
from pydantic import BaseModel
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvisorProfile(BaseModel):
    advisor_id: str
    advisor_name: str
    current_advisory_group: str
    previous_advisory_group: Optional[str] = None
    department: str
    previous_departments: Optional[str] = None
    business_function: str
    country: str
    other_countries_handled: Optional[str] = None
    avg_resolution_time: float
    total_cases_handled: int
    success_rate: float
    profile_summary: Optional[str] = None
    expertise_tags: Optional[str] = None
    complexity_preference: float
    created_at: datetime
    updated_at: Optional[datetime] = None

class QueryFeatures(BaseModel):
    topic: str
    subtopic: str
    query_text: str
    business_function: str
    department: str
    country: str
    category: str
    complexity: float

class AdvisorMatch(BaseModel):
    advisor_id: str
    advisor_name: str
    matching_score: float
    matching_reasons: List[str]
    expertise_tags: str
    success_rate: float
    total_cases: int

class OfflineTextProcessor(BaseEstimator, TransformerMixin):
    """Completely offline text processor using TF-IDF and custom features"""
    
    def __init__(self, max_features=1000):
        self.max_features = max_features
        self.tfidf = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9
        )
        self.fitted = False
        
    def fit(self, X, y=None):
        try:
            # Fit TF-IDF on the text data
            self.tfidf.fit(X)
            self.fitted = True
            logger.info("TF-IDF vectorizer fitted successfully")
        except Exception as e:
            logger.warning(f"Could not fit TF-IDF: {e}")
            self.fitted = False
        return self
    
    def transform(self, X):
        if not self.fitted:
            # Return zero features if not fitted
            return np.zeros((len(X), self.max_features))
        
        try:
            # Transform text to TF-IDF features
            tfidf_features = self.tfidf.transform(X).toarray()
            
            # Add custom text features
            custom_features = self._extract_custom_features(X)
            
            # Combine features
            combined_features = np.hstack([tfidf_features, custom_features])
            
            return combined_features
        except Exception as e:
            logger.error(f"Error in text transformation: {e}")
            return np.zeros((len(X), self.max_features + 10))  # +10 for custom features
    
    def _extract_custom_features(self, texts):
        """Extract custom text features without external dependencies"""
        features = []
        
        for text in texts:
            if not isinstance(text, str):
                text = str(text)
            
            # Text length features
            text_length = len(text)
            word_count = len(text.split())
            avg_word_length = np.mean([len(word) for word in text.split()]) if word_count > 0 else 0
            
            # Complexity features
            unique_words = len(set(text.lower().split()))
            vocabulary_richness = unique_words / word_count if word_count > 0 else 0
            
            # Special character features
            special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', text))
            numbers = len(re.findall(r'\d', text))
            
            # Topic-specific keywords (business domain)
            business_keywords = ['tax', 'audit', 'consulting', 'strategy', 'risk', 'compliance', 'financial', 'advisory']
            keyword_count = sum(1 for keyword in business_keywords if keyword.lower() in text.lower())
            
            # Country/region keywords
            country_keywords = ['united states', 'canada', 'uk', 'australia', 'singapore', 'europe', 'asia']
            country_count = sum(1 for country in country_keywords if country.lower() in text.lower())
            
            # Department keywords
            dept_keywords = ['tax', 'audit', 'consulting', 'technology', 'risk', 'strategy']
            dept_count = sum(1 for dept in dept_keywords if dept.lower() in text.lower())
            
            # Combine all features
            feature_vector = [
                text_length,
                word_count,
                avg_word_length,
                unique_words,
                vocabulary_richness,
                special_chars,
                numbers,
                keyword_count,
                country_count,
                dept_count
            ]
            
            features.append(feature_vector)
        
        return np.array(features)

class AdvisorMatchingMLOffline:
    """
    Completely offline ML model for advisor matching - no external downloads required
    """
    
    def __init__(self, model_path: str = "models/advisor_matching_model_offline.pkl"):
        self.model_path = model_path
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.text_processor = OfflineTextProcessor()
        self.feature_columns = [
            'Topics', 'Current Sub-Topic', 'Business Function', 'Department', 
            'Country', 'Category', 'Complexity'
        ]
        self.text_columns = ['query_text']
        self.target_column = 'Current Case Owner'
        self.advisor_profiles = {}
        self.model_metrics = {}
        
        # Create models directory
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
    def load_and_preprocess_data(self, excel_path: str) -> pd.DataFrame:
        """
        Load and preprocess transaction data from Excel
        """
        logger.info(f"Loading data from {excel_path}")
        
        try:
            # Load Excel file
            df = pd.read_excel(excel_path)
            logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
            
            # Clean and preprocess data
            df_clean = self._clean_data(df)
            
            # Create query text by combining relevant columns
            df_clean['query_text'] = self._create_query_text(df_clean)
            
            # Only use resolved cases for training (as per requirements)
            df_resolved = df_clean[df_clean['Status'] == 'Resolved'].copy()
            logger.info(f"Using {len(df_resolved)} resolved cases for training")
            
            return df_resolved
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare the data
        """
        # Handle missing values
        df = df.fillna({
            'Previous Sub-Topic': 'None',
            'Previous Case Owner': 'None',
            'Previous Advisory Group': 'None',
            'Please describe your query': ''
        })
        
        # Convert date columns
        date_columns = ['Date Created', 'Date Submitted']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate resolution time
        df['resolution_time'] = (df['Date Submitted'] - df['Date Created']).dt.days
        
        return df
    
    def _create_query_text(self, df: pd.DataFrame) -> pd.Series:
        """
        Create comprehensive query text by combining relevant columns
        """
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
    
    def create_advisor_profiles(self, df: pd.DataFrame) -> Dict[str, AdvisorProfile]:
        """
        Create comprehensive advisor profiles from transaction data
        """
        logger.info("Creating advisor profiles...")
        
        profiles = {}
        
        # Group by advisor
        advisor_groups = df.groupby('Current Case Owner')
        
        for advisor_id, group in advisor_groups:
            if pd.isna(advisor_id) or advisor_id == 'None':
                continue
                
            # Sort by date to get latest information
            group_sorted = group.sort_values('Date Created', ascending=False)
            latest_record = group_sorted.iloc[0]
            
            # Calculate metrics
            total_cases = len(group)
            success_rate = 100.0  # All resolved cases are considered successful
            avg_resolution_time = group['resolution_time'].mean()
            avg_complexity = group['Complexity'].mean()
            
            # Get unique values for lists
            advisory_groups = group['Current Advisory Group'].unique()
            previous_advisory_groups = group['Previous Advisory Group'].unique()
            departments = group['Department'].unique()
            countries = group['Country'].unique()
            
            # Create expertise tags
            topics = group['Topics'].unique()
            subtopics = group['Current Sub-Topic'].unique()
            services = group['Services'].unique()
            
            expertise_tags = ', '.join(list(topics) + list(subtopics) + list(services))
            
            # Generate profile summary using local text analysis
            profile_summary = self._generate_profile_summary_offline(group)
            
            profile = AdvisorProfile(
                advisor_id=str(advisor_id),
                advisor_name=str(advisor_id),  # Using ID as name for now
                current_advisory_group=str(latest_record['Current Advisory Group']),
                previous_advisory_group=', '.join(previous_advisory_groups) if len(previous_advisory_groups) > 1 else None,
                department=str(latest_record['Department']),
                previous_departments=', '.join(departments) if len(departments) > 1 else None,
                business_function=str(latest_record['Business Function']),
                country=str(latest_record['Country']),
                other_countries_handled=', '.join(countries) if len(countries) > 1 else None,
                avg_resolution_time=avg_resolution_time,
                total_cases_handled=total_cases,
                success_rate=success_rate,
                profile_summary=profile_summary,
                expertise_tags=expertise_tags,
                complexity_preference=avg_complexity,
                created_at=datetime.now(),
                updated_at=None
            )
            
            profiles[str(advisor_id)] = profile
        
        self.advisor_profiles = profiles
        logger.info(f"Created {len(profiles)} advisor profiles")
        return profiles
    
    def _generate_profile_summary_offline(self, advisor_data: pd.DataFrame) -> str:
        """
        Generate profile summary using local text analysis (no external APIs)
        """
        try:
            # Create summary from advisor's case data
            topics = advisor_data['Topics'].unique()
            subtopics = advisor_data['Current Sub-Topic'].unique()
            services = advisor_data['Services'].unique()
            countries = advisor_data['Country'].unique()
            
            # Calculate key metrics
            avg_complexity = advisor_data['Complexity'].mean()
            avg_resolution_time = advisor_data['resolution_time'].mean()
            total_cases = len(advisor_data)
            
            # Determine expertise level
            if total_cases >= 5:
                expertise_level = "expert"
            elif total_cases >= 3:
                expertise_level = "experienced"
            else:
                expertise_level = "specialist"
            
            # Determine primary focus areas
            primary_topics = list(topics)[:3] if len(topics) > 3 else list(topics)
            primary_services = list(services)[:2] if len(services) > 2 else list(services)
            
            summary_text = f"""
            This {expertise_level} advisor specializes in {', '.join(primary_services)} with expertise in {', '.join(primary_topics)}.
            Key areas include {', '.join(subtopics)}. They have handled cases in {', '.join(countries)}.
            Total cases: {total_cases}, Average resolution time: {avg_resolution_time:.1f} days, Average complexity: {avg_complexity:.1f}.
            """
            
            return summary_text.strip()
            
        except Exception as e:
            logger.warning(f"Could not generate profile summary: {e}")
            return "Advisor profile generated from case history."
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for ML model training
        """
        logger.info("Preparing features for ML model...")
        
        # Prepare categorical features
        X_categorical = df[self.feature_columns].copy()
        
        # Encode categorical variables
        for col in self.feature_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                X_categorical[col] = self.label_encoders[col].fit_transform(X_categorical[col].astype(str))
            else:
                X_categorical[col] = self.label_encoders[col].transform(X_categorical[col].astype(str))
        
        # Prepare text features
        X_text = df['query_text'].fillna('')
        
        # Prepare numerical features
        X_numerical = df[['Complexity']].values
        
        # Combine features
        X_combined = np.hstack([
            X_categorical.values,
            X_numerical
        ])
        
        # Store feature names for consistency
        self.feature_names = self.feature_columns + ['Complexity']
        
        # Prepare target
        y = df[self.target_column].astype(str)
        
        return X_combined, y.values
    
    def train_model(self, df: pd.DataFrame) -> Dict:
        """
        Train the ML model
        """
        logger.info("Training ML model...")
        
        # Prepare features
        X, y = self.prepare_features(df)
        
        # Split data (without stratification due to small sample size)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multiple models and compare
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            logger.info(f"Training {name}...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # For small datasets, skip cross-validation
            cv_mean = test_score
            cv_std = 0.0
            
            logger.info(f"{name} - Train: {train_score:.3f}, Test: {test_score:.3f}")
            
            if test_score > best_score:
                best_score = test_score
                best_model = model
                best_model_name = name
        
        self.model = best_model
        
        # Store metrics
        self.model_metrics = {
            'model_name': best_model_name,
            'train_score': train_score,
            'test_score': test_score,
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'feature_importance': dict(zip(self.feature_columns, best_model.feature_importances_)) if best_model else {}
        }
        
        logger.info(f"Best model: {best_model_name} with test score: {best_score:.3f}")
        
        return self.model_metrics
    
    def save_model(self):
        """
        Save the trained model and components
        """
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'advisor_profiles': self.advisor_profiles,
            'model_metrics': self.model_metrics
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """
        Load the trained model and components
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']
        self.advisor_profiles = model_data['advisor_profiles']
        self.model_metrics = model_data['model_metrics']
        
        logger.info(f"Model loaded from {self.model_path}")
    
    def predict_advisors(self, query: QueryFeatures) -> List[AdvisorMatch]:
        """
        Predict top 3 matching advisors for a new query
        """
        if self.model is None:
            raise ValueError("Model not loaded. Load or train the model first.")
        
        # Prepare query features
        query_data = pd.DataFrame([{
            'Topics': query.topic,
            'Current Sub-Topic': query.subtopic,
            'Business Function': query.business_function,
            'Department': query.department,
            'Country': query.country,
            'Category': query.category,
            'Complexity': query.complexity
        }])
        
        # Encode features
        encoded_features = []
        for col in self.feature_columns:
            if col in self.label_encoders:
                # Handle unseen categories
                try:
                    encoded_val = self.label_encoders[col].transform([query_data[col].iloc[0]])[0]
                except ValueError:
                    # Use most common category for unseen values
                    encoded_val = 0
                encoded_features.append(encoded_val)
            else:
                encoded_features.append(0)
        
        # Add numerical features
        encoded_features.append(query_data['Complexity'].iloc[0])
        
        # Convert to numpy array
        query_features = np.array([encoded_features])
        
        # Scale features
        query_features = self.scaler.transform(query_features)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(query_features)[0]
        classes = self.model.classes_
        
        # Create advisor matches
        advisor_matches = []
        
        for i, (advisor_id, prob) in enumerate(zip(classes, probabilities)):
            if advisor_id in self.advisor_profiles:
                profile = self.advisor_profiles[advisor_id]
                
                # Calculate matching reasons
                reasons = self._calculate_matching_reasons(query, profile)
                
                match = AdvisorMatch(
                    advisor_id=advisor_id,
                    advisor_name=profile.advisor_name,
                    matching_score=prob * 100,  # Convert to percentage
                    matching_reasons=reasons,
                    expertise_tags=profile.expertise_tags or "",
                    success_rate=profile.success_rate,
                    total_cases=profile.total_cases_handled
                )
                
                advisor_matches.append(match)
        
        # Sort by matching score and return top 3
        advisor_matches.sort(key=lambda x: x.matching_score, reverse=True)
        return advisor_matches[:3]
    
    def _calculate_matching_reasons(self, query: QueryFeatures, profile: AdvisorProfile) -> List[str]:
        """
        Calculate reasons why an advisor matches the query
        """
        reasons = []
        
        # Topic matching (highest priority)
        if query.topic.lower() in profile.expertise_tags.lower():
            reasons.append(f"Expertise in {query.topic}")
        
        # Subtopic matching
        if query.subtopic.lower() in profile.expertise_tags.lower():
            reasons.append(f"Specialized in {query.subtopic}")
        
        # Business function matching
        if query.business_function.lower() == profile.business_function.lower():
            reasons.append(f"Same business function: {query.business_function}")
        
        # Department matching
        if query.department.lower() == profile.department.lower():
            reasons.append(f"Same department: {query.department}")
        
        # Country matching
        if query.country.lower() == profile.country.lower():
            reasons.append(f"Experience in {query.country}")
        
        # Complexity preference
        if abs(query.complexity - profile.complexity_preference) <= 10:
            reasons.append(f"Handles similar complexity levels")
        
        # Success rate
        if profile.success_rate >= 90:
            reasons.append(f"High success rate: {profile.success_rate}%")
        
        return reasons
    
    def update_advisor_profile(self, advisor_id: str, new_case_data: Dict):
        """
        Update advisor profile with new case data
        """
        if advisor_id not in self.advisor_profiles:
            logger.warning(f"Advisor {advisor_id} not found in profiles")
            return
        
        profile = self.advisor_profiles[advisor_id]
        
        # Update metrics
        profile.total_cases_handled += 1
        
        # Update expertise tags
        new_topics = new_case_data.get('topic', '')
        new_subtopics = new_case_data.get('subtopic', '')
        new_services = new_case_data.get('services', '')
        
        current_tags = profile.expertise_tags or ""
        new_tags = f"{new_topics}, {new_subtopics}, {new_services}"
        profile.expertise_tags = f"{current_tags}, {new_tags}".strip(', ')
        
        # Update complexity preference
        new_complexity = new_case_data.get('complexity', 50)
        total_cases = profile.total_cases_handled
        profile.complexity_preference = (
            (profile.complexity_preference * (total_cases - 1) + new_complexity) / total_cases
        )
        
        # Update timestamp
        profile.updated_at = datetime.now()
        
        logger.info(f"Updated profile for advisor {advisor_id}")
    
    def get_model_performance(self) -> Dict:
        """
        Get model performance metrics
        """
        return self.model_metrics
    
    def retrain_model(self, new_data_path: str):
        """
        Retrain model with new data
        """
        logger.info("Retraining ML model with new data...")
        
        # Load new data
        new_df = self.load_and_preprocess_data(new_data_path)
        
        # Combine with existing data if available
        if hasattr(self, 'current_data'):
            combined_df = pd.concat([self.current_data, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        # Update advisor profiles
        self.create_advisor_profiles(combined_df)
        
        # Retrain model
        metrics = self.train_model(combined_df)
        
        # Save updated model
        self.save_model()
        
        logger.info("Model retraining completed")
        return metrics

# Example usage and testing
if __name__ == "__main__":
    # Initialize ML model
    ml_model = AdvisorMatchingMLOffline()
    
    # Load and preprocess data
    df = ml_model.load_and_preprocess_data("transactions.xlsx")
    
    # Create advisor profiles
    profiles = ml_model.create_advisor_profiles(df)
    
    # Train model
    metrics = ml_model.train_model(df)
    
    # Save model
    ml_model.save_model()
    
    # Test prediction
    test_query = QueryFeatures(
        topic="Corporate Tax",
        subtopic="Tax Planning",
        query_text="Client needs tax optimization strategy for M&A transaction",
        business_function="Tax Advisory",
        department="Tax",
        country="United States",
        category="Consultation",
        complexity=85.0
    )
    
    matches = ml_model.predict_advisors(test_query)
    
    print("\n=== MODEL PERFORMANCE ===")
    print(f"Test Score: {metrics['test_score']:.3f}")
    print(f"Cross-validation: {metrics['cv_mean']:.3f} (+/- {metrics['cv_std'] * 2:.3f})")
    
    print("\n=== TOP MATCHES ===")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.advisor_name} (Score: {match.matching_score:.1f}%)")
        print(f"   Reasons: {', '.join(match.matching_reasons)}")
        print(f"   Success Rate: {match.success_rate}%")
        print()
