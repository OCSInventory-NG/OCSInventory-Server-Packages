# Debian build

This quickguide explain how to compile OCS Inventory backend, frontend and agent for debian.

## Requirements

```bash
sudo apt update
sudo apt -y install \
  build-essential \
  devscripts \
  debhelper \
  dh-python \
  dpkg-dev \
  lintian \
  equivs \
  python3-all \
  gnupg \
  python3-setuptools
```

A generated GPG key available on the system in the case you want to sign the package

_Recommended : building package need to be done in a non-root user_

## Deb layout (frontend / backend)


```bash
ocsinventory-xxxx/
├── deb
│   ├── ocsinventory-xxxx
│   │   ├── debian # Contains debian packages definition and control files
│   │   ├── etc # Contains services configuraiton
│   │   └── usr # Contains app source code
```

## Check package infos 

Before building the deb package, you can check build dependencies and changelog using : 

```bash
dpkg-parsechangelog
dpkg-checkbuilddeps
```

## Build the package

First, navigate the the package directory : 

```bash
cd ocsinventory-backend/deb/ocsinventory-backend # Backend package path
cd ocsinventory-frontend/deb/ocsinventory-frontend # Frontend package path
cd ocsinventory-agent/deb/ocsinventory-agent # Agent package path
```

In order to build the package and sign it using a GPG key, use : 

```bash
gpg --list-secret-keys --keyid-format LONG
sudo dpkg-buildpackage -S -sa -k"<KEYID|KEYMAIL>" # Sources
sudo dpkg-buildpackage -b -sa -k"<KEYID|KEYMAIL>" # Binary
```

For dev purpose, build without signing : 
```bash
sudo dpkg-buildpackage -S -sa -us -ui -uc # Sources
sudo dpkg-buildpackage -b -sa -us -ui -uc # Binary
```

The -us -ui -uc arguments means : 
- unsigned source package
- unsigned .buildinfo file
- unsigned .buildinfo and .changes file

## Package files ouput 

Building the package will output different files in the parent folder.

```bash
ocsinventory-[backend|frontend|agent]_X.X.X.dsc 
ocsinventory-[backend|frontend|agent]_X.X.X.tar.gz 
ocsinventory-[backend|frontend|agent]_X.X.X_amd64.buildinfo 
ocsinventory-[backend|frontend|agent]_X.X.X_amd64.changes 
ocsinventory-[backend|frontend|agent]_X.X.X_source.buildinfo 
ocsinventory-[backend|frontend|agent]_X.X.X_source.changes 
ocsinventory-[backend|frontend|agent]_X.X.X_all.deb 
```

