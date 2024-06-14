%define debug_package %{nil}
%define name ocsinventory-frontend
%define version 0.1.0
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Name: %{name}
Version: %{version}
Release: %{release}
Summary: ocsinventory-frontend

Group: Applications/Internet
License: GPLv2
URL: http://www.ocsinventory-ng.org/

Source0: %{name}.tar.gz
Source1: ocsinventory-frontend.conf

BuildRoot: %{buildroot}
Requires: httpd
AutoReqProv: no

%description
Web UI for OCS Inventory Backend API

%prep
%setup -q -c -n %{name}

%install
mkdir -p %{buildroot}/usr/share
cp -r ./ %{buildroot}/usr/share
mkdir -p %{buildroot}/var/log/ocsinventory-frontend
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d

mv %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d

%clean
rm -rf %{buildroot}

%files
%defattr(644, apache, apache, 755)
/usr/share/ocsinventory-frontend
/var/log/ocsinventory-frontend
%config(noreplace) %{_sysconfdir}/httpd/conf.d/ocsinventory-frontend.conf

%changelog
* Fri Jun 14 2024 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 0.1.0-1
- Initial RPM
