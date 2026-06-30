#!/bin/bash
# Setup script for RoboMaster S1 USB/RNDIS connection on Linux

echo "=============================================="
echo "RoboMaster S1 USB Setup (Linux)"
echo "=============================================="
echo ""

# Check if running as root for some operations
if [ "$EUID" -eq 0 ]; then 
   echo "ℹ️  Script läuft als root (für Netzwerk-Konfiguration)"
fi

echo "Prüfe USB-Verbindung..."
echo ""

# Check dmesg for RNDIS device
echo "1. Suche RNDIS-Gerät in dmesg:"
dmesg | grep -i "rndis\|robomaster\|usb.*eth" | tail -5

echo ""
echo "2. Netzwerk-Interfaces:"
ip addr | grep -A2 "usb\|enx\|eth" | head -20

echo ""
echo "3. Prüfe Verbindung zu RoboMaster (192.168.42.2):"
ping -c 2 -W 2 192.168.42.2 && echo "✅ RoboMaster erreichbar!" || echo "❌ RoboMaster nicht erreichbar"

echo ""
echo "=============================================="
echo "Setup-Anleitung:"
echo "=============================================="
echo ""
echo "Falls der RoboMaster nicht erreichbar ist:"
echo ""
echo "Schritt 1: USB-Interface identifizieren"
echo "  ip addr"
echo "  → Suche nach 'usb', 'enx' oder ähnlichem"
echo ""
echo "Schritt 2: Manuelle IP-Konfiguration"
echo "  sudo ip addr add 192.168.42.20/24 dev <INTERFACE>"
echo "  sudo ip link set <INTERFACE> up"
echo ""
echo "Beispiel:"
echo "  sudo ip addr add 192.168.42.20/24 dev enx123456789abc"
echo "  sudo ip link set enx123456789abc up"
echo ""
echo "Schritt 3: Verbindung testen"
echo "  ping 192.168.42.2"
echo ""
echo "=============================================="
