#!/usr/bin/env python3
"""
Migrate Issue Target Date to Cascading Date
Converts Microsoft.VSTS.Scheduling.TargetDate (UTC) → Custom.CascadingDate (Athens date)

The TargetDate field stores UTC datetime. We convert to Athens timezone and extract
the date in YYYY-MM-DD format for the CascadingDate picklist field.

Requirements:
  pip install azure-devops pytz

Usage:
  export AZURE_DEVOPS_PAT="your-pat-here"
  
  # Dry run (show what would be updated)
  python3 migrate_issue_target_date.py --dry-run
  
  # Test on specific Issue
  python3 migrate_issue_target_date.py --issue-id 544
  
  # Test on first N Issues
  python3 migrate_issue_target_date.py --limit 10
  
  # Full migration
  python3 migrate_issue_target_date.py
"""

import os
import sys
import argparse
from datetime import datetime
import pytz
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation, Wiql

# Configuration
ORGANIZATION_URL = "https://dev.azure.com/ncryptedcloud"
PROJECT = "eShare"
BATCH_SIZE = 200

# Timezone setup - Athens is where the team is based
ATHENS = pytz.timezone('Europe/Athens')

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


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Migrate Issue TargetDate to CascadingDate (with timezone conversion)'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be updated without making changes')
    parser.add_argument('--issue-id', type=int,
                        help='Process only a specific Issue ID')
    parser.add_argument('--limit', type=int,
                        help='Process only first N Issues')
    return parser.parse_args()


def convert_utc_to_athens_date(utc_datetime_str):
    """
    Convert UTC datetime string to Athens date string (YYYY-MM-DD)
    
    ADO stores date-only fields as midnight in the user's timezone, but exports as UTC.
    Example: Dec 11 midnight Athens = Dec 10 22:00 UTC = "2025-12-10T22:00:00Z"
    We convert back to Athens to get the intended date.
    """
    if not utc_datetime_str:
        return None
    
    try:
        # Handle both 'Z' suffix and '+00:00' format
        if utc_datetime_str.endswith('Z'):
            utc_datetime_str = utc_datetime_str[:-1] + '+00:00'
        
        utc_dt = datetime.fromisoformat(utc_datetime_str)
        athens_dt = utc_dt.astimezone(ATHENS)
        return athens_dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"    Warning: Could not parse date '{utc_datetime_str}': {e}")
        return None


def query_work_items(issue_id=None):
    """Query for Issues with TargetDate but no CascadingDate"""
    if issue_id:
        print(f"Fetching Issue {issue_id}...")
        return [issue_id]
    
    print("Querying for Issues with TargetDate...")
    
    # Query for Issues with TargetDate populated
    # We'll filter for missing CascadingDate in prepare_updates
    wiql = """
    SELECT [System.Id]
    FROM WorkItems
    WHERE [System.TeamProject] = 'eShare'
      AND [System.WorkItemType] = 'Issue'
      AND [Microsoft.VSTS.Scheduling.TargetDate] <> ''
    ORDER BY [System.Id]
    """
    
    wiql_object = Wiql(query=wiql)
    result = wit_client.query_by_wiql(wiql_object)
    
    if not result.work_items:
        return []
    
    work_item_ids = [item.id for item in result.work_items]
    print(f"Found {len(work_item_ids)} Issues with TargetDate")
    
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
            fields=['System.WorkItemType', 'System.Title', 'System.State',
                   'Microsoft.VSTS.Scheduling.TargetDate', 'Custom.CascadingDate']
        )
        all_items.extend(items)
    
    return all_items


def prepare_updates(work_items, limit=None):
    """Prepare update operations"""
    print(f"\nAnalyzing {len(work_items)} work items...")
    
    updates = []
    stats = {
        'total': len(work_items),
        'needs_update': 0,
        'already_correct': 0,
        'already_has_cascading': 0,
        'no_target_date': 0,
        'invalid_date': 0
    }
    
    for wi in work_items:
        target_date_utc = wi.fields.get('Microsoft.VSTS.Scheduling.TargetDate')
        cascading_date = wi.fields.get('Custom.CascadingDate')
        
        # Skip if no TargetDate
        if not target_date_utc:
            stats['no_target_date'] += 1
            continue
        
        # Convert UTC to Athens date
        athens_date = convert_utc_to_athens_date(target_date_utc)
        if not athens_date:
            stats['invalid_date'] += 1
            continue
        
        # Skip if CascadingDate already matches
        if cascading_date == athens_date:
            stats['already_correct'] += 1
            continue
        
        # Skip if CascadingDate already has a value (different from converted date)
        if cascading_date and cascading_date.strip():
            stats['already_has_cascading'] += 1
            continue
        
        # Add to updates
        updates.append({
            'id': wi.id,
            'type': wi.fields.get('System.WorkItemType'),
            'state': wi.fields.get('System.State'),
            'title': wi.fields.get('System.Title', 'N/A')[:50],
            'path': '/fields/Custom.CascadingDate',
            'old_value': cascading_date or '(empty)',
            'utc_value': target_date_utc,
            'value': athens_date,
            'op': 'add'
        })
        stats['needs_update'] += 1
        
        # Apply limit if specified
        if limit and stats['needs_update'] >= limit:
            print(f"  Limit of {limit} reached")
            break
    
    print(f"\nAnalysis complete:")
    print(f"  Total Issues analyzed: {stats['total']}")
    print(f"  Need updates: {stats['needs_update']}")
    print(f"  Already correct: {stats['already_correct']}")
    print(f"  Already has CascadingDate: {stats['already_has_cascading']}")
    print(f"  No target date: {stats['no_target_date']}")
    print(f"  Invalid date format: {stats['invalid_date']}")
    
    return updates, stats


