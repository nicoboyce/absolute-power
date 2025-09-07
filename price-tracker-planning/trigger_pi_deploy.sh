#!/bin/bash
#
# Trigger Pi deployment remotely
# This script connects to the Pi and runs the deployment script
#

set -e

PI_HOST="192.168.1.191"
PI_USER="nico"
PI_PASSWORD="Eight432Rpi!"
DEPLOY_SCRIPT="~/absolute/absolute-power/price-tracker-planning/deploy.sh"

echo "Triggering Pi deployment..."
echo "Host: ${PI_USER}@${PI_HOST}"
echo "Script: ${DEPLOY_SCRIPT}"
echo ""

# Use sshpass to automate password entry
if command -v sshpass >/dev/null 2>&1; then
    echo "Using sshpass for authentication..."
    sshpass -p "${PI_PASSWORD}" ssh -o StrictHostKeyChecking=no "${PI_USER}@${PI_HOST}" "cd ~/absolute/absolute-power/price-tracker-planning && ./deploy.sh"
else
    echo "sshpass not found. Install with: brew install sshpass"
    echo "Or manually SSH and run: ssh ${PI_USER}@${PI_HOST}"
    echo "Then execute: ${DEPLOY_SCRIPT}"
    exit 1
fi

echo ""
echo "Pi deployment triggered successfully!"
echo "Check git for new commits to confirm completion."