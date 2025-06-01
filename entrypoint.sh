#!/bin/bash

# Wait for database to be ready
./wait-for-it.sh db:5432

# Apply migrations
echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating sample data..."
 python manage.py loaddata fixtures/shop.json

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the script
echo "Executing: $@"
exec "$@"