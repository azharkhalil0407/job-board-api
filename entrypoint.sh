#!/bin/sh
echo "Waiting for database..."
python manage.py migrate

echo "Starting server..."
exec "$@"