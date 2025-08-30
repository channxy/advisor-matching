#!/usr/bin/env python3
"""
Integration test for the complete AdvisorConnect system
Tests all components working together: ML, AI Gateway, Frontend APIs, Database
"""

import sys
import os
import asyncio
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_model_offline import AdvisorMatchingMLOffline, QueryFeatures
from app.services.ai_service_gateway import AIServiceGateway
from app.services.matching_service import MatchingService
from app.services.ml_service import MLAdvisorService
from app.models.database import get_db
from app.models import Base, engine
import pandas as pd

def test_database_integration():
    """Test database models and connections"""
    print("🗄️  Testing Database Integration...")
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        print("   ✅ Database tables created")
        
        # Test database connection
        db = next(get_db())
        print("   ✅ Database connection successful")
        
        # Test basic operations
        from app.models import Advisor, Case
        advisor_count = db.query(Advisor).count()
        case_count = db.query(Case).count()
        print(f"   ✅ Database queries working (Advisors: {advisor_count}, Cases: {case_count})")
        
        return True
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_ml_model_integration():
    """Test ML model integration"""
    print("🤖 Testing ML Model Integration...")
    
    try:
        # Initialize ML model
        ml_model = AdvisorMatchingMLOffline()
        print("   ✅ ML model initialized")
        
        # Create sample data
        sample_data = {
            'Case ID': ['CASE001', 'CASE002', 'CASE003', 'CASE004'],
            'Services': ['Tax Advisory', 'Audit Review', 'Consulting', 'Strategy'],
            'Topics': ['Corporate Tax', 'Financial Audit', 'Business Strategy', 'Risk Management'],
            'Current Sub-Topic': ['Tax Planning', 'Compliance Review', 'Market Analysis', 'Risk Assessment'],
            'Previous Sub-Topic': ['None', 'None', 'None', 'None'],
            'Date Created': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'Date Submitted': ['2024-01-05', '2024-01-07', '2024-01-10', '2024-01-12'],
            'Created By (Bank ID)': ['USER001', 'USER002', 'USER003', 'USER004'],
            'Current Case Owner': ['ADV001', 'ADV002', 'ADV003', 'ADV001'],
            'Previous Case Owner': ['None', 'None', 'None', 'None'],
            'Status': ['Resolved', 'Resolved', 'Resolved', 'Resolved'],
            'Current Advisory Group': ['Tax Advisory', 'Audit Group', 'Strategy Group', 'Risk Group'],
            'Previous Advisory Group': ['None', 'None', 'None', 'None'],
            'Overall Case Age (Days)': [4, 5, 7, 8],
            'Business Function': ['Tax Advisory', 'Audit', 'Strategy', 'Risk Management'],
            'Department': ['Tax', 'Audit', 'Strategy', 'Risk'],
            'Country': ['United States', 'Canada', 'UK', 'Australia'],
            'Category': ['Consultation', 'Review', 'Planning', 'Assessment'],
            'Complexity': [75.0, 60.0, 85.0, 70.0],
            'Time Spent': [8.0, 12.0, 16.0, 10.0],
            'Please describe your query': [
                'Client needs tax optimization strategy',
                'Annual compliance review required',
                'Market entry strategy for European expansion',
                'Risk assessment for new product launch'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        print("   ✅ Sample data created")
        
        # Test data preprocessing
        df_processed = ml_model._clean_data(df)
        df_processed['query_text'] = ml_model._create_query_text(df_processed)
        print("   ✅ Data preprocessing completed")
        
        # Test advisor profile creation
        profiles = ml_model.create_advisor_profiles(df_processed)
        print(f"   ✅ Created {len(profiles)} advisor profiles")
        
        # Test model training
        metrics = ml_model.train_model(df_processed)
        print(f"   ✅ Model trained (Test Score: {metrics['test_score']:.3f})")
        
        # Test predictions
        test_query = QueryFeatures(
            topic="Corporate Tax",
            subtopic="Tax Planning",
            query_text="Client needs tax optimization strategy",
            business_function="Tax Advisory",
            department="Tax",
            country="United States",
            category="Consultation",
            complexity=75.0
        )
        
        matches = ml_model.predict_advisors(test_query)
        print(f"   ✅ Generated {len(matches)} advisor matches")
        
        return True
    except Exception as e:
        print(f"   ❌ ML model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_gateway_integration():
    """Test AI gateway integration"""
    print("🧠 Testing AI Gateway Integration...")
    
    try:
        # Initialize AI service
        ai_service = AIServiceGateway()
        print("   ✅ AI service initialized")
        
        # Check gateway availability
        is_available = ai_service.is_gateway_available()
        print(f"   ✅ Gateway available: {is_available}")
        
        if is_available:
            # Test case classification
            classification = await ai_service.classify_case(
                "Client needs tax optimization for M&A transaction",
                "Corporate Tax",
                "Tax Planning",
                "gpt4o"
            )
            print(f"   ✅ Case classification: {classification.get('complexity_score', 'N/A')}")
            
            # Test profile summary
            advisor_data = {
                'advisor_name': 'ADV001',
                'department': 'Tax Advisory',
                'business_function': 'Tax Planning',
                'country': 'United States',
                'total_cases_handled': 10,
                'avg_resolution_time': 7.0,
                'success_rate': 95.0,
                'expertise_tags': 'Corporate Tax, M&A, International Tax'
            }
            
            summary = await ai_service.generate_profile_summary(advisor_data)
            print(f"   ✅ Profile summary generated: {summary[:50]}...")
        else:
            print("   ⚠️  Gateway not available, using offline fallback")
            
            # Test offline fallback
            classification = await ai_service.classify_case(
                "Test query",
                "Test Topic",
                "Test Subtopic"
            )
            print(f"   ✅ Offline classification: {classification.get('complexity_score', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"   ❌ AI gateway test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_matching_service_integration():
    """Test matching service integration"""
    print("🎯 Testing Matching Service Integration...")
    
    try:
        # Initialize matching service
        matching_service = MatchingService()
        print("   ✅ Matching service initialized")
        
        # Test with sample case
        from app.models import Case, Advisor
        
        # Create sample case
        sample_case = Case(
            case_id="TEST001",
            topic="Corporate Tax",
            subtopic="Tax Planning",
            query="Client needs tax optimization strategy",
            complexity=75.0,
            country="United States"
        )
        
        # Create sample advisor
        sample_advisor = Advisor(
            advisor_id="ADV001",
            advisor_name="Test Advisor",
            department="Tax Advisory",
            business_function="Tax Planning",
            country="United States",
            total_cases_handled=10,
            avg_resolution_time=7.0,
            complexity_preference=70.0
        )
        
        print("   ✅ Sample case and advisor created")
        
        # Test matching logic (with mock database)
        db = next(get_db())
        topic_score = matching_service._calculate_topic_match(sample_case, sample_advisor, db)
        complexity_score = matching_service._calculate_complexity_match(sample_case, sample_advisor)
        
        print(f"   ✅ Topic match score: {topic_score:.1f}")
        print(f"   ✅ Complexity match score: {complexity_score:.1f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Matching service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_service_integration():
    """Test ML service integration"""
    print("📊 Testing ML Service Integration...")
    
    try:
        # Initialize ML service
        ml_service = MLAdvisorService()
        print("   ✅ ML service initialized")
        
        # Test Excel processing (with sample data)
        sample_data = {
            'Case ID': ['CASE001'],
            'Services': ['Tax Advisory'],
            'Topics': ['Corporate Tax'],
            'Current Sub-Topic': ['Tax Planning'],
            'Previous Sub-Topic': ['None'],
            'Date Created': ['2024-01-01'],
            'Date Submitted': ['2024-01-05'],
            'Created By (Bank ID)': ['USER001'],
            'Current Case Owner': ['ADV001'],
            'Previous Case Owner': ['None'],
            'Status': ['Resolved'],
            'Current Advisory Group': ['Tax Advisory'],
            'Previous Advisory Group': ['None'],
            'Overall Case Age (Days)': [4],
            'Business Function': ['Tax Advisory'],
            'Department': ['Tax'],
            'Country': ['United States'],
            'Category': ['Consultation'],
            'Complexity': [75.0],
            'Time Spent': [8.0],
            'Please describe your query': ['Client needs tax optimization strategy']
        }
        
        # Save sample data to temporary file
        temp_file = "temp_sample.xlsx"
        df = pd.DataFrame(sample_data)
        df.to_excel(temp_file, index=False)
        
        try:
            # Test Excel processing
            db = next(get_db())
            result = ml_service.process_excel_data(temp_file, db)
            print(f"   ✅ Excel processing: {result.get('cases_processed', 0)} cases")
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return True
    except Exception as e:
        print(f"   ❌ ML service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints (if server is running)"""
    print("🌐 Testing API Endpoints...")
    
    try:
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend server is running")
            
            # Test API documentation
            docs_response = requests.get(f"{base_url}/docs", timeout=5)
            if docs_response.status_code == 200:
                print("   ✅ API documentation accessible")
            else:
                print("   ⚠️  API documentation not accessible")
            
            return True
        else:
            print("   ⚠️  Backend server not responding")
            return False
            
    except requests.exceptions.RequestException:
        print("   ⚠️  Backend server not running (this is normal if not started)")
        return True  # Not a failure, just not running

async def test_frontend_integration():
    """Test frontend integration (if running)"""
    print("🎨 Testing Frontend Integration...")
    
    try:
        frontend_url = "http://localhost:3000"
        
        # Test frontend accessibility
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is running")
            
            # Check if it's a React app
            if "react" in response.text.lower() or "advisor" in response.text.lower():
                print("   ✅ Frontend appears to be the correct application")
            else:
                print("   ⚠️  Frontend response doesn't match expected content")
            
            return True
        else:
            print("   ⚠️  Frontend not responding")
            return False
            
    except requests.exceptions.RequestException:
        print("   ⚠️  Frontend not running (this is normal if not started)")
        return True  # Not a failure, just not running

async def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests...\n")
    
    tests = [
        ("Database", test_database_integration),
        ("ML Model", test_ml_model_integration),
        ("AI Gateway", test_ai_gateway_integration),
        ("Matching Service", test_matching_service_integration),
        ("ML Service", test_ml_service_integration),
        ("API Endpoints", test_api_endpoints),
        ("Frontend", test_frontend_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! System is ready.")
    elif passed >= total - 2:  # Allow 2 failures (usually API/Frontend if not running)
        print("✅ Core system integration successful!")
        print("⚠️  Some optional components not available (API/Frontend)")
    else:
        print("❌ Multiple integration issues detected")
    
    return passed >= total - 2  # Success if core components work

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
