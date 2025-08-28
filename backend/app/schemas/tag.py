from pydantic import BaseModel
from datetime import datetime

class TagResponse(BaseModel):
    id: int
    advisor_id: int
    tag_name: str
    tag_category: str
    confidence_score: float
    usage_count: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
