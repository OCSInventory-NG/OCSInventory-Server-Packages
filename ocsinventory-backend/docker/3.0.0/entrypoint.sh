#!/bin/bash

if [ -f "/app/ocsinventory-backend/.env" ]; then
    source /app/ocsinventory-backend/.env
    
    # generating secret for Django 
    echo "Generating Django secret key ..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    # replace SECRET_KEY in .env file
    sed -i "s/SECRET_KEY=.*/SECRET_KEY='${SECRET_KEY}'/" /app/ocsinventory-backend/.env
    # replace POSTGRES_DB_HOST in .env file
    sed -i "s/POSTGRES_DB_HOST=.*/POSTGRES_DB_HOST='ocsinventory-db'/" /app/ocsinventory-backend/.env
fi

echo "Activating virtual environment ..."
source /app/ocs-venv/bin/activate
echo "Installing requirements ..."
pip3 install -r /app/ocsinventory-backend/requirements.txt

echo "Running database migrations ..."
python3 /app/ocsinventory-backend/manage.py migrate
deactivate

uwsgi --ini /app/uwsgi.ini

tail -f /dev/null