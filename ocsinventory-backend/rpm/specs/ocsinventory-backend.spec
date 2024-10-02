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
Recommends:     postgresql-server, postgresql-contrib
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
%defattr(644, nginx, nginx, 755)
/usr/share/ocsinventory-backend
%config(noreplace) %{_sysconfdir}/nginx/conf.d/ocsinventory-backend.conf
%config(noreplace) %{_sysconfdir}/uwsgi.d/ocsinventory-backend.ini
%attr(755, nginx, nginx) /var/log/ocsinventory-backend

%pre
if [ -d /usr/share/ocsinventory-backend ]; then
    echo "Existing installation detected, updating OCS Inventory Backend"
    update=1
    echo $update > /tmp/upade_ocsinventory_backend
else
    echo "New installation detected, installing OCS Inventory Backend"
    update=0
fi

%post
echo "Launching OCS Inventory Backend post-installation script"

# PostgreSQL setup
if rpm -q postgresql-server > /dev/null 2>&1; then
    echo "Setup PostgreSQL"
    setenforce 0
    sudo -i -u postgres psql -c "SELECT 1" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "PostgreSQL not initialized, initializing..."
        postgresql-setup --initdb --unit postgresql  >> /tmp/pgsetup.log 2>&1
        if [ $? -eq 0 ]; then
            echo "PostgreSQL database initialized successfully"
            # update pg_hba.conf to allow local connections
            echo "Updating pg_hba.conf to allow local connections"
            sed -i 's/ident/md5/' /var/lib/pgsql/data/pg_hba.conf

            sudo systemctl enable postgresql
            su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data -l logfile start"
        else
            echo "PostgreSQL initialization failed"
            exit 1
        fi
    else
        echo "PostgreSQL is already initialized"
    fi
fi

# If PostgreSQL and new OCS Backend installation
if [ "$(su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data status" | grep "server is running")" ]; then
    echo "Setup OCS Inventory Backend database"
    # Generate dynamic password
    POSTGRES_DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/POSTGRES_DB_PASSWORD=.*/POSTGRES_DB_PASSWORD='${POSTGRES_DB_PASSWORD}'/" /usr/share/ocsinventory-backend/.env
    source /usr/share/ocsinventory-backend/.env
    runuser -l postgres -c "psql -c \"CREATE DATABASE ${POSTGRES_DB_NAME};\""
    runuser -l postgres -c "psql -c \"CREATE USER ${POSTGRES_DB_USER} WITH PASSWORD '${POSTGRES_DB_PASSWORD}';\""
    runuser -l postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB_NAME} TO ${POSTGRES_DB_USER};\""

    sed -i 's/peer/md5/' /var/lib/pgsql/data/pg_hba.conf
    su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data -l logfile restart"
fi

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

if [ "$(su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data status" | grep "server is running")" ]; then
    echo "Running database migrations..."
    python3 /usr/share/ocsinventory-backend/manage.py migrate
else
    echo "Database not detected, skip migration."
fi

deactivate

chown -R nginx:nginx /usr/share/ocsinventory-backend/
chmod -R 755 /usr/share/ocsinventory-backend/logs

# ocsinventory socket dir and permissions
mkdir -p /var/run/ocsinventory-backend/
chown nginx:nginx /var/run/ocsinventory-backend/
chmod 755 /var/run/ocsinventory-backend/


echo "Starting uWSGI service..."
systemctl restart uwsgi
systemctl enable uwsgi

systemctl restart nginx

echo "Post-installation script completed successfully."

%postun
echo "Clean OCS Inventory Backend files..."
rm -rf /usr/share/ocsinventory-backend
rm -rf /usr/lib/ocsinventory-backend
rm -rf /var/log/ocsinventory-backend
echo "OCS Inventory Backend successfully uninstalled."

%changelog
* Fri Sep 17 2024 Lea Droguet <lea.droguet@ocsinventory-ng.org> - 3.0.0-1
- Initial RPM