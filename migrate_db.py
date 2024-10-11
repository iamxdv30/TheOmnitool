import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy_utils import database_exists, create_database
from main import create_app
from model.model import db, User, Admin, SuperAdmin, UsageLog, EmailTemplate, ToolAccess, Tool

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def migrate_db(source_url, target_url):
    logging.info(f"Starting migration from {source_url} to {target_url}")

    # Correct the target URL if necessary
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)

    # Create the target database if it doesn't exist, but only for local SQLite
    engine = create_engine(target_url)
    if target_url.startswith("sqlite://") and not database_exists(engine.url):
        create_database(engine.url)

    # Create a Flask app context
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = target_url

    with app.app_context():
        # Create all tables in the new database
        db.create_all()

        # Define the models to migrate
        models = [User, Admin, SuperAdmin, UsageLog, EmailTemplate, ToolAccess, Tool]

        # Migrate data for each model
        for model in models:
            if hasattr(model, "__tablename__"):
                table_name = model.__tablename__
                logging.info(f"Migrating {table_name}")

                # Get column names
                columns = [column.key for column in inspect(model).columns]

                # Construct the SELECT query
                select_query = text(f"SELECT {', '.join(columns)} FROM {table_name}")

                try:
                    # Execute the query and fetch all rows
                    rows = db.session.execute(select_query).fetchall()

                    # Insert data into the new database
                    for row in rows:
                        try:
                            new_row = model(**dict(zip(columns, row)))
                            db.session.add(new_row)
                        except Exception as insert_error:
                            logging.error(f"Failed to insert row in {table_name}: {insert_error}")
                            db.session.rollback()

                    db.session.commit()
                except Exception as e:
                    logging.error(f"Error migrating {table_name}: {str(e)}")
                    db.session.rollback()

    logging.info("Migration completed successfully!")


if __name__ == "__main__":
    try:
        # Check the IS_LOCAL environment variable
        is_local = os.getenv("IS_LOCAL", "true").lower() == "true"
        if not is_local:
            logging.info("Skipping migration because IS_LOCAL is set to false.")
            exit(0)

        source_url = "sqlite:///users.db"

        # Choose the target based on the environment
        environment = os.getenv("FLASK_ENV", "development")
        logging.info(f"Running migration for {environment} environment")

        if environment in ["production", "staging"]:
            target_url = os.getenv("DATABASE_URL", "")
        else:
            target_url = "sqlite:///users.db"  # Use SQLite for local development

        if not target_url:
            raise ValueError(f"No DATABASE_URL found for {environment} environment")

        # Ensure the target_url uses the correct format for PostgreSQL
        if target_url.startswith("postgres://"):
            target_url = target_url.replace("postgres://", "postgresql://", 1)

        # Perform the migration
        migrate_db(source_url, target_url)
    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
        raise
