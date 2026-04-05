#!/usr/bin/env python3
"""
Audit Issue work item links to validate relationship rules:
  - Issues (Enhancement Request) should have a Related link to a Feature
  - Issues (Bug) should have a Related link to a Bug

Reports issues that:
  1. Have no link to the expected work item type
  2. Have a link but with wrong link type (e.g., Parent/Child instead of Related)

Usage:
    cd eSHARE-DevOps-Dashboard
    python3 "ADO Python Scripts/audit_issue_links.py"
    python3 "ADO Python Scripts/audit_issue_links.py" --state Active
    python3 "ADO Python Scripts/audit_issue_links.py" --verbose

Data source: Local JSON files (ALL Items.json, WorkItemLinks.json)
"""

import json
import os
import sys
import argparse
from collections import defaultdict

# Paths relative to repo root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ITEMS_FILE = os.path.join(REPO_ROOT, 'ALL Items.json')
LINKS_FILE = os.path.join(REPO_ROOT, 'WorkItemLinks.json')

ADO_BASE_URL = 'https://dev.azure.com/ncryptedcloud/eShare/_workitems/edit'


def load_data():
    """Load work items and links from local JSON files."""
    if not os.path.exists(ITEMS_FILE):
        print(f"ERROR: {ITEMS_FILE} not found. Run ./copy-data-files.sh first.")
        sys.exit(1)
    if not os.path.exists(LINKS_FILE):
        print(f"ERROR: {LINKS_FILE} not found. Run ./copy-data-files.sh first.")
        sys.exit(1)

    with open(ITEMS_FILE, 'r') as f:
        items = json.load(f)
    with open(LINKS_FILE, 'r') as f:
        links = json.load(f)

    return items, links


def build_item_map(items):
    """Build a map of item ID -> item for quick lookup."""
    return {item['id']: item for item in items}


def build_link_map(links):
    """Build a map of source ID -> list of {target, type} for all links."""
    link_map = defaultdict(list)
    for link in links:
        source = link.get('source')
        target = link.get('target')
        link_type = link.get('type', '')
        if source and target:
            link_map[source].append({'target': target, 'type': link_type})
            # Also add reverse direction (links are directional in ADO)
            link_map[target].append({'target': source, 'type': link_type})
    return link_map


def audit_issues(items, links, state_filter=None, verbose=False):
    """Audit Issue work items for correct link relationships."""
    item_map = build_item_map(items)
    link_map = build_link_map(links)

    # Filter to Issues only
    issues = [i for i in items if i.get('type') == 'Issue']
    if state_filter:
        state_lower = state_filter.lower()
        issues = [i for i in issues if (i.get('state') or '').lower() == state_lower]

    # Separate by ticket category
    er_issues = [i for i in issues if i.get('ticketCategory') == 'Enhancement Request']
    bug_issues = [i for i in issues if i.get('ticketCategory') == 'Bug']
    other_issues = [i for i in issues if i.get('ticketCategory') not in ('Enhancement Request', 'Bug')]

    # Audit Enhancement Requests -> should have Related Feature
    er_results = audit_category(er_issues, item_map, link_map, 'Feature', verbose)

    # Audit Bug Issues -> should have Related Bug
    bug_results = audit_category(bug_issues, item_map, link_map, 'Bug', verbose)

    return er_issues, er_results, bug_issues, bug_results, other_issues


