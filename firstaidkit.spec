#
# Spec file for firstaidkit
#
# How to create the tar file:
# After cloning the git repo, run the folloing line from the directory that contains firstaidkit.
# VER=`cat firstaidkit/firstaidkit.spec | grep Version | awk 'system(echo  )'` ;  mv firstaidkit/ firstaidkit-$VER/ ; tar cvfj firstaidkit-$VER.tar.bz2 firstaidkit-$VER --exclude='*.git' --exclude='.placeholder'; mv firstaidkit-$VER/ firstaidkit/

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           firstaidkit
Version:        0.1.0
Release:        6%{?dist}
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


%package devel
Group:          Applications/System
Summary:        Devel package for firstaidkit
Requires:       %{name} = %{version}-%{release}

%package plugin-all
Group:          Applications/System
Summary:        All firstaidkit plugins
#
# Since there are no plugins yet, this section only has firstaidkit as requires.
#
Requires:       %{name} = %{version}-%{release}


%description
A tool that automates simple and common system recovery tasks.

%description devel
Provides the examples and requires firstaidkit without plugins.

%description plugin-all
This package provides all the necessary firstaidkit plugins.  It
probes the system and according to what it finds, it installs the
needed firstaidkit plugins.

%prep
%setup -q


%build
%{__python} setup.py build


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__install} -d $RPM_BUILD_ROOT%{_mandir}/man1
%{__install} -p doc/fakplugin.1 doc/firstaidkit.1 $RPM_BUILD_ROOT/%{_mandir}/man1
%{__install} -d $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/examples

%{__cp} -rfp plugins/* $RPM_BUILD_ROOT%{_libdir}/firstaidkit-plugins/examples

%clean
%{__rm} -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING doc/README
# For noarch packages: sitelib
%{python_sitelib}/pyfirstaidkit
%{python_sitelib}/%{name}-%{version}-py2.5.egg-info
%{_bindir}/firstaidkit
%attr(0644,root,root) %{_mandir}/man1/firstaidkit.1.gz

%files devel
%{_libdir}/firstaidkit-plugins/examples
%attr(0644,root,root) %{_mandir}/man1/fakplugin.1.gz

%files plugin-all

%Changelog
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
