from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.assignment import AssignmentStatus

class AssignmentCreate(BaseModel):
    case_id: int
    advisor_id: int
    matching_score: float
    matching_insights: str

class AssignmentAction(BaseModel):
    action: str  # "accept" or "decline"
    reason: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: int
    case_id: int
    advisor_id: int
    status: AssignmentStatus
    matching_score: float
    matching_insights: str
    action_taken_at: Optional[datetime]
    decline_reason: Optional[str]
    transfer_reason: Optional[str]
    time_to_accept: Optional[float]
    time_to_resolve: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
