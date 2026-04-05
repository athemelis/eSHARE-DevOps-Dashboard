#!/usr/bin/env python3
"""
Sync tags between linked Issue and Feature/Bug work items.

Rules:
  1. Issue (ER) <-> Feature (Related):
     - Copy CS tags (CS:*) from Issue to Feature
     - Copy OKR tags (1:*, 2:*, 3:*, 4:*) from Feature to Issue
  2. Issue (Bug) <-> Bug (Related):
     - Copy architecture tags from Bug to Issue

Only processes items with a Related link (not Parent/Child).
Checks for existing tags before adding — no duplicates.

Usage:
    cd eSHARE-DevOps-Dashboard
    python3 "ADO Python Scripts/sync_tags_between_linked_items.py"
    python3 "ADO Python Scripts/sync_tags_between_linked_items.py" --apply
    python3 "ADO Python Scripts/sync_tags_between_linked_items.py" --state Active
    python3 "ADO Python Scripts/sync_tags_between_linked_items.py" --verbose

Data source: Local JSON files (ALL Items.json, WorkItemLinks.json)
Requires: AZURE_DEVOPS_PAT environment variable (only with --apply)
"""

import json
import os
import sys
import argparse
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ITEMS_FILE = os.path.join(REPO_ROOT, 'ALL Items.json')
LINKS_FILE = os.path.join(REPO_ROOT, 'WorkItemLinks.json')

ADO_ORG = 'https://dev.azure.com/ncryptedcloud'
ADO_PROJECT = 'eShare'
ADO_BASE_URL = f'{ADO_ORG}/{ADO_PROJECT}/_workitems/edit'

# Tag prefix patterns
CS_PREFIXES = ('CS:',)
OKR_PREFIXES = ('1:', '2:', '3:', '4:')
ARCH_PREFIXES = ('UI:', 'CWP:', 'SCG:', 'ESG:', 'Analytics:', 'Utilities:', 'Infra:')


def load_data():
    """Load work items and links from local JSON files."""
    for path, name in [(ITEMS_FILE, 'ALL Items.json'), (LINKS_FILE, 'WorkItemLinks.json')]:
        if not os.path.exists(path):
            print(f"ERROR: {path} not found. Run ./copy-data-files.sh first.")
            sys.exit(1)

    with open(ITEMS_FILE, 'r') as f:
        items = json.load(f)
    with open(LINKS_FILE, 'r') as f:
        links = json.load(f)
    return items, links


def parse_tags(tag_string):
    """Parse semicolon-separated tag string into a set of trimmed tags."""
    if not tag_string:
        return set()
    return {t.strip() for t in tag_string.split('; ') if t.strip()}


def tags_matching(tags, prefixes):
    """Return tags that match any of the given prefixes."""
    return {t for t in tags if any(t.startswith(p) for p in prefixes)}


def build_related_link_map(links, item_map):
    """Build map of source_id -> list of Related target IDs, filtering to valid items."""
    link_map = defaultdict(set)
    for link in links:
        if link.get('type') != 'Related':
            continue
        source = link.get('source')
        target = link.get('target')
        if source and target and source in item_map and target in item_map:
            link_map[source].add(target)
            link_map[target].add(source)
    return link_map


