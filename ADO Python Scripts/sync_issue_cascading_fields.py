#!/usr/bin/env python3
"""
Sync Issue Cascading Fields from Related Work Items

Periodically run this script to ensure Issue cascading fields (Version, Date)
are in sync with their related Bug (for Bug Issues) or Feature (for ER Issues).

Requirements:
  pip install azure-devops

Usage:
  export AZURE_DEVOPS_PAT="your-pat-here"
  
  # Interactive mode (default)
  python3 sync_issue_cascading_fields.py
  
  # Dry run (show what would be updated)
  python3 sync_issue_cascading_fields.py --dry-run
  
  # Auto-sync empty fields without prompting
  python3 sync_issue_cascading_fields.py --auto-empty
  
  # Auto-sync all differences without prompting
  python3 sync_issue_cascading_fields.py --auto-all
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation

# Configuration
ORGANIZATION_URL = "https://dev.azure.com/ncryptedcloud"
PROJECT = "eShare"

# Local data file paths (relative to dashboard root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(SCRIPT_DIR)
ALL_ITEMS_PATH = os.path.join(DASHBOARD_DIR, "ALL Items.json")
LINKS_PATH = os.path.join(DASHBOARD_DIR, "WorkItemLinks.json")

# Setup logging with timestamped filename
LOG_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")
LOG_FILENAME = f"sync_issue_cascading_fields_{LOG_TIMESTAMP}.log"
LOG_PATH = os.path.join(SCRIPT_DIR, LOG_FILENAME)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH),
    ]
)
logger = logging.getLogger(__name__)

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
    parser = argparse.ArgumentParser(
        description='Sync Issue cascading fields from related Bug/Feature'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be updated without making changes')
    parser.add_argument('--auto-empty', action='store_true',
                        help='Automatically sync empty Issue fields without prompting')
    parser.add_argument('--auto-all', action='store_true',
                        help='Automatically sync all differences without prompting')
    return parser.parse_args()


def load_local_data():
    """Load work items and links from local JSON files"""
    print("Loading local data files...")
    
    if not os.path.exists(ALL_ITEMS_PATH):
        print(f"ERROR: {ALL_ITEMS_PATH} not found")
        print("Please run ./copy-data-files.sh first")
        sys.exit(1)
    
    if not os.path.exists(LINKS_PATH):
        print(f"ERROR: {LINKS_PATH} not found")
        print("Please run ./copy-data-files.sh first")
        sys.exit(1)
    
    with open(ALL_ITEMS_PATH) as f:
        items = json.load(f)
    
    with open(LINKS_PATH) as f:
        links = json.load(f)
    
    print(f"  Loaded {len(items)} work items")
    print(f"  Loaded {len(links)} links")
    
    return items, links


def build_related_map(links):
    """Build a map of related work items"""
    related_map = {}
    for link in links:
        source = link.get('source')
        target = link.get('target')
        link_type = link.get('type', '')
        
        if link_type == 'Related':
            if source not in related_map:
                related_map[source] = []
            related_map[source].append(target)
            if target not in related_map:
                related_map[target] = []
            related_map[target].append(source)
    
    return related_map


def analyze_issues(items, related_map, ticket_category, related_type):
    """Analyze Issues of a specific category and their related items"""
    items_by_id = {i['id']: i for i in items}
    
    issues = [i for i in items if i.get('type') == 'Issue' 
              and i.get('ticketCategory') == ticket_category]
    
    results = {
        'same': [],           # Both version and date match
        'version_empty': [],  # Issue version empty, related has value
        'date_empty': [],     # Issue date empty, related has value
        'version_diff': [],   # Both have values but different
        'date_diff': [],      # Both have values but different
        'no_related': [],     # No related item found
    }
    
    for issue in issues:
        issue_id = issue['id']
        related_ids = related_map.get(issue_id, [])
        
        # Find related item of the specified type
        related_item = None
        for rid in related_ids:
            item = items_by_id.get(rid)
            if item and item.get('type') == related_type:
                related_item = item
                break
        
        if not related_item:
            results['no_related'].append(issue)
            continue
        
        issue_ver = issue.get('cascadingVersion') or ''
        issue_date = issue.get('cascadingDate') or ''
        related_ver = related_item.get('cascadingVersion') or ''
        related_date = related_item.get('cascadingDate') or ''
        
        record = {
            'issue': issue,
            'related': related_item,
            'issue_ver': issue_ver,
            'issue_date': issue_date,
            'related_ver': related_ver,
            'related_date': related_date,
        }
        
        ver_status = 'same'
        date_status = 'same'
        
        # Check version
        if not issue_ver and related_ver:
            ver_status = 'empty'
            results['version_empty'].append(record)
        elif issue_ver and related_ver and issue_ver != related_ver:
            ver_status = 'diff'
            results['version_diff'].append(record)
        
        # Check date
        if not issue_date and related_date:
            date_status = 'empty'
            results['date_empty'].append(record)
        elif issue_date and related_date and issue_date != related_date:
            date_status = 'diff'
            results['date_diff'].append(record)
        
        # If both match (including both empty)
        if ver_status == 'same' and date_status == 'same':
            results['same'].append(record)
    
    return results


def print_analysis(results, ticket_category, related_type):
    """Print analysis results"""
    total_with_related = (len(results['same']) + len(results['version_empty']) + 
                          len(results['date_empty']) + len(results['version_diff']) + 
                          len(results['date_diff']))
    # Deduplicate - issues can appear in multiple categories
    issues_with_diff = set()
    for r in results['version_empty'] + results['date_empty'] + results['version_diff'] + results['date_diff']:
        issues_with_diff.add(r['issue']['id'])
    
    print(f"\n{'='*80}")
    print(f"{ticket_category.upper()} ISSUES vs RELATED {related_type.upper()}S")
    print(f"{'='*80}")
    
    print(f"\nTotal {ticket_category} Issues: {total_with_related + len(results['no_related'])}")
    print(f"  With related {related_type}: {total_with_related}")
    print(f"  No related {related_type}: {len(results['no_related'])}")
    
    print(f"\nSync Status (of {total_with_related} with related {related_type}):")
    print(f"  ✓ All fields match: {len(results['same'])}")
    print(f"  ⚠ Issue Version empty (can copy): {len(results['version_empty'])}")
    print(f"  ⚠ Issue Date empty (can copy): {len(results['date_empty'])}")
    print(f"  ✗ Version differs (would overwrite): {len(results['version_diff'])}")
    print(f"  ✗ Date differs (would overwrite): {len(results['date_diff'])}")


def print_differences_table(results, related_type):
    """Print table of differences"""
    # Collect all issues with any difference
    all_diffs = {}
    
    for r in results['version_empty']:
        issue_id = r['issue']['id']
        if issue_id not in all_diffs:
            all_diffs[issue_id] = r.copy()
            all_diffs[issue_id]['ver_status'] = 'empty'
            all_diffs[issue_id]['date_status'] = 'same'
        else:
            all_diffs[issue_id]['ver_status'] = 'empty'
    
    for r in results['date_empty']:
        issue_id = r['issue']['id']
        if issue_id not in all_diffs:
            all_diffs[issue_id] = r.copy()
            all_diffs[issue_id]['ver_status'] = 'same'
            all_diffs[issue_id]['date_status'] = 'empty'
        else:
            all_diffs[issue_id]['date_status'] = 'empty'
    
    for r in results['version_diff']:
        issue_id = r['issue']['id']
        if issue_id not in all_diffs:
            all_diffs[issue_id] = r.copy()
            all_diffs[issue_id]['ver_status'] = 'diff'
            all_diffs[issue_id]['date_status'] = 'same'
        else:
            all_diffs[issue_id]['ver_status'] = 'diff'
    
    for r in results['date_diff']:
        issue_id = r['issue']['id']
        if issue_id not in all_diffs:
            all_diffs[issue_id] = r.copy()
            all_diffs[issue_id]['ver_status'] = 'same'
            all_diffs[issue_id]['date_status'] = 'diff'
        else:
            all_diffs[issue_id]['date_status'] = 'diff'
    
    if not all_diffs:
        print("\n  No differences found!")
        return
    
    print(f"\n  Differences Table ({len(all_diffs)} Issues):")
    print(f"  {'Issue':<8} {related_type:<8} {'Issue Ver':<14} {f'{related_type} Ver':<14} {'Issue Date':<12} {f'{related_type} Date':<12} Status")
    print(f"  {'-'*8} {'-'*8} {'-'*14} {'-'*14} {'-'*12} {'-'*12} {'-'*12}")
    
    for issue_id in sorted(all_diffs.keys()):
        r = all_diffs[issue_id]
        ver_mark = '←COPY' if r['ver_status'] == 'empty' else ('≠DIFF' if r['ver_status'] == 'diff' else '')
        date_mark = '←COPY' if r['date_status'] == 'empty' else ('≠DIFF' if r['date_status'] == 'diff' else '')
        status = f"{ver_mark} {date_mark}".strip()
        
        print(f"  {r['issue']['id']:<8} {r['related']['id']:<8} "
              f"{r['issue_ver'] or '(empty)':<14} {r['related_ver'] or '(empty)':<14} "
              f"{r['issue_date'] or '(empty)':<12} {r['related_date'] or '(empty)':<12} {status}")


def get_updates_to_apply(results, sync_empty=False, sync_diff=False, related_type=''):
    """Build list of updates to apply"""
    updates = []
    
    if sync_empty:
        for r in results['version_empty']:
            updates.append({
                'issue_id': r['issue']['id'],
                'field': 'Custom.CascadingVersion',
                'old_value': r['issue_ver'] or '(empty)',
                'new_value': r['related_ver'],
                'type': 'empty',
                'related_type': related_type,
                'related_id': r['related']['id']
            })
        
        for r in results['date_empty']:
            updates.append({
                'issue_id': r['issue']['id'],
                'field': 'Custom.CascadingDate',
                'old_value': r['issue_date'] or '(empty)',
                'new_value': r['related_date'],
                'type': 'empty',
                'related_type': related_type,
                'related_id': r['related']['id']
            })
    
    if sync_diff:
        for r in results['version_diff']:
            updates.append({
                'issue_id': r['issue']['id'],
                'field': 'Custom.CascadingVersion',
                'old_value': r['issue_ver'],
                'new_value': r['related_ver'],
                'type': 'overwrite',
                'related_type': related_type,
                'related_id': r['related']['id']
            })
        
        for r in results['date_diff']:
            updates.append({
                'issue_id': r['issue']['id'],
                'field': 'Custom.CascadingDate',
                'old_value': r['issue_date'],
                'new_value': r['related_date'],
                'type': 'overwrite',
                'related_type': related_type,
                'related_id': r['related']['id']
            })
    
    # Deduplicate by issue_id + field
    seen = set()
    deduped = []
    for u in updates:
        key = (u['issue_id'], u['field'])
        if key not in seen:
            seen.add(key)
            deduped.append(u)
    
    return deduped


def apply_updates(updates, dry_run=False):
    """Apply updates to ADO"""
    if not updates:
        print("\n  No updates to apply.")
        return 0, []
    
    if dry_run:
        print(f"\n  [DRY RUN] Would update {len(updates)} fields:")
        for u in updates[:20]:
            print(f"    Issue {u['issue_id']}: {u['field']} = '{u['new_value']}' (was: '{u['old_value']}')")
        if len(updates) > 20:
            print(f"    ... and {len(updates) - 20} more")
        return 0, []
    
    print(f"\n  Applying {len(updates)} updates...")
    
    # Group updates by issue_id
    updates_by_issue = {}
    for u in updates:
        if u['issue_id'] not in updates_by_issue:
            updates_by_issue[u['issue_id']] = []
        updates_by_issue[u['issue_id']].append(u)
    
    updated = 0
    failed = []
    
    for issue_id, issue_updates in updates_by_issue.items():
        try:
            patch_doc = []
            for u in issue_updates:
                patch_doc.append(JsonPatchOperation(
                    op='add',
                    path=f"/fields/{u['field']}",
                    value=u['new_value']
                ))
            
            wit_client.update_work_item(
                document=patch_doc,
                id=issue_id,
                project=PROJECT
            )
            
            updated += len(issue_updates)
            fields_updated = ', '.join(u['field'].split('.')[-1] for u in issue_updates)
            print(f"    ✓ Issue {issue_id}: {fields_updated}")
            
            # Log each update
            for u in issue_updates:
                logger.info(f"UPDATED | Issue {issue_id} | {u['field']} | '{u['old_value']}' -> '{u['new_value']}' | from {u['related_type']} {u['related_id']}")
            
        except Exception as e:
            for u in issue_updates:
                failed.append({
                    'issue_id': issue_id,
                    'field': u['field'],
                    'value': u['new_value'],
                    'error': str(e)
                })
                logger.error(f"FAILED | Issue {issue_id} | {u['field']} | '{u['new_value']}' | Error: {e}")
            print(f"    ✗ Issue {issue_id}: {e}")
    
    return updated, failed


def prompt_user_action():
    """Prompt user for what action to take"""
    print("\n" + "-" * 40)
    print("What would you like to do?")
    print("  a) Copy ALL (both empty and different values)")
    print("  b) Copy ONLY different values (overwrite existing)")
    print("  c) Copy ONLY empty values (safe, no overwrites)")
    print("  d) Do nothing")
    print("-" * 40)
    
    while True:
        choice = input("Enter choice (a/b/c/d): ").strip().lower()
        if choice in ['a', 'b', 'c', 'd']:
            return choice
        print("Invalid choice. Please enter a, b, c, or d.")


def process_category(items, related_map, ticket_category, related_type, args):
    """Process a category of Issues"""
    results = analyze_issues(items, related_map, ticket_category, related_type)
    
    print_analysis(results, ticket_category, related_type)
    print_differences_table(results, related_type)
    
    # Check if any updates needed
    has_empty = len(results['version_empty']) > 0 or len(results['date_empty']) > 0
    has_diff = len(results['version_diff']) > 0 or len(results['date_diff']) > 0
    
    if not has_empty and not has_diff:
        print(f"\n  ✓ All {ticket_category} Issues are in sync with their related {related_type}s!")
        return 0, []
    
    # Determine action
    if args.auto_all:
        sync_empty = True
        sync_diff = True
        print(f"\n  [AUTO-ALL] Syncing all differences...")
    elif args.auto_empty:
        sync_empty = True
        sync_diff = False
        print(f"\n  [AUTO-EMPTY] Syncing empty fields only...")
    elif args.dry_run:
        sync_empty = True
        sync_diff = True
    else:
        choice = prompt_user_action()
        if choice == 'a':
            sync_empty = True
            sync_diff = True
        elif choice == 'b':
            sync_empty = False
            sync_diff = True
        elif choice == 'c':
            sync_empty = True
            sync_diff = False
        else:  # d
            print("\n  Skipping...")
            return 0, []
    
    updates = get_updates_to_apply(results, sync_empty, sync_diff, related_type)
    
    if updates and not args.dry_run:
        confirm = input(f"\n  Confirm updating {len(updates)} fields? (yes/no): ")
        if confirm.lower() != 'yes':
            print("  Cancelled.")
            return 0, []
    
    updated, failed = apply_updates(updates, args.dry_run)
    return updated, failed


def main():
    args = parse_args()
    
    # Log session start
    logger.info("=" * 60)
    logger.info("SYNC SESSION STARTED")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    if args.auto_empty:
        logger.info("Auto-mode: empty fields only")
    if args.auto_all:
        logger.info("Auto-mode: all differences")
    logger.info("=" * 60)
    
    print("=" * 80)
    print("SYNC ISSUE CASCADING FIELDS")
    print("=" * 80)
    print(f"Log file: {LOG_FILENAME}")
    if args.dry_run:
        print("[DRY RUN MODE - No changes will be made]")
    if args.auto_empty:
        print("[AUTO-EMPTY MODE - Will sync empty fields without prompting]")
    if args.auto_all:
        print("[AUTO-ALL MODE - Will sync all differences without prompting]")
    
    # Load data
    items, links = load_local_data()
    related_map = build_related_map(links)
    
    total_updated = 0
    total_failed = []
    
    # Process Bug Issues
    updated, failed = process_category(items, related_map, 'Bug', 'Bug', args)
    total_updated += updated
    total_failed.extend(failed)
    
    # Process Enhancement Request Issues
    updated, failed = process_category(items, related_map, 'Enhancement Request', 'Feature', args)
    total_updated += updated
    total_failed.extend(failed)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Count orphans
    bug_issues = [i for i in items if i.get('type') == 'Issue' and i.get('ticketCategory') == 'Bug']
    er_issues = [i for i in items if i.get('type') == 'Issue' and i.get('ticketCategory') == 'Enhancement Request']
    
    items_by_id = {i['id']: i for i in items}
    
    bug_orphans = 0
    for issue in bug_issues:
        related_ids = related_map.get(issue['id'], [])
        has_related_bug = any(items_by_id.get(rid, {}).get('type') == 'Bug' for rid in related_ids)
        if not has_related_bug:
            bug_orphans += 1
    
    er_orphans = 0
    for issue in er_issues:
        related_ids = related_map.get(issue['id'], [])
        has_related_feature = any(items_by_id.get(rid, {}).get('type') == 'Feature' for rid in related_ids)
        if not has_related_feature:
            er_orphans += 1
    
    print(f"\nOrphan Issues (no related item):")
    print(f"  Bug Issues without related Bug: {bug_orphans}")
    print(f"  Enhancement Request Issues without related Feature: {er_orphans}")
    
    if not args.dry_run:
        print(f"\nUpdates Applied:")
        print(f"  Successfully updated: {total_updated} fields")
        print(f"  Failed: {len(total_failed)}")
        
        if total_failed:
            print("\nFailed updates:")
            for f in total_failed[:10]:
                print(f"  Issue {f['issue_id']}: {f['field']} - {f['error']}")
            if len(total_failed) > 10:
                print(f"  ... and {len(total_failed) - 10} more")
    
    # Log session summary
    logger.info("=" * 60)
    logger.info("SESSION SUMMARY")
    logger.info(f"Bug Issues without related Bug: {bug_orphans}")
    logger.info(f"Enhancement Request Issues without related Feature: {er_orphans}")
    if not args.dry_run:
        logger.info(f"Successfully updated: {total_updated} fields")
        logger.info(f"Failed: {len(total_failed)}")
    else:
        logger.info("DRY RUN - No changes made")
    logger.info("=" * 60)
    
    print("\n" + "=" * 80)
    if total_updated > 0:
        print("✓ Sync complete!")
        print(f"\nLog file: {LOG_PATH}")
        print("\nNOTE: Run ./copy-data-files.sh to refresh local data after ADO updates.")
    elif args.dry_run:
        print("✓ Dry run complete - no changes made")
        print(f"\nLog file: {LOG_PATH}")
    else:
        print("✓ No updates needed")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
