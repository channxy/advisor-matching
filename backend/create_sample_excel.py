#!/usr/bin/env python3
"""
Create Sample Excel File for Testing
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_excel():
    """Create a sample Excel file with transaction data"""
    
    # Sample data
    data = [
        # Tax Advisory Cases
        ['CASE001', 'Tax Advisory', 'Corporate Tax', 'Tax Planning', 'Compliance', 
         '2024-01-15', '2024-01-18', 'BANK001', 'ADV001', '', 'Resolved',
         'Tax Advisory', 'Audit Advisory', 3.0, 'Tax Advisory', 'Tax', 'United States',
         'Consultation', 85.0, 8.5, 'Client needs tax optimization strategy for M&A transaction'],
        
        ['CASE002', 'Tax Advisory', 'Corporate Tax', 'Transfer Pricing', 'Tax Planning',
         '2024-01-20', '2024-01-25', 'BANK002', 'ADV001', '', 'Resolved',
         'Tax Advisory', 'Audit Advisory', 5.0, 'Tax Advisory', 'Tax', 'United States',
         'Compliance', 90.0, 12.0, 'Transfer pricing documentation for multinational'],
        
        # Audit Cases
        ['CASE003', 'Audit Services', 'Financial Audit', 'Internal Controls', 'Risk Assessment',
         '2024-01-25', '2024-02-01', 'BANK003', 'ADV002', '', 'Resolved',
         'Audit Advisory', 'Risk Advisory', 7.0, 'Audit Services', 'Audit', 'Canada',
         'Audit', 75.0, 15.0, 'Internal control assessment for retail chain'],
        
        ['CASE004', 'Audit Services', 'Financial Audit', 'Financial Statements', 'Internal Controls',
         '2024-02-01', '2024-02-08', 'BANK004', 'ADV002', '', 'Resolved',
         'Audit Advisory', 'Risk Advisory', 7.0, 'Audit Services', 'Audit', 'Canada',
         'Audit', 80.0, 18.0, 'Annual financial statement audit for tech startup'],
        
        # Strategy Cases
        ['CASE005', 'Strategy Consulting', 'Business Strategy', 'Digital Transformation', 'Market Entry',
         '2024-02-05', '2024-02-15', 'BANK005', 'ADV003', '', 'Resolved',
         'Strategy Advisory', 'Consulting', 10.0, 'Strategy Consulting', 'Consulting', 'United Kingdom',
         'Consultation', 95.0, 25.0, 'Digital transformation roadmap for traditional retailer'],
        
        ['CASE006', 'Strategy Consulting', 'Business Strategy', 'Market Entry', 'Digital Transformation',
         '2024-02-10', '2024-02-20', 'BANK006', 'ADV003', '', 'Resolved',
         'Strategy Advisory', 'Consulting', 10.0, 'Strategy Consulting', 'Consulting', 'United Kingdom',
         'Consultation', 90.0, 22.0, 'Market entry strategy for European expansion'],
        
        # Technology Cases
        ['CASE007', 'Technology Advisory', 'Technology Advisory', 'Cybersecurity', 'Cloud Migration',
         '2024-02-15', '2024-02-25', 'BANK007', 'ADV004', '', 'Resolved',
         'Technology Advisory', 'IT Consulting', 10.0, 'Technology Advisory', 'Technology', 'Singapore',
         'Assessment', 85.0, 20.0, 'Cybersecurity assessment for financial services firm'],
        
        ['CASE008', 'Technology Advisory', 'Technology Advisory', 'Digital Transformation', 'Cybersecurity',
         '2024-02-20', '2024-03-02', 'BANK008', 'ADV004', '', 'Resolved',
         'Technology Advisory', 'IT Consulting', 10.0, 'Technology Advisory', 'Technology', 'Singapore',
         'Consultation', 92.0, 24.0, 'Cloud migration strategy for manufacturing company'],
        
        # Risk Management Cases
        ['CASE009', 'Risk Advisory', 'Risk Management', 'Compliance Risk', 'Operational Risk',
         '2024-02-25', '2024-03-05', 'BANK009', 'ADV005', '', 'Resolved',
         'Risk Advisory', 'Compliance', 8.0, 'Risk Advisory', 'Risk', 'Australia',
         'Risk Assessment', 80.0, 16.0, 'Regulatory compliance assessment for fintech startup'],
        
        ['CASE010', 'Risk Advisory', 'Risk Management', 'Operational Risk', 'Compliance Risk',
         '2024-03-01', '2024-03-10', 'BANK010', 'ADV005', '', 'Resolved',
         'Risk Advisory', 'Compliance', 9.0, 'Risk Advisory', 'Risk', 'Australia',tus
         'Risk Assessment', 75.0, 18.0, 'Operational risk framework for logistics company']
    ]
    
    # Column names
    columns = [
        'Case ID', 'Services', 'Topics', 'Current Sub-Topic', 'Previous Sub-Topic',
        'Date Created', 'Date Submitted', 'Created By (Bank ID)',
        'Current Case Owner', 'Previous Case Owner', 'Status',
        'Current Advisory Group', 'Previous Advisory Group',
        'Overall Case Age (Days)', 'Business Function', 'Department', 'Country',
        'Category', 'Complexity', 'Time Spent',
        'Please describe your query'
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    # Save to Excel
    excel_file = 'sample_transactions.xlsx'
    df.to_excel(excel_file, index=False)
    
    print(f"✅ Created sample Excel file: {excel_file}")
    print(f"📊 Contains {len(df)} transactions across {df['Current Case Owner'].nunique()} advisors")
    print(f"🌍 Covers {df['Country'].nunique()} countries")
    print(f"📈 Services: {', '.join(df['Services'].unique())}")
    print(f"🎯 Topics: {', '.join(df['Topics'].unique())}")
    
    return excel_file

if __name__ == "__main__":
    create_sample_excel()
