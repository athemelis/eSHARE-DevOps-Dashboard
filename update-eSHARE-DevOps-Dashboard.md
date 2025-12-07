# eShare DevOps Dashboard – Automatic Refresh (macOS launchd)

This setup runs your `generate_dashboard.py` script every minute using a `launchd` LaunchAgent. Your current layout:

- Shell wrapper script (Git checkout):  
  `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/update-eSHARE-DevOps-Dashboard.sh`
- Dashboard project (in OneDrive):  
  `/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ᵉShare DevOps Dashboard`

---

## 1. Create/update the runner shell script

File:

`/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/update-eSHARE-DevOps-Dashboard.sh`

Contents:

```
#!/bin/bash

cd "/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ᵉShare DevOps Dashboard"

/usr/bin/python3 generate_dashboard.py \
  -c "../ALL Items.csv" \
  -g "../Org Chart.csv" \
  -t Templates \
  -o "../ᵉShare DevOps Dashboard.html"
```

Make it executable:

```
chmod +x "/Users/tonythem/GitHub/ᵉShare DevOps Dashboard/update_ᵉShare_DevOps_Dashboard.sh"
```

The `cd` ensures the script runs in the correct directory so the relative CSV/template paths work as expected.[web:7]

---

## 2. Create the LaunchAgent plist

Ensure the LaunchAgents folder exists:

```
mkdir -p ~/Library/LaunchAgents
```

Create:

`~/Library/LaunchAgents/com.eshare.devops.dashboard.plist`

with:

```
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
    </array>

    <!-- Run every 60 seconds (1 minute) -->
    <key>StartInterval</key>
    <integer>60</integer>

    <!-- Also run once immediately when loaded -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Logs for debugging -->
    <key>StandardOutPath</key>
    <string>/tmp/eshare_devops_dashboard.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/eshare_devops_dashboard.err</string>
</dict>
</plist>
```

`StartInterval` is in seconds; `60` means “run every minute”.[web:16][web:149]

---

## 3. Load the agent and force a first run

Initial load:

```
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist 2>/dev/null || true
launchctl load   ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
```

Force the job to run immediately (without waiting a minute):

```
launchctl kickstart -k gui/"$(id -u)"/com.eshare.devops.dashboard
```

- `kickstart` tells `launchd` to start the job now.  
- `-k` kills any existing instance before starting a new one, which is useful when testing changes.[web:95][web:96][web:97]

---

## 4. Logs, debugging, and the “reset & rerun” steps that worked

The job’s stdout/stderr go to:

- Output: `/tmp/eshare_devops_dashboard.out`  
- Errors: `/tmp/eshare_devops_dashboard.err`

A handy “reset & rerun” sequence (this is what un-stuck your job):

```
# Clear old error log so only the next run’s errors are visible
> /tmp/eshare_devops_dashboard.err

# Force one run of the current LaunchAgent definition
launchctl kickstart -k gui/"$(id -u)"/com.eshare.devops.dashboard

# Wait a moment and inspect fresh errors (if any)
sleep 2
tail -n 20 /tmp/eshare_devops_dashboard.err
```

Truncating the log avoids confusing old errors (from earlier configurations) with current behavior, and `kickstart` guarantees the latest plist and script are what’s actually being run.[web:24][web:95][web:145]

---

## 5. Health check commands (quick status & tests)

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

These commands let you confirm that the job is loaded, see which script and arguments are actually being executed, and quickly inspect logs without opening Console.[web:27][web:33][web:95]

---

## 6. Apply changes, stop, or remove the job

When you edit either the plist or the `.sh` script, reload:

```
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
launchctl load   ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
launchctl kickstart -k gui/"$(id -u)"/com.eshare.devops.dashboard
```

To temporarily stop it:

```
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
```

To start it again:

```
launchctl load ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
```

To fully remove the job:

```
launchctl unload ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
rm ~/Library/LaunchAgents/com.eshare.devops.dashboard.plist
rm /tmp/eshare_devops_dashboard.out /tmp/eshare_devops_dashboard.err 2>/dev/null
```

After removal, the script will no longer run automatically every minute.[web:18][web:33]
```

Sources
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
