#!/bin/bash

python /opt/ocsinventory-backend/manage.py migrate

uwsgi --ini /etc/uwsgi/apps-available/ocsinventory-backend.ini
