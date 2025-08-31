#!/usr/bin/env python3
"""
Clear all dummy data from the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clear_dummy_data():
    """Clear all dummy data from the database"""
    try:
        print("🧹 Clearing all dummy data from database...")
        
        from app.models.database import SessionLocal
        from app.models.advisor import Advisor
        from app.models.case import Case
        from app.models.assignment import Assignment
        from app.models.tag import Tag
        
        db = SessionLocal()
        
        try:
            # Count existing data
            advisor_count = db.query(Advisor).count()
            case_count = db.query(Case).count()
            assignment_count = db.query(Assignment).count()
            tag_count = db.query(Tag).count()
            
            print(f"📊 Current data in database:")
            print(f"   👤 Advisors: {advisor_count}")
            print(f"   📋 Cases: {case_count}")
            print(f"   🔗 Assignments: {assignment_count}")
            print(f"   🏷️  Tags: {tag_count}")
            
            # Clear all data
            print("\n🗑️  Clearing all data...")
            
            # Delete in correct order to avoid foreign key constraints
            db.query(Assignment).delete()
            db.query(Tag).delete()
            db.query(Case).delete()
            db.query(Advisor).delete()
            
            db.commit()
            
            print("✅ All dummy data cleared successfully!")
            
            # Verify clearing
            advisor_count_after = db.query(Advisor).count()
            case_count_after = db.query(Case).count()
            assignment_count_after = db.query(Assignment).count()
            tag_count_after = db.query(Tag).count()
            
            print(f"\n📊 Database after clearing:")
            print(f"   👤 Advisors: {advisor_count_after}")
            print(f"   📋 Cases: {case_count_after}")
            print(f"   🔗 Assignments: {assignment_count_after}")
            print(f"   🏷️  Tags: {tag_count_after}")
            
            if advisor_count_after == 0:
                print("\n🎉 Database is now clean and ready for your Excel data!")
                print("💡 Upload your transactions.xlsx file to create real advisor profiles.")
            else:
                print("\n⚠️  Some data still exists. Please check manually.")
                
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_dummy_data()
