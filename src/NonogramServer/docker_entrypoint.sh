#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python src/NonogramServer/manage.py makemigrations
python src/NonogramServer/manage.py migrate

# Start server
echo "Starting server"
exec "$@"