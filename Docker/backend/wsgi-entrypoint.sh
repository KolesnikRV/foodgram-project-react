#!/bin/bash

until cd /backend
do
    echo "Waiting for server volume..."
done

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

until python manage.py loaddata data.json
do
    echo "Waiting for load dump data..."
    sleep 2
done

until python manage.py collectstatic --noinput
do
    echo "Waiting for collect static..."
    sleep 2
done

gunicorn foodram.wsgi --bind 0.0.0.0:8000