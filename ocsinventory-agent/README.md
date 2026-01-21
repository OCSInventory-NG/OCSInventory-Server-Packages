# OCS Inventory Agent Packages

Packages repository for the OCS Inventory Agent.

Package name: ocsinventory-agent
Binary name: ocsinventory-cli

## Expected tree

- ocsinventory-agent
    - rpm
        - sources
            - ocsinventory-cli
            - install.sh
            - uninstall.sh
            - ocsinventory-agent.service
        - specs
            - ocsinventory-agent.spec
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
  - `ocsinventory-agent/rpm/sources/ocsinventory-cli`
  - `ocsinventory-agent/rpm/sources/install.sh`
  - `ocsinventory-agent/rpm/sources/uninstall.sh`
  - `ocsinventory-agent/rpm/sources/ocsinventory-agent.service`

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
cd ocsinventory-agent
rpmbuild -bb rpm/specs/ocsinventory-agent.spec \
  --define "_sourcedir $(pwd)/rpm/sources"
```
