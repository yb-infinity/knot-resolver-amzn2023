#!/bin/bash
set -e

# Knot Resolver Amazon Linux 2023 RPM Build Script
# This script can be used both in GitHub Actions and for local builds

# Configuration
WORKSPACE_DIR=${WORKSPACE_DIR:-$(pwd)}
FURY_REPO_URL=${FURY_REPO_URL:-"https://yum.fury.io/drakemazzy/"}
OUTPUT_DIR=${OUTPUT_DIR:-"$WORKSPACE_DIR/rpmbuild-output"}
SPEC_TEMPLATE=${SPEC_TEMPLATE:-}
SPEC_BASENAME=""
SPEC_FILE_PATH=""
KNOT_RESOLVER_VERSION=${KNOT_RESOLVER_VERSION:-"5.7.6"}

echo "[INFO] Starting Knot Resolver Amazon Linux 2023 RPM build"
echo "[INFO] Workspace: $WORKSPACE_DIR"
echo "[INFO] Output directory: $OUTPUT_DIR"

# Function to install dependencies from fury repository
install_dependencies() {
    echo "[INFO] Installing dependencies for Knot Resolver..."

    echo "[INFO] Adding Fury repository..."
    cat > /etc/yum.repos.d/fury.repo << 'EOF'
[fury]
name=Fury Repository
baseurl=https://yum.fury.io/drakemazzy/
enabled=1
gpgcheck=0
EOF
    echo "[INFO] Updating package manager..."
    dnf clean all && dnf -y update

    echo "[INFO] Installing essential build tools only (no graphics)..."
    # Install only essential build tools, avoid Development Tools group which pulls graphics
    dnf install -y \
        rpm-build rpmdevtools \
        gcc gcc-c++ cmake ninja-build \
        meson pkgconfig \
        m4 \
        libknot-devel \
        luajit-devel \
        libedit-devel \
        gnutls-devel \
        systemd-devel \
        libcap-ng-devel \
        libuv-devel \
        libnghttp2-devel \
        lmdb-devel \
        openssl-devel \
        libffi-devel \
        jemalloc-devel \
        lua-devel \
        luarocks \
        libzscanner-devel || {
        echo "[ERROR] Failed to install dependencies"
        return 1
    }

    echo "[SUCCESS] Dependencies installed successfully"
}

# Function to setup RPM build environment
setup_rpm_environment() {
    echo "[INFO] Setting up RPM build environment..."
    rpmdev-setuptree
    echo "[SUCCESS] RPM build environment set up"
}

timestamp_to_tag() {
    local timestamp="$1"
    local hex=$(printf "%x" "$timestamp")
    echo "dmz${hex}"
}

# Function to create source archive
create_source_archive() {
    echo "[INFO] Downloading and preparing Knot Resolver source archive..."

    cd "$WORKSPACE_DIR"

    # Download Knot Resolver source if not already present
    ARCHIVE="knot-resolver-${KNOT_RESOLVER_VERSION}.tar.xz"
    if [ ! -f "$ARCHIVE" ]; then
        echo "[INFO] Downloading Knot Resolver ${KNOT_RESOLVER_VERSION}..."
        wget -O "$ARCHIVE" "https://secure.nic.cz/files/knot-resolver/${ARCHIVE}" || {
            echo "[ERROR] Failed to download Knot Resolver source"; exit 1;
        }
    fi

    echo "[SUCCESS] Source archive ready: $ARCHIVE"

    # Export for later use
    export ARCHIVE
}

