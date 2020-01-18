# Tests are EPEL only
%bcond_with tests

# No Python 3 by default
%bcond_with python3

%global srcname urllib3

Name:           python-%{srcname}
Version:        1.10.2
Release:        7%{?dist}
Summary:        Python HTTP library with thread-safe connection pooling and file post

License:        MIT
URL:            http://urllib3.readthedocs.org/
Source0:        https://pypi.python.org/packages/source/u/%{srcname}/%{srcname}-%{version}.tar.gz

# Patch to change default behaviour to check SSL certs for validity
# https://bugzilla.redhat.com/show_bug.cgi?id=855320
Patch0:         python-urllib3-default-ssl-cert-validate.patch

# Patch for the PoolManager instance to consider additional SSL
# configuration when providing a pooled connection for a request.
# https://bugzilla.redhat.com/show_bug.cgi?id=1329395
# Upstream issue: https://github.com/shazow/urllib3/pull/830
Patch1: key-connection-pools-off-custom-keys.patch

# Support IP address SAN fields.
# https://bugzilla.redhat.com/show_bug.cgi?id=1434114
# Upstream: https://github.com/shazow/urllib3/pull/922
Patch2: Add-support-for-IP-address-SAN-fields.patch

# Patch for CVE-2018-20060
# Cross-host redirect does not remove Authorization header allow
# for credential exposure
# Backported without tests!
# https://bugzilla.redhat.com/show_bug.cgi?id=1649153
# Upstream: https://github.com/urllib3/urllib3/pull/1346
Patch3: CVE-2018-20060.patch

# Patch for CVE-2019-9740
# CRLF injection due to not encoding the '\r\n' sequence leading to possible
# attack on internal service.
# https://github.com/urllib3/urllib3/pull/1591/commits/c147f359520cab339ec96b3ef96e471c0da261f6
# https://github.com/urllib3/urllib3/pull/1593/commits/e951dfc83a642b0b5239559cb1c8cc287481f1ae
# https://bugzilla.redhat.com/show_bug.cgi?id=1700824
Patch4: CVE-2019-9740.patch

BuildArch:      noarch

Requires:       ca-certificates

# Previously bundled things:
Requires:       python-six
Requires:       python-backports-ssl_match_hostname
Requires:       python-ipaddress

%if 0%{?rhel} <= 6
BuildRequires:  python-ordereddict
Requires:       python-ordereddict
%endif

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-six
BuildRequires:  python-backports-ssl_match_hostname
BuildRequires:  python-ipaddress
# For unittests
%if %{with tests}
BuildRequires: python-nose
BuildRequires: python-tornado
BuildRequires: python-mock
%endif

%{?python_provide:%python_provide %{name}}

%description
Python HTTP module with connection pooling and file POST abilities.


%if %{with python3}
%package -n python3-%{srcname}
Summary:        Python 3 HTTP library with thread-safe connection pooling and file post
%{?python_provide:%python_provide python3-%{srcname}}

Requires:       ca-certificates
Requires:       python3-six
BuildRequires:  python3-devel

# For unittests
%if %{with tests}
BuildRequires:  python3-nose
BuildRequires:  python3-six
BuildRequires:  python3-tornado
BuildRequires:  python3-mock
%endif # with tests

%description -n python3-%{srcname}
Python3 HTTP module with connection pooling and file POST abilities.
%endif # with python3


%prep
%setup -q -n %{srcname}-%{version}

# Drop the dummyserver tests in koji.  They fail there in real builds, but not
# in scratch builds (weird).
rm -rf test/with_dummyserver/

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1


%build
%py2_build

%if %{with python3}
%py3_build
%endif

%install
%py2_install

rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python2_sitelib}/urllib3/packages/
# ovirt composes remove *.py files, leaving only *.pyc files there; this means we have to symlink
#  six.py* to make sure urllib3.packages.six will be importable
for i in ../../six.py{,o,c}; do
  ln -s $i %{buildroot}/%{python2_sitelib}/urllib3/packages/
done
ln -s ../../backports/ssl_match_hostname %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname

# dummyserver is part of the unittest framework
rm -rf %{buildroot}%{python2_sitelib}/dummyserver

%if %{with python3}
%py3_install

# dummyserver is part of the unittest framework
rm -rf %{buildroot}%{python3_sitelib}/dummyserver
%endif # with python3

%if %{with tests}
%check
nosetests-%{python2_version}

%if %{with python3}
nosetests-%{python3_version}
%endif # with python3
%endif # with tests

%files
%doc CHANGES.rst README.rst CONTRIBUTORS.txt
%license LICENSE.txt
%{python2_sitelib}/urllib3*

%if %{with python3}
%files -n python3-%{srcname}
%doc CHANGES.rst README.rst CONTRIBUTORS.txt
%license LICENSE.txt
%{python3_sitelib}/urllib3*
%endif # with python3

%changelog
* Fri May 03 2019 Miro Hrončok <mhroncok@redhat.com> - 1.10.2-7
- Provide python2-urllib3
- Add patch for CVE-2019-11236
Resolves: rhbz#1703360

* Mon Mar 04 2019 Lumír Balhar <lbalhar@redhat.com> - 1.10.2-6
- Source URL switched to HTTPS protocol
- Add patch for CVE-2018-20060
Resolves: rhbz#1658471

* Wed Oct 11 2017 Iryna Shcherbina <ishcherb@redhat.com> - 1.10.2-5
- Add patch to support IP address SAN fields.
Resolves: rhbz#1434114

* Thu Sep 14 2017 Charalampos Stratakis <cstratak@redhat.com> - 1.10.2-4
- Update patch to find ca_certs in the correct location.
Resolves: rhbz#1450213

* Mon Jan 23 2017 Iryna Shcherbina <ishcherb@redhat.com> - 1.10.2-3
- Fix PoolManager instance to take into account new SSL configuration
Resolves: rhbz#1329395

* Mon Jul 27 2015 bkabrda <bkabrda@redhat.com> - 1.10.2-2
- Fix the way we unbundle six to make ovirt work even when they remove .py files
Resolves: rhbz#1247093

* Mon Apr 13 2015 Matej Stuchlik <mstuchli@redhat.com> - 1.10.2-1
- Update to 1.10.2
Resolves: rhbz#1226901

* Fri Mar  1 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-5
- Unbundling finished!

* Fri Mar 01 2013 Ralph Bean <rbean@redhat.com> - 1.5-4
- Upstream patch to fix Accept header when behind a proxy.
- Reorganize patch numbers to more clearly distinguish them.

* Wed Feb 27 2013 Ralph Bean <rbean@redhat.com> - 1.5-3
- Renamed patches to python-urllib3-*
- Fixed ssl check patch to use the correct cert path for Fedora.
- Included dependency on ca-certificates
- Cosmetic indentation changes to the .spec file.

* Tue Feb  5 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-2
- python3-tornado BR and run all unittests on python3

* Mon Feb 04 2013 Toshio Kuratomi <toshio@fedoraproject.org> 1.5-1
- Initial fedora build.

