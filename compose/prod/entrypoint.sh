#!/bin/bash

# Stop the script immediately if any command fails
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h db -p 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating sample data..."
python manage.py loaddata fixtures/shop.json
python manage.py initd

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the script
echo "Executing: $@"
exec "$@"