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
Requires:       %{name}-plugin-undelete-partitions
Requires:       %{name}-plugin-passwd
Requires:       %{name}-plugin-xserver
Requires:       %{name}-plugin-grub
Requires:       %{name}-plugin-rpm
Requires:       %{name}-gui


%description plugin-all
This package provides all the necessary firstaidkit plugins.  It
probes the system and according to what it finds, it installs the
needed firstaidkit plugins.


%package plugin-undelete-partitions
Group:          Applications/System
Summary:        FirstAidKit plugin to recover erased partitions
BuildRequires:  python-devel, parted-devel, pkgconfig
Requires:       %{name} = %{version}-%{release}
Requires:       parted

%description plugin-undelete-partitions
This FirstAidKit plugin automates the recovery of erased partitions.


%package plugin-passwd
Group:          Applications/System
Summary:        FirstAidKit plugin to manipulate passwd system
Requires:       %{name} = %{version}-%{release}

%description plugin-passwd
This FirstAidKit plugin automates the recovery of the root system
password.


%package plugin-xserver
Group:          Applications/System
Summary:        FirstAidKit plugin to recover xserver configuration files
Requires:       %{name} = %{version}-%{release}
Requires:       rhpl, rhpxl

%description plugin-xserver
This FirstAidKit plugin automates the recovery of the xserver
configuration file xorg.conf.

%package plugin-grub
Group:          Applications/System
Summary:        FirstAidKit plugin to diagnose or repair the GRUB instalation
Requires:       %{name} = %{version}-%{release}
Requires:       anaconda, booty

%description plugin-grub
This FirstAidKit plugin automates the recovery from the GRUB bootloader problems.

%package plugin-rpm
Group:          Applications/System
Summary:        FirstAidKit plugin to diagnose or repair the RPM packaging system
Requires:       %{name} = %{version}-%{release}
Requires:       rpm, rpm-python

%description plugin-rpm
This FirstAidKit plugin automates the tasks related to RPM problems.
For example: corrupted database or important system packages missing.

%package gui
Group:          Applications/System
Summary:        FirstAidKit GUI
Requires:       %{name} = %{version}-%{release}
Requires:       pygtk2

%description gui
This package contains the Gtk based FirstAidKit GUI

%prep
%setup -q
#generate the about file with version and license path
echo "version=%{version}" >> etc/firstaidkit/about
echo "copying=%{_docdir}/COPYING" >> etc/firstaidkit/about

%build
%{__python} setup.py build
%{__make} subdirs

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

#docs
%{__install} -d $RPM_BUILD_ROOT%{_mandir}/man1
%{__install} -p doc/fakplugin.1 doc/firstaidkit.1 $RPM_BUILD_ROOT%{_mandir}/man1
#examples
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/examples
%{__mv} -f plugins/plugin_examples $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/examples

#configuration
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit
%{__install} -p etc/firstaidkit/firstaidkit.conf $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit
%{__install} -p etc/firstaidkit/about $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit

#gui
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/frontend
%{__install} -p frontend/*.py  $RPM_BUILD_ROOT%{_libdir}/firstaidkit/frontend/
%{__install} -p frontend/*.glade  $RPM_BUILD_ROOT%{_libdir}/firstaidkit/frontend/
%{__install} -p frontend/*.gladep  $RPM_BUILD_ROOT%{_libdir}/firstaidkit/frontend/

#plugins
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/plugin_undelete_partitions
%{__cp} -f plugins/plugin_undelete_partitions/{*.py,_undelpart.so} $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/plugin_undelete_partitions/
%{__cp} -f plugins/passwd.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/
%{__cp} -f plugins/xserver.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/plugin_rpm
%{__cp} -f plugins/plugin_rpm/*.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/plugin_rpm/
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/plugin_rpm_lowlevel
%{__cp} -f plugins/plugin_rpm_lowlevel/*.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/plugin_rpm_lowlevel/
%{__cp} -f plugins/plugin_grub.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/
%{__install} -p etc/firstaidkit/firstaidkit-plugin-grub $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit


%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING doc/README doc/FLAGS
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{python_sitelib}/%{name}-%{version}-py2.5.egg-info
%{_bindir}/firstaidkit
%{_sysconfdir}/firstaidkit/firstaidkit.conf
%{_sysconfdir}/firstaidkit/about
%attr(0644,root,root) %{_mandir}/man1/firstaidkit.1.gz

%files gui
%{_libdir}/firstaidkit/frontend/*.py
%{_libdir}/firstaidkit/frontend/*.glade
%{_libdir}/firstaidkit/frontend/*.gladep

%files devel
%{_libdir}/firstaidkit/plugins/examples
%attr(0644,root,root) %{_mandir}/man1/fakplugin.1.gz

%files plugin-all

%files plugin-undelete-partitions
%{_libdir}/firstaidkit/plugins/plugin_undelete_partitions/*.py
%{_libdir}/firstaidkit/plugins/plugin_undelete_partitions/*.so

%files plugin-passwd
%{_libdir}/firstaidkit/plugins/passwd.py

%files plugin-xserver
%{_libdir}/firstaidkit/plugins/xserver.py

%files plugin-rpm
%{_libdir}/firstaidkit/plugins/plugin_rpm_lowlevel/*.py
%{_libdir}/firstaidkit/plugins/plugin_rpm/*.py

%files plugin-grub
%{_libdir}/firstaidkit/plugins/plugin_grub.py
%{_sysconfdir}/firstaidkit/firstaidkit-plugin-grub


