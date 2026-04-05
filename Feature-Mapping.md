# OKR Tag Mapping for Features

This document maps Azure DevOps tags to OKR (Objectives and Key Results) categories in the Roadmap Dashboard OKR Summary section.

## How Tag Matching Works

- Tags are matched by **prefix** (e.g., `1:`, `2:`, `3:`, `4:`)
- A feature can appear in **multiple OKR categories** if it has tags from different objectives (this is flagged as a warning)
- Tags in Azure DevOps are semicolon-separated (e.g., `1: Intelligent Email; 4: Customer Experience`)
- Clicking an OKR box filters the table to show features with that specific tag

---

## Objective 1: eSHARE is must-have

| Tag | Description |
|-----|-------------|
| `1: Email Risk Report` | Email risk reporting features |
| `1: Intelligent Email` | Smart email capabilities |
| `1: M365 File & Site Risk Reports` | Microsoft 365 risk reporting |
| `1: Report Performance` | Report performance improvements |
| `1: Support Agentic AI Workflows` | AI workflow support |

---

## Objective 2: eSHARE is the collaboration standard

| Tag | Description |
|-----|-------------|
| `2: CSPP+ Compliance` | CSPP+ compliance features |
| `2: External User Collaboration from Teams and Outlook` | External collaboration from Teams/Outlook |
| `2: M365 App` | Microsoft 365 application features |
| `2: MISA Compliance` | MISA compliance features |
| `2: PDF Collaboration` | PDF collaboration capabilities |
| `2: Support Data Isolation with SharePoint Embedded` | SharePoint Embedded data isolation |

---

## Objective 3: eSHARE deployability

| Tag | Description |
|-----|-------------|
| `3: ABAC Enhancements` | ABAC deployment enhancements |
| `3: Enhancing Purview Integration` | Enhanced Purview integration |
| `3: Native ABAC` | Native ABAC implementation |
| `3: Simplifying Purview Integration` | Simplified Purview integration |
| `3: Workflows for Site Governance` | Site governance workflows |

---

## Objective 4: eSHARE is customer-focused, stable and secure

| Tag | Description |
|-----|-------------|
| `4: ABAC Enhancements` | ABAC stability/security enhancements |
| `4: Compliance` | General compliance features |
| `4: Customer Experience` | Customer experience improvements |
| `4: Customer Success` | Customer success initiatives |
| `4: Delivery Velocity` | Development velocity improvements |
| `4: Documentation` | Documentation updates |
| `4: Improved Auditing` | Auditing improvements |
| `4: Notifications` | Notification system improvements |

---

## Adding New Tags

To add a new OKR tag, simply add it to a Feature in Azure DevOps with the format `N: Tag Name` where N is the objective number (1-4).

The dashboard automatically discovers all tags that match the `1:`, `2:`, `3:`, or `4:` prefixes and displays them in the OKR Summary section.

---

## Color Coding

Each objective has a distinct color in the dashboard:
- **Objective 1** (eSHARE is must-have): Blue
- **Objective 2** (eSHARE is the collaboration standard): Purple
- **Objective 3** (eSHARE deployability): Green
- **Objective 4** (eSHARE is customer-focused, stable and secure): Orange