def compute_tag_updates(items, links, state_filter=None):
    """
    Compute all tag updates needed. Returns list of:
      {'id': int, 'title': str, 'type': str, 'current_tags': set, 'add_tags': set,
       'source_id': int, 'source_type': str, 'rule': str}
    """
    item_map = {i['id']: i for i in items}
    related_map = build_related_link_map(links, item_map)

    updates = []
    in_sync = {'er_to_feature': 0, 'feature_to_er': 0, 'bug_to_issue': 0}
    needs_update = {'er_to_feature': 0, 'feature_to_er': 0, 'bug_to_issue': 0}

    # Filter Issues
    issues = [i for i in items if i.get('type') == 'Issue']
    if state_filter:
        sf = state_filter.lower()
        if sf == 'active':
            issues = [i for i in issues if (i.get('state') or '').lower() not in ('done', 'closed')]
        else:
            issues = [i for i in issues if (i.get('state') or '').lower() == sf]

    for issue in issues:
        issue_id = issue['id']
        issue_tags = parse_tags(issue.get('tags'))
        category = issue.get('ticketCategory')
        related_ids = related_map.get(issue_id, set())

        if category == 'Enhancement Request':
            # Find Related Features
            for rid in related_ids:
                related_item = item_map.get(rid)
                if not related_item or related_item.get('type') != 'Feature':
                    continue

                feature_tags = parse_tags(related_item.get('tags'))

                # Rule 1a: Copy CS tags from Issue (ER) -> Feature
                cs_tags = tags_matching(issue_tags, CS_PREFIXES)
                cs_to_add = cs_tags - feature_tags
                if cs_to_add:
                    updates.append({
                        'id': rid,
                        'title': related_item.get('title', ''),
                        'type': 'Feature',
                        'current_tags': feature_tags,
                        'add_tags': cs_to_add,
                        'source_id': issue_id,
                        'source_type': 'Issue (ER)',
                        'rule': 'CS tags from ER → Feature',
                    })
                    needs_update['er_to_feature'] += 1
                else:
                    if cs_tags:
                        in_sync['er_to_feature'] += 1

                # Rule 1b: Copy OKR tags from Feature -> Issue (ER)
                okr_tags = tags_matching(feature_tags, OKR_PREFIXES)
                okr_to_add = okr_tags - issue_tags
                if okr_to_add:
                    updates.append({
                        'id': issue_id,
                        'title': issue.get('title', ''),
                        'type': 'Issue (ER)',
                        'current_tags': issue_tags,
                        'add_tags': okr_to_add,
                        'source_id': rid,
                        'source_type': 'Feature',
                        'rule': 'OKR tags from Feature → ER',
                    })
                    needs_update['feature_to_er'] += 1
                else:
                    if okr_tags:
                        in_sync['feature_to_er'] += 1

        elif category == 'Bug':
            # Find Related Bugs
            for rid in related_ids:
                related_item = item_map.get(rid)
                if not related_item or related_item.get('type') != 'Bug':
                    continue

                bug_tags = parse_tags(related_item.get('tags'))

                # Rule 2: Copy architecture tags from Bug -> Issue (Bug)
                arch_tags = tags_matching(bug_tags, ARCH_PREFIXES)
                arch_to_add = arch_tags - issue_tags
                if arch_to_add:
                    updates.append({
                        'id': issue_id,
                        'title': issue.get('title', ''),
                        'type': 'Issue (Bug)',
                        'current_tags': issue_tags,
                        'add_tags': arch_to_add,
                        'source_id': rid,
                        'source_type': 'Bug',
                        'rule': 'Arch tags from Bug → Issue',
                    })
                    needs_update['bug_to_issue'] += 1
                else:
                    if arch_tags:
                        in_sync['bug_to_issue'] += 1

    return updates, in_sync, needs_update


