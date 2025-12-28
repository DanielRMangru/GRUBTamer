#!/bin/bash
# Uninstall GrubTamer

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./uninstall.sh)"
  exit
fi

echo "Removing GrubTamer..."
rm -rf /opt/grubtamer
rm -f /usr/local/bin/grubtamer
rm -f /usr/share/applications/org.example.GrubTamer.desktop

echo "Uninstallation complete."