import openai
import os
import json
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
        
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API"""
        if not self.client:
            return [0.0] * 1536  # Default embedding size
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return [0.0] * 1536  # Default embedding size
    
    async def classify_case(self, query: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """Classify case complexity and domain relevance"""
        if not self.client:
            return {
                "complexity_score": 50.0,
                "domain_relevance": 0.5,
                "classification_confidence": 0.5,
                "suggested_tags": []
            }
        
        try:
            prompt = f"""
            Analyze this case and provide classification:
            
            Topic: {topic}
            Subtopic: {subtopic}
            Query: {query}
            
            Provide a JSON response with:
            - complexity_score: 0-100 scale
            - domain_relevance: 0-1 scale
            - classification_confidence: 0-1 scale
            - suggested_tags: list of relevant expertise tags
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error classifying case: {e}")
            return {
                "complexity_score": 50.0,
                "domain_relevance": 0.5,
                "classification_confidence": 0.5,
                "suggested_tags": []
            }
    
    async def generate_matching_insights(self, case_data: Dict, advisor_data: Dict) -> str:
        """Generate AI insights for why an advisor matches a case"""
        if not self.client:
            return "Advisor has relevant experience in this domain."
        
        try:
            prompt = f"""
            Explain why this advisor is a good match for this case:
            
            Case: {case_data['topic']} - {case_data['subtopic']}
            Query: {case_data['query']}
            Complexity: {case_data['complexity']}
            
            Advisor: {advisor_data['advisor_name']}
            Department: {advisor_data['department']}
            Business Function: {advisor_data['business_function']}
            Country: {advisor_data['country']}
            Past Cases: {advisor_data['total_cases_handled']}
            Avg Resolution: {advisor_data['avg_resolution_time']} days
            Tags: {advisor_data.get('expertise_tags', '')}
            
            Provide a concise explanation (2-3 sentences) of why this advisor is well-suited for this case.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating insights: {e}")
            return "Advisor has relevant experience in this domain."
    
    async def update_advisor_profile(self, advisor_data: Dict, new_case_data: Dict) -> Dict[str, Any]:
        """Update advisor profile based on new case resolution"""
        if not self.client:
            return {
                "profile_summary": advisor_data.get('profile_summary', ''),
                "new_tags": [],
                "updated_complexity_preference": advisor_data.get('complexity_preference', 50.0)
            }
        
        try:
            prompt = f"""
            Update advisor profile based on new case resolution:
            
            Advisor: {advisor_data['advisor_name']}
            Current Profile: {advisor_data.get('profile_summary', '')}
            Current Tags: {advisor_data.get('expertise_tags', '')}
            
            New Case Resolved:
            Topic: {new_case_data['topic']}
            Subtopic: {new_case_data['subtopic']}
            Complexity: {new_case_data['complexity']}
            Resolution Time: {new_case_data['resolution_time']} days
            
            Provide updated:
            - profile_summary: Updated advisor profile
            - new_tags: List of new expertise tags to add
            - updated_complexity_preference: 0-100 scale
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error updating profile: {e}")
            return {
                "profile_summary": advisor_data.get('profile_summary', ''),
                "new_tags": [],
                "updated_complexity_preference": advisor_data.get('complexity_preference', 50.0)
            }
