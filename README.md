# OCS Inventory Server Packages

**WORK IN PROGRESS**

Packages repository for OCS Inventory Rework.

## Structure

```
ocsinventory-backend/
  rpm/
    sources/
      .env
      ocsinventory-backend.conf
      ocsinventory-backend.ini
      ocsinventory-backend-X.X.X.tar.gz
    specs/
      ocsinventory-backend.spec
  deb/
    ocsinventory-backend/
      debian/
      etc/nginx/sites-available/
        ocsinventory-backend
      etc/uwsgi/apps-available/
        ocsinventory-backend.ini
      usr/share/ocsinventory-backend/
  docker/
    X.X.X/
      files/
        nginx/
          ocsinventory-backend.conf
        uwsgi/
          uwsgi.ini
        ocsinventory-backend-X.X.X.tar.gz
      docker-compose.yml
      Dockerfile
      entrypoint.sh
ocsinventory-frontend/
  rpm/
    sources/
      ocsinventory-frontend.conf
      ocsinventory-frontend-X.X.X.tar.gz
    specs/
      ocsinventory-frontend.spec
  deb/
    ocsinventory-frontend/
      debian/
      etc/apache2/sites-available/
        ocsinventory-frontend.conf
      usr/share/ocsinventory-frontend/
  docker/
    X.X.X/
      files/
        ocsinventory-frontend.conf
        ocsinventory-frontend-X.X.X.tar.gz
      docker-compose.yml
      Dockerfile
ocsinventory-server
  rpm
    specs
      ocsinventory-server.spec
  deb
    ocsinventory-server
      DEBIAN
  docker
    X.X.X
      files
        nginx
          ocsinventory-backend.conf
      docker-compose.yml
```

```
ocsinventory-agent/
  rpm/
    BUILD/
    BUILDROOT/
    RPMS/
    SOURCES/
      ocsinventory-cli
      install.sh
      uninstall.sh
      ocsinventory-agent.service
    SPECS/
      ocsinventory-agent.spec
    SRPMS/
  deb/
    ocsinventory-agent/
      debian/
      etc/ocsinventory-agent
        config.json
      usr/share/ocsinventory-agent/
        install.sh
        uninstall.sh
        ocsinventory-agent.service
        ocsinventory-cli
```

## Build .deb

For debian package creation instructions, see [DEBIAN.md](DEBIAN.md).

## Build .rpm

### Prerequisite

- rpmdevtools

### Commands to build

```bash
rpmbuild -bs SPECS/ocsinventory-[backend|frontend|agent|server].spec
mock -r ocs-[elX|fXX] SRPMS/ocsinventory-[backend|frontend|agent|server]-X.X.X-X.fcXX.src.rpm
```

## Build docker

### Commands to build

```bash
docker build --pull --rm -f "X.X.X/Dockerfile" -t ocsinventory/ocsinventory-[backend|frontend]:X.X.X "X.X.X"
```

## Run docker-compose (server)

```bash
docker compose -f ocsinventory-server/docker/X.X.X/docker-compose.yml up -d
```
