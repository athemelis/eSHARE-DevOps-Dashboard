# Architecture Component Tag Mapping

This document maps Azure DevOps tags to architecture component boxes in the Bugs Dashboard diagram.

## How Tag Matching Works

- Tags are matched **case-insensitively**
- A bug can appear in **multiple boxes** if it has multiple matching tags
- Tags in Azure DevOps are semicolon-separated (e.g., `UI: Portal; CWP: Authentication`)
- The first tag in the list is used when clicking a box to filter

---

## User Interface

| Box Label | Tags |
|-----------|------|
| Portal (User/Guest) | `UI: Portal` |
| Admin | `UI: Admin` |
| M365 App | `UI: M365 App` |
| Outlook Addins | `UI: Outlook Add-Ins` |
| File Handler | `UI: File Handler` |
| Sharepoint App | `UI: Sharepoint App` |
| Teams External User Collaboration | `UI: Teams Collaboration` |
| Security Attributes | `UI: Security Attributes` |
| SFTP | `UI: SFTP` |
| Reporting | `UI: Reporting` |

---

## CWP

| Box Label | Tags |
|-----------|------|
| Admin | `CWP: Admin` |
| Trusted Sharing | `CWP: Trusted Sharing` |
| Cloud Provider | `CWP: Cloud Provider` |
| Secure Conversation | `CWP: Secure Conversation` |
| PDF Support | `CWP: PDF Support` |
| Office Online | `CWP: Office Online` |
| Labels | `CWP: Labels` |
| DLP | `CWP: DLP` |
| ABAC | `CWP: ABAC` |
| Auditing | `CWP: Auditing` |
| Sharing Policies | `CWP: Sharing Policies` |
| Authentication | `CWP: Authentication` |
| Multimedia Support | `CWP: Multimedia Support` |
| Branding Templates | `CWP: Branding Templates` |
| API | `CWP: API` |
| Notifications | `CWP: Notifications` |
| VTTS | `CWP: VTTS` |

---

## SCG

| Box Label | Tags |
|-----------|------|
| Secure Messaging | `SCG: Secure Messaging` |
| MDR | `SCG: MDR` |
| Orchestrator | `SCG: Orchestrator` |
| OOO | `SCG: OOO` |
| Text | `SCG: Text` |

---

## ESG

| Box Label | Tags |
|-----------|------|
| Pep Engine | `ESG: PEP Engine` |
| Tenant Scanner | `ESG: Tenant Scanner` |
| DLP Engine | `ESG: DLP Engine` |
| Auth Service | `ESG: Auth Service` |

---

## Analytics

| Box Label | Tags |
|-----------|------|
| Databricks | `Analytics: Databricks` |
| Data Pipelines | `Analytics: Data Pipelines` |

---

## Utilities

| Box Label | Tags |
|-----------|------|
| Migrations | `Utilities: Migrations` |
| CWP | `Utilities: CWP` |

---

## Infrastructure

| Box Label | Tags |
|-----------|------|
| Notification Engine | `Infra: Notification Engine` |
| TS Metadata Database | `Infra: TS Metadata` |
| Auditing Data (Mongo) | `Infra: Auditing Data` |
| Email Providers | `Infra: Email Providers` |
| Azure Infrastructure | `Infra: Azure` |
| Build | `Infra: Build` |
| Environments | `Infra: Environments` |

---

## Adding New Tags

To add a new tag mapping, update the `ARCHITECTURE_COMPONENTS` object in `dashboard.js` (around line 13344).

Each component has:
- `id`: Unique identifier (used internally)
- `label`: Display name shown in the box
- `tags`: Array of tags that map to this box (first tag is used for filtering)

Example:
```javascript
{ id: 'newcomponent', label: 'New Component', tags: ['New: Tag1', 'New: Tag2'] }
```
