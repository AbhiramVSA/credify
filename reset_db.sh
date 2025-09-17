#!/bin/bash

# Reset database script
echo "Resetting database for UUID conversion..."

# Stop any running containers
echo "Stopping containers..."
docker-compose down

# Remove the database volume to start fresh
echo "Removing database volume..."
docker volume rm alemno-backend_postgres_data 2>/dev/null || true

# Remove migration files (keep __init__.py)
echo "Cleaning migration files..."
rm -f src/core/migrations/000*.py

# Recreate initial migration
echo "Creating fresh migrations..."
echo "from django.db import migrations

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = []
" > src/core/migrations/0001_initial.py

# Start containers
echo "Starting fresh containers..."
docker-compose up --build