# Table Column Specification

This document defines the standard columns for each generic table across all dashboards. The column order (left to right) follows the header order below. Each table includes only ✔ columns.

## Column Spec

| Dashboard (Table)         | ID  | Title | State | Priority | Customer | Category | Bug Type | Progress | Aging | Architecture | Tags | CS Owner | Bug Owner | Assigned To | Team | Release Version | Target Date | Effort |
| ------------------------- | --- | ----- | ----- | -------- | -------- | -------- | -------- | -------- | ----- | ------------ | ---- | -------- | --------- | ----------- | ---- | --------------- | ----------- | ------ |
| Releases (Features)       | ✔   | ✔     | ✔     | ✔        | ✔        | ❌        | ❌        | ✔        | ❌     | ❌            | ✔    | ❌        | ❌         | ✔           | ✔    | ✔               | ✔           | ❌      |
| Releases (Issues)         | ✔   | ✔     | ✔     | ✔        | ✔        | ❌        | ❌        | ❌        | ❌     | ❌            | ✔    | ✔        | ❌         | ✔           | ❌    | ✔               | ✔           | ❌      |
| Releases (Customer Bugs)  | ✔   | ✔     | ✔     | ✔        | ✔        | ❌        | ❌        | ✔        | ❌     | ✔            | ❌    | ❌        | ✔         | ✔           | ✔    | ✔               | ✔           | ❌      |
| Releases (Internal Bugs)  | ✔   | ✔     | ✔     | ✔        | ❌        | ❌        | ❌        | ✔        | ❌     | ✔            | ❌    | ❌        | ✔         | ✔           | ✔    | ✔               | ✔           | ❌      |
| Roadmap (Feature Details) | ✔   | ✔     | ✔     | ✔        | ✔        | ❌        | ❌        | ✔        | ❌     | ❌            | ✔    | ❌        | ❌         | ✔           | ✔    | ✔               | ✔           | ✔      |
| Customers (Issue Details) | ✔   | ✔     | ✔     | ✔        | ✔        | ✔        | ❌        | ❌        | ✔     | ❌            | ✔    | ✔        | ❌         | ✔           | ❌    | ✔               | ✔           | ❌      |
| Bugs (Bug Details)        | ✔   | ✔     | ✔     | ✔        | ✔        | ❌        | ✔        | ✔        | ✔     | ✔            | ❌    | ❌        | ✔         | ✔           | ✔    | ✔               | ✔           | ❌      |

## Column Key Reference

| Column Label    | JS Key             | Notes                                          |
| --------------- | ------------------ | ---------------------------------------------- |
| ID              | `id`               | Links to ADO work item                         |
| Title           | `title`            | Includes relationship pills and badges         |
| State           | `state`            | Color-coded state badge                        |
| Priority        | `priority`         | Displayed as P1-P4                             |
| Customer        | `customers`        | Semicolon-separated customer names             |
| Category        | `ticketCategory`   | Ticket category (Enhancement Request, Bug, Task) |
| Bug Type        | `bugType`          | Customer Related, Internal, etc.               |
| Progress        | `progress`         | Mini progress bar with percentage              |
| Aging           | `aging`            | Calculated aging bucket                        |
| Architecture    | `architecture`     | Architecture component tags only               |
| Tags            | `tags`             | All tags (semicolon-separated)                 |
| CS Owner        | `csOwner`          | Customer Success owner                         |
| Bug Owner       | `bugOwner`         | Maps to `deliverySliceOwner` field             |
| Assigned To     | `assignedTo`       | Current assignee                               |
| Team            | `team`             | Team from area path                            |
| Release Version | `cascadingVersion` | Release version (cascading from parent)        |
| Target Date     | `cascadingDate`    | Target date (cascading from parent)            |
| Effort          | `effort`           | Computed sum from child delivery slices         |
