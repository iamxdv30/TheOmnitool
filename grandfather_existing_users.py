"""
SIMPLIFIED Grandfather Existing Users Script - Just does the grandfathering
Focuses only on marking existing users as email verified

Usage: python grandfather_existing_users.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime
import logging

# Add the current directory to Python path to import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from model import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns_safely():
    """Add only essential missing columns with SQLite-compatible syntax"""
    try:
        # Check what columns exist in the users table
        result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
        existing_columns = [row[1] for row in result]
        
        logger.info(f"Current columns in users table: {existing_columns}")
        
        # Only add columns that are essential and SQLite-compatible
        columns_to_add = []
        
        if 'name' not in existing_columns:
            columns_to_add.append(('name', 'TEXT'))
        
        if 'created_at' not in existing_columns:
            # Use NULL default instead of CURRENT_TIMESTAMP to avoid SQLite error
            columns_to_add.append(('created_at', 'DATETIME'))
        
        if 'updated_at' not in existing_columns:
            columns_to_add.append(('updated_at', 'DATETIME'))
        
        if 'last_login' not in existing_columns:
            columns_to_add.append(('last_login', 'DATETIME'))
        
        if 'is_active' not in existing_columns:
            columns_to_add.append(('is_active', 'BOOLEAN DEFAULT 1'))
        
        # Add missing columns one by one with error handling
        added_columns = []
        for column_name, column_definition in columns_to_add:
            try:
                logger.info(f"Adding missing column: {column_name}")
                db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}"))
                added_columns.append(column_name)
            except Exception as e:
                logger.warning(f"⚠️  Could not add column {column_name}: {e}")
                # Continue with other columns
                continue
        
        if added_columns:
            db.session.commit()
            logger.info(f"✅ Successfully added columns: {added_columns}")
        
        # Populate name column if it was added and is empty
        if 'name' in added_columns:
            logger.info("Populating name column from fname/lname...")
            db.session.execute(text("""
                UPDATE users 
                SET name = COALESCE(fname || ' ' || lname, fname, lname, 'User') 
                WHERE name IS NULL OR name = ''
            """))
            db.session.commit()
            logger.info("✅ Name column populated")
        
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Error with column operations: {e}")
        # Don't fail the whole process, continue with grandfathering
        return True

def grandfather_existing_users():
    """Mark all existing users as email verified to allow them to continue logging in"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # First, try to add missing columns (but don't fail if it doesn't work)
            logger.info("🔧 Checking database schema...")
            add_missing_columns_safely()
            
            # Check if email_verified column exists
            result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
            existing_columns = [row[1] for row in result]
            
            if 'email_verified' not in existing_columns:
                logger.error("❌ email_verified column missing! Please run the database fix script first.")
                return
            
            logger.info("✅ email_verified column found!")
            
            # Get current status of users
            result = db.session.execute(text(
                "SELECT COUNT(*) as total, SUM(CASE WHEN email_verified = 1 THEN 1 ELSE 0 END) as verified FROM users"
            )).fetchone()
            
            total_users = result[0]
            verified_users = result[1] if result[1] is not None else 0
            unverified_users = total_users - verified_users
            
            logger.info(f"📊 Current user status:")
            logger.info(f"  - Total users: {total_users}")
            logger.info(f"  - Already verified: {verified_users}")
            logger.info(f"  - Unverified: {unverified_users}")
            
            if unverified_users == 0:
                logger.info("✅ All users are already verified!")
                logger.info("🎉 No grandfathering needed!")
                return
            
            # Get list of unverified users for logging
            unverified_list = db.session.execute(text(
                "SELECT id, username, email FROM users WHERE email_verified = 0 OR email_verified IS NULL"
            )).fetchall()
            
            logger.info(f"🔄 Grandfathering {len(unverified_list)} existing users:")
            for user in unverified_list:
                logger.info(f"  - User ID {user[0]}: {user[1]} ({user[2]})")
            
            # Perform the grandfathering - mark all existing users as verified
            logger.info("🔄 Updating users to verified status...")
            
            result = db.session.execute(text("""
                UPDATE users 
                SET email_verified = 1
                WHERE email_verified = 0 OR email_verified IS NULL
            """))
            
            affected_rows = result.rowcount
            db.session.commit()
            
            logger.info(f"✅ Successfully grandfathered {affected_rows} existing users!")
            
            # Verify the update worked
            final_result = db.session.execute(text(
                "SELECT COUNT(*) as total, SUM(CASE WHEN email_verified = 1 THEN 1 ELSE 0 END) as verified FROM users"
            )).fetchone()
            
            final_total = final_result[0]
            final_verified = final_result[1]
            
            logger.info(f"📊 Final status:")
            logger.info(f"  - Total users: {final_total}")
            logger.info(f"  - Verified users: {final_verified}")
            logger.info(f"  - Unverified users: {final_total - final_verified}")
            
            if final_verified == final_total:
                logger.info("🎉 SUCCESS: All existing users are now grandfathered and can log in!")
                return True
            else:
                logger.warning(f"⚠️  Still {final_total - final_verified} unverified users remaining")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error grandfathering users: {e}")
            db.session.rollback()
            raise

def verify_grandfathering():
    """Double-check that grandfathering worked"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get final user status
            result = db.session.execute(text(
                "SELECT id, username, email, email_verified FROM users ORDER BY id"
            )).fetchall()
            
            logger.info("📋 Final user verification status:")
            for user in result:
                status = "✅ VERIFIED" if user[3] else "❌ UNVERIFIED"
                logger.info(f"  - User ID {user[0]}: {user[1]} ({user[2]}) - {status}")
            
            verified_count = sum(1 for user in result if user[3])
            total_count = len(result)
            
            logger.info(f"📊 Summary: {verified_count}/{total_count} users are verified")
            
            return verified_count == total_count
            
        except Exception as e:
            logger.error(f"❌ Error verifying grandfathering: {e}")
            return False

if __name__ == "__main__":
    logger.info("🚀 Starting existing user grandfathering process...")
    
    success = grandfather_existing_users()
    
    if success:
        logger.info("✅ Grandfathering process completed successfully!")
        
        # Double-check the results
        logger.info("🔍 Verifying grandfathering results...")
        if verify_grandfathering():
            print("\n" + "="*60)
            print("🎉 GRANDFATHERING COMPLETED SUCCESSFULLY!")
            print("📧 Email verification will only apply to NEW registrations")
            print("🔐 ALL existing users can now log in normally")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠️  GRANDFATHERING INCOMPLETE!")
            print("Some users may still need manual verification")
            print("="*60)
    else:
        logger.error("❌ Grandfathering process failed!")
        print("\n" + "="*60)
        print("❌ GRANDFATHERING FAILED!")
        print("Please check the errors above and try again")
        print("="*60)