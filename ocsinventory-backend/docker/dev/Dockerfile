# Dev/CI image: builds from an arbitrary branch, tag or full commit SHA of
# OCSInventory-Server-Backend-Rework instead of a published release tarball
#
# Example:
#   docker build \
#     --build-arg BACKEND_REF=my-feature-branch \
#     -t ocsinventory/ocsinventory-backend:dev \
#     ocsinventory-backend/docker/dev
#
# BACKEND_REF accepts a branch name, a tag, or a full 40-character commit SHA
# (GitHub allows fetching any reachable commit over HTTPS on public repos;
# abbreviated SHAs are not resolvable this way).
# no rebuild needed.
ARG BACKEND_REPO="https://github.com/OCSInventory-NG/OCSInventory-Server-Backend-Rework.git"
ARG BACKEND_REF="dev"

FROM python:3.12-slim AS build

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

ARG BACKEND_REPO
ARG BACKEND_REF

WORKDIR /app

# build-time dependencies (headers/compilers needed to build python-ldap and
# mysqlclient; git to fetch the source at BACKEND_REF)
RUN apt-get update && apt-get install -y \
    build-essential python3-dev \
    libldap2-dev libsasl2-dev \
    default-libmysqlclient-dev pkg-config \
    git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Fetch the exact branch/tag/commit under test instead of a release archive.
RUN git init -q ocsinventory-backend \
    && cd ocsinventory-backend \
    && git remote add origin "${BACKEND_REPO}" \
    && git fetch --depth 1 origin "${BACKEND_REF}" \
    && git checkout -q FETCH_HEAD

# create the venv
RUN python3 -m venv /app/ocs-venv \
    && /app/ocs-venv/bin/pip install --upgrade pip \
    && /app/ocs-venv/bin/pip install uwsgi \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements.txt \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements_psql.txt \
    && /app/ocs-venv/bin/pip install -r /app/ocsinventory-backend/requirements_mysql.txt

COPY files/uwsgi/uwsgi.ini /app/uwsgi.ini


FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

ARG BACKEND_REPO
ARG BACKEND_REF
LABEL org.opencontainers.image.title="ocsinventory-backend (dev)"
LABEL org.opencontainers.image.source="${BACKEND_REPO}"
LABEL org.opencontainers.image.revision="${BACKEND_REF}"
LABEL org.ocsinventory.image.kind="dev"

WORKDIR /app

# runtime dependencies (libldap2/libsasl2 needed by python-ldap, libmariadb3
# needed by mysqlclient - psycopg2-binary already bundles libpq, libexpat1
# needed by uwsgi)
RUN apt-get update && apt-get install -y \
    libldap2 libsasl2-2 libmariadb3 libexpat1 curl \
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
