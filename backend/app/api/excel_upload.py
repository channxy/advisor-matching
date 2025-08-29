from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import tempfile
import os
import shutil
import pandas as pd

from ..models.database import get_db
from ..services.excel_processor import ExcelProcessor
from ..services.ml_service import MLAdvisorService

router = APIRouter(prefix="/api/v1", tags=["excel-upload"])

# Initialize services
excel_processor = ExcelProcessor()
ml_service = MLAdvisorService()

@router.post("/upload-excel")
async def upload_excel_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload Excel file with transaction data and process advisor profiles"""
    try:
        # Validate file type
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Only Excel (.xlsx) files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            # Process Excel data and generate advisor profiles
            result = excel_processor.process_excel_and_generate_profiles(tmp_file_path, db)
            
            # Train ML model on the processed data
            ml_result = ml_service._train_model(pd.read_excel(tmp_file_path), db)
            
            return {
                "success": True,
                "message": result['message'],
                "cases_created": result['cases_created'],
                "advisors_created": result['advisors_created'],
                "assignments_created": result['assignments_created'],
                "model_accuracy": ml_result.get('accuracy', 0.0)
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/recommend-advisors")
async def get_advisor_recommendations(
    case_data: Dict,
    db: Session = Depends(get_db)
):
    """Get AI-powered advisor recommendations for a new case"""
    try:
        # Validate required fields
        required_fields = ['topic', 'subtopic', 'query']
        for field in required_fields:
            if field not in case_data or not case_data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get recommendations
        recommendations = ml_service.recommend_advisors(case_data, db)
        
        return {
            "success": True,
            "case_data": case_data,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.post("/update-advisor-profile")
async def update_advisor_profile(
    advisor_id: str,
    case_data: Dict,
    db: Session = Depends(get_db)
):
    """Update advisor profile after case completion"""
    try:
        ml_service.update_advisor_profile(advisor_id, case_data, db)
        
        return {
            "success": True,
            "message": f"Advisor profile updated for {advisor_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating advisor profile: {str(e)}")

@router.get("/advisor-inbox/{advisor_id}")
async def get_advisor_inbox(
    advisor_id: str,
    db: Session = Depends(get_db)
):
    """Get advisor's inbox with AI-matched cases"""
    try:
        from ..models import Advisor, Case, Assignment
        
        # Get advisor
        advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
        if not advisor:
            raise HTTPException(status_code=404, detail="Advisor not found")
        
        # Get assigned cases
        assignments = db.query(Assignment).filter(Assignment.advisor_id == advisor.id).all()
        
        inbox_cases = []
        for assignment in assignments:
            case = assignment.case
            inbox_cases.append({
                "case_id": case.case_id,
                "topic": case.topic,
                "subtopic": case.subtopic,
                "query": case.query,
                "status": case.status.value,
                "complexity": case.complexity,
                "business_function": case.business_function,
                "country": case.country,
                "date_created": case.date_created.isoformat() if case.date_created else None,
                "matching_score": assignment.matching_score if hasattr(assignment, 'matching_score') else 0.0
            })
        
        return {
            "success": True,
            "advisor": {
                "advisor_id": advisor.advisor_id,
                "advisor_name": advisor.advisor_name,
                "expertise_tags": advisor.expertise_tags,
                "success_rate": advisor.success_rate,
                "total_cases": advisor.total_cases_handled
            },
            "inbox_cases": inbox_cases,
            "total_cases": len(inbox_cases)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching advisor inbox: {str(e)}")
