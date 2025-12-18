#!/usr/bin/env python3
"""
eShare Dashboard Generator v2
=============================
Generates the final dashboard HTML by injecting work item data from CSV into the template.

SCHEMA VERSION: v45-compatible
This script produces the exact field names expected by the dashboard JavaScript.

Usage:
    python3 generate_dashboard.py [options]

Options:
    -c, --csv PATH        Path to ALL_Items.csv
    -g, --org PATH        Path to Org_Chart.csv
    -t, --templates PATH  Folder containing template part files (default: ./Templates)
    -o, --output PATH     Output HTML file path (default: local directory)
    -p, --publish         Publish to SharePoint instead of local directory
    -h, --help            Show this help message

Workflow:
    1. Generate to local directory for testing:
       python3 generate_dashboard.py

    2. Open local file in browser and validate changes

    3. If good, publish to SharePoint:
       python3 generate_dashboard.py --publish

Examples:
    # Generate to local directory (default - for testing)
    python3 generate_dashboard.py

    # Publish to SharePoint (after validation)
    python3 generate_dashboard.py --publish
    python3 generate_dashboard.py -p

    # Custom output path
    python3 generate_dashboard.py -o ~/Documents/test-dashboard.html

Requirements:
    - pandas
    - Template files: dashboard_v3_part1.html through part4.html (in Templates folder)
"""

import pandas as pd
import json
import re
import os
import sys
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Configuration - Default paths (can be overridden via command line)
DEFAULT_CSV_PATH = '/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ALL Items.csv'
DEFAULT_ORG_CHART_PATH = '/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/Org Chart.csv'
DEFAULT_LINKS_CSV_PATH = '/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/WorkItemLinks.csv'
DEFAULT_TEMPLATE_DIR = './Templates'

# Output paths
LOCAL_OUTPUT_PATH = '/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/eSHARE-DevOps-Dashboard.html'
PUBLISH_OUTPUT_PATH = '/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ᵉShare DevOps Dashboard.html'

CURRENT_VERSION = 98  # Increment this with each code change

# Placeholders that MUST be replaced
PLACEHOLDERS = {
    'WORK_ITEMS_PLACEHOLDER': 'Work items data array',
    'REFRESH_TIMESTAMP_PLACEHOLDER': 'Refresh timestamp string',
    'ORG_CHART_DATA_PLACEHOLDER': 'Org chart data array',
    'CSV_VALIDATION_DATA_PLACEHOLDER': 'CSV validation metadata',
    'WORK_ITEM_LINKS_PLACEHOLDER': 'Work item links data array'
}


def get_refresh_timestamp(csv_path=None):
    """Get refresh timestamp from CSV file's last modified date, formatted for 3 timezones.
    
    If csv_path is provided, uses the file's modification time.
    Otherwise falls back to hardcoded DATA_REFRESH values.
    """
    if csv_path and os.path.exists(csv_path):
        # Get file modification time as UTC
        mod_time = os.path.getmtime(csv_path)
        utc_dt = datetime.fromtimestamp(mod_time, tz=ZoneInfo('UTC'))
        
        # Convert to all three timezones
        athens_dt = utc_dt.astimezone(ZoneInfo('Europe/Athens'))
        boston_dt = utc_dt.astimezone(ZoneInfo('America/New_York'))
        seattle_dt = utc_dt.astimezone(ZoneInfo('America/Los_Angeles'))
        
        # Use Seattle date for the display date (M/D/YYYY format)
        display_date = seattle_dt.strftime("%-m/%-d/%Y")
        
        return f"Refreshed: {display_date} — Athens {athens_dt.strftime('%H:%M')} · Boston {boston_dt.strftime('%H:%M')} · Seattle {seattle_dt.strftime('%H:%M')}"
    else:
        # Fallback to hardcoded values
        seattle_tz = ZoneInfo('America/Los_Angeles')
        dt_str = f"{DATA_REFRESH_DATE} {DATA_REFRESH_TIME}"
        seattle_dt = datetime.strptime(dt_str, "%m/%d/%Y %H:%M").replace(tzinfo=seattle_tz)
        
        athens_dt = seattle_dt.astimezone(ZoneInfo('Europe/Athens'))
        boston_dt = seattle_dt.astimezone(ZoneInfo('America/New_York'))
        
        return f"Refreshed: {DATA_REFRESH_DATE} — Athens {athens_dt.strftime('%H:%M')} · Boston {boston_dt.strftime('%H:%M')} · Seattle {seattle_dt.strftime('%H:%M')}"


