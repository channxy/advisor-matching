from sqlalchemy.orm import Session
from app.models.database import SessionLocal, engine
from app.models import Advisor, Case, Assignment, Tag, Base
from datetime import datetime, timedelta
import random

def seed_data():
    db = SessionLocal()
    
    # Clear existing data
    db.query(Assignment).delete()
    db.query(Tag).delete()
    db.query(Case).delete()
    db.query(Advisor).delete()
    db.commit()
    
    # Create advisors
    advisors_data = [
        {
            "advisor_id": "ADV001",
            "advisor_name": "Sarah Johnson",
            "current_advisory_group": "Tax Advisory",
            "previous_advisory_group": "Audit",
            "department": "Tax",
            "business_function": "Corporate Tax",
            "country": "United States",
            "avg_resolution_time": 3.2,
            "total_cases_handled": 45,
            "success_rate": 92.0,
            "profile_summary": "Expert in corporate tax planning and compliance with 8+ years experience",
            "expertise_tags": "corporate tax,compliance,planning",
            "complexity_preference": 75.0
        },
        {
            "advisor_id": "ADV002",
            "advisor_name": "Michael Chen",
            "current_advisory_group": "Audit Advisory",
            "previous_advisory_group": "Risk Management",
            "department": "Audit",
            "business_function": "Financial Audit",
            "country": "Canada",
            "avg_resolution_time": 2.8,
            "total_cases_handled": 38,
            "success_rate": 89.0,
            "profile_summary": "Specialized in financial auditing and risk assessment",
            "expertise_tags": "financial audit,risk assessment,compliance",
            "complexity_preference": 65.0
        },
        {
            "advisor_id": "ADV003",
            "advisor_name": "Emily Rodriguez",
            "current_advisory_group": "Consulting",
            "previous_advisory_group": "Strategy",
            "department": "Consulting",
            "business_function": "Business Strategy",
            "country": "United Kingdom",
            "avg_resolution_time": 4.1,
            "total_cases_handled": 52,
            "success_rate": 94.0,
            "profile_summary": "Strategic consultant with expertise in business transformation",
            "expertise_tags": "strategy,transformation,business planning",
            "complexity_preference": 85.0
        },
        {
            "advisor_id": "ADV004",
            "advisor_name": "David Kim",
            "current_advisory_group": "Technology Advisory",
            "previous_advisory_group": "IT Consulting",
            "department": "Technology",
            "business_function": "Digital Transformation",
            "country": "Singapore",
            "avg_resolution_time": 3.5,
            "total_cases_handled": 41,
            "success_rate": 91.0,
            "profile_summary": "Technology expert specializing in digital transformation and cybersecurity",
            "expertise_tags": "digital transformation,cybersecurity,technology",
            "complexity_preference": 80.0
        },
        {
            "advisor_id": "ADV005",
            "advisor_name": "Lisa Thompson",
            "current_advisory_group": "Risk Advisory",
            "previous_advisory_group": "Compliance",
            "department": "Risk",
            "business_function": "Risk Management",
            "country": "Australia",
            "avg_resolution_time": 2.9,
            "total_cases_handled": 35,
            "success_rate": 88.0,
            "profile_summary": "Risk management specialist with focus on regulatory compliance",
            "expertise_tags": "risk management,compliance,regulatory",
            "complexity_preference": 70.0
        },
        {
            "advisor_id": "ADV006",
            "advisor_name": "James Wilson",
            "current_advisory_group": "M&A Advisory",
            "previous_advisory_group": "Investment Banking",
            "department": "M&A",
            "business_function": "Mergers & Acquisitions",
            "country": "United States",
            "avg_resolution_time": 5.2,
            "total_cases_handled": 28,
            "success_rate": 96.0,
            "profile_summary": "M&A specialist with extensive experience in complex transactions",
            "expertise_tags": "mergers,acquisitions,transactions,valuation",
            "complexity_preference": 90.0
        },
        {
            "advisor_id": "ADV007",
            "advisor_name": "Maria Garcia",
            "current_advisory_group": "Sustainability Advisory",
            "previous_advisory_group": "Environmental",
            "department": "Sustainability",
            "business_function": "ESG Consulting",
            "country": "Germany",
            "avg_resolution_time": 3.8,
            "total_cases_handled": 33,
            "success_rate": 90.0,
            "profile_summary": "Sustainability expert focusing on ESG reporting and compliance",
            "expertise_tags": "sustainability,esg,environmental,reporting",
            "complexity_preference": 75.0
        },
        {
            "advisor_id": "ADV008",
            "advisor_name": "Robert Taylor",
            "current_advisory_group": "Forensic Advisory",
            "previous_advisory_group": "Investigations",
            "department": "Forensic",
            "business_function": "Forensic Accounting",
            "country": "United Kingdom",
            "avg_resolution_time": 6.1,
            "total_cases_handled": 22,
            "success_rate": 95.0,
            "profile_summary": "Forensic accounting specialist with expertise in fraud detection",
            "expertise_tags": "forensic,accounting,fraud,investigation",
            "complexity_preference": 95.0
        },
        {
            "advisor_id": "ADV009",
            "advisor_name": "Anna Kowalski",
            "current_advisory_group": "HR Advisory",
            "previous_advisory_group": "Organizational Development",
            "department": "Human Resources",
            "business_function": "HR Consulting",
            "country": "Poland",
            "avg_resolution_time": 2.5,
            "total_cases_handled": 47,
            "success_rate": 87.0,
            "profile_summary": "HR consultant specializing in organizational development and change management",
            "expertise_tags": "hr,organizational development,change management",
            "complexity_preference": 60.0
        },
        {
            "advisor_id": "ADV010",
            "advisor_name": "Carlos Mendez",
            "current_advisory_group": "Operations Advisory",
            "previous_advisory_group": "Supply Chain",
            "department": "Operations",
            "business_function": "Supply Chain Optimization",
            "country": "Mexico",
            "avg_resolution_time": 3.3,
            "total_cases_handled": 39,
            "success_rate": 93.0,
            "profile_summary": "Operations expert with focus on supply chain optimization and efficiency",
            "expertise_tags": "operations,supply chain,optimization,efficiency",
            "complexity_preference": 70.0
        }
    ]
    
    advisors = []
    for data in advisors_data:
        advisor = Advisor(**data)
        db.add(advisor)
        advisors.append(advisor)
    
    db.commit()
    
    # Create sample cases
    cases_data = [
        {
            "case_id": "CASE001",
            "topic": "Tax Planning",
            "subtopic": "Corporate Tax Optimization",
            "query": "Need assistance with corporate tax planning strategies for multinational operations",
            "casetype": "Consultation",
            "transaction_type": "Planning",
            "business_function": "Corporate Tax",
            "country": "United States",
            "complexity": 85.0,
            "status": "pending"
        },
        {
            "case_id": "CASE002",
            "topic": "Audit",
            "subtopic": "Financial Statement Audit",
            "query": "Annual financial statement audit for manufacturing company",
            "casetype": "Audit",
            "transaction_type": "Annual",
            "business_function": "Financial Audit",
            "country": "Canada",
            "complexity": 70.0,
            "status": "assigned"
        },
        {
            "case_id": "CASE003",
            "topic": "Strategy",
            "subtopic": "Business Transformation",
            "query": "Digital transformation strategy for traditional retail business",
            "casetype": "Consultation",
            "transaction_type": "Strategy",
            "business_function": "Business Strategy",
            "country": "United Kingdom",
            "complexity": 90.0,
            "status": "pending"
        },
        {
            "case_id": "CASE004",
            "topic": "Technology",
            "subtopic": "Cybersecurity Assessment",
            "query": "Cybersecurity risk assessment and compliance review",
            "casetype": "Assessment",
            "transaction_type": "Review",
            "business_function": "Digital Transformation",
            "country": "Singapore",
            "complexity": 80.0,
            "status": "in_progress"
        },
        {
            "case_id": "CASE005",
            "topic": "Risk Management",
            "subtopic": "Compliance Framework",
            "query": "Development of regulatory compliance framework for financial services",
            "casetype": "Framework",
            "transaction_type": "Development",
            "business_function": "Risk Management",
            "country": "Australia",
            "complexity": 75.0,
            "status": "resolved"
        }
    ]
    
    cases = []
    for data in cases_data:
        case = Case(**data)
        db.add(case)
        cases.append(case)
    
    db.commit()
    
    # Create sample assignments
    assignments_data = [
        {
            "case_id": cases[0].id,
            "advisor_id": advisors[0].id,
            "matching_score": 92.5,
            "matching_insights": "Sarah has extensive experience in corporate tax planning with 45 cases handled. Perfect match for multinational tax optimization.",
            "status": "pending"
        },
        {
            "case_id": cases[1].id,
            "advisor_id": advisors[1].id,
            "matching_score": 88.0,
            "matching_insights": "Michael specializes in financial auditing with 38 cases completed. Strong match for financial statement audit.",
            "status": "accepted"
        },
        {
            "case_id": cases[2].id,
            "advisor_id": advisors[2].id,
            "matching_score": 95.0,
            "matching_insights": "Emily has expertise in business transformation with 52 cases. Excellent match for digital transformation strategy.",
            "status": "pending"
        },
        {
            "case_id": cases[3].id,
            "advisor_id": advisors[3].id,
            "matching_score": 91.0,
            "matching_insights": "David specializes in digital transformation and cybersecurity. Strong match for cybersecurity assessment.",
            "status": "accepted"
        },
        {
            "case_id": cases[4].id,
            "advisor_id": advisors[4].id,
            "matching_score": 87.5,
            "matching_insights": "Lisa has expertise in risk management and compliance. Good match for regulatory compliance framework.",
            "status": "accepted"
        }
    ]
    
    for data in assignments_data:
        assignment = Assignment(**data)
        db.add(assignment)
    
    db.commit()
    
    # Create sample tags
    from datetime import datetime
    current_time = datetime.now(datetime.UTC)
    
    tags_data = [
        {"advisor_id": advisors[0].id, "tag_name": "Corporate Tax", "tag_category": "topic", "confidence_score": 0.95, "usage_count": 15, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[0].id, "tag_name": "Compliance", "tag_category": "skill", "confidence_score": 0.90, "usage_count": 12, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[1].id, "tag_name": "Financial Audit", "tag_category": "topic", "confidence_score": 0.92, "usage_count": 18, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[1].id, "tag_name": "Risk Assessment", "tag_category": "skill", "confidence_score": 0.88, "usage_count": 10, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[2].id, "tag_name": "Strategy", "tag_category": "topic", "confidence_score": 0.94, "usage_count": 20, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[2].id, "tag_name": "Transformation", "tag_category": "skill", "confidence_score": 0.91, "usage_count": 16, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[3].id, "tag_name": "Digital Transformation", "tag_category": "topic", "confidence_score": 0.93, "usage_count": 14, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[3].id, "tag_name": "Cybersecurity", "tag_category": "skill", "confidence_score": 0.89, "usage_count": 11, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[4].id, "tag_name": "Risk Management", "tag_category": "topic", "confidence_score": 0.90, "usage_count": 13, "created_at": current_time, "updated_at": current_time},
        {"advisor_id": advisors[4].id, "tag_name": "Compliance", "tag_category": "skill", "confidence_score": 0.87, "usage_count": 9, "created_at": current_time, "updated_at": current_time}
    ]
    
    for data in tags_data:
        tag = Tag(**data)
        db.add(tag)
    
    db.commit()
    db.close()
    
    print("Sample data seeded successfully!")

if __name__ == "__main__":
    seed_data()
