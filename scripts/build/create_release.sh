#!/bin/bash

# Create a new release with version tagging
# Usage: ./create_release.sh
# Note: Reads version from scripts/VERSION file (created by setVersion.sh)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if VERSION file exists
VERSION_FILE="$SCRIPT_DIR/VERSION"
if [ ! -f "$VERSION_FILE" ]; then
    print_error "VERSION File nicht gefunden: $VERSION_FILE"
    echo ""
    echo "Bitte zuerst Version setzen:"
    echo "  ${YELLOW}cd $SCRIPT_DIR${NC}"
    echo "  ${YELLOW}./setVersion.sh <VERSION>${NC}"
    echo ""
    echo "Beispiel:"
    echo "  ${YELLOW}./setVersion.sh 2.2.3${NC}"
    echo ""
    exit 1
fi

# Read version from file
VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')

# Validate version format (vX.Y.Z)
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Ungültiges Versionsformat in $VERSION_FILE: $VERSION"
    print_error "Erwarte Format: vX.Y.Z (z.B. v2.1.6)"
    exit 1
fi

print_header "Release ${VERSION} erstellen"

cd "$PROJECT_DIR"

git fetch

# ──────────────────────────────────────
# 1. Prüfe, ob der Arbeitsbaum sauber ist
# ──────────────────────────────────────
print_info "Prüfe Git Status..."
if ! git diff-index --quiet HEAD --; then
    print_error "Der Arbeitsbaum enthält nicht committete Änderungen."
    exit 1
fi
print_success "Arbeitsbaum ist sauber"

# ──────────────────────────────────────
# 2. Prüfe, ob noch unpushed Commits existieren
# ──────────────────────────────────────
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
    if git rev-list @{u}..HEAD | grep -q .; then
        print_error "Es gibt lokale Commits, die noch nicht gepusht wurden."
        exit 1
    fi
    print_success "Alle Commits sind gepusht"
else
    print_warning "Kein Upstream Remote gesetzt – Push Check übersprungen"
fi

# ──────────────────────────────────────
# 3. Prüfen, ob Tag schon existiert
# ──────────────────────────────────────
print_info "Prüfe ob Tag ${VERSION} bereits existiert..."
if git show-ref --verify --quiet "refs/tags/${VERSION}"; then
    print_error "Tag ${VERSION} existiert bereits (lokal)."
    exit 1
fi
if git ls-remote --tags origin | grep -q "refs/tags/${VERSION}\$"; then
    print_error "Tag ${VERSION} existiert bereits (remote)."
    exit 1
fi
print_success "Tag ${VERSION} ist verfügbar"

# ──────────────────────────────────────
# 4. VERSION Files aktualisieren
# ──────────────────────────────────────
print_info "Aktualisiere VERSION Files..."

echo "${VERSION}" > "$PROJECT_DIR/aiproxysrv/VERSION"
print_success "aiproxysrv/VERSION → ${VERSION}"

echo "${VERSION}" > "$PROJECT_DIR/aiwebui/VERSION"
print_success "aiwebui/VERSION → ${VERSION}"

# ──────────────────────────────────────
# 5. Änderungen committen
# ──────────────────────────────────────
print_info "Committe VERSION Updates..."
git add aiproxysrv/VERSION aiwebui/VERSION
git commit -m "Bump version to ${VERSION}"
print_success "VERSION Files committed"

# ──────────────────────────────────────
# 6. Git Tag erstellen und pushen
# ──────────────────────────────────────
print_info "Erstelle Git Tag ${VERSION}..."
git tag ${VERSION} -m "Release ${VERSION}"
print_success "Tag ${VERSION} erstellt"

print_info "Pushe Commit und Tag..."
git push origin main
git push origin ${VERSION}
print_success "Tag und Commit gepusht"

# ──────────────────────────────────────────────────────────
# 8. Drone CI Information
# ──────────────────────────────────────────────────────────
print_header "Drone CI Build"
print_info "Drone CI wird automatisch den Build starten..."
echo ""
echo "  🔗 Build Status: ${BLUE}http://10.0.1.120:8080/rwellinger/thwelly_ai_tools${NC}"
echo ""
print_info "Drone CI wird folgende Images bauen und pushen:"
echo "  • ghcr.io/rwellinger/aiproxysrv-app:${VERSION}"
echo "  • ghcr.io/rwellinger/celery-worker-app:${VERSION}"
echo "  • ghcr.io/rwellinger/aiwebui-app:${VERSION}"
echo ""
print_warning "Manuelle Builds sind weiterhin möglich:"
echo "  ./scripts/build/build-and-push-aiproxysrv.sh ${VERSION}"
echo "  ./scripts/build/build-and-push-aiwebui.sh ${VERSION}"
echo ""
