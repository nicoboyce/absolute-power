# Pi Setup Instructions - Claude Ready

## Complete setup commands for Claude to run on the Pi

### 1. Clone and setup project
```bash
# Clone the repository
cd /home/pi
git clone https://github.com/nicoboyce/absolute-power.git power-tracker
cd power-tracker

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Test the setup
python3 scrape_all.py
python3 generate.py
```

### 2. Verify git configuration
```bash
# Check git is configured for pushing
git config --list | grep user
git remote -v

# Test git push access
git pull
echo "# Test commit from Pi - $(date)" >> test-pi.txt
git add test-pi.txt
git commit -m "Pi setup test - $(date)"
git push
```

### 3. Setup cron job for hourly runs
```bash
# Make deploy script executable
chmod +x deploy.sh

# Test deploy script
./deploy.sh

# Add to crontab for hourly execution
(crontab -l 2>/dev/null; echo "0 * * * * /home/pi/power-tracker/deploy.sh") | crontab -

# Verify crontab entry
crontab -l
```

### 4. Monitor and verify
```bash
# Check logs after first run
tail -f logs/deployment.log

# Check git commits
git log --oneline -5

# Verify static files are being generated
ls -la static/
```

### 5. Troubleshooting commands
```bash
# Check Python dependencies
pip list

# Test database connection (will show error if MariaDB not configured)
python3 -c "from config import DB_CONFIG; print('Config loaded')"

# Check disk space
df -h

# Check process status
ps aux | grep python

# View recent cron jobs
grep CRON /var/log/syslog | tail -10
```

## Expected Results

After setup:
- Repository cloned to `/home/pi/power-tracker`
- Virtual environment activated with all dependencies
- Cron job running hourly at minute 0
- Static site regenerated every hour with latest prices
- Git commits pushed automatically with timestamp

## Files to monitor
- `logs/deployment.log` - Main deployment log
- `logs/scraping.log` - Scraping activity  
- `logs/generation.log` - Site generation
- `static/index.html` - Generated homepage
- `static/products/*.html` - Product pages

## Manual test command
```bash
cd /home/pi/power-tracker && ./deploy.sh
```