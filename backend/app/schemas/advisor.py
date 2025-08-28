from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .tag import TagResponse

class AdvisorResponse(BaseModel):
    id: int
    advisor_id: str
    advisor_name: str
    current_advisory_group: str
    previous_advisory_group: Optional[str]
    department: str
    business_function: str
    country: str
    avg_resolution_time: float
    total_cases_handled: int
    success_rate: float
    profile_summary: Optional[str]
    expertise_tags: Optional[str]
    complexity_preference: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AdvisorListResponse(BaseModel):
    advisors: List[AdvisorResponse]
    total: int

class AdvisorDashboardResponse(BaseModel):
    advisor: AdvisorResponse
    incoming_cases: List[dict]
    resolved_cases: List[dict]
    performance_metrics: dict
    recent_activity: List[dict]
    tags: List[TagResponse]
