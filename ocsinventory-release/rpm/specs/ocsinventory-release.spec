%define debug_package %{nil}
%define name ocsinventory-release
%define version 1.0.0
%define release 1
%define buildroot %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Name:           %{name}
Version:        %{version}
Release:        %{release}%{dist}
Summary:        OCS Inventory repository configuration and GPG key

Group:          System Environment/Base
License:        GPLv2
URL:            https://www.ocsinventory-ng.org/

Source0:        ocsinventory-el.repo
Source1:        ocsinventory-fc.repo
Source2:        RPM-GPG-KEY-ocsinventory

BuildArch:      noarch
BuildRoot:      %{buildroot}

AutoReqProv:    no

%description
This package installs the OCS Inventory YUM repository configuration
file and the GPG key used to sign OCS Inventory packages.

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d
%if 0%{?rhel}
cp %{SOURCE0} %{buildroot}%{_sysconfdir}/yum.repos.d/ocsinventory.repo
%else
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/yum.repos.d/ocsinventory.repo
%endif

mkdir -p %{buildroot}%{_sysconfdir}/pki/rpm-gpg
cp %{SOURCE2} %{buildroot}%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-ocsinventory

%clean
rm -rf %{buildroot}

%files
%defattr(644, root, root, 755)
%config(noreplace) %{_sysconfdir}/yum.repos.d/ocsinventory.repo
%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-ocsinventory

%changelog
* Fri Jul 31 2026 Charlene Auger <charlene.auger@ocsinventory-ng.org> - 1.0.0-1
- Initial RPM
