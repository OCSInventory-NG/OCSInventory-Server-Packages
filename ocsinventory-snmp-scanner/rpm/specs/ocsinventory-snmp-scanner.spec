%define debug_package %{nil}
%define name ocsinventory-snmp-scanner
%define version 3.0.0
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
%{!?_unitdir: %define _unitdir /usr/lib/systemd/system}

Name:           %{name}
Version:        %{version}
Release:        %{release}%{dist}
Summary:        OCS Inventory SNMP Scanner

Group:          Applications/System
License:        GPLv2
URL:            https://www.ocsinventory-ng.org/

Source0:        %{name}-%{version}.tar.gz
Source1:        ocsinventory-snmp-scanner.service
Source2:        ocsinventory-snmp-scanner.timer

BuildArch:      noarch
BuildRoot:      %{buildroot}

Requires:       python3 >= 3.9, python3-pip, shadow-utils, ca-certificates

AutoReqProv:    no

%description
Network scanner that collects device information over SNMP and reports it to
an OCS Inventory server, or stores the inventories locally when running in
OFFLINE mode.

%prep
%setup -q -c -n %{name}-%{version}

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/
cp -r * %{buildroot}/usr/share/

# The scanner reads config/ and writes logs/ and files/ next to itself:
# replace them with symlinks to their FHS locations, as debian/rules does.
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp %{buildroot}/usr/share/%{name}/config/scanner.conf-sample \
   %{buildroot}%{_sysconfdir}/%{name}/scanner.conf
cp %{buildroot}/usr/share/%{name}/config/configs.json-sample \
   %{buildroot}%{_sysconfdir}/%{name}/configs.json
rm -rf %{buildroot}/usr/share/%{name}/config \
       %{buildroot}/usr/share/%{name}/logs \
       %{buildroot}/usr/share/%{name}/files
ln -s %{_sysconfdir}/%{name} %{buildroot}/usr/share/%{name}/config
ln -s /var/log/%{name} %{buildroot}/usr/share/%{name}/logs
ln -s /var/lib/%{name}/files %{buildroot}/usr/share/%{name}/files

mkdir -p %{buildroot}/var/log/%{name}
mkdir -p %{buildroot}/var/lib/%{name}/files
mkdir -p %{buildroot}/var/lib/%{name}/mibs
mkdir -p %{buildroot}/usr/lib/%{name}

mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
cp %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.timer

%clean
rm -rf %{buildroot}

%files
%defattr(644, root, root, 755)
/usr/share/%{name}
%attr(640, ocssnmp, ocssnmp) %config(noreplace) %{_sysconfdir}/%{name}/scanner.conf
%attr(640, root, ocssnmp) %config(noreplace) %{_sysconfdir}/%{name}/configs.json
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.timer
%dir /usr/lib/%{name}
%dir %attr(755, ocssnmp, ocssnmp) /var/log/%{name}
%dir %attr(755, ocssnmp, ocssnmp) /var/lib/%{name}
%dir %attr(755, ocssnmp, ocssnmp) /var/lib/%{name}/files
%dir %attr(755, ocssnmp, ocssnmp) /var/lib/%{name}/mibs

%pre
if ! getent passwd ocssnmp >/dev/null; then
    useradd --system --no-create-home --home-dir /var/lib/%{name} \
            --shell /sbin/nologin ocssnmp
fi

%post
VENV=/usr/lib/%{name}/venv
if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV"
fi
echo "Installing requirements ..."
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r /usr/share/%{name}/requirements.txt

# Left empty, the scanner generates a name and rewrites scanner.conf through
# configparser, dropping every comment from the config file.
if [ "$1" = "1" ] && grep -qE '^name[[:space:]]*=[[:space:]]*$' %{_sysconfdir}/%{name}/scanner.conf; then
    sed -i "s|^name[[:space:]]*=.*|name = $(hostname -s)|" %{_sysconfdir}/%{name}/scanner.conf
fi

systemctl daemon-reload

# Shipped disabled: nothing is configured yet at install time.
if [ "$1" = "1" ]; then
    echo "==============================================================================="
    echo "= OCS Inventory SNMP Scanner installed.                                       ="
    echo "=                                                                             ="
    echo "= 1. Configure it:   /etc/ocsinventory-snmp-scanner/scanner.conf              ="
    echo "=                    /etc/ocsinventory-snmp-scanner/configs.json              ="
    echo "= 2. Try a run:      systemctl start ocsinventory-snmp-scanner.service        ="
    echo "= 3. Schedule it:    systemctl enable --now ocsinventory-snmp-scanner.timer   ="
    echo "==============================================================================="
fi

%preun
if [ "$1" = "0" ]; then
    systemctl stop %{name}.timer %{name}.service >/dev/null 2>&1 || true
    systemctl disable %{name}.timer %{name}.service >/dev/null 2>&1 || true
fi

%postun
if [ "$1" = "0" ]; then
    rm -rf /usr/lib/%{name} /var/log/%{name} /var/lib/%{name}
    if getent passwd ocssnmp >/dev/null; then
        userdel ocssnmp >/dev/null 2>&1 || true
    fi
    systemctl daemon-reload
fi

%changelog
* Fri Sep 18 2026 Léa Droguet <lea.droguet@factorfx.com> - 3.0.0-1
- Initial RPM
