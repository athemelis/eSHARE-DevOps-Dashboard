# eShare DevOps Dashboard - Reference

This file contains feature-specific code reference material. For session workflow, standards, and checklists, see `.github/copilot-instructions.md`.

## Current Version: v249

---

## Architecture & Data Flow Diagrams

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AZURE DEVOPS                                │
│                   (Source of Truth - Live Data)                      │
│  Work Items: Features, Bugs, Tasks, Issues, Delivery Slices         │
│  Work Item Links: Parent/Child, Related relationships               │
│  Analytics API: OData v3.0 endpoint                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP API (OData)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       POWER AUTOMATE                                │
│  Flow 1: ALL Items Export          → Every 3 minutes                │
│  Flow 2: WorkItemLinks Export      → Every 5 minutes                │
│  Flow 3: Org Chart Sync            → Manual updates                 │
│  Setup guide: README_PowerAutomate.md                               │
│  Flow definitions: flows/ directory (version-controlled)            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Write JSON Files
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  SHAREPOINT DOCUMENT LIBRARY                        │
│  Site: wardedbox.sharepoint.com/sites/ProductManagement             │
│  ALL Items.json  ·  WorkItemLinks.json  ·  Org Chart.json          │
│  cascading_lists.json                                               │
└───────────────┬─────────────────────────────────┬───────────────────┘
                │                                 │
    OneDrive Sync (dev)                Microsoft Graph API (prod)
                │                                 │
                ▼                                 ▼
┌───────────────────────┐      ┌──────────────────────────────────────┐
│   LOCAL DEVELOPMENT   │      │          PRODUCTION                  │
│  copy-data-files.sh   │      │  devops-dashboard.e-share.io         │
│  serve-dashboard.sh   │      │  (Cloudflare Pages)                  │
│  localhost:8000       │      │          ▼                           │
│  MSAL bypassed        │      │  MSAL prompts for Azure AD login    │
│  JSON loaded from ./  │      │          ▼                           │
│                       │      │  Graph API fetches JSON from SP      │
│                       │      │          ▼                           │
│                       │      │  Dashboard renders in browser        │
└───────────────────────┘      └──────────────────────────────────────┘
```

### Data Export Schedule

| File | Update Frequency | Records |
|------|-----------------|---------|
| ALL Items.json | Every 3 minutes | ~7,100 work items |
| WorkItemLinks.json | Every 5 minutes | ~15,400 links |
| Org Chart.json | Manual | ~50 team members |
| cascading_lists.json | Manual | Picklist values |

### MSAL Authentication Flow (Production)

```
┌─────────────┐        ┌──────────────────┐        ┌─────────────────┐
│   Browser   │───────▶│  Azure AD Login  │───────▶│  Access Token   │
│  (User)     │        │  (Microsoft)     │        │  (JWT)          │
└─────────────┘        └──────────────────┘        └─────────────────┘
                                                           │
                                ┌──────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Authorization: Bearer eyJ0eXAiOiJKV1QiLC...                       │
│  GET graph.microsoft.com/v1.0/sites/{siteId}/drive/                 │
│      root:/Product%20Planning/ALL%20Items.json:/content              │
└─────────────────────────────────────────────────────────────────────┘

MSAL Config:
  Client ID:  bf683b68-0dc3-4205-a5b7-676f54a958c0
  Authority:  login.microsoftonline.com/wardedbox.onmicrosoft.com
  Scopes:     Sites.Selected
```

### Deployment Flow

```
  Developer                    GitHub                    Cloudflare Pages
  ─────────                    ──────                    ────────────────
      │                           │                            │
      │  1. Create feature branch │                            │
      │     from main             │                            │
      │                           │                            │
      │  2. Edit & test locally   │                            │
      │     (localhost:8000)      │                            │
      │                           │                            │
      │  3. git push + create PR  │                            │
      │ ─────────────────────────▶│                            │
      │                           │                            │
      │  4. PR reviewed & merged  │                            │
      │     to main               │                            │
      │                           │  5. Auto-deploy triggered  │
      │                           │───────────────────────────▶│
      │                           │                            │
      │                           │         devops-dashboard   │
      │                           │         .e-share.io live   │
      │                           │                            │
