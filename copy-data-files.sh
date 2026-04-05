#!/bin/bash

# Copy JSON data files from SharePoint (OneDrive sync) to local project directory
# This enables local development with the dashboard-body.html

SOURCE_DIR="/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning"
DEST_DIR="/Users/tonythem/GitHub/eSHARE/eSHARE-DevOps-Dashboard"

echo "Copying data files from SharePoint..."

# Copy each file
cp "$SOURCE_DIR/ALL Items.json" "$DEST_DIR/" && echo "✓ ALL Items.json"
cp "$SOURCE_DIR/WorkItemLinks.json" "$DEST_DIR/" && echo "✓ WorkItemLinks.json"
cp "$SOURCE_DIR/Org Chart.json" "$DEST_DIR/" && echo "✓ Org Chart.json"
cp "$SOURCE_DIR/cascading_lists.json" "$DEST_DIR/" && echo "✓ cascading_lists.json"
cp "$SOURCE_DIR/mention-cache.json" "$DEST_DIR/" 2>/dev/null && echo "✓ mention-cache.json" || echo "⚠ mention-cache.json not found (notifications won't be available offline)"

echo ""
echo "Done! Files copied to: $DEST_DIR"
ls -lh "$DEST_DIR"/*.json 2>/dev/null
