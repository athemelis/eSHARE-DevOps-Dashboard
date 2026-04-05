# Bug Planning Considerations

**Date:** 2026-01-30 06:08
**Session:** 2026-01-29 bug fixes

---

## User Prompt

I'd like to verify how we treat Bugs in the Capacity Dashboard. Let's take Bug 3252 as an example.
1. It's Iteration is CY2026Q1-Mar, so it shows in the Backlog Work Candidates column for March.
2. It has a Frontend Estimation of 1.
3. Actual Work was completed in Dec (1 day) - based on Task 3371
4. What happens when I add the Bug to the Committed Work Plan?

I'm seeing that the 1 day of work completed in Dec shows up in Mar

Before we solve for this, can you find me all Bugs where the Task has worklog data and is set to an Iteration different than the parent Bug itself?

Review this data and compare with how we treat Features/Delivery Slices/Tasks

Propose a solution to solve for this problem

---

## Analysis

### Bug 3252 Details

| Field | Value |
|-------|-------|
| Iteration | CY2026Q1-Mar |
| Frontend Estimation | 1.0 |
| State | In Progress |

**Child Tasks:**

| Task | Iteration | Effort | State | WorkLog |
|------|-----------|--------|-------|---------|
| 3371 | CY2025Q4-Dec | 1.0 | Done | 1 day logged (Dec 16, 2025) |
| 3887 | CY2026Q1-Jan | None | New | None |

**Problem:** The Bug is in **March 2026** but the work was done in **December 2025**.

---

### Bugs with Tasks in Different Iterations (42 found)

```
Bug 368 (CY2025Q4-Dec) -> Task 1323 (CY2025Q4-Nov) - effort: 1.25
Bug 956 (CY2026Q1-Jan) -> Task 2368 (CY2025Q4-Dec) - effort: 1.0
Bug 1327 (CY2026Q1-Jan) -> Task 2371 (CY2025Q4-Dec) - effort: 1.0
Bug 1328 (CY2026Q1-Jan) -> Task 2372 (CY2025Q4-Dec) - effort: 1.0
Bug 1906 (CY2026Q1-Mar) -> Task 2375 (CY2025Q4-Dec) - effort: 1.0
Bug 1915 (CY2026Q1-Mar) -> Task 2376 (CY2025Q4-Dec) - effort: 2.0
Bug 2431 (CY2026Q1-Jan) -> Task 3126 (CY2025Q4-Dec) - effort: 3.0
Bug 2699 (CY2026Q1-Feb) -> Task 3059 (CY2026Q1-Jan) - effort: 2.0
Bug 2717 (CY2026Q1-Jan) -> Task 3205 (CY2025Q4-Dec) - effort: 1.0
Bug 2731 (CY2026Q1-Jan) -> Task 3460 (CY2025Q4-Dec) - effort: 3.0
Bug 2757 (CY2026Q1-Jan) -> Task 3204 (CY2025Q4-Dec) - effort: 2.0
Bug 2797 (CY2026Q1-Jan) -> Task 3148 (CY2025Q4-Dec) - effort: 1.5
Bug 2831 (CY2026Q1-Jan) -> Task 3149 (CY2025Q4-Dec) - effort: 2.0
Bug 2837 (CY2026Q1-Feb) -> Task 2840 (CY2025Q4-Dec) - effort: 1.0
Bug 2950 (CY2026Q1-Jan) -> Task 3061 (CY2025Q4-Dec) - effort: 2.0
Bug 3252 (CY2026Q1-Mar) -> Task 3371 (CY2025Q4-Dec) - effort: 1.0
Bug 3364 (CY2026Q1-Jan) -> Task 3365 (CY2025Q4-Dec) - effort: 1.0
Bug 3373 (CY2026Q1-Jan) -> Task 3510 (z_Backlog) - effort: 0.5
Bug 3374 (CY2026Q1-Jan) -> Task 3388 (CY2025Q4-Dec) - effort: 1.0
Bug 3403 (CY2026Q1-Jan) -> Task 3535 (CY2025Q4-Dec) - effort: 2.5
Bug 3412 (CY2026Q1-Jan) -> Task 3847 (CY2025Q4-Dec) - effort: 2.0
Bug 3421 (CY2026Q1-Jan) -> Task 3430 (CY2025Q4-Dec) - effort: 2.3
Bug 3441 (CY2026Q1-Jan) -> Task 3531 (z_Backlog) - effort: 1.0
Bug 3479 (CY2026Q1-Jan) -> Task 3629 (CY2025Q4-Dec) - effort: 1.0
Bug 3492 (CY2026Q1-Jan) -> Task 3583 (CY2025Q4-Dec) - effort: 1.0
Bug 3528 (CY2026Q1-Jan) -> Task 3785 (CY2025Q4-Dec) - effort: 0.2
Bug 3560 (CY2026Q1-Jan) -> Task 5090 (z_Backlog) - effort: 0.1
Bug 3580 (CY2026Q1-Jan) -> Task 3594 (CY2025Q4-Dec) - effort: 0.5
Bug 3671 (CY2026Q1-Jan) -> Task 3673 (CY2025Q4-Dec) - effort: 1.25
Bug 3671 (CY2026Q1-Jan) -> Task 3674 (z_Backlog) - effort: 1.25
Bug 3688 (CY2026Q1-Jan) -> Task 3691 (CY2025Q4-Dec) - effort: 1.0
Bug 3750 (CY2026Q1-Jan) -> Task 4175 (eShare) - effort: 0.25
Bug 3794 (CY2026Q1-Jan) -> Task 3903 (CY2025Q4-Dec) - effort: 1.5
Bug 3798 (CY2026Q1-Jan) -> Task 4222 (z_Backlog) - effort: 0.2
Bug 3827 (CY2026Q1-Jan) -> Task 3828 (CY2025Q4-Dec) - effort: 1.0
Bug 3837 (CY2026Q1-Jan) -> Task 3840 (CY2025Q4-Dec) - effort: 1.0
Bug 3915 (CY2026Q1-Jan) -> Task 3916 (CY2025Q4-Dec) - effort: 0.125
Bug 4044 (CY2026Q1-Jan) -> Task 4045 (CY2025Q4-Dec) - effort: 0.125
Bug 4099 (CY2026Q1-Jan) -> Task 4136 (CY2025Q4-Dec) - effort: 0.75
Bug 4103 (CY2026Q1-Jan) -> Task 4106 (CY2025Q4-Dec) - effort: 0.125
Bug 4177 (CY2026Q1-Jan) -> Task 4184 (CY2025Q4-Dec) - effort: 0.25
Bug 4232 (CY2026Q1-Feb) -> Task 4586 (CY2026Q1-Jan) - effort: 1.0
```

