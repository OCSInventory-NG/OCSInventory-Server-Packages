FROM ubuntu:24.04

ARG REPO="ocsinventory-frontend"
ARG VERSION=3.0.0-rc2

RUN apt-get update && \
        apt-get install -y nginx curl && \
        apt-get -y clean && \
        rm -r /var/lib/apt/lists/* && \
        rm /etc/nginx/sites-enabled/default

ADD https://github.com/OCSInventory-NG/OCSInventory-Server-Frontend-Rework/releases/download/${VERSION}/${REPO}-${VERSION}.tar.gz /usr/share/
RUN tar -xf /usr/share/${REPO}-${VERSION}.tar.gz -C /usr/share && \
    rm -rf /usr/share/${REPO}-${VERSION}.tar.gz && \
    chown -R www-data: /usr/share/${REPO}

COPY files/ocsinventory-frontend.conf /etc/nginx/sites-enabled/

RUN mkdir -p /var/log/ocsinventory-frontend

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK CMD ["curl", "--fail", "http://localhost/"]

ENTRYPOINT ["/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]
