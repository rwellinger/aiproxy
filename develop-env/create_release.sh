#!/bin/bash

VERSION="v2.1.5"

git fetch

# ──────────────────────────────────────
# 1. Prüfe, ob der Arbeitsbaum sauber ist
#    (keine nicht gestagten, nicht committeten Änderungen)
# ──────────────────────────────────────
if ! git diff-index --quiet HEAD --; then
    echo "❌  Der Arbeitsbaum enthält nicht committete Änderungen." >&2
    exit 1
fi

# ──────────────────────────────────────
# 2. Prüfe, ob noch unpushed‑Commits existieren
#    (nur relevant, wenn ein Upstream‑Remote gesetzt ist)
# ──────────────────────────────────────
# 2a. Existiert ein Upstream‑Remote?
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
    # 2b. Gibt es Commits, die noch nicht gepusht wurden?
    if git rev-list @{u}..HEAD | grep -q .; then
        echo "❌  Es gibt lokale Commits, die noch nicht gepusht wurden." >&2
        exit 1
    fi
else
    echo "⚠️  Kein Upstream‑Remote gesetzt – Push‑Check übersprungen."
fi

# ──────────────────────────────────────
# 3. Version prüfen (vorheriges Beispiel einfügen)
# ──────────────────────────────────────

# 3a. Prüfen, ob Tag schon existiert
if git show-ref --verify --quiet "refs/tags/${VERSION}"; then
    echo "❌  Tag ${VERSION} existiert bereits (lokal)." >&2
    exit 1
fi
if git ls-remote --tags origin | grep -q "refs/tags/${VERSION}\$"; then
    echo "❌  Tag ${VERSION} existiert bereits (remote)." >&2
    exit 1
fi
git tag ${VERSION} -m "New Release"
git push origin ${VERSION}
