from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    advisor_id = Column(Integer, ForeignKey("advisors.id"))
    tag_name = Column(String, index=True)
    tag_category = Column(String, index=True)  # e.g., "topic", "skill", "domain"
    confidence_score = Column(Float, default=0.0)  # 0-1 scale
    usage_count = Column(Integer, default=1)  # how many times this tag was relevant
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    advisor = relationship("Advisor", back_populates="tags")
