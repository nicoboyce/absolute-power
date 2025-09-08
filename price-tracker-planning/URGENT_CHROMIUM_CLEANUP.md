# URGENT: Chromium Process Leak - Critical Memory Issue

## Priority: 🔴 CRITICAL - System Memory Exhausted

### Current Situation (as of 08/09/2025 11:35 BST)
- **65 zombie chromium processes** running on the Raspberry Pi
- **SWAP completely full** (511MB/511MB used)
- **RAM critically low** (716MB/921MB used, only 204MB available)
- **Load average dangerously high** (3.70, 3.26, 2.66)
- Processes running since Sep 7 (over 24 hours) consuming massive resources

### Root Cause
The `deploy.sh` script is spawning headless Chromium browsers for web scraping but **NOT properly terminating them**. Each hourly cron run (at :00) creates new processes without cleaning up old ones.

## Immediate Actions Required

### 1. Emergency Cleanup (DO THIS FIRST)
```bash
# Kill all old chromium processes
pkill -f "chromium.*headless"

# Verify processes are gone
ps aux | grep chromium | wc -l

# Check memory recovery
free -h
```

### 2. Fix the deploy.sh Script
The script needs proper browser cleanup. Look for these issues:

#### Check for Missing browser.quit() or browser.close()
```python
# BAD - browser never closes
browser = webdriver.Chrome(options=chrome_options)
browser.get(url)
# script ends without cleanup

# GOOD - proper cleanup
browser = webdriver.Chrome(options=chrome_options)
try:
    browser.get(url)
    # do work
finally:
    browser.quit()  # CRITICAL: Always quit the browser
```

#### Add Process Timeout Protection
```python
import signal
import atexit

def cleanup_browser():
    if browser:
        try:
            browser.quit()
        except:
            pass

# Register cleanup on script exit
atexit.register(cleanup_browser)

# Add timeout to prevent hung processes
signal.alarm(300)  # 5 minute timeout
```

### 3. Monitor Script Improvements Needed

#### A. Add Pre-execution Cleanup
At the start of `deploy.sh`, add:
```bash
# Kill any lingering chromium processes from previous runs
pkill -f "chromium.*headless.*price" || true
```

#### B. Add Process Limits
```python
# Check if too many chromium processes already running
import subprocess
result = subprocess.run(['pgrep', '-c', 'chromium'], capture_output=True, text=True)
if int(result.stdout.strip()) > 10:
    print("ERROR: Too many chromium processes already running")
    sys.exit(1)
```

#### C. Use Context Managers
```python
from contextlib import contextmanager

@contextmanager
def get_browser():
    browser = None
    try:
        browser = webdriver.Chrome(options=chrome_options)
        yield browser
    finally:
        if browser:
            browser.quit()

# Usage
with get_browser() as browser:
    browser.get(url)
    # browser automatically closes even if error occurs
```

### 4. Cron Job Modification
Consider adding a cleanup job:
```bash
# Add to crontab
55 * * * * pkill -f "chromium.*headless" || true  # Cleanup 5 mins before next run
```

### 5. Long-term Fixes

1. **Implement proper Selenium Grid** or browser pooling
2. **Use requests library** instead of Selenium where possible
3. **Add monitoring alerts** for high process counts
4. **Consider using Playwright** instead of Selenium (better resource management)
5. **Add memory checks** before spawning new browsers

## Files to Check
1. `/home/nico/absolute/absolute-power/price-tracker-planning/deploy.sh`
2. `/home/nico/absolute/absolute-power/price-tracker-planning/scrape_all.py`
3. `/home/nico/absolute/absolute-power/price-tracker-planning/generate.py`
4. Any files in `/home/nico/absolute/absolute-power/price-tracker-planning/scrapers/`

## Testing After Fixes
```bash
# Run the script manually
cd /home/nico/absolute/absolute-power/price-tracker-planning
./deploy.sh

# Monitor processes
watch 'ps aux | grep chromium | wc -l'

# Check for cleanup after script ends
ps aux | grep chromium
```

## Success Criteria
- [ ] No chromium processes remain after script completion
- [ ] Memory usage returns to normal after script runs
- [ ] Swap usage drops below 50%
- [ ] Load average stays below 2.0
- [ ] Script completes within 5 minutes

## Notes
- The RSS feed script is working perfectly - no issues there
- This is specifically a price tracker problem
- System has been under memory pressure for at least 24 hours
- Raspberry Pi cannot handle 65+ browser processes

**Created by Claude on 08/09/2025 for urgent attention**