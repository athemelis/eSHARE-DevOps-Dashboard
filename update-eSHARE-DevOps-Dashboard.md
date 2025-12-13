# eShare DevOps Dashboard – Automatic Refresh (macOS launchd)

This setup runs your `generate_dashboard.py` script every minute using a `launchd` LaunchAgent.

**Key files:**
- Shell wrapper script: `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/update-eSHARE-DevOps-Dashboard.sh`
- Reload helper script: `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/reload-launchd-agent.sh`
- LaunchAgent plist: `~/Library/LaunchAgents/com.eshare.devops.dashboard.plist`

**Template directories:**
- Development: `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/Templates/`
- Production: `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/Templates-Production/`

**Output locations:**
- Local (for testing): `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/eSHARE-DevOps-Dashboard.html`
- Published (production): `/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ᵉShare DevOps Dashboard.html`

---

## 1. The runner shell script

File: `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/update-eSHARE-DevOps-Dashboard.sh`

This script selects the appropriate template directory based on the mode:
- **Local mode**: Uses `Templates/` (development templates)
- **Publish mode**: Uses `Templates-Production/` (stable production templates)

```bash
#!/bin/bash
#
# Update eSHARE DevOps Dashboard
#
# Usage:
#   ./update-eSHARE-DevOps-Dashboard.sh           # Generate to local directory (for testing) using dev templates
#   ./update-eSHARE-DevOps-Dashboard.sh --publish # Publish to SharePoint (production) using production templates
#   ./update-eSHARE-DevOps-Dashboard.sh -p        # Same as above
#
# Template directories:
#   - Dev templates:  ./Templates (for local development)
#   - Prod templates: ./Templates-Production (for scheduled publishing)
#

cd "/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/"

# Check if --publish or -p flag is present
if [[ "$*" == *"--publish"* ]] || [[ "$*" == *"-p"* ]]; then
    # Use production templates for publishing
    /usr/bin/python3 generate_dashboard.py -t "./Templates-Production" "$@"
else
    # Use dev templates for local testing
    /usr/bin/python3 generate_dashboard.py "$@"
fi
```

**Usage:**
```bash
# Local mode (for testing) - uses Templates/, outputs to local directory
./update-eSHARE-DevOps-Dashboard.sh

# Publish mode (production) - uses Templates-Production/, outputs to SharePoint
./update-eSHARE-DevOps-Dashboard.sh --publish
./update-eSHARE-DevOps-Dashboard.sh -p
```

This separation allows you to develop and test code changes locally without affecting the production dashboard. The launchd job runs with `--publish` and uses the stable `Templates-Production/` templates.

Make it executable:
```bash
chmod +x /Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/update-eSHARE-DevOps-Dashboard.sh
```

---

## 2. The LaunchAgent plist

File: `~/Library/LaunchAgents/com.eshare.devops.dashboard.plist`

Ensure the LaunchAgents folder exists:
```bash
mkdir -p ~/Library/LaunchAgents
```

