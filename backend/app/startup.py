import os
import logging
from sqlalchemy.orm import Session
from .models.database import SessionLocal

logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database - no automatic sample data creation"""
    try:
        db = SessionLocal()
        
        # Check if advisors already exist
        from .models import Advisor
        existing_advisors = db.query(Advisor).count()
        
        if existing_advisors == 0:
            logger.info("Database is empty. Upload Excel file to create advisor profiles.")
        else:
            logger.info(f"Database contains {existing_advisors} advisors.")
            
    except Exception as e:
        logger.error(f"Error checking database: {e}")
    finally:
        db.close()
