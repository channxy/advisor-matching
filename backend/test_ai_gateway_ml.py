#!/usr/bin/env python3
"""
Test script for the new AI Gateway ML model
Tests both with and without AI gateway connection
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_model import AdvisorMatchingML
from app.services.ai_service_gateway import AIServiceGateway

async def test_ai_gateway_ml():
    """Test the AI Gateway ML model"""
    print("🧪 Testing AI Gateway ML Model")
    print("=" * 50)
    
    # Test AI Gateway connection
    print("\n1. Testing AI Gateway Connection...")
    ai_service = AIServiceGateway()
    gateway_available = ai_service.is_gateway_available()
    print(f"   AI Gateway Available: {gateway_available}")
    
    if not gateway_available:
        print("   ⚠️  AI Gateway not available - will use offline fallback")
        print("   To enable AI Gateway, set OPENAI_API_BASE_URL and OPENAI_API_KEY in .env file")
    
    # Test ML Model initialization
    print("\n2. Testing ML Model Initialization...")
    try:
        ml_model = AdvisorMatchingML()
        print(f"   ✅ ML Model initialized successfully")
        print(f"   AI Gateway Available: {ml_model.ai_gateway_available}")
        print(f"   Model Name: {ml_model.model_metrics['model_name']}")
    except Exception as e:
        print(f"   ❌ Error initializing ML Model: {e}")
        return
    
    # Test model performance
    print("\n3. Testing Model Performance...")
    try:
        performance = ml_model.get_model_performance()
        print(f"   ✅ Model performance retrieved")
        print(f"   Success: {performance.get('success', False)}")
        print(f"   Model Name: {performance.get('model_name', 'Unknown')}")
        print(f"   AI Gateway Available: {performance.get('ai_gateway_available', False)}")
    except Exception as e:
        print(f"   ❌ Error getting model performance: {e}")
    
    # Test embedding generation
    print("\n4. Testing Embedding Generation...")
    try:
        test_text = "tax planning and optimization for multinational corporations"
        if ml_model.ai_gateway_available:
            embedding = await ml_model.ai_service.get_embedding(test_text, model="text3large")
        else:
            embedding = await ml_model.ai_service._get_embedding_offline(test_text)
        
        print(f"   ✅ Embedding generated successfully")
        print(f"   Embedding length: {len(embedding)}")
        print(f"   Sample values: {embedding[:5]}")
    except Exception as e:
        print(f"   ❌ Error generating embedding: {e}")
    
    # Test advisor prediction (without database)
    print("\n5. Testing Advisor Prediction...")
    try:
        test_query = "international tax compliance for manufacturing company"
        predictions = await ml_model.predict_advisors(
            query=test_query,
            department="Tax Advisory",
            business_function="Tax",
            country="United States",
            complexity=7.0,
            db=None
        )
        
        print(f"   ✅ Advisor prediction completed")
        print(f"   Predictions returned: {len(predictions)}")
        if predictions:
            print(f"   Top match: {predictions[0]}")
    except Exception as e:
        print(f"   ❌ Error predicting advisors: {e}")
    
    print("\n" + "=" * 50)
    print("✅ AI Gateway ML Model test completed!")
    
    if not gateway_available:
        print("\n📝 Note: System is running in offline fallback mode.")
        print("   To enable full AI Gateway features:")
        print("   1. Set OPENAI_API_BASE_URL in your .env file")
        print("   2. Set OPENAI_API_KEY in your .env file")
        print("   3. Ensure your AI gateway is accessible")

if __name__ == "__main__":
    asyncio.run(test_ai_gateway_ml())
