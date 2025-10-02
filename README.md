# Knot Resolver RPM Packages for Amazon Linux 2023

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Knot Resolver Version](https://img.shields.io/badge/Knot%20Resolver-5.7.6-green.svg)](https://www.knot-resolver.cz/)
[![Amazon Linux 2023](https://img.shields.io/badge/Amazon%20Linux-2023-orange.svg)](https://docs.aws.amazon.com/linux/al2023/ug/what-is-amazon-linux.html)

This repository contains scripts and configuration files to build Knot Resolver RPM packages for Amazon Linux 2023.

## Quick Links

- [Releases](https://github.com/yb-infinity/knot-resolver-amzn2023/releases) - Download pre-built RPM packages
- [Installation Guide](INSTALL.md) - Step-by-step installation instructions
- [Issues](https://github.com/yb-infinity/knot-resolver-amzn2023/issues) - Report bugs or request features
- [Discussions](https://github.com/yb-infinity/knot-resolver-amzn2023/discussions) - Community support and questions
- [Changelog](CHANGELOG.md) - See what's new

## Overview

Knot Resolver is a DNSSEC-enabled caching full resolver implementation written in C and LuaJIT. This project provides:

- RPM spec file for Knot Resolver
- Build script for Amazon Linux 2023
- GitHub Actions workflow for automated building
- Support for both x86_64 and ARM64 architectures

## Features

- Latest Knot Resolver: Builds the latest stable version (5.7.6)
- Amazon Linux 2023: Optimized for Amazon Linux 2023
- Multi-architecture: Supports both x86_64 and ARM64
- DNSSEC Validation: Full DNSSEC support with automatic trust anchor management
- DNS-over-TLS: Secure DNS resolution support
- Modular Architecture: Includes various resolver modules
- Systemd Integration: Native systemd service support
- Automated CI/CD: GitHub Actions workflow for continuous building
- Package Repository: Automatic upload to Gemfury repository

## Quick Start

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

```bash
# Quick installation from repository
sudo tee /etc/yum.repos.d/fury.repo << EOF
[fury]
name=Gemfury Repository
baseurl=https://yum.fury.io/drakemazzy/
enabled=1
gpgcheck=0
priority=1
EOF

sudo dnf makecache && sudo dnf install -y knot-resolver
sudo systemctl enable --now kresd@1.service
```

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Support

- Knot Resolver Documentation: [https://knot-resolver.readthedocs.io/](https://knot-resolver.readthedocs.io/)
- Official Website: [https://www.knot-resolver.cz/](https://www.knot-resolver.cz/)
