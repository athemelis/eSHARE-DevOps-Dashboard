# eShare DevOps Dashboard - Development Setup Guide

This guide walks you through setting up your development environment to work on the eShare DevOps Dashboard using Claude Code and GitHub.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [One-Time Setup](#one-time-setup)
3. [Daily Workflow](#daily-workflow)
4. [Sample Claude Code Prompts](#sample-claude-code-prompts)
5. [Git Quick Reference](#git-quick-reference)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- **macOS 10.15+** (or Ubuntu 20.04+ / Windows with WSL)
- **Python 3.9+** with pandas (`pip3 install pandas`)
- **Node.js** (for Claude Code installation)
- **Anthropic account** with Pro or Max subscription (or API credits)
- **GitHub account** with access to the repository

---

## One-Time Setup

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Node.js

```bash
brew install node
```

### Step 3: Install Claude Code

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

If you see a PATH warning, run:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

Verify installation:

```bash
claude --version
claude doctor
```

### Step 4: Authenticate Claude Code

```bash
claude login
```

Choose **Claude App (Pro/Max)** if you have a Pro or Max subscription, or **Claude Console** if you use API credits.

### Step 5: Install GitHub CLI

```bash
brew install gh
```

### Step 6: Authenticate GitHub CLI

```bash
gh auth login
```

When prompted, choose:
- **GitHub.com**
- **HTTPS** protocol
- **Yes** to authenticate Git with GitHub credentials
- **Login with a web browser**

Follow the browser prompts to complete authentication.

Verify:

```bash
gh auth status
```

### Step 7: Clone the Repository

```bash
cd ~/Projects  # or wherever you keep your projects
git clone https://github.com/athemelis/eSHARE-DevOps-Dashboard.git
cd eSHARE-DevOps-Dashboard
```

### Step 8: Set Up Data Files

The dashboard requires two CSV files that are **not** stored in the repository:

| File | Source | Location |
|------|--------|----------|
| `ALL_Items.csv` | Power Automate (auto-updated) | Project root or SharePoint |
| `Org_Chart.csv` | Manual maintenance | Project root or SharePoint |

Copy these files to your project folder or specify their paths when running the generator.

---

## Daily Workflow

### Starting a Development Session

```bash
# 1. Navigate to project folder
cd ~/Projects/eSHARE-DevOps-Dashboard

# 2. Pull latest changes from GitHub
git pull

# 3. Start Claude Code
claude
```

### Making Changes with Claude Code

Inside Claude Code, describe what you want in natural language:

```
> Add a Priority filter to the Releases view header, similar to the Team filter.
```

Claude will read your files, make the edits, and show you what changed.

### Testing Your Changes

Ask Claude to generate and preview:

```
> Run the generator script and open the output in my browser
```

Or run manually:

```bash
# Generate to local directory (for testing)
python3 generate_dashboard.py
open "eSHARE-DevOps-Dashboard.html"

# Generate and publish to SharePoint (when ready)
python3 generate_dashboard.py --publish
```

### Committing Your Changes

Once you've validated the changes in your browser:

```
> Update the version to v71, add an entry to the version history in 
> DASHBOARD_README.md, then commit and push to GitHub with a descriptive message.
```

Or manually:

```bash
git add .
git commit -m "v71: Added Priority filter to Releases view"
git push
```

### Ending a Session

Just close the terminal or type:

```
/exit
```

---

## Sample Claude Code Prompts

### Getting Oriented

```
Read the CLAUDE.md and DASHBOARD_README.md files, then tell me what 
version we're on and summarize recent changes.
```

```
Show me the structure of the Templates folder and explain what each file does.
```

### Making UI Changes

```
Add a "Component" filter dropdown to the Bugs view header, similar to 
how the Bug Type filter works.
```

```
In the Teams view, change the time period filter to default to "Last 30 Days" 
instead of "Last 7 Days".
```

```
Make the stat cards in the Releases view clickable to filter the chart below.
```

### Fixing Bugs

```
There's a JavaScript error when I click on a team card. Check the browser 
console error and fix it. The error says "Cannot read property 'filter' of undefined".
```

```
The Target Date column is showing times like "T00:00:00" - it should only 
show the date portion.
```

### Testing and Validation

```
Run the generator with my CSV file at ../ALL_Items.csv and open the result 
in my browser.
```

```
Check the generated HTML file size - it should be around 5MB. If it's 
only ~350KB, the data didn't inject properly.
```

### Version Management

```
Update to version 72. Change the version in generate_dashboard.py, 
dashboard_v3_part1.html, and add a changelog entry to DASHBOARD_README.md 
describing: "Fixed null reference error in team card click handler".
```

### Git Operations

```
Show me what files have changed since the last commit.
```

```
Commit all changes with message "v72: Fixed team card click handler" 
and push to GitHub.
```

```
I made a mistake - revert the last commit but keep the files changed.
```

---

## Git Quick Reference

### Daily Commands

| Command | What It Does |
|---------|--------------|
| `git pull` | Get latest changes from GitHub |
| `git status` | See what files have changed |
| `git add .` | Stage all changes for commit |
| `git commit -m "message"` | Commit with a message |
| `git push` | Upload commits to GitHub |

### Checking History

| Command | What It Does |
|---------|--------------|
| `git log --oneline -10` | Show last 10 commits |
| `git diff` | Show unstaged changes |
| `git diff --staged` | Show staged changes |

### Fixing Mistakes

| Command | What It Does |
|---------|--------------|
| `git checkout -- filename` | Discard changes to a file |
| `git reset HEAD~1` | Undo last commit, keep changes |
| `git reset --hard HEAD~1` | Undo last commit, discard changes |

### Working with Branches (Advanced)

| Command | What It Does |
|---------|--------------|
| `git checkout -b feature-name` | Create and switch to new branch |
| `git checkout main` | Switch back to main branch |
| `git merge feature-name` | Merge branch into current branch |

---

## Claude Code Quick Reference

### Useful Commands

| Command | What It Does |
|---------|--------------|
| `/help` | Show all available commands |
| `/model` | Switch between Claude models |
| `/clear` | Clear conversation context |
| `/rewind` | Revert to a previous checkpoint |
| `Esc Esc` | Quick rewind (tap Escape twice) |
| `Ctrl+R` | Search prompt history |
| `/exit` | Exit Claude Code |

### Tips for Better Results

1. **Be specific**: "Add a dropdown filter for Priority with options High, Medium, Low" works better than "add a filter"

2. **Reference existing patterns**: "Make it work like the Team filter" helps Claude match your codebase style

3. **Break down complex changes**: Ask for one thing at a time rather than multiple changes at once

4. **Validate incrementally**: Test after each change rather than making many changes before testing

---

## Troubleshooting

### Claude Code won't start

```bash
# Check installation
claude doctor

# Re-authenticate if needed
claude login
```

### Git push fails with authentication error

```bash
# Re-authenticate GitHub CLI
gh auth login

# Check status
gh auth status
```

### Generator script fails

```bash
# Check Python and pandas
python3 --version
pip3 show pandas

# Install pandas if missing
pip3 install pandas

# Run with explicit paths
python3 generate_dashboard.py -c "./ALL_Items.csv" -t "./Templates"
```

### Dashboard shows no data / wrong file size

1. Check that `ALL_Items.csv` exists and has data
2. Verify file size: output should be ~5MB, not ~350KB
3. Open browser console (F12) and look for JavaScript errors
4. Check generator output for "Validation passed"

### Git says "nothing to commit" but files changed

Files might be in `.gitignore`. Check:

```bash
git status --ignored
```

### Need to sync after editing in Finder

Any changes made in Finder (rename, delete, move) need to be committed:

```bash
git add .
git commit -m "Describe what you changed"
git push
```

---

## Project Contacts

- **Repository**: https://github.com/athemelis/eSHARE-DevOps-Dashboard
- **Original Developer**: Tony Athemelis

---

## Version History of This Guide

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | December 2024 | Initial setup guide |
