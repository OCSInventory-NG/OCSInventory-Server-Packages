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
Requires:       epel-release, python3, python3-pip, uwsgi, nginx, python3-virtualenv, python3-devel, openldap-devel, uwsgi-plugin-python3, postgresql-server, postgresql-contrib

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
%defattr(644, nginx, nginx, 755)
/usr/share/ocsinventory-backend
%config(noreplace) %{_sysconfdir}/nginx/conf.d/ocsinventory-backend.conf
%config(noreplace) %{_sysconfdir}/uwsgi.d/ocsinventory-backend.ini
%attr(755, nginx, nginx) /var/log/ocsinventory-backend

%pre
if [ -d /usr/share/ocsinventory-backend ]; then
    echo "Existing installation detected, updating OCS Inventory Backend ..."
else
    echo "New installation detected, installing OCS Inventory Backend ..."
fi

%post
echo "Launching post-installation script ..."

# PostgreSQL setup
if [ ! -f "/var/lib/pgsql/data/PG_VERSION" ]; then
    echo "Starting PostgreSQL setup ..."
    setenforce 0
    postgresql-setup --initdb --unit postgresql  >> /tmp/pgsetup.log 2>&1
    sleep 5
    systemctl start postgresql
    systemctl enable postgresql
    systemctl status postgresql
else
    echo "PostgreSQL is already installed."
fi

# default credentials
DB_NAME="ocsdb"
DB_USER="ocsuser"
DB_PASSWORD="ocsuser"


# check that postgres is running
if [ "$(systemctl is-active postgresql)" != "active" ]; then
    echo "PostgreSQL does not appear to be running. Attempting to start PostgreSQL ..."
    systemctl restart postgresql
    systemctl status postgresql
fi


echo "Creating PostgreSQL database and user..."
runuser -l postgres -c "psql -c \"CREATE DATABASE ${DB_NAME};\""
runuser -l postgres -c "psql -c \"CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';\""
runuser -l postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};\""

# venv and requirements
if [ ! -d "/usr/lib/ocsinventory-backend/venv" ]; then
    echo "Creating virtual environment ..."
    python3 -m venv /usr/lib/ocsinventory-backend/venv
fi

echo "Activating virtual environment ..."
source /usr/lib/ocsinventory-backend/venv/bin/activate
echo "Installing requirements ..."
pip3 install -r /usr/share/ocsinventory-backend/requirements.txt

echo "Running database migrations ..."
python3 /usr/share/ocsinventory-backend/manage.py migrate
deactivate

chown -R nginx:nginx /usr/share/ocsinventory-backend/
chmod -R 755 /usr/share/ocsinventory-backend/logs

# ocsinventory socket dir and permissions
mkdir -p /var/run/ocsinventory-backend/
chown nginx:nginx /var/run/ocsinventory-backend/
chmod 755 /var/run/ocsinventory-backend/


echo "Starting uWSGI service ..."
systemctl restart uwsgi
systemctl enable uwsgi

systemctl restart nginx

echo "Post-installation script completed successfully."