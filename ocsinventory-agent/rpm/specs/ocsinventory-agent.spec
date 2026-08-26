%define debug_package %{nil}
%define name ocsinventory-agent
%define version 3.0.0~rc2
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
%global __strip /bin/true

Name:           %{name}
Version:        %{version}
Release:        %{release}%{dist}
Summary:        OCS Inventory Agent

Group:          Applications/System
License:        GPLv3+
URL:            https://www.ocsinventory-ng.org/

Source0:        %{name}-%{version}.tar.xz

BuildArch:      x86_64
BuildRoot:      %{buildroot}
Requires:       glibc, bash, coreutils, util-linux, grep
Recommends:     systemd, openssl, ca-certificates

AutoReqProv:    no

%description
OCS Inventory Agent.

%prep
# The agent's release doesn't ship a plain ocsinventory-agent-<version>.tar.gz:
# its "Linux-Rhel" setup archive wraps the same 4 files (ocsinventory-cli,
# install.sh, uninstall.sh, ocsinventory-agent.service) under its own
# OCSInventory-Agent-Linux-Rhel-Setup/ directory instead of ocsinventory-agent-
# <version>/, hence the explicit -n flag below instead of the usual default.
# (NB: RPM expands macros even inside comments, so never spell out the name
# of the directive used below in a comment - a bare mention runs it a
# second time, with no args, and breaks this section.)
%setup -q -n OCSInventory-Agent-Linux-Rhel-Setup

%build
# Nothing to build: ocsinventory-cli ships as a prebuilt binary from the
# agent's own release pipeline.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/ocsinventory-agent
cp -r ./* %{buildroot}/usr/share/ocsinventory-agent/
chmod 0755 %{buildroot}/usr/share/ocsinventory-agent/ocsinventory-cli
chmod 0755 %{buildroot}/usr/share/ocsinventory-agent/install.sh
chmod 0755 %{buildroot}/usr/share/ocsinventory-agent/uninstall.sh
chmod 0644 %{buildroot}/usr/share/ocsinventory-agent/ocsinventory-agent.service

mkdir -p %{buildroot}%{_sysconfdir}/ocsinventory-agent
cat <<'CONFIG' > %{buildroot}%{_sysconfdir}/ocsinventory-agent/config.json
{
  "url": "",
  "username": "",
  "password": "",
  "mode": 4,
  "log_level": 3,
  "log_file": true,
  "log_file_path": "/var/log/ocsinventory-agent/ocsinventory-agent.log",
  "data_directory": "/var/lib/ocsinventory-data",
  "certificate": "none",
  "bypass_certificate": false
}
CONFIG

%clean
rm -rf %{buildroot}

%files
%defattr(644, root, root, 755)
/usr/share/ocsinventory-agent/ocsinventory-cli
/usr/share/ocsinventory-agent/install.sh
/usr/share/ocsinventory-agent/uninstall.sh
/usr/share/ocsinventory-agent/ocsinventory-agent.service
%config(noreplace) %{_sysconfdir}/ocsinventory-agent/config.json

%post
AGENT_SHARE="/usr/share/ocsinventory-agent"
AGENT_BIN="/usr/local/bin/ocsinventory-cli"
SYMLINK="/usr/bin/ocsinventory-cli"
CONFIG_DIR="/etc/ocsinventory-agent"
CONFIG_FILE="${CONFIG_DIR}/config.json"
SERVICE_FILE="/etc/systemd/system/ocsinventory-agent.service"
LOG_FILE="/var/log/ocsinventory-agent/ocsinventory-agent.log"
DATA_DIR="/var/lib/ocsinventory-data"
LOG_DIR="$(dirname "$LOG_FILE")"

if [ "$1" -eq 1 ] && [ -t 0 ] && [ -t 1 ] && [ -x "${AGENT_SHARE}/install.sh" ]; then
    rm -rf "${CONFIG_DIR}"
    "${AGENT_SHARE}/install.sh"
    exit 0
fi

install -d /usr/local/bin
if [ -f "${AGENT_SHARE}/ocsinventory-cli" ]; then
    install -m 0755 "${AGENT_SHARE}/ocsinventory-cli" "${AGENT_BIN}"
fi

if [ ! -L "${SYMLINK}" ]; then
    ln -s "${AGENT_BIN}" "${SYMLINK}" || true
fi

install -d "${DATA_DIR}"
install -d "${LOG_DIR}"
touch "${LOG_FILE}"

if [ -f "${AGENT_SHARE}/ocsinventory-agent.service" ]; then
    install -m 0644 "${AGENT_SHARE}/ocsinventory-agent.service" "${SERVICE_FILE}"
fi

if command -v systemctl >/dev/null 2>&1; then
    systemctl daemon-reload >/dev/null 2>&1 || true
fi

echo "OCSInventory Agent installed in local mode (no template)."
echo "Run /usr/share/ocsinventory-agent/install.sh for interactive setup."

%postun
if [ "$1" -eq 0 ]; then
    rm -f /usr/local/bin/ocsinventory-cli
    rm -f /usr/bin/ocsinventory-cli
    rm -f /etc/systemd/system/ocsinventory-agent.service
    if command -v systemctl >/dev/null 2>&1; then
        systemctl daemon-reload >/dev/null 2>&1 || true
    fi
fi

%changelog
* Wed Aug 26 2026 OCS Inventory Release Bot <ci@ocsinventory-ng.org> - 3.0.0~rc2-1
- Release 3.0.0-rc2.

* Thu Jun 04 2026 Lea Droguet <lea.droguet@factorfx.com> - 3.0.0~rc1-1
- Initial RPM
