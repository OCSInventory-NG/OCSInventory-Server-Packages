# OCS Inventory Server Packages

**WORK IN PROGRESS**

Packages repository for OCS Inventory Rework.

## Structure

- ocsinventory-frontend
    - rpm
        - sources
        - specs
    - deb
        - ocsinventory-frontend
            - DEBIAN
            - etc/apache2/sites-available
            - usr/share/ocsinventory-frontend

## Build .deb

### Prerequisite

- dpkg-dev

### Commands to build

```bash
cd ocsinventory-[backend/frontend/agent]/deb
dpkg-deb -Zgzip --build ocsinventory-[backend/frontend/agent]
```

## Build .rpm

### Prerequisite

- rpmdevtools

### Commands to build

```bash
rpmbuild -bs SPECS/ocsinventory-[backend/frontend/agent].spec
mock -r ocs-[elX/fXX] SRPMS/ocsinventory-[backend/frontend/agent]-X.X.X-X.fcXX.src.rpm
```