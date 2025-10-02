%global _hardened_build 1
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}}

# Disable debug packages
%global debug_package %{nil}

%define GPG_CHECK 0
%define repodir %{_builddir}/%{name}-%{version}
%define NINJA ninja-build

Name:           knot-resolver
Version:        {{ rpm_version }}
Release:        {{ release }}%{?dist}
Summary:        Caching full DNS Resolver

License:        GPL-3.0-or-later
URL:            https://www.knot-resolver.cz/
Source0:        https://secure.nic.cz/files/%{name}/%{name}-{{ source_version }}.tar.xz

# LuaJIT only on these arches
ExclusiveArch:  %{arm} aarch64 %{ix86} x86_64

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson >= 0.49
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  libknot-devel >= 3.4
BuildRequires:  libzscanner-devel >= 3.4
BuildRequires:  libedit-devel
BuildRequires:  luajit-devel
BuildRequires:  libuv-devel >= 1.7
BuildRequires:  gnutls-devel
BuildRequires:  lmdb-devel
BuildRequires:  luarocks
BuildRequires:  openssl-devel
BuildRequires:  libffi-devel
BuildRequires:  jemalloc-devel

Requires(pre):  shadow-utils

Requires:       openssl-libs
Requires:       jemalloc

%description
The Knot Resolver is a DNSSEC-enabled caching full resolver implementation
written in C and LuaJIT, including both a resolver library and a daemon.
Modular architecture of the library keeps the core tiny and efficient, and
provides a state-machine like API for extensions.

This package includes a systemd service file for easy service management.
To start using it, enable and start the kresd service:
$ systemctl enable kresd.service
$ systemctl start kresd.service

%package devel
Summary:        Development headers for Knot Resolver
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The package contains development headers for Knot Resolver.

%prep
%setup -q -n %{name}-%{version}

# Create a sysusers.d config file
cat >knot-resolver.sysusers.conf <<EOF
u knot-resolver - 'Knot Resolver' %{_sysconfdir}/knot-resolver -
EOF

# Create a tmpfiles.d config file
cat >knot-resolver.tmpfiles.conf <<EOF
d %{_localstatedir}/cache/knot-resolver 0750 knot-resolver knot-resolver -
d %{_sharedstatedir}/knot-resolver 0750 knot-resolver knot-resolver -
d /run/knot-resolver 0755 knot-resolver knot-resolver -
EOF

%build
# Configure luarocks to use LuaJIT explicitly
mkdir -p %{_builddir}/lua-modules

# Create luarocks config for LuaJIT
cat > %{_builddir}/luarocks-config-luajit.lua << 'LREOF'
lua_version = "5.1"
lua_interpreter = "luajit"
variables = {
   LUA = "/usr/bin/luajit",
   LUA_INCDIR = "/usr/include/luajit-2.1",
   LUA_LIBDIR = "/usr/lib64",
   LUA_BINDIR = "/usr/bin",
}
LREOF

# Install lua dependencies using luarocks with LuaJIT config
echo "=== Installing Lua modules for LuaJIT ==="
export LUAROCKS_CONFIG=%{_builddir}/luarocks-config-luajit.lua

# Install with explicit lua-version flag
luarocks --tree %{_builddir}/lua-modules --lua-version=5.1 install lua-cjson || echo "Warning: Failed to install lua-cjson"
luarocks --tree %{_builddir}/lua-modules --lua-version=5.1 install cqueues || echo "Warning: Failed to install cqueues"
luarocks --tree %{_builddir}/lua-modules --lua-version=5.1 install basexx || echo "Warning: Failed to install basexx"
luarocks --tree %{_builddir}/lua-modules --lua-version=5.1 install http || echo "Warning: Failed to install http"

# Verify what was installed
echo "=== Verifying installed modules ==="
find %{_builddir}/lua-modules -name "*.so" -o -name "*.lua" | grep -E "(cqueues|cjson|basexx|http)"

