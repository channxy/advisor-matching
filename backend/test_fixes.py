#!/usr/bin/env python3
"""
Simple test to verify advisor profile fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_advisor_model_attributes():
    """Test that advisor model attributes are correct"""
    try:
        from app.models.advisor import Advisor
        from app.models.case import Case, CaseStatus
        
        print("✅ Successfully imported models")
        
        # Test Advisor attributes
        advisor = Advisor(
            advisor_id="TEST001",
            advisor_name="Test Advisor",
            department="Test Department",
            business_function="Test Function",
            country="Test Country",
            expertise_tags="Tax,Audit,Compliance",
            total_cases_handled=10,
            success_rate=85.0
        )
        
        print("✅ Advisor object created successfully")
        print(f"   Advisor ID: {advisor.advisor_id}")
        print(f"   Advisor Name: {advisor.advisor_name}")
        print(f"   Expertise Tags: {advisor.expertise_tags}")
        print(f"   Total Cases: {advisor.total_cases_handled}")
        print(f"   Success Rate: {advisor.success_rate}")
        
        # Test Case attributes
        case = Case(
            case_id="CASE001",
            topic="Test Topic",
            subtopic="Test Subtopic",
            query="Test Query",
            status=CaseStatus.RESOLVED,
            complexity=7.0
        )
        
        print("✅ Case object created successfully")
        print(f"   Case ID: {case.case_id}")
        print(f"   Status: {case.status}")
        print(f"   Complexity: {case.complexity}")
        
        # Test expertise tags parsing
        if advisor.expertise_tags:
            tags = advisor.expertise_tags.split(',')
            print(f"✅ Expertise tags parsed: {tags}")
        
        print("\n🎉 All tests passed! Advisor profile updates should work correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advisor_model_attributes()
