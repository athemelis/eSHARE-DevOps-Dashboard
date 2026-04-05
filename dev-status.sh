#!/bin/bash

# dev-status.sh - Check current branch status vs main (GitHub Flow)

MAIN_BRANCH="main"

# Fetch latest from origin
git fetch origin --quiet

# Current branch
CURRENT=$(git branch --show-current)

# Get versions from dashboard-body.html (2 sources: production + local)
PROD_VERSION=$(git show origin/$MAIN_BRANCH:dashboard-body.html 2>/dev/null | grep -oE 'class="version">v[0-9]+' | head -1 | sed 's/.*>//')
DEV_LOCAL_VERSION=$(grep -oE 'class="version">v[0-9]+' dashboard-body.html 2>/dev/null | head -1 | sed 's/.*>//')

# ============================================================================
# SECTION 1: PRODUCTION (main branch)
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    1. PRODUCTION (main branch)                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Version: ${PROD_VERSION:-unknown}"
echo ""
echo "  Recent commits:"
git log origin/$MAIN_BRANCH --oneline -3 | sed 's/^/    /'

# ============================================================================
# SECTION 2: CURRENT BRANCH
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              2. CURRENT BRANCH ($CURRENT)"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Version: ${DEV_LOCAL_VERSION:-unknown}"
echo ""

if [ "$CURRENT" = "$MAIN_BRANCH" ]; then
    echo "  On main branch — ready to create a feature branch"
else
    # Check if remote branch exists
    REMOTE_EXISTS=$(git ls-remote --heads origin "$CURRENT" 2>/dev/null | wc -l | tr -d ' ')

    if [ "$REMOTE_EXISTS" -gt 0 ]; then
        # Compare with main
        AHEAD=$(git rev-list --count origin/main..origin/$CURRENT 2>/dev/null || echo "0")
        BEHIND=$(git rev-list --count origin/$CURRENT..origin/main 2>/dev/null || echo "0")

        echo "  Compared to production:"
        echo "    Commits ahead:  $AHEAD"
        echo "    Commits behind: $BEHIND"
    else
        echo "  Remote branch: not yet pushed"
        AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
        BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

        echo "  Compared to production (local):"
        echo "    Commits ahead:  $AHEAD"
        echo "    Commits behind: $BEHIND"
    fi

    # Check for open PRs
    echo ""
    OPEN_PR=$(gh pr list --head "$CURRENT" --state open --json number --jq '.[0].number' 2>/dev/null)
    if [ -n "$OPEN_PR" ]; then
        echo "  Open PR: #$OPEN_PR"
    else
        echo "  Open PR: None"
    fi

    echo ""
    echo "  Recent commits:"
    git log HEAD --oneline -3 | sed 's/^/    /'
fi

# ============================================================================
# SECTION 3: WORKING COPY
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 3. WORKING COPY                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Uncommitted changes
CHANGES=$(git status --porcelain | wc -l | tr -d ' ')
if [ "$CHANGES" -gt 0 ]; then
    echo "  Uncommitted changes: $CHANGES file(s)"
    git status --short | sed 's/^/    /'
else
    echo "  Working directory: Clean"
fi

# Unpushed commits
echo ""
REMOTE_REF="origin/$CURRENT"
REMOTE_EXISTS_CHECK=$(git rev-parse --verify "$REMOTE_REF" 2>/dev/null)
if [ -n "$REMOTE_EXISTS_CHECK" ]; then
    UNPUSHED=$(git rev-list --count "$REMOTE_REF"..HEAD 2>/dev/null || echo "0")
    if [ "$UNPUSHED" -gt 0 ]; then
        echo "  Unpushed commits: $UNPUSHED"
        git log "$REMOTE_REF"..HEAD --oneline | sed 's/^/    /'
    else
        echo "  Unpushed commits: 0 (in sync with remote)"
    fi
else
    # No remote branch yet — all local commits are unpushed
    LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        echo "  Unpushed commits: $LOCAL_COMMITS (remote branch not yet created)"
    else
        echo "  Unpushed commits: 0"
    fi
fi

# Status interpretation
echo ""
echo "─────────────────────────────────────────────────────────────────"

# Changelog validation: check for placeholder text in the LATEST changelog entry only
CHANGELOG_PLACEHOLDER=""
if [ -f "changelog.js" ]; then
    # Extract first entry (up to the next "version:" line) and check only that block
    LATEST_ENTRY=$(awk '/version:/{n++} n==2{exit} {print}' changelog.js)
    if echo "$LATEST_ENTRY" | grep -qiE 'session in progress|coming soon|placeholder|TODO'; then
        CHANGELOG_PLACEHOLDER="yes"
    fi
fi
# Also check if current version has no changelog entry at all
CHANGELOG_MISSING=""
if [ -f "changelog.js" ] && [ -n "$DEV_LOCAL_VERSION" ]; then
    VERSION_NUM="${DEV_LOCAL_VERSION#v}"
    if ! grep -q "version: $VERSION_NUM" changelog.js 2>/dev/null; then
        CHANGELOG_MISSING="yes"
    fi
fi

if [ -n "$CHANGELOG_PLACEHOLDER" ]; then
    echo "  ⚠️  WARNING: changelog.js has placeholder text!"
    echo "          Update changelog.js with real content before committing."
    echo ""
fi
if [ -n "$CHANGELOG_MISSING" ]; then
    echo "  ⚠️  WARNING: changelog.js missing entry for $DEV_LOCAL_VERSION!"
    echo "          Add a changelog entry before committing."
    echo ""
fi

if [ "$CURRENT" = "$MAIN_BRANCH" ]; then
    if [ "$CHANGES" -gt 0 ]; then
        echo "  ⚠️  WARNING: Uncommitted changes on main!"
        echo "          Create a feature branch first: git checkout -b feature/my-feature"
    else
        echo "  STATUS: On main — ready to create a feature branch"
        echo "          git checkout -b feature/descriptive-name"
    fi
elif [ "$CHANGES" -gt 0 ]; then
    echo "  ACTION: Commit your changes"
    echo "          git add . && git commit -m 'v${DEV_LOCAL_VERSION#v}: [summary]' && git push"
elif [ -n "$REMOTE_EXISTS_CHECK" ] && [ "$UNPUSHED" -gt 0 ]; then
    echo "  ACTION: Push your commits"
    echo "          git push"
elif [ -z "$REMOTE_EXISTS_CHECK" ] && [ "$LOCAL_COMMITS" -gt 0 ]; then
    echo "  ACTION: Push your branch"
    echo "          git push -u origin $CURRENT"
elif [ -n "$OPEN_PR" ]; then
    echo "  STATUS: Waiting for PR #$OPEN_PR to be reviewed/merged"
elif [ "$AHEAD" -gt 0 ]; then
    echo "  ACTION: Create a PR when ready"
    echo "          gh pr create --base main --title 'v${DEV_LOCAL_VERSION#v}: ...'"
else
    echo "  STATUS: Ready to start new work"
fi
echo ""
