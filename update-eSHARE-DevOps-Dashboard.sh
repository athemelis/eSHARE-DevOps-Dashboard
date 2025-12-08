#!/bin/bash
#
# Update eSHARE DevOps Dashboard
#
# Usage:
#   ./update-eSHARE-DevOps-Dashboard.sh           # Generate to local directory (for testing)
#   ./update-eSHARE-DevOps-Dashboard.sh --publish # Publish to SharePoint (production)
#   ./update-eSHARE-DevOps-Dashboard.sh -p        # Same as above
#

cd "/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/"

# Pass all arguments through to the Python script
/usr/bin/python3 generate_dashboard.py "$@"
