import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from ..models import Advisor, Case, Assignment, Tag
import logging

logger = logging.getLogger(__name__)

class ExcelProcessor:
    def __init__(self):
        pass
    
    def process_excel_and_generate_profiles(self, excel_file_path: str, db: Session) -> Dict:
        """Process Excel file and generate advisor profiles from Current Case Owner data"""
        logger.info(f"Processing Excel file: {excel_file_path}")
        
        try:
            # Load Excel data
            df = pd.read_excel(excel_file_path)
            logger.info(f"Loaded {len(df)} transactions from Excel")
            
            # Clear existing data (optional - you might want to append instead)
            db.query(Assignment).delete()
            db.query(Tag).delete()
            db.query(Case).delete()
            db.query(Advisor).delete()
            db.commit()
            
            # Process transactions and group by Current Case Owner
            advisor_profiles = self._extract_advisor_profiles_from_excel(df)
            
            # Create cases and advisors
            cases_created = self._create_cases_from_excel(df, db)
            advisors_created = self._create_advisors_from_profiles(advisor_profiles, db)
            
            # Create assignments linking cases to advisors
            assignments_created = self._create_assignments_from_excel(df, db)
            
            return {
                'message': 'Excel data processed and advisor profiles generated successfully',
                'cases_created': cases_created,
                'advisors_created': advisors_created,
                'assignments_created': assignments_created,
                'advisor_profiles': len(advisor_profiles)
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
    
    def _extract_advisor_profiles_from_excel(self, df: pd.DataFrame) -> Dict:
        """Extract advisor profiles from Excel data grouped by Current Case Owner"""
        advisor_profiles = {}
        
        for _, row in df.iterrows():
            advisor_id = str(row.get('Current Case Owner', ''))
            if not advisor_id or pd.isna(advisor_id) or advisor_id == '':
                continue
            
            if advisor_id not in advisor_profiles:
                advisor_profiles[advisor_id] = {
                    'advisor_id': advisor_id,
                    'advisor_name': advisor_id,  # Using ID as name for now
                    'cases': [],
                    'topics': set(),
                    'subtopics': set(),
                    'services': set(),
                    'business_functions': set(),
                    'countries': set(),
                    'complexities': [],
                    'resolution_times': [],
                    'success_count': 0,
                    'total_count': 0,
                    'current_advisory_group': '',
                    'department': '',
                    'country': ''
                }
            
            profile = advisor_profiles[advisor_id]
            
            # Collect case data
            case_data = {
                'case_id': str(row.get('Case ID', '')),
                'topic': str(row.get('Topics', '')),
                'subtopic': str(row.get('Current Sub-Topic', '')),
                'query': str(row.get('Please describe your query', '')),
                'service': str(row.get('Services', '')),
                'business_function': str(row.get('Business Function', '')),
                'country': str(row.get('Country', '')),
                'complexity': float(row.get('Complexity', 50.0)),
                'status': str(row.get('Status', '')),
                'date_created': row.get('Date Created'),
                'date_submitted': row.get('Date Submitted'),
                'current_advisory_group': str(row.get('Current Advisory Group', '')),
                'department': str(row.get('Department', ''))
            }
            
            profile['cases'].append(case_data)
            
            # Update profile metrics
            if case_data['topic']:
                profile['topics'].add(case_data['topic'])
            if case_data['subtopic']:
                profile['subtopics'].add(case_data['subtopic'])
            if case_data['service']:
                profile['services'].add(case_data['service'])
            if case_data['business_function']:
                profile['business_functions'].add(case_data['business_function'])
            if case_data['country']:
                profile['countries'].add(case_data['country'])
            
            profile['complexities'].append(case_data['complexity'])
            profile['total_count'] += 1
            
            # Track success rate
            if case_data['status'].lower() in ['resolved', 'completed']:
                profile['success_count'] += 1
            
            # Calculate resolution time
            try:
                if case_data['date_created'] and case_data['date_submitted']:
                    date_created = pd.to_datetime(case_data['date_created'])
                    date_submitted = pd.to_datetime(case_data['date_submitted'])
                    resolution_time = (date_submitted - date_created).days
                    profile['resolution_times'].append(resolution_time)
            except:
                pass
            
            # Update current advisory group and department (use most recent)
            if case_data['current_advisory_group']:
                profile['current_advisory_group'] = case_data['current_advisory_group']
            if case_data['department']:
                profile['department'] = case_data['department']
            if case_data['country']:
                profile['country'] = case_data['country']
        
        return advisor_profiles
    
    def _create_cases_from_excel(self, df: pd.DataFrame, db: Session) -> int:
        """Create Case objects from Excel data"""
        cases_created = 0
        
        for _, row in df.iterrows():
            case_id = str(row.get('Case ID', ''))
            if not case_id or pd.isna(case_id):
                continue
            
            # Check if case already exists
            existing_case = db.query(Case).filter(Case.case_id == case_id).first()
            if existing_case:
                continue
            
            # Create new case
            case = Case(
                case_id=case_id,
                topic=str(row.get('Topics', '')),
                subtopic=str(row.get('Current Sub-Topic', '')),
                query=str(row.get('Please describe your query', '')),
                casetype=str(row.get('Category', '')),
                transaction_type=str(row.get('Services', '')),
                business_function=str(row.get('Business Function', '')),
                country=str(row.get('Country', '')),
                complexity=float(row.get('Complexity', 50.0)),
                status='resolved' if str(row.get('Status', '')).lower() in ['resolved', 'completed'] else 'pending'
            )
            
            # Set dates if available
            try:
                if pd.notna(row.get('Date Created')):
                    case.date_created = pd.to_datetime(row.get('Date Created'))
                if pd.notna(row.get('Date Submitted')):
                    case.date_resolved = pd.to_datetime(row.get('Date Submitted'))
                
                # Calculate resolution time
                if case.date_created and case.date_resolved:
                    case.resolution_time = (case.date_resolved - case.date_created).days
            except:
                pass
            
            db.add(case)
            cases_created += 1
        
        db.commit()
        logger.info(f"Created {cases_created} cases from Excel data")
        return cases_created
    
    def _create_advisors_from_profiles(self, advisor_profiles: Dict, db: Session) -> int:
        """Create Advisor objects from extracted profiles"""
        advisors_created = 0
        
        for advisor_id, profile_data in advisor_profiles.items():
            # Calculate metrics
            total_cases = profile_data['total_count']
            success_rate = (profile_data['success_count'] / total_cases * 100) if total_cases > 0 else 0
            avg_resolution_time = np.mean(profile_data['resolution_times']) if profile_data['resolution_times'] else 0
            avg_complexity = np.mean(profile_data['complexities']) if profile_data['complexities'] else 50.0
            
            # Create expertise tags
            topics = list(profile_data['topics'])
            subtopics = list(profile_data['subtopics'])
            services = list(profile_data['services'])
            expertise_areas = topics + subtopics + services
            expertise_tags = ','.join(expertise_areas[:10])  # Limit to 10 tags
            
            # Generate profile summary
            profile_summary = self._generate_profile_summary(profile_data)
            
            # Create advisor
            advisor = Advisor(
                advisor_id=advisor_id,
                advisor_name=profile_data['advisor_name'],
                current_advisory_group=profile_data['current_advisory_group'],
                previous_advisory_group='',  # Not available in Excel
                department=profile_data['department'],
                business_function=list(profile_data['business_functions'])[0] if profile_data['business_functions'] else '',
                country=profile_data['country'],
                avg_resolution_time=avg_resolution_time,
                total_cases_handled=total_cases,
                success_rate=success_rate,
                profile_summary=profile_summary,
                expertise_tags=expertise_tags,
                complexity_preference=avg_complexity
            )
            
            db.add(advisor)
            advisors_created += 1
        
        db.commit()
        logger.info(f"Created {advisors_created} advisor profiles from Excel data")
        return advisors_created
    
    def _create_assignments_from_excel(self, df: pd.DataFrame, db: Session) -> int:
        """Create Assignment objects linking cases to advisors"""
        assignments_created = 0
        
        for _, row in df.iterrows():
            case_id = str(row.get('Case ID', ''))
            advisor_id = str(row.get('Current Case Owner', ''))
            
            if not case_id or not advisor_id or pd.isna(case_id) or pd.isna(advisor_id):
                continue
            
            # Get case and advisor
            case = db.query(Case).filter(Case.case_id == case_id).first()
            advisor = db.query(Advisor).filter(Advisor.advisor_id == advisor_id).first()
            
            if not case or not advisor:
                continue
            
            # Check if assignment already exists
            existing_assignment = db.query(Assignment).filter(
                Assignment.case_id == case.id,
                Assignment.advisor_id == advisor.id
            ).first()
            
            if existing_assignment:
                continue
            
            # Create assignment
            assignment = Assignment(
                case_id=case.id,
                advisor_id=advisor.id,
                matching_score=95.0,  # High score since it's historical data
                matching_insights=f"Historical assignment based on expertise in {case.topic}",
                status='accepted' if case.status.value == 'resolved' else 'pending',
                action_taken_at=case.date_created or datetime.now(),
                time_to_accept=1.0,
                time_to_resolve=case.resolution_time or 0.0
            )
            
            db.add(assignment)
            assignments_created += 1
        
        db.commit()
        logger.info(f"Created {assignments_created} assignments from Excel data")
        return assignments_created
    
    def _generate_profile_summary(self, profile_data: Dict) -> str:
        """Generate advisor profile summary"""
        total_cases = profile_data['total_count']
        success_rate = (profile_data['success_count'] / total_cases * 100) if total_cases > 0 else 0
        topics = list(profile_data['topics'])
        services = list(profile_data['services'])
        
        summary = f"Advisor with {total_cases} cases handled"
        if topics:
            summary += f", specializing in {', '.join(topics[:3])}"
        if services:
            summary += f" across {', '.join(services[:2])} services"
        summary += f" with {success_rate:.1f}% success rate"
        
        return summary
