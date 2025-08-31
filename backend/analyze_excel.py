#!/usr/bin/env python3
"""
Script to analyze Excel file structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
    
    # Read the Excel file
    df = pd.read_excel('transactions.xlsx')
    
    print(f"\n📊 Excel File Analysis:")
    print(f"Shape: {df.shape}")
    print(f"Columns ({len(df.columns)}):")
    
    for i, col in enumerate(df.columns):
        print(f"  {i+1:2d}. {col}")
    
    print(f"\n📋 Sample Data (first 2 rows):")
    print(df.head(2).to_string())
    
    print(f"\n🔍 Data Types:")
    print(df.dtypes)
    
    print(f"\n📈 Missing Values:")
    missing = df.isnull().sum()
    print(missing[missing > 0])
    
    # Check for date columns
    date_cols = []
    for col in df.columns:
        if 'date' in col.lower() or 'completion' in col.lower() or 'submitted' in col.lower():
            date_cols.append(col)
    
    print(f"\n📅 Potential Date Columns: {date_cols}")
    
    # Check for query/title columns
    query_cols = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['query', 'title', 'description', 'explain', 'please']):
            query_cols.append(col)
    
    print(f"\n❓ Potential Query Columns: {query_cols}")
    
except ImportError as e:
    print(f"❌ Error importing pandas: {e}")
    print("Please install pandas: pip install pandas openpyxl")
except Exception as e:
    print(f"❌ Error analyzing Excel: {e}")
