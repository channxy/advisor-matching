from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from ..models.database import get_db
from ..models import Case, CaseStatus
from ..schemas.case import CaseCreate, CaseResponse, CaseListResponse
from ..services.matching_service import MatchingService
from ..services.ai_service import AIService

router = APIRouter(prefix="/cases", tags=["cases"])
matching_service = MatchingService()
ai_service = AIService()

@router.post("/submit_case", response_model=CaseResponse)
async def submit_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    """Submit a new case and find matching advisors"""
    # Generate unique case ID
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    
    # Classify case using AI
    classification = await ai_service.classify_case(
        case_data.query, case_data.topic, case_data.subtopic
    )
    
    # Create case
    case = Case(
        case_id=case_id,
        topic=case_data.topic,
        subtopic=case_data.subtopic,
        query=case_data.query,
        casetype=case_data.casetype,
        transaction_type=case_data.transaction_type,
        business_function=case_data.business_function,
        country=case_data.country,
        complexity=classification["complexity_score"],
        domain_relevance=classification["domain_relevance"],
        classification_confidence=classification["classification_confidence"]
    )
    
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Find matching advisors
    matches = await matching_service.find_best_advisors(case, db)
    
    # Create assignments for top matches
    if matches:
        await matching_service.create_assignments(case, matches, db)
    
    return case

@router.get("/", response_model=CaseListResponse)
async def get_cases(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[CaseStatus] = None,
    topic: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated list of cases with filters"""
    query = db.query(Case)
    
    # Apply filters
    if status:
        query = query.filter(Case.status == status)
    if topic:
        query = query.filter(Case.topic.ilike(f"%{topic}%"))
    if country:
        query = query.filter(Case.country.ilike(f"%{country}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    cases = query.offset((page - 1) * size).limit(size).all()
    
    return CaseListResponse(
        cases=cases,
        total=total,
        page=page,
        size=size,
        total_pages=(total + size - 1) // size
    )

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get case details by case_id"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}/resolve")
async def resolve_case(
    case_id: str,
    resolution_time: float,
    db: Session = Depends(get_db)
):
    """Mark case as resolved and update metrics"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = CaseStatus.RESOLVED
    case.date_resolved = datetime.utcnow()
    case.resolution_time = resolution_time
    
    db.commit()
    db.refresh(case)
    
    return {"message": "Case resolved successfully"}
