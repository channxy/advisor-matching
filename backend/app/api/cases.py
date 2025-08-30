from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from ..models.database import get_db
from ..models import Case, CaseStatus
from ..schemas.case import CaseCreate, CaseResponse, CaseListResponse, CaseWithAssignmentResponse
from ..services.matching_service import MatchingService
from ..services.ai_service_gateway import AIServiceGateway as AIService

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
    """Get paginated list of cases with filters and assigned advisor information"""
    from ..models import Assignment, Advisor
    
    # Start with case query
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
    
    # Get assigned advisor information for each case
    cases_with_assignments = []
    for case in cases:
        # Find accepted assignment for this case
        accepted_assignment = db.query(Assignment, Advisor).join(
            Advisor, Assignment.advisor_id == Advisor.id
        ).filter(
            Assignment.case_id == case.id,
            Assignment.status == "ACCEPTED"
        ).first()
        

        
        case_dict = {
            "id": case.id,
            "case_id": case.case_id,
            "topic": case.topic,
            "subtopic": case.subtopic,
            "query": case.query,
            "status": case.status.value if hasattr(case.status, 'value') else case.status,
            "complexity": case.complexity,
            "casetype": case.casetype,
            "transaction_type": case.transaction_type,
            "business_function": case.business_function,
            "country": case.country,
            "date_created": case.date_created.isoformat() if case.date_created else None,
            "date_resolved": case.date_resolved.isoformat() if case.date_resolved else None,
            "resolution_time": case.resolution_time,
            "domain_relevance": case.domain_relevance,
            "classification_confidence": case.classification_confidence,
            "assigned_advisor": {
                "advisor_id": accepted_assignment[1].advisor_id if accepted_assignment else None,
                "advisor_name": accepted_assignment[1].advisor_name if accepted_assignment else None
            } if accepted_assignment else None
        }
        cases_with_assignments.append(case_dict)
    
    return CaseListResponse(
        cases=cases_with_assignments,
        total=total,
        page=page,
        size=size,
        total_pages=(total + size - 1) // size
    )

@router.get("/advisor/{advisor_id}", response_model=CaseListResponse)
async def get_advisor_cases(
    advisor_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[CaseStatus] = None,
    db: Session = Depends(get_db)
):
    """Get cases assigned to a specific advisor"""
    from ..models import Assignment, Advisor
    
    # First verify the advisor exists
    advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    
    # Get cases that have assignments for this advisor
    query = db.query(Case).join(Assignment, Case.id == Assignment.case_id).filter(
        Assignment.advisor_id == advisor.id
    )
    
    # Apply status filter if provided
    if status:
        query = query.filter(Case.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    cases = query.offset((page - 1) * size).limit(size).all()
    
    # Get assignment details for each case
    cases_with_assignments = []
    for case in cases:
        # Get the specific assignment for this advisor and case
        assignment = db.query(Assignment).filter(
            Assignment.case_id == case.id,
            Assignment.advisor_id == advisor.id
        ).first()
        
        case_dict = {
            "id": case.id,
            "case_id": case.case_id,
            "topic": case.topic,
            "subtopic": case.subtopic,
            "query": case.query,
            "status": case.status.value if hasattr(case.status, 'value') else case.status,
            "complexity": case.complexity,
            "casetype": case.casetype,
            "transaction_type": case.transaction_type,
            "business_function": case.business_function,
            "country": case.country,
            "date_created": case.date_created.isoformat() if case.date_created else None,
            "date_resolved": case.date_resolved.isoformat() if case.date_resolved else None,
            "resolution_time": case.resolution_time,
            "domain_relevance": case.domain_relevance,
            "classification_confidence": case.classification_confidence,
            "assignment_status": assignment.status if assignment else None,
            "matching_score": assignment.matching_score if assignment else None,
            "assigned_advisor": {
                "advisor_id": advisor.advisor_id,
                "advisor_name": advisor.advisor_name
            }
        }
        cases_with_assignments.append(case_dict)
    
    return CaseListResponse(
        cases=cases_with_assignments,
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
