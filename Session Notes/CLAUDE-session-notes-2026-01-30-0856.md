# Capacity Bar Experiment - Session Notes
**Date:** 2026-01-30
**Status:** Abandoned (saved for future reference)
**Base Version:** v151 → v152

## Overview

This session explored redesigning the Capacity Planning Dashboard's team capacity bars to show **estimated vs actual effort** per work type (Features, Customer Bugs, Internal Bugs).

## Problem Statement

The original capacity bars showed only committed/estimated effort. The goal was to visualize both:
- **Estimated effort** (from Delivery Slice/Bug estimates)
- **Actual effort** (from Task workLogData)

This would help identify where teams are over/under-delivering against estimates.

## Approaches Tried

### Option A: Stacked Pills (Actual vs Estimated per Type)

Each type (Features, Customer Bugs, Internal Bugs) shown as a "pill" segment:
- If actual ≤ estimated: Show actual in color, gray for unused estimate
- If actual > estimated: Show estimate in color, red for overage
- Scale bar to max(capacity, totalEstimated, totalActual)
- Capacity threshold line when over-committed

**Visual refinements attempted:**
1. Border-right separators (not distinct enough)
2. Box-shadow separators (still not distinct)
3. Gap-based separation with rounded pill segments (better but complex)
4. Added padding to bar-track for edge visibility
5. Light outline for dark mode visibility

### Option B: Split Rows (Actual / Estimated)

Two rows per team:
- Top row: Actual effort (stacked by type)
- Bottom row: Estimated effort (stacked by type, 60% opacity)
- Both rows on same scale: max(actual, estimated, capacity)
- Capacity threshold line on both rows

## Code Changes Made

### dashboard.js

1. **New function: `getTeamActualEffort()`** - Extracts actual work hours from Task workLogData
   - Location: Around line 25650
   - Parses workLogData JSON, extracts hours per team member
   - Maps team members to teams via Org Chart

2. **Modified: `calculateCommittedTeamCapacities()`** - Returns `byType` with `{estimated, actual}` for each type
   - Added actual effort calculation per type
   - Returns both totalEstimated and totalActual

3. **Modified: `renderCompactBar()`** - Complete rewrite for Option A visualization
   - Builds stacked segments with actual/estimate split
   - Handles overage (red) display
   - Shows capacity threshold line

4. **New function: `renderSplitBar()`** - Option B visualization
   - Two-row layout per team
   - Actual on top, Estimated on bottom

### dashboard.css

1. **Bar track changes:**
   - Added `gap: 3px` for segment separation
   - Added `padding: 1px 3px` for edge visibility
   - Height increased to 14px

2. **Segment group styling:**
   - `border-radius: 3px` for pill appearance
   - `outline: 1px solid rgba(255, 255, 255, 0.5)` for dark mode
   - `overflow: hidden` for rounded corners

3. **New styles for Option B:**
   - `.capacity-bars-split` - grid layout
   - `.capacity-bar-split` - split row container
   - `.bar-rows`, `.bar-row`, `.bar-row-label` - two-row structure

### dashboard-body.html

1. Added visualization labels ("Option A", "Option B")
2. Added second container for Option B (`capacity-bars-split-left/right`)
3. Changed Customer Bugs legend color from red (#f87171) to purple (#a855f7)

## Why Abandoned

The visualizations became too complex to reason about at a glance:
- Multiple visual elements competing for attention
- Hard to quickly assess team capacity status
- The original simple bar was more intuitive

## To Revisit This Work

1. Start from v151 (the clean version)
2. The key insight: Need to track actual vs estimated effort per type
3. Consider simpler visualizations:
   - Tooltip-only approach (show details on hover)
   - Separate "Actuals" dashboard view
   - Simple numeric indicators instead of visual bars

## Key Functions to Reference

```javascript
// Get actual effort from Task workLogData
function getTeamActualEffort(tasks, orgChart, iteration) {
    // Parses workLogData JSON from tasks
    // Maps team members to teams
    // Returns { teamName: { features: X, customerBugs: Y, internalBugs: Z } }
}

// Calculate both estimated AND actual per team
function calculateCommittedTeamCapacities(committedItems, iteration) {
    // Returns array with:
    // - totalEstimated, totalActual
    // - byType: { features: {estimated, actual}, customerBugs: {...}, internalBugs: {...} }
}
```

## Files to Restore

To return to v151, reset these files:
- dashboard.js
- dashboard.css
- dashboard-body.html

Or simply: `git checkout v151 -- dashboard.js dashboard.css dashboard-body.html`
