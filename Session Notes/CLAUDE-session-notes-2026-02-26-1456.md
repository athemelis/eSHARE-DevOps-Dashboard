# Session Notes — 2026-02-26 14:56

## Summary
Added drag-to-reorder support for the Capacity Dashboard planning board (both Backlog Candidates and Committed Plan panels).

## Commits in this PR
- `271e9fe` v193: Capacity Dashboard drag-to-reorder priority

## Changes Made

### Capacity Dashboard Drag-to-Reorder (v193)
- **`renderPlanningItem()`**: Added `draggable="true"`, `data-backlog-priority` attribute, and `onmousedown="event.stopPropagation()"` on checkbox to prevent drag from checkbox
- **`setupCapacityDragReorder()`**: New function that attaches drag handlers to all `.candidate-list` containers (left panel) and `#committed-items-list` (right panel)
- **`setupCapacityDragOnContainer()`**: Full drag/drop lifecycle (dragstart, dragover, drop, dragend) with section-scoped containment
- **`getScopedSiblings()`**: Returns sibling items within same section — left panel uses all items in container, right panel finds items between `.committed-group-header` divs
- **`inSameCommittedGroup()`**: Prevents cross-group dragging in committed panel
- **Click-vs-drag guard**: Added 200ms suppression in `handleCapacityRowClick()` to prevent modal opening after drag
- **CSS**: Added `.planning-item` drag states (`.dragging`, `.drag-over-above`, `.drag-over-below`, `.drag-saving`, `.drag-pending-sync`)

### Reused Infrastructure
- `updateWorkItemBacklogPriority()` — ADO PATCH call
- `_pendingPriorityChanges` map — pending sync state
- `applyPendingPriorityOverrides()` — auto-refresh persistence
- Midpoint priority algorithm with `PRIORITY_GAP` edge handling
- `showDragToast()` — success/error notifications

## Decisions
- Drag scoped within sections (no cross-section dragging) — Customer Bugs stays in Customer Bugs, etc.
- Right panel committed groups use `.committed-group-header` boundaries for scoping
- Same pending sync / 5-min timeout / revert behavior as generic tables

## Known Issues
- "Failed to update priority: not authenticated" on localhost — expected, ADO auth only works in prod (SharePoint)

## Next Steps
- Test drag-to-reorder in prod after PR merge
- Monitor for any edge cases with committed panel group boundaries