def audit_category(issues, item_map, link_map, expected_type, verbose):
    """Audit a category of issues for correct link to expected work item type."""
    results = {
        'no_link': [],        # No link to expected type at all
        'wrong_type': [],     # Has link to expected type but not Related
        'correct': [],        # Has Related link to expected type
    }

    for issue in issues:
        issue_id = issue['id']
        issue_links = link_map.get(issue_id, [])

        # Find all links to the expected work item type
        links_to_expected = []
        for link in issue_links:
            target_item = item_map.get(link['target'])
            if target_item and target_item.get('type') == expected_type:
                links_to_expected.append({
                    'target_id': link['target'],
                    'target_title': target_item.get('title', ''),
                    'target_state': target_item.get('state', ''),
                    'link_type': link['type']
                })

        if not links_to_expected:
            results['no_link'].append({
                'id': issue_id,
                'title': issue.get('title', ''),
                'state': issue.get('state', ''),
                'assignedTo': (issue.get('assignedTo') or '').split(' <')[0],
            })
        else:
            has_related = any(l['link_type'] == 'Related' for l in links_to_expected)
            wrong_type_links = [l for l in links_to_expected if l['link_type'] != 'Related']

            if has_related:
                results['correct'].append({
                    'id': issue_id,
                    'title': issue.get('title', ''),
                    'links': links_to_expected
                })
            else:
                results['wrong_type'].append({
                    'id': issue_id,
                    'title': issue.get('title', ''),
                    'state': issue.get('state', ''),
                    'assignedTo': (issue.get('assignedTo') or '').split(' <')[0],
                    'links': wrong_type_links
                })

    return results


def print_report(label, expected_type, total, results, verbose):
    """Print audit report for a category."""
    no_link = results['no_link']
    wrong_type = results['wrong_type']
    correct = results['correct']

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"  Expected: Related link to a {expected_type}")
    print(f"{'='*70}")
    print(f"  Total:            {total:>5}")
    print(f"  ✅ Correct:       {len(correct):>5}  (has Related {expected_type})")
    print(f"  ❌ No link:       {len(no_link):>5}  (no {expected_type} linked at all)")
    print(f"  ⚠️  Wrong type:    {len(wrong_type):>5}  (has {expected_type} but not as Related)")
    print()

    if no_link:
        print(f"  --- Issues with NO {expected_type} link ({len(no_link)}) ---")
        for item in sorted(no_link, key=lambda x: x['id']):
            print(f"    #{item['id']:<6} {item['state']:<12} {item['assignedTo']:<25} {item['title'][:60]}")
            if verbose:
                print(f"           {ADO_BASE_URL}/{item['id']}")
        print()

    if wrong_type:
        print(f"  --- Issues with WRONG link type to {expected_type} ({len(wrong_type)}) ---")
        for item in sorted(wrong_type, key=lambda x: x['id']):
            link_desc = ', '.join(f"#{l['target_id']} ({l['link_type']})" for l in item['links'])
            print(f"    #{item['id']:<6} {item['state']:<12} {item['assignedTo']:<25} {item['title'][:50]}")
            print(f"           Links: {link_desc}")
            if verbose:
                print(f"           {ADO_BASE_URL}/{item['id']}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Audit Issue work item links')
    parser.add_argument('--state', help='Filter by state (e.g., Active, New, Closed)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show ADO links for each item')
    args = parser.parse_args()

    print("Loading data files...")
    items, links = load_data()
    print(f"  Loaded {len(items)} work items and {len(links)} links")

    state_label = f" (state: {args.state})" if args.state else ""
    print(f"\nAuditing Issue work item links{state_label}...")

    er_issues, er_results, bug_issues, bug_results, other_issues = \
        audit_issues(items, links, state_filter=args.state, verbose=args.verbose)

    print_report(
        f"Enhancement Request Issues{state_label}",
        "Feature",
        len(er_issues),
        er_results,
        args.verbose
    )

    print_report(
        f"Bug Issues{state_label}",
        "Bug",
        len(bug_issues),
        bug_results,
        args.verbose
    )

    if other_issues:
        print(f"\n  ℹ️  {len(other_issues)} Issues with other/missing ticket categories (skipped)")

    # Summary
    total_issues = len(er_issues) + len(bug_issues)
    total_problems = len(er_results['no_link']) + len(er_results['wrong_type']) + \
                     len(bug_results['no_link']) + len(bug_results['wrong_type'])
    total_correct = len(er_results['correct']) + len(bug_results['correct'])

    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total Issues audited:  {total_issues}")
    print(f"  ✅ Correctly linked:   {total_correct}")
    print(f"  ❌ Problems found:     {total_problems}")
    print()


if __name__ == '__main__':
    main()
