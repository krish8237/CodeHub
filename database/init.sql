-- Initialize database for assessment platform
-- This script runs when PostgreSQL container starts for the first time

-- Create test database
CREATE DATABASE assessment_platform_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE assessment_platform TO postgres;
GRANT ALL PRIVILEGES ON DATABASE assessment_platform_test TO postgres;