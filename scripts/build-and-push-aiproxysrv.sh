#!/bin/bash

# Build and push aiproxysrv images to GitHub Container Registry
# Usage: ./build-and-push-aiproxysrv.sh [VERSION] [--force]
# Example: ./build-and-push-aiproxysrv.sh v2.1.5
# Example with force: ./build-and-push-aiproxysrv.sh v2.1.5 --force

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="ghcr.io/rwellinger"
APP_IMAGE="aiproxysrv-app"
WORKER_IMAGE="celery-worker-app"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/aiproxysrv"
FORCE_PUSH=false

# Print functions
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Parse arguments
parse_arguments() {
    VERSION=""
    for arg in "$@"; do
        if [ "$arg" = "--force" ]; then
            FORCE_PUSH=true
        elif [ -z "$VERSION" ]; then
            VERSION="$arg"
        fi
    done
}

# Get version
get_version() {
    if [ -z "$VERSION" ]; then
        if [ -f "$BUILD_DIR/VERSION" ]; then
            VERSION=$(cat "$BUILD_DIR/VERSION" | tr -d '[:space:]')
            print_info "Using version from VERSION file: $VERSION"
        else
            print_error "No version specified and no VERSION file found."
            print_info "Usage: $0 [VERSION] [--force]"
            print_info "Example: $0 v2.1.5"
            exit 1
        fi
    fi
}

# Check if image tag exists in registry
check_image_exists() {
    local image=$1
    if docker manifest inspect "$image" > /dev/null 2>&1; then
        return 0  # exists
    else
        return 1  # does not exist
    fi
}

# Confirm overwrite if image exists
confirm_overwrite() {
    local image=$1

    if [ "$FORCE_PUSH" = true ]; then
        return 0  # skip confirmation
    fi

    if check_image_exists "$image"; then
        print_warning "Image $image already exists!"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Aborted by user"
            exit 1
        fi
    fi
}

# Build images
build_images() {
    print_header "Building Images"

    cd "$BUILD_DIR"

    print_info "Building $APP_IMAGE..."
    docker build -f dockerfile --target app -t "$APP_IMAGE:local" -t "$APP_IMAGE:$VERSION" -t "$REGISTRY/$APP_IMAGE:$VERSION" -t "$REGISTRY/$APP_IMAGE:latest" .
    print_success "$APP_IMAGE built successfully"

    print_info "Building $WORKER_IMAGE..."
    docker build -f dockerfile --target worker -t "$WORKER_IMAGE:local" -t "$WORKER_IMAGE:$VERSION" -t "$REGISTRY/$WORKER_IMAGE:$VERSION" -t "$REGISTRY/$WORKER_IMAGE:latest" .
    print_success "$WORKER_IMAGE built successfully"
}

# Push images
push_images() {
    print_header "Pushing Images to GitHub Container Registry"

    # Check APP_IMAGE version tag
    confirm_overwrite "$REGISTRY/$APP_IMAGE:$VERSION"
    print_info "Pushing $APP_IMAGE:$VERSION..."
    docker push "$REGISTRY/$APP_IMAGE:$VERSION"
    print_success "$APP_IMAGE:$VERSION pushed"

    # latest tag is always pushed without confirmation
    print_info "Pushing $APP_IMAGE:latest..."
    docker push "$REGISTRY/$APP_IMAGE:latest"
    print_success "$APP_IMAGE:latest pushed"

    # Check WORKER_IMAGE version tag
    confirm_overwrite "$REGISTRY/$WORKER_IMAGE:$VERSION"
    print_info "Pushing $WORKER_IMAGE:$VERSION..."
    docker push "$REGISTRY/$WORKER_IMAGE:$VERSION"
    print_success "$WORKER_IMAGE:$VERSION pushed"

    # latest tag is always pushed without confirmation
    print_info "Pushing $WORKER_IMAGE:latest..."
    docker push "$REGISTRY/$WORKER_IMAGE:latest"
    print_success "$WORKER_IMAGE:latest pushed"
}

# Summary
print_summary() {
    print_header "Summary"
    echo "Successfully built and pushed:"
    echo -e "  ${GREEN}•${NC} $REGISTRY/$APP_IMAGE:$VERSION"
    echo -e "  ${GREEN}•${NC} $REGISTRY/$APP_IMAGE:latest"
    echo -e "  ${GREEN}•${NC} $REGISTRY/$WORKER_IMAGE:$VERSION"
    echo -e "  ${GREEN}•${NC} $REGISTRY/$WORKER_IMAGE:latest"
    echo ""
    print_info "You can now use these images in your docker-compose.yml"
    echo ""
}

# Main execution
main() {
    print_header "AI Proxy Service - Build & Push"

    parse_arguments "$@"
    get_version

    print_info "Version: $VERSION"
    print_info "Build directory: $BUILD_DIR"
    if [ "$FORCE_PUSH" = true ]; then
        print_warning "Force mode enabled - will overwrite existing tags"
    fi

    check_docker
    build_images
    push_images
    print_summary
}

# Run main function
main "$@"
