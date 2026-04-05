#!/usr/bin/env python3
"""
Add picklist values to Custom.CascadingDate - Using PUT method
Updates the entire picklist in one operation
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# Configuration
ORGANIZATION = "ncryptedcloud"
PICKLIST_ID = "76934430-a481-4bdd-a6e6-1e638935911f"

# Get PAT from environment
PAT = os.environ.get('AZURE_DEVOPS_PAT')
if not PAT:
    print("ERROR: AZURE_DEVOPS_PAT environment variable not set")
    sys.exit(1)

# All target date values to add
TARGET_DATES = [
    "2025-08-02", "2025-08-08", "2025-08-09", "2025-08-30", "2025-09-06",
    "2025-09-13", "2025-09-16", "2025-09-20", "2025-09-27", "2025-10-04",
    "2025-10-11", "2025-10-18", "2025-10-25", "2025-10-28", "2025-11-01",
    "2025-11-04", "2025-11-08", "2025-11-15", "2025-11-19", "2025-11-22",
    "2025-11-29", "2025-12-02", "2025-12-06", "2025-12-11", "2025-12-13",
    "2025-12-20", "2025-12-23", "2025-12-27", "2026-01-10", "2026-01-11",
    "2026-01-13", "2026-01-14", "2026-01-15", "2026-01-17", "2026-01-22",
    "2026-01-24", "2026-01-31", "2026-02-07", "2026-02-14", "2026-02-21",
    "2026-02-28", "2026-03-07", "2026-03-14", "2026-03-21", "2026-03-28",
    "2026-04-04", "2026-04-11", "2026-04-18", "2026-04-25", "2026-05-02",
    "2026-05-09", "2026-05-16", "2026-05-23", "2026-05-30", "2026-06-06",
    "2026-06-13", "2026-06-20", "2026-06-27", "2026-07-04", "2026-07-11",
    "2026-07-18", "2026-07-25", "2026-08-01", "2026-08-08", "2026-08-15",
    "2026-08-22", "2026-08-29", "2026-09-05", "2026-09-12", "2026-09-19",
    "2026-09-26", "2026-10-03", "2026-10-10", "2026-10-17", "2026-10-24",
    "2026-10-31", "2026-11-07", "2026-11-14", "2026-11-21", "2026-11-28",
    "2026-12-05", "2026-12-12", "2026-12-19", "2026-12-26"
]

# Remove duplicates and sort
UNIQUE_DATES = sorted(list(set(TARGET_DATES)))

def get_current_picklist():
    """Get the current picklist with all its values"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/lists/{PICKLIST_ID}?api-version=7.1-preview.1"
    
    response = requests.get(url, auth=HTTPBasicAuth('', PAT))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting picklist: {response.status_code}")
        print(response.text)
        return None

def update_picklist(picklist_data, new_items):
    """Update the picklist with new items"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/lists/{PICKLIST_ID}?api-version=7.1-preview.1"
    
    # Build the payload with required fields
    payload = {
        "id": picklist_data.get('id'),
        "name": picklist_data.get('name'),
        "type": picklist_data.get('type', 'String'),
        "isSuggested": picklist_data.get('isSuggested', False),
        "items": new_items
    }
    
    response = requests.put(
        url,
        json=payload,
        auth=HTTPBasicAuth('', PAT),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code in [200, 204]:
        return True, None
    else:
        return False, f"{response.status_code}: {response.text}"

def main():
    print("=" * 80)
    print("ADD PICKLIST VALUES TO Custom.CascadingDate")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Get current picklist
        print("Step 1: Getting current picklist...")
        picklist = get_current_picklist()
        
        if not picklist:
            print("ERROR: Could not retrieve picklist")
            return
        
        print(f"  Picklist Name: {picklist.get('name', 'N/A')}")
        print(f"  Picklist ID: {picklist.get('id', 'N/A')}")
        
        # Step 2: Get existing items
        existing_items = picklist.get('items', [])
        # Items might be strings or dicts with 'value' key
        if existing_items and isinstance(existing_items[0], str):
            existing_values = existing_items
        else:
            existing_values = [item['value'] if isinstance(item, dict) else item for item in existing_items]
        
        print(f"\nStep 2: Found {len(existing_values)} existing values")
        if existing_values:
            print(f"  Example: {existing_values[:3]}")
        
        # Step 3: Merge with new values
        print(f"\nStep 3: Merging values...")
        all_values = sorted(list(set(existing_values + UNIQUE_DATES)))
        new_count = len(all_values) - len(existing_values)
        
        print(f"  Existing: {len(existing_values)}")
        print(f"  To add: {new_count}")
        print(f"  Total after merge: {len(all_values)}")
        
        if new_count == 0:
            print("\n✓ All values already exist!")
            return
        
        # Show new values
        new_values = sorted(set(UNIQUE_DATES) - set(existing_values))
        print(f"\nNew values to be added ({len(new_values)}):")
        for val in new_values[:10]:
            print(f"  {val}")
        if len(new_values) > 10:
            print(f"  ... and {len(new_values) - 10} more")
        
        # Step 4: Confirm
        print("\n" + "=" * 80)
        response = input(f"Update picklist to include all {len(all_values)} values? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
        
        # Step 5: Build new items array (always use object format for PUT)
        print("\nStep 4: Preparing update...")
        new_items = [{"value": value} for value in all_values]
        
        # Step 6: Update picklist
        print("Step 5: Updating picklist...")
        success, error = update_picklist(picklist, new_items)
        
        if success:
            print("\n" + "=" * 80)
            print("✓ SUCCESS!")
            print("=" * 80)
            print(f"Picklist updated with {len(all_values)} values")
            print(f"Added {new_count} new values")
            print("=" * 80)
        else:
            print(f"\n✗ Failed to update picklist")
            print(f"Error: {error}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
