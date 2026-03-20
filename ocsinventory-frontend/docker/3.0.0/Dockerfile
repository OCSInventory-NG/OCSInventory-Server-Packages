FROM ubuntu:latest

ARG REPO="ocsinventory-frontend"
ARG VERSION=3.0.0

RUN apt update && apt dist-upgrade -y && \
        apt install -y apache2 && \
        a2enmod rewrite && \
        apt-get -y clean && \
	    rm -r /var/lib/apt/lists/* && \
        rm /etc/apache2/sites-enabled/000-default.conf

COPY files/${REPO}-${VERSION}.tar.gz /usr/share
RUN cd /usr/share && \
    tar -xf ${REPO}-${VERSION}.tar.gz && \
    rm -rf ${REPO}-${VERSION}.tar.gz && \
    chown -R www-data: /usr/share/${REPO}

COPY files/ocsinventory-frontend.conf /etc/apache2/sites-enabled/

RUN mkdir -p /var/log/ocsinventory-frontend

EXPOSE 80

CMD apachectl -D FOREGROUND