%define debug_package %{nil}
%define name ocsinventory-frontend
%define version 3.0.0~rc1
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Name: %{name}
Version: %{version}
Release: %{release}
Summary: ocsinventory-frontend

Group: Applications/Internet
License: GPLv2
URL: http://www.ocsinventory-ng.org/

Source0: %{name}-%{version}.tar.gz
Source1: ocsinventory-frontend.conf

BuildRoot: %{buildroot}
Requires: nginx
AutoReqProv: no

%description
Web UI for OCS Inventory Backend API

%prep
%setup -q -c -n %{name}-%{version}

%install
mkdir -p %{buildroot}/usr/share
cp -r ./ %{buildroot}/usr/share
mkdir -p %{buildroot}/var/log/ocsinventory-frontend
mkdir -p %{buildroot}%{_sysconfdir}/nginx/conf.d

cp %{SOURCE1} %{buildroot}%{_sysconfdir}/nginx/conf.d/ocsinventory-frontend.conf

%clean
rm -rf %{buildroot}

%post
chown -R nginx:nginx /usr/share/ocsinventory-frontend
systemctl restart nginx

%files
%defattr(644, nginx, nginx, 755)
/usr/share/ocsinventory-frontend
/var/log/ocsinventory-frontend
%config(noreplace) %{_sysconfdir}/nginx/conf.d/ocsinventory-frontend.conf

%changelog
* Thu Jun 04 2026 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 3.0.0~rc1-1
- Initial RPM
