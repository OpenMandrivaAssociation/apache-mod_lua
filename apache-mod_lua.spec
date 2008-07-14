#Module-Specific definitions
%define mod_name mod_lua
%define mod_conf A93_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	A module to embed lua in apache
Name:		apache-%{mod_name}
Version:	0.5
Release:	%mkrel 6
Group:		System/Servers
License:	MIT
URL:		http://sourceforge.net/projects/mod-lua/
Source0:	http://kent.dl.sourceforge.net/sourceforge/mod-lua/%{mod_name}-%{version}.tgz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	liblua-devel >= 5.1
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_lua is a content generate module for Apache2. It can run in three modes
based LUA, One is full lua script, second is lua-html mixed, another is lua
custom handle. All not need any CGI process, lighter and faster. Aimed to embed
system and thin webs.

%prep

%setup -q -n %{mod_name}

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;
		
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
pushd src
    %{_sbindir}/apxs `apr-1-config --cppflags` -Wc,-Wall -L%{_libdir} -llua -c mod_lua.c \
    apache2_lib.c lhtml_compile.c storage_dbm.c storage_shmcb.c storage_shmht.c \
    storage_util.c storage_util_mutex.c storage_util_table.c
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 src/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc bin/COPYRIGHT bin/HISTORY lib web etc/lua.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}


