%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           firstaidkit
Version:        0.1.0
Release:        3%{?dist}
Summary:        System Rescue Tool

Group:          Applications/System
License:        GPLv2+
URL:            http://fedorahosted.org/firstaidkit
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  python-devel

# Maybe its just enough with the python-setuptools-devel.  Lets use both for now.
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif

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
%{__install} -d $RPM_BUILD_ROOT/%{_mandir}/man1
%{__install} doc/fakplugin.1 $RPM_BUILD_ROOT/%{_mandir}/man1
%{__cp} -rfp plugins/* $RPM_BUILD_ROOT/%{_libexecdir}/firstaidkit/plugins

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING doc/README doc/PLUGINS
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{python_sitelib}/%{name}-%{version}-py2.5.egg-info
%{_bindir}/firstaidkit
%{_libexecdir}/firstaidkit/plugins/*
%attr(0644,-,-) %{_mandir}/man1/fakplugin.1.gz

%Changelog
* Fri Jan 04 2008 Joel Granados <jgranado@redhat.com> 0.1.0-3
- Change the License variable
- Fix man page being executable

* Fri Jan 04 2008 Joel Granados <jgranado@redhat.com> 0.1.0-2
- Include python-setuptools-devel in the BuildRequires
- Added manpage stuff in the spec file

* Wed Jan 02 2008 Joel Granados <jgranado@redhat.com> 0.1.0-1
- Initial spec
