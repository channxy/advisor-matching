from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import tempfile
import os
import shutil
import pandas as pd

from ..models.database import get_db
from ..services.ml_service import MLAdvisorService
from ..services.matching_service import MatchingService

router = APIRouter(prefix="/api/v1", tags=["excel-upload"])

# Initialize services
ml_service = MLAdvisorService()
matching_service = MatchingService()

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
            # Process Excel data using the new comprehensive ML service
            result = await ml_service.process_excel_data(tmp_file_path, db)
            
            return {
                "success": True,
                "message": result['message'],
                "cases_processed": result['cases_processed'],
                "advisors_updated": result['advisors_updated'],
                "model_accuracy": result['model_accuracy'],
                "model_name": "AI Gateway Enhanced Advisor Matching"
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
        
        # Get recommendations using the new AI Gateway ML model
        query_text = f"{case_data.get('topic', '')} {case_data.get('subtopic', '')} {case_data.get('query', '')}"
        ml_recommendations = await ml_service.advisor_matching_ml.predict_advisors(
            query=query_text,
            department=case_data.get('department'),
            business_function=case_data.get('business_function'),
            country=case_data.get('country'),
            complexity=float(case_data.get('complexity', 5.0)),
            db=db
        )
        
        # Also get recommendations using matching service for comparison
        # Create a temporary case object for matching service
        from ..models import Case
        temp_case = Case(
            topic=case_data.get('topic', ''),
            subtopic=case_data.get('subtopic', ''),
            query=case_data.get('query', ''),
            complexity=float(case_data.get('complexity', 50.0)),
            business_function=case_data.get('business_function', ''),
            country=case_data.get('country', '')
        )
        
        matching_recommendations = await matching_service.find_best_advisors(temp_case, db)
        
        # Combine and prioritize recommendations
        recommendations = []
        
        # Add ML recommendations first
        for rec in ml_recommendations:
            recommendations.append({
                'advisor_id': rec['advisor_id'],
                'advisor_name': rec['advisor_name'],
                'confidence': rec['similarity_score'],
                'expertise_tags': rec.get('expertise_tags', ''),
                'success_rate': 0.8,  # Default success rate
                'total_cases': rec['query_count'],
                'matching_reasons': rec.get('reasons', []),
                'source': 'AI Gateway ML Model',
                'match_percentage': rec['match_percentage']
            })
        
        # Add matching service recommendations
        for rec in matching_recommendations:
            advisor = rec['advisor']
            # Check if already in recommendations
            if not any(r['advisor_id'] == advisor.advisor_id for r in recommendations):
                recommendations.append({
                    'advisor_id': advisor.advisor_id,
                    'advisor_name': advisor.advisor_name,
                    'confidence': rec['score'] / 100,  # Convert to 0-1 scale
                    'expertise_tags': advisor.expertise_tags,
                    'success_rate': advisor.success_rate,
                    'total_cases': advisor.total_cases_handled,
                    'source': 'Matching Service',
                    'insights': rec['insights']
                })
        
        # Sort by confidence and take top 3
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        recommendations = recommendations[:3]
        
        return {
            "success": True,
            "case_data": case_data,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.get("/model-performance")
async def get_model_performance():
    """Get ML model performance metrics"""
    try:
        # Get model performance from the new AI Gateway model
        performance_data = ml_service.advisor_matching_ml.get_model_performance()
        
        if performance_data.get('success', False):
            return {
                "success": True,
                "model_name": performance_data.get('model_name', 'AI Gateway Model'),
                "test_score": performance_data.get('test_score', 0.0),
                "train_score": performance_data.get('train_score', 0.0),
                "cv_mean": performance_data.get('cv_mean', 0.0),
                "cv_std": performance_data.get('cv_std', 0.0),
                "feature_importance": performance_data.get('feature_importance', {}),
                "ai_gateway_available": ml_service.advisor_matching_ml.ai_service.is_gateway_available()
            }
        else:
            return {
                "success": False,
                "message": "No model metrics available. Train the model first.",
                "ai_gateway_available": ml_service.advisor_matching_ml.ai_service.is_gateway_available()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model performance: {str(e)}")

@router.post("/retrain-model")
async def retrain_model(
    excel_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Retrain the ML model with new data"""
    try:
        # Validate file type
        if not excel_file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Only Excel (.xlsx) files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            shutil.copyfileobj(excel_file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            # Retrain the comprehensive ML model
            df = pd.read_excel(tmp_file_path)
            ml_result = await ml_service.advisor_matching_ml.retrain_model(tmp_file_path, db)
            
            # Get updated model performance data
            performance_data = ml_service.advisor_matching_ml.get_model_performance()
            
            return {
                "success": True,
                "message": "Model retrained successfully",
                "model_name": performance_data.get('model_name', 'Unknown'),
                "test_score": performance_data.get('test_score', 0.0),
                "train_score": performance_data.get('train_score', 0.0),
                "cv_mean": performance_data.get('cv_mean', 0.0),
                "cv_std": performance_data.get('cv_std', 0.0),
                "feature_importance": performance_data.get('feature_importance', {})
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retraining model: {str(e)}")

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
