-- AI Callcenter Agent Database Initialization
-- Designer: Abdullah Alawiss

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS callcenter_db;

-- Connect to the database
\c callcenter_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for performance
-- These will be created by Alembic migrations, but we prepare the database

-- Set timezone
SET timezone = 'Europe/Oslo';

-- Create schema for better organization (optional)
-- CREATE SCHEMA IF NOT EXISTS callcenter;

-- Insert initial data (optional)
-- This can be used for demo data or initial configuration

COMMENT ON DATABASE callcenter_db IS 'AI Callcenter Agent - Norwegian Telecom Compliance Analysis';
