# Contributing to Knot Resolver Amazon Linux 2023

Thank you for your interest in contributing to this project!

## Getting Started

1. **Fork the repository** at [https://github.com/yb-infinity/knot-resolver-amzn2023](https://github.com/yb-infinity/knot-resolver-amzn2023)
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/knot-resolver-amzn2023.git
   cd knot-resolver-amzn2023
   ```

## Development Workflow

### Local Testing

For detailed build instructions, see [INSTALL.md](INSTALL.md#building-from-source).

Quick test:
```bash
# Verify the build output after running build script
ls -la rpmbuild-output/RPMS/noarch/
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** to:
   - `scripts/build-amzn2023.sh` - Build script improvements
   - `distro/pkg/rpm/knot-resolver.spec` - RPM spec file changes
   - `.github/workflows/` - CI/CD improvements
   - Documentation files

3. **Test your changes**:
   - Run the build script locally
   - Verify RPM installation works
   - Check documentation renders correctly

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Types of Contributions

### Bug Reports
- Use [GitHub Issues](https://github.com/yb-infinity/knot-resolver-amzn2023/issues)
- Include system information and error logs
- Provide steps to reproduce

### Feature Requests
- Open a [Discussion](https://github.com/yb-infinity/knot-resolver-amzn2023/discussions)
- Explain the use case and benefits
- Consider implementation complexity

### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update installation instructions

### Code Improvements
- Build script optimizations
- RPM spec file enhancements
- CI/CD workflow improvements

## Guidelines

### Code Style
- Use clear, descriptive commit messages
- Follow shell scripting best practices
- Add comments for complex logic
- Use error handling and logging

### Testing
- Test on clean Amazon Linux 2023 environment
- Verify both x86_64 and ARM64 architectures
- Ensure backwards compatibility

### Documentation
- Update relevant documentation files
- Include examples where helpful
- Keep installation guide current

## Pull Request Process

1. **Ensure tests pass**: Build succeeds locally
2. **Update documentation**: If functionality changes
3. **Describe changes**: Clear PR description
4. **Link issues**: Reference related issues
5. **Wait for review**: Maintainer will review

## Questions?

- General Questions: [Discussions](https://github.com/yb-infinity/knot-resolver-amzn2023/discussions)
- Bug Reports: [Issues](https://github.com/yb-infinity/knot-resolver-amzn2023/issues)
- Knot Resolver Help: [Knot Resolver Documentation](https://knot-resolver.readthedocs.io/)

Thank you for contributing!
