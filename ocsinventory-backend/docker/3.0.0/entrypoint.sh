#!/bin/bash

. /opt/ocsinventory-backend/venv/bin/activate

python /opt/ocsinventory-backend/manage.py migrate

uwsgi --ini /etc/uwsgi/apps-available/ocsinventory-backend.ini
