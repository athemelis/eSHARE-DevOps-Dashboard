# Session Notes — 2026-02-12 07:50 UTC

## Commits in this PR
- `30d5988` v167: Estimate missing items included in warnings filter with icon
- `29cef78` v167: Enhanced warning detection - deadline risk, missing child estimates, multiple warnings

## Changes Made

### 1. Estimate Missing Items in Warnings Filter
**Problem:** Items with "Estimate missing" (red bar) like Bug 5832 were not included in the warnings filter ("⚠️ X items with issues - click to filter") and didn't show the ⚠️ icon.
**Root Cause:** `detectStateInconsistency()` returned `null` early when `estimatedEffort === 0`, before checking any warning rules.
**Fix:** Added Rule 0 (estimate_missing) that fires when `actualLogged > 0` but `estimatedEffort === 0`, before the early return. Added ⚠️ icon to both `renderProgressCell` and `renderCapacityProgressCell` estimate missing cases.

### 2. Enhanced Warning Detection — Multiple Warnings Support
**Problem:** Feature 428 had two issues (deadline risk + missing child estimates) but the single-warning system could only surface one.
**Changes:**
- Rewrote `detectStateInconsistency()` to collect an **array** of warnings instead of returning on first match
- Returns backward-compatible object: `{ hasWarning, type, message, warnings[] }` where `message` concatenates all warnings with " · "
- All existing consumers (`hasWarning`, `message`) work without changes

### 3. New Warning Rules
- **Rule 6 — Missing child estimates bubble-up:** Counts child tasks (from Bug tasks, DS tasks, and child bug tasks) that have work logged but no `originalEstimate`. Flags parent Feature/Bug with count.
- **Rule 7 — Deadline proximity risk:** If item has a target date within 7 days AND progress < 75%, flags as deadline risk with days remaining.

### 4. Multiple Warning Banners in Popup
- Both Bug and Feature progress popups now render individual warning banners for each warning (previously showed single concatenated message)

## Decisions
- Kept backward-compatible warning interface (`hasWarning`, `message`, `type`) — `type` is first warning's type, `message` joins all with " · "
- Deadline threshold: 7 days / 75% progress — matches common project management risk thresholds
- Missing child estimate rule requires `work > 0` — tasks with no work AND no estimate are not flagged (they haven't started)

## Open Items
- None

## Next Steps
- Continue dashboard improvements as needed
