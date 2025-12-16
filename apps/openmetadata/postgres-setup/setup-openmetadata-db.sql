-- Create database for OpenMetadata
CREATE DATABASE openmetadata_db;

-- Create user for OpenMetadata
CREATE USER openmetadata_user WITH PASSWORD 'PLACEHOLDER_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE openmetadata_db TO openmetadata_user;

-- Connect to the database and grant schema privileges
\c openmetadata_db
GRANT ALL ON SCHEMA public TO openmetadata_user;

