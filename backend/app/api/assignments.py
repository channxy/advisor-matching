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
    from ..models import Advisor
    
    # Find the case first
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get advisor information first
    advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    
    # Find the assignment for this case and advisor (using advisor's database ID)
    assignment = db.query(Assignment).filter(
        Assignment.case_id == case.id,
        Assignment.advisor_id == advisor.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.status != AssignmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Assignment is not pending")
    
    # Update assignment
    assignment.status = AssignmentStatus.ACCEPTED
    assignment.action_taken_at = datetime.utcnow()
    
    # Calculate time to accept
    if assignment.created_at:
        time_diff = (assignment.action_taken_at - assignment.created_at).total_seconds() / 3600
        assignment.time_to_accept = time_diff
    
    # Update case status to assigned
    case.status = "assigned"
    
    # Update all other assignments for this case to declined (optional - you might want to keep them pending)
    other_assignments = db.query(Assignment).filter(
        Assignment.case_id == case.id,
        Assignment.advisor_id != advisor.id,
        Assignment.status == AssignmentStatus.PENDING
    ).all()
    
    for other_assignment in other_assignments:
        other_assignment.status = AssignmentStatus.DECLINED
        other_assignment.decline_reason = f"Case accepted by {advisor.advisor_name}"
    
    db.commit()
    
    return {
        "message": "Case accepted successfully",
        "case_id": case_id,
        "advisor_id": advisor_id,
        "advisor_name": advisor.advisor_name,
        "new_status": "assigned"
    }

@router.post("/case/{case_id}/decline")
async def decline_case(
    case_id: str,
    advisor_id: str,
    action: AssignmentAction,
    db: Session = Depends(get_db)
):
    """Decline a case assignment"""
    from ..models import Advisor
    
    # Find the case first
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get advisor information first
    advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    
    # Find the assignment for this case and advisor (using advisor's database ID)
    assignment = db.query(Assignment).filter(
        Assignment.case_id == case.id,
        Assignment.advisor_id == advisor.id
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
    
    return {
        "message": "Case declined successfully",
        "case_id": case_id,
        "advisor_id": advisor_id,
        "advisor_name": advisor.advisor_name,
        "reason": action.reason
    }

@router.get("/case/{case_id}")
async def get_case_assignments(case_id: str, db: Session = Depends(get_db)):
    """Get all assignments for a case with advisor information"""
    from ..models import Advisor
    
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get assignments with advisor information
    assignments = db.query(Assignment, Advisor).join(
        Advisor, Assignment.advisor_id == Advisor.id
    ).filter(Assignment.case_id == case.id).all()
    
    # Format the response
    formatted_assignments = []
    for assignment, advisor in assignments:
        formatted_assignments.append({
            "id": assignment.id,
            "case_id": assignment.case_id,
            "advisor_id": assignment.advisor_id,
            "advisor_name": advisor.advisor_name,
            "advisor_expertise": advisor.expertise_tags,
            "matching_score": assignment.matching_score,
            "matching_insights": assignment.matching_insights,
            "status": assignment.status.value if hasattr(assignment.status, 'value') else assignment.status,
            "action_taken_at": assignment.action_taken_at.isoformat() if assignment.action_taken_at else None,
            "time_to_accept": assignment.time_to_accept,
            "time_to_resolve": assignment.time_to_resolve,
            "decline_reason": assignment.decline_reason,
            "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
            "updated_at": assignment.updated_at.isoformat() if assignment.updated_at else None
        })
    
    return {"assignments": formatted_assignments}
