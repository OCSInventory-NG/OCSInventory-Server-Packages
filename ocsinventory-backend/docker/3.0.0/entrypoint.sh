#!/bin/bash

python /usr/share/ocsinventory-backend/manage.py migrate

uwsgi --ini /etc/uwsgi/apps-available/ocsinventory-backend.ini
