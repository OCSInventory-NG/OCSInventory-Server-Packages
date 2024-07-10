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
Source1:        ocsbackend
Source2:        ocsbackend.ini

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
mkdir -p %{buildroot}/etc/nginx/sites-available
cp %{SOURCE1} %{buildroot}/etc/nginx/sites-available/ocsbackend

mkdir -p %{buildroot}/etc/uwsgi/apps-available
cp %{SOURCE2} %{buildroot}/etc/uwsgi/apps-available/ocsbackend.ini

%clean
rm -rf %{buildroot}

%files
%defattr(644, nginx, nginx, 755)
/opt/ocsinventory-backend
/etc/nginx/sites-available/ocsbackend
/etc/uwsgi/apps-available/ocsbackend.ini
%config(noreplace) %{_sysconfdir}/nginx/sites-available/ocsbackend
%config(noreplace) %{_sysconfdir}/uwsgi/apps-available/ocsbackend.ini

%pre
if [ -d /opt/ocsinventory-backend ]; then
    echo "Existing installation detected, updating OCS Inventory Backend ..."
    UPDATE=1
else
    echo "New installation detected, installing OCS Inventory Backend ..."
    UPDATE=0
fi

if [ $UPDATE -eq 1 ]; then
    echo "Backing up existing installation ..."
    mkdir -p /opt/ocsinventory-backend-backup

    if [ -f /etc/nginx/sites-available/ocsinventory-backend ]; then
        cp /etc/nginx/sites-available/ocsinventory-backend /opt/ocsinventory-backend-backup/ocsinventory-backend
    fi
    if [ -f /etc/uwsgi/apps-available/ocsbackend.ini ]; then
        cp /etc/uwsgi/apps-available/ocsinventory-backend.ini /opt/ocsinventory-backend-backup/ocsinventory-backend.ini
    fi
    if [ -f /opt/ocsinventory-backend/ocsinventory_backend/settings.py ]; then
        cp /opt/ocsinventory-backend/ocsinventory_backend/settings.py /opt/ocsinventory-backend-backup/settings.py
    fi
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

if [ -d "/opt/ocsinventory-backend-backup" ]; then
    UPDATE=1
else
    UPDATE=0
fi

if [ $UPDATE -eq 1 ]; then
    echo "Restoring Nginx and UWSGI configuration ..."
    if [ -f /opt/ocsinventory-backend-backup/ocsinventory-backend.ini ]; then
        cp /opt/ocsinventory-backend-backup/ocsinventory-backend.ini /etc/uwsgi/apps-available/ocsinventory-backend.ini
    fi
    if [ -f /opt/ocsinventory-backend-backup/ocsinventory-backend ]; then
        cp /opt/ocsinventory-backend-backup/ocsinventory-backend /etc/nginx/sites-available/ocsbackend
    fi
fi

if [ ! -L /etc/nginx/sites-enabled/ocsbackend ]; then
    ln -s /etc/nginx/sites-available/ocsbackend /etc/nginx/sites-enabled/
fi

if [ ! -L /etc/uwsgi/apps-enabled/ocsbackend.ini ]; then
    ln -s /etc/uwsgi/apps-available/ocsbackend.ini /etc/uwsgi/apps-enabled/
fi

echo "Running database migrations ..."
source /opt/ocsinventory-backend/venv/bin/activate
python3 /opt/ocsinventory-backend/manage.py migrate
deactivate

chown -R nginx:nginx /opt/ocsinventory-backend/
chmod -R 755 /opt/ocsinventory-backend/logs

systemctl restart uwsgi
systemctl restart nginx

if [ $UPDATE -eq 1 ]; then
    echo "Removing backup directory ..."
    rm -rf /opt/ocsinventory-backend-backup
fi

echo "Post-installation script completed successfully. Please edit nginx configuration server_name to match your domain name and restart nginx service. Additional database configuration may be required in /opt/ocsinventory-backend/ocsinventory_backend/settings.py."
