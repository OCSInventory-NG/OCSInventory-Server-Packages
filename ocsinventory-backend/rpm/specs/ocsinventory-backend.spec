%define debug_package %{nil}
%define name ocsinventory-backend
%define version 3.0.0~rc1
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
%{!?_unitdir: %define _unitdir /usr/lib/systemd/system}

Name:           %{name}
Version:        %{version}
Release:        %{release}%{dist}
Summary:        OCS Inventory Backend API

Group:          Applications/System
License:        GPLv2
URL:            https://www.ocsinventory-ng.org/

Source0:        %{name}-%{version}.tar.gz
Source1:        ocsinventory-backend.conf
Source2:        ocsinventory-backend.ini
Source3:        ocsinventory-backend-uwsgi.service

BuildRoot:      %{buildroot}

%if 0%{?rhel} == 9
Requires:       python3.14, python3.14-pip, python3.14-devel, nginx, openldap-devel, gcc, openldap-clients, epel-release
%else
Requires:       python3, python3-pip, python3-devel, nginx, openldap-devel, gcc, openldap-clients, epel-release
%endif

Requires:       shadow-utils

AutoReqProv:    no

%description
OCS Inventory Backend API

%prep
%setup -q -c -n %{name}-%{version}

%build
# Nothing to build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/
cp -r * %{buildroot}/usr/share/
cp %{buildroot}/usr/share/%{name}/.env-sample %{buildroot}/usr/share/%{name}/.env

# Copy NGINX and UWSGI configuration files
mkdir -p %{buildroot}/etc/nginx/conf.d/
cp %{SOURCE1} %{buildroot}/etc/nginx/conf.d/ocsinventory-backend.conf

mkdir -p %{buildroot}/etc/uwsgi.d/
cp %{SOURCE2} %{buildroot}/etc/uwsgi.d/ocsinventory-backend.ini

# Copy systemd unit
mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE3} %{buildroot}%{_unitdir}/ocsinventory-backend-uwsgi.service

# create log directory
mkdir -p %{buildroot}/var/log/ocsinventory-backend

%clean
rm -rf %{buildroot}

%files
%defattr(644, ocsbackend, nginx, 755)
/usr/share/ocsinventory-backend
%config(noreplace) %{_sysconfdir}/nginx/conf.d/ocsinventory-backend.conf
%config(noreplace) %{_sysconfdir}/uwsgi.d/ocsinventory-backend.ini
%{_unitdir}/ocsinventory-backend-uwsgi.service
%attr(755, ocsbackend, nginx) /var/log/ocsinventory-backend

%if 0%{?rhel} == 9
%global python_bin python3.14
%else
%global python_bin python3
%endif

%pre
if ! getent passwd ocsbackend >/dev/null; then
    useradd --system --no-create-home --shell /sbin/nologin --gid nginx ocsbackend
fi

if [ -d /usr/share/ocsinventory-backend ]; then
    echo "============================================"
    echo "=                                          ="
    echo "=      Updating OCS Inventory Backend      ="
    echo "=                                          ="
    echo "============================================"
    # Save environment configuration
    mkdir -p /var/lib/ocsinventory-backend
    chmod 700 /var/lib/ocsinventory-backend
    if [ -f /usr/share/ocsinventory-backend/.env ]; then
        cp /usr/share/ocsinventory-backend/.env /var/lib/ocsinventory-backend/.envbackup
        chmod 600 /var/lib/ocsinventory-backend/.envbackup
    fi
else
    echo "=============================================="
    echo "=                                            ="
    echo "=      Installing OCS Inventory Backend      ="
    echo "=                                            ="
    echo "=============================================="
fi

%post
set -e
echo "Launching OCS Inventory Backend post-installation script"

# venv and requirements
if [ ! -d "/usr/lib/ocsinventory-backend/venv" ]; then
    # generating secret for Django
    echo "Generating Django secret key..."
    SECRET_KEY=$(%{python_bin} -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY='${SECRET_KEY}'/" /usr/share/ocsinventory-backend/.env
    echo "Creating virtual environment..."
    %{python_bin} -m venv /usr/lib/ocsinventory-backend/venv
fi

echo "Activating virtual environment ..."
source /usr/lib/ocsinventory-backend/venv/bin/activate
echo "Installing requirements ..."
pip3 install -r /usr/share/ocsinventory-backend/requirements.txt
pip3 install uwsgi

# Check if update
if [ -f /var/lib/ocsinventory-backend/.envbackup ]; then
    echo "OCS Inventory Backend update detected"
    cp /var/lib/ocsinventory-backend/.envbackup /usr/share/ocsinventory-backend/.env
    echo "Running database migrations..."
    python3 /usr/share/ocsinventory-backend/manage.py migrate
fi

deactivate

if [ ! -f /var/lib/ocsinventory-backend/.envbackup ]; then
    chown -R ocsbackend:nginx /usr/share/ocsinventory-backend/
    chmod -R 755 /usr/share/ocsinventory-backend/logs

    # ocsinventory socket dir and permissions
    mkdir -p /var/run/ocsinventory-backend/
    chown ocsbackend:nginx /var/run/ocsinventory-backend/
    chmod 755 /var/run/ocsinventory-backend/

    systemctl daemon-reload
    systemctl enable ocsinventory-backend-uwsgi
fi

echo "Restarting UWSGI and Nginx services..."
systemctl restart ocsinventory-backend-uwsgi
systemctl restart nginx

echo "OCS Inventory Backend successfully installed."

if [ ! -f /var/lib/ocsinventory-backend/.envbackup ]; then
    echo "================================================================================================================================="
    echo "=                                                                                                                               ="
    echo "= Please run the script '/usr/share/ocsinventory-backend/tools/configure-ocsinventory-backend.sh' to configure the application. ="
    echo "=                                                                                                                               ="
    echo "================================================================================================================================="
else
    rm -rf /var/lib/ocsinventory-backend/.envbackup
fi

%preun
if [ "$1" = "0" ]; then
    systemctl stop ocsinventory-backend-uwsgi
    systemctl disable ocsinventory-backend-uwsgi
fi

%postun
if [ "$1" = "0" ]; then
    echo "Clean OCS Inventory Backend files..."
    rm -rf /usr/share/ocsinventory-backend
    rm -rf /usr/lib/ocsinventory-backend
    rm -rf /var/log/ocsinventory-backend
    systemctl daemon-reload
    echo "OCS Inventory Backend successfully uninstalled."
fi

%changelog
* Thu Jun 04 2026 Charlène Auger <charlene.auger@ocsinventory-ng.org> - 3.0.0~rc1-1
- Initial RPM