-- File: sql/00_create_schemas.sql
-- Purpose: Create base schemas for the shopsphere database

-- Connect to the target database first (in pgAdmin or psql):
-- \c shopsphere

-- Create schemas for different stages of the pipeline
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Verify schemas
-- SELECT schema_name FROM information_schema.schemata;
