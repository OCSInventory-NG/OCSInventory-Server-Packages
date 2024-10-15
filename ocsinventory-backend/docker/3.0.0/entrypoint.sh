#!/bin/bash
# vim:sw=4:ts=4:et

set -e

if [ -f "/app/ocsinventory-backend/.env" ]; then
    source /app/ocsinventory-backend/.env

    # Generating Django secret key
    echo "Generating Django secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" | sed -e 's/[\/&]/\\&/g')
    sed -i "s/SECRET_KEY=.*/SECRET_KEY='${SECRET_KEY}'/" /app/ocsinventory-backend/.env

    # Replace DB_HOST in .env file
    sed -i "s/DB_HOST=.*/DB_HOST='ocsinventory-db'/" /app/ocsinventory-backend/.env
fi

echo "Activating virtual environment..."
if [ -f "/app/ocs-venv/bin/activate" ]; then
    source /app/ocs-venv/bin/activate
else
    echo "Virtual environment not found. Exiting."
    exit 1
fi

# Uncomment if you want to reinstall dependencies each time (optional)
# echo "Installing requirements ..."
# pip3 install -r /app/ocsinventory-backend/requirements.txt

if [ -f "/app/ocsinventory-backend/manage.py" ]; then
    echo "Running database migrations..."
    if ! python3 /app/ocsinventory-backend/manage.py migrate; then
        echo "Migration failed. Exiting."
        exit 1
    fi
else
    echo "manage.py not found. Exiting."
    exit 1
fi

deactivate

# Pass control to CMD in Dockerfile
if [ -z "$1" ]; then
    echo "No command provided. Exiting."
    exit 1
fi

exec "$@"
