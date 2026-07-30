FROM ubuntu:latest

ARG REPO="ocsinventory-frontend"
ARG VERSION=3.0.0-rc1

RUN apt update && apt dist-upgrade -y && \
        apt install -y nginx curl && \
        apt-get -y clean && \
        rm -r /var/lib/apt/lists/* && \
        rm /etc/nginx/sites-enabled/default

ADD https://github.com/OCSInventory-NG/OCSInventory-Server-Frontend-Rework/releases/download/${VERSION}/${REPO}-${VERSION}.tar.gz /usr/share/
RUN cd /usr/share && \
    tar -xf ${REPO}-${VERSION}.tar.gz && \
    rm -rf ${REPO}-${VERSION}.tar.gz && \
    chown -R www-data: /usr/share/${REPO}

COPY files/ocsinventory-frontend.conf /etc/nginx/sites-enabled/

RUN mkdir -p /var/log/ocsinventory-frontend

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]

CMD nginx -g "daemon off;"
