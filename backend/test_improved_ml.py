#!/usr/bin/env python3
"""
Test script for the improved ML model with dynamic Excel column handling
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_model_improved import AdvisorMatchingML
from app.services.ai_service_gateway import AIServiceGateway

async def test_improved_ml():
    """Test the improved ML model"""
    print("🧪 Testing Improved ML Model")
    print("=" * 50)
    
    # Test AI Gateway connection
    print("\n1. Testing AI Gateway Connection...")
    ai_service = AIServiceGateway()
    gateway_available = ai_service.is_gateway_available()
    print(f"   AI Gateway Available: {gateway_available}")
    
    if not gateway_available:
        print("   ⚠️  AI Gateway not available - will use offline fallback")
    
    # Test ML Model initialization
    print("\n2. Testing ML Model Initialization...")
    try:
        ml_model = AdvisorMatchingML()
        print(f"   ✅ ML Model initialized successfully")
        print(f"   AI Gateway Available: {ml_model.ai_service.is_gateway_available()}")
        print(f"   Model Name: {ml_model.model_metrics['model_name']}")
    except Exception as e:
        print(f"   ❌ Error initializing ML Model: {e}")
        return
    
    # Test column mapping detection
    print("\n3. Testing Column Mapping Detection...")
    try:
        # Create sample data with different column names
        sample_data = pd.DataFrame({
            'Current Case Owner': ['ADV001', 'ADV002', 'ADV001'],
            'Case ID': ['CASE001', 'CASE002', 'CASE003'],
            'Topics': ['Tax Planning', 'Audit Review', 'Risk Management'],
            'Subtopics': ['Corporate Tax', 'Internal Audit', 'Operational Risk'],
            'Query Title': ['Tax optimization for MNC', 'Audit compliance review', 'Risk assessment framework'],
            'Query Description': ['Need help with tax planning', 'Audit process review', 'Risk management strategy'],
            'Business Function': ['Tax', 'Audit', 'Risk'],
            'Department': ['Tax Advisory', 'Audit Services', 'Risk Advisory'],
            'Country': ['USA', 'UK', 'Australia'],
            'Complexity Score': [7.0, 5.0, 8.0],
            'Status': ['Resolved', 'Pending', 'Completed'],
            'Date Created': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Date Submitted': ['2024-01-05', '2024-01-07', '2024-01-10'],
            'Case Completion Date': ['2024-01-10', '2024-01-12', '2024-01-15'],
            'Please select your industry': ['Financial Services', 'Manufacturing', 'Technology'],
            'Please describe your specific needs': ['Tax optimization', 'Compliance review', 'Risk framework']
        })
        
        # Test column mapping detection
        processed_data = ml_model._process_excel_data(sample_data)
        column_mapping = processed_data.attrs['column_mapping']
        
        print(f"   ✅ Column mapping detected successfully")
        print(f"   Advisor ID column: {column_mapping.get('advisor_id')}")
        print(f"   Case ID column: {column_mapping.get('case_id')}")
        print(f"   Topic column: {column_mapping.get('topic')}")
        print(f"   Query columns: {column_mapping.get('query_title')}, {column_mapping.get('query_description')}")
        print(f"   Date columns: {column_mapping.get('date_created')}, {column_mapping.get('date_completion')}")
        print(f"   Text columns: {len(column_mapping.get('all_text_columns', []))}")
        
    except Exception as e:
        print(f"   ❌ Error testing column mapping: {e}")
    
    # Test model performance
    print("\n4. Testing Model Performance...")
    try:
        performance = ml_model.get_model_performance()
        print(f"   ✅ Model performance retrieved")
        print(f"   Success: {performance.get('success', False)}")
        print(f"   Model Name: {performance.get('model_name', 'Unknown')}")
        print(f"   AI Gateway Available: {performance.get('ai_gateway_available', False)}")
    except Exception as e:
        print(f"   ❌ Error getting model performance: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Improved ML Model test completed!")
    
    if not gateway_available:
        print("\n📝 Note: System is running in offline fallback mode.")
        print("   To enable full AI Gateway features:")
        print("   1. Set OPENAI_API_BASE_URL in your .env file")
        print("   2. Set OPENAI_API_KEY in your .env file")
        print("   3. Ensure your AI gateway is accessible")

if __name__ == "__main__":
    asyncio.run(test_improved_ml())
