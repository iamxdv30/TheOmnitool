"""
CRITICAL DATABASE FIX - Add missing email_verified column
Run this script to fix the database schema immediately

Usage: python fix_database.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import logging

# Add the current directory to Python path to import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from model import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database():
    """Add missing email verification columns to users table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if email_verified column exists
            result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [row[1] for row in result]  # column name is at index 1
            
            logger.info(f"Current columns in users table: {columns}")
            
            if 'email_verified' not in columns:
                logger.info("Adding missing email_verified column...")
                
                # Add email_verified column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0 NOT NULL"
                ))
                
                # Add email_verification_token column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN email_verification_token TEXT"
                ))
                
                # Add email_verification_sent_at column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN email_verification_sent_at DATETIME"
                ))
                
                # Add oauth_provider column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN oauth_provider TEXT"
                ))
                
                # Add oauth_id column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN oauth_id TEXT"
                ))
                
                # Add requires_password_setup column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN requires_password_setup BOOLEAN DEFAULT 0"
                ))
                
                # Add created_at column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
                ))
                
                # Add updated_at column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
                ))
                
                # Add last_login column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN last_login DATETIME"
                ))
                
                # Add is_active column
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"
                ))
                
                # Add name column if it doesn't exist
                if 'name' not in columns:
                    db.session.execute(text(
                        "ALTER TABLE users ADD COLUMN name TEXT"
                    ))
                    
                    # Populate name column from fname and lname
                    db.session.execute(text(
                        "UPDATE users SET name = COALESCE(fname, '') || ' ' || COALESCE(lname, '') WHERE name IS NULL"
                    ))
                
                db.session.commit()
                logger.info("✅ Successfully added missing columns!")
                
                # Update existing users to have email_verified = False (unverified)
                result = db.session.execute(text(
                    "UPDATE users SET email_verified = 0 WHERE email_verified IS NULL"
                ))
                db.session.commit()
                
                logger.info(f"✅ Updated {result.rowcount} existing users to unverified status")
                
                # Show updated table structure
                result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
                new_columns = [row[1] for row in result]
                logger.info(f"Updated columns in users table: {new_columns}")
                
            else:
                logger.info("✅ email_verified column already exists!")
                
                # Check current users
                result = db.session.execute(text(
                    "SELECT id, username, email, email_verified FROM users"
                )).fetchall()
                
                logger.info("Current users in database:")
                for row in result:
                    logger.info(f"  User ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Verified: {row[3]}")
                
        except OperationalError as e:
            logger.error(f"Database operation failed: {e}")
            db.session.rollback()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    logger.info("🔧 Starting database fix...")
    fix_database()
    logger.info("🎉 Database fix completed!")