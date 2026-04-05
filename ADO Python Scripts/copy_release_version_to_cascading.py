#!/usr/bin/env python3
"""
Copy Custom.ReleaseVersion to Custom.CascadingVersion
Copies exact string values from one field to another
"""

import os
import sys
from datetime import datetime
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation, Wiql

# Configuration
ORGANIZATION_URL = "https://dev.azure.com/ncryptedcloud"
PROJECT = "eShare"
BATCH_SIZE = 200

# Get PAT from environment
PAT = os.environ.get('AZURE_DEVOPS_PAT')
if not PAT:
    print("ERROR: AZURE_DEVOPS_PAT environment variable not set")
    sys.exit(1)

# Azure DevOps connection
credentials = BasicAuthentication('', PAT)
connection = Connection(base_url=ORGANIZATION_URL, creds=credentials)
wit_client = connection.clients.get_work_item_tracking_client()

def query_work_items():
    """Query for all work items with Custom.ReleaseVersion populated"""
    print("Querying for work items with Custom.ReleaseVersion...")
    
    wiql = """
    SELECT [System.Id]
    FROM WorkItems
    WHERE [System.TeamProject] = 'eShare'
      AND [Custom.ReleaseVersion] <> ''
    ORDER BY [System.Id]
    """
    
    wiql_object = Wiql(query=wiql)
    result = wit_client.query_by_wiql(wiql_object)
    
    if not result.work_items:
        return []
    
    work_item_ids = [item.id for item in result.work_items]
    print(f"Found {len(work_item_ids)} work items with Custom.ReleaseVersion")
    
    return work_item_ids

def fetch_work_items(ids):
    """Fetch work items in batches"""
    print(f"\nFetching {len(ids)} work items...")
    
    all_items = []
    for i in range(0, len(ids), BATCH_SIZE):
        batch = ids[i:i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}: Fetching {len(batch)} items...")
        
        items = wit_client.get_work_items(
            ids=batch,
            project=PROJECT,
            fields=['System.WorkItemType', 'System.Title', 
                   'Custom.ReleaseVersion', 'Custom.CascadingVersion']
        )
        all_items.extend(items)
    
    return all_items

def prepare_updates(work_items):
    """Prepare update operations"""
    print(f"\nAnalyzing {len(work_items)} work items...")
    
    updates = []
    stats = {
        'total': len(work_items),
        'needs_update': 0,
        'already_correct': 0,
        'no_release_version': 0,
        'empty_release_version': 0
    }
    
    for wi in work_items:
        release_version = wi.fields.get('Custom.ReleaseVersion')
        cascading_version = wi.fields.get('Custom.CascadingVersion')
        
        # Skip if no ReleaseVersion
        if not release_version:
            stats['no_release_version'] += 1
            continue
        
        # Skip if ReleaseVersion is empty string
        if release_version.strip() == '':
            stats['empty_release_version'] += 1
            continue
        
        # Check if update needed
        if cascading_version == release_version:
            stats['already_correct'] += 1
            continue
        
        # Add to updates
        updates.append({
            'id': wi.id,
            'type': wi.fields.get('System.WorkItemType'),
            'title': wi.fields.get('System.Title', 'N/A')[:50],
            'path': '/fields/Custom.CascadingVersion',
            'value': release_version,
            'op': 'add'
        })
        stats['needs_update'] += 1
    
    print(f"\nAnalysis complete:")
    print(f"  Total work items: {stats['total']}")
    print(f"  Need updates: {stats['needs_update']}")
    print(f"  Already correct: {stats['already_correct']}")
    print(f"  No release version: {stats['no_release_version']}")
    print(f"  Empty release version: {stats['empty_release_version']}")
    
    return updates, stats

def update_work_items(updates):
    """Execute batch updates"""
    if not updates:
        print("\nNo updates needed!")
        return 0, []
    
    print(f"\nUpdating {len(updates)} work items...")
    
    updated = 0
    failed = []
    
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(updates) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"  Batch {batch_num}/{total_batches}: Updating {len(batch)} items...")
        
        for update in batch:
            try:
                patch_doc = [JsonPatchOperation(
                    op=update['op'],
                    path=update['path'],
                    value=update['value']
                )]
                
                wit_client.update_work_item(
                    document=patch_doc,
                    id=update['id'],
                    project=PROJECT
                )
                updated += 1
                
                # Progress indicator
                if updated % 50 == 0:
                    print(f"    Progress: {updated}/{len(updates)} ({100*updated//len(updates)}%)")
                    
            except Exception as e:
                error_msg = str(e)
                failed.append({
                    'id': update['id'],
                    'type': update['type'],
                    'title': update['title'],
                    'value': update['value'],
                    'error': error_msg
                })
                print(f"    ⚠️  Failed work item {update['id']}: {error_msg}")
        
        print(f"  ✓ Batch {batch_num} complete")
    
    return updated, failed

def main():
    print("=" * 80)
    print("COPY: Custom.ReleaseVersion → Custom.CascadingVersion")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Query for work items
        work_item_ids = query_work_items()
        if not work_item_ids:
            print("No work items found to process.")
            return
        
        # Step 2: Fetch work items
        work_items = fetch_work_items(work_item_ids)
        
        # Step 3: Prepare updates
        updates, stats = prepare_updates(work_items)
        
        # Step 4: Confirm before proceeding
        if updates:
            print("\n" + "=" * 80)
            # Show sample of what will be updated
            print("Sample updates (first 5):")
            for update in updates[:5]:
                print(f"  {update['type']} {update['id']}: '{update['value']}'")
            if len(updates) > 5:
                print(f"  ... and {len(updates) - 5} more")
            
            print("=" * 80)
            response = input(f"\nProceed with updating {len(updates)} work items? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
            print("=" * 80)
        
        # Step 5: Execute updates
        updated, failed = update_work_items(updates)
        
        # Final summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        print(f"Total work items queried: {stats['total']}")
        print(f"Successfully updated: {updated}")
        print(f"Already correct (skipped): {stats['already_correct']}")
        print(f"Failed: {len(failed)}")
        
        if failed:
            print("\nFailed updates:")
            for f in failed[:20]:
                print(f"  - {f['type']} {f['id']}: '{f['value']}' - {f['error']}")
            if len(failed) > 20:
                print(f"  ... and {len(failed) - 20} more")
            
            # Check if failures are due to invalid picklist values
            invalid_picklist = [f for f in failed if 'is not a valid list value' in f['error'].lower() 
                                or 'not in the list' in f['error'].lower()]
            if invalid_picklist:
                print(f"\n⚠️  {len(invalid_picklist)} failures appear to be invalid picklist values.")
                print("You may need to add these values to the picklist or disable validation.")
                unique_values = set(f['value'] for f in invalid_picklist)
                print(f"\nUnique values that failed ({len(unique_values)}):")
                for val in sorted(unique_values)[:20]:
                    print(f"  - {val}")
                if len(unique_values) > 20:
                    print(f"  ... and {len(unique_values) - 20} more")
        
        print("\n" + "=" * 80)
        if updated > 0:
            print("✓ Copy complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
