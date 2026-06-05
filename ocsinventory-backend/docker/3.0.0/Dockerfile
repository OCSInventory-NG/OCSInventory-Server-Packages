FROM tiangolo/uwsgi-nginx:python3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND noninteractive

ARG REPO="ocsinventory-backend"
ARG VERSION=3.0.0-rc1

WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install -y \
    build-essential python3-dev \
    libldap2-dev libsasl2-dev slapd ldap-utils tox \
    lcov valgrind \
    && rm -rf /var/lib/apt/lists/*

# extract source code to /app
COPY files/${REPO}-${VERSION}.tar.gz /app/
RUN tar -xzf /app/${REPO}-${VERSION}.tar.gz -C /app

# ocsbackend user and permissions
RUN useradd ocsbackend --home /app --shell /bin/bash \
    && chown -R ocsbackend:ocsbackend /app

# create the venv
USER ocsbackend
RUN python3 -m venv /app/ocs-venv \
    && /app/ocs-venv/bin/pip install --upgrade pip \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements.txt \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements_psql.txt

USER root

COPY files/uwsgi/uwsgi.ini /app/
RUN chown -R ocsbackend:ocsbackend /app \
    && chmod 644 /app/uwsgi.ini

# log directory and permissions
RUN mkdir -p /var/log/ocsinventory-backend \
    && chown -R ocsbackend:ocsbackend /var/log/ocsinventory-backend \
    && chmod 755 /var/log/ocsinventory-backend

# Socket setup
RUN mkdir -p /var/run/ocsinventory-backend \
    && chown -R ocsbackend:ocsbackend /var/run/ocsinventory-backend \
    && chmod 755 /var/run/ocsinventory-backend

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ocsbackend

ENTRYPOINT ["/entrypoint.sh"]

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]

HEALTHCHECK CMD curl --fail http://localhost:8000 || exit 1