def apply_updates(updates):
    """Apply tag updates to Azure DevOps via REST API."""
    pat = os.environ.get('AZURE_DEVOPS_PAT')
    if not pat:
        print("ERROR: AZURE_DEVOPS_PAT environment variable not set.")
        print("       Set it with: export AZURE_DEVOPS_PAT='your-pat-here'")
        sys.exit(1)

    import requests
    from requests.auth import HTTPBasicAuth

    auth = HTTPBasicAuth('', pat)
    api_url = f'{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workitems'
    headers = {'Content-Type': 'application/json-patch+json'}

    # Deduplicate: merge add_tags for the same target item
    merged = {}
    for u in updates:
        wid = u['id']
        if wid not in merged:
            merged[wid] = {
                'id': wid,
                'title': u['title'],
                'type': u['type'],
                'current_tags': u['current_tags'],
                'add_tags': set(u['add_tags']),
            }
        else:
            merged[wid]['add_tags'] |= u['add_tags']

    success = 0
    failed = 0
    total = len(merged)

    for idx, (wid, entry) in enumerate(merged.items(), 1):
        new_tags = entry['current_tags'] | entry['add_tags']
        tag_string = '; '.join(sorted(new_tags))

        patch = [
            {
                'op': 'replace',
                'path': '/fields/System.Tags',
                'value': tag_string
            }
        ]

        try:
            resp = requests.patch(
                f'{api_url}/{wid}?api-version=7.0',
                json=patch,
                auth=auth,
                headers=headers
            )
            if resp.status_code == 200:
                success += 1
                adding = ', '.join(sorted(entry['add_tags']))
                print(f"  [{idx}/{total}] ✅ #{wid} ({entry['type']}): added [{adding}]")
            else:
                failed += 1
                print(f"  [{idx}/{total}] ❌ #{wid}: HTTP {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            failed += 1
            print(f"  [{idx}/{total}] ❌ #{wid}: {e}")

    return success, failed


def print_report(updates, in_sync, needs_update, verbose=False):
    """Print tag sync report."""
    print(f"\n{'='*70}")
    print(f"  TAG SYNC REPORT")
    print(f"{'='*70}")

    rules = [
        ('CS tags: Issue (ER) → Feature', 'er_to_feature'),
        ('OKR tags: Feature → Issue (ER)', 'feature_to_er'),
        ('Arch tags: Bug → Issue (Bug)', 'bug_to_issue'),
    ]

    for label, key in rules:
        sync = in_sync[key]
        need = needs_update[key]
        total = sync + need
        status = '✅' if need == 0 else '⚠️ '
        print(f"\n  {status} {label}")
        print(f"     Total pairs with tags:  {total}")
        print(f"     ✅ Already in sync:     {sync}")
        print(f"     📝 Need update:         {need}")

    total_sync = sum(in_sync.values())
    total_need = sum(needs_update.values())

    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total pairs checked:  {total_sync + total_need}")
    print(f"  ✅ In sync:           {total_sync}")
    print(f"  📝 Need update:       {total_need}")

    if updates and verbose:
        print(f"\n{'='*70}")
        print(f"  UPDATES NEEDED (detail)")
        print(f"{'='*70}")
        for u in sorted(updates, key=lambda x: (x['rule'], x['id'])):
            adding = ', '.join(sorted(u['add_tags']))
            print(f"\n  {u['rule']}")
            print(f"    Target: #{u['id']} ({u['type']}) — {u['title'][:60]}")
            print(f"    Source: #{u['source_id']} ({u['source_type']})")
            print(f"    Adding: [{adding}]")
            print(f"    {ADO_BASE_URL}/{u['id']}")

    if updates and not verbose:
        print(f"\n  💡 Run with --verbose to see details of each update")

    if total_need > 0:
        print(f"\n  💡 Run with --apply to push tag updates to Azure DevOps")
    print()


def main():
    parser = argparse.ArgumentParser(description='Sync tags between linked Issue and Feature/Bug items')
    parser.add_argument('--state', help='Filter Issues by state: Active (excludes Done/Closed), Done, Closed, or All (default)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show details of each update needed')
    parser.add_argument('--apply', action='store_true', help='Apply tag updates to Azure DevOps (requires AZURE_DEVOPS_PAT)')
    args = parser.parse_args()

    print("Loading data files...")
    items, links = load_data()
    print(f"  Loaded {len(items)} work items and {len(links)} links")

    state_label = f" (state: {args.state})" if args.state else ""
    print(f"\nComputing tag sync status{state_label}...")

    updates, in_sync, needs_update = compute_tag_updates(items, links, state_filter=args.state)

    print_report(updates, in_sync, needs_update, verbose=args.verbose)

    if args.apply:
        if not updates:
            print("Nothing to update — all tags are in sync.")
            return

        total_need = sum(needs_update.values())
        print(f"Applying {total_need} tag updates to Azure DevOps...")
        success, failed = apply_updates(updates)
        print(f"\n  Done: {success} succeeded, {failed} failed")
        if success > 0:
            print("  ⚠️  Run ./copy-data-files.sh to refresh local data after updates")


if __name__ == '__main__':
    main()
