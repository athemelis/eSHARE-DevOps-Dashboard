# Cowork Starter Prompt

Copy and paste this into Cowork to continue with full context:

---

I just completed a three-phase Azure DevOps field migration project and created 6 Python scripts for one-time data migrations. I need help organizing these files in my GitHub repository.

**Project Context:**
- Organization: ncryptedcloud
- Project: eShare  
- Process Template: ᵉShareScrum
- Migration completed: 941 field updates across 969 work items

**What I have:**
1. Six Python scripts (3 production, 3 utility)
2. Comprehensive README.md
3. Detailed SESSION_LOG.md
4. All files currently in `/Users/tonythem/GitHub/eSHARE/` directory

**What I need to do:**
1. Create new folder: `ADO-Python-Scripts`
2. Move all Python scripts (.py files) into this folder
3. Move README.md and SESSION_LOG.md into this folder
4. Create git commits with appropriate messages
5. Push to GitHub repository

**Files to organize:**
- convert_all_target_dates_production.py
- copy_target_date_to_cascading.py
- copy_release_version_to_cascading.py
- list_processes.py
- add_picklist_bulk.py
- add_picklist_values_v2.py
- README.md
- SESSION_LOG.md

**Git repository:**
- Path: `/Users/tonythem/GitHub/eSHARE/`
- Remote: (already configured)
- Branch: main

**Additional context:**
The scripts were created to:
1. Convert UTC datetime to Athens timezone (368 work items)
2. Migrate target dates from text field to picklist (351 work items)  
3. Migrate release versions from text field to picklist (590 work items)

All migrations are complete and successful. These scripts are for reference and potential future similar migrations.

Can you help me organize these files in the repository with appropriate git commits?

---

**Note:** All files are already downloaded to the local directory. Just need help with folder organization and git operations.
