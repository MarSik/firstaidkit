%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
#I don't want the unpackaged file check
%define _unpackaged_files_terminate_build 0

Name:           firstaidkit
Version:        0.2.2
Release:        1%{?dist}
Summary:        System Rescue Tool

Group:          Applications/System
License:        GPLv2+
URL:            http://fedorahosted.org/firstaidkit
Source0:        %{name}-%{version}.tar.bz2
Source3:        %{name}.desktop
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  desktop-file-utils
BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
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
Summary:        All firstaidkit plugins, and the gui
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-plugin-passwd
Requires:       %{name}-plugin-xserver
Requires:       %{name}-plugin-grub
Requires:       %{name}-gui
Requires:       %{name}-plugin-mdadm-conf
#Requires:       %{name}-plugin-undelete-partitions
#Requires:       %{name}-plugin-rpm


%description plugin-all
This package provides all the necessary firstaidkit plugins.  It
probes the system and according to what it finds, it installs the
needed firstaidkit plugins.

%package gui
Group:          Applications/System
Summary:        FirstAidKit GUI
Requires:       %{name} = %{version}-%{release}
Requires:       pygtk2, pygtk2-libglade

%description gui
This package contains the Gtk based FirstAidKit GUI


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

%description plugin-xserver
This FirstAidKit plugin automates the recovery of the xserver
configuration file xorg.conf.


%package plugin-grub
Group:          Applications/System
Summary:        FirstAidKit plugin to diagnose or repair the GRUB instalation
Requires:       %{name} = %{version}-%{release}
Requires:       dbus-python
Requires:       grub
Requires:       pyparted

%description plugin-grub
This FirstAidKit plugin automates the recovery from the GRUB bootloader problems.


%package plugin-mdadm-conf
Group:          Applications/System
Summary:        Firstaidkit plugin to diagnose software raid configuration file
Requires:       %{name} = %{version}-%{release}
Requires:       mdadm

%description plugin-mdadm-conf
This plugin will assess the validity and existence of the mdadm.conf file.
The file will get replaced if any inconsistencies are found.


#%package plugin-rpm
#Group:          Applications/System
#Summary:        FirstAidKit plugin to diagnose or repair the RPM packaging system
#Requires:       %{name} = %{version}-%{release}
#Requires:       rpm, rpm-python
#
#%description plugin-rpm
#This FirstAidKit plugin automates the tasks related to RPM problems.
#For example: corrupted database or important system packages missing.
#
#%package plugin-undelete-partitions
#Group:          Applications/System
#Summary:        FirstAidKit plugin to recover erased partitions
#BuildRequires:  python-devel, parted-devel, pkgconfig
#Requires:       %{name} = %{version}-%{release}
#Requires:       parted
#
#%description plugin-undelete-partitions
#This FirstAidKit plugin automates the recovery of erased partitions.


%prep
%setup -q
./test


%build
%{__python} setup.py build
%{__make} build


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

#docs
%{__install} -d $RPM_BUILD_ROOT%{_mandir}/man1
%{__install} -d $RPM_BUILD_ROOT%{_datadir}/doc/%name-%version
%{__install} -p doc/firstaidkit-plugin.1 doc/firstaidkit.1 $RPM_BUILD_ROOT%{_mandir}/man1
%{__install} -p COPYING $RPM_BUILD_ROOT%{_datadir}/doc/%name-%version/COPYING

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
desktop-file-install --vendor="fedora" --dir=${RPM_BUILD_ROOT}%{_datadir}/applications %{SOURCE3}

#plugins
%{__cp} -f plugins/passwd.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/
%{__cp} -f plugins/xserver.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/grub
%{__cp} -f plugins/grub/*.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/grub
%{__cp} -f plugins/mdadm_conf.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/
#%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/undelparts
#%{__cp} -f plugins/undelparts/{*.py,_undelpart.so} $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/undelparts/
#%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/rpm
#%{__cp} -f plugins/rpm/*.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/rpm/
#%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/rpm_lowlevel
#%{__cp} -f plugins/rpm_lowlevel/*.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/rpm_lowlevel/

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info
%{_bindir}/firstaidkit
%dir %{_bindir}/firstaidkit
%{_bindir}/firstaidkitrevert
%config(noreplace) %{_sysconfdir}/firstaidkit/firstaidkit.conf
%config(noreplace) %{_sysconfdir}/firstaidkit/about
%attr(0644,root,root) %{_mandir}/man1/firstaidkit.1.gz
%attr(0644,root,root) %{_datadir}/doc/%name-%version/COPYING
%dir %{_libdir}/firstaidkit
%dir %{_libdir}/firstaidkit/plugins
%dir %{_datadir}/doc/%name-%version

%files gui
%{_libdir}/firstaidkit/frontend/*.py*
%{_libdir}/firstaidkit/frontend/*.glade
%{_libdir}/firstaidkit/frontend/*.gladep
%{_datadir}/applications/*.desktop
%dir %{_libdir}/firstaidkit/frontend

%files devel
%{_libdir}/firstaidkit/plugins/examples
%attr(0644,root,root) %{_mandir}/man1/firstaidkit-plugin.1.gz

%files plugin-all

%files plugin-passwd
%{_libdir}/firstaidkit/plugins/passwd.py*

%files plugin-xserver
%{_libdir}/firstaidkit/plugins/xserver.py*

%files plugin-grub
%{_libdir}/firstaidkit/plugins/grub/*
%dir %{_libdir}/firstaidkit/plugins/grub/*

%files plugin-mdadm-conf
%{_libdir}/firstaidkit/plugins/mdadm_conf.py*

#%files plugin-undelete-partitions
#%{_libdir}/firstaidkit/plugins/undelparts/*.py*
#%{_libdir}/firstaidkit/plugins/undelparts/*.so
#
#%files plugin-rpm
#%{_libdir}/firstaidkit/plugins/rpm_lowlevel/*
#%{_libdir}/firstaidkit/plugins/rpm/*
