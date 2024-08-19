#!/bin/bash

python /app/ocsinventory-backend/manage.py migrate

uwsgi --ini /etc/uwsgi/apps-available/ocsinventory-backend.ini
