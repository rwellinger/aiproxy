#!/bin/bash
echo "🎵 === MUSIC PRODUCTION MODE ==="
echo ""

# Check sudo access (will prompt for password if needed)
echo "Checking sudo access..."
if ! sudo -v; then
    echo "❌ Sudo access required. Exiting."
    exit 1
fi
echo ""

# 1. Stop Development
echo "[1/6] Stopping development services..."
colima stop 2>/dev/null
pkill -f "PyCharm"
pkill -f "python"
pkill -f "node"
echo "✅ Development stopped"

# 2. Disable macOS Background
echo "[2/6] Disabling macOS background processes..."
sudo mdutil -a -i off
sudo tmutil disable
echo "✅ Spotlight & Time Machine disabled"

# 3. Network (optional - comment out if you need internet)
# echo "[3/6] Disabling WiFi/Bluetooth..."
# networksetup -setairportpower en0 off
# blueutil -p 0 2>/dev/null
# echo "✅ Network disabled"

# 4. Kill unnecessary apps
echo "[4/6] Closing unnecessary apps..."
pkill -f "Slack"
pkill -f "Mail"
pkill -f "Messages"
echo "✅ Apps closed"

# 5. Audio optimization
echo "[5/6] Optimizing Core Audio..."
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.audio.coreaudiod.plist 2>/dev/null
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.audio.coreaudiod.plist
echo "✅ Core Audio restarted"

# 6. Show stats
echo "[6/6] System status:"
echo "  Free RAM: $(vm_stat | perl -ne '/page free count[^0-9]+([0-9]+)/ and printf("%.2f GB\n", $1 * 4096 / 1073741824);')"
echo "  CPU Temp: $(osx-cpu-temp 2>/dev/null || echo 'N/A (install: brew install osx-cpu-temp)')"
echo ""
echo "🎹 READY FOR PRODUCTION!"
echo "⚠️  Don't forget:"
echo "   - Close browser tabs"
echo "   - Set DAW buffer size to 128 samples"
echo "   - Disable WiFi if recording (networksetup -setairportpower en0 off)"
echo ""
echo "Run './scripts/operation/dev_mode.sh' to restore settings."
