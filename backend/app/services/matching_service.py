from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import Advisor, Case, Assignment, Tag
from .ai_service import AIService
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MatchingService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def find_best_advisors(self, case: Case, db: Session, limit: int = 3) -> List[Dict[str, Any]]:
        """Find best advisors for a case using AI matching"""
        # Get all active advisors
        advisors = db.query(Advisor).all()
        
        if not advisors:
            return []
        
        # Calculate matching scores for each advisor
        matches = []
        for advisor in advisors:
            score, insights = await self._calculate_match_score(case, advisor, db)
            matches.append({
                "advisor": advisor,
                "score": score,
                "insights": insights
            })
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:limit]
    
    async def _calculate_match_score(self, case: Case, advisor: Advisor, db: Session) -> tuple[float, str]:
        """Calculate matching score between case and advisor"""
        score = 0.0
        
        # 1. Topic/domain matching (30%)
        topic_score = self._calculate_topic_match(case, advisor, db)
        score += topic_score * 0.3
        
        # 2. Complexity preference matching (25%)
        complexity_score = self._calculate_complexity_match(case, advisor)
        score += complexity_score * 0.25
        
        # 3. Geographic matching (15%)
        geo_score = self._calculate_geographic_match(case, advisor)
        score += geo_score * 0.15
        
        # 4. Performance-based matching (20%)
        performance_score = self._calculate_performance_match(advisor)
        score += performance_score * 0.2
        
        # 5. Availability/workload matching (10%)
        workload_score = self._calculate_workload_match(advisor, db)
        score += workload_score * 0.1
        
        # Generate AI insights
        insights = await self.ai_service.generate_matching_insights(
            {
                "topic": case.topic,
                "subtopic": case.subtopic,
                "query": case.query,
                "complexity": case.complexity,
                "country": case.country
            },
            {
                "advisor_name": advisor.advisor_name,
                "department": advisor.department,
                "business_function": advisor.business_function,
                "country": advisor.country,
                "total_cases_handled": advisor.total_cases_handled,
                "avg_resolution_time": advisor.avg_resolution_time,
                "expertise_tags": advisor.expertise_tags
            }
        )
        
        return min(score, 100.0), insights
    
    def _calculate_topic_match(self, case: Case, advisor: Advisor, db: Session) -> float:
        """Calculate topic/domain matching score"""
        # Get advisor's tags
        advisor_tags = db.query(Tag).filter(Tag.advisor_id == advisor.id).all()
        advisor_tag_names = [tag.tag_name.lower() for tag in advisor_tags]
        
        # Check if case topic/subtopic matches advisor tags
        case_text = f"{case.topic} {case.subtopic}".lower()
        
        matches = 0
        for tag in advisor_tag_names:
            if tag in case_text or any(word in case_text for word in tag.split()):
                matches += 1
        
        if advisor_tag_names:
            return min(matches / len(advisor_tag_names) * 100, 100)
        return 50.0  # Default score if no tags
    
    def _calculate_complexity_match(self, case: Case, advisor: Advisor) -> float:
        """Calculate complexity preference matching"""
        complexity_diff = abs(case.complexity - advisor.complexity_preference)
        # Lower difference = higher score
        return max(100 - complexity_diff, 0)
    
    def _calculate_geographic_match(self, case: Case, advisor: Advisor) -> float:
        """Calculate geographic matching score"""
        if case.country and advisor.country:
            if case.country.lower() == advisor.country.lower():
                return 100.0
            # Could add region-based matching here
        return 50.0  # Default score
    
    def _calculate_performance_match(self, advisor: Advisor) -> float:
        """Calculate performance-based matching score"""
        # Higher success rate and lower resolution time = better score
        success_score = advisor.success_rate
        resolution_score = max(100 - advisor.avg_resolution_time * 10, 0)  # Penalize long resolution times
        
        return (success_score + resolution_score) / 2
    
    def _calculate_workload_match(self, advisor: Advisor, db: Session) -> float:
        """Calculate workload/availability matching"""
        # Count pending assignments
        pending_assignments = db.query(Assignment).filter(
            Assignment.advisor_id == advisor.id,
            Assignment.status == "pending"
        ).count()
        
        # Lower workload = higher score
        return max(100 - pending_assignments * 10, 0)
    
    async def create_assignments(self, case: Case, matches: List[Dict], db: Session) -> List[Assignment]:
        """Create assignments for top matching advisors"""
        assignments = []
        
        for match in matches:
            assignment = Assignment(
                case_id=case.id,
                advisor_id=match["advisor"].id,
                matching_score=match["score"],
                matching_insights=match["insights"],
                status="pending"
            )
            db.add(assignment)
            assignments.append(assignment)
        
        db.commit()
        return assignments
