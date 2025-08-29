from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.case import CaseStatus

class CaseCreate(BaseModel):
    topic: str
    subtopic: str
    query: str
    casetype: Optional[str] = None
    transaction_type: Optional[str] = None
    business_function: Optional[str] = None
    country: Optional[str] = None

class CaseUpdate(BaseModel):
    status: Optional[CaseStatus] = None
    complexity: Optional[float] = None
    date_resolved: Optional[datetime] = None

class CaseResponse(BaseModel):
    id: int
    case_id: str
    topic: str
    subtopic: str
    query: str
    status: CaseStatus
    complexity: float
    casetype: Optional[str]
    transaction_type: Optional[str]
    business_function: Optional[str]
    country: Optional[str]
    date_created: datetime
    date_resolved: Optional[datetime]
    resolution_time: Optional[float]
    domain_relevance: float
    classification_confidence: float

    class Config:
        from_attributes = True

class AssignedAdvisor(BaseModel):
    advisor_id: Optional[str] = None
    advisor_name: Optional[str] = None

class CaseWithAssignmentResponse(BaseModel):
    id: int
    case_id: str
    topic: str
    subtopic: str
    query: str
    status: str
    complexity: float
    casetype: Optional[str]
    transaction_type: Optional[str]
    business_function: Optional[str]
    country: Optional[str]
    date_created: Optional[str]
    date_resolved: Optional[str]
    resolution_time: Optional[float]
    domain_relevance: float
    classification_confidence: float
    assigned_advisor: Optional[AssignedAdvisor] = None
    assignment_status: Optional[str] = None
    matching_score: Optional[float] = None

class CaseListResponse(BaseModel):
    cases: List[CaseWithAssignmentResponse]
    total: int
    page: int
    size: int
    total_pages: int
