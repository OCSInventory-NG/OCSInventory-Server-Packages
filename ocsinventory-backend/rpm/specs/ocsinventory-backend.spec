%define debug_package %{nil}
%define name ocsinventory-backend
%define version 3.0.0
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        OCS Inventory Backend API

Group:          Applications/System
License:        GPLv2
URL:            https://www.ocsinventory-ng.org/

Source0:        %{name}-%{version}.tar.gz
Source1:        ocsinventory-backend.conf
Source2:        ocsinventory-backend.ini

BuildRoot:      %{buildroot}
Requires:       python3, python3-pip, uwsgi, nginx, python3-virtualenv, python3-devel, openldap-devel, uwsgi-plugin-python3, gcc, openldap-clients, epel-release

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

# Copy NGINX and UWSGI configuration files
mkdir -p %{buildroot}/etc/nginx/conf.d/
cp %{SOURCE1} %{buildroot}/etc/nginx/conf.d/ocsinventory-backend.conf

mkdir -p %{buildroot}/etc/uwsgi.d/
cp %{SOURCE2} %{buildroot}/etc/uwsgi.d/ocsinventory-backend.ini

# create log directory
mkdir -p %{buildroot}/var/log/ocsinventory-backend

%clean
rm -rf %{buildroot}

%files
%defattr(644, nginx, nginx, 755) /usr/share/ocsinventory-backend
%config(noreplace) %{_sysconfdir}/nginx/conf.d/ocsinventory-backend.conf
%config(noreplace) %{_sysconfdir}/uwsgi.d/ocsinventory-backend.ini
%attr(755, nginx, nginx) /var/log/ocsinventory-backend

%pre
if [ -d /usr/share/ocsinventory-backend ]; then
    echo "============================================"
    echo "=                                          ="
    echo "=      Updating OCS Inventory Backend      ="
    echo "=                                          ="
    echo "============================================"
    # Save environment configuration
    cp /usr/share/ocsinventory-backend/.env /tmp/.ocsenvbackup
else
    echo "=============================================="
    echo "=                                            ="
    echo "=      Installing OCS Inventory Backend      ="
    echo "=                                            ="
    echo "=============================================="
fi

%post
echo "Launching OCS Inventory Backend post-installation script"

# venv and requirements
if [ ! -d "/usr/lib/ocsinventory-backend/venv" ]; then
    # generating secret for Django 
    echo "Generating Django secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY='${SECRET_KEY}'/" /usr/share/ocsinventory-backend/.env
    echo "Creating virtual environment..."
    python3 -m venv /usr/lib/ocsinventory-backend/venv
fi

echo "Activating virtual environment ..."
source /usr/lib/ocsinventory-backend/venv/bin/activate
echo "Installing requirements ..."
pip3 install -r /usr/share/ocsinventory-backend/requirements.txt

# Check if update
if [ -f /tmp/.ocsenvbackup ]; then
    echo "OCS Inventory Backend update detected"
    cp /tmp/.ocsenvbackup /usr/share/ocsinventory-backend/.env
    echo "Running database migrations..."
    python3 /usr/share/ocsinventory-backend/manage.py migrate
fi

deactivate

if [ ! -f /tmp/.ocsenvbackup ]; then
    chown -R nginx:nginx /usr/share/ocsinventory-backend/
    chmod -R 755 /usr/share/ocsinventory-backend/logs

    # ocsinventory socket dir and permissions
    mkdir -p /var/run/ocsinventory-backend/
    chown nginx:nginx /var/run/ocsinventory-backend/
    chmod 755 /var/run/ocsinventory-backend/

    systemctl enable uwsgi
fi

echo "Restarting UWSGI and Nginx services..."
systemctl restart uwsgi
systemctl restart nginx

echo "OCS Inventory Backend successfully installed."

if [ ! -f /tmp/.ocsenvbackup ]; then
    echo "================================================================================================================================="
    echo "=                                                                                                                               ="
    echo "= Please run the script '/usr/share/ocsinventory-backend/tools/configure-ocsinventory-backend.sh' to configure the application. ="
    echo "=                                                                                                                               ="
    echo "================================================================================================================================="
else
    rm -rf /tmp/.ocsenvbackup
fi

%postun
echo "Clean OCS Inventory Backend files..."
rm -rf /usr/share/ocsinventory-backend
rm -rf /usr/lib/ocsinventory-backend
rm -rf /var/log/ocsinventory-backend
echo "OCS Inventory Backend successfully uninstalled."

%changelog
* Fri Oct 04 2024 Charlène Auger <charlene.auger@ocsinventory-ng.org> - 3.0.0-1
- Initial RPM