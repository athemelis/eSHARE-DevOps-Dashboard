#!/usr/bin/env python3
"""
migrate_bug_estimates_to_tasks.py

Migrates Bug estimation fields to child Task originalEstimate fields.

For each Bug with estimation fields:
1. Find existing child Tasks matching team Area Path
2. Split estimation evenly across matching Tasks
3. Create new Tasks if no matching Task exists for a team with an estimate
4. Skip Tasks that already have originalEstimate populated

Usage:
    # Dry run (read-only, shows what would happen)
    python3 migrate_bug_estimates_to_tasks.py --dry-run

    # Test on 1 bug
    python3 migrate_bug_estimates_to_tasks.py --limit 1

    # Test on 10 bugs
    python3 migrate_bug_estimates_to_tasks.py --limit 10

    # Full migration
    python3 migrate_bug_estimates_to_tasks.py

Environment:
    AZURE_DEVOPS_PAT - Personal Access Token with Work Items Read & Write
    
IMPORTANT: Refresh local data files (./copy-data-files.sh) between runs to avoid
processing the same Bugs twice. The script reads from local JSON files.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import Wiql, JsonPatchOperation

# Configuration
ORGANIZATION_URL = "https://dev.azure.com/ncryptedcloud"
PROJECT = "eShare"

# Estimation field mapping: Bug field -> (Team name, Area Path suffix, Task Type)
# Task Types: Code, Design, Spike, Test
ESTIMATION_FIELDS = {
    'analyticsEstimation': ('Analytics', 'eShare\\Analytics', 'Code'),
    'backendEstimation': ('Backend', 'eShare\\Backend', 'Code'),
    'frontendEstimation': ('Frontend', 'eShare\\Frontend', 'Code'),
    'governEstimation': ('Govern', 'eShare\\Govern', 'Code'),
    'scgEstimation': ('SCG', 'eShare\\Security and Compliance', 'Code'),
    'devopsEstimation': ('DevOps', 'eShare\\DevOps', 'Code'),
    'qaEstimation': ('QA', 'eShare\\QA', 'Test'),
    'staffEstimation': ('Staff', 'eShare\\Staff', 'Code'),
}

# Data file paths (relative to script directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)
ALL_ITEMS_FILE = os.path.join(DATA_DIR, "ALL Items.json")
WORK_ITEM_LINKS_FILE = os.path.join(DATA_DIR, "WorkItemLinks.json")
LOG_DIR = SCRIPT_DIR

# Global logger
logger = None


def setup_logging(dry_run=False):
    """Set up logging to both console and file."""
    global logger
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_suffix = "_DRYRUN" if dry_run else ""
    log_filename = f"migration_log_{timestamp}{mode_suffix}.txt"
    log_filepath = os.path.join(LOG_DIR, log_filename)
    
    # Create logger
    logger = logging.getLogger('migration')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Console handler (simpler format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return log_filepath


def log(message):
    """Log a message to both console and file."""
    if logger:
        logger.info(message)
    else:
        print(message)


def load_local_data():
    """Load work items and links from local JSON files."""
    with open(ALL_ITEMS_FILE, 'r') as f:
        items = json.load(f)
    
    with open(WORK_ITEM_LINKS_FILE, 'r') as f:
        links = json.load(f)
    
    return items, links


def get_ado_client():
    """Initialize Azure DevOps client."""
    pat = os.environ.get('AZURE_DEVOPS_PAT')
    if not pat:
        print("ERROR: AZURE_DEVOPS_PAT environment variable not set")
        print("Set it with: export AZURE_DEVOPS_PAT='your-token-here'")
        sys.exit(1)
    
    credentials = BasicAuthentication('', pat)
    connection = Connection(base_url=ORGANIZATION_URL, creds=credentials)
    return connection.clients.get_work_item_tracking_client()


def get_bug_estimations(bug):
    """Extract non-zero estimation fields from a Bug."""
    estimations = {}
    for field, (team, area_path, task_type) in ESTIMATION_FIELDS.items():
        val = bug.get(field)
        if val not in [None, '', 0]:
            try:
                estimations[field] = {
                    'value': float(val),
                    'team': team,
                    'area_path': area_path,
                    'task_type': task_type
                }
            except (ValueError, TypeError):
                pass
    return estimations


def find_child_tasks(bug_id, items_by_id, parent_to_children):
    """Find all child Tasks for a Bug."""
    child_ids = parent_to_children.get(bug_id, [])
    tasks = []
    for child_id in child_ids:
        child = items_by_id.get(child_id)
        if child and child.get('type') == 'Task':
            tasks.append(child)
    return tasks


def match_tasks_to_teams(tasks, estimations):
    """
    Match existing Tasks to teams based on Area Path.
    Returns dict: team -> list of matching tasks
    """
    team_tasks = {est['team']: [] for est in estimations.values()}
    
    for task in tasks:
        area_path = task.get('areaPath', '')
        for field, est in estimations.items():
            # Check if team name is in the area path
            if est['team'].lower() in area_path.lower():
                team_tasks[est['team']].append(task)
                break  # Each task belongs to one team only
    
    return team_tasks


def calculate_updates(bug, estimations, team_tasks):
    """
    Calculate what updates need to be made.
    Returns:
        - updates: list of (task_id, new_estimate) tuples
        - creates: list of (team, area_path, estimate) tuples for new Tasks
        - skipped: list of (task_id, reason) tuples
    """
    updates = []
    creates = []
    skipped = []
    
    for field, est in estimations.items():
        team = est['team']
        total_estimate = est['value']
        area_path = est['area_path']
        matching_tasks = team_tasks.get(team, [])
        
        if not matching_tasks:
            # No matching Task exists - need to create one
            creates.append({
                'team': team,
                'area_path': area_path,
                'estimate': total_estimate,
                'task_type': est['task_type'],
                'field': field
            })
        else:
            # Split estimate evenly across matching Tasks
            tasks_without_estimate = [t for t in matching_tasks 
                                       if t.get('originalEstimate') in [None, '', 0]]
            tasks_with_estimate = [t for t in matching_tasks 
                                    if t.get('originalEstimate') not in [None, '', 0]]
            
            # Skip tasks that already have estimates
            for task in tasks_with_estimate:
                skipped.append({
                    'task_id': task['id'],
                    'reason': f"Already has originalEstimate: {task.get('originalEstimate')}"
                })
            
            if tasks_without_estimate:
                # Split evenly among tasks without estimates
                per_task_estimate = total_estimate / len(tasks_without_estimate)
                for task in tasks_without_estimate:
                    updates.append({
                        'task_id': task['id'],
                        'estimate': per_task_estimate,
                        'team': team,
                        'task_title': task.get('title', '')[:50]
                    })
            elif tasks_with_estimate:
                # All tasks already have estimates - nothing to update
                pass
    
    return updates, creates, skipped


def create_task(wit_client, bug, team, area_path, estimate, task_type, dry_run=False):
    """Create a new Task as a child of the Bug."""
    task_title = f"[{team}] {bug.get('title', 'Bug fix')[:80]}"
    
    if dry_run:
        return {'id': 'NEW', 'title': task_title}
    
    # Build the patch document for creating a Task
    patch_document = [
        JsonPatchOperation(
            op="add",
            path="/fields/System.Title",
            value=task_title
        ),
        JsonPatchOperation(
            op="add",
            path="/fields/System.WorkItemType",
            value="Task"
        ),
        JsonPatchOperation(
            op="add",
            path="/fields/System.AreaPath",
            value=area_path
        ),
        JsonPatchOperation(
            op="add",
            path="/fields/System.IterationPath",
            value=bug.get('iterationPath', 'eShare')
        ),
        JsonPatchOperation(
            op="add",
            path="/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
            value=estimate
        ),
        JsonPatchOperation(
            op="add",
            path="/fields/Microsoft.VSTS.CMMI.TaskType",
            value=task_type
        ),
        # Link to parent Bug
        JsonPatchOperation(
            op="add",
            path="/relations/-",
            value={
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": f"{ORGANIZATION_URL}/{PROJECT}/_apis/wit/workItems/{bug['id']}"
            }
        )
    ]
    
    # Create the work item
    result = wit_client.create_work_item(
        document=patch_document,
        project=PROJECT,
        type="Task"
    )
    
    return {'id': result.id, 'title': task_title}


def update_task_estimate(wit_client, task_id, estimate, dry_run=False):
    """Update a Task's originalEstimate field."""
    if dry_run:
        return True
    
    patch_document = [
        JsonPatchOperation(
            op="add",
            path="/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
            value=estimate
        )
    ]
    
    wit_client.update_work_item(
        document=patch_document,
        id=task_id,
        project=PROJECT
    )
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Bug estimation fields to child Task originalEstimate'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without making changes')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit to N bugs (for testing)')
    parser.add_argument('--bug-id', type=int, default=None,
                        help='Process only a specific Bug ID')
    args = parser.parse_args()
    
    dry_run = args.dry_run
    limit = args.limit
    specific_bug_id = args.bug_id
    
    # Set up logging
    log_filepath = setup_logging(dry_run)
    
    log("=" * 70)
    log("BUG ESTIMATION TO TASK MIGRATION")
    log("=" * 70)
    log(f"Log file: {log_filepath}")
    
    if dry_run:
        log("\n*** DRY RUN MODE - No changes will be made ***\n")
    
    # Load local data
    log("Loading local data files...")
    items, links = load_local_data()
    
    # Build lookups
    items_by_id = {item['id']: item for item in items}
    
    # Build parent -> children mapping
    child_links = [link for link in links if link.get('type') == 'Child']
    parent_to_children = {}
    for link in child_links:
        parent_id = link['source']
        child_id = link['target']
        if parent_id not in parent_to_children:
            parent_to_children[parent_id] = []
        parent_to_children[parent_id].append(child_id)
    
    # Get Bugs with estimations
    bugs = [item for item in items if item.get('type') == 'Bug']
    bugs_with_estimates = []
    for bug in bugs:
        estimations = get_bug_estimations(bug)
        if estimations:
            bugs_with_estimates.append((bug, estimations))
    
    # Filter by specific bug ID if provided
    if specific_bug_id:
        bugs_with_estimates = [(b, e) for b, e in bugs_with_estimates if b['id'] == specific_bug_id]
        if not bugs_with_estimates:
            log(f"Bug {specific_bug_id} not found or has no estimations")
            return
    
    # Apply limit
    if limit:
        bugs_with_estimates = bugs_with_estimates[:limit]
    
    log(f"Found {len(bugs_with_estimates)} Bugs with estimations to process")
    
    # Initialize ADO client (only if not dry run or we'll need it)
    wit_client = None
    if not dry_run:
        log("Connecting to Azure DevOps...")
        wit_client = get_ado_client()
    
    # Process each Bug
    total_updates = 0
    total_creates = 0
    total_skipped = 0
    errors = []
    
    for i, (bug, estimations) in enumerate(bugs_with_estimates):
        bug_id = bug['id']
        bug_title = bug.get('title', '')[:50]
        
        log(f"\n[{i+1}/{len(bugs_with_estimates)}] Bug {bug_id}: {bug_title}")
        log(f"  Estimations: {', '.join(f'{e['team']}={e['value']}d' for e in estimations.values())}")
        
        # Find child tasks
        child_tasks = find_child_tasks(bug_id, items_by_id, parent_to_children)
        log(f"  Child Tasks: {len(child_tasks)}")
        
        # Match tasks to teams
        team_tasks = match_tasks_to_teams(child_tasks, estimations)
        
        # Calculate what needs to be done
        updates, creates, skipped = calculate_updates(bug, estimations, team_tasks)
        
        # Report skipped
        for skip in skipped:
            log(f"  SKIP Task {skip['task_id']}: {skip['reason']}")
            total_skipped += 1
        
        # Process updates
        for update in updates:
            action = "WOULD UPDATE" if dry_run else "UPDATE"
            log(f"  {action} Task {update['task_id']} ({update['team']}): "
                  f"originalEstimate = {update['estimate']:.2f}d")
            
            if not dry_run:
                try:
                    update_task_estimate(wit_client, update['task_id'], update['estimate'])
                    total_updates += 1
                except Exception as e:
                    errors.append(f"Bug {bug_id}, Task {update['task_id']}: {e}")
                    log(f"    ERROR: {e}")
            else:
                total_updates += 1
        
        # Process creates
        for create in creates:
            action = "WOULD CREATE" if dry_run else "CREATE"
            log(f"  {action} Task for {create['team']}: "
                  f"areaPath={create['area_path']}, originalEstimate={create['estimate']:.2f}d")
            
            if not dry_run:
                try:
                    result = create_task(wit_client, bug, create['team'], 
                                        create['area_path'], create['estimate'],
                                        create['task_type'])
                    log(f"    Created Task {result['id']}: {result['title']}")
                    total_creates += 1
                except Exception as e:
                    errors.append(f"Bug {bug_id}, Create {create['team']}: {e}")
                    log(f"    ERROR: {e}")
            else:
                total_creates += 1
    
    # Summary
    log("\n" + "=" * 70)
    log("SUMMARY")
    log("=" * 70)
    log(f"Bugs processed: {len(bugs_with_estimates)}")
    log(f"Tasks {'would be ' if dry_run else ''}updated: {total_updates}")
    log(f"Tasks {'would be ' if dry_run else ''}created: {total_creates}")
    log(f"Tasks skipped (already have estimate): {total_skipped}")
    
    if errors:
        log(f"\nErrors: {len(errors)}")
        for err in errors:
            log(f"  - {err}")
    
    if dry_run:
        log("\n*** DRY RUN COMPLETE - No changes were made ***")
        log("Run without --dry-run to execute the migration")
    
    log(f"\nLog saved to: {log_filepath}")


if __name__ == "__main__":
    main()
