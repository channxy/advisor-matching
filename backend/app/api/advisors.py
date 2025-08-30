from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.database import get_db
from ..models import Advisor, Assignment, Case, Tag
from ..schemas.advisor import AdvisorResponse, AdvisorListResponse, AdvisorDashboardResponse
router = APIRouter(prefix="/advisors", tags=["advisors"])

@router.get("/", response_model=AdvisorListResponse)
async def get_advisors(
    department: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of advisors with optional filters"""
    query = db.query(Advisor)
    
    if department:
        query = query.filter(Advisor.department.ilike(f"%{department}%"))
    if country:
        query = query.filter(Advisor.country.ilike(f"%{country}%"))
    
    advisors = query.all()
    return AdvisorListResponse(advisors=advisors, total=len(advisors))

@router.get("/{advisor_id}", response_model=AdvisorResponse)
async def get_advisor(advisor_id: str, db: Session = Depends(get_db)):
    """Get advisor details by advisor_id"""
    advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    return advisor

@router.get("/dashboard/{advisor_id}", response_model=AdvisorDashboardResponse)
async def get_advisor_dashboard(advisor_id: str, db: Session = Depends(get_db)):
    """Get advisor dashboard data"""
    advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    
    # Get incoming cases (pending assignments)
    incoming_assignments = db.query(Assignment).filter(
        Assignment.advisor_id == advisor.id,
        Assignment.status == "pending"
    ).all()
    
    incoming_cases = []
    for assignment in incoming_assignments:
        case = db.query(Case).filter(Case.id == assignment.case_id).first()
        if case:
            incoming_cases.append({
                "case_id": case.case_id,
                "topic": case.topic,
                "subtopic": case.subtopic,
                "date_created": case.date_created,
                "matching_score": assignment.matching_score,
                "matching_insights": assignment.matching_insights
            })
    
    # Get resolved cases (last 10)
    resolved_assignments = db.query(Assignment).filter(
        Assignment.advisor_id == advisor.id,
        Assignment.status == "accepted"
    ).order_by(Assignment.created_at.desc()).limit(10).all()
    
    resolved_cases = []
    for assignment in resolved_assignments:
        case = db.query(Case).filter(Case.id == assignment.case_id).first()
        if case:
            resolved_cases.append({
                "case_id": case.case_id,
                "topic": case.topic,
                "subtopic": case.subtopic,
                "date_resolved": case.date_resolved,
                "resolution_time": case.resolution_time
            })
    
    # Get performance metrics
    performance_metrics = {
        "avg_resolution_time": advisor.avg_resolution_time,
        "total_cases_handled": advisor.total_cases_handled,
        "success_rate": advisor.success_rate,
        "pending_cases": len(incoming_cases)
    }
    
    # Get recent activity
    recent_activity = []
    all_assignments = db.query(Assignment).filter(
        Assignment.advisor_id == advisor.id
    ).order_by(Assignment.created_at.desc()).limit(5).all()
    
    for assignment in all_assignments:
        case = db.query(Case).filter(Case.id == assignment.case_id).first()
        if case:
            recent_activity.append({
                "action": assignment.status,
                "case_id": case.case_id,
                "topic": case.topic,
                "date": assignment.created_at
            })
    
    # Get tags
    tags = db.query(Tag).filter(Tag.advisor_id == advisor.id).all()
    
    return AdvisorDashboardResponse(
        advisor=advisor,
        incoming_cases=incoming_cases,
        resolved_cases=resolved_cases,
        performance_metrics=performance_metrics,
        recent_activity=recent_activity,
        tags=tags
    )


