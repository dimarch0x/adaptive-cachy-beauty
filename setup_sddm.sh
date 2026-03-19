#!/bin/bash

# Adaptive Cachy Beauty - SDDM Setup Script
# This script performs the one-time root actions needed for seamless SDDM integration.

set -e

THEME_NAME="AdaptiveCachy"
SDDM_THEME_DIR="/usr/share/sddm/themes/$THEME_NAME"
CONFIG_DIR="/var/lib/adaptive-cachy"
CURRENT_USER=$(logname || echo $USER)

echo "🚀 Starting SDDM Integration Setup..."

# 1. Create the global config directory
echo "📁 Creating configuration directory: $CONFIG_DIR"
sudo mkdir -p "$CONFIG_DIR"
sudo chown "$CURRENT_USER:$CURRENT_USER" "$CONFIG_DIR"
sudo chmod 755 "$CONFIG_DIR"

# 2. Copy the SDDM theme to the system directory
echo "🎨 Installing SDDM theme to $SDDM_THEME_DIR"
sudo mkdir -p "$SDDM_THEME_DIR"
sudo cp -r src/integrations/sddm_theme/* "$SDDM_THEME_DIR/"

# 3. Configure SDDM to use our theme
echo "⚙️ Setting $THEME_NAME as the current SDDM theme..."
SDDM_CONF_DIR="/etc/sddm.conf.d"
sudo mkdir -p "$SDDM_CONF_DIR"

cat <<EOF | sudo tee "$SDDM_CONF_DIR/adaptive-cachy.conf" > /dev/null
[Theme]
Current=$THEME_NAME
EOF

echo "✅ SDDM Setup Complete!"
echo "Now, whenever your wallpaper changes, the Adaptive Cachy engine will update the login screen without asking for a password."
