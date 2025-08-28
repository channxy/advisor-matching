from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.database import get_db
from ..models import Assignment, Case, AssignmentStatus
from ..schemas.assignment import AssignmentAction, AssignmentResponse

router = APIRouter(prefix="/assignments", tags=["assignments"])

@router.post("/case/{case_id}/accept")
async def accept_case(
    case_id: str,
    advisor_id: str,
    db: Session = Depends(get_db)
):
    """Accept a case assignment"""
    # Find the assignment
    assignment = db.query(Assignment).join(Case).filter(
        Case.case_id == case_id,
        Assignment.advisor_id == db.query(Assignment.advisor_id).filter(
            Assignment.advisor_id == advisor_id
        ).scalar()
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.status != AssignmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Assignment is not pending")
    
    # Update assignment
    assignment.status = AssignmentStatus.ACCEPTED
    assignment.action_taken_at = datetime.utcnow()
    
    # Update case status
    case = db.query(Case).filter(Case.id == assignment.case_id).first()
    if case:
        case.status = "assigned"
    
    # Calculate time to accept
    time_diff = (assignment.action_taken_at - assignment.created_at).total_seconds() / 3600
    assignment.time_to_accept = time_diff
    
    db.commit()
    
    return {"message": "Case accepted successfully"}

@router.post("/case/{case_id}/decline")
async def decline_case(
    case_id: str,
    advisor_id: str,
    action: AssignmentAction,
    db: Session = Depends(get_db)
):
    """Decline a case assignment"""
    # Find the assignment
    assignment = db.query(Assignment).join(Case).filter(
        Case.case_id == case_id,
        Assignment.advisor_id == db.query(Assignment.advisor_id).filter(
            Assignment.advisor_id == advisor_id
        ).scalar()
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.status != AssignmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Assignment is not pending")
    
    if not action.reason:
        raise HTTPException(status_code=400, detail="Decline reason is required")
    
    # Update assignment
    assignment.status = AssignmentStatus.DECLINED
    assignment.action_taken_at = datetime.utcnow()
    assignment.decline_reason = action.reason
    
    db.commit()
    
    return {"message": "Case declined successfully"}

@router.get("/case/{case_id}")
async def get_case_assignments(case_id: str, db: Session = Depends(get_db)):
    """Get all assignments for a case"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    assignments = db.query(Assignment).filter(Assignment.case_id == case.id).all()
    return {"assignments": assignments}