# Function to prepare spec file
prepare_spec_file() {
    echo "[INFO] Preparing spec file..."

    # Copy source archive to RPM SOURCES directory
    cp "$ARCHIVE" ~/rpmbuild/SOURCES/ || { echo "[ERROR] Failed to copy archive"; exit 1; }

    # Determine spec file template location
    SPEC_TEMPLATE="${SPEC_TEMPLATE:-$WORKSPACE_DIR/distro/pkg/rpm/knot-resolver.spec}"
    [ -f "$SPEC_TEMPLATE" ] || { echo "[ERROR] Spec template not found: $SPEC_TEMPLATE"; exit 1; }

    # Copy spec file to RPM SPECS directory
    SPEC_BASENAME=$(basename "$SPEC_TEMPLATE")
    SPEC_FILE_PATH="$HOME/rpmbuild/SPECS/$SPEC_BASENAME"
    cp "$SPEC_TEMPLATE" "$SPEC_FILE_PATH" || { echo "[ERROR] Failed to copy spec file"; exit 1; }

    # Determine version strings
    SOURCE_VERSION=$(echo "$KNOT_RESOLVER_VERSION" | sed 's/-.*$//')
    RPM_VERSION="$SOURCE_VERSION"

    # Generate release string with timestamp tag
    CURRENT_TIMESTAMP=$(date +%s)
    RELEASE_TAG=$(timestamp_to_tag "$CURRENT_TIMESTAMP")
    RELEASE_VALUE="${RELEASE_TAG}.amzn2023"

    echo "[INFO] Source version: $SOURCE_VERSION"
    echo "[INFO] RPM version: $RPM_VERSION"
    echo "[INFO] Release: $RELEASE_VALUE"

    # Update spec file with dynamic version and Jinja2 templates
    sed -i "s/Version:.*/Version: $RPM_VERSION/" "$SPEC_FILE_PATH"
    sed -i "s/Release:.*/Release: $RELEASE_VALUE/" "$SPEC_FILE_PATH"

    # Replace Jinja2 templates
    sed -i "s/{{ rpm_version }}/$RPM_VERSION/g" "$SPEC_FILE_PATH"
    sed -i "s/{{ release }}/$RELEASE_VALUE/g" "$SPEC_FILE_PATH"
    sed -i "s/{{ source_version }}/$SOURCE_VERSION/g" "$SPEC_FILE_PATH"

    # Fix changelog date format
    CURRENT_DATE=$(date '+%a %b %d %Y')
    sed -i "s/{{ now }}/$CURRENT_DATE/g" "$SPEC_FILE_PATH"

    # Update source URL in spec file if using downloaded source
    if [[ "$ARCHIVE" == knot-resolver-*.tar.xz ]]; then
        sed -i "s|^Source0:.*|Source0: $ARCHIVE|" "$SPEC_FILE_PATH"
    fi

    echo "[SUCCESS] Spec file prepared"
}


# Function to build RPM packages
build_rpm_packages() {
    echo "[INFO] Building Knot Resolver RPM package..."

    # Build RPM packages
    if [ -z "$SPEC_BASENAME" ]; then
        echo "[ERROR] Spec file name not set"
        exit 1
    fi

    cd ~/rpmbuild/SPECS
    rpmbuild -ba "$SPEC_BASENAME" || { echo "[ERROR] RPM build failed"; exit 1; }

    echo "[SUCCESS] Knot Resolver RPM package built successfully"
}

# Function to copy built packages and verify
copy_and_verify_packages() {
    echo "[INFO] Copying built packages to output directory..."

    # Clean and create output directories
    rm -rf "$OUTPUT_DIR/RPMS" "$OUTPUT_DIR/SRPMS"
    mkdir -p "$OUTPUT_DIR/RPMS" "$OUTPUT_DIR/SRPMS"

    # Copy packages with error checking
    [ -d ~/rpmbuild/RPMS ] && [ "$(ls -A ~/rpmbuild/RPMS 2>/dev/null)" ] || {
        echo "[ERROR] No RPMS found - build failed"; exit 1;
    }
    [ -d ~/rpmbuild/SRPMS ] && [ "$(ls -A ~/rpmbuild/SRPMS 2>/dev/null)" ] || {
        echo "[ERROR] No SRPMS found - build failed"; exit 1;
    }

    cp -r ~/rpmbuild/RPMS/* "$OUTPUT_DIR/RPMS/"
    cp ~/rpmbuild/SRPMS/* "$OUTPUT_DIR/SRPMS/"

    echo "[SUCCESS] Packages copied successfully"
    find "$OUTPUT_DIR" -name "*.rpm" -type f -exec basename {} \; | sort
}

# Function to show final results
show_results() {
    echo "[SUCCESS] Build completed successfully!"
    echo "Output directory: $OUTPUT_DIR"
    ls -la "$OUTPUT_DIR"/RPMS/aarch64/*.rpm 2>/dev/null || echo "No RPMs found"
}

# Main execution
main() {
    cd "$WORKSPACE_DIR"

    install_dependencies
    setup_rpm_environment
    create_source_archive
    prepare_spec_file
    build_rpm_packages
    copy_and_verify_packages
    show_results

    echo "[SUCCESS] Knot Resolver Amazon Linux 2023 RPM build completed!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --workspace)
            WORKSPACE_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --output-dir DIR  Set output directory (default: \$WORKSPACE/rpmbuild-output)"
            echo "  --workspace DIR   Set workspace directory (default: current directory)"
            echo "  --help            Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  FURY_REPO_URL     Fury repository URL"
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main
