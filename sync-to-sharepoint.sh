#!/bin/bash

# =============================================================================
# sync-to-sharepoint.sh
# 
# Syncs the eShare DevOps Dashboard from GitHub repo to SharePoint/OneDrive
# =============================================================================

# Define source and destination paths
SOURCE="/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/"
DEST="/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ᵉShare DevOps Dashboard/"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  eShare DevOps Dashboard Sync"
echo "=========================================="
echo ""

# Check if source exists
if [ ! -d "$SOURCE" ]; then
    echo "❌ Error: Source folder not found:"
    echo "   $SOURCE"
    exit 1
fi

# Check if destination exists
if [ ! -d "$DEST" ]; then
    echo "❌ Error: Destination folder not found:"
    echo "   $DEST"
    echo ""
    echo "   Make sure OneDrive is running and the folder is synced."
    exit 1
fi

echo "📁 Source:      $SOURCE"
echo "📂 Destination: $DEST"
echo ""

# Use rsync to copy files
# -a = archive mode (recursive, preserves permissions, etc.)
# -v = verbose (show files being copied)
# --delete = remove files in dest that don't exist in source
# --exclude = skip files that shouldn't be synced

echo "🔄 Syncing files..."
echo ""

rsync -av --delete \
    --exclude '.git' \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.env' \
    "$SOURCE" "$DEST"

# Check if rsync succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Sync complete!${NC}"
    echo ""
    echo "Files have been copied to SharePoint/OneDrive."
    echo "OneDrive will upload changes automatically."
else
    echo ""
    echo "❌ Sync failed. Check the error messages above."
    exit 1
fi