def clean_name(val):
    """Remove email addresses from name fields, return None for empty."""
    if pd.isna(val) or str(val).strip() == '':
        return None
    val = str(val)
    val = re.sub(r'\s*<[^>]+>', '', val)
    val = val.strip()
    return val if val else None


def clean_string(val):
    """Clean string value, return None for empty."""
    if pd.isna(val):
        return None
    val = str(val).strip()
    return val if val else None


def process_org_chart(csv_path):
    """
    Process Org_Chart.csv and convert to the orgChartData format.
    
    CSV columns: Lead, Formal Name, Common Name, Team, Status
    
    Output format:
    [
        { lead: 'Name', team: 'Team1 & Team2', members: [{ name: 'Name', team: 'Team', status: 'Status' }] },
        ...
    ]
    """
    if not os.path.exists(csv_path):
        print(f"WARNING: Org chart CSV not found: {csv_path}")
        return []
    
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # Group by Lead
    grouped = {}
    for _, row in df.iterrows():
        lead = clean_string(row.get('Lead'))
        if not lead:
            continue
        
        if lead not in grouped:
            grouped[lead] = {
                'lead': lead,
                'teams': set(),
                'members': []
            }
        
        member_name = clean_string(row.get('Common Name')) or clean_string(row.get('Formal Name'))
        member_team = clean_string(row.get('Team'))
        member_status = clean_string(row.get('Status')) or 'Employed'
        
        if member_name and member_team:
            grouped[lead]['teams'].add(member_team)
            grouped[lead]['members'].append({
                'name': member_name,
                'team': member_team,
                'status': member_status
            })
    
    # Convert to final format with combined team names
    result = []
    for lead, data in grouped.items():
        teams_sorted = sorted(data['teams'])
        team_label = ' & '.join(teams_sorted) if len(teams_sorted) > 1 else (teams_sorted[0] if teams_sorted else 'Unknown')
        
        result.append({
            'lead': data['lead'],
            'team': team_label,
            'members': data['members']
        })
    
    # Sort by lead name for consistent output
    result.sort(key=lambda x: x['lead'])

    return result


