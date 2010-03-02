%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
#I don't want the unpackaged file check
%define _unpackaged_files_terminate_build 0

Name:           firstaidkit
Version:        0.2.9
Release:        1%{?dist}
Summary:        System Rescue Tool

Group:          Applications/System
License:        GPLv2+
Url:            http://git.fedorahosted.org/git/?p=firstaidkit.git;a=snapshot;h=%{name}-%{version}-%{release};sf=tgz
Source0:        %{name}-%{version}.tar.gz
Source3:        %{name}.desktop
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  desktop-file-utils
BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
Requires:	newt
Requires:       %{name}-engine
Requires:       %{name}-plugin-all

%description
A tool that automates simple and common system recovery tasks.


%package engine
Group:          Applications/System
Summary:        Core engine for firstaidkit
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description engine
Base engine files needed for the firstaidkit to work

%package devel
Group:          Applications/System
Summary:        Devel package for firstaidkit
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description devel
Provides the examples and requires firstaidkit without plugins.


%package plugin-all
Group:          Applications/System
Summary:        All firstaidkit plugins, and the gui
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-plugin-passwd
Requires:       %{name}-plugin-xserver
%ifnarch s390 s390x ppc64 ppc sparc
Requires:       %{name}-plugin-grub
%endif
Requires:       %{name}-gui
Requires:       %{name}-plugin-mdadm-conf
Requires:       %{name}-plugin-key-recovery
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
Requires:       pygtk2, pygtk2-libglade, zenity
BuildArch:      noarch

%description gui
This package contains the Gtk based FirstAidKit GUI


%package plugin-passwd
Group:          Applications/System
Summary:        FirstAidKit plugin to manipulate passwd system
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description plugin-passwd
This FirstAidKit plugin automates the recovery of the root system
password.


%package plugin-xserver
Group:          Applications/System
Summary:        FirstAidKit plugin to recover xserver configuration files
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description plugin-xserver
This FirstAidKit plugin automates the recovery of the xserver
configuration file xorg.conf.


%ifnarch s390 s390x ppc64 ppc sparc
%package plugin-grub
Group:          Applications/System
Summary:        FirstAidKit plugin to diagnose or repair the GRUB instalation
Requires:       %{name} = %{version}-%{release}
Requires:       dbus-python
Requires:       grub
Requires:       pyparted

%description plugin-grub
This FirstAidKit plugin automates the recovery from the GRUB bootloader problems.
%endif


%package plugin-mdadm-conf
Group:          Applications/System
Summary:        Firstaidkit plugin to diagnose software raid configuration file
Requires:       %{name} = %{version}-%{release}
Requires:       mdadm
BuildArch:      noarch

%description plugin-mdadm-conf
This plugin will assess the validity and existence of the mdadm.conf file.
The file will get replaced if any inconsistencies are found.

%package plugin-key-recovery
Group:          Applications/System
Summary:        Firstaidkit plugin to recover key encryption keys
Requires:       %{name} = %{version}-%{release}
Requires:       python-volume_key, python-nss
BuildArch:      noarch

%description plugin-key-recovery
This plugin helps recover encryption keys using a previously created escrow
packet.

#%package plugin-rpm
#Group:          Applications/System
#Summary:        FirstAidKit plugin to diagnose or repair the RPM packaging system
#Requires:       %{name} = %{version}-%{release}
#Requires:       rpm, rpm-python
#BuildArch:      noarch
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

#configuration
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit
%{__install} -p etc/firstaidkit/firstaidkit.conf $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit
%{__install} -p etc/firstaidkit/about $RPM_BUILD_ROOT%{_sysconfdir}/firstaidkit

