# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.7.6] - 2025-10-01

### Added
- Initial adaptation for Knot Resolver from LuaRocks project
- RPM spec file for Knot Resolver 5.7.6
- Support for Amazon Linux 2023
- DNSSEC validation with automatic trust anchor management
- DNS-over-TLS support
- Systemd integration with kresd@.service
- Modular architecture support
- Multiple subpackages (devel, doc, module-dnstap, module-http)
- Build script optimized for Knot Resolver compilation
- GitHub Actions workflow for automated building
- Support for both x86_64 and ARM64 architectures
- HTTP API interface for monitoring
- dnstap logging support

### Changed
- Switched from LuaRocks to Knot Resolver
- Updated dependencies to match Knot Resolver requirements
- Modified build script for meson/ninja build system
- Updated documentation for DNS resolver instead of package manager

### Removed
- LuaRocks-specific configuration and dependencies
- Lua version-specific directories

[5.7.6]: https://github.com/yb-infinity/knot-resolver-amzn2023/releases/tag/v5.7.6
