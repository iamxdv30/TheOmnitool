-- PostgreSQL Initialization Script
-- This file runs automatically when the container is first created
-- Location: /docker-entrypoint-initdb.d/init-db.sql

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant all privileges to the omnitool user
GRANT ALL PRIVILEGES ON DATABASE omnitool_dev TO omnitool;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL initialized for Omnitool development';
    RAISE NOTICE 'Database: omnitool_dev';
    RAISE NOTICE 'User: omnitool';
END $$;
