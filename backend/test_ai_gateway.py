#!/usr/bin/env python3
"""
Test script for AI Gateway - verifies connection and functionality
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service_gateway import AIServiceGateway

async def test_ai_gateway():
    """Test the AI gateway functionality"""
    print("🤖 Testing AI Gateway...")
    
    try:
        # Initialize AI service
        print("1. Initializing AI Gateway service...")
        ai_service = AIServiceGateway()
        
        # Check gateway availability
        print("2. Checking gateway availability...")
        is_available = ai_service.is_gateway_available()
        print(f"   Gateway available: {is_available}")
        
        if not is_available:
            print("⚠️  AI Gateway not available. Check your .env configuration.")
            print("   The system will use offline fallback mode.")
            return False
        
        # Get available models
        print("3. Getting available models...")
        models = ai_service.get_available_models()
        print(f"   Available models: {list(models.keys())}")
        
        # Test case classification
        print("4. Testing case classification...")
        classification = await ai_service.classify_case(
            "Client needs tax optimization strategy for M&A transaction involving multiple jurisdictions",
            "Corporate Tax",
            "Tax Planning",
            "gpt4o"
        )
        print(f"   ✅ Case classification test passed")
        print(f"   - Complexity: {classification.get('complexity_score', 'N/A')}")
        print(f"   - Domain Relevance: {classification.get('domain_relevance', 'N/A')}")
        print(f"   - Confidence: {classification.get('classification_confidence', 'N/A')}")
        print(f"   - Tags: {classification.get('suggested_tags', [])}")
        
        # Test profile summary generation
        print("5. Testing profile summary generation...")
        advisor_data = {
            'advisor_name': 'ADV001',
            'department': 'Tax Advisory',
            'business_function': 'Tax Planning',
            'country': 'United States',
            'total_cases_handled': 15,
            'avg_resolution_time': 7.2,
            'success_rate': 95.0,
            'expertise_tags': 'Corporate Tax, M&A, International Tax, Transfer Pricing',
            'other_countries_handled': 'Canada, UK, Germany, Singapore'
        }
        
        summary = await ai_service.generate_profile_summary(advisor_data, "claude-3-5-sonnet")
        print(f"   ✅ Profile summary test passed")
        print(f"   Summary: {summary[:100]}...")
        
        # Test matching insights
        print("6. Testing matching insights...")
        case_data = {
            'topic': 'Corporate Tax',
            'subtopic': 'M&A Tax Planning',
            'query': 'Client needs tax optimization for cross-border acquisition',
            'complexity': 85.0
        }
        
        insights = await ai_service.generate_matching_insights(case_data, advisor_data, "gpt4o")
        print(f"   ✅ Matching insights test passed")
        print(f"   Insights: {insights}")
        
        # Test embeddings
        print("7. Testing embeddings...")
        embedding = await ai_service.get_embedding(
            "Tax optimization for international M&A transactions",
            "text3large"
        )
        print(f"   ✅ Embedding test passed")
        print(f"   Embedding dimensions: {len(embedding)}")
        
        # Test query similarity
        print("8. Testing query similarity...")
        similarity = await ai_service.analyze_query_similarity(
            "Tax optimization for M&A",
            "Corporate tax planning for acquisitions",
            "text3large"
        )
        print(f"   ✅ Query similarity test passed")
        print(f"   Similarity score: {similarity:.3f}")
        
        print("\n🎉 AI Gateway is working perfectly!")
        print("✅ All AI features are operational")
        print("✅ Multiple models available")
        print("✅ Fallback mode available")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_model_specific():
    """Test different models specifically"""
    print("\n🧪 Testing Specific Models...")
    
    ai_service = AIServiceGateway()
    
    if not ai_service.is_gateway_available():
        print("⚠️  Gateway not available for model testing")
        return
    
    models_to_test = ['gpt4o', 'claude-3-5-sonnet', 'llama-3-3-70b']
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...")
            result = await ai_service.classify_case(
                "Test query for model validation",
                "Test Topic",
                "Test Subtopic",
                model
            )
            print(f"   ✅ {model}: Working")
        except Exception as e:
            print(f"   ❌ {model}: {str(e)[:50]}...")

if __name__ == "__main__":
    success = asyncio.run(test_ai_gateway())
    
    if success:
        asyncio.run(test_model_specific())
    
    sys.exit(0 if success else 1)
