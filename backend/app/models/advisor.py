from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Advisor(Base):
    __tablename__ = "advisors"

    id = Column(Integer, primary_key=True, index=True)
    advisor_id = Column(String, unique=True, index=True)
    advisor_name = Column(String, index=True)
    current_advisory_group = Column(String)
    previous_advisory_group = Column(String)
    department = Column(String, index=True)
    business_function = Column(String, index=True)
    country = Column(String, index=True)
    
    # Performance metrics
    avg_resolution_time = Column(Float, default=0.0)  # in days
    total_cases_handled = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # percentage
    
    # AI-generated profile
    profile_summary = Column(Text)
    expertise_tags = Column(Text)  # JSON string of tags
    complexity_preference = Column(Float, default=50.0)  # 0-100 scale
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignments = relationship("Assignment", back_populates="advisor")
    tags = relationship("Tag", back_populates="advisor")
