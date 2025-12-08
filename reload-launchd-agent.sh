#!/bin/bash
#
# Reload the eSHARE DevOps Dashboard launchd agent
#
# Usage:
#   ./reload-launchd-agent.sh
#

PLIST=~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
LABEL=com.eshare.devops.dashboard

echo "Reloading launchd agent: $LABEL"

# Clear previous logs
echo "  Clearing old logs..."
: > /tmp/eshare_devops_dashboard.out
: > /tmp/eshare_devops_dashboard.err

# Unload (ignore errors if not loaded)
echo "  Unloading..."
launchctl unload "$PLIST" 2>/dev/null || true

# Load
echo "  Loading..."
launchctl load "$PLIST"

# Kickstart to run immediately
echo "  Kickstarting..."
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "Done! Waiting for output..."
sleep 2

echo ""
echo "========== Recent Output (last 20 lines) =========="
tail -n 20 /tmp/eshare_devops_dashboard.out 2>/dev/null || echo "(no output yet)"

echo ""
echo "========== Recent Errors (last 20 lines) =========="
tail -n 20 /tmp/eshare_devops_dashboard.err 2>/dev/null || echo "(no errors)"

echo ""
echo "Check status with: launchctl list | grep eshare"
