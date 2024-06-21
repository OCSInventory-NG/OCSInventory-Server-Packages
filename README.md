# OCS Inventory Server Packages

**WORK IN PROGRESS**

Packages repository for OCS Inventory Rework.

## Structure

- ocsinventory-frontend
    - rpm
        - sources
            - ocsinventory-frontend.conf
            - ocsinventory-frontend-X.X.X.tar.gz
        - specs
            - ocsinventory-frontend.spec
    - deb
        - ocsinventory-frontend
            - DEBIAN
            - etc/apache2/sites-available
            - usr/share/ocsinventory-frontend
    - docker
        - X.X.X
            - files
                - ocsinventory-frontend.conf
                - ocsinventory-frontend-X.X.X.tar.gz

## Build .deb

### Prerequisite

- dpkg-dev

### Commands to build

```bash
cd ocsinventory-[backend|frontend|agent]/deb
dpkg-deb -Zgzip --build ocsinventory-[backend|frontend|agent]
```

## Build .rpm

### Prerequisite

- rpmdevtools

### Commands to build

```bash
rpmbuild -bs SPECS/ocsinventory-[backend|frontend|agent].spec
mock -r ocs-[elX|fXX] SRPMS/ocsinventory-[backend|frontend|agent]-X.X.X-X.fcXX.src.rpm
```

## Build docker

### Commands to build

```bash
docker build --pull --rm -f "X.X.X/Dockerfile" -t ocsinventory/[backend|frontend]:X.X.X "X.X.X"
```