from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import Advisor, Case, Assignment, Tag
from .ai_service import AIService
import json
from datetime import datetime, timedelta

class ProfilingService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def update_advisor_profile(self, advisor_id: int, db: Session) -> Dict[str, Any]:
        """Update advisor profile based on recent case history"""
        advisor = db.query(Advisor).filter(Advisor.id == advisor_id).first()
        if not advisor:
            return {}
        
        # Get recent assignments
        recent_assignments = db.query(Assignment).filter(
            Assignment.advisor_id == advisor_id,
            Assignment.status == "accepted"
        ).order_by(Assignment.created_at.desc()).limit(20).all()
        
        if not recent_assignments:
            return {}
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(advisor_id, db)
        
        # Update advisor metrics
        advisor.avg_resolution_time = performance_metrics["avg_resolution_time"]
        advisor.total_cases_handled = performance_metrics["total_cases"]
        advisor.success_rate = performance_metrics["success_rate"]
        
        # Generate new profile summary
        profile_data = await self._generate_profile_summary(advisor, recent_assignments, db)
        
        advisor.profile_summary = profile_data["profile_summary"]
        advisor.complexity_preference = profile_data["complexity_preference"]
        
        # Update tags
        await self._update_advisor_tags(advisor_id, recent_assignments, db)
        
        db.commit()
        
        return {
            "profile_summary": advisor.profile_summary,
            "performance_metrics": performance_metrics,
            "complexity_preference": advisor.complexity_preference
        }
    
    def _calculate_performance_metrics(self, advisor_id: int, db: Session) -> Dict[str, Any]:
        """Calculate advisor performance metrics"""
        # Get resolved cases
        resolved_assignments = db.query(Assignment).filter(
            Assignment.advisor_id == advisor_id,
            Assignment.status == "accepted"
        ).all()
        
        if not resolved_assignments:
            return {
                "avg_resolution_time": 0.0,
                "total_cases": 0,
                "success_rate": 0.0
            }
        
        total_cases = len(resolved_assignments)
        resolution_times = []
        successful_cases = 0
        
        for assignment in resolved_assignments:
            if assignment.time_to_resolve:
                resolution_times.append(assignment.time_to_resolve)
            
            # Consider case successful if resolved within reasonable time
            if assignment.time_to_resolve and assignment.time_to_resolve <= 7:  # 7 days
                successful_cases += 1
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0.0
        success_rate = (successful_cases / total_cases) * 100 if total_cases > 0 else 0.0
        
        return {
            "avg_resolution_time": avg_resolution_time,
            "total_cases": total_cases,
            "success_rate": success_rate
        }
    
    async def _generate_profile_summary(self, advisor: Advisor, assignments: List[Assignment], db: Session) -> Dict[str, Any]:
        """Generate AI-powered profile summary"""
        # Get case details for recent assignments
        case_ids = [assignment.case_id for assignment in assignments]
        cases = db.query(Case).filter(Case.id.in_(case_ids)).all()
        
        # Prepare data for AI analysis
        case_summary = []
        complexity_scores = []
        
        for case in cases:
            case_summary.append(f"{case.topic} - {case.subtopic}")
            complexity_scores.append(case.complexity)
        
        # Calculate average complexity preference
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 50.0
        
        # Generate profile summary using AI
        profile_data = await self.ai_service.update_advisor_profile(
            {
                "advisor_name": advisor.advisor_name,
                "profile_summary": advisor.profile_summary or "",
                "expertise_tags": advisor.expertise_tags or ""
            },
            {
                "topic": ", ".join(set([case.topic for case in cases])),
                "subtopic": ", ".join(set([case.subtopic for case in cases])),
                "complexity": avg_complexity,
                "resolution_time": sum([case.resolution_time or 0 for case in cases]) / len(cases) if cases else 0
            }
        )
        
        return {
            "profile_summary": profile_data["profile_summary"],
            "complexity_preference": profile_data["updated_complexity_preference"]
        }
    
    async def _update_advisor_tags(self, advisor_id: int, assignments: List[Assignment], db: Session) -> None:
        """Update advisor expertise tags based on recent cases"""
        # Get case details
        case_ids = [assignment.case_id for assignment in assignments]
        cases = db.query(Case).filter(Case.id.in_(case_ids)).all()
        
        # Extract topics and subtopics
        topics = {}
        subtopics = {}
        
        for case in cases:
            topics[case.topic] = topics.get(case.topic, 0) + 1
            subtopics[case.subtopic] = subtopics.get(case.subtopic, 0) + 1
        
        # Create or update tags
        for topic, count in topics.items():
            if count >= 2:  # Only tag if handled multiple times
                self._upsert_tag(advisor_id, topic, "topic", count / len(cases), db)
        
        for subtopic, count in subtopics.items():
            if count >= 2:
                self._upsert_tag(advisor_id, subtopic, "subtopic", count / len(cases), db)
    
    def _upsert_tag(self, advisor_id: int, tag_name: str, tag_category: str, confidence: float, db: Session) -> None:
        """Create or update a tag"""
        existing_tag = db.query(Tag).filter(
            Tag.advisor_id == advisor_id,
            Tag.tag_name == tag_name,
            Tag.tag_category == tag_category
        ).first()
        
        if existing_tag:
            existing_tag.usage_count += 1
            existing_tag.confidence_score = max(existing_tag.confidence_score, confidence)
        else:
            new_tag = Tag(
                advisor_id=advisor_id,
                tag_name=tag_name,
                tag_category=tag_category,
                confidence_score=confidence,
                usage_count=1
            )
            db.add(new_tag)
    
    async def get_advisor_learning_curve(self, advisor_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get advisor learning curve data"""
        assignments = db.query(Assignment).filter(
            Assignment.advisor_id == advisor_id,
            Assignment.status == "accepted"
        ).order_by(Assignment.created_at).all()
        
        learning_curve = []
        cumulative_cases = 0
        cumulative_resolution_time = 0
        
        for assignment in assignments:
            cumulative_cases += 1
            if assignment.time_to_resolve:
                cumulative_resolution_time += assignment.time_to_resolve
            
            avg_resolution = cumulative_resolution_time / cumulative_cases if cumulative_cases > 0 else 0
            
            learning_curve.append({
                "case_number": cumulative_cases,
                "avg_resolution_time": avg_resolution,
                "date": assignment.created_at.strftime("%Y-%m-%d")
            })
        
        return learning_curve
