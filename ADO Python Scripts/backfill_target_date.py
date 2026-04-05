#!/usr/bin/env python3
"""
Production Script: Convert targetDate (UTC) to Custom.Target_Date (Athens timezone)
for all Features and Bugs in eShare project

Requirements:
  pip install azure-devops pytz

Usage:
  export AZURE_DEVOPS_PAT="your-pat-here"
  python3 convert_all_target_dates_production.py
"""

import os
import sys
from datetime import datetime
import pytz
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation

# Configuration
ORGANIZATION_URL = "https://dev.azure.com/ncryptedcloud"
PROJECT = "eShare"
BATCH_SIZE = 200  # Process updates in batches

# Get PAT from environment
PAT = os.environ.get('AZURE_DEVOPS_PAT')
if not PAT:
    print("ERROR: AZURE_DEVOPS_PAT environment variable not set")
    print("Usage: export AZURE_DEVOPS_PAT='your-pat-here'")
    sys.exit(1)

# Azure DevOps connection
credentials = BasicAuthentication('', PAT)
connection = Connection(base_url=ORGANIZATION_URL, creds=credentials)
wit_client = connection.clients.get_work_item_tracking_client()

# Timezone setup
ATHENS = pytz.timezone('Europe/Athens')

def convert_utc_to_athens_date(utc_datetime_str):
    """Convert UTC datetime string to Athens date string (YYYY-MM-DD)"""
    utc_dt = datetime.fromisoformat(utc_datetime_str.replace('Z', '+00:00'))
    athens_dt = utc_dt.astimezone(ATHENS)
    return athens_dt.strftime('%Y-%m-%d')

def query_work_items():
    """Query for all Features and Bugs with targetDate"""
    print("Querying for Features and Bugs with targetDate...")
    
    wiql = """
    SELECT [System.Id]
    FROM WorkItems
    WHERE [System.TeamProject] = 'eShare'
      AND [System.WorkItemType] IN ('Feature', 'Bug')
      AND [Microsoft.VSTS.Scheduling.TargetDate] <> ''
    ORDER BY [System.Id]
    """
    
    result = wit_client.query_by_wiql({'query': wiql}, project=PROJECT)
    
    if not result.work_items:
        return []
    
    work_item_ids = [item.id for item in result.work_items]
    print(f"Found {len(work_item_ids)} work items with targetDate")
    
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
                   'Microsoft.VSTS.Scheduling.TargetDate', 'Custom.Target_Date']
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
        'no_target_date': 0,
        'conversion_error': 0
    }
    
    for wi in work_items:
        target_date_utc = wi.fields.get('Microsoft.VSTS.Scheduling.TargetDate')
        current_custom = wi.fields.get('Custom.Target_Date')
        
        # Skip if no targetDate
        if not target_date_utc:
            stats['no_target_date'] += 1
            continue
        
        # Convert to Athens
        try:
            athens_date = convert_utc_to_athens_date(target_date_utc)
        except Exception as e:
            print(f"  Warning: Conversion error for work item {wi.id}: {e}")
            stats['conversion_error'] += 1
            continue
        
        # Check if update needed
        if current_custom == athens_date:
            stats['already_correct'] += 1
            continue
        
        # Add to updates
        updates.append({
            'id': wi.id,
            'path': '/fields/Custom.Target_Date',
            'value': athens_date,
            'op': 'add'
        })
        stats['needs_update'] += 1
    
    print(f"\nAnalysis complete:")
    print(f"  Total work items: {stats['total']}")
    print(f"  Need updates: {stats['needs_update']}")
    print(f"  Already correct: {stats['already_correct']}")
    print(f"  No target date: {stats['no_target_date']}")
    print(f"  Conversion errors: {stats['conversion_error']}")
    
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
                failed.append({'id': update['id'], 'error': str(e)})
                print(f"    ⚠️  Failed work item {update['id']}: {e}")
        
        print(f"  ✓ Batch {batch_num} complete")
    
    return updated, failed

def main():
    print("=" * 80)
    print("TARGET DATE CONVERSION: UTC → Athens (YYYY-MM-DD)")
    print("=" * 80)
    print()
    
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
        response = input(f"Proceed with updating {len(updates)} work items? (yes/no): ")
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
            print(f"  - Work item {f['id']}: {f['error']}")
        if len(failed) > 20:
            print(f"  ... and {len(failed) - 20} more")
    
    print("\n" + "=" * 80)
    if updated > 0:
        print("✓ Conversion complete!")
    print("=" * 80)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)