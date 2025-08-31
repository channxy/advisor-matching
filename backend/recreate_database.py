#!/usr/bin/env python3
"""
Recreate database with correct schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def recreate_database():
    """Recreate the database with correct schema"""
    try:
        print("🔧 Recreating database with correct schema...")
        
        # Import database components
        from app.models.database import engine, Base
        from app.models.advisor import Advisor
        from app.models.case import Case
        from app.models.assignment import Assignment
        from app.models.tag import Tag
        
        # Drop all tables
        print("🗑️  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("🏗️  Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database recreated successfully!")
        
        # Verify the schema
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        if 'advisors' in inspector.get_table_names():
            columns = inspector.get_columns('advisors')
            column_names = [col['name'] for col in columns]
            
            print(f"📋 Advisors table columns: {column_names}")
            
            if 'expertise_tags' in column_names:
                print("✅ expertise_tags column exists in new schema")
            else:
                print("❌ expertise_tags column still missing!")
            
            if 'expertise_areas' in column_names:
                print("❌ expertise_areas column still exists!")
            else:
                print("✅ expertise_areas column does not exist (correct)")
        
        print("\n🎉 Database recreation complete!")
        print("💡 You can now upload Excel files without expertise_areas errors")
        
    except Exception as e:
        print(f"❌ Database recreation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    recreate_database()
