#!/bin/bash

chown -R ocsbackend: /app/

su - ocsbackend

python3.11 -m venv /app/ocs-venv 

# Get in Venv
source /app/ocs-venv/bin/activate

# virtualenv and python deps
pip install -r /app/ocsinventory-backend/requirements.txt

tail -f /dev/null