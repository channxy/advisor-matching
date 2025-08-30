import openai
import os
import json
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class AIServiceGateway:
    """
    AI service using local AI gateway with multiple model options
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, default_model: str = "gpt4o"):
        # Use environment variables or provided parameters
        self.base_url = base_url or os.getenv("OPENAI_API_BASE_URL")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_model = default_model
        
        # Available models on your gateway
        self.available_models = {
            "gpt4o": "gpt-4o",
            "gpt4o-mini": "gpt-4o-mini", 
            "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3-opus": "claude-3-opus-20240229",
            "llama-3-3-70b": "llama-3-3-70b-instruct",
            "llama-3-1-8b": "llama-3-1-8b-instruct",
            "o3mini": "o3mini",
            "bgelarge": "bgelarge",
            "text3large": "text3large"
        }
        
        # Initialize OpenAI client
        if self.base_url and self.api_key:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"AI Gateway connected to: {self.base_url}")
            logger.info(f"Available models: {list(self.available_models.keys())}")
        else:
            self.client = None
            logger.warning("AI Gateway not configured. Using offline fallback.")
        
        # Fallback TF-IDF for offline mode
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        self.fitted = False
    
    def _get_model_name(self, model_key: str = None) -> str:
        """Get the actual model name for the gateway"""
        model_key = model_key or self.default_model
        return self.available_models.get(model_key, self.available_models[self.default_model])
    
    async def get_embedding(self, text: str, model: str = "text3large") -> List[float]:
        """Get embedding using AI gateway"""
        if not self.client:
            return await self._get_embedding_offline(text)
        
        try:
            # Use text3large for embeddings (or bgelarge if available)
            embedding_model = "text3large" if model == "text3large" else "bgelarge"
            
            response = self.client.embeddings.create(
                model=embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Gateway embedding failed: {e}. Using offline fallback.")
            return await self._get_embedding_offline(text)
    
    async def _get_embedding_offline(self, text: str) -> List[float]:
        """Offline embedding fallback"""
        try:
            if not self.fitted:
                sample_texts = [
                    "tax planning and optimization",
                    "audit and compliance review", 
                    "financial advisory services",
                    "risk management strategy",
                    "merger and acquisition consulting"
                ]
                self.tfidf.fit(sample_texts)
                self.fitted = True
            
            embedding = self.tfidf.transform([text]).toarray()[0]
            
            if len(embedding) < 1536:
                embedding = np.pad(embedding, (0, 1536 - len(embedding)), 'constant')
            else:
                embedding = embedding[:1536]
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Offline embedding failed: {e}")
            return [0.0] * 1536
    
    async def classify_case(self, query: str, topic: str, subtopic: str, model: str = None) -> Dict[str, Any]:
        """Classify case using AI gateway"""
        if not self.client:
            return await self._classify_case_offline(query, topic, subtopic)
        
        try:
            model_name = self._get_model_name(model)
            
            prompt = f"""
            Analyze this business case and provide classification:
            
            Topic: {topic}
            Subtopic: {subtopic}
            Query: {query}
            
            Provide a JSON response with:
            - complexity_score: 0-100 scale (based on technical difficulty, regulatory requirements, scope)
            - domain_relevance: 0-1 scale (how relevant to business/financial domain)
            - classification_confidence: 0-1 scale (confidence in classification)
            - suggested_tags: list of relevant expertise tags (max 5 tags)
            
            Consider factors like:
            - Technical complexity (tax law, regulations, financial instruments)
            - Geographic scope (international, multi-jurisdictional)
            - Industry-specific requirements
            - Regulatory compliance needs
            - Business impact and strategic importance
            
            Return only valid JSON, no additional text.
            """
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Case classified using {model_name}")
            return result
            
        except Exception as e:
            logger.warning(f"Gateway classification failed: {e}. Using offline fallback.")
            return await self._classify_case_offline(query, topic, subtopic)
    
    async def _classify_case_offline(self, query: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """Offline case classification fallback"""
        try:
            combined_text = f"{topic} {subtopic} {query}".lower()
            
            # Simple rule-based classification
            complexity_score = min(100, max(0, 
                len(query.split()) * 0.5 +
                len([c for c in query if c.isupper()]) * 0.3 +
                len([word for word in query.lower().split() if word in ['complex', 'advanced', 'technical', 'regulatory', 'international']]) * 15
            ))
            
            domain_relevance = min(1.0, max(0.0,
                len([word for word in query.lower().split() if word in ['tax', 'audit', 'financial', 'compliance', 'strategy']]) / 10.0
            ))
            
            classification_confidence = min(1.0, max(0.0, 0.5 + len(query.split()) / 100.0))
            
            suggested_tags = [topic, subtopic]
            if 'tax' in query.lower():
                suggested_tags.append('Tax')
            if 'audit' in query.lower():
                suggested_tags.append('Audit')
            if 'strategy' in query.lower():
                suggested_tags.append('Strategy')
            
            return {
                "complexity_score": round(complexity_score, 1),
                "domain_relevance": round(domain_relevance, 2),
                "classification_confidence": round(classification_confidence, 2),
                "suggested_tags": suggested_tags[:5]
            }
        except Exception as e:
            logger.error(f"Offline classification failed: {e}")
            return {
                "complexity_score": 50.0,
                "domain_relevance": 0.5,
                "classification_confidence": 0.5,
                "suggested_tags": []
            }
    
    async def generate_matching_insights(self, case_data: Dict, advisor_data: Dict, model: str = None) -> str:
        """Generate AI insights for advisor matching"""
        if not self.client:
            return await self._generate_insights_offline(case_data, advisor_data)
        
        try:
            model_name = self._get_model_name(model)
            
            prompt = f"""
            Explain why this advisor is a good match for this case:
            
            Case Details:
            - Topic: {case_data.get('topic', '')}
            - Subtopic: {case_data.get('subtopic', '')}
            - Query: {case_data.get('query', '')}
            - Complexity: {case_data.get('complexity', 50)}
            
            Advisor Profile:
            - Name: {advisor_data.get('advisor_name', '')}
            - Department: {advisor_data.get('department', '')}
            - Business Function: {advisor_data.get('business_function', '')}
            - Country: {advisor_data.get('country', '')}
            - Total Cases: {advisor_data.get('total_cases_handled', 0)}
            - Avg Resolution Time: {advisor_data.get('avg_resolution_time', 0)} days
            - Expertise Tags: {advisor_data.get('expertise_tags', '')}
            
            Provide a concise, professional explanation (2-3 sentences) of why this advisor is well-suited for this case.
            Focus on specific expertise, experience, and relevant background.
            """
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info(f"Matching insights generated using {model_name}")
            return insights
            
        except Exception as e:
            logger.warning(f"Gateway insights failed: {e}. Using offline fallback.")
            return await self._generate_insights_offline(case_data, advisor_data)
    
    async def _generate_insights_offline(self, case_data: Dict, advisor_data: Dict) -> str:
        """Offline insights generation fallback"""
        try:
            case_topic = case_data.get('topic', '')
            advisor_tags = advisor_data.get('expertise_tags', '')
            advisor_cases = advisor_data.get('total_cases_handled', 0)
            
            insights = []
            
            if case_topic.lower() in advisor_tags.lower():
                insights.append(f"Expertise in {case_topic}")
            
            if advisor_cases >= 5:
                insights.append(f"Experienced advisor with {advisor_cases} cases")
            
            if insights:
                return f"{advisor_data.get('advisor_name', 'Advisor')} is well-suited: {', '.join(insights)}."
            else:
                return f"{advisor_data.get('advisor_name', 'Advisor')} has relevant experience in this domain."
                
        except Exception as e:
            logger.error(f"Offline insights failed: {e}")
            return "Advisor has relevant experience in this domain."
    
    async def generate_profile_summary(self, advisor_data: Dict, model: str = None) -> str:
        """Generate advisor profile summary using AI gateway"""
        if not self.client:
            return await self._generate_profile_summary_offline(advisor_data)
        
        try:
            model_name = self._get_model_name(model)
            
            prompt = f"""
            Create a professional advisor profile summary based on this data:
            
            Advisor Information:
            - Name: {advisor_data.get('advisor_name', '')}
            - Department: {advisor_data.get('department', '')}
            - Business Function: {advisor_data.get('business_function', '')}
            - Country: {advisor_data.get('country', '')}
            - Total Cases Handled: {advisor_data.get('total_cases_handled', 0)}
            - Average Resolution Time: {advisor_data.get('avg_resolution_time', 0)} days
            - Success Rate: {advisor_data.get('success_rate', 0)}%
            - Expertise Tags: {advisor_data.get('expertise_tags', '')}
            - Other Countries: {advisor_data.get('other_countries_handled', '')}
            
            Create a concise, professional summary (2-3 sentences) that highlights:
            - Expertise level and specialization
            - Key areas of focus
            - Performance metrics
            - Geographic coverage
            
            Write in a professional business tone.
            """
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Profile summary generated using {model_name}")
            return summary
            
        except Exception as e:
            logger.warning(f"Gateway profile summary failed: {e}. Using offline fallback.")
            return await self._generate_profile_summary_offline(advisor_data)
    
    async def _generate_profile_summary_offline(self, advisor_data: Dict) -> str:
        """Offline profile summary fallback"""
        try:
            advisor_name = advisor_data.get('advisor_name', '')
            advisor_dept = advisor_data.get('department', '')
            advisor_cases = advisor_data.get('total_cases_handled', 0)
            advisor_resolution = advisor_data.get('avg_resolution_time', 0)
            
            if advisor_cases >= 10:
                expertise_level = "expert"
            elif advisor_cases >= 5:
                expertise_level = "experienced"
            elif advisor_cases >= 3:
                expertise_level = "specialist"
            else:
                expertise_level = "junior"
            
            summary = f"{advisor_name} is a {expertise_level} advisor in {advisor_dept}. "
            summary += f"Handled {advisor_cases} cases with average resolution time of {advisor_resolution:.1f} days."
            
            return summary
            
        except Exception as e:
            logger.error(f"Offline profile summary failed: {e}")
            return f"{advisor_data.get('advisor_name', 'Advisor')} profile generated from case history."
    
    async def analyze_query_similarity(self, query1: str, query2: str, model: str = "text3large") -> float:
        """Analyze query similarity using AI gateway embeddings"""
        if not self.client:
            return await self._analyze_similarity_offline(query1, query2)
        
        try:
            # Get embeddings for both queries
            embedding1 = await self.get_embedding(query1, model)
            embedding2 = await self.get_embedding(query2, model)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            
            logger.info(f"Query similarity analyzed using {model}")
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Gateway similarity analysis failed: {e}. Using offline fallback.")
            return await self._analyze_similarity_offline(query1, query2)
    
    async def _analyze_similarity_offline(self, query1: str, query2: str) -> float:
        """Offline similarity analysis fallback"""
        try:
            if not self.fitted:
                sample_texts = [query1, query2, "sample business query"]
                self.tfidf.fit(sample_texts)
                self.fitted = True
            
            query1_vector = self.tfidf.transform([query1]).toarray()
            query2_vector = self.tfidf.transform([query2]).toarray()
            
            similarity = cosine_similarity(query1_vector, query2_vector)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Offline similarity analysis failed: {e}")
            return 0.0
    
    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models"""
        return self.available_models.copy()
    
    def is_gateway_available(self) -> bool:
        """Check if AI gateway is available"""
        return self.client is not None
