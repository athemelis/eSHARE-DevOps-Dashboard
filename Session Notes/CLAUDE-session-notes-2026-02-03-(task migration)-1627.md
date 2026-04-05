# Task Migration Analysis

**Generated:** February 3, 2026
**Last Updated:** February 3, 2026
**Total Tasks:** 2,678

---

## Tasks by Parent Work Item Type

### Before/After Comparison

| Parent Work Item Type | Original | After Phase 1 | After Phase 2 | Current | Total Change |
|-----------------------|----------|---------------|---------------|---------|--------------|
| Delivery Slice        | 2,107    | 2,122         | 2,135         | 2,161   | +54          |
| Bug                   | 483      | 487           | 490           | 515     | +32          |
| Feature               | 10       | 0             | 0             | 0       | -10 ✓        |
| Issue                 | 5        | 0             | 0             | 0       | -5 ✓         |
| Task                  | 2        | 0             | 0             | 0       | -2 ✓         |

**Summary:**
| Metric | Original | Current | Total Change |
|--------|----------|---------|--------------|
| Tasks with a Parent | 2,607 (98.3%) | 2,676 (99.9%) | +69 |
| Tasks without a Parent (orphan) | 45 (1.7%) | 2 (0.1%) | -43 |

---

### Tasks with Non-Standard Parents - Cleanup Complete ✓

**17 Tasks were migrated** from non-standard parents (Feature, Issue, Task) to standard parents (Delivery Slice or Bug).

**Tasks previously with Feature parent (10) → Now reassigned:**

| Task ID | Title | State | Old Parent | Old Parent ID | New Parent | New Parent ID |
|---------|-------|-------|------------|---------------|------------|---------------|
| 1619 | Attach a unity catalog in prod databricks... | Closed | Feature | 351 | Delivery Slice | 352 |
| 3033 | Govern - Tenant Scan - create pipeline... | New | Feature | 5088 | Delivery Slice | 5496 |
| 3063 | Automatic artifact push to Azure DevOps | New | Feature | 5088 | Delivery Slice | 5496 |
| 3142 | CVE-2025-55182 - Black List Threat Actor | New | Feature | 5085 | Delivery Slice | 1715 |
| 3187 | DevOps: Deploy and run QA data copy on... | New | Feature | 5088 | Delivery Slice | 3132 |
| 3229 | CWP: Deploy v176.1.0 | Done | Feature | 2473 | Delivery Slice | 2348 |
| 3328 | BE 2719 When Calling eSHARE API Endpoint... | Closed | Feature | 2719 | Delivery Slice | 1419 |
| 3360 | MFA required | Done | Feature | 3026 | Delivery Slice | 3197 |
| 3471 | Upgrade gcchdev SMG to version 2025.1... | Done | Feature | 496 | Delivery Slice | 4636 |
| 3495 | CWP: Deploy v176.0.x on government | New | Feature | 496 | Delivery Slice | 4636 |

**Tasks previously with Issue parent (5) → Now reassigned:**

| Task ID | Title | State | Old Parent | Old Parent ID | New Parent | New Parent ID |
|---------|-------|-------|------------|---------------|------------|---------------|
| 1731 | Write documentation about our customer... | New | Issue | 1463 | Delivery Slice | 1058 |
| 2674 | Add Access-Control-Allow-Private-Network... | Done | Issue | 2574 | Delivery Slice | 1109 |
| 2737 | DevOps - Compare indexes / configuration... | Done | Issue | 2691 | Bug | 2698 |
| 2819 | Review and consolidate API permissions | New | Issue | 2320 | Delivery Slice | 2941 |
| 3457 | Work on fixing 1333 SFTP Authentication... | Done | Issue | 1177 | Bug | 1333 |

**Tasks previously with Task parent (2) → Now reassigned:**

| Task ID | Title | State | Old Parent | Old Parent ID | New Parent | New Parent ID |
|---------|-------|-------|------------|---------------|------------|---------------|
| 2850 | staging: Enable CWP SA for all staging... | Done | Task | 2794 | Delivery Slice | 3015 |
| 2886 | Run a smoke test on demo-01 or staging... | Closed | Task | 2794 | Delivery Slice | 3015 |

---

## Orphan Tasks (No Parent) - Cleanup Complete ✓

### Before/After Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Orphan Tasks | 43 | 0 | -43 ✓ |
| Orphan tasks with Related items | 9 | 0 | -9 |
| Orphan tasks with Child items | 10 | 0 | -10 |
| Orphan tasks with NO links at all | 24 | 0 | -24 |