Current plist (includes `--publish` flag for production output):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.eshare.devops.dashboard</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/update-eSHARE-DevOps-Dashboard.sh</string>
        <string>--publish</string>
    </array>

    <key>StartInterval</key>
    <integer>60</integer>

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/eshare_devops_dashboard.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/eshare_devops_dashboard.err</string>
</dict>
</plist>
```

**Note:** The `--publish` flag ensures the scheduled job outputs directly to SharePoint using the production templates. The launchd job should always run with `--publish` to use the stable `Templates-Production/` directory.

---

## 3. Development vs Production Workflow

### How it works

The dashboard uses **two separate template directories** to isolate development from production:

| Directory | Purpose | Used by |
|-----------|---------|---------|
| `Templates/` | Development templates | Local testing (`./update-eSHARE-DevOps-Dashboard.sh`) |
| `Templates-Production/` | Stable production templates | Scheduled job (`--publish` flag) |

### Development workflow

1. **Make code changes** to files in `Templates/`
2. **Test locally** by running:
   ```bash
   ./update-eSHARE-DevOps-Dashboard.sh
   open eSHARE-DevOps-Dashboard.html
   ```
3. **Iterate** until changes are ready for production

### Publishing to production

When your changes are ready:

1. **Copy templates** to production directory:
   ```bash
   cp Templates/*.html Templates-Production/
   ```

2. **Verify the version** in `Templates-Production/dashboard_v3_part1.html`

3. **Publish once** to confirm:
   ```bash
   ./update-eSHARE-DevOps-Dashboard.sh --publish
   ```

4. The launchd job will continue refreshing data every 60 seconds using the new production templates

### Rolling back

If you need to revert production to a previous version:

```bash
# Restore from git (e.g., v79)
git show 6b53f68:Templates/dashboard_v3_part1.html > Templates-Production/dashboard_v3_part1.html
git show 6b53f68:Templates/dashboard_v3_part2.html > Templates-Production/dashboard_v3_part2.html
git show 6b53f68:Templates/dashboard_v3_part3.html > Templates-Production/dashboard_v3_part3.html
git show 6b53f68:Templates/dashboard_v3_part4.html > Templates-Production/dashboard_v3_part4.html

# Force a publish
./update-eSHARE-DevOps-Dashboard.sh --publish
```

---

## 4. Load the agent and force a first run

**Easiest method - use the reload helper script:**
```bash
./reload-launchd-agent.sh
```

This script:
1. Clears old log files
2. Unloads the agent (if loaded)
3. Loads the agent
4. Kickstarts it to run immediately
5. Waits 2 seconds and shows the last 20 lines of output/error logs

**Manual method:**
```bash
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist 2>/dev/null || true
launchctl load   ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
launchctl kickstart -k gui/"$(id -u)"/com.eshare.devops.dashboard
```

- `kickstart` tells `launchd` to start the job now
- `-k` kills any existing instance before starting a new one

---

## 5. Logs and debugging

**Log file locations:**
- Output: `/tmp/eshare_devops_dashboard.out`
- Errors: `/tmp/eshare_devops_dashboard.err`

**Quick debugging with the reload script:**
```bash
./reload-launchd-agent.sh
```
This clears logs, reloads the agent, and shows fresh output automatically.

**Manual reset & rerun:**
```bash
# Clear old logs
: > /tmp/eshare_devops_dashboard.out
: > /tmp/eshare_devops_dashboard.err

# Force one run
launchctl kickstart -k gui/"$(id -u)"/com.eshare.devops.dashboard

# Wait and inspect
sleep 2
tail -n 20 /tmp/eshare_devops_dashboard.out
tail -n 20 /tmp/eshare_devops_dashboard.err
```

**OneDrive/SharePoint file lock handling:**
The Python script includes retry logic (5 attempts with exponential backoff) to handle "Resource deadlock avoided" errors that can occur when OneDrive is syncing the CSV files.

---

## 6. Health check commands (quick status & tests)

Use these commands any time you want to check or debug the job:

```
# Is the agent loaded?
launchctl list | grep com.eshare.devops.dashboard

# See how launchd currently understands this job (program, args, interval, etc.)
launchctl print gui/"$(id -u)"/com.eshare.devops.dashboard
```

```
# Force an immediate run
launchctl kickstart -k gui/"$(id -u)"/com.eshare.devops.dashboard
```

```
# Inspect recent output and error logs
tail -n 20 /tmp/eshare_devops_dashboard.out
tail -n 20 /tmp/eshare_devops_dashboard.err
```

These commands let you confirm that the job is loaded, see which script and arguments are actually being executed, and quickly inspect logs without opening Console.

---

## 7. Apply changes, stop, or remove the job

**After editing plist or shell script:**
```bash
./reload-launchd-agent.sh
```

**To temporarily stop:**
```bash
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
```

**To start again:**
```bash
launchctl load ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
```

**To fully remove:**
```bash
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
rm ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
rm /tmp/eshare_devops_dashboard.out /tmp/eshare_devops_dashboard.err 2>/dev/null
```

---

## References
[1] Using launchd agents to schedule scripts on macOS - David Hamann https://davidhamann.de/2018/03/13/setting-up-a-launchagent-macos-cron/
[2] MacOS launchd plist StartInterval and StartCalendarInterval examples https://alvinalexander.com/mac-os-x/launchd-plist-examples-startinterval-startcalendarinterval/
[3] A launchd Tutorial https://www.launchd.info
[4] Kickstarting and tearing down with launchctl https://eclecticlight.co/2019/08/27/kickstarting-and-tearing-down-with-launchctl/
[5] Running Launchd Services with Non Root User on macOS https://stackoverflow.com/questions/70127661/running-launchd-services-with-non-root-user-on-macos
[6] Launchctl 2.0 Syntax | Babo D's Corner - WordPress.com https://babodee.wordpress.com/2016/04/09/launchctl-2-0-syntax/
[7] launchd StartInterval problem | Community - Jamf Nation https://community.jamf.com/fid-2/tid-41725
[8] tail - Mac OS X in a Nutshell [Book] - O'Reilly https://www.oreilly.com/library/view/mac-os-x/0596003706/re369.html
[9] macOS launchctl commands - rakhesh.com https://rakhesh.com/mac/macos-launchctl-commands/
[10] tail -f issue - Apple Support Communities https://discussions.apple.com/thread/8179959
[11] Autostart Server After Crash - BlueBubbles Documentation https://docs.bluebubbles.app/server/basic-guides/autostart-server-after-crash
[12] Notes on Apple's under-documented launchd - GitHub Gist https://gist.github.com/dabrahams/4092951
[13] Mastering Tail Logs: Importance, Techniques, Challenges, Best ... https://edgedelta.com/company/blog/tail-logs
[14] man page launchd.plist section 5 - manpagez https://www.manpagez.com/man/5/launchd.plist/
[15] Mac Logging and the log Command: A Guide for Apple Admins https://the-sequence.com/mac-logging-and-the-log-command-a-guide-for-apple-admins
[16] How does StartInterval key affects the started daemon - Stack Overflow https://stackoverflow.com/questions/26627227/how-does-startinterval-key-affects-the-started-daemon
[17] Retrieve last 100 lines logs - Stack Overflow https://stackoverflow.com/questions/36989457/retrieve-last-100-lines-logs
[18] Creating Launch Daemons and Agents - Apple Developer https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
[19] View log messages in Console on Mac - Apple Support https://support.apple.com/guide/console/log-messages-cnsl1012/mac
[20] How to Run a Program or Script Hourly on macOS - Veerpal Brar https://veerpalbrar.github.io/blog/How-to-Run-A-Program-or-Script-Hourly-on-MacOS/
