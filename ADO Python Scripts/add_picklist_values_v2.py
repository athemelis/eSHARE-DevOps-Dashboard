#!/usr/bin/env python3
"""
Add picklist values to Custom.CascadingDate field - Alternative Method
Uses the organization-level fields API
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import time

# Configuration
ORGANIZATION = "ncryptedcloud"
PROJECT = "eShare"

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

print(f"Total unique values to add: {len(UNIQUE_DATES)}")

def get_field_info():
    """Get current field information"""
    url = f"https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis/wit/fields/Custom.CascadingDate?api-version=7.1"
    
    response = requests.get(url, auth=HTTPBasicAuth('', PAT))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting field info: {response.status_code}")
        print(response.text)
        return None

def get_picklist_id():
    """Get the picklist ID for Custom.CascadingDate"""
    field_info = get_field_info()
    
    if not field_info:
        return None
    
    # Check if it has a picklist
    if field_info.get('isPicklist'):
        picklist_id = field_info.get('picklistId')
        print(f"Found picklist ID: {picklist_id}")
        return picklist_id
    else:
        print("ERROR: Field is not a picklist type")
        return None

def get_picklist_values(picklist_id):
    """Get current picklist values"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/lists/{picklist_id}?api-version=7.1-preview.1"
    
    response = requests.get(url, auth=HTTPBasicAuth('', PAT))
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            return [item for item in data['items']]
        return []
    else:
        print(f"Warning: Could not get existing values ({response.status_code})")
        return []

def add_picklist_item(picklist_id, value):
    """Add a single item to the picklist"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/lists/{picklist_id}/items?api-version=7.1-preview.1"
    
    payload = {"value": value}
    
    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth('', PAT),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code in [200, 201]:
        return True, None
    else:
        return False, f"{response.status_code}: {response.text}"

def main():
    print("=" * 80)
    print("ADD PICKLIST VALUES TO Custom.CascadingDate")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Get picklist ID
        print("Step 1: Getting picklist ID...")
        picklist_id = get_picklist_id()
        
        if not picklist_id:
            print("\nERROR: Could not find picklist ID")
            print("\nAlternative: You can add the values manually in Azure DevOps:")
            print("1. Go to Project Settings > Process > ᵉShareScrum")
            print("2. Find Custom.CascadingDate field")
            print("3. Edit the field and add the values from the list")
            print("\nValues to add:")
            for date in UNIQUE_DATES:
                print(f"  {date}")
            return
        
        # Step 2: Get existing values
        print("\nStep 2: Getting existing picklist values...")
        existing = get_picklist_values(picklist_id)
        existing_values = [item['value'] for item in existing] if existing else []
        print(f"  Found {len(existing_values)} existing values")
        
        # Step 3: Merge with new values
        print("\nStep 3: Merging values...")
        new_values = sorted(set(UNIQUE_DATES) - set(existing_values))
        new_count = len(new_values)
        print(f"  Total unique dates: {len(UNIQUE_DATES)}")
        print(f"  Already exists: {len(existing_values)}")
        print(f"  New values to add: {new_count}")
        
        if new_count == 0:
            print("\n✓ All values already exist in the picklist!")
            return
        
        # Show what will be added
        print(f"\nNew values to be added ({len(new_values)}):")
        for val in new_values[:10]:
            print(f"  {val}")
        if len(new_values) > 10:
            print(f"  ... and {len(new_values) - 10} more")
        
        # Step 4: Confirm
        print("\n" + "=" * 80)
        response = input(f"Add {new_count} new values to picklist? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
        
        # Step 5: Add items one by one
        print("\nStep 4: Adding values...")
        added = 0
        failed = 0
        
        for i, value in enumerate(new_values, 1):
            success, error = add_picklist_item(picklist_id, value)
            
            if success:
                added += 1
                print(f"  [{i}/{len(new_values)}] Added '{value}' ✓")
            else:
                failed += 1
                print(f"  [{i}/{len(new_values)}] Failed '{value}': {error}")
            
            # Small delay to avoid rate limiting
            if i % 10 == 0:
                time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Successfully added: {added}")
        print(f"Failed: {failed}")
        print(f"Total values in picklist: {len(existing_values) + added}")
        print("=" * 80)
        
        if added > 0:
            print("\n✓ Picklist values added successfully!")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
