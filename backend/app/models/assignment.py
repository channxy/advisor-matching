from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class AssignmentStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TRANSFERRED = "transferred"

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    advisor_id = Column(Integer, ForeignKey("advisors.id"))
    
    # Assignment details
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.PENDING)
    matching_score = Column(Float, default=0.0)  # 0-100 percentage
    matching_insights = Column(Text)  # AI-generated reasoning
    
    # Action tracking
    action_taken_at = Column(DateTime(timezone=True), nullable=True)
    decline_reason = Column(Text, nullable=True)
    transfer_reason = Column(Text, nullable=True)
    
    # Performance tracking
    time_to_accept = Column(Float, nullable=True)  # in hours
    time_to_resolve = Column(Float, nullable=True)  # in days
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    case = relationship("Case", back_populates="assignments")
    advisor = relationship("Advisor", back_populates="assignments")
