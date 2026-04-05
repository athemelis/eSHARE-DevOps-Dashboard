# Power Automate Flows — Azure DevOps Data Export

Two Power Automate flows export data from Azure DevOps to SharePoint as JSON files. The dashboard consumes these files to render work item data and relationships.

| Flow | Output File | Connector | Interval | Actions/run | Records |
|------|-------------|-----------|----------|-------------|---------|
| ADO ALL Items | `ALL Items.json` | ADO connector (built-in) | Every 3 minutes | 7 | ~7,100 work items |
| Export ADO WorkItemLinks | `WorkItemLinks.json` | HTTP + PAT | Every 5 minutes | 19 | ~15,400 links |

Both flows write to the same SharePoint folder (`/Shared Documents/Product Planning/`) and overwrite on each run. SharePoint maintains version history.

---

## Prerequisites

1. **Power Automate License** — Office 365 (included) is sufficient at current intervals; HTTP connector may require Premium trial activation
2. **Azure DevOps Access** — Permissions to read Analytics data and run saved queries
3. **SharePoint Site** — A folder where you can write files
4. **Personal Access Token (PAT)** — From Azure DevOps with Analytics (Read) scope (WorkItemLinks flow only)

### Create Your PAT in Azure DevOps

> **Note**: Only the WorkItemLinks flow needs a PAT. The ALL Items flow uses the built-in ADO connector and authenticates via your Microsoft account.

