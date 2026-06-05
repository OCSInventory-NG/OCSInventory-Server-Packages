# Red Hat build

This quick guide explain how to compile OCS Inventory backend, frontend, agent and meta packages for Red Hat.

## Requirements

```bash
sudo dnf update
sudo dnf -y install \
  rpm-build \
  rpmdevtools \
  rpmlint \
  mock \
  gcc \
  make \
  redhat-rpm-config \
  gnupg2
```

A GPG key available on the system, if you want to sign the package


_Recommended : Packages should be built as a non-root user_

## RPM layout (frontend / backend / agent)

```bash
ocsinventory-xxxx/
├── rpm
│   ├── sources # Contains services configuration and optional patches/tarballs
│   └── specs   # Contains the RPM spec file (.spec)
```

## Check package infos

Before building the RPM package, you can verify the spec file syntax using:

```bash
rpmlint ocsinventory-xxxx/rpm/specs/ocsinventory-xxxx.spec
```

## Build the package

First, prepare your RPM build environment (it will create `~/rpmbuild` directory layout):

```bash
rpmdev-setuptree
```

Copy the source and spec files to the RPM build directory:

```bash
# Example for backend
cp ocsinventory-backend/rpm/sources/* ~/rpmbuild/SOURCES/
cp ocsinventory-backend/rpm/specs/ocsinventory-backend.spec ~/rpmbuild/SPECS/
```

> [!NOTE]
> Ensure all source files and archives required by the spec files (e.g. `ocsinventory-cli`, `install.sh`, etc. for the agent, or the release tarball `ocsinventory-[backend|frontend]-X.X.X.tar.gz` for the backend/frontend) are placed in `~/rpmbuild/SOURCES/`.

Navigate to your RPM build directory:

```bash
cd ~/rpmbuild
```

In order to build the Source RPM (SRPM):

```bash
rpmbuild -bs SPECS/ocsinventory-[backend|frontend|agent|server].spec
```

In order to build the binary RPM:

```bash
rpmbuild -bb SPECS/ocsinventory-[backend|frontend|agent|server].spec
```

Or you can use mock to build in a clean chroot environment for a specific target:

```bash
mock -r ocs-[elX|fXX] SRPMS/ocsinventory-[backend|frontend|agent|server]-X.X.X-X.fcXX.src.rpm
```

### Sign the package

To sign RPM packages, configure your GPG key in `~/.rpmmacros`:

```rpmmacros
%_gpg_name <KEYID|KEYMAIL>
```

Then sign your packages using:

```bash
rpmsign --addsign SRPMS/ocsinventory-[backend|frontend|agent|server]-X.X.X-X.src.rpm
rpmsign --addsign RPMS/[x86_64|noarch]/ocsinventory-[backend|frontend|agent|server]-X.X.X-X.rpm
```

## Package files output

Building the package will output different files in `~/rpmbuild/SRPMS` and `~/rpmbuild/RPMS`:

```bash
~/rpmbuild/SRPMS/ocsinventory-[backend|frontend|agent|server]-X.X.X-X.src.rpm
~/rpmbuild/RPMS/[x86_64|noarch]/ocsinventory-[backend|frontend|agent|server]-X.X.X-X.[x86_64|noarch].rpm
```
