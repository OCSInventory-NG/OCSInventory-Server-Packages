# hadolint CI dry-run: dummy comment to exercise PR diff annotations
ARG REPO="ocsinventory-backend"
ARG VERSION=3.0.0-rc2

FROM python:3.12-slim AS build

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

ARG REPO
ARG VERSION

WORKDIR /app

# build-time dependencies (headers/compilers needed to build python-ldap and friends)
RUN apt-get update && apt-get install -y \
    build-essential python3-dev \
    libldap2-dev libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# download and extract source code to /app
ADD https://github.com/OCSInventory-NG/OCSInventory-Server-Backend-Rework/releases/download/${VERSION}/${REPO}-${VERSION}.tar.gz /app/
RUN tar -xzf /app/${REPO}-${VERSION}.tar.gz -C /app \
    && rm /app/${REPO}-${VERSION}.tar.gz

# create the venv
RUN python3 -m venv /app/ocs-venv \
    && /app/ocs-venv/bin/pip install --upgrade pip \
    && /app/ocs-venv/bin/pip install uwsgi \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements.txt \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements_psql.txt

COPY files/uwsgi/uwsgi.ini /app/uwsgi.ini


FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# runtime dependencies (libldap2/libsasl2 needed by python-ldap, libexpat1 needed by uwsgi)
RUN apt-get update && apt-get install -y \
    libldap2 libsasl2-2 libexpat1 curl \
    && rm -rf /var/lib/apt/lists/*

# ocsbackend user and permissions
RUN useradd ocsbackend --home /app --shell /bin/bash

COPY --from=build --chown=ocsbackend:ocsbackend /app /app

RUN chmod 644 /app/uwsgi.ini

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