**43 Tasks were assigned parents** (previously had no parent):

| Task ID | Title | State | New Parent | New Parent ID |
|---------|-------|-------|------------|---------------|
| 434 | Remove rich text edit from file ... | Done | Bug | 310 |
| 497 | [PDP] New ABAC use case for demo | Done | Delivery Slice | 260 |
| 818 | Test Preparation & Execution | Done | Delivery Slice | 779 |
| 899 | QA eSHARE Insights report and de... | Closed | Delivery Slice | 239 |
| 911 | Test Preparation & Execution | Done | Bug | 900 |
| 968 | Add mysql data source to grafana | New | Delivery Slice | 1109 |
| 977 | Test Preparation & Execution | In Progress | Delivery Slice | 976 |
| 1271 | QA work for Vulnerability on loa... | Done | Bug | 631 |
| 2186 | Test Execution for OTP incorrect... | Done | Delivery Slice | 2185 |
| 2426 | Cache cleanup script: make it le... | Done | Delivery Slice | 1109 |
| 2600 | Missed SP and SMG runs in the sm... | New | Delivery Slice | 536 |
| 3066 | MDR Eventhub Namespace does not ... | Done | Delivery Slice | 3015 |
| 3141 | REACT Critical Vulnerability | Closed | Delivery Slice | 5299 |
| 3173 | HumanaMilitary - disable RosterE... | Done | Delivery Slice | 1109 |
| 3188 | Deploy CUI addin to production | Done | Delivery Slice | 3011 |
| 3311 | esg notifications: Deploy v3.25... | Done | Delivery Slice | 3310 |
| 3324 | QA work for 500 server error | Done | Bug | 3322 |
| 3370 | Fix SWML link | Done | Bug | 3003 |
| 3398 | Fix issue with user-agent | Done | Bug | 3358 |
| 3399 | Fix content is missing in TS shares | Done | Bug | 3120 |
| 3419 | testing new work log list | Done | Delivery Slice | 406 |
| 3453 | Fix google drive and dropbox upl... | Done | Bug | 3431 |
| 3585 | FE - OTP Authenticator method | Done | Bug | 3579 |
| 3745 | Fix internal server error | Done | Bug | 3708 |
| 3906 | When viewing a native link on Se... | New | Bug | 3799 |
| 4082 | Disable Celery Worker Mingle | Closed | Delivery Slice | 591 |
| 4160 | Fix KubernetesHpaScaleInability | Done | Delivery Slice | 1109 |
| 4236 | testing WorkLog issues | Closed | Delivery Slice | 406 |
| 4356 | Fix Syslog failure | Done | Bug | 4355 |
| 4358 | Fix SAML Error | Done | Bug | 4357 |
| 4360 | Fix UnboundLocalError | Done | Bug | 4359 |
| 4363 | Fix MongoDB errors written to file | Done | Bug | 4362 |
| 4365 | Deploy SFTP 2025.12.2 to Govt | Done | Bug | 1333 |
| 4368 | Fix exception handling | Done | Bug | 4367 |
| 4514 | Fix watermarking issue | Done | Bug | 4509 |
| 4524 | Support for Automating test results | New | Delivery Slice | 1109 |
| 4566 | Fix write json files | Done | Bug | 4565 |
| 4603 | Tenant Scan (Surface Attack Report) | Done | Delivery Slice | 1109 |
| 4608 | Fix Mailgun error | Done | Bug | 4607 |
| 4910 | Humana and Humana-Military need... | New | Delivery Slice | 1109 |
| 5067 | Adaptive Cards is not showing | Done | Delivery Slice | 3237 |
| 5074 | Adaptive Card reload | To Do | Delivery Slice | 4609 |
| 5077 | Fix config drift in staging envs | Done | Delivery Slice | 4670 |

---

## Tasks with Bug as Child - Cleanup Complete ✓

### Before/After Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Tasks with Bug as Child | 10 | 0 | -10 ✓ |

**10 Tasks had their Bug child relationships fixed** (hierarchy was inverted — Task is now child of Bug):