---

## Root Cause: Different Data Models

| Aspect | Features | Bugs |
|--------|----------|------|
| **Effort stored on** | Delivery Slices (children) | Bug itself (estimation fields) |
| **Iteration filtering** | `matchesIteration(slice, iteration)` | None |
| **Result** | Effort correctly attributed to slice's iteration | Effort always shows in Bug's iteration |

**Features** can span iterations because each Delivery Slice has its own iteration and effort.

**Bugs** have one iteration but estimation fields don't know when the actual work happens.

### Code Comparison

**Features** (`getTeamEffortBreakdown`):
```javascript
// CRITICAL: Filter by iteration to only include slices in the selected iteration
const deliverySlices = (allItems || []).filter(i =>
    childIdSet.has(i.id) &&
    (i.type === 'Delivery Slice' || i.workItemType === 'Delivery Slice') &&
    (!iteration || cpd.matchesIteration(i, iteration))  // <-- FILTERS BY ITERATION
);
```

**Bugs** (`getTeamEffortBreakdown`):
```javascript
// Read from estimation fields - NO ITERATION FILTERING
const fieldToTeam = {
    analyticsEstimation: 'Analytics',
    backendEstimation: 'Backend',
    // ...
};
```

---

## Proposed Solutions

### Option A: Use Task Effort Instead of Bug Estimation Fields

Change `getTeamEffortBreakdown()` for Bugs to:
1. Look at child Tasks (like Features look at Delivery Slices)
2. Filter Tasks by iteration
3. Use Task's `effort` field and `areaPath` for team

**Pros:** Mirrors Feature behavior, iteration-accurate
**Cons:** Requires Tasks to have effort filled in (many don't)

### Option B: Keep Estimation Fields, Subtract Completed Work

1. Keep using Bug's estimation fields for planned effort
2. Subtract effort from Tasks with `state=Done` in previous iterations

**Pros:** Works with existing data, shows remaining effort
**Cons:** More complex logic

### Option C: Exclude Bugs with All Tasks Done in Past Iterations

1. If all child Tasks are Done and in past iterations, don't show Bug in current iteration capacity
2. These Bugs are "work complete, waiting for release"

**Pros:** Simple to implement, semantically correct
**Cons:** Doesn't handle partial completion

---

## Recommendation

**Option A** - it aligns Bug handling with Feature handling and is the cleanest approach. However, it depends on Tasks having proper `effort` values.

---

## Status

**On hold** - User requested to save this analysis for later consideration.
