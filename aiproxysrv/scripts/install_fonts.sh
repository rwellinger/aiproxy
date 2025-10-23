#!/bin/bash
# Install Google Fonts for Text Overlay Feature
# License: All fonts are Open Source (OFL or Apache 2.0)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FONTS_DIR="$PROJECT_ROOT/fonts"

echo "Creating fonts directory..."
mkdir -p "$FONTS_DIR"
cd "$FONTS_DIR"

echo "Downloading Anton-Regular.ttf (Bold - Heavy Display)..."
curl -L -o Anton-Regular.ttf \
  "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"

echo "Downloading Inter-Regular.ttf (Modern - Clean Sans)..."
curl -L -o Inter-Regular.ttf \
  "https://github.com/shadcn-ui/taxonomy/raw/main/assets/fonts/Inter-Regular.ttf"

echo "Downloading PlayfairDisplay-Regular.ttf (Elegant - Serif)..."
curl -L -o PlayfairDisplay-Regular.ttf \
  "https://raw.githubusercontent.com/technext/cozastore/master/fonts/PlayfairDisplay/PlayfairDisplay-Regular.ttf"

echo "Downloading Roboto-Light.ttf (Light - Thin Sans)..."
curl -L -o Roboto-Light.ttf \
  "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Light.ttf"

echo ""
echo "✅ Fonts installed successfully!"
echo "Location: $FONTS_DIR"
echo ""
ls -lh "$FONTS_DIR"
