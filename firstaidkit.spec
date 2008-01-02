%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           firstaidkit
Version:        0.1.0
Release:        1%{?dist}
Summary:        System Rescue Tool

Group:          Applications/System
License:        GPLv2
URL:            http://fedorahosted.org/firstaidkit
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  python-devel

BuildArch:      noarch

%description
A tool that automates simple and common system recovery tasks.


%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__install} -d $RPM_BUILD_ROOT/%{_libexecdir}/firstaidkit/plugins
%{__cp} -rf plugins/* $RPM_BUILD_ROOT/%{_libexecdir}/firstaidkit/plugins


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING GPL doc/README doc/PLUGINS
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{_bindir}/firstaidkit
%{_libexecdir}/firstaidkit/plugins/*


%Changelog
* Wed Jan 02 2008 Joel Granados <jgranado@redhat.com> 0.1.0-1
- Initial spec
