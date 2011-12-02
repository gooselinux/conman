Name:               conman
Version:            0.2.5
Release:            2.3%{?dist}
Summary:            The Console Manager

Group:              Applications/System
License:            GPLv2+
URL:                http://home.gna.org/conman/
Source0:            http://download.gna.org/%{name}/%{version}/%{name}-%{version}.tar.bz2
Source1:            %{name}.init
Source2:            %{name}.logrotate
BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:           logrotate
Requires(post):     /sbin/chkconfig
Requires(preun):    /sbin/chkconfig
Requires(preun):    /sbin/service
Requires(postun):   /sbin/service
BuildRequires:      tcp_wrappers

%description
ConMan is a serial console management program designed to support a large
number of console devices and simultaneous users.  It currently supports
local serial devices and remote terminal servers (via the telnet protocol).
Its features include:

  - mapping symbolic names to console devices
  - logging all output from a console device to file
  - supporting monitor (R/O), interactive (R/W), and
    broadcast (W/O) modes of console access
  - allowing clients to join or steal console "write" privileges
  - executing Expect scripts across multiple consoles in parallel

%prep
%setup -q

%build
# not really lib material, more like share
mv lib share
chmod -x share/examples/*.exp
%{__perl} -pi.orig -e 's|cd lib|cd share|g' \
    Makefile.in
%{__perl} -pi -e 's|lib\/|share\/|g' \
    Makefile.in share/examples/*.exp
# don't strip the bins on install, let find-debug.sh do it
%{__perl} -pi -e 's|-m 755 -s conman|-m 755 conman|g' \
    Makefile.in

%configure --with-tcp-wrappers
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# coerce installation to conform to Fedora rules
if [ "%{_sysconfdir}/init.d" != "%{_initddir}" ]; then
	mkdir -p $RPM_BUILD_ROOT%{_initddir}
	mv $RPM_BUILD_ROOT%{_sysconfdir}/init.d/* $RPM_BUILD_ROOT%{_initddir}/
fi
# put in our own initscript and logrotate
install -m 0755 %{SOURCE1} $RPM_BUILD_ROOT%{_initddir}/%{name}
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}
# make log directories
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}.old
# examples don't belong in datadir...
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/examples
# these shouldn't be executable
chmod -x $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
# adjust perms on main config file
chmod 644 $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

%clean
rm -rf "$RPM_BUILD_ROOT"

%post
/sbin/chkconfig --add conman

%preun
if [ "$1" = 0 ]; then
  /sbin/service conman stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del conman
fi

%postun
if [ "$1" -ge 1 ]; then
  /sbin/service conman condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING FAQ NEWS README
%doc share/examples
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_initddir}/%{name}
%{_localstatedir}/log/%{name}
%{_localstatedir}/log/%{name}.old
%{_bindir}/*
%{_sbindir}/*
%{_datadir}/%{name}
%{_mandir}/*/*

%changelog
* Wed May 12 2010 Denys Vlasenko <dvlasenk@redhat.com> - 0.2.5-2.3
- Fixed location and logic of initscript.
- Resolves: rhbz#576846, rhbz#576247.

* Fri Mar 12 2010 Denys Vlasenko <dvlasenk@redhat.com> - 0.2.5-2.2
- Added README to docs
- Fixed name-repeated-in-summary rpmlint warning

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.2.5-2.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun 08 2009 Steven M. Parrish <tuxbrewr@fedoraproject.org> - 0.2.5-0
- New upstream release

* Mon Apr 20 2009 Steven M. Parrish <tuxbrewr@fedoraproject.org> - 0.2.4.1-1
- New upstream release

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Oct 06 2008 Jarod Wilson <jarod@redhat.com> 0.2.2-2
- The console option in conman.conf is case-insensitive, so relax
  defined consoles check in initscript (Mark McLoughlin, #465777)

* Mon Sep 08 2008 Steven M. Parrish <smparrish@shallowcreek.net> 0.2.2-1
- New upstream release

* Fri May 02 2008 Jarod Wilson <jwilson@redhat.com> 0.2.1-1
- New upstream release

* Wed Feb 13 2008 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-8
- Bump and rebuild for gcc 4.3

* Thu Apr 26 2007 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-7
- Update project urls
- Fix up initscript exit codes (#237936)

* Tue Sep 05 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-6
- Bump for new glibc

* Fri Jul 28 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-5
- Properly enable smp_mflags this time

* Fri Jul 28 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-4
- Add Reqs on chkconfig and service
- Turn on smp_mflags
- Initial build for RHEL5

* Wed Jul 05 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-3
- Add missing condrestart fuction to initscript

* Tue Jun 27 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-2
- Don't strip bins on make install, leave for find-debug.sh

* Tue Jun 27 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.2-1
- Update to 0.1.9.2

* Tue Jun 20 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.1-3
- Add Requires: logrotate
- Ugh, conmand exits cleanly if no CONSOLE(s) are defined in
  /etc/conman.conf, add check to initscript to report failure
  if none are defined

* Wed Jun 14 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.1-2
- Create log directories and install working logrotate config
- Use a much cleaner RH/FC-specific initscript

* Tue Jun 13 2006 Jarod Wilson <jwilson@redhat.com> 0.1.9.1-1
- Initial build for Fedora Extras
