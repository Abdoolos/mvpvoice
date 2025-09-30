# Alembic Database Migrations

This folder contains database migration files managed by Alembic.

## Designer: Abdullah Alawiss

Use Alembic to manage database schema changes:

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
