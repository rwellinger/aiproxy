#!/bin/bash

# Create a new release with version tagging
# Usage: ./create_release.sh <VERSION>
# Example: ./create_release.sh v2.1.6

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

# Check arguments
if [ -z "$1" ]; then
    print_error "Keine Version angegeben"
    echo "Usage: $0 <VERSION>"
    echo "Example: $0 v2.1.6"
    exit 1
fi

VERSION="$1"

# Validate version format (vX.Y.Z)
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Ungültiges Versionsformat. Erwarte Format: vX.Y.Z (z.B. v2.1.6)"
    exit 1
fi

print_header "Release ${VERSION} erstellen"

# Get project root directory
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
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

# ──────────────────────────────────────
# 7. Summary
# ──────────────────────────────────────
print_header "Release ${VERSION} erfolgreich erstellt"
echo "Nächste Schritte:"
echo ""
echo "  1. Build aiproxysrv:"
echo -e "     ${BLUE}./scripts/build/build-and-push-aiproxysrv.sh${NC}"
echo ""
echo "  2. Build aiwebui:"
echo -e "     ${BLUE}./scripts/build/build-and-push-aiwebui.sh${NC}"
echo ""
print_info "Die Scripts lesen automatisch die VERSION Files"
