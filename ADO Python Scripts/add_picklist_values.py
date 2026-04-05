#!/usr/bin/env python3
"""
Add picklist values to Custom.CascadingDate field
This script adds all target date values as picklist options
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# Configuration
ORGANIZATION = "ncryptedcloud"
PROJECT = "eShare"
PROCESS_NAME = "ᵉShareScrum"

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
    "2025-12-20", "2025-12-23", "2025-12-27", "2026-01-10", "2026-01-10",
    "2026-01-10", "2026-01-11", "2026-01-13", "2026-01-14", "2026-01-15",
    "2026-01-17", "2026-01-22", "2026-01-24", "2026-01-31", "2026-02-07",
    "2026-02-14", "2026-02-21", "2026-02-28", "2026-03-07", "2026-03-14",
    "2026-03-21", "2026-03-28", "2026-04-04", "2026-04-11", "2026-04-18",
    "2026-04-25", "2026-05-02", "2026-05-09", "2026-05-16", "2026-05-23",
    "2026-05-30", "2026-06-06", "2026-06-13", "2026-06-20", "2026-06-27",
    "2026-07-04", "2026-07-11", "2026-07-18", "2026-07-25", "2026-08-01",
    "2026-08-08", "2026-08-15", "2026-08-22", "2026-08-29", "2026-09-05",
    "2026-09-12", "2026-09-19", "2026-09-26", "2026-10-03", "2026-10-10",
    "2026-10-17", "2026-10-24", "2026-10-31", "2026-11-07", "2026-11-14",
    "2026-11-21", "2026-11-28", "2026-12-05", "2026-12-12", "2026-12-19",
    "2026-12-26"
]

# Remove duplicates and sort
UNIQUE_DATES = sorted(list(set(TARGET_DATES)))

print(f"Will add {len(UNIQUE_DATES)} unique picklist values")
print(f"(Removed {len(TARGET_DATES) - len(UNIQUE_DATES)} duplicates)")

def get_process_id():
    """Get the process ID for eShareScrum"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes?api-version=7.1-preview.2"
    
    response = requests.get(url, auth=HTTPBasicAuth('', PAT))
    response.raise_for_status()
    
    processes = response.json()['value']
    for process in processes:
        if process['name'] == PROCESS_NAME:
            return process['typeId']
    
    raise Exception(f"Process '{PROCESS_NAME}' not found")

def get_field_id(process_id):
    """Get the field ID for Custom.CascadingDate"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/{process_id}/fields?api-version=7.1-preview.2"
    
    response = requests.get(url, auth=HTTPBasicAuth('', PAT))
    response.raise_for_status()
    
    fields = response.json()['value']
    for field in fields:
        if field.get('referenceName') == 'Custom.CascadingDate':
            return field['id']
    
    raise Exception("Field 'Custom.CascadingDate' not found")

def get_existing_picklist_values(process_id, field_id):
    """Get existing picklist values"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/{process_id}/fields/{field_id}/picklists?api-version=7.1-preview.1"
    
    try:
        response = requests.get(url, auth=HTTPBasicAuth('', PAT))
        if response.status_code == 200:
            data = response.json()
            if 'items' in data:
                return [item['value'] for item in data['items']]
        return []
    except:
        return []

def add_picklist_value(process_id, field_id, value):
    """Add a single picklist value"""
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes/{process_id}/fields/{field_id}/picklists?api-version=7.1-preview.1"
    
    payload = {"value": value}
    
    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth('', PAT),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code in [200, 201]:
        return True
    else:
        print(f"  Error adding '{value}': {response.status_code} - {response.text}")
        return False

def main():
    print("=" * 80)
    print("ADD PICKLIST VALUES TO Custom.CascadingDate")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Get process ID
        print("Step 1: Getting process ID for eShareScrum...")
        process_id = get_process_id()
        print(f"  Process ID: {process_id}")
        
        # Step 2: Get field ID
        print("\nStep 2: Getting field ID for Custom.CascadingDate...")
        field_id = get_field_id(process_id)
        print(f"  Field ID: {field_id}")
        
        # Step 3: Get existing picklist values
        print("\nStep 3: Checking existing picklist values...")
        existing_values = get_existing_picklist_values(process_id, field_id)
        print(f"  Found {len(existing_values)} existing values")
        
        # Step 4: Add new values
        print(f"\nStep 4: Adding {len(UNIQUE_DATES)} picklist values...")
        added = 0
        skipped = 0
        failed = 0
        
        for i, date_value in enumerate(UNIQUE_DATES, 1):
            if date_value in existing_values:
                print(f"  [{i}/{len(UNIQUE_DATES)}] Skipped '{date_value}' (already exists)")
                skipped += 1
            else:
                if add_picklist_value(process_id, field_id, date_value):
                    print(f"  [{i}/{len(UNIQUE_DATES)}] Added '{date_value}' ✓")
                    added += 1
                else:
                    failed += 1
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total values: {len(UNIQUE_DATES)}")
        print(f"Added: {added}")
        print(f"Skipped (already existed): {skipped}")
        print(f"Failed: {failed}")
        print("=" * 80)
        
        if failed > 0:
            print("\nNOTE: Some values failed to add. You may need to add them manually.")
            print("Go to: Project Settings > Process > eShareScrum > Custom.CascadingDate")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
