import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy_utils import database_exists, create_database
from main import create_app
from model.model import db, User, Admin, SuperAdmin, UsageLog, EmailTemplate, ToolAccess, Tool
from urllib.parse import urlparse

def migrate_db(source_url, target_url):
    # Create the target database if it doesn't exist
    engine = create_engine(target_url)
    if not database_exists(engine.url):
        create_database(engine.url)

    # Create a Flask app context
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = target_url

    with app.app_context():
        # Create all tables in the new database
        db.create_all()

        # Define the models to migrate
        models = [User, Admin, SuperAdmin, UsageLog, EmailTemplate, ToolAccess, Tool]

        # Migrate data for each model
        for model in models:
            if hasattr(model, '__tablename__'):
                table_name = model.__tablename__
                print(f"Migrating {table_name}")
                
                # Get column names
                columns = [column.key for column in inspect(model).columns]
                
                # Construct the SELECT query
                select_query = text(f"SELECT {', '.join(columns)} FROM {table_name}")
                
                try:
                    # Execute the query and fetch all rows
                    rows = db.session.execute(select_query).fetchall()
                    
                    # Insert data into the new database
                    for row in rows:
                        new_row = model(**dict(zip(columns, row)))
                        db.session.add(new_row)
                    
                    db.session.commit()
                except Exception as e:
                    print(f"Error migrating {table_name}: {str(e)}")
                    db.session.rollback()

    print("Migration completed successfully!")

if __name__ == "__main__":
    source_url = 'sqlite:///users.db'
    
    # Choose the target based on an environment variable or command-line argument
    environment = os.getenv('DEPLOY_ENV', 'local')  # Default to local if not specified
    
    if environment == 'production':
        target_url = os.getenv('DATABASE_URL_PRODUCTION', 'postgresql://postgres:AQtYQtjOxxItlHHycrYZduiNMhldOPBh@postgres.railway.internal:5432/railway')
    elif environment == 'staging':
        target_url = os.getenv('DATABASE_URL_STAGING','postgresql://postgres:WvllZGauoptALTJQZizPBIkjEfjRIXFk@postgres.railway.internal:5432/railway')
    else:
        target_url = os.getenv('DATABASE_URL_LOCAL', 'postgresql://postgres:iamxdv-172530@localhost/omnitool" /M')

    if not target_url:
        raise ValueError(f"No database URL found for {environment} environment")

    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)

    print(f"Migrating to {environment} environment")
    migrate_db(source_url, target_url)