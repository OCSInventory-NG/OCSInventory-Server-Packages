#!/bin/bash
# vim:sw=4:ts=4:et

set -e

if [ ! -f "/app/ocsinventory-backend/.env" ]; then
    if [ -f "/app/ocsinventory-backend/.env-sample" ]; then
        echo ".env not found. Creating it from .env-sample..."
        cp /app/ocsinventory-backend/.env-sample /app/ocsinventory-backend/.env
    else
        echo ".env and .env-sample not found. Exiting."
        exit 1
    fi
fi

if [ -f "/app/ocsinventory-backend/.env" ]; then
    source /app/ocsinventory-backend/.env

    # User-configurable settings, overridable via environment variables.
    # Fall back to the value already present in the .env file if unset.
    DEBUG="${DEBUG_ENV:-${DEBUG}}"
    FRONTEND_REDIRECT="${FRONTEND_REDIRECT_ENV:-${FRONTEND_REDIRECT}}"
    DB_ENGINE="${DB_ENGINE_ENV:-${DB_ENGINE}}"
    DB_NAME="${DB_NAME_ENV:-${DB_NAME}}"
    DB_USER="${DB_USER_ENV:-${DB_USER}}"
    DB_PASSWORD="${DB_PASSWORD_ENV:-${DB_PASSWORD}}"
    DB_HOST="${DB_HOST_ENV:-${DB_HOST}}"
    DB_PORT="${DB_PORT_ENV:-${DB_PORT}}"

    # Escape backslashes, forward slashes and ampersands so sed's replacement
    # stays well-formed regardless of what a user puts in these values.
    escape_for_sed() {
        printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
    }

    DEBUG_ESCAPED=$(escape_for_sed "${DEBUG}")
    FRONTEND_REDIRECT_ESCAPED=$(escape_for_sed "${FRONTEND_REDIRECT}")
    DB_ENGINE_ESCAPED=$(escape_for_sed "${DB_ENGINE}")
    DB_NAME_ESCAPED=$(escape_for_sed "${DB_NAME}")
    DB_USER_ESCAPED=$(escape_for_sed "${DB_USER}")
    DB_PASSWORD_ESCAPED=$(escape_for_sed "${DB_PASSWORD}")
    DB_HOST_ESCAPED=$(escape_for_sed "${DB_HOST}")
    DB_PORT_ESCAPED=$(escape_for_sed "${DB_PORT}")

    sed -i "s/^DEBUG=.*/DEBUG=${DEBUG_ESCAPED}/" /app/ocsinventory-backend/.env
    sed -i "s/^FRONTEND_REDIRECT=.*/FRONTEND_REDIRECT='${FRONTEND_REDIRECT_ESCAPED}'/" /app/ocsinventory-backend/.env
    sed -i "s/^DB_ENGINE=.*/DB_ENGINE='${DB_ENGINE_ESCAPED}'/" /app/ocsinventory-backend/.env
    sed -i "s/^DB_NAME=.*/DB_NAME='${DB_NAME_ESCAPED}'/" /app/ocsinventory-backend/.env
    sed -i "s/^DB_USER=.*/DB_USER='${DB_USER_ESCAPED}'/" /app/ocsinventory-backend/.env
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD='${DB_PASSWORD_ESCAPED}'/" /app/ocsinventory-backend/.env
    sed -i "s/^DB_HOST=.*/DB_HOST='${DB_HOST_ESCAPED}'/" /app/ocsinventory-backend/.env
    sed -i "s/^DB_PORT=.*/DB_PORT='${DB_PORT_ESCAPED}'/" /app/ocsinventory-backend/.env

    # Generating Django secret key (not user-configurable)
    echo "Generating Django secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" | sed -e 's/[\/&]/\\&/g')
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY='${SECRET_KEY}'/" /app/ocsinventory-backend/.env
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

# Pass control to CMD in Dockerfile
if [ -z "$1" ]; then
    echo "No command provided. Exiting."
    exit 1
fi

exec "$@"