def process_work_item_links(csv_path, max_retries=5, retry_delay=5):
    """
    Process WorkItemLinks.csv and convert to a compact format for JavaScript.

    CSV columns: WorkItemLinkSK, SourceWorkItemId, TargetWorkItemId, CreatedDate,
                 DeletedDate, Comment, LinkTypeId, LinkTypeReferenceName, LinkTypeName,
                 LinkTypeIsAcyclic, LinkTypeIsDirectional, AnalyticsUpdatedDate, ProjectSK

    Output format (optimized for JavaScript lookup):
    [
        { source: 1082, target: 2776, type: 'Child', comment: '' },
        { source: 1082, target: 1940, type: 'Related', comment: 'mentioned...' },
        ...
    ]

    We only include forward links (LinkTypeId > 0) to avoid duplicates.
    """
    if not os.path.exists(csv_path):
        print(f"WARNING: WorkItemLinks CSV not found: {csv_path}")
        return []

    print(f"Reading WorkItemLinks CSV: {csv_path}")

    # Retry logic for handling file locks
    df = None
    last_error = None
    for attempt in range(max_retries):
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            break
        except OSError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                print(f"  File locked (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"WARNING: Could not read WorkItemLinks CSV after {max_retries} attempts")
                return []

    print(f"Found {len(df)} link rows")

    # Filter to only forward links (positive LinkTypeId) to avoid duplicates
    # LinkTypeId > 0 = forward direction (Child, Related-Forward)
    # LinkTypeId < 0 = reverse direction (Parent, Related-Reverse) - skip these
    forward_links = df[df['LinkTypeId'] > 0]
    print(f"Filtered to {len(forward_links)} forward links (excluding reverse duplicates)")

    records = []
    for _, row in forward_links.iterrows():
        source_id = int(row['SourceWorkItemId']) if pd.notna(row['SourceWorkItemId']) else None
        target_id = int(row['TargetWorkItemId']) if pd.notna(row['TargetWorkItemId']) else None

        if source_id is None or target_id is None:
            continue

        # Simplify LinkTypeName to just the core type
        link_type_name = str(row.get('LinkTypeName', '')).strip()
        # "Child" stays "Child", "Related" stays "Related"

        comment = clean_string(row.get('Comment', ''))

        records.append({
            'source': source_id,
            'target': target_id,
            'type': link_type_name,
            'comment': comment
        })

    return records


def parse_datetime(val):
    """Parse datetime, return ISO format string or None."""
    if pd.isna(val) or str(val).strip() == '':
        return None
    try:
        val_str = str(val).strip()
        
        # Handle ISO format with timezone (from PA export): 2025-08-02T01:50:47.94Z
        if 'T' in val_str:
            # Remove timezone indicator and fractional seconds for consistent output
            val_str = val_str.rstrip('Z')
            if '.' in val_str:
                val_str = val_str.split('.')[0]
            # Already in ISO format, just return it
            return val_str
        
        # Handle legacy date formats
        for fmt in ['%m/%d/%Y %I:%M:%S %p', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y']:
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            except ValueError:
                continue
        return val_str
    except:
        return None


def parse_date_only(val):
    """Parse date-only fields with timezone adjustment. Returns DATE-ONLY format (no time).

    ADO stores date-only fields (like ClosedDate, TargetDate) as midnight in the
    organization's timezone (Athens). Power Automate exports convert this to UTC,
    which can shift the date back by one day.
    We convert UTC back to Athens timezone to get the intended date.

    Used for: closedDate, targetDate, and any other date-only ADO fields.
    """
    if pd.isna(val) or str(val).strip() == '':
        return None
    try:
        val_str = str(val).strip()

        # Handle ISO format with timezone (from PA export): 2025-10-03T21:00:00Z or 2025-11-11T03:04:24.25Z
        # Convert from UTC to Athens timezone to get the intended date
        if 'T' in val_str and val_str.endswith('Z'):
            from zoneinfo import ZoneInfo
            # Remove trailing Z and any fractional seconds for parsing
            utc_str = val_str.rstrip('Z')
            # Remove fractional seconds if present (e.g., ".25" or ".123456")
            if '.' in utc_str:
                utc_str = utc_str.split('.')[0]
            utc_str += '+00:00'
            utc_dt = datetime.fromisoformat(utc_str)
            # Convert to Athens timezone
            athens_tz = ZoneInfo('Europe/Athens')
            athens_dt = utc_dt.astimezone(athens_tz)
            return athens_dt.strftime('%Y-%m-%d')

        # Handle ISO format without Z (just extract date)
        if 'T' in val_str:
            return val_str.split('T')[0]

        # Handle legacy formats with time component
        for fmt in ['%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %H:%M:%S']:
            try:
                dt = datetime.strptime(val_str, fmt)
                # If time is after noon, likely needs +1 day adjustment (timezone issue)
                if dt.hour >= 12:
                    dt = dt + timedelta(days=1)
                return dt.strftime('%Y-%m-%d')  # DATE-ONLY, no time
            except ValueError:
                continue
        # Just a date
        for fmt in ['%m/%d/%Y', '%Y-%m-%d']:
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.strftime('%Y-%m-%d')  # DATE-ONLY, no time
            except ValueError:
                continue
        return val_str
    except:
        return None


def parse_target_date(val):
    """Parse target date. Wrapper for parse_date_only for backward compatibility."""
    return parse_date_only(val)


def clean_float(val):
    """Convert to float, return None for empty/invalid."""
    if pd.isna(val):
        return None
    try:
        f = float(val)
        return f if f != 0 else None
    except:
        return None


def clean_int(val):
    """Convert to int, return None for empty/invalid."""
    if pd.isna(val):
        return None
    try:
        i = int(float(val))
        return i if i != 0 else None
    except:
        return None


def get_team(area_path):
    """Extract team name from area path."""
    if pd.isna(area_path):
        return 'eShare'
    parts = str(area_path).split('\\')
    return parts[-1] if len(parts) > 1 else 'eShare'


def get_iteration_name(iteration_path):
    """Extract iteration name from iteration path."""
    if pd.isna(iteration_path):
        return None
    parts = str(iteration_path).split('\\')
    return parts[-1] if parts else None


def process_csv(csv_path, max_retries=5, retry_delay=5):
    """Process the CSV and return list of work item records matching v45 schema.

    Includes retry logic to handle file locks from OneDrive/SharePoint sync.
    """
    print(f"Reading CSV: {csv_path}")

    # Retry logic for handling file locks (OneDrive/SharePoint sync)
    df = None
    last_error = None
    for attempt in range(max_retries):
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            break  # Success, exit retry loop
        except OSError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)  # Increasing delay
                print(f"  File locked (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"ERROR: Could not read CSV after {max_retries} attempts")
                raise last_error

    print(f"Found {len(df)} rows, {len(df.columns)} columns")
    
    # Detect which column naming convention is used
    is_new_format = 'System.Id' in df.columns
    print(f"Column format: {'ADO Field Names (from PA)' if is_new_format else 'Friendly Names (legacy)'}")
    
    def get_col(row, *possible_names):
        """Get value from row, trying multiple possible column names."""
        for name in possible_names:
            if name in row.index:
                return row[name]
        return None
    
    records = []
    for idx, row in df.iterrows():
        # v45 SCHEMA - exact field names expected by dashboard JS
        # New ADO field names listed first, legacy friendly names as fallbacks
        record = {
            'id': clean_int(get_col(row, 'System.Id', 'ID')),
            'type': clean_string(get_col(row, 'System.WorkItemType', 'Work Item Type')),
            'title': clean_string(get_col(row, 'System.Title', 'Title')),
            'state': clean_string(get_col(row, 'System.State', 'State')),
            'assignedTo': clean_name(get_col(row, 'System.AssignedTo', 'Assigned To')),
            'areaPath': clean_string(get_col(row, 'System.AreaPath', 'Area Path')),
            'team': get_team(get_col(row, 'System.AreaPath', 'Area Path')),
            'iterationPath': clean_string(get_col(row, 'System.IterationPath', 'Iteration Path')),
            'iteration': get_iteration_name(get_col(row, 'System.IterationPath', 'Iteration Path')),
            'createdDate': parse_datetime(get_col(row, 'System.CreatedDate', 'Created Date')),
            'stateChangeDate': parse_datetime(get_col(row, 'Microsoft.VSTS.Common.StateChangeDate', 'State Change Date')),
            'closedDate': parse_date_only(get_col(row, 'Microsoft.VSTS.Common.ClosedDate', 'Closed Date')),
            'targetDate': parse_target_date(get_col(row, 'Microsoft.VSTS.Scheduling.TargetDate', 'Target Date')),
            'priority': clean_int(get_col(row, 'Microsoft.VSTS.Common.Priority', 'Priority')),
            'severity': clean_string(get_col(row, 'Microsoft.VSTS.Common.Severity', 'Severity')),
            'tags': clean_string(get_col(row, 'System.Tags', 'Tags')),
            'parentId': clean_int(get_col(row, 'System.Parent', 'Parent')),
            'effort': clean_float(get_col(row, 'Microsoft.VSTS.Scheduling.Effort', 'Effort')),
            'effortRollup': clean_float(get_col(row, 'Custom.EffortRollup', 'Effort Rollup')) or 0.0,
            'backlogPriority': clean_float(get_col(row, 'Microsoft.VSTS.Common.BacklogPriority', 'Backlog Priority')),
            # Custom fields
            'customers': clean_string(get_col(row, 'Custom.Customers', 'Customers')),
            'teamsAffected': clean_string(get_col(row, 'Custom.TeamsAffected', 'Teams Affected')),
            'releaseVersion': clean_string(get_col(row, 'Custom.ReleaseVersion', 'Release Version')),
            'bugType': clean_string(get_col(row, 'Custom.BugType', 'Bug Type')),
            'component': clean_string(get_col(row, 'Custom.Component', 'Component')),
            'feature': clean_string(get_col(row, 'Custom.Feature', 'Feature')),
            'ticketCategory': clean_string(get_col(row, 'Custom.TicketCategory', 'Ticket Category')),
            'deliverySliceOwner': clean_name(get_col(row, 'Custom.DeliverySliceOwner', 'Delivery Slice Owner')),
            'csOwner': clean_name(get_col(row, 'Custom.CSOwner', 'CS Owner')),
            'workLogData': clean_string(get_col(row, 'Custom.WorkLogData', 'Work Log Data')),
            'url': f"https://dev.azure.com/ncryptedcloud/eShare/_workitems/edit/{clean_int(get_col(row, 'System.Id', 'ID'))}"
        }
        records.append(record)

    return records


def generate_csv_validation_data(records):
    """Generate validation metadata from processed records for comparison in dashboard."""
    from collections import Counter

    # Total count
    total = len(records)

    # Count by type
    type_counts = Counter(r['type'] for r in records if r.get('type'))

    # Count by state
    state_counts = Counter(r['state'] for r in records if r.get('state'))

    # Count by team
    team_counts = Counter(r['team'] for r in records if r.get('team'))

    # Date range (created dates)
    created_dates = [r['createdDate'] for r in records if r.get('createdDate')]
    if created_dates:
        # Dates are in ISO format, so string comparison works
        min_date = min(created_dates)[:10]  # Just the date part
        max_date = max(created_dates)[:10]
    else:
        min_date = None
        max_date = None

    # Unique IDs check
    ids = [r['id'] for r in records if r.get('id')]
    unique_ids = len(set(ids))
    duplicate_ids = total - unique_ids

    return {
        'total': total,
        'byType': dict(type_counts),
        'byState': dict(state_counts),
        'byTeam': dict(team_counts),
        'dateRange': {
            'earliest': min_date,
            'latest': max_date
        },
        'uniqueIds': unique_ids,
        'duplicateIds': duplicate_ids
    }


def build_template(template_dir):
    """Concatenate the 4 part files into a single template."""
    parts = []
    for i in range(1, 5):
        part_path = os.path.join(template_dir, f'dashboard_v3_part{i}.html')
        if not os.path.exists(part_path):
            print(f"ERROR: Missing template part: {part_path}")
            print(f"Looking in: {template_dir}")
            print(f"Available files: {os.listdir(template_dir) if os.path.exists(template_dir) else 'directory not found'}")
            sys.exit(1)
        with open(part_path, 'r', encoding='utf-8') as f:
            parts.append(f.read())
    return ''.join(parts)


def validate_output(output):
    """Validate that all placeholders were replaced."""
    errors = []
    for placeholder, description in PLACEHOLDERS.items():
        if placeholder in output:
            errors.append(f"  - {placeholder} ({description}) was NOT replaced!")
    
    if errors:
        print("=" * 60)
        print("VALIDATION FAILED - Placeholders still present in output:")
        print("=" * 60)
        for error in errors:
            print(error)
        print("=" * 60)
        sys.exit(1)
    
    print("✓ Validation passed: All placeholders replaced successfully")


def validate_schema(records):
    """Validate that records have the expected v45 schema fields."""
    expected_fields = {
        'id', 'type', 'title', 'state', 'assignedTo', 'areaPath', 'team',
        'iterationPath', 'iteration', 'createdDate', 'stateChangeDate',
        'closedDate', 'targetDate', 'priority', 'severity', 'tags',
        'parentId', 'effort', 'effortRollup', 'backlogPriority',
        'customers', 'teamsAffected', 'releaseVersion', 'bugType',
        'component', 'feature', 'ticketCategory', 'deliverySliceOwner', 'csOwner',
        'workLogData', 'url'
    }
    
    if records:
        actual_fields = set(records[0].keys())
        missing = expected_fields - actual_fields
        extra = actual_fields - expected_fields
        
        if missing:
            print(f"⚠ Missing fields: {missing}")
        if extra:
            print(f"⚠ Extra fields: {extra}")
        
        if not missing and not extra:
            print("✓ Schema validation passed: All expected fields present")
        
        return len(missing) == 0
    return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='eShare Dashboard Generator - Generate HTML dashboard from Azure DevOps data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple run with all files in current directory
  python3 generate_dashboard.py

  # Specify input CSV and output location  
  python3 generate_dashboard.py -c ~/Downloads/ALL_Items.csv -o ~/Documents/dashboard.html

  # Full run with all paths specified
  python3 generate_dashboard.py \\
      -c "/path/to/ALL_Items.csv" \\
      -g "/path/to/Org_Chart.csv" \\
      -t "/path/to/Templates" \\
      -o "/path/to/ᵉShare DevOps Dashboard.html"
        """
    )
    
    parser.add_argument('-c', '--csv', 
                        default=DEFAULT_CSV_PATH,
                        help=f'Path to ALL_Items.csv (default: {DEFAULT_CSV_PATH})')
    
    parser.add_argument('-g', '--org',
                        default=DEFAULT_ORG_CHART_PATH,
                        help=f'Path to Org_Chart.csv (default: {DEFAULT_ORG_CHART_PATH})')

    parser.add_argument('-l', '--links',
                        default=DEFAULT_LINKS_CSV_PATH,
                        help=f'Path to WorkItemLinks.csv (default: {DEFAULT_LINKS_CSV_PATH})')

    parser.add_argument('-t', '--templates',
                        default=DEFAULT_TEMPLATE_DIR,
                        help=f'Folder containing template part files (default: {DEFAULT_TEMPLATE_DIR})')
    
    parser.add_argument('-o', '--output',
                        default=LOCAL_OUTPUT_PATH,
                        help=f"Output HTML file path (default: local directory)")

    parser.add_argument('-p', '--publish',
                        action='store_true',
                        help=f"Publish to SharePoint instead of local directory")

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine output path based on --publish flag
    if args.publish:
        output_path = PUBLISH_OUTPUT_PATH
        mode = "PUBLISH"
    else:
        output_path = os.path.expanduser(args.output)
        mode = "LOCAL" if output_path == LOCAL_OUTPUT_PATH else "CUSTOM"

    print("=" * 60)
    print(f"eShare Dashboard Generator v{CURRENT_VERSION} [{mode}]")
    print("=" * 60)

    # Resolve paths
    csv_path = os.path.expanduser(args.csv)
    org_chart_path = os.path.expanduser(args.org)
    links_csv_path = os.path.expanduser(args.links)
    template_dir = os.path.expanduser(args.templates)

    # Check CSV exists
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        sys.exit(1)

    # Print configuration
    print(f"CSV file:      {csv_path}")
    print(f"Org Chart:     {org_chart_path}")
    print(f"Links CSV:     {links_csv_path}")
    print(f"Templates:     {template_dir}")
    print(f"Output:        {output_path}")
    print("-" * 60)
    
    # Get refresh timestamp (from CSV file's last modified date)
    refresh_timestamp = get_refresh_timestamp(csv_path)
    print(f"Refresh timestamp: {refresh_timestamp}")
    
    # Process CSV
    records = process_csv(csv_path)
    print(f"Processed {len(records)} work items")

    # Generate CSV validation data
    csv_validation_data = generate_csv_validation_data(records)
    print(f"Generated validation metadata (total: {csv_validation_data['total']}, types: {len(csv_validation_data['byType'])}, states: {len(csv_validation_data['byState'])}, teams: {len(csv_validation_data['byTeam'])})")

    # Process Org Chart
    org_chart_data = process_org_chart(org_chart_path)
    print(f"Processed {len(org_chart_data)} org chart entries")

    # Process Work Item Links
    work_item_links = process_work_item_links(links_csv_path)
    print(f"Processed {len(work_item_links)} work item links")

    # Validate schema
    validate_schema(records)

    # Build template
    print("Building template from part files...")
    template = build_template(template_dir)
    print(f"Template size: {len(template):,} chars")

    # Replace placeholders
    print("Replacing placeholders...")
    json_data = json.dumps(records, indent=None)
    org_chart_json = json.dumps(org_chart_data, indent=None)
    csv_validation_json = json.dumps(csv_validation_data, indent=None)
    work_item_links_json = json.dumps(work_item_links, indent=None)
    print(f"JSON data size: {len(json_data):,} chars")
    print(f"Links data size: {len(work_item_links_json):,} chars")

    output = template.replace('WORK_ITEMS_PLACEHOLDER', json_data)
    output = output.replace('REFRESH_TIMESTAMP_PLACEHOLDER', refresh_timestamp)
    output = output.replace('ORG_CHART_DATA_PLACEHOLDER', org_chart_json)
    output = output.replace('CSV_VALIDATION_DATA_PLACEHOLDER', csv_validation_json)
    output = output.replace('WORK_ITEM_LINKS_PLACEHOLDER', work_item_links_json)
    
    # Validate placeholders replaced
    validate_output(output)
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    file_size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"Dashboard written to: {output_path}")
    print(f"File size: {file_size_mb:.1f} MB")
    
    # Sanity check - v45 was ~5MB, if much smaller, data may be wrong
    if file_size_mb < 3:
        print("⚠ WARNING: Output file smaller than expected. Data may not have loaded correctly.")
    
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)


if __name__ == '__main__':
    main()
