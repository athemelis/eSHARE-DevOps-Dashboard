#!/bin/bash

# Import a Power Automate flow export ZIP into the flows/ directory
# Extracts, pretty-prints, redacts secrets, and saves for version control
#
# Usage:
#   ./import-flow.sh <path-to-flow-export.zip>
#   ./import-flow.sh ~/Downloads/ExportADOWorkItemLinks_20260403.zip
#
# Output:
#   flows/<Flow-Display-Name>/definition.json   (redacted, pretty-printed)
#   flows/<Flow-Display-Name>/manifest.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/flows"

# ─── Validate input ─────────────────────────────────────────────

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <flow-export.zip>"
    echo ""
    echo "Export a flow from Power Automate (My flows → ... → Export → Package (.zip))"
    echo "Then run this script to import it into the flows/ directory."
    exit 1
fi

ZIP_PATH="$1"

if [[ ! -f "$ZIP_PATH" ]]; then
    echo "Error: File not found: $ZIP_PATH"
    exit 1
fi

if [[ ! "$ZIP_PATH" == *.zip ]]; then
    echo "Error: Expected a .zip file, got: $ZIP_PATH"
    exit 1
fi

# ─── Extract to temp directory ──────────────────────────────────

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Extracting flow package..."
unzip -q "$ZIP_PATH" -d "$TEMP_DIR"

# ─── Find the definition.json ──────────────────────────────────

DEFINITION=$(find "$TEMP_DIR" -name "definition.json" -path "*/Microsoft.Flow/*" | head -1)

if [[ -z "$DEFINITION" ]]; then
    echo "Error: No flow definition found in ZIP"
    echo "Contents:"
    find "$TEMP_DIR" -type f
    exit 1
fi

# ─── Extract metadata ──────────────────────────────────────────

DISPLAY_NAME=$(python3 -c "
import json, sys
with open('$DEFINITION') as f:
    d = json.load(f)
print(d['properties']['displayName'])
")

FLOW_ID=$(python3 -c "
import json, sys
with open('$DEFINITION') as f:
    d = json.load(f)
print(d['name'])
")

LAST_MODIFIED=$(python3 -c "
import json, sys
with open('$DEFINITION') as f:
    d = json.load(f)
print(d['properties']['definition']['metadata'].get('clientLastModifiedTime', 'unknown'))
")

# Convert display name to folder name (spaces → hyphens, remove special chars)
FOLDER_NAME=$(echo "$DISPLAY_NAME" | tr ' ' '-' | tr -cd '[:alnum:]-_')

echo ""
echo "Flow:          $DISPLAY_NAME"
echo "ID:            $FLOW_ID"
echo "Last modified: $LAST_MODIFIED"
echo "Folder:        flows/$FOLDER_NAME/"

# ─── Redact secrets and pretty-print ───────────────────────────

DEST_DIR="$FLOWS_DIR/$FOLDER_NAME"
mkdir -p "$DEST_DIR"

python3 << PYEOF
import json, re, sys

with open('$DEFINITION') as f:
    data = json.load(f)

# Track what was redacted
redacted = []

def redact_secrets(obj, path=""):
    """Recursively walk the definition and redact sensitive values."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            # Known secret variable names
            if key == 'value' and isinstance(value, str):
                # Check if parent path indicates a secret variable
                if any(secret in path.lower() for secret in ['pat', 'token', 'secret', 'password', 'apikey', 'api_key']):
                    redacted.append(f"  {current_path} (secret variable)")
                    obj[key] = "<REDACTED>"
                    continue

                # Detect long base64-like strings (>40 chars, alphanumeric)
                if len(value) > 40 and re.match(r'^[A-Za-z0-9+/=]+$', value):
                    redacted.append(f"  {current_path} (long token-like string, {len(value)} chars)")
                    obj[key] = "<REDACTED>"
                    continue

            # Check Authorization headers
            if key.lower() == 'authorization' and isinstance(value, str):
                redacted.append(f"  {current_path} (authorization header)")
                obj[key] = "<REDACTED>"
                continue

            redact_secrets(value, current_path)

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            redact_secrets(item, f"{path}[{i}]")

redact_secrets(data)

# Write pretty-printed, redacted definition
output_path = '$DEST_DIR/definition.json'
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

if redacted:
    print("")
    print("🔒 Redacted secrets:")
    for r in redacted:
        print(r)
else:
    print("")
    print("ℹ  No secrets detected (verify manually)")

print("")
print(f"✓ Definition saved to: flows/$FOLDER_NAME/definition.json")
PYEOF

# ─── Copy manifest ─────────────────────────────────────────────

FLOW_MANIFEST=$(find "$TEMP_DIR" -name "manifest.json" -path "*/Microsoft.Flow/flows/manifest.json" | head -1)
if [[ -n "$FLOW_MANIFEST" ]]; then
    python3 -c "import json; json.dump(json.load(open('$FLOW_MANIFEST')), open('$DEST_DIR/manifest.json', 'w'), indent=2)"
    echo "✓ Manifest saved to: flows/$FOLDER_NAME/manifest.json"
fi

# ─── Summary ────────────────────────────────────────────────────

echo ""
echo "Done! Review the redacted definition before committing:"
echo "  cat flows/$FOLDER_NAME/definition.json | head -20"
echo ""
echo "To verify no secrets remain:"
echo "  grep -i 'pat\|token\|secret\|password\|apikey' flows/$FOLDER_NAME/definition.json"
