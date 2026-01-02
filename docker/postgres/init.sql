-- Enterprise Boilerplate PostgreSQL Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Enable required extensions for enterprise features
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Create custom functions for enhanced search capabilities
CREATE OR REPLACE FUNCTION normalize_text(text)
RETURNS text AS $$
BEGIN
    RETURN unaccent(lower($1));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create indexes for common search patterns (will be created by migrations)
-- These are examples for reference:
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_normalized 
-- ON users (normalize_text(email));

-- Set default configurations
ALTER SYSTEM SET search_path TO public, extensions;
ALTER SYSTEM SET timezone TO 'UTC';

-- Grant necessary permissions to the default user
-- Note: The actual user will be created by PostgreSQL based on POSTGRES_USER env var

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'Enterprise Boilerplate PostgreSQL initialization completed';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pg_trgm, unaccent, pgvector';
END $$;
