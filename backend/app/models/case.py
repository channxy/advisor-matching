from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DECLINED = "declined"

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True)
    topic = Column(String, index=True)
    subtopic = Column(String, index=True)
    query = Column(Text)
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING)
    complexity = Column(Float, default=50.0)  # 0-100 scale
    
    # Case details
    casetype = Column(String)
    transaction_type = Column(String)
    business_function = Column(String, index=True)
    country = Column(String, index=True)
    
    # Timestamps
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_resolved = Column(DateTime(timezone=True), nullable=True)
    resolution_time = Column(Float, nullable=True)  # in days
    
    # AI classification
    domain_relevance = Column(Float, default=0.0)
    classification_confidence = Column(Float, default=0.0)
    
    # Relationships
    assignments = relationship("Assignment", back_populates="case")
