#!/bin/bash

uwsgi --ini /app/uwsgi.ini

tail -f /dev/null