# Build with meson
CFLAGS="%{optflags}" LDFLAGS="%{?__global_ldflags}" meson build_rpm \
 -Dsystemd_files=disabled \
 -Dclient=enabled \
 -Dunit_tests=disabled \
 -Dmanaged_ta=enabled \
 -Dkeyfile_default="%{_sharedstatedir}/knot-resolver/root.keys" \
 -Dinstall_root_keys=enabled \
 -Dinstall_kresd_conf=disabled \
 -Ddoc=disabled \
 -Ddnstap=disabled \
 -Dmalloc=jemalloc \
 --buildtype=plain \
 --prefix="%{_prefix}" \
 --sbindir="%{_sbindir}" \
 --libdir="%{_libdir}" \
 --includedir="%{_includedir}" \
 --sysconfdir="%{_sysconfdir}"

%{NINJA} -v -C build_rpm

%install
DESTDIR="${RPM_BUILD_ROOT}" %{NINJA} -v -C build_rpm install

# Create default kresd.conf configuration file
mkdir -p %{buildroot}%{_sysconfdir}/knot-resolver
cat > %{buildroot}%{_sysconfdir}/knot-resolver/kresd.conf << 'EOF'
-- Load modules
modules.load('stats')
modules.load('http')

-- HTTP module configuration for metrics
http.config({ tls = false })

-- Listen for web management/metrics on port 8053
net.listen('0.0.0.0', 8053, { kind = 'webmgmt' })

-- Disable IPv6
net.ipv6 = false

-- DNS listeners
net.listen('0.0.0.0', 53, { kind = 'dns' })

-- Cache configuration
cache.open( 100 * MB, 'lmdb:///var/lib/knot-resolver/cache')
EOF

# Install lua modules from the build tree
mkdir -p %{buildroot}%{_datadir}/luajit-2.1.0-beta3
mkdir -p %{buildroot}%{_libdir}/luajit-2.1.0-beta3

# Copy lua modules from the build tree to LuaJIT paths
echo "=== DEBUG: Checking lua-modules directory ==="
ls -la %{_builddir}/lua-modules/ || echo "lua-modules directory not found"

