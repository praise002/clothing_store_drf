#!/bin/bash

# Stop the script immediately if any command fails
set -e

# Wait for database to be ready
./wait-for-it.sh db:5432 -- echo "PostgreSQL is up!"

# Apply migrations - Only run Django management commands for web service
if [ "$SERVICE_TYPE" = "web" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput
  
  echo "Creating sample data..."
  python manage.py loaddata fixtures/shop.json
  python manage.py initd

  # Collect static files
  echo "Collecting static files..."
  python manage.py collectstatic --noinput

  exec gunicorn --bind 0.0.0.0:8000 clothing_store.wsgi:application
elif [ "$SERVICE_TYPE" = "celery" ]|| [ "$SERVICE_TYPE" = "celery-beat" ]; then
  echo "Waiting for Django to be ready..."
  while ! curl -s http://web:8000 >/dev/null; do
    echo "Django not ready. Retrying in 5s..."
    sleep 5
  done
  
  if [ "$SERVICE_TYPE" = "celery" ]; then
    exec celery -A clothing_store worker --loglevel=info
  else
    exec celery -A clothing_store beat --loglevel=info
  fi
fi

# Execute the command passed to the script
echo "Executing: $@"
exec "$@"