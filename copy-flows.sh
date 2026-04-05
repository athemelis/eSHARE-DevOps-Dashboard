#!/bin/bash

# Copy Power Automate flow exports from SharePoint and import them into flows/
# Mirrors copy-data-files.sh but for flow definitions
#
# Prerequisites: Export each flow from Power Automate and save the ZIP to
#   SharePoint > Product Management > Product Planning
#
# Expected files in SharePoint:
#   ADOALLItems.zip              → flows/ADO-ALL-Items/
#   ExportADOWorkItemLinks.zip   → flows/Export-ADO-WorkItemLinks/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning"

echo "Copying flow exports from SharePoint..."
echo ""

IMPORTED=0
FAILED=0

for ZIP_NAME in "ADOALLItems.zip" "ExportADOWorkItemLinks.zip"; do
    ZIP_PATH="$SOURCE_DIR/$ZIP_NAME"
    if [[ -f "$ZIP_PATH" ]]; then
        echo "─── $ZIP_NAME ───"
        "$SCRIPT_DIR/import-flow.sh" "$ZIP_PATH"
        echo ""
        IMPORTED=$((IMPORTED + 1))
    else
        echo "⚠ $ZIP_NAME not found in SharePoint"
        FAILED=$((FAILED + 1))
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Done! Imported: $IMPORTED, Not found: $FAILED"
if [[ $IMPORTED -gt 0 ]]; then
    echo ""
    echo "Imported flows:"
    ls -la "$SCRIPT_DIR/flows"/*/definition.json 2>/dev/null
fi
