#!/bin/bash

# Stop the script immediately if any command fails
set -e

# Wait for database to be ready
./wait-for-it.sh db:5432

# Apply migrations - Only run Django management commands for web service
echo "Running migrations..."
if [ "$1" = "gunicorn" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

echo "Creating sample data..."
python manage.py loaddata fixtures/shop.json
python manage.py initd

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the script
echo "Executing: $@"
# Finally, drop privileges and run the app
exec su-exec appuser "$@"