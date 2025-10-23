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

echo "Downloading Montserrat-Bold.ttf..."
curl -L -o Montserrat-Bold.ttf \
  "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"

echo "Downloading Roboto-Black.ttf..."
curl -L -o Roboto-Black.ttf \
  "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf"

echo "Downloading PlayfairDisplay-Regular.ttf..."
curl -L -o PlayfairDisplay-Regular.ttf \
  "https://github.com/clauseggers/Playfair-Display/raw/master/fonts/PlayfairDisplay-Regular.ttf"

echo ""
echo "✅ Fonts installed successfully!"
echo "Location: $FONTS_DIR"
echo ""
ls -lh "$FONTS_DIR"