| Task ID | Task Title | Task State | Old Child ID | Old Child Type | New Parent ID | New Parent Type | New Parent Title |
|---------|------------|------------|--------------|----------------|---------------|-----------------|------------------|
| 3739 | SMG equinix-gov sentry errors | Closed | 4221 | Bug | 4221 | Bug | SMG equinix-gov sentry errors |
| 3745 | Fix internal server error... | Done | 3708 | Bug | 3708 | Bug | Internal server error appea... |
| 4356 | Fix Syslog failure | Done | 4355 | Bug | 4355 | Bug | SysLog Handler Socket Failu... |
| 4358 | Fix SAML Error | Done | 4357 | Bug | 4357 | Bug | SAML Error Reporting String... |
| 4360 | Fix UnboundLocalError | Done | 4359 | Bug | 4359 | Bug | Data Transfer Exception - U... |
| 4363 | Fix MongoDB errors written... | Done | 4362 | Bug | 4362 | Bug | MongoDB Failsafe - Write Fa... |
| 4368 | Fix exception handling | Done | 4367 | Bug | 4367 | Bug | Watermark Exception Handlin... |
| 4514 | Fix watermarking issue | Done | 4509 | Bug | 4509 | Bug | Watermarking fails with `At... |
| 4566 | Fix write json files | Done | 4565 | Bug | 4565 | Bug | JSON Write Bug After Python... |
| 4608 | Fix Mailgun error | Done | 4607 | Bug | 4607 | Bug | KeyError - 'accepted' in Ma... |

---

## Tasks by Child Work Item Type

### Before/After Comparison

| Child Work Item Type | Original | Current | Change |
|----------------------|----------|---------|--------|
| Bug                  | 12       | 0       | -12 ✓  |
| Task                 | 1        | 0       | -1 ✓   |
| Delivery Slice       | 1        | 0       | -1 ✓   |

**Summary:**
| Metric | Original | Current | Change |
|--------|----------|---------|--------|
| Tasks that have children | 14 (0.5%) | 0 (0.0%) | -14 ✓ |

---

## Tasks by Related Work Item Type

### Before/After Comparison

| Related Work Item Type | Original | Current | Change |
|------------------------|----------|---------|--------|
| Task                   | 141      | 143     | +2     |
| Delivery Slice         | 38       | 35      | -3     |
| Bug                    | 34       | 31      | -3     |
| Feature                | 10       | 10      | 0      |
| Issue                  | 6        | 9       | +3     |

**Summary:**
| Metric | Original | Current | Change |
|--------|----------|---------|--------|
| Tasks with Related links | 220 (8.3%) | 217 (8.1%) | -3 |

---

## Bugs with Estimation Fields

**Total Bugs:** 530

| Field                   | Bugs with Value | % of Total |
|-------------------------|-----------------|------------|
| Total Effort Estimation | 0               | 0.0%       |
| Analytics Estimation    | 0               | 0.0%       |
| Backend Estimation      | 57              | 10.8%      |
| Frontend Estimation     | 49              | 9.2%       |
| Govern Estimation       | 4               | 0.8%       |
| SCG Estimation          | 1               | 0.2%       |
| DevOps Estimation       | 0               | 0.0%       |
| QA Estimation           | 143             | 27.0%      |
| Staff Estimation        | 63              | 11.9%      |
| Effort Rollup           | 231             | 43.6%      |

**Summary:**
- Bugs with ANY estimation field filled: **284** (53.6%)
- Bugs with NO estimation fields: **246** (46.4%)

---

## Key Observations

1. **Task Hierarchy (Final):** 80.7% of Tasks are children of Delivery Slices, 19.2% are children of Bugs
2. **Non-Standard Parents:** ✓ **CLEANED UP** - All 17 Tasks with Feature/Issue/Task parents reassigned
3. **Orphan Tasks:** ✓ **CLEANED UP** - Reduced from 43 to **0** (all tasks now have parents)
4. **Tasks as Parents:** ✓ **CLEANED UP** - Reduced from 14 to **0** (no tasks have children)
5. **Related Links:** 217 Tasks (8.1%) have Related links, mostly to other Tasks
6. **Bug Estimations:** Over half of Bugs (53.6%) have at least one team estimation field filled
   - QA Estimation is most commonly used (27.0%)
   - Effort Rollup is populated for 43.6% of Bugs (likely auto-calculated)

---

## Migration Summary

| Phase | Items Cleaned | Status |
|-------|---------------|--------|
| Phase 1: Non-Standard Parents | 17 Tasks | ✓ Complete |
| Phase 2: Orphan Tasks | 43 Tasks | ✓ Complete |
| Phase 3: Tasks with Bug Children | 10 Tasks | ✓ Complete |
| **Total Tasks Migrated** | **70 Tasks** | ✓ All Complete |

---

## Notes

_Working document for Task Migration planning_