def update_work_items(updates, dry_run=False):
    """Execute batch updates"""
    if not updates:
        print("\nNo updates needed!")
        return 0, []
    
    if dry_run:
        print(f"\n[DRY RUN] Would update {len(updates)} work items:")
        for update in updates:
            print(f"  Issue {update['id']} ({update['state']}): UTC '{update['utc_value']}' → Athens '{update['value']}'")
            print(f"    Title: {update['title']}")
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
                print(f"    ✓ Issue {update['id']}: UTC '{update['utc_value']}' → Athens '{update['value']}'")
                
            except Exception as e:
                error_msg = str(e)
                failed.append({
                    'id': update['id'],
                    'type': update['type'],
                    'title': update['title'],
                    'value': update['value'],
                    'error': error_msg
                })
                print(f"    ⚠️  Failed Issue {update['id']}: {error_msg}")
        
        print(f"  ✓ Batch {batch_num} complete")
    
    return updated, failed


def main():
    args = parse_args()
    
    print("=" * 80)
    print("MIGRATE ISSUES: TargetDate (UTC) → CascadingDate (Athens)")
    if args.dry_run:
        print("[DRY RUN MODE - No changes will be made]")
    if args.issue_id:
        print(f"[SINGLE ISSUE MODE - Issue {args.issue_id}]")
    if args.limit:
        print(f"[LIMITED MODE - First {args.limit} Issues]")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Query for Issues
        work_item_ids = query_work_items(args.issue_id)
        if not work_item_ids:
            print("No Issues found to process.")
            return
        
        # Step 2: Fetch work items
        work_items = fetch_work_items(work_item_ids)
        
        # Step 3: Prepare updates
        updates, stats = prepare_updates(work_items, args.limit)
        
        # Step 4: Confirm before proceeding (unless dry run or single issue)
        if updates and not args.dry_run:
            print("\n" + "=" * 80)
            print("Updates to be made:")
            for update in updates[:10]:
                print(f"  Issue {update['id']} ({update['state']}): → '{update['value']}'")
            if len(updates) > 10:
                print(f"  ... and {len(updates) - 10} more")
            
            print("=" * 80)
            response = input(f"\nProceed with updating {len(updates)} Issues? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
            print("=" * 80)
        
        # Step 5: Execute updates
        updated, failed = update_work_items(updates, args.dry_run)
        
        # Final summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        print(f"Total Issues analyzed: {stats['total']}")
        if args.dry_run:
            print(f"Would update: {len(updates)}")
        else:
            print(f"Successfully updated: {updated}")
        print(f"Already correct (skipped): {stats['already_correct']}")
        print(f"Already has CascadingDate (skipped): {stats.get('already_has_cascading', 0)}")
        print(f"Failed: {len(failed)}")
        
        if failed:
            print("\nFailed updates:")
            for f in failed:
                print(f"  - Issue {f['id']}: '{f['value']}' - {f['error']}")
            
            # Check for picklist errors
            picklist_errors = [f for f in failed if 'picklist' in f['error'].lower() 
                              or 'not a valid' in f['error'].lower()]
            if picklist_errors:
                print(f"\n⚠️  {len(picklist_errors)} failures appear to be invalid picklist values.")
                print("You may need to add these date values to the CascadingDate picklist:")
                unique_values = sorted(set(f['value'] for f in picklist_errors))
                for val in unique_values[:20]:
                    print(f"  - {val}")
                if len(unique_values) > 20:
                    print(f"  ... and {len(unique_values) - 20} more")
        
        print("\n" + "=" * 80)
        if updated > 0:
            print("✓ Migration complete!")
        elif args.dry_run and updates:
            print("✓ Dry run complete - no changes made")
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
