#!/bin/bash

# GrubTamer Installer
# Installs application to /opt/grubtamer and creates menu shortcuts.

APP_NAME="GrubTamer"
INSTALL_DIR="/opt/grubtamer"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit
fi

# Check if we are in the project directory
if [ ! -f "main.py" ]; then
  echo "Error: Could not find main.py. Please run this script from the GrubTamer project folder."
  exit 1
fi

echo "--- Installing Dependencies ---"
# Install Python GI, GTK4, LibAdwaita, and Cairo
apt update
apt install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

echo "--- Creating Installation Directory ---"
# Create /opt/grubtamer
mkdir -p "$INSTALL_DIR"

echo "--- Copying Files ---"
# Copy source code
cp -r src "$INSTALL_DIR/"
cp main.py "$INSTALL_DIR/"

# If you have an icon, copy it (Assuming icon.png exists, otherwise use generic)
if [ -f "icon.png" ]; then
    cp icon.png "$INSTALL_DIR/icon.png"
    ICON_PATH="$INSTALL_DIR/icon.png"
else
    # Fallback to a system icon
    ICON_PATH="system-search" # A generic looking icon
fi

echo "--- Creating Executable ---"
# Create a wrapper script in /usr/local/bin
cat > "$BIN_DIR/grubtamer" <<EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 main.py "\$@"
EOF

# Make it executable
chmod +x "$BIN_DIR/grubtamer"

echo "--- Creating Desktop Entry ---"
# Create the .desktop file for the Start Menu
cat > "$DESKTOP_DIR/org.example.GrubTamer.desktop" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=Customize your GRUB bootloader theme and settings
Exec=grubtamer
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=System;Settings;
EOF

echo "--- Installation Complete! ---"
echo "You can now run '$APP_NAME' from your applications menu or by typing 'grubtamer' in the terminal."