```

### Local vs Production Comparison

| Aspect | Local Development | Production |
|--------|-------------------|------------|
| **URL** | `localhost:8000/dashboard.html` | `devops-dashboard.e-share.io/dashboard.html` |
| **HTML/JS served by** | Python HTTP server | Cloudflare Pages |
| **Authentication** | None (MSAL bypassed) | MSAL + Azure AD |
| **Data Source** | Local `./` directory | SharePoint via Graph API |
| **JSON Files** | Copied via `copy-data-files.sh` | Fetched with OAuth token |

### Key URLs & Endpoints

| Purpose | URL |
|---------|-----|
| **Production Site** | `https://devops-dashboard.e-share.io` |
| **SharePoint Site** | `https://wardedbox.sharepoint.com/sites/ProductManagement` |
| **Data Folder** | `/Shared Documents/Product Planning/` |
| **Azure AD Authority** | `https://login.microsoftonline.com/wardedbox.onmicrosoft.com` |
| **MSAL Client ID** | `bf683b68-0dc3-4205-a5b7-676f54a958c0` |
| **ADO Work Items** | `https://dev.azure.com/ncryptedcloud/eShare/_workitems/edit/{id}` |
| **GitHub Repo** | `https://github.com/eshare-inc/eSHARE-DevOps-Dashboard` |
| **Local Dev** | `http://localhost:8000/dashboard.html` |

---

## Auto-Refresh Feature (v107+)
- **Silent auto-refresh**: Data reloads every 60 seconds without page reload
- **Countdown timer**: Shows seconds until next refresh in header
- **Manual refresh button (↻)**: Click to refresh immediately with visual feedback
- **Chart animations disabled during auto-refresh**: Prevents visual disruption

