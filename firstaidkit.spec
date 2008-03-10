%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
#I don't want the unpackaged file check
%define _unpackaged_files_terminate_build 0

Name:           firstaidkit
Version:        0.1.1
Release:        1%{?dist}
Summary:        System Rescue Tool

Group:          Applications/System
License:        GPLv2+
URL:            http://fedorahosted.org/firstaidkit
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel
# Take this away in the future. when f7 is gone.
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif
BuildArch:      noarch

%description
A tool that automates simple and common system recovery tasks.


%package devel
Group:          Applications/System
Summary:        Devel package for firstaidkit
Requires:       %{name} = %{version}-%{release}

%description devel
Provides the examples and requires firstaidkit without plugins.


%package plugin-all
Group:          Applications/System
Summary:        All firstaidkit plugins
Requires:       %{name} = %{version}-%{release}

%description plugin-all
This package provides all the necessary firstaidkit plugins.  It
probes the system and according to what it finds, it installs the
needed firstaidkit plugins.


%package plugin-undelete-partitions
Group:          Applications/System
Summary:        FirstAidKit plugin to recover erased partitions
BuildRequires:  python-devel, parted-devel, pkgconfig
Requires:       parted

%description plugin-undelete-partitions
This FirstAidKit plugin automates the recovery of erased partitions.


%package plugin-passwd
Group:          Applications/System
Summary:        FirstAidKit plugin to manipulate passwd system

%description plugin-passwd
This plugin provides operations for convenient manipulation
with the password system.


%prep
%setup -q


%build
%{__python} setup.py build
%{__make} subdirs


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
#docs
%{__install} -d $RPM_BUILD_ROOT%{_mandir}/man1 $RPM_BUILD_ROOT%{_sysconfdir}
%{__install} -p doc/fakplugin.1 doc/firstaidkit.1 $RPM_BUILD_ROOT%{_mandir}/man1
#examples
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/examples
%{__mv} -f plugins/plugin_examples $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/examples
#configuration
%{__install} -p etc/firstaidkit.conf $RPM_BUILD_ROOT%{_sysconfdir}

#plugins
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/plugin_undelete_partitions
%{__cp} -f plugins/plugin_undelete_partitions/{*.py,_undelpart.so} $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/plugin_undelete_partitions/
%{__cp} -f plugins/passwd.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/


%clean
%{__rm} -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING doc/README
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{python_sitelib}/%{name}-%{version}-py2.5.egg-info
%{_bindir}/firstaidkit
%{_sysconfdir}/firstaidkit.conf
%attr(0644,root,root) %{_mandir}/man1/firstaidkit.1.gz

%files devel
%{_libdir}/firstaidkit-plugins/examples
%attr(0644,root,root) %{_mandir}/man1/fakplugin.1.gz

%files plugin-all

%files plugin-undelete-partitions
%{_libdir}/firstaidkit-plugins/plugin_undelete_partitions/*.py
%{_libdir}/firstaidkit-plugins/plugin_undelete_partitions/*.so

%files plugin-passwd
%{_libdir}/firstaidkit-plugins/passwd.py

%Changelog
* Mon Mar 10 2008 Joel Granados <jgranado@redhat.com> 0.1.1-1
- new version

* Wed Jan 09 2008 Joel Granados <jgranado@redhat.com> 0.1.0-6
- Put examples under the firstaidkit-plugins dir
- Create a firstaidkit-plugin-all package

* Tue Jan 08 2008 Joel Granados <jgranado@redhat.com> 0.1.0-5
- Leave just the firstaidkit and firstaidkit-devel pacages.

* Mon Jan 07 2008 Joel Granados <jgranado@redhat.com> 0.1.0-4
- Create firstaidkit dummy package
- Create firstaidkit-pluginsystem subpackage
- Create firstaidkit-devel subpackage
- Bump the release tag

* Fri Jan 04 2008 Joel Granados <jgranado@redhat.com> 0.1.0-3
- Change the License variable
- Fix man page being executable

* Fri Jan 04 2008 Joel Granados <jgranado@redhat.com> 0.1.0-2
- Include python-setuptools-devel in the BuildRequires
- Added manpage stuff in the spec file

* Wed Jan 02 2008 Joel Granados <jgranado@redhat.com> 0.1.0-1
- Initial spec
