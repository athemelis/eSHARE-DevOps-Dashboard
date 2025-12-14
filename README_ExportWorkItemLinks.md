# Export Azure DevOps WorkItemLinks to SharePoint CSV

This Power Automate flow exports WorkItemLinks from Azure DevOps Analytics OData API to a CSV file in SharePoint. The flow runs on a schedule and overwrites the file each time (SharePoint maintains version history).

---

## Prerequisites

Before you begin, ensure you have:

1. **Power Automate Premium License** - Required for the HTTP connector
2. **Azure DevOps Access** - With permissions to read Analytics data
3. **SharePoint Site** - With a folder where you can write files
4. **Personal Access Token (PAT)** - From Azure DevOps with Analytics (Read) scope

---

## Step 1: Create Your PAT in Azure DevOps

1. Go to [Azure DevOps](https://dev.azure.com)
2. Click your profile icon (top-right) → **Personal access tokens**
3. Click **+ New Token**
4. Configure:
   - **Name**: `PowerAutomate-WorkItemLinks`
   - **Organization**: Select your organization
   - **Expiration**: Choose appropriate duration (max 1 year)
   - **Scopes**: Click **Show all scopes**, find **Analytics**, check **Read**
5. Click **Create**
6. **Copy the token immediately** - you won't see it again!

---

## Step 2: Create the Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **My flows** → **+ New flow** → **Scheduled cloud flow**
3. Configure:
   - **Flow name**: `Export ADO WorkItemLinks`
   - **Starting**: Choose your start date/time (format: `2025-12-14T10:00:00`)
   - **Repeat every**: `10` `Minutes`
   - **Time zone**: Select your timezone
4. Click **Create**

> **Note**: We use 10 minutes because the flow takes approximately 5 minutes to run with ~6,000 records.

---

## Step 3: Initialize Variables

You need to create 4 variables. For each one:

1. Click **+** → **Add an action**
2. Search for `Initialize variable`
3. Select **Initialize variable**

### Variable 1: varAllLinks

- **Name**: `varAllLinks`
- **Type**: Array
- **Value**: `[]` (type these two characters literally)

Rename the action to `Initialize varAllLinks`

### Variable 2: varNextLink

- **Name**: `varNextLink`
- **Type**: String
- **Value**: 
```
https://analytics.dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}/_odata/v3.0-preview/WorkItemLinks?$select=WorkItemLinkSK,SourceWorkItemId,TargetWorkItemId,CreatedDate,DeletedDate,Comment,LinkTypeId,LinkTypeReferenceName,LinkTypeName,LinkTypeIsAcyclic,LinkTypeIsDirectional,AnalyticsUpdatedDate,ProjectSK
```

> **Important**: Replace `{YOUR_ORG}` and `{YOUR_PROJECT}` with your Azure DevOps organization and project names.

Rename the action to `Initialize varNextLink`

### Variable 3: varKeepGoing

- **Name**: `varKeepGoing`
- **Type**: Integer
- **Value**: `1`

> **Note**: We use an Integer instead of Boolean to avoid Power Automate expression issues.

Rename the action to `Initialize varKeepGoing`

### Variable 4: varPAT

- **Name**: `varPAT`
- **Type**: String
- **Value**: Paste your PAT from Step 1

Rename the action to `Initialize varPAT`

**Save the flow.**

---

## Step 4: Create the Do Until Loop

1. Click **+** → **Add an action**
2. Search for `Do until`
3. Select **Do until** (under Control)
4. **Immediately** click **Edit in advanced mode** (before entering anything else)
5. Enter this expression:
   ```
   @equals(variables('varKeepGoing'), 0)
   ```
6. Click outside the box or press Done

Rename the action to `Do Until No More Pages`

**Save the flow.**

---

## Step 5: Add HTTP Action (Inside Do Until)

1. Inside the Do Until loop, click **+** → **Add an action**
2. Search for `HTTP`
3. Select **HTTP** (with the green icon, NOT HTTP Webhook)
4. Configure:
   - **Method**: `GET`
   - **URI**: Click ⚡ (lightning bolt) → **Variables** → select `varNextLink`
   - **Headers**: Click **+ Add new item**
     - **Key**: `Authorization` (just type the word)
     - **Value**: Click **fx** (expression) and enter:
       ```
       concat('Basic ', base64(concat(':', variables('varPAT'))))
       ```
       Click **Add**

Rename the action to `HTTP Get WorkItemLinks`

**Save the flow.**

---

## Step 6: Add Apply to Each Loop (Inside Do Until)

Since Power Automate doesn't allow self-referencing variables, we must loop through results individually.

1. Inside Do Until, click **+** below HTTP → **Add an action**
2. Search for `Apply to each`
3. Select **Apply to each** (under Control)
4. **Select an output from previous steps**: Click **fx** and enter:
   ```
   body('HTTP_Get_WorkItemLinks')?['value']
   ```
   Click **Add**

Rename the action to `Loop Through Results`

### Add Append Action Inside the Loop

1. Inside "Loop Through Results", click **+** → **Add an action**
2. Search for `Append to array variable`
3. Select **Append to array variable**
4. Configure:
   - **Name**: Select `varAllLinks`
   - **Value**: Click **fx** and enter:
     ```
     item()
     ```
     Click **Add**

**Save the flow.**

### Enable Concurrency for Speed

1. Click on **Loop Through Results**
2. Click the **three dots (⋯)** → **Settings**
3. Toggle **Concurrency Control** to **On**
4. Set **Degree of Parallelism** to `20`
5. Click **Done**

**Save the flow.**

---

## Step 7: Add Condition for Pagination (Inside Do Until)

1. Inside Do Until (after Loop Through Results), click **+** → **Add an action**
2. Search for `Condition`
3. Select **Condition** (under Control)
4. Configure the condition:
   - **Left box**: Click **fx** and enter:
     ```
     body('HTTP_Get_WorkItemLinks')?['@odata.nextLink']
     ```
     Click **Add**
   - **Middle dropdown**: **is not equal to**
   - **Right box**: Click **fx** and enter:
     ```
     null
     ```
     Click **Add**

Rename the action to `Check for NextLink`

**Save the flow.**

### True Branch (More Pages Exist)

1. In the **True** branch, click **+** → **Add an action**
2. Search for `Set variable`
3. Select **Set variable**
4. Configure:
   - **Name**: Select `varNextLink`
   - **Value**: Click **fx** and enter:
     ```
     body('HTTP_Get_WorkItemLinks')?['@odata.nextLink']
     ```
     Click **Add**

Rename to `Set NextLink`

### False Branch (No More Pages)

1. In the **False** branch, click **+** → **Add an action**
2. Search for `Set variable`
3. Select **Set variable**
4. Configure:
   - **Name**: Select `varKeepGoing`
   - **Value**: `0` (just type the number)

Rename to `Set KeepGoing Zero`

**Save the flow.**

---

## Step 8: Add Select Action (Outside Do Until)

1. Click **+** below "Do Until No More Pages" (outside the loop) → **Add an action**
2. Search for `Select`
3. Select **Select** (under Data Operation)
4. Configure:
   - **From**: Click ⚡ → **Variables** → select `varAllLinks`
   - **Map**: Add each field by clicking **+ Add new item**:

| Key (type as text) | Value (click **fx** for each) |
|-----|------------------------|
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

Rename to `Select Fields for CSV`

**Save the flow.**

---

## Step 9: Create CSV Table

1. Click **+** → **Add an action**
2. Search for `Create CSV table`
3. Select **Create CSV table** (under Data Operation)
4. Configure:
   - **From**: Click ⚡ → **Select Fields for CSV** → select `Output`
   - **Columns**: Leave as **Automatic**

Rename to `Create CSV Table`

**Save the flow.**

---

## Step 10: Update File in SharePoint

First, you need to manually create an empty `WorkItemLinks.csv` file in your SharePoint folder (the flow will update it).

1. Click **+** → **Add an action**
2. Search for `Update file`
3. Select **Update file** (under SharePoint)
4. Configure:
   - **Site Address**: Select your SharePoint site
   - **File Identifier**: Type the full path: `/Shared Documents/YOUR_FOLDER/WorkItemLinks.csv`
   - **File Content**: Click ⚡ → **Create CSV Table** → select `Output`

Rename to `Update File in SharePoint`

**Save the flow.**

---

## Step 11: Test the Flow

1. Click **Test** (top-right)
2. Select **Manually**
3. Click **Run flow**
4. Wait for completion (approximately 5 minutes for ~6,000 records)
5. Verify:
   - All actions show green checkmarks
   - The CSV file in SharePoint has all records
   - Column headers and data look correct

---

## Flow Structure Summary

```
Recurrence (every 6 minutes)
│
├── Initialize varAllLinks (Array: [])
├── Initialize varNextLink (String: OData URL)
├── Initialize varKeepGoing (Integer: 1)
├── Initialize varPAT (String: your PAT)
│
├── Do Until No More Pages (varKeepGoing = 0)
│   │
│   ├── HTTP Get WorkItemLinks
│   │
│   ├── Loop Through Results (for each item in response)
│   │   └── Append to array variable
│   │
│   └── Check for NextLink
│       ├── True → Set NextLink (to next page URL)
│       └── False → Set KeepGoing Zero (stop loop)
│
├── Select Fields for CSV
├── Create CSV Table
└── Update File in SharePoint
```

---

## Troubleshooting

### Error: 401 Unauthorized
- Your PAT may have expired
- PAT doesn't have Analytics (Read) scope
- Re-check the Authorization header expression

### Error: Invalid expression in Do Until
- Use advanced mode and enter: `@equals(variables('varKeepGoing'), 0)`
- Use Integer type for varKeepGoing, not Boolean

### Error: Self reference not supported
- You cannot use `union()` to append to the same variable
- Use Apply to each with Append to array variable instead

### Flow runs slowly
- Enable Concurrency Control on Loop Through Results
- Set Degree of Parallelism to 20

### Error: File not found in SharePoint
- Ensure the file exists before running (create an empty CSV first)
- Check the file path is correct

---

## Performance Notes

- **~6,000 records**: Approximately 5 minutes runtime
- **Pagination**: OData returns ~1,000 records per page
- **Concurrency**: Setting parallelism to 20 significantly speeds up the loop

---

## Exporting This Flow

To export the flow for backup or sharing:

1. Go to **My flows**
2. Find **Export ADO WorkItemLinks**
3. Click the **three dots (⋯)** → **Export** → **Package (.zip)**
4. Configure the package name and click **Export**
5. Download the .zip file

To import on another environment:

1. Go to **My flows** → **Import** → **Import Package (Legacy)**
2. Upload the .zip file
3. Configure connections and click **Import**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-14 | Initial version |