Key code locations:
- `isAutoRefresh` flag: [dashboard.js:44](dashboard.js#L44)
- `performAutoRefresh()`: [dashboard.js:19393](dashboard.js#L19393)
- `scheduleAutoRefresh()`: [dashboard.js:19369](dashboard.js#L19369)
- Chart animation control in `createChart()`: [dashboard.js:4833](dashboard.js#L4833)

## Bug Closed Date Algorithm (v127+)

When determining the closed date for bugs, use this logic:

| Bug State | Closed Date Source | Reason |
|-----------|-------------------|--------|
| **Done** | `closedDate` field | ADO automatically populates `closedDate` when state becomes Done |
| **Closed** | `stateChangeDate` field | ADO does NOT populate `closedDate` for Closed state; use `stateChangeDate` instead |

Key code location:
- `getBugClosedDate()`: [dashboard.js:14859](dashboard.js#L14859)

**Note:** The Bug Trend chart counts ALL bugs that transitioned to a terminal state (Done or Closed), not just bugs currently in those states. This provides accurate historical tracking even if a bug was reopened after being closed.

## Relationship Pills (v218+)

Pills appear next to work item titles in tables and in the Unified Modal header. Clicking a pill opens the related item in the Unified Modal.

| Scenario | Pill Shown | Style | Click Action |
|----------|-----------|-------|--------------|
| Bug Issue → has related Bug | "Bug 3598: title" | Red | Opens Unified Modal |
| Bug Issue → no related Bug | "no Bug" | Red warning | — |
| ER Issue → has related Feature | "Feature 4552: title" | Purple | Opens Unified Modal |
| ER Issue → no related Feature | "no Feature" | Purple warning | — |
| Customer Bug → has related Issue | "Issue 6467: title" | Orange | Opens Unified Modal |
| Customer Bug → no related Issue | "no Issue" | Orange warning | — |
| Feature → has related Issue(s) | "Issue 6467: title" | Orange | Opens Unified Modal |

**Where pills appear:**
- Generic table title columns (all dashboards)
- Bugs Dashboard title column (Issue pill for Customer Bugs)
- Customers Dashboard title column (Bug pill for Bug Issues, Feature pill for ER Issues)
- Releases Dashboard: Customer Bugs table (Issue pill), Issues table (Bug pill)
- Unified Modal header tag area (Issue pill for Bugs, Bug pill for Bug Issues)

Key code locations:
- `buildBugPillForIssue()`: Bug pill for Bug Issues
- `buildFeaturePillForIssue()`: Feature pill for ER Issues
- `buildIssuePillForCustomerBug()`: Issue pill for Customer Bugs
- `buildIssuePillsForFeature()`: Issue pill(s) for Features
- `getRelatedBugForIssue()`, `getRelatedIssueForBug()`, `getRelatedFeatureForIssue()`: Relationship lookup helpers

## Untagged Filters vs (No Tags) (v133+)

The dashboard has two different concepts for "untagged" items:

### "Untagged" (Special Filter)
Clicking "Untagged: X" in a dashboard summary filters for items missing **specific category tags**:

| Dashboard | "Untagged" means | Tag categories checked |
|-----------|------------------|----------------------|
| **Roadmap** | Features without OKR tags | Tags starting with `1:`, `2:`, `3:`, `4:` |
| **Customers** | Enhancement Requests without CS tags | `CS: High Value`, `CS: Low Value`, `CS: Strategic` |
| **Bugs** | Bugs without architecture component tags | Tags from `ARCHITECTURE_COMPONENTS` (API, Database, UI, etc.) |

### "(No Tags)" (Generic Filter Option)
Selecting "(No Tags)" from the Tag dropdown filters for items with **completely empty tags field**.

### Key Difference
An item can appear in "Untagged" but NOT in "(No Tags)":
- A bug with tags "Regression, Security" but no architecture tags → shows in "Untagged: 149"
- A bug with absolutely no tags → shows in both "Untagged" AND "(No Tags)"

Key code locations:
- `showUntaggedArchOnly` flag: Bugs dashboard untagged architecture filter
- `showUntaggedCSOnly` flag: Customers dashboard untagged CS filter
- `showUntaggedOkrOnly` flag: Roadmap dashboard untagged OKR filter
- `filterBugsByUntaggedArch()`: [dashboard.js:14582](dashboard.js#L14582)
- `filterERUntagged()`: [dashboard.js:9215](dashboard.js#L9215)
- `filterByUntaggedOkr()`: Roadmap untagged OKR filter

## Capacity Dashboard - Key Concepts (v140+)

**Feature Visibility Logic:**

The Backlog Candidates view determines which iteration to show a Feature in based on its **child Delivery Slices**, NOT the Feature's own `iterationPath` field.

**Key Function: `featureHasSlicesInIteration()`**
- Checks if a Feature has one or more Delivery Slices in the selected iteration
- Uses `workItemLinks` to find parent-child relationships
- Filters by `type: 'Delivery Slice'` and matching `iterationPath`
- This allows Features to span multiple iterations through their Delivery Slices

**Example:**
| Item | Own iterationPath | Delivery Slice iterationPath | Appears in Iteration |
|------|-------------------|------------------------------|----------------------|
| Feature 4143 | `eShare\z_Backlog` | Slice 4581: `CY2026Q1-Feb` | **CY2026Q1-Feb** |
| Feature 4563 | `eShare\z_Backlog` | Slice 4686: `z_Backlog` | **z_Backlog** |
| Feature 2963 | `CY2025Q4-Dec` | Slice 2966: `CY2025Q4-Dec` | **CY2025Q4-Dec** |

**Why This Design:**
- Features often span multiple iterations
- Delivery Slices represent the actual work planned for each iteration
- This approach allows accurate capacity planning by iteration
- A Feature's own `iterationPath` might be outdated or set to `z_Backlog`

**Related Work Items:**
- **Features:** High-level epics (may span multiple iterations)
- **Delivery Slices:** Child work items that define iteration-specific deliverables
- **Bugs:** Can be linked to Features, shown in separate tables (use own `iterationPath`)

Key code locations:
- `featureHasSlicesInIteration()`: [dashboard.js:23949](dashboard.js#L23949)
- `matchesIteration()`: [capacity-planning-data.js:257](capacity-planning-data.js#L257)

## Collapsible Sections

CSS class `.collapsible.collapsed` with `toggleRoadmapTeamSummary()`. Structure: `.roadmap-section.collapsible` > `.roadmap-section-header` (click handler) + `.section-content` (animated via `max-height`/`opacity` transitions). Collapse state persisted via `saveStateToStorage()`.

## State Persistence (localStorage)

- **Save/load**: `saveStateToStorage()` / `loadStateFromStorage()` / `applyLoadedState()`
- **Key**: `eshare-devops-dashboard-state` (DEV/PROD separated)
- **What's persisted**: Current view, all dashboard filter states, sort states, collapse states, chart filter selections
- **Sync after load**: `stateWasLoaded` flag triggers `syncGenericFilterDropdowns()` to update checkbox UI

---

## Data Schema
The dashboard expects specific field names. See `README.md` for the complete schema.
