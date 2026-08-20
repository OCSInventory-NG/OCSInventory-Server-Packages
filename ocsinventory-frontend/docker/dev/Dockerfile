# Dev/CI image: builds from an arbitrary branch, tag or full commit SHA of
# OCSInventory-Server-Frontend-Rework instead of a published release tarball
#
# Example:
#   docker build \
#     --build-arg FRONTEND_REF=my-feature-branch \
#     -t ocsinventory/ocsinventory-frontend:dev \
#     ocsinventory-frontend/docker/dev
#
# FRONTEND_REF accepts a branch name, a tag, or a full 40-character commit SHA
# (GitHub allows fetching any reachable commit over HTTPS on public repos;
# abbreviated SHAs are not resolvable this way).
ARG FRONTEND_REPO="https://github.com/gillesdubois/OCSInventory-Server-Frontend-Rework.git"
ARG FRONTEND_REF="dev"

FROM node:20-slim AS build

ARG FRONTEND_REPO
ARG FRONTEND_REF

WORKDIR /app

RUN apt-get update && apt-get install -y git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Fetch the exact branch/tag/commit under test instead of a release archive.
RUN git init -q ocsinventory-frontend \
    && cd ocsinventory-frontend \
    && git remote add origin "${FRONTEND_REPO}" \
    && git fetch --depth 1 origin "${FRONTEND_REF}" \
    && git checkout -q FETCH_HEAD

WORKDIR /app/ocsinventory-frontend
RUN npm ci
RUN npm run build


FROM ubuntu:latest

ARG FRONTEND_REPO
ARG FRONTEND_REF
LABEL org.opencontainers.image.title="ocsinventory-frontend (dev)"
LABEL org.opencontainers.image.source="${FRONTEND_REPO}"
LABEL org.opencontainers.image.revision="${FRONTEND_REF}"
LABEL org.ocsinventory.image.kind="dev"

RUN apt update && apt dist-upgrade -y && \
        apt install -y nginx curl && \
        apt-get -y clean && \
        rm -r /var/lib/apt/lists/* && \
        rm /etc/nginx/sites-enabled/default

COPY --from=build /app/ocsinventory-frontend/dist /usr/share/ocsinventory-frontend
RUN chown -R www-data: /usr/share/ocsinventory-frontend

COPY files/ocsinventory-frontend.conf /etc/nginx/sites-enabled/

RUN mkdir -p /var/log/ocsinventory-frontend

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]
