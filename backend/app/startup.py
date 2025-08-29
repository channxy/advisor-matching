import os
import logging
from sqlalchemy.orm import Session
from .models.database import SessionLocal
from .services.excel_processor import ExcelProcessor

logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with sample Excel data if no advisors exist"""
    try:
        db = SessionLocal()
        
        # Check if advisors already exist
        from .models import Advisor
        existing_advisors = db.query(Advisor).count()
        
        if existing_advisors == 0:
            logger.info("No advisors found in database. Initializing with sample Excel data...")
            
            # Check if sample Excel file exists
            sample_file = "sample_transactions.xlsx"
            if os.path.exists(sample_file):
                # Process the sample Excel file
                excel_processor = ExcelProcessor()
                result = excel_processor.process_excel_and_generate_profiles(sample_file, db)
                
                logger.info(f"Database initialized with {result['advisors_created']} advisors from Excel data")
                logger.info(f"Created {result['cases_created']} cases and {result['assignments_created']} assignments")
            else:
                logger.warning(f"Sample Excel file {sample_file} not found. Database will be empty.")
        else:
            logger.info(f"Database already contains {existing_advisors} advisors. Skipping initialization.")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        db.close()
