FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ARG REPO="ocsinventory-backend"
ARG VERSION=3.0.0

WORKDIR /usr/share/${REPO}

# system dependencies
RUN apt-get update && apt-get install -y \
    uwsgi \
    uwsgi-plugin-python3 \
    build-essential python3-dev \
    libldap2-dev libsasl2-dev slapd ldap-utils tox \
    lcov valgrind \
    && rm -rf /var/lib/apt/lists/*


COPY files/${REPO}-${VERSION}.tar.gz /usr/share/
RUN tar -xzvf /usr/share/${REPO}-${VERSION}.tar.gz -C /usr/share/${REPO} --strip-components=1

# virtualenv and python deps
RUN pip install -r /usr/share/${REPO}/requirements.txt

COPY files/uwsgi/ocsinventory-backend.ini /etc/uwsgi/apps-available/

RUN mkdir -p /var/log/ocsinventory-backend \
    && chmod 777 /var/log/ocsinventory-backend

EXPOSE 80

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
