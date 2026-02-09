# OCS Inventory Agent Packages

Packages repository for the OCS Inventory Agent.

Package name: ocsinventory-agent
Binary name: ocsinventory-cli

## Expected tree

- ocsinventory-agent
    - rpm
        - BUILD
        - BUILDROOT
        - RPMS
        - SOURCES
            - ocsinventory-cli
            - install.sh
            - uninstall.sh
            - ocsinventory-agent.service
        - SPECS
            - ocsinventory-agent.spec
        - SRPMS
    - deb
        - ocsinventory-agent
            - debian
            - etc/ocsinventory-agent
                - config.json
            - usr/share/ocsinventory-agent
                - install.sh
                - uninstall.sh
                - ocsinventory-agent.service
                - ocsinventory-cli

## Place the payload files before build

- DEB payload:
  - `ocsinventory-agent/deb/ocsinventory-agent/usr/share/ocsinventory-agent/ocsinventory-cli`
  - `ocsinventory-agent/deb/ocsinventory-agent/usr/share/ocsinventory-agent/install.sh`
  - `ocsinventory-agent/deb/ocsinventory-agent/usr/share/ocsinventory-agent/uninstall.sh`
  - `ocsinventory-agent/deb/ocsinventory-agent/usr/share/ocsinventory-agent/ocsinventory-agent.service`
  - `ocsinventory-agent/deb/ocsinventory-agent/etc/ocsinventory-agent/config.json` (defaults)
- RPM sources:
  - `ocsinventory-agent/rpm/SOURCES/ocsinventory-cli`
  - `ocsinventory-agent/rpm/SOURCES/install.sh`
  - `ocsinventory-agent/rpm/SOURCES/uninstall.sh`
  - `ocsinventory-agent/rpm/SOURCES/ocsinventory-agent.service`
  - Spec file in `ocsinventory-agent/rpm/SPECS/ocsinventory-agent.spec`

## Build .deb

### Requirements

- build-essential
- devscripts
- debhelper
- dh-python
- dpkg-dev
- lintian
- equivs
- python3-all
- gnupg

Recommended: build as a non-root user. A GPG key is required if you want to sign packages.

### Check package info

```bash
cd ocsinventory-agent/deb/ocsinventory-agent
dpkg-parsechangelog
dpkg-checkbuilddeps
```

### Build

```bash
# Signed build
gpg --list-secret-keys --keyid-format LONG
dpkg-buildpackage -S -sa -k"<KEYID|KEYMAIL>"
dpkg-buildpackage -b -sa -k"<KEYID|KEYMAIL>"

# Unsigned build (dev)
dpkg-buildpackage -S -sa -us -ui -uc
dpkg-buildpackage -b -sa -us -ui -uc
```

### Package files output

```bash
ocsinventory-agent_<upstream-version>.dsc
ocsinventory-agent_<upstream-version>.tar.gz
ocsinventory-agent_<upstream-version>_<arch>.buildinfo
ocsinventory-agent_<upstream-version>_<arch>.changes
ocsinventory-agent_<upstream-version>_source.buildinfo
ocsinventory-agent_<upstream-version>_source.changes
ocsinventory-agent_<upstream-version>_<arch>.deb
```

## Build .rpm

### Prerequisite

- rpmdevtools

### Build

```bash
rpmbuild -bb ocsinventory-agent.spec
```
