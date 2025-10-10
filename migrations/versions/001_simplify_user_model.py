"""
Database migration to simplify User model for enhanced authentication
This migration safely transitions from the multi-field registration to simplified registration

Revision ID: simplify_user_model
Revises: (previous_revision_id)
Create Date: 2024-12-XX
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, DateTime, Integer

# revision identifiers
revision = 'a1b2c3d4e5f6'  # Generated unique revision ID
down_revision = None  # This is the first migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Apply changes to simplify the User model
    """
    # Create a reference to the users table for data migration
    users_table = table('users',
        column('id', Integer),
        column('fname', String),
        column('lname', String),
        column('name', String),
        column('email_verified', Boolean),
        column('email_verification_token', String),
        column('email_verification_sent_at', DateTime),
        column('oauth_provider', String),
        column('oauth_id', String),
        column('requires_password_setup', Boolean),
        column('created_at', DateTime),
        column('updated_at', DateTime),
        column('last_login', DateTime),
        column('is_active', Boolean),
    )
    
    # Step 1: Add new columns
    print("Adding new authentication columns...")
    
    # Add the new name column (nullable initially)
    op.add_column('users', sa.Column('name', sa.String(100), nullable=True))
    
    # Add authentication enhancement columns (nullable initially to allow data migration)
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('email_verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('email_verification_sent_at', sa.DateTime(), nullable=True))
    
    # OAuth integration columns
    op.add_column('users', sa.Column('oauth_provider', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('requires_password_setup', sa.Boolean(), default=False))
    
    # Account management columns
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), default=True))
    
    # Step 2: Migrate existing data
    print("Migrating existing user data...")
    
    # Get database connection
    connection = op.get_bind()
    
    # Combine fname and lname into name field for existing users
    connection.execute(
        users_table.update().values(
            name=sa.func.concat(
                users_table.c.fname, 
                sa.text("' '"), 
                users_table.c.lname
            ),
            email_verified=True,  # Mark existing users as verified
            oauth_provider='manual',  # Mark as manual registration
            is_active=True,
            created_at=sa.func.now(),
            updated_at=sa.func.now()
        )
    )
    
    # Step 3: Make name and email_verified columns non-nullable after data migration
    op.alter_column('users', 'name', nullable=False)
    op.alter_column('users', 'email_verified', nullable=False)

    # Step 4: Make password column nullable (for OAuth users)
    op.alter_column('users', 'password', nullable=True)
    
    print("Migration completed successfully!")


def downgrade():
    """
    Revert changes (for rollback)
    """
    print("Rolling back user model changes...")
    
    # Remove new columns (in reverse order)
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'requires_password_setup')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
    op.drop_column('users', 'email_verification_sent_at')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'name')
    
    # Restore password column to non-nullable
    op.alter_column('users', 'password', nullable=False)
    
    print("Rollback completed!")


# Manual migration commands for development:
"""
To run this migration:

1. Generate the migration file:
   flask db revision --autogenerate -m "Simplify user model for enhanced auth"

2. Edit the generated file to include the data migration logic above

3. Run the migration:
   flask db upgrade

4. If rollback needed:
   flask db downgrade
"""