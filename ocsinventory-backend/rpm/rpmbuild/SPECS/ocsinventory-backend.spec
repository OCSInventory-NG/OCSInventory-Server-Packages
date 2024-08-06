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
Source3:        ocsinventory-backend.service

BuildRoot:      %{buildroot}
Requires:       epel-release, python3, python3-pip, uwsgi, nginx, python3-virtualenv, python3-devel, openldap-devel, uwsgi-plugin-python3
AutoReqProv:    no

%description
OCS Inventory Backend API

%prep
%setup -q -c -n %{name}-%{version}

%build
# Nothing to build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/
cp -r * %{buildroot}/opt/

# Copy NGINX and UWSGI configuration files
mkdir -p %{buildroot}/etc/nginx/conf.d/
cp %{SOURCE1} %{buildroot}/etc/nginx/conf.d/ocsinventory-backend.conf

mkdir -p %{buildroot}/etc/uwsgi.d/
cp %{SOURCE2} %{buildroot}/etc/uwsgi.d/ocsinventory-backend.ini

mkdir -p %{buildroot}/etc/systemd/system/
cp %{SOURCE3} %{buildroot}/etc/systemd/system/ocsinventory-backend.service

# create log directory
mkdir -p %{buildroot}/var/log/ocsinventory-backend

%clean
rm -rf %{buildroot}

%files
%defattr(644, nginx, nginx, 755)
/opt/ocsinventory-backend
%config(noreplace) %{_sysconfdir}/nginx/conf.d/ocsinventory-backend.conf
%config(noreplace) %{_sysconfdir}/uwsgi.d/ocsinventory-backend.ini
%{_sysconfdir}/systemd/system/ocsinventory-backend.service
%attr(755, nginx, nginx) /var/log/ocsinventory-backend

%pre
if [ -d /opt/ocsinventory-backend ]; then
    echo "Existing installation detected, updating OCS Inventory Backend ..."
else
    echo "New installation detected, installing OCS Inventory Backend ..."
fi

%post
echo "Launching post-installation script ..."

if [ ! -d "/opt/ocsinventory-backend/venv" ]; then
    echo "Creating virtual environment ..."
    python3 -m venv /opt/ocsinventory-backend/venv
fi

echo "Activating virtual environment ..."
source /opt/ocsinventory-backend/venv/bin/activate
echo "Installing requirements ..."
pip3 install -r /opt/ocsinventory-backend/requirements.txt
deactivate

echo "Running database migrations ..."
source /opt/ocsinventory-backend/venv/bin/activate
python3 /opt/ocsinventory-backend/manage.py migrate
deactivate

chown -R nginx:nginx /opt/ocsinventory-backend/
chmod -R 755 /opt/ocsinventory-backend/logs

echo "Restarting services ..."
systemctl restart uwsgi
systemctl restart nginx
# reload systemd
systemctl daemon-reload
systemctl enable ocsinventory-backend.service
systemctl start ocsinventory-backend.service

echo "Post-installation script completed successfully. Additional database configuration may be required in /opt/ocsinventory-backend/ocsinventory_backend/settings.py."