1. Go to [Azure DevOps](https://dev.azure.com)
2. Click your profile icon (top-right) → **Personal access tokens**
3. Click **+ New Token**
4. Configure:
   - **Name**: `PowerAutomate-WorkItemLinks`
   - **Organization**: Select your organization
   - **Expiration**: Choose appropriate duration (max 1 year)
   - **Scopes**: Click **Show all scopes**, find **Analytics**, check **Read**
5. Click **Create**
6. **Copy the token immediately** — you won't see it again!

---

## Flow 1: ADO ALL Items

This flow uses the built-in Azure DevOps connector to run a saved WIQL query and export the results as JSON (and a legacy CSV) to SharePoint.

### Flow Structure

```
Recurrence (every 3 minutes)
│
├── Get_query_results (ADO connector — saved query by ID)
├── Create_CSV_table (legacy artifact)
├── Select_Transformed_Fields (reshape to dashboard schema)
├── Compose_JSON
├── Update_file (CSV to SharePoint — legacy)
└── Update_JSON_file (JSON to SharePoint)
```

### Configuration

- **ADO Organization**: `ncryptedcloud`
- **ADO Project**: `eShare`
- **Query**: Saved query (ID: `d98c6d59-07e6-4c39-ad44-aab85b2e295e`), max 20,000 items
- **SharePoint Site**: `wardedbox.sharepoint.com/sites/ProductManagement`
- **Output**: `/Shared Documents/Product Planning/ALL Items.json`
- **Authentication**: Microsoft account via ADO connector (no PAT needed)

### Notes

- No pagination needed — the ADO connector handles it internally
- No loops — 7 actions per run regardless of item count
- Also writes `ALL Items.csv` (legacy artifact, not consumed by dashboard)

---

## Flow 2: Export ADO WorkItemLinks

This flow uses raw HTTP requests with a PAT to query the Azure DevOps Analytics OData API and export WorkItemLinks as JSON to SharePoint. It handles pagination via a Do Until loop with the Compose + union pattern.

### Create the Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **My flows** → **+ New flow** → **Scheduled cloud flow**
3. Configure:
   - **Flow name**: `Export ADO WorkItemLinks`
   - **Starting**: Choose your start date/time
   - **Repeat every**: `5` `Minutes`
   - **Time zone**: Select your timezone
4. Click **Create**

### Step 1: Initialize Variables

Create 4 variables. For each: click **+** → **Add an action** → search `Initialize variable`.

#### varAllLinks

- **Name**: `varAllLinks`
- **Type**: Array
- **Value**: `[]`

Rename to `Initialize varAllLinks`

#### varNextLink

- **Name**: `varNextLink`
- **Type**: String
- **Value**: 
```
https://analytics.dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}/_odata/v3.0-preview/WorkItemLinks?$select=WorkItemLinkSK,SourceWorkItemId,TargetWorkItemId,CreatedDate,DeletedDate,Comment,LinkTypeId,LinkTypeReferenceName,LinkTypeName,LinkTypeIsAcyclic,LinkTypeIsDirectional,AnalyticsUpdatedDate,ProjectSK
```

> **Important**: Replace `{YOUR_ORG}` and `{YOUR_PROJECT}` with your Azure DevOps organization and project names.

Rename to `Initialize varNextLink`

#### varKeepGoing

- **Name**: `varKeepGoing`
- **Type**: Integer
- **Value**: `1`

> **Note**: We use Integer instead of Boolean to avoid Power Automate expression issues.

Rename to `Initialize varKeepGoing`

#### varPAT

- **Name**: `varPAT`
- **Type**: String
- **Value**: Paste your PAT from the Prerequisites section

Rename to `Initialize varPAT`

**Save the flow.**

### Step 2: Create the Do Until Loop

1. Click **+** → **Add an action** → search `Do until` → select **Do until** (Control)
2. **Immediately** click **Edit in advanced mode**
3. Enter: `@equals(variables('varKeepGoing'), 0)`
4. Click outside the box

Rename to `Do Until No More Pages`

**Save the flow.**

### Step 3: HTTP Action (Inside Do Until)

1. Inside Do Until → **+** → **Add an action** → search `HTTP` → select **HTTP** (green icon, NOT Webhook)
2. Configure:
   - **Method**: `GET`
   - **URI**: Click ⚡ → **Variables** → select `varNextLink`
   - **Headers**: Click **+ Add new item**
     - **Key**: `Authorization`
     - **Value**: Click **fx** and enter:
       ```
       concat('Basic ', base64(concat(':', variables('varPAT'))))
       ```

Rename to `HTTP Get WorkItemLinks`

**Save the flow.**

### Step 4: Compose + Set Variable (Inside Do Until)

We merge each page of results into `varAllLinks` using a two-step pattern. Power Automate doesn't allow self-referencing in Set Variable, so Compose evaluates the `union()` first.

> **Why not Foreach + Append?** The old pattern created ~10,000 actions per page (~15,000 per run), consuming the entire daily action quota in a single run. The Compose + union pattern replaces ~10,000 actions with 2.

#### Compose_Merged_Results

1. Inside Do Until, **+** below HTTP → search `Compose` → select **Compose** (Data Operations)
2. In **Inputs**, click **fx** and enter:
   ```
   union(variables('varAllLinks'), body('HTTP_Get_WorkItemLinks')?['value'])
   ```

Rename to `Compose_Merged_Results`

#### Set_varAllLinks

1. **+** below Compose → search `Set variable` → select **Set variable**
2. **Name**: `varAllLinks`
3. **Value**: Click **fx** and enter: `outputs('Compose_Merged_Results')`

Rename to `Set_varAllLinks`

**Save the flow.**

### Step 5: Pagination Condition (Inside Do Until)

1. Inside Do Until → **+** → search `Condition` → select **Condition** (Control)
2. Configure:
   - **Left**: Click **fx** → `body('HTTP_Get_WorkItemLinks')?['@odata.nextLink']`
   - **Operator**: **is not equal to**
   - **Right**: Click **fx** → `null`

Rename to `Check for NextLink`

#### True Branch (More Pages)

Add **Set variable**: Name = `varNextLink`, Value (fx) = `body('HTTP_Get_WorkItemLinks')?['@odata.nextLink']`

Rename to `Set NextLink`

#### False Branch (No More Pages)

Add **Set variable**: Name = `varKeepGoing`, Value = `0`

Rename to `Set KeepGoing Zero`

**Save the flow.**

### Step 6: Select Fields (Outside Do Until)

1. **+** below Do Until → search `Select` → select **Select** (Data Operation)
2. **From**: Click ⚡ → **Variables** → `varAllLinks`
3. **Map** (click **+ Add new item** for each):

| Key | Value (fx) |
|-----|------------|
| `WorkItemLinkSK` | `item()?['WorkItemLinkSK']` |
| `SourceWorkItemId` | `item()?['SourceWorkItemId']` |
| `TargetWorkItemId` | `item()?['TargetWorkItemId']` |
| `CreatedDate` | `item()?['CreatedDate']` |
| `DeletedDate` | `item()?['DeletedDate']` |
| `Comment` | `item()?['Comment']` |
| `LinkTypeId` | `item()?['LinkTypeId']` |
| `LinkTypeReferenceName` | `item()?['LinkTypeReferenceName']` |
| `LinkTypeName` | `item()?['LinkTypeName']` |
| `LinkTypeIsAcyclic` | `item()?['LinkTypeIsAcyclic']` |
| `LinkTypeIsDirectional` | `item()?['LinkTypeIsDirectional']` |
| `AnalyticsUpdatedDate` | `item()?['AnalyticsUpdatedDate']` |
| `ProjectSK` | `item()?['ProjectSK']` |

Rename to `Select Fields`

**Save the flow.**

### Step 7: Transform and Compose JSON Output

#### Select Transformed Links

1. **+** → search `Select` → select **Select**
2. **From**: Click ⚡ → **Select Fields** → `Output`
3. **Map**:

| Key | Value (fx) |
|-----|------------|
| `source` | `item()?['SourceWorkItemId']` |
| `target` | `item()?['TargetWorkItemId']` |
| `type` | `item()?['LinkTypeName']` |
| `comment` | `item()?['Comment']` |

Rename to `Select Transformed Links`

#### Compose JSON

1. **+** → search `Compose` → select **Compose**
2. **Inputs**: Click ⚡ → **Select Transformed Links** → `Output`

Rename to `Compose JSON`

**Save the flow.**

### Step 8: Update File in SharePoint

First, manually create an empty `WorkItemLinks.json` file in your SharePoint folder.

1. **+** → search `Update file` → select **Update file** (SharePoint)
2. Configure:
   - **Site Address**: Select your SharePoint site
   - **File Identifier**: `/Shared Documents/YOUR_FOLDER/WorkItemLinks.json`
   - **File Content**: Click ⚡ → **Compose JSON** → `Output`

Rename to `Update JSON file`

**Save the flow.**

### Step 9: Test the Flow

1. Click **Test** (top-right) → **Manually** → **Run flow**
2. Wait for completion (~13 seconds with Compose + union pattern)
3. Verify:
   - All actions show green checkmarks
   - The JSON file in SharePoint has all records (~15,000)
   - Data structure looks correct

### Flow Structure

```
Recurrence (every 5 minutes)
│
├── Initialize varAllLinks (Array: [])
├── Initialize varNextLink (String: OData URL)
├── Initialize varKeepGoing (Integer: 1)
├── Initialize varPAT (String: your PAT)
│
├── Do Until No More Pages (varKeepGoing = 0, timeout: PT2H)
│   │
│   ├── HTTP Get WorkItemLinks
│   │
│   ├── Compose_Merged_Results
│   │   └── union(varAllLinks, response['value'])
│   │
│   ├── Set_varAllLinks = outputs('Compose_Merged_Results')
│   │
│   └── Check for NextLink
│       ├── True → Set NextLink (to next page URL)
│       └── False → Set KeepGoing Zero (stop loop)
│
├── Select Fields
├── Select Transformed Links (JSON format)
├── Compose JSON
└── Update JSON file in SharePoint
```

---

## Troubleshooting

### Error: 401 Unauthorized (WorkItemLinks flow)
- Your PAT may have expired
- PAT doesn't have Analytics (Read) scope
- Re-check the Authorization header expression

### Error: Invalid expression in Do Until
- Use advanced mode and enter: `@equals(variables('varKeepGoing'), 0)`
- Use Integer type for varKeepGoing, not Boolean

### Error: Self reference not supported
- You cannot use `union()` directly in Set Variable for the same variable
- Use the two-step pattern: Compose evaluates `union()`, then Set Variable reads `outputs('Compose_Merged_Results')`

### Flow runs slowly (>5 minutes)
- Verify you are using the Compose + union pattern, NOT Foreach + Append
- The Foreach + Append pattern creates ~10,000 actions per page and causes 45–270 min runtimes
- With Compose + union, the flow should complete in under 30 seconds

### Error: File not found in SharePoint
- Ensure the file exists before running (create an empty JSON file first)
- Check the file path is correct

### ADO connector query fails (ALL Items flow)
- Verify the saved query ID exists in your ADO project
- Check that your Microsoft account has access to the ADO project
- The connector authenticates via your Microsoft account, not a PAT

---

## Performance & Throttling

### WorkItemLinks Performance
- **~15,000 links**: Approximately 13 seconds runtime with Compose + union pattern
- **Pagination**: OData returns up to 10,000 records per page; the flow typically processes 2 pages
- **Actions per run**: ~19 total (vs ~15,000 with the old Foreach + Append pattern)

### Action Budget & Scheduling

Both flows share the same owner's action quota. The binding constraint is the [Power Platform request limit](https://learn.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations) per license.

**Current intervals** (as of v249):

| Flow | Interval | Actions/day |
|------|----------|-------------|
| ALL Items | Every 3 minutes | 3,360 |
| WorkItemLinks | Every 5 minutes | 5,472 |
| **Combined** | | **8,832 (88% of 10K limit)** |

**Actions per run:**

| Flow | Actions/run | Method |
|------|-------------|--------|
| ALL Items | 7 | ADO connector (no loops) |
| WorkItemLinks | 19 | HTTP + Compose/union pagination (2 pages) |

**License limits** (from [Microsoft docs](https://learn.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations#request-limits-in-power-automate)):

| License | Per user / 24h | Per flow / 24h | Price |
|---------|---------------|----------------|-------|
| Office 365 (included) | 6,000 | 10,000 | Included |
| Power Automate Premium | 40,000 | 200,000 | ~$15/user/mo |
| Power Automate Process | — | 250,000 | ~$150/flow/mo |

**Scheduling options by interval combination:**

| ALL Items | WorkItemLinks | AI/day | WIL/day | Total | % of 10K limit | License required |
|-----------|---------------|--------|---------|-------|----------------|------------------|
| 1 min | 1 min | 10,080 | 27,360 | 37,440 | 374% | Premium |
| 2 min | 2 min | 5,040 | 13,680 | 18,720 | 187% | Premium |
| 2 min | 5 min | 5,040 | 5,472 | 10,512 | 105% | Premium |
| 2 min | 10 min | 5,040 | 2,736 | 7,776 | 78% | Office 365 |
| 3 min | 3 min | 3,360 | 9,120 | 12,480 | 125% | Premium |
| **3 min** | **5 min** | **3,360** | **5,472** | **8,832** | **88%** | **Office 365 (active)** |
| 3 min | 10 min | 3,360 | 2,736 | 6,096 | 61% | Office 365 |
| 4 min | 4 min | 2,520 | 6,840 | 9,360 | 94% | Office 365 (tight) |
| 4 min | 5 min | 2,520 | 5,472 | 7,992 | 80% | Office 365 |
| 4 min | 10 min | 2,520 | 2,736 | 5,256 | 53% | Office 365 |
| 5 min | 5 min | 2,016 | 5,472 | 7,488 | 75% | Office 365 |
| 5 min | 10 min | 2,016 | 2,736 | 4,752 | 48% | Office 365 |
| 10 min | 10 min | 1,008 | 2,736 | 3,744 | 37% | Office 365 |

> **Note:** The Office 365 user-level limit is 6,000 actions/day across all flows owned by the same user. Microsoft is currently in a [transition period](https://learn.microsoft.com/en-us/power-platform/admin/power-automate-licensing/types#transition-period) with lenient enforcement, but build for the official limits. Target 75% or below to leave headroom for retries and future growth.

### Content Throughput Limits

In addition to action counts, Power Automate enforces [content throughput limits](https://learn.microsoft.com/en-us/power-automate/limits-and-config#content-throughput-limits) on the total data flowing through run history. These are separate from action limits and apply per flow version on a sliding window.

**Per-run data volume:**

| Flow | Payload size | Runs/day (current) | Daily volume |
|------|-------------|-------------------|-------------|
| ALL Items | ~8.6 MB | 480 (every 3 min) | ~4.1 GB |
| WorkItemLinks | ~0.9 MB | 288 (every 5 min) | ~0.26 GB |
| **Combined** | | | **~4.4 GB** |

**Microsoft limits** (from [limits and config docs](https://learn.microsoft.com/en-us/power-automate/limits-and-config#content-throughput-limits)):

| Metric | Official (Low profile) | Transition period | Our usage | Status |
|--------|----------------------|-------------------|-----------|--------|
| Per 5 minutes | 120 MB | 120 MB | ~17 MB worst case | Safe |
| Per 24 hours | 200 MB | 2.5 GB | ~4.4 GB | **Over both** |

> **Risk assessment:** Our daily content throughput (~4.4 GB) exceeds the official Low profile limit (200 MB) and the transition period limit (2.5 GB). Microsoft is currently lenient during the transition period, so this is not causing issues today. However, if enforcement tightens, mitigation options include:
>
> 1. **Longer intervals** — 10 min / 10 min reduces to ~1.5 GB/day
> 2. **Power Automate Premium** — raises content throughput to 2 GB official / 20 GB transition
> 3. **Reduce payload size** — trim unused fields from the ALL Items query (the dominant contributor at 8.6 MB/run)
> 4. **Per-action message size** (100 MB) is not a concern — largest payload is ~8.6 MB

### Historical Note (pre-v249)

The original WorkItemLinks flow used a Foreach loop ("Loop Through Results") with Append to array variable. This created one action per link (~15,000/run), causing:
- 45–270 minute runtimes (vs 13 seconds)
- 60,000+ actions/day (6× over the license limit)
- Microsoft throttling warnings
- Data truncation at exactly 10,000 rows when the Do Until timeout was reached before pagination completed

### Legacy CSV Exports

Both flows also export CSV files to SharePoint (`ALL Items.csv`, `WorkItemLinks.csv`). These are legacy artifacts — the dashboard only consumes the JSON files. The CSVs remain in the flows for backward compatibility but are not actively used.

---

## Flow Version Control

Flow definitions are version-controlled in the `flows/` directory. Secrets (PATs, Authorization headers) are automatically redacted before committing.

### Exporting a Flow

1. Go to **My flows** in [Power Automate](https://make.powerautomate.com)
2. Find the flow → click **three dots (⋯)** → **Export** → **Package (.zip)**
3. Save the ZIP to the SharePoint **Product Planning** folder
4. Run the import script:
   ```bash
   ./copy-flows.sh       # Imports all flow ZIPs from SharePoint
   # Or import a single flow:
   ./import-flow.sh path/to/flow-export.zip
   ```
5. Review the redacted output, then commit:
   ```bash
   git add flows/
   git commit -m "Update flow definitions"
   ```

### What Gets Committed

```
flows/
  ADO-ALL-Items/
    definition.json    ← Pretty-printed (no secrets to redact)
    manifest.json
  Export-ADO-WorkItemLinks/
    definition.json    ← Pretty-printed, secrets redacted
    manifest.json
```

### PAT Redaction

The `import-flow.sh` script automatically detects and replaces:
- Variables with names containing `pat`, `token`, `secret`, `password`, or `apikey`
- `Authorization` header values
- Long base64-like strings (>40 characters)

All are replaced with `<REDACTED>`. Raw ZIP exports (which contain unredacted secrets) are gitignored and never committed.

### Reviewing Flow Changes

The committed `definition.json` files are diff-friendly:
```bash
git diff flows/Export-ADO-WorkItemLinks/definition.json
git diff flows/ADO-ALL-Items/definition.json
git log --oneline flows/
```

### Re-constituting a Flow

The committed definitions are **documentation only** — they cannot be imported directly into Power Automate because secrets are redacted. To rebuild:

1. **From a backup ZIP**: Import the raw ZIP from SharePoint via Power Automate → **My flows** → **Import** → **Import Package (Legacy)**. This preserves all secrets and connections.

2. **From the redacted definition**: Create a new flow manually following the step-by-step guides above. The `definition.json` documents the exact structure, expressions, and action configuration — only secrets and connection references need to be re-entered.

3. **Secrets to restore**:

   | Flow | Secret | Description |
   |------|--------|-------------|
   | WorkItemLinks | `varPAT` | Azure DevOps PAT with Analytics (Read) scope |
   | Both | SharePoint connection | Authenticated connection to `wardedbox.sharepoint.com/sites/ProductManagement` |
   | ALL Items | ADO connector | Microsoft account with access to `ncryptedcloud/eShare` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-14 | Initial version (WorkItemLinks flow only) |
| 2.0 | 2026-04-03 | Renamed from README_ExportWorkItemLinks.md. Added ALL Items flow. Replaced Foreach+Append with Compose+union. Added action budget analysis, flow version control, and reconstitution guide. |
