# Knot Resolver Installation Guide

[![GitHub release](https://img.shields.io/github/release/yb-infinity/knot-resolver-amzn2023.svg)](https://github.com/yb-infinity/knot-resolver-amzn2023/releases)
[![Download](https://img.shields.io/github/downloads/yb-infinity/knot-resolver-amzn2023/total.svg)](https://github.com/yb-infinity/knot-resolver-amzn2023/releases)

## Installation Options

Choose the installation method that works best for you:

1. **[From Repository](#installation-from-repository)** - Recommended for production
2. **[From GitHub Releases](#installation-from-github-releases)** - Pre-built packages
3. **[Building from Source](#building-from-source)** - Latest development version

## Installation from Repository

### 1. Add the Repository

Create the repository configuration file:

```bash
sudo tee /etc/yum.repos.d/fury.repo << EOF
[fury]
name=Gemfury Repository
baseurl=https://yum.fury.io/drakemazzy/
enabled=1
gpgcheck=0
priority=1
EOF
```

### 2. Install Knot Resolver

```bash
# Update package cache
sudo dnf makecache

# Install Knot Resolver
sudo dnf install -y knot-resolver
```

### 3. Configure and Start the Service

```bash
# Enable and start the service
sudo systemctl enable --now kresd@1.service

# Check service status
sudo systemctl status kresd@1.service

# View logs
sudo journalctl -u kresd@1.service -f
```

### 4. Verify Installation

```bash
# Check if the resolver is responding
dig @127.0.0.1 example.com

# Test DNSSEC validation
dig @127.0.0.1 +dnssec example.com

# Check resolver configuration
sudo kresd -h
```

## Installation from GitHub Releases

Download pre-built RPM packages from GitHub releases:

```bash
# Download the latest release (replace VERSION with actual version)
wget https://github.com/yb-infinity/knot-resolver-amzn2023/releases/download/v5.7.6/knot-resolver-5.7.6-*.rpm

# Install dependencies
sudo dnf install -y knot-libs luajit libuv gnutls lmdb jemalloc systemd-libs libcap-ng libedit libnghttp2

# Install the downloaded package
sudo dnf install -y ./knot-resolver-*.rpm
```

## Installation from Local RPM

If you have built the RPM locally or downloaded from releases:

```bash
# Install dependencies
sudo dnf install -y knot-libs luajit libuv gnutls lmdb jemalloc systemd-libs libcap-ng libedit libnghttp2

# Install the RPM package
sudo dnf install -y ./rpmbuild-output/RPMS/x86_64/knot-resolver-*.rpm
```

## Building from Source

To build the RPM package yourself:

```bash
# Clone the repository
git clone https://github.com/yb-infinity/knot-resolver-amzn2023.git
cd knot-resolver-amzn2023

# Build using Docker (recommended)
docker build -t knot-resolver-build -f Dockerfile.build .
docker run --rm -v $(pwd)/rpmbuild-output:/workspace/rpmbuild-output knot-resolver-build

# Install the built package
sudo dnf install -y ./rpmbuild-output/RPMS/x86_64/knot-resolver-*.rpm
```

## Configuration

### Basic Configuration

The default configuration file is located at `/etc/knot-resolver/kresd.conf`:

```lua
-- Basic configuration for Knot Resolver
net.listen('127.0.0.1', 53, { kind = 'dns' })
net.listen('::1', 53, { kind = 'dns' })

-- Enable DNSSEC validation
trust_anchors.add_file('/var/lib/knot-resolver/root.keys')

-- Set cache size (default: 100 MB)
cache.size = 100 * MB
```

### DNS-over-TLS Configuration

To enable DNS-over-TLS:

```lua
-- Enable TLS on port 853
net.listen('127.0.0.1', 853, { kind = 'tls' })
net.listen('::1', 853, { kind = 'tls' })

-- Configure TLS certificate (for local testing)
net.tls("/path/to/server.crt", "/path/to/server.key")
```

### Multiple Instances

To run multiple resolver instances:

```bash
# Enable multiple instances
sudo systemctl enable kresd@1.service kresd@2.service kresd@3.service

# Start all instances via target
sudo systemctl start kresd.target
```

## Monitoring and Maintenance

### Log Files

```bash
# View resolver logs
sudo journalctl -u kresd@1.service

# View real-time logs
sudo journalctl -u kresd@1.service -f

# View logs with timestamp
sudo journalctl -u kresd@1.service --since today
```

### Cache Management

```bash
# Check cache statistics (requires HTTP module)
# Add to kresd.conf: modules = {'http'}
curl http://localhost:8053/stats

# Clear cache (restart service)
sudo systemctl restart kresd@1.service
```

### Performance Tuning

For high-load environments:

```lua
-- Increase cache size
cache.size = 1 * GB

-- Enable more worker processes
net.listen('127.0.0.1', 53, { kind = 'dns', freebind = true })

-- Configure memory allocator
jit.opt.start("minstitch=0", "maxmcode=8192")
```

## Troubleshooting

### Common Issues

1. **Service fails to start**:
   ```bash
   sudo systemctl status kresd@1.service
   sudo journalctl -u kresd@1.service
   ```

2. **Permission denied errors**:
   ```bash
   # Check file permissions
   ls -la /etc/knot-resolver/
   ls -la /var/lib/knot-resolver/

   # Fix permissions if needed
   sudo chown -R knot-resolver:knot-resolver /var/lib/knot-resolver/
   ```

3. **DNSSEC validation issues**:
   ```bash
   # Check trust anchors
   sudo ls -la /var/lib/knot-resolver/root.keys

   # Test DNSSEC validation
   dig @127.0.0.1 +dnssec +cd example.com
   ```

### Getting Help

- [Knot Resolver Documentation](https://knot-resolver.readthedocs.io/)
- [GitHub Issues](https://github.com/yb-infinity/knot-resolver-amzn2023/issues)
- [Community Support](https://github.com/yb-infinity/knot-resolver-amzn2023/discussions)

## Package Information

- **Package Name**: knot-resolver
- **Version**: 5.7.6
- **Architecture**: x86_64, ARM64
- **Dependencies**: Automatically handled by DNF/YUM
- **Target OS**: Amazon Linux 2023

## Amazon Linux 2023 Notes

### Service Management
- Use systemd for service management
- Multiple instances supported via kresd@N.service
- Automatic startup on boot when enabled

### Security
- Runs as dedicated knot-resolver user
- SELinux compatible
- Secure defaults for DNS resolution
