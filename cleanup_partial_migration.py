"""
Cleanup script for partial migration failure.
This script removes partially added columns from failed migration attempt.
"""
from main import create_app
from model import db
import sqlalchemy

app = create_app()

with app.app_context():
    # Get database connection
    connection = db.engine.connect()
    trans = connection.begin()

    try:
        # Check what columns exist
        inspector = sqlalchemy.inspect(db.engine)
        existing_columns = [c['name'] for c in inspector.get_columns('users')]

        print("Current columns in users table:")
        for col in existing_columns:
            print(f"  - {col}")

        # List of columns that might have been partially added
        columns_to_remove = [
            'email_verified',
            'email_verification_token',
            'email_verification_sent_at',
            'oauth_provider',
            'oauth_id',
            'requires_password_setup',
            'created_at',
            'updated_at',
            'last_login',
            'is_active',
            'name'
        ]

        # Drop columns that exist
        for column in columns_to_remove:
            if column in existing_columns:
                print(f"Dropping column: {column}")
                connection.execute(sqlalchemy.text(f"ALTER TABLE users DROP COLUMN IF EXISTS {column}"))

        # Reset alembic version to allow clean migration
        print("Resetting alembic_version...")
        connection.execute(sqlalchemy.text("DELETE FROM alembic_version"))

        trans.commit()
        print("\nCleanup completed successfully!")

    except Exception as e:
        trans.rollback()
        print(f"Error during cleanup: {e}")
        raise
    finally:
        connection.close()