# Copy Lua source files (share) to LuaJIT path
if [ -d "%{_builddir}/lua-modules/share/lua" ]; then
    echo "=== DEBUG: Copying share/lua files to LuaJIT path ==="
    find %{_builddir}/lua-modules/share/lua/ -name "*.lua" | head -10
    # Find the lua version directory and copy to LuaJIT path
    for lua_ver_dir in %{_builddir}/lua-modules/share/lua/*; do
        if [ -d "$lua_ver_dir" ]; then
            echo "=== DEBUG: Found lua version directory: $lua_ver_dir ==="
            cp -r "$lua_ver_dir"/* %{buildroot}%{_datadir}/luajit-2.1.0-beta3/ 2>/dev/null || true
        fi
    done
fi

# Copy binary modules (lib) - This is the critical part for cqueues!
if [ -d "%{_builddir}/lua-modules/lib" ]; then
    echo "=== DEBUG: Contents of lua-modules/lib ==="
    find %{_builddir}/lua-modules/lib -name "*.so" -o -name "_cqueues.so" | head -10

    # Copy all .so files from luarocks structure to LuaJIT path
    if [ -d "%{_builddir}/lua-modules/lib/luarocks" ]; then
        echo "=== DEBUG: Found luarocks structure, copying .so files to LuaJIT path ==="
        find %{_builddir}/lua-modules/lib/luarocks -name "*.so" -exec cp {} %{buildroot}%{_libdir}/luajit-2.1.0-beta3/ \; 2>/dev/null || true
        echo "=== DEBUG: Copied .so files, checking LuaJIT destination ==="
        ls -la %{buildroot}%{_libdir}/luajit-2.1.0-beta3/
    fi

    # Also try direct lib/lua structure if it exists
    for lua_lib_dir in %{_builddir}/lua-modules/lib/lua/*; do
        if [ -d "$lua_lib_dir" ]; then
            echo "=== DEBUG: Found lua lib directory: $lua_lib_dir, copying to LuaJIT ==="
            cp -r "$lua_lib_dir"/* %{buildroot}%{_libdir}/luajit-2.1.0-beta3/ 2>/dev/null || true
        fi
    done
fi

# remove modules with missing dependencies
rm -f %{buildroot}%{_libdir}/knot-resolver/kres_modules/etcd.lua
rm -f %{buildroot}%{_libdir}/knot-resolver/kres_modules/dnstap.so
rm -f %{buildroot}%{_libdir}/knot-resolver/debug_opensslkeylog.so
rm -f %{buildroot}%{_libdir}/knot-resolver/kres_modules/experimental_dot_auth.lua

# remove doc files to avoid issues with missing doc dependencies
rm -rf %{buildroot}%{_datadir}/doc
rm -rf %{buildroot}%{_datadir}/info

# install sysusers config
install -m0644 -D knot-resolver.sysusers.conf %{buildroot}%{_sysusersdir}/knot-resolver.conf

# install tmpfiles config
install -m0644 -D knot-resolver.tmpfiles.conf %{buildroot}%{_tmpfilesdir}/knot-resolver.conf

# Create systemd service file for kresd
install -m 0755 -d %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/kresd.service << 'EOF'
[Unit]
Description=Knot Resolver daemon
Documentation=https://www.knot-resolver.cz/documentation/
After=network.target

[Service]
Environment="LUA_PATH=/usr/share/luajit-2.1.0-beta3/?.lua;/usr/share/luajit-2.1.0-beta3/?/init.lua;;"
Environment="LUA_CPATH=/usr/lib64/luajit-2.1.0-beta3/?.so;;"
Type=simple
User=knot-resolver
Group=knot-resolver
WorkingDirectory=/var/lib/knot-resolver
ExecStart=/usr/sbin/kresd -n -c /etc/knot-resolver/kresd.conf
Restart=on-failure
RestartSec=5
StartLimitBurst=0
RuntimeDirectory=knot-resolver
RuntimeDirectoryMode=0750
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

%pre
# Create knot-resolver user through sysusers.d
%sysusers_create_package knot-resolver knot-resolver.sysusers.conf

# Fallback: create user/group manually if sysusers didn't work
getent group knot-resolver >/dev/null || groupadd -r knot-resolver
getent passwd knot-resolver >/dev/null || \
    useradd -r -g knot-resolver -d %{_sysconfdir}/knot-resolver -s /sbin/nologin \
    -c "Knot Resolver" knot-resolver


%post
# Create temporary files and directories
%tmpfiles_create %{_tmpfilesdir}/knot-resolver.conf
/sbin/ldconfig

%preun
# Stop and disable the service before removal
if [ $1 -eq 0 ]; then
    # Package is being removed (not upgraded)
    systemctl stop kresd.service >/dev/null 2>&1 || true
    systemctl disable kresd.service >/dev/null 2>&1 || true
fi

%postun
/sbin/ldconfig

# Clean up after package removal
if [ $1 -eq 0 ]; then
    # Package is being removed (not upgraded)

    # Remove service file if it exists
    if [ -f %{_unitdir}/kresd.service ]; then
        rm -f %{_unitdir}/kresd.service
    fi

    # Remove data directory and all its contents
    if [ -d /var/lib/knot-resolver ]; then
        rm -rf /var/lib/knot-resolver
    fi

    # Remove cache directory if it exists
    if [ -d /var/cache/knot-resolver ]; then
        rm -rf /var/cache/knot-resolver
    fi

    # Remove runtime directory if it exists
    if [ -d /run/knot-resolver ]; then
        rm -rf /run/knot-resolver
    fi

    # Reload systemd daemon to remove the service from systemctl
    systemctl daemon-reload >/dev/null 2>&1 || true
fi

%files
%dir %{_sysconfdir}/knot-resolver
%config(noreplace) %{_sysconfdir}/knot-resolver/kresd.conf
%config(noreplace) %{_sysconfdir}/knot-resolver/root.hints
%{_sysconfdir}/knot-resolver/icann-ca.pem
%attr(750,knot-resolver,knot-resolver) %dir %{_sharedstatedir}/knot-resolver
%attr(640,knot-resolver,knot-resolver) %{_sharedstatedir}/knot-resolver/root.keys
%{_tmpfilesdir}/knot-resolver.conf
%{_sysusersdir}/knot-resolver.conf
%{_unitdir}/kresd.service
%ghost /run/%{name}
%ghost %{_localstatedir}/cache/%{name}
%attr(750,knot-resolver,knot-resolver) %dir %{_libdir}/%{name}
%{_sbindir}/kresd
%{_sbindir}/kresc
%{_sbindir}/kres-cache-gc
%{_libdir}/libkres.so.*
%{_libdir}/knot-resolver/*.so
%{_libdir}/knot-resolver/*.lua
%dir %{_libdir}/knot-resolver/kres_modules
%{_libdir}/knot-resolver/kres_modules/bogus_log.so
%{_libdir}/knot-resolver/kres_modules/edns_keepalive.so
%{_libdir}/knot-resolver/kres_modules/extended_error.so
%{_libdir}/knot-resolver/kres_modules/hints.so
%{_libdir}/knot-resolver/kres_modules/nsid.so
%{_libdir}/knot-resolver/kres_modules/refuse_nord.so
%{_libdir}/knot-resolver/kres_modules/stats.so
%{_libdir}/knot-resolver/kres_modules/daf
%{_libdir}/knot-resolver/kres_modules/daf.lua
%{_libdir}/knot-resolver/kres_modules/detect_time_jump.lua
%{_libdir}/knot-resolver/kres_modules/detect_time_skew.lua
%{_libdir}/knot-resolver/kres_modules/dns64.lua
%{_libdir}/knot-resolver/kres_modules/graphite.lua
%{_libdir}/knot-resolver/kres_modules/http
%{_libdir}/knot-resolver/kres_modules/http*.lua
%{_libdir}/knot-resolver/kres_modules/policy.lua
%{_libdir}/knot-resolver/kres_modules/predict.lua
%{_libdir}/knot-resolver/kres_modules/prefill.lua
%{_libdir}/knot-resolver/kres_modules/priming.lua
%{_libdir}/knot-resolver/kres_modules/prometheus.lua
%{_libdir}/knot-resolver/kres_modules/rebinding.lua
%{_libdir}/knot-resolver/kres_modules/renumber.lua
%{_libdir}/knot-resolver/kres_modules/serve_stale.lua
%{_libdir}/knot-resolver/kres_modules/ta_sentinel.lua
%{_libdir}/knot-resolver/kres_modules/ta_signal_query.lua
%{_libdir}/knot-resolver/kres_modules/ta_update.lua
%{_libdir}/knot-resolver/kres_modules/view.lua
%{_libdir}/knot-resolver/kres_modules/watchdog.lua
%{_libdir}/knot-resolver/kres_modules/workarounds.lua
%{_mandir}/man8/kresd.8.gz
%{_sysusersdir}/knot-resolver.conf
# Lua modules installed via luarocks for LuaJIT
%{_datadir}/luajit-2.1.0-beta3/*
%{_libdir}/luajit-2.1.0-beta3/*

%files devel
%{_includedir}/libkres
%{_libdir}/pkgconfig/libkres.pc
%{_libdir}/libkres.so

%changelog
* {{ now }} DrakeMazzy <drake@mazzy.rv.ua> - {{ rpm_version }}-{{ release }}
- Initial build of Knot Resolver {{ source_version }} for Amazon Linux 2023
- Based on Fedora knot-resolver package
- Added custom systemd service file (kresd.service) for easy service management
- Added luarocks from fury repo for lua package management
- Fixed Lua dependencies (lua-cjson, cqueues, basexx) installation for LuaJIT compatibility
- Created explicit LuaJIT configuration for luarocks to prevent Lua 5.4 conflicts
- Added --lua-version=5.1 flag and LUAROCKS_CONFIG for proper LuaJIT targeting
- Configured LuaJIT paths instead of Lua 5.4 for proper knot-resolver operation
- Fixed ABI compatibility issues between LuaJIT and Lua 5.4
- Updated systemd service environment to use LuaJIT paths
- Added verification step for installed Lua modules
- Included HTTP and Prometheus modules
- Configured for standalone deployment with custom service configuration