#gui
%{__install} -d $RPM_BUILD_ROOT/usr/lib/firstaidkit/frontend
%{__install} -p frontend/*.py  $RPM_BUILD_ROOT/usr/lib/firstaidkit/frontend/
%{__install} -p frontend/*.glade  $RPM_BUILD_ROOT/usr/lib/firstaidkit/frontend/
%{__install} -p frontend/*.gladep  $RPM_BUILD_ROOT/usr/lib/firstaidkit/frontend/
desktop-file-install --vendor="fedora" --dir=${RPM_BUILD_ROOT}%{_datadir}/applications %{SOURCE3}

#examples
%{__install} -d $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/examples
%{__mv} -f plugins/plugin_examples $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/examples

#plugins arch independent and dependent
%{__install} -d $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins
%{__install} -d $RPM_BUILD_ROOT%{libdir}/firstaidkit/plugins

%{__cp} -f plugins/passwd.py $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/
%{__cp} -f plugins/xserver.py $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/grub
%{__cp} -f plugins/grub/*.py $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/grub
%{__cp} -f plugins/mdadm_conf.py $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/
%{__cp} -f plugins/key_recovery.py $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/

#%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/undelparts
#%{__cp} -f plugins/undelparts/{*.py,_undelpart.so} $RPM_BUILD_ROOT%{_libdir}/firstaidkit/plugins/undelparts/
#%{__install} -d $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/rpm
#%{__cp} -f plugins/rpm/*.py $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/rpm/
#%{__install} -d $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/rpm_lowlevel
#%{__cp} -f plugins/rpm_lowlevel/*.py $RPM_BUILD_ROOT/usr/lib/firstaidkit/plugins/rpm_lowlevel/

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{_libdir}/firstaidkit
%dir %{_libdir}/firstaidkit/plugins
%dir /usr/lib/firstaidkit
%dir /usr/lib/firstaidkit/plugins

%files engine
%config %{_sysconfdir}/firstaidkit/about
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info
%{_bindir}/firstaidkit
%{_bindir}/firstaidkit-qs
%{_bindir}/firstaidkitrevert
%config(noreplace) %{_sysconfdir}/firstaidkit/firstaidkit.conf
%attr(0644,root,root) %{_mandir}/man1/firstaidkit.1.gz
%attr(0644,root,root) %{_datadir}/doc/%name-%version/COPYING
%dir %{_datadir}/doc/%name-%version

%files gui
/usr/lib/firstaidkit/frontend/*.py*
/usr/lib/firstaidkit/frontend/*.glade
/usr/lib/firstaidkit/frontend/*.gladep
%{_datadir}/applications/*.desktop
%dir /usr/lib/firstaidkit/frontend

%files devel
/usr/lib/firstaidkit/plugins/examples
%attr(0644,root,root) %{_mandir}/man1/firstaidkit-plugin.1.gz

%files plugin-all

%files plugin-passwd
/usr/lib/firstaidkit/plugins/passwd.py*

%files plugin-xserver
/usr/lib/firstaidkit/plugins/xserver.py*

%ifnarch s390 s390x ppc64 ppc sparc
%files plugin-grub
%{_libdir}/firstaidkit/plugins/grub/*
%dir %{_libdir}/firstaidkit/plugins/grub
%endif

%files plugin-mdadm-conf
/usr/lib/firstaidkit/plugins/mdadm_conf.py*

%files plugin-key-recovery
/usr/lib/firstaidkit/plugins/key_recovery.py*

#%files plugin-undelete-partitions
#%{_libdir}/firstaidkit/plugins/undelparts/*.py*
#%{_libdir}/firstaidkit/plugins/undelparts/*.so
#
#%files plugin-rpm
#/usr/lib/firstaidkit/plugins/rpm_lowlevel/*
#

%changelog
* Mon Mar 01 2010 Martin Sivak <msivak@redhat.com> - 0.2.9-1
- Make most of the subpackages arch independent as they
  contain only python code
  Related: rhbz#557202

* Thu Jan 21 2010 Martin Sivak <msivak@redhat.com> - 0.2.8-6
- use ifnarch for ackages section too
  Related: rhbz#557202

* Thu Jan 21 2010 Martin Sivak <msivak@redhat.com> - 0.2.8-5
- ExcludeArch is global directive, use ifnarch instead
  Related: rhbz#557202

* Thu Jan 21 2010 Martin Sivak <msivak@redhat.com> - 0.2.8-4
- Error in .spec release line
  Related: rhbz#557202

* Thu Jan 21 2010 Martin Sivak <msivak@redhat.com> - 0.2.8-3
- wrong Source0 in spec file
  Related: rhbz#557202

* Thu Jan 21 2010 Martin Sivak <msivak@redhat.com> - 0.2.8-2
- we need new version name, because it is not possible to retag
  Related: rhbz#557202

* Thu Jan 21 2010 Martin Sivak <msivak@redhat.com> - 0.2.8-1
- Set different Url in spec file
- Make package arch specific
  Resolves: rhbz#557202

* Tue Sep 29 2009 Martin Sivak <msivak@redhat.com> - 0.2.7-1
- Make the dialog in whiptail bigger, so it looks nicer

* Tue Sep 22 2009 Martin Sivak <msivak@redhat.com> - 0.2.6-1
- Use whiptail instead of dialog for firstaidkit-qs

* Wed Aug 19 2009 Joel Granados <jgranado@redhat.com> - 0.2.5-1
- Docs updated, new artwork

* Tue Aug 04 2009 Martin Sivak <msivak@redhat.com> - 0.2.4-1
- Fix temp file generation in firstaidkit-qs

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 17 2009 Martin Sivak <msivak@redhat.com> - 0.2.3-4
- Simple enhancement to the API (inreplyto)

* Mon Jul 13 2009 Martin Sivak <msivak@redhat.com> - 0.2.3-3
- Add timeout to firstaidkit-qs

* Mon Jul 13 2009 Martin Sivak <msivak@redhat.com> - 0.2.3-2
- Fixed firstaidkit-qs included..

* Mon Jul 13 2009 Martin Sivak <msivak@redhat.com> - 0.2.3-1
- Add firstaidkit-qs script
- Do not build undelparts plugin since we ignore it anyways

* Mon Jun 29 2009 Martin Sivak <msivak@redhat.com> - 0.2.2-10
- Exclude grub plugin from s390 archs

* Thu Mar 19 2009 Joel Granados <jgranado@redhat.com> - 0.2.2-9
- Track the grub plugin directory.

* Thu Mar 19 2009 Joel Granados <jgranado@redhat.com> - 0.2.2-8
- Track the sysconfig directory.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jan 05 2009 Joel Granados <jgranado@redhat.com> - 0.2.2-6
- The ppc and ppc64 arch do not handle grub as their bootloader.

* Thu Dec 04 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.2.2-5
- Rebuild for Python 2.6

* Sun Nov 30 2008 Joel Granados <jgranado@redhat.com> - 0.2.2-4
- Include the firstaidkit directories in the package.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.2.2-3
- Fix locations for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.2.2-2
- Rebuild for Python 2.6

* Thu Nov 20 2008 Joel Granados <jgranado@redhat.com> 0.2.2-1
- Update to new version.

* Thu Aug 28 2008 Michael Schwendt <mschwendt@fedoraproject.org> 0.2.1-2
- Include unowned directories.

* Tue Jul 15 2008 Joel Granados <jgranado@redhat.com> 0.2.1-1
- New version
- Brings in a new plugin.

* Tue Jun 3 2008 Joel Granados <jgranado@redhat.com> 0.2.0-1
- New upstream version
- Fixup the spec file
- Erase the unneeded patch files

* Thu Mar 13 2008 Joel Granados <jgranado@redhat.com> 0.1.1-4
- Fix dependency with passwd plugin

* Tue Mar 11 2008 Joel Granados <jgranado@redhat.com> 0.1.1-3
- Rebuild

* Tue Mar 11 2008 Joel Granados <jgranado@redhat.com> 0.1.1-2
- Fix dependency problem for ppc64
- Patch a syntax error

* Mon Mar 10 2008 Joel Granados <jgranado@redhat.com> 0.1.1-1
- New version

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
%{_libdir}/firstaidkit/plugins/rpm/*
