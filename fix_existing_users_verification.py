"""
Fix existing users email verification status
Sets email_verified = True for all existing users
"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['IS_LOCAL'] = 'true'

from main import create_app
from model import db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_existing_users():
    """Set email_verified = True for all existing users"""
    app = create_app()
    with app.app_context():
        try:
            # Update all users with email_verified = False to True
            # These are existing users who should be grandfathered in
            logger.info("Updating existing users to verified status...")

            result = db.session.execute(
                text("UPDATE users SET email_verified = 1 WHERE email_verified = 0 OR email_verified IS NULL")
            )

            db.session.commit()

            logger.info(f"✅ Updated {result.rowcount} users to verified status")

            # Verify the fix
            verified_count = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE email_verified = 1")
            ).scalar()

            unverified_count = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE email_verified = 0 OR email_verified IS NULL")
            ).scalar()

            logger.info(f"Total verified users: {verified_count}")
            logger.info(f"Total unverified users: {unverified_count}")

            # Show specific user status
            user_status = db.session.execute(
                text("SELECT username, email_verified FROM users")
            ).fetchall()

            logger.info("\nUser verification status:")
            for username, verified in user_status:
                status = "✅ VERIFIED" if verified else "❌ NOT VERIFIED"
                logger.info(f"  {username}: {status}")

        except Exception as e:
            logger.error(f"Failed to update users: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    fix_existing_users()
