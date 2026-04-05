// What's New changelog - shown to users when a new version is deployed
// Add new entries at the TOP of the array (newest first)
// Each entry: { version: number, title: string, bullets: string[] }
window.DASHBOARD_CHANGELOG = [
    {
        version: 249,
        title: 'Power Automate Flow Fix & Version Control',
        bullets: [
            'Fixed WorkItemLinks data truncation — replaced Foreach+Append pattern with Compose+union(), restoring 15,400 links (was truncated at 10,000)',
            'Flow runtime reduced from 45–270 minutes to 13 seconds per run',
            'New flow version control: import-flow.sh and copy-flows.sh scripts with automatic PAT redaction',
            'Both flow definitions now tracked in flows/ directory (diff-friendly, secrets redacted)',
            'Recurrence intervals updated: ALL Items every 3 min, WorkItemLinks every 5 min (88% of action budget)',
            'Comprehensive Power Automate documentation: README_PowerAutomate.md covers both flows, action budgets, content throughput, and reconstitution'
        ]
    },
    {
        version: 248,
        title: 'Releases Dashboard Generic Filter Migration',
        bullets: [
            'Migrated Releases Dashboard filters from inline code to generic infrastructure — all 11 filter types now use shared components',
            'New generic filter builders: Type (4 composite categories), Progress Status (single-select with 5 statuses), Bug Owner (new to Releases)',
            'Cross-filter aware dropdowns — each dropdown shows counts filtered by all OTHER active filters',
            'Consolidated Bug Type from 3 raw ADO values to 2 derived categories (Customer Bug, Internal Bug) across all dashboards',
            'State persistence: automatic migration from old singular keys to new plural keys on load',
            'Removed ~500 lines of dead inline filter code, replaced with generic populateGenericFilterDropdowns() and applyGenericSecondaryFilters()'
        ]
    },
    {
        version: 247,
        title: 'Spec Kit Onboarding & GitHub Flow Migration',
        bullets: [
            'Onboarded GitHub Spec Kit for structured feature specification, planning, and implementation',
            'Established project constitution with 9 principles covering generic infrastructure, theme system, regression testing, and more',
            'Migrated branching model from single tony-dev branch to Standard GitHub Flow (per-feature branches from main)',
            'Rewrote dev-status.sh to be branch-agnostic — works with any feature branch, not just tony-dev',
            'Updated all workflow documentation (copilot-instructions.md, CLAUDE.md, GIT-WORKFLOW.md) for new branching model',
            'Pre-migration state archived at git tag pre-speckit for rollback if needed'
        ]
    },
    {
        version: 246,
        title: 'Unified Modal Resize Fix & Customer Editing',
        bullets: [
            'Fixed regression where horizontal (left/right pane) and vertical (description/discussion) resize handles in the Unified Modal stopped responding to drag',
            'Added inline customer editing in the Unified Modal header — click any customer badge to add/remove customers via a multi-select picker with search',
            'Items without a customer now show a "+ Customer" button in the modal header for quick assignment'
        ]
    },
    {
        version: 245,
        title: 'Releases Dashboard Performance Fix',
        bullets: [
            'Fixed Clear Filters taking up to a minute on Releases Dashboard — now near-instant',
            'Eliminated redundant renders: Clear All now resets all filters in one pass instead of triggering 3-4 separate render cycles',
            'Cached org chart map lookup: built once per render instead of once per bug (~728× reduction)',
            'Added short-circuit for cross-filter dropdown population when no filters are active',
            'Fixed uncaught TypeError in generic filter handlers for dashboards without filters() registered'
        ]
    },
    {
        version: 244,
        title: 'Customers Dashboard: Quarterly Flow & Aging Improvements',
        bullets: [
            'Quarterly Flow Summary table: shows issue flow by priority (P1–P4) with Start of Quarter, Added, Closed, End of Quarter columns — click any cell to filter the issues table',
            'Unique Customers column in quarterly table with popup showing per-customer breakdown — click a customer to filter to their items',
            'Issue Aging Distribution: closed/done items now limited to past quarter for accurate aging; open items show all ages',
            'Average age display on histogram (e.g., "Avg: 8.6w") with item count',
            'Click-to-filter toggle on aging bars — click a bar to filter, click again to clear; active bar highlighted with cyan outline',
            'Issue Trend chart aligned to same rolling-quarter date range as Quarterly Flow Summary',
            'Fixed Capacity Dashboard crash caused by variable shadowing isCustomerBug function',
            'Corrected hosting documentation: GitHub Pages, not SharePoint'
        ]
    },
    {
        version: 243,
        title: '@Mention Scanning Optimization',
        bullets: [
            'Incremental comment scanning: batch-fetches comment counts first, then only fetches full comments for items with new comments — reduces API calls from ~6,500 to ~66 on subsequent loads (99% reduction)',
            'First page load builds the comment count cache; subsequent loads complete in seconds instead of minutes',
            'Fixed 403 Forbidden error when saving mention cache to SharePoint — removed SharePoint write, localStorage is now the sole cache'
        ]
    },
    {
        version: 242,
        title: 'Comparison Modal & Customer Pills',
        bullets: [
            'Comparison modal always shows the Issue in the left pane, regardless of which item was opened first',
            'Customer name pill now appears in Unified Modal and Comparison Modal for all work item types',
            'Customer pill shows "Customer:" label outside the pill with the customer name inside',
            'Added generic infrastructure guidelines to project instructions for filters, headers, and tables'
        ]
    },
    {
        version: 241,
        title: 'Generic Filter & Matching Infrastructure',
        bullets: [
            'Generic secondary filter function shared across all dashboards — eliminates duplicate filter logic',
            'Dashboard filter registry with generic handler helpers — reduces 284 if/else branches to centralized routing',
            'Generic Feature-Team matching utilities (getFeatureTeams, featureMatchesTeams) — consistent team detection via Delivery Slice area paths across all dashboards',
            'Generic Bug-Team matching utilities (bugMatchesTeams, bugMatchesIteration, getBugOwnerTeam) — consistent team detection via child Task area paths and Org Chart membership',
            'Generic bug type utilities (isCustomerBug, isInternalBug, getBugTypeCssClass, getBugTypeLabel) — replaces 42 inline string comparisons',
            'Teams dashboard: added Customer, Release, Tags columns to all tables; fixed bug categorization using canonical bugType field',
            'Teams dashboard: Contributing tables now show the owner\'s actual team name',
            'Removed deprecated team estimation fields (frontendEstimation, etc.) — all effort tracking now uses Task originalEstimate',
            'Consolidated column width persistence into generic auto-save — removed ~100 lines of per-dashboard boilerplate'
        ]
    },
    {
        version: 240,
        title: 'New Teams Dashboard',
        bullets: [
            'New Teams dashboard for team leads — unified view of Features and Bugs, distinguishing owned vs. contributing items',
            'Feature ownership based on Assigned To matching team members from the Org Chart',
            'Six tables: Features Owned/Contributing, Customer Bugs Owned/Contributing, Internal Bugs Owned/Contributing',
            'Cut line status showing committed vs. backlog items per iteration',
            'Full generic filter bar: Search, Iteration, Release, Customer, Priority, State, Tag, Team, Bug Owner, Assignee',
            'Drag-to-reorder rows to change ADO backlog priority',
            'Progress column with percentage, effort, and validation warnings (same as all other dashboards)',
            'Generic table auto-persistence: sort state and column widths now auto-save to localStorage — no per-dashboard boilerplate needed',
            'Previous Teams view moved to Reports → Teams (archive)'
        ]
    },
    {
        version: 239,
        title: 'Universal Cross-Dashboard Search',
        bullets: [
            'Search box now finds work items across ALL dashboards, not just the current one',
            'Dropdown appears after 3+ characters with results grouped by scope: current view, hidden by filters, related items, other dashboards, and hierarchy',
            'Click a result to scroll to it, open the Unified Modal, or switch dashboards automatically',
            'Deep search walks parent/child and Related links to surface connected items',
            'Epics, Key Results, and Objectives appear in a Hierarchy group with child counts'
        ]
    },
    {
        version: 238,
        title: 'Customers Dashboard: CS Owner & Assignee Filters, OKR Column Click-to-Filter',
        bullets: [
            'Added CS Owner filter dropdown to the Customers dashboard sticky header',
            'Added Assigned To filter dropdown to the Customers dashboard sticky header',
            'Both filters support multi-select, search, cross-filter aware counts, and state persistence',
            'ER Prioritization: Click OKR column headers to filter by tag prefix (toggle on/off, with visual highlight)',
            'Fixed cross-filter dropdown counts to respect Insight card and heatmap cell filters'
        ]
    },
    {
        version: 237,
        title: 'OKR Reordering, Mugshots, Comparison Modal Fixes',
        bullets: [
            'Roadmap OKR Summary: Drag-and-drop tag boxes within each column to reorder manually; order persists across refreshes',
            'New mugshots for Tom Porter, George Spiliakos, George Moschoglou, Michael Dendrinos, Timothy S Papakyrikos',
            'Comparison Modal: Fixed field row misalignment when panels have different header heights',
            'Removed debug console output from Release Progress Tracking'
        ]
    },
    {
        version: 236,
        title: 'Comparison Modal: Sync Arrow Realignment After Tag Edit',
        bullets: [
            'Fixed sync arrows drifting out of alignment after editing tags in the Comparison Modal',
            'Arrow row heights now recalculate after any field edit to match updated field row sizes'
        ]
    },
    {
        version: 235,
        title: 'Comparison Modal: Editable Tags Row',
        bullets: [
            'New Tags row in Comparison Modal between Priority and Release — view all tags as pills on each side',
            'Click to edit tags via searchable multi-select checkbox dropdown, saved directly to ADO',
            'Sync arrows merge tags (additive) — clicking ← or → adds the other side\'s tags without removing existing ones'
        ]
    },
    {
        version: 234,
        title: 'Customers: No OKR Filter Fixes',
        bullets: [
            '"No OKR" filter now correctly shows only Enhancement Requests (not Bug Issues)',
            '"No OKR" toggle highlights when active and toggles on/off like "No CS Tag"',
            'Clicking a CS tag in the No OKR column (e.g. High Value × No OKR) now correctly filters to that intersection'
        ]
    },
    {
        version: 233,
        title: 'Comparison Modal: Light Mode & Arrow Alignment Fixes',
        bullets: [
            'Light mode: "Compare with Bug/Feature" button now uses darker teal color for better contrast',
            'Sync arrow alignment: arrow buttons in the center column now align precisely with their corresponding field rows',
            'Fixed horizontal scrollbar in sync column: compact buttons and hidden overflow ensure arrows are always visible'
        ]
    },
    {
        version: 232,
        title: 'Comparison Modal: Discussion Copy & Sticky Headers',
        bullets: [
            'Copy discussion comments between sides: "📋 Copy All" copies all comments with attribution, individual 📋 button on each bubble for single-comment copy',
            'Sticky headers in Comparison Modal: header, badges, owner info, and field rows stay pinned when scrolling down to descriptions and discussions',
            'Synchronized scroll across left panel, sync column, and right panel — all three columns scroll together',
            'Inline field editing: State, Priority, and Release/Target Date editable via dropdown pickers directly in the Comparison Modal',
            'State sync guardrails: incompatible states blocked with disabled arrows and explanatory tooltips (e.g. "Triaged" cannot sync to Bug)'
        ]
    },
    {
        version: 231,
        title: 'Comparison Modal Editing & State Guardrails',
        bullets: [
            'Editable fields in Comparison Modal: State, Priority, and Release/Target Date can now be edited inline via dropdown pickers — same as Unified Modal',
            'Release & Target Date edited as paired values: selecting a release automatically sets the matching target date',
            'State sync guardrails: incompatible states are blocked when syncing between work item types (e.g. "Triaged" cannot sync to a Bug). Invalid arrows appear disabled with explanatory tooltip',
            'Copy description between sides: "📋 Copy from [Type] [ID]" button in each description header copies content to the other item',
            'Copy discussion comments: "📋 Copy All" button copies all comments to the other item with attribution. Individual 📋 button on each comment for single-entry copy',
            'Full description editing in Comparison Modal: edit button, rich text toolbar, save/cancel — matching Unified Modal',
            'Full discussion editing in Comparison Modal: comment bubbles with edit buttons, comment editor with @mentions and #mentions',
            'Fixed duplicate relationship rows: Child dedup check prevents ADO dual-link entries from showing the same child twice',
            'Generic comment editor refactor: container-scoped lookups replace global IDs, enabling multiple editors on same page'
        ]
    },
    {
        version: 230,
        title: 'Relationship Fixes & Side-by-Side Comparison Modal',
        bullets: [
            'New Comparison Modal: side-by-side view for related Issue↔Feature and Issue↔Bug pairs with field sync arrows',
            'Compare button appears in Unified Modal when a related counterpart exists (ER↔Feature, Bug Issue↔Bug)',
            'One-click field synchronization: State, Priority, Release Version, and Target Date sync immediately to ADO',
            'Each panel shows full header with type/state/priority badges, owner mugshots, and category pills — matching Unified Modal style',
            'Descriptions and discussions load side-by-side for easy comparison',
            'Breadcrumb navigation: closing comparison modal returns to the source Unified Modal',
            'Clicking insight-filtered table rows opens comparison modal directly',
            'Fixed relationship editing: Parent link type now handled correctly (ADO exports both Child and Parent entries)',
            'Relationship changes persist across auto-refresh via pending link edits mechanism'
        ]
    },
    {
        version: 229,
        title: 'Staff Team Utilization & Customers Relationship Insights',
        bullets: [
            'Staff team now included in Tasks utilization — assignee filter correctly infers team for Staff members like Andreas Porevopoulos',
            'Customers Insights section shows 4 new relationship warnings: ERs with no Feature, ERs inconsistent with Feature, Customer Bugs with no Bug, Customer Bugs inconsistent with Bug',
            'Clicking any relationship insight filters the Issue Details table to show only affected items',
            'Inconsistency detection compares Release Version, Target Date, and terminal state (Done/Closed) between Issue and linked work item'
        ]
    },
    {
        version: 228,
        title: 'Toggle Defaults, Tasks Utilization & Modal Enhancements',
        bullets: [
            'Active toggle now defaults to ON across Roadmap, Customers, and Bugs dashboards — automatically filters to non-Done/Closed items on first load',
            'Bugs dashboard Active/Unreleased toggle buttons moved from stats row to sticky filter header for consistency',
            'Clear All button shows only when filters deviate from the Active-ON baseline; re-activates Active toggle after clearing',
            'Tasks dashboard: filtering by Assigned To now shows Team Utilization and Individual Breakdown (infers team from org chart)',
            'Tasks Individual Breakdown table has a Total row with summed days and recalculated utilization percentages',
            'Selected assignee highlighted in Individual Breakdown with cyan left border',
            'Tasks utilization calculation fixed — Work Log Summary now uses assignee count as denominator when filtering by assignee, matching Individual Breakdown',
            'Gap days calculation fixed — now counts all business days in work log entry date range instead of just the start date',
            'Description images in Unified Modal show fallback placeholder with "View in ADO" link when images fail to load on small screens',
            'Click any description image to open a full-screen lightbox overlay (95% viewport, click or Esc to close)',
            'Assigned To column added to all modal relationship tables (Delivery Slices, Relationships, Progress)',
            'Deep search now opens the full Unified Modal with child item highlighted instead of simple progress popup',
            'Warning banners in Unified Modal are now clickable — see which specific items have issues',
            'Fixed column width drift during auto-refresh, at-mention modal scroll bouncing, and deep search re-trigger',
            'Releases Tags columns show all tags with full inline editing; legacy field fallbacks removed',
            'Release picker search filter and auto-refresh persistence; customer name badges in Unified Modal header'
        ]
    },
    {
        version: 227,
        title: 'Utilization Fixes, Modal Enhancements & Mugshot Fix',
        bullets: [
            'Fixed utilization formula: individual % now uses days logged ÷ business days (was showing 100% for partial-day contributors)',
            'External contributors excluded from team utilization math when team filter active, shown with "↗ external (not included in util)" badge',
            'Multi-team members (e.g., leads of two teams) now correctly appear in both teams\' Individual Breakdown tables',
            'Period selector moved from Work Log Summary to sticky header for better visibility',
            'Fixed mugshots not showing in Roadmap, Bugs, Releases, and Capacity dashboard tables',
            'Unified Modal: Cmd/Ctrl+K inserts hyperlinks in description and comment editors',
            'Unified Modal: Resizable divider between Description and Discussion panes',
            'Unified Modal: Priority badge (color-coded P1-P4) shown in modal header',
            'Unified Modal: Effort estimate badge shown for Delivery Slices in modal header',
            'Unified Modal: DS Owner with mugshot shown for Delivery Slices in modal header',
            'Unified Modal: Team column added to all relationship and delivery slice tables',
            'Unified Modal: Set Release dropdown now works correctly (was clipped by overflow)',
            'Scroll position preserved during auto-refresh across all dashboards'
        ]
    },
    {
        version: 226,
        title: 'Tasks Dashboard Enhancements',
        bullets: [
            'Team Utilization Breakdown section: Own Team Work, Cross-Team Contributions, External Help with clickable detail chips',
            'Individual Breakdown table showing per-member effort, own/cross utilization %, and gap days',
            'Utilization formula rework: uses actual logged days (not calendar capacity) to prevent empty-week inflation',
            'Performance optimization: cached work log parsing and parent resolution for instant period changes',
            'Stat cards (Tasks Worked, Effort Logged, Open, Completed, Orphan) now scoped to selected time period',
            'Work Log Summary shows #ID: Title for all parent types; clicking task ID opens Unified Modal',
            'Standardized table modals: utilization and member detail modals match @mention notification modal styling with resize persistence',
            'Shared modal resize function used by all three modal types (mention, utilization, member)',
            'Mugshots added to all person-name columns (Assigned To, CS Owner, Bug Owner) across all dashboard tables',
            'Unified Modal header now shows Area Path (Team) next to Assigned To',
            'Task fields editable in Unified Modal: State, Assigned To, Iteration, Team, Task Type, Priority',
            'Task Parent link in Unified Modal now opens parent in Unified Modal instead of ADO'
        ]
    },
    {
        version: 225,
        title: 'Updated Mugshots',
        bullets: [
            'Added profile photos for Mark Cassetta, Konstantinos Gkofas, Sangeet Saha, Athina Kalampogia, Vasiliki Tzanaki, and Sai Kishore Punagani'
        ]
    },
    {
        version: 224,
        title: 'Add Relationship & Modal Category Pills',
        bullets: [
            'New "+" button in the Relationships section header to add a new relationship',
            'Search work items by ID or title with a relationship type dropdown (Parent, Child, Related)',
            'Issues now show Ticket Category pill (Enhancement Request, Bug, Task) in modal header',
            'Bugs now show Bug Type pill (Customer Related, Internal) in modal header before architecture tags'
        ]
    },
    {
        version: 223,
        title: 'Fix Duplicate @Mention Entries for Team Leads',
        bullets: [
            'Team leads who manage multiple teams (e.g., Andreas Davros — Frontend & UX Design) no longer appear twice in the @mention dropdown',
            'All team leads now display a "Team Lead" indicator with their team name(s) in the @mention suggestions',
            'Fixed isLead detection for leads whose formal name differs from their common name (e.g., Thanos Terzis / Athanasios Terzis)'
        ]
    },
    {
        version: 222,
        title: 'Modal Contextual Tags & Pill Breadcrumbs',
        bullets: [
            'Unified Modal now shows contextual tags in the header: OKR + CS tags for Features, CS tags for Enhancement Requests, Architecture tags for Bugs, Iteration Path for Tasks',
            'Clicking a relationship pill in the modal header now navigates with breadcrumb trail — click the back arrow to return to the previous item',
        ]
    },
    {
        version: 221,
        title: 'Clickable Relationship Pills',
        bullets: [
            'Relationship pills in table Title columns (Feature↔Issue, Bug↔Issue) now correctly open the Unified Modal for the linked item when clicked',
            'Fixed a scoping bug where pill click handlers could not access work item data, causing clicks to silently fail',
        ]
    },
    {
        version: 220,
        title: 'Modal Mugshots, Iteration Column & Release Mismatch Warnings',
        bullets: [
            'Mugshot photos in Unified Modal header — Bug Owner and Assigned To now show profile photos (same as Org Chart) instead of initials',
            'Iteration Path column added to the Relationships section in the progress panel, showing the iteration for each related item',
            'Release mismatch warnings — when a Bug and its related Issue (or Feature and its related ER) have different Release Version or Target Date, a yellow warning banner appears with one-click alignment buttons to sync them',
        ]
    },
    {
        version: 219,
        title: 'Relationship Type Editing & Bug Type Badges',
        bullets: [
            'Bug type badges in Relationships tables — Bugs now show "Customer", "Internal", or "Infra" badge next to the Type column so you can quickly identify bug categories',
            'Editable relationship types — click any ⬆️ Parent / ⬇️ Child / 🔗 Related cell in the Relationships table to change the relationship type directly in Azure DevOps',
            'Relationship changes are synced to ADO in real-time via the API — the old link is removed and the new link is added in a single operation',
        ]
    },
    {
        version: 218,
        title: 'Relationship Pills & Modal Improvements',
        bullets: [
            'Relationship pills now open the Unified Modal instead of ADO — click Bug, Issue, or Feature pills to navigate within the dashboard',
            'Bug Issues show "no Bug" warning pill, ER Issues show "no Feature" warning pill, Customer Bugs show "no Issue" warning pill when related items are missing',
            'Issue pill added to Bugs Dashboard title column for Customer Bugs, and Bug pill added to Releases Issues table for Bug Issues',
            'Unified Modal header shows Bug Owner + Assigned To for Bugs, CS Owner + Assigned To for Issues',
            'Renamed "Owner" column to "Assigned To" in Delivery Slices and Relationships modal sections',
            'Unified Modal now always shows full progress panel (Progress by Team, Delivery Slices) — previously missing when opened from Capacity Dashboard',
        ]
    },
    {
        version: 217,
        title: 'Inline Edit Fixes',
        bullets: [
            'Multi-select picker (Customers, Tags) — clicking the option text now toggles the checkbox, not just the checkbox itself',
            'Inline edits now persist across auto-refresh cycles — edited values stay visible for up to 5 minutes while waiting for ADO sync confirmation',
            'Inline edit picker now appears above modals — editing works correctly in @mention notification panel and Reports popup tables',
        ]
    },
    {
        version: 216,
        title: 'Inline Field Editing & Notification Modal Fixes',
        bullets: [
            'Inline editing for 10 work item fields — click any editable cell to change State, Assigned To, Team, Tags, Customers, Release, Category, CS Owner, Bug Type, or Bug Owner directly in any table',
            'Single-select pickers for State, Assigned To, Team, Category, CS Owner, Bug Type, Bug Owner — dropdown with search, current value highlighted',
            'Multi-select pickers for Tags and Customers — checkboxes with search and Apply button',
            'Release picker — paired version + date selection with search',
            'Tags filtered by work item type: Bugs show architecture tags only, Features/Issues show OKR and CS tags',
            'Editable cells available across all dashboards: Roadmap, Customers, Bugs, Releases, Reports popup, and @mention notification tables',
            'Roadmap Team Summary section now expanded by default',
            'Notification modal resize handle — drag the bottom-right corner to resize, size persists across sessions',
            'Clicking a notification row now opens the Unified Modal and returns to the notification panel on close',
        ]
    },
    {
        version: 215,
        title: 'Reports Popup Tables, Responsive Columns & Breadcrumbs',
        bullets: [
            'Reports chart popup now shows a full generic table with all 14 columns, relationship pills, architecture tags, state badges, and progress bars — click any row to open the Unified Modal',
            'Reports popup modal is larger by default (92vw × 85vh) and resizable via drag handle — column widths persist to localStorage',
            'Column widths now stored as percentages instead of pixels — layouts scale correctly across ultrawide, laptop, and small monitors',
            'Reports Dashboard — full filter suite: Search, Release, Customer, Priority, State, Tag, Team, Bug Type, Aging, Bug Owner, Assigned To with sticky header and Clear All button',
            'Filter dropdowns now expand to fit content — no more truncated team names like "Customer Success"',
            'Relationship rows in Unified Modal are now clickable — click any Feature, Bug, Epic, or other work item to open its modal with breadcrumb navigation',
            'Title columns now wrap text instead of truncating with ellipsis — see full titles without hovering',
            'Offline notification cache — production syncs mention cache to SharePoint for localhost development and testing',
        ]
    },
    {
        version: 214,
        title: 'Capacity Bug Effort Fix',
        bullets: [
            'Fixed Feature→Bug effort calculation in Capacity Dashboard — now uses child Task iterations instead of Bug iteration to determine effort per iteration',
            'Bug estimation fields are not per-iteration; the fix looks at grandchild Tasks filtered by iteration, matching the standalone Bug effort logic',
            'Affects 6 Features in March with cross-iteration bug tasks — adds ~18d Backend and ~21d QA previously invisible effort',
        ]
    },
    {
        version: 213,
        title: 'Notification Cache & Persistence',
        bullets: [
            'Notification scan results now cached in localStorage — badge appears instantly on page load without re-scanning',
            'Auto-refresh skips re-scan when cache is complete, just refreshes item state/title from latest data',
            'Partial scan results saved every 10 items — progress survives page reload during long scans',
            'Rate-limited scans resume from cached results on next page load',
        ]
    },
    {
        version: 212,
        title: 'Combined Release Column',
        bullets: [
            'Release Version and Target Date merged into a single "Release" column across all generic tables — version on top, date below in smaller muted text',
            'Saves horizontal space in Roadmap, Bugs, Customers, Releases, Capacity, and Validation tables',
            'Release column positioned after Progress (or after Priority in Customers table)',
            'Fixed generic table sort function that was using undefined stateOrder variable for numeric columns',
        ]
    },
    {
        version: 211,
        title: '@Mention Notification Fix',
        bullets: [
            'Fixed @mention notification scan finding 0 results — detection now matches the native ADO mention format (data-vss-mention attribute) in addition to the dashboard editor format',
        ]
    },
    {
        version: 210,
        title: 'Task Detail Modal',
        bullets: [
            'Click any Task row in the Unified Modal progress section to open a detailed Task view',
            'Left panel shows description and discussion with full edit support',
            'Right panel shows progress bar, key fields (estimate, completed, remaining, state, assignee, iteration, team, priority), and worklog entries table',
            'Stacked modal design — parent modal stays visible underneath with darker backdrop',
            'Escape key closes only the topmost modal; clicking the #ID link still opens ADO directly'
        ]
    },
    {
        version: 209,
        title: '@Mention Notification Bell',
        bullets: [
            'New 🔔 bell icon in the header shows how many work items mention you',
            'Scans descriptions and discussion comments for @mentions of your name',
            'Red badge pill shows unread mention count — click to open notification table',
            'Table shows Work Item ID, Title, Type, State, and where the mention was found',
            'Click any row to open the Unified Modal with the @mention highlighted in cyan',
            'Viewed mentions are automatically cleared; use "Clear All" or "Show Cleared" to manage',
            'Background scanning with rate-limit detection and retry with exponential backoff'
        ]
    },
    {
        version: 208,
        title: 'Edit Discussion Messages',
        bullets: [
            'Hover over any discussion message in the Unified Modal to reveal a ✏️ edit button',
            'Click to inline-edit the message with full rich text toolbar and @mention/#mention support',
            'Save updates the comment directly in Azure DevOps',
            'Press Escape or Cancel to discard changes'
        ]
    },
    {
        version: 207,
        title: 'Editor List Fix & @Mention Common Names',
        bullets: [
            'Fixed bullet and numbered lists rendering off-screen in description and discussion editors',
            'Lists now have proper left padding so they stay visible within the editor area',
            '@mentions now display common names (e.g., "Thanos Terzis") instead of formal ADO names (e.g., "Athanasios Terzis")',
            'Mention dropdown also searches by formal name so either name works when typing'
        ]
    },
    {
        version: 206,
        title: 'Comment Editor Always Visible',
        bullets: [
            'Fixed comment editor text box sometimes not appearing in the Unified Modal discussion panel',
            'Editor now sits below discussion bubbles in a fixed position — always visible regardless of discussion content height'
        ]
    },
    {
        version: 205,
        title: 'Comment Editor Sticky Toolbar',
        bullets: [
            'Toolbar with Bold, Italic, list buttons, and Save now stays visible at the bottom as you type — no more scrolling to find Save',
            'Comment editor auto-expands with more room before internal scrolling kicks in'
        ]
    },
    {
        version: 204,
        title: 'Mention Dropdown Enter Key',
        bullets: [
            'Press Enter to select the first match in @mention and #mention dropdowns — no need to arrow-key or click when the match is already visible'
        ]
    },
    {
        version: 203,
        title: 'CSP Fix for @Mention Identity Resolution',
        bullets: [
            'Fixed @mention identity resolution failing on production — Content Security Policy now allows requests to vssps.dev.azure.com',
            '@mentions now properly resolve ADO identity GUIDs for notifications instead of falling back to bold text'
        ]
    },
    {
        version: 202,
        title: 'Unified Modal – Edit Description & Discussion',
        bullets: [
            'Edit description directly in the Unified Modal with rich text toolbar (Bold, Italic, Lists)',
            'Add new discussion comments — saved to Azure DevOps with your name and timestamp',
            '@mention people: type @ to search team members, resolves ADO identity for notifications',
            '#mention work items: type # to search by ID or title, inserts clickable link',
            'Draggable resize handle between left and right panels in the Unified Modal',
            'Localhost dev mode: editor UI visible for testing (saves require SharePoint auth)'
        ]
    },
    {
        version: 201,
        title: 'Nav Tab Responsive Layout',
        bullets: [
            'Fixed nav tabs overflowing the page when many tabs are present',
            'Tabs now shrink to fit on one line and wrap to a second row on narrower screens',
            'All dashboard tabs remain visible at every viewport width'
        ]
    },
    {
        version: 200,
        title: 'Reports Tab – Bug Aging Report Enhancements',
        bullets: [
            'New Reports tab: Bug Aging Report scoped to bugs whose direct parent is a customer Issue',
            'MTTR Chart: Mean Time to Resolution by priority (P1–P4), month-over-month with configurable 3/6/12-month period selector',
            'Open Bug Aging Chart: Open bugs by age bucket (0–7d, 8–30d, 31–60d, 61–90d, 90+d) and priority — stacked bar chart',
            'Customer filter: top-level dropdown filters both charts and summary stats to a single customer',
            'Click any bar in either chart to open a popup table showing Bug #, Title, Days Open, Customer, Team, and Release for the matching bugs',
            'P1 and P2 trend lines overlaid on MTTR chart to show month-over-month progression'
        ]
    },
    {
        version: 199,
        title: 'Capacity Warnings Search Fix',
        bullets: [
            'Fixed warnings badge disappearing when using search filter — items not on the board (e.g. committed but no work items in iteration) are now found via simple title/ID match instead of deep search'
        ]
    },
    {
        version: 198,
        title: 'Capacity Warnings Improvements',
        bullets: [
            'Warnings modal respects all sticky header filters (Bug Owner, Assignee, Customer, Priority, State, Tag, Team)',
            'Warnings modal redesigned with sortable table columns and 3 collapsible sections for easier triage',
            'Warnings modal enlarged (85vw × 80vh) and user-resizable via drag handle'
        ]
    },
    {
        version: 197,
        title: 'Modal Fixes & Capacity Warnings',
        bullets: [
            'Progress by Team table: moved State column between Actual and Progress for better readability',
            'Fixed release date display in Unified Modal header showing one day earlier than expected (timezone parsing issue)',
            'Capacity Dashboard: warning badge next to Committed Work Plan header detects 6 types of inconsistencies',
            'Warnings modal with per-item remediation — add/remove committed iterations, set effort estimates inline, all via ADO API'
        ]
    },
    {
        version: 196,
        title: 'Tasks Dashboard & Unified Modal Editing',
        bullets: [
            'Assigned To filter now updates all sections — Work Log Summary, Team Summary, Insights, Charts, and Table all respond to assignee selection',
            'Assignee dropdown shows names only (without email addresses)',
            'Utilization % metric in Work Log Summary stats row — Total Logged ÷ (business days × engineers)',
            'Utilization % on each Team Summary card below participation rate',
            'Work Log "By Work Item" links open the Unified Modal instead of navigating to ADO',
            'Parent badges (Features/Bugs) in "By Team" section also open the Unified Modal',
            'Committed Iterations shown in Unified Modal header — add/remove directly with live ADO sync',
            'Release Version & Target Date editable in Unified Modal — pick from paired cascading list values, saved to ADO',
            'Priority column editable in all tables — click any priority cell to change P1–P4, saved to ADO',
            'Fixed HTML escaping for assignee names containing angle brackets'
        ]
    },
    {
        version: 195,
        title: 'Unified Modal Enhancements',
        bullets: [
            'Owner display in modal header — initials avatar and name shown next to the title',
            'Tag pills in header — OKR and CS tags for Features, Architecture tags for Bugs',
            'Work item ID is now a clickable hyperlink to Azure DevOps (replaced Open in ADO button)',
            'Release version and target date shown in modal subtitle with 📦 and 📅 icons',
            'State badge added to modal subtitle showing item state',
            'Worst-case state per team in Progress by Team — shows least-progressed child item state per team row',
            'Unified modal now looks identical when opened from Capacity dashboard or generic tables'
        ]
    },
    {
        version: 194,
        title: 'Capacity Dashboard Bulk Commit by Release',
        bullets: [
            'New "Commit by Release" button in the Backlog Work Candidates column header',
            'Dropdown shows release versions with item counts from current backlog candidates',
            'Select one or more releases and click "Commit X items" to bulk-move them to the Committed Work Plan',
            'Uses the same local change tracking and ADO sync workflow as individual checkboxes'
        ]
    },
    {
        version: 193,
        title: 'Capacity Dashboard Drag-to-Reorder',
        bullets: [
            'Drag planning items to reorder Backlog Priority in both Backlog Candidates and Committed Plan panels',
            'Reordering is scoped within sections — Customer Bugs, P1-P4 Features, and Internal Bugs stay in their own groups',
            'Reuses existing ADO write-back, pending sync indicators, and 5-minute timeout with Revert'
        ]
    },
    {
        version: 192,
        title: 'Column Width Persistence Fix',
        bullets: [
            'Fixed column widths not persisting across page refreshes — resized columns now stay at their custom widths',
            'Root cause: switching views caused hidden table headers to report 0px width, overwriting saved values'
        ]
    },
    {
        version: 191,
        title: 'Drag-Reorder Pending Sync',
        bullets: [
            'Dragged rows now show pending sync indicator (orange border + ⏳) until ADO confirms the new priority',
            'Priority changes persist across auto-refresh and manual refresh — items stay in their new position',
            'Sync errors after 5 minutes show red warning with a Revert button to restore original priority',
            'Hard refresh (Cmd+Shift+R) clears pending state and reloads from ADO'
        ]
    },
    {
        version: 190,
        title: 'Drag-to-Reorder Priority & Fixes',
        bullets: [
            'Drag any table row up or down to change its Backlog Priority — new position is saved to Azure DevOps automatically',
            'Drag-to-reorder is available on all dashboards (Roadmap, Customers, Bugs, Releases) when sorted by default priority order',
            'Visual feedback: cyan drop indicator, saving animation, green flash on success, red flash on failure',
            'Bugs dashboard now defaults to Backlog Priority sort order (consistent with all other dashboards)',
            'Improved markdown rendering in work item modal — bold, lists, links, and code blocks now display correctly in description and conversation tabs'
        ]
    },
    {
        version: 188,
        title: 'Unified Work Item Modal',
        bullets: [
            'Consolidated 3 separate modals (row click, 💬 conversation, progress bar) into a single two-panel modal',
            'Left panel shows work item description and conversation thread (requires authentication)',
            'Right panel shows relationships, progress summary, team breakdown, and collapsible delivery slice/bug/task details',
            'All sections in the right panel have consistent bordered styling',
            'Clicking anywhere on a table row opens the unified modal — no more separate click targets',
            'Removed hyperlink on work item ID and progress bar hover highlight for cleaner UX'
        ]
    },
    {
        version: 187,
        title: 'Multi-Value Column Separators',
        bullets: [
            'Customer and Architecture columns now show dotted line separators between entries, matching the Tags column style',
            'Added Table-Columns.md reference to instruction documentation'
        ]
    },
    {
        version: 186,
        title: 'Standardized Table Columns',
        bullets: [
            'Standardized columns across all 7 generic tables (Releases, Roadmap, Customers, Bugs) for consistency',
            'Added Priority column to all Releases tables (Features, Issues, Customer Bugs, Internal Bugs)',
            'Added Tags column to Releases Features and Issues tables',
            'Added Assigned To column to Releases Issues and Customers Issue Details tables',
            'Added Team column to Roadmap Feature Details and Bugs Bug Details tables',
            'Added Architecture column to Bugs Bug Details table',
            'Tags, Customer, and Architecture columns now display each value on a separate line',
            'New Table-Columns.md reference document defines the standard column spec'
        ]
    },
    {
        version: 185,
        title: 'Version Merge Feature',
        bullets: [
            'New 🔀 merge button in Versions modal lets you move all work items from one version/date pair to another',
            'Inline merge UI with target dropdown showing all available pairs',
            'Option to delete the source pair after merge (checked by default)',
            'Work items are bulk-updated with the target version and date via ADO API',
            'Picklist values synced before work item updates to avoid validation errors'
        ]
    },
    {
        version: 184,
        title: 'Persistent Column Widths',
        bullets: [
            'Removed 24-hour expiration on dashboard state — column widths, sort orders, filters, and scroll positions now persist indefinitely',
            'Previously, all saved preferences were silently cleared after 24 hours of inactivity'
        ]
    },
    {
        version: 183,
        title: 'Picklist Consistency Fix Actions',
        bullets: [
            'All consistency issues now listed individually (no more "+N more" summary)',
            'Fix Inconsistencies now shows per-issue choices: "Add to picklist" or "Remove from config"',
            'Stale picklist values can be removed or added to config with one click',
            'JSON internal repairs and picklist fixes handled as separate workflows'
        ]
    },
    {
        version: 182,
        title: 'Picklist Consistency Detection',
        bullets: [
            'Versions modal now detects when cascade config values are missing from ADO picklist fields',
            'Also detects stale picklist values that are no longer in the cascade config',
            'Picklist check runs automatically when opening the Versions modal (requires authentication)',
            'Issues appear in the existing consistency warning banner with "Fix Inconsistencies" repair action'
        ]
    },
    {
        version: 181,
        title: 'Versions Modal: Picklist Cleanup & Sort Fix',
        bullets: [
            'Deleting a version-date pair now removes stale values from the ADO picklist fields (previously only added)',
            'Editing a date now removes the old date value from the picklist when no other version uses it',
            'Edited/added entries now appear in sorted order in the cascading lists instead of appended at the end',
            'Work item bulk updates now run before picklist sync to avoid brief validation issues'
        ]
    },
    {
        version: 180,
        title: 'Bulk Work Item Updates on Version Edit/Delete',
        bullets: [
            'Editing a version-date pair now updates all assigned work items in Azure DevOps automatically',
            'Deleting a version-date pair clears the version and date fields from all assigned work items',
            'Confirmation dialog shows affected item counts by type (e.g., 10 Features, 10 Bugs) before updating',
            'Live progress indicator shows update status (e.g., "Updating 5/20...") during bulk operations',
            'Only changed fields are patched — editing just the date leaves version untouched and vice versa',
            'Dashboard data updates immediately after successful patches without waiting for auto-refresh'
        ]
    },
    {
        version: 179,
        title: 'Picklist Sync & Conversation Modal',
        bullets: [
            'Adding or repairing version/date pairs now automatically updates the ADO picklist field allowed values',
            'New 💬 icon next to every Work Item ID — click to view the ADO discussion thread in a popup',
            'Fixed Content Security Policy blocking ADO Extension Management API calls in production',
            'Fixed ADO data envelope parsing (read/save) so Versions modal displays and saves correctly',
            '⚠️ SharePoint write-back requires admin permission grant — save continues via ADO as primary'
        ]
    },
    {
        version: 178,
        title: 'Table Column Width Persistence',
        bullets: [
            'Column widths you resize in any table now persist across auto-refresh, tab switches, and page reloads',
            'Resizing one column now locks all column widths so the entire layout stays stable'
        ]
    },
    {
        version: 177,
        title: 'Live ADO Sync & Consistency Repair',
        bullets: [
            'Cascading lists now load directly from ADO as the single source of truth (SharePoint as fallback)',
            'Auto-refresh every 60 seconds picks up changes made by anyone in the ADO extension',
            'Bidirectional consistency check detects partial edits — ⚠️ warning badge on Versions link across all dashboards',
            'One-click "Fix Inconsistencies" button auto-repairs missing reverse mappings and saves to ADO + SharePoint'
        ]
    },
    {
        version: 176,
        title: 'Cascading Lists Phase 3: Edit & Write-Back',
        bullets: [
            'Versions modal now has Edit Mode toggle for adding, editing, and deleting version-date pairs',
            'Changes write back to both Azure DevOps Cascading Picklists extension and SharePoint in one save',
            'Concurrency control via __etag prevents overwriting concurrent edits',
            'Inline editing with validation (YYYYMM.X.X format, date format, duplicate prevention)',
            'Visual indicators for added (green), modified (cyan), and deleted (red strikethrough) rows with undo support'
        ]
    },
    {
        version: 175,
        title: 'ADO API Integration & Commit to ADO',
        bullets: [
            'Browser-based Azure DevOps API access via MSAL authentication',
            'Capacity Dashboard "Commit to ADO" button writes changes directly to ADO — no more manual CLI commands',
            'Read-merge-write pattern prevents overwriting concurrent edits from other users',
            'Per-item error tracking with partial failure support',
            'Automatic pending confirmation via auto-refresh after commit'
        ]
    },
    {
        version: 174,
        title: 'Estimate Warnings & Resize Handles',
        bullets: [
            'Fixed false "missing original estimate" warning on Features with Done/Closed Delivery Slices',
            'Table column resize handles now always visible with subtle gray indicator',
            'Workaround for Chromium/Edge macOS bug where hover state gets stuck after drag operations'
        ]
    },
    {
        version: 173,
        title: 'Clickable Date Issues Insight',
        bullets: [
            'Clickable "items with date issues" insight in Releases Dashboard filters to affected items'
        ]
    },
    {
        version: 172,
        title: 'Deep Search (Releases Dashboard)',
        bullets: [
            'Search for any child item (Delivery Slice, Bug, Task) by ID or title — parent Feature/Bug appears in table with progress popup auto-opening and highlighting the matched child',
            'Search for an Issue — both the Issue and related Feature(s) appear in results',
            'Search for a Feature — related Issue(s) also shown in the Issues table',
            '"Contains: #ID" / "Related: #ID" badges on table rows indicate how items were matched',
            'Issues table auto-expands when search returns Issues, re-collapses when search is cleared'
        ]
    },
    {
        version: 171,
        title: 'Releases Insights Interactivity',
        bullets: [
            'Clickable "Next" release insight — filters to the next upcoming release',
            'Clickable "needs release version" insight — filters to items missing a release',
            'Next release column highlighted in Items by Release chart with "Next" arrow label and theme-aware border',
            'Theme toggle now re-renders charts for instant color updates'
        ]
    },
    {
        version: 170,
        title: 'DS Estimate Fixes',
        bullets: [
            'Warning count for missing estimates now correctly checks Delivery Slice effort instead of task-level originalEstimate',
            'Removed misleading per-task Estimate column from DS task tables in progress popup — estimate is shown once at the DS header level'
        ]
    },
    {
        version: 169,
        title: 'Warning Count Fix',
        bullets: [
            'Fixed child estimate warning count to include all tasks with missing original estimate, not just those with work logged — count now matches what the progress popup displays'
        ]
    },
    {
        version: 168,
        title: 'Estimate Missing Display Consistency',
        bullets: [
            'Progress cell for items with missing estimates now shows "?% (Xd / ?d)" format instead of "Estimate missing", matching the normal progress display pattern with ? for unknown values'
        ]
    },
    {
        version: 167,
        title: 'Enhanced Warning Detection',
        bullets: [
            'Items with "Estimate missing" (red bar) now included in warnings filter and show ⚠️ icon',
            'New warning: child tasks with work logged but no original estimate bubble up to parent Feature/Bug',
            'New warning: deadline risk — items within 7 days of target date with less than 75% progress',
            'Multiple warnings now shown as separate banners in progress popup instead of single combined message'
        ]
    },
    {
        version: 166,
        title: 'Progress Popup Estimation Fix & Total Row',
        bullets: [
            'Fixed estimation source mismatch in Feature progress popup — Progress section and Summary Estimates table now use the same source (task originalEstimate with bug-level fallback)',
            'Added Total row to Progress by Team table in both Bug and Feature progress popups',
            'Fixed "Clear Filter" button in Releases dashboard blue filter bar not clearing Warnings filter'
        ]
    },
    {
        version: 165,
        title: 'Validation Drilldown Tables Refactored',
        bullets: [
            'New "Bugs Under Delivery Slices" validation check in Hierarchy group — identifies bugs parented to Delivery Slices instead of Features',
            'All 15 data quality drilldown tables now use the standard generic table format with pills, relationship badges, progress bars, and sortable columns',
            'Click any row in a drilldown table to open the full work item details modal with relationships and history',
            'Release Date Issues card retains its unique grouped card layout'
        ]
    },
    {
        version: 164,
        title: 'Show Unestimated Teams in Progress Popup',
        bullets: [
            'Teams with actual work logged but no estimation now appear in Progress by Team table with 0.0d estimated and red "No estimate" indicator',
            'Fixes incorrect overall progress percentage when child tasks belong to teams without estimation fields set (e.g., Bug #4221 showed 81% instead of 131%)',
            'Consistent "No estimate" display across Bug popup, Feature/Capacity popup, and Release Progress Summary'
        ]
    },
    {
        version: 163,
        title: 'Progress Popup Iteration & Team Scoping',
        bullets: [
            'Progress popup now scopes to the selected iteration and team filter from the Capacity dashboard',
            'New "Summary Estimates Across ALL Iterations" table at top of Feature progress popup with highlighted current iteration column',
            'Child Bugs\' team estimation fields now included in capacity effort calculations (row display and header bars)',
            'Added emoji indicators (📋 Delivery Slice, 🐛 Bug), team name, and state to all child items in the popup',
            'Added Assigned To and State columns to child task tables in progress popup',
            'Progress popup is now wider (1200px) and resizable by dragging the bottom-right corner',
        ]
    },
    {
        version: 162,
        title: 'What\'s New Popup Fix',
        bullets: [
            'Fixed What\'s New popup not appearing after a new version is deployed and detected via auto-refresh',
            'Auto-refresh now triggers a full page reload when a new version is detected, ensuring all new code and changelog entries are loaded',
        ]
    },
    {
        version: 161,
        title: 'Feature Progress includes Child Bugs',
        bullets: [
            'Internal bugs that are children of a Feature now roll up into the Feature\'s progress bar (e.g., "bug bash" Features now show accurate composite progress)',
            'Internal Bugs table no longer shows bugs that belong to a Feature — they appear in the Feature\'s progress instead',
            'Progress detail popup now shows both Delivery Slices and Child Bugs sections with individual progress bars',
        ]
    },
    {
        version: 160,
        title: 'Team Mapping & Clickable Progress',
        bullets: [
            'Fixed team mapping: UX Design and Govern teams now display correctly in Progress by Team (no more "Unknown" or duplicate "Governance" rows)',
            'Team names now display with proper casing (QA, DevOps, UX Design instead of Qa, Devops, Ux design)',
            'Click any team row in Progress by Team to filter tables below to that team\'s contributed items',
        ]
    },
    {
        version: 159,
        title: 'Auto-Update Detection',
        bullets: [
            'Dashboard now silently detects new versions during auto-refresh and shows the What\'s New popup without page reload',
            'Capacity Planning deep linking now updates the URL as you change filters',
        ]
    },
    {
        version: 158,
        title: 'Deep Linking & Shareable URLs',
        bullets: [
            'The browser URL now updates in real-time as you navigate and filter — share the exact view you\'re on by copying the URL',
            'Right-click any table row to "Copy link to item" — sends a colleague directly to that work item with a highlight animation',
        ]
    },
    {
        version: 157,
        title: 'Versions Modal',
        bullets: [
            'New "📅 Versions" link on every dashboard shows a searchable table of all release versions with their target dates',
            'Table auto-scrolls to the current date on open',
        ]
    },
    {
        version: 156,
        title: 'Issue Fields & Progress Tracking',
        bullets: [
            'Bug effort is now calculated from child Tasks — iteration-aware, like Features use Delivery Slices',
            'Added Bug Owner column to Releases dashboard for Customer and Internal Bugs tables',
        ]
    },
    {
        version: 155,
        title: 'Bug Effort Migration to Tasks',
        bullets: [
            'Bug estimation fields migrated to child Task estimates for more accurate effort tracking',
            'Capacity planning now uses Task iteration paths, allowing bugs to span multiple iterations',
            'Added fallback logic for release version and target date fields during migration period',
        ]
    }
];
