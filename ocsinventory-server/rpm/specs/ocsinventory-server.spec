%define debug_package %{nil}
%define name ocsinventory-server
%define version 3.0.0~rc2
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Name:           %{name}
Version:        %{version}
Release:        %{release}%{dist}
Summary:        OCS Inventory Server (Backend API + Web Console)

Group:          Applications/System
License:        GPLv2
URL:            https://www.ocsinventory-ng.org/

BuildArch:      noarch
BuildRoot:      %{buildroot}
Requires:       ocsinventory-backend = %{version}-%{release}, ocsinventory-frontend = %{version}-%{release}

AutoReqProv:    no

%description
Meta package installing the backend API and web console.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_docdir}/%{name}
cat <<'EOF' > %{buildroot}%{_docdir}/%{name}/README
OCS Inventory Server meta package.
This package pulls the backend API (backend) and the web console (frontend).
EOF

%clean
rm -rf %{buildroot}

%files
%defattr(644, root, root, 755)
%doc %{_docdir}/%{name}/README

%changelog
* Wed Aug 26 2026 OCS Inventory Release Bot <ci@ocsinventory-ng.org> - 3.0.0~rc2-1
- Release 3.0.0-rc2.

* Thu Jun 04 2026 Léa Droguet <lea.droguet@factorfx.com> - 3.0.0~rc1-1
- Initial RPM
