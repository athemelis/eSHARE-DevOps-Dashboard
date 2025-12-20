#!/bin/bash
#
# Update eSHARE DevOps Dashboard
#
# Usage:
#   ./update-eSHARE-DevOps-Dashboard.sh           # Generate to local directory (for testing) using dev templates
#   ./update-eSHARE-DevOps-Dashboard.sh --publish # Publish to SharePoint (production) using production templates
#   ./update-eSHARE-DevOps-Dashboard.sh -p        # Same as above
#
# Template directories:
#   - Dev templates:  ./Templates (for local development)
#   - Prod templates: ./Templates-Production (for scheduled publishing)
#

cd "/Users/tonythem/GitHub/athemelis/eSHARE-DevOps-Dashboard/"

# Check if --publish or -p flag is present
if [[ "$*" == *"--publish"* ]] || [[ "$*" == *"-p"* ]]; then
    # Use production templates for publishing
    /usr/bin/python3 generate_dashboard.py -t "./Templates-Production" "$@"
else
    # Use dev templates for local testing
    /usr/bin/python3 generate_dashboard.py "$@"
fi
