#!/bin/bash
#
# Trigger Pi deployment remotely with network diagnostics
# This script connects to the Pi and runs the deployment script
#

PI_HOST="192.168.1.191"
PI_USER="nico"
PI_PASSWORD="Eight432Rpi!"
DEPLOY_SCRIPT="~/absolute/absolute-power/price-tracker-planning/deploy.sh"

echo "🚀 Triggering Pi deployment..."
echo "Host: ${PI_USER}@${PI_HOST}"
echo "Script: ${DEPLOY_SCRIPT}"
echo ""

# Network diagnostics
echo "🔍 Running network diagnostics..."

# Test network connectivity
echo -n "Testing network connectivity to ${PI_HOST}... "
if ping -c 1 -W 5000 ${PI_HOST} >/dev/null 2>&1; then
    echo "✅ Pi is reachable"
else
    echo "❌ Pi is not responding to ping"
    echo ""
    echo "🔧 Troubleshooting suggestions:"
    echo "1. Check if Pi is powered on and connected to network"
    echo "2. Verify Pi IP address hasn't changed (check router/DHCP)"
    echo "3. Try: nmap -sn 192.168.1.0/24 | grep -B2 -A2 192.168.1.191"
    echo "4. Check WiFi connection on Pi"
    exit 1
fi

# Test SSH port
echo -n "Testing SSH port (22) on ${PI_HOST}... "
if nc -z -w5 ${PI_HOST} 22 2>/dev/null; then
    echo "✅ SSH port is open"
else
    echo "❌ SSH port is not accessible"
    echo ""
    echo "🔧 Troubleshooting suggestions:"
    echo "1. Check if SSH service is running on Pi: sudo systemctl status ssh"
    echo "2. Check SSH configuration: sudo nano /etc/ssh/sshd_config"
    echo "3. Restart SSH service: sudo systemctl restart ssh"
    exit 1
fi

# Check sshpass availability
if ! command -v sshpass >/dev/null 2>&1; then
    echo "❌ sshpass not found. Install with: brew install sshpass"
    echo "Or manually SSH and run: ssh ${PI_USER}@${PI_HOST}"
    echo "Then execute: ${DEPLOY_SCRIPT}"
    exit 1
fi

echo ""
echo "🔐 Connecting to Pi and triggering deployment..."

# SSH with timeout and better error handling
if sshpass -p "${PI_PASSWORD}" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${PI_USER}@${PI_HOST}" "cd ~/absolute/absolute-power/price-tracker-planning && ./deploy.sh"; then
    echo ""
    echo "✅ Pi deployment triggered successfully!"
    echo "📊 Check git for new commits to confirm completion."
    echo "🕐 Deployment typically takes 2-5 minutes."
else
    echo ""
    echo "❌ SSH connection or deployment failed"
    echo ""
    echo "🔧 Manual connection command:"
    echo "ssh ${PI_USER}@${PI_HOST}"
    echo ""
    echo "🔧 Manual deployment command:"
    echo "cd ~/absolute/absolute-power/price-tracker-planning && ./deploy.sh"
    exit 1
fi