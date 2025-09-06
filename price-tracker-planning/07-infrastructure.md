# Infrastructure

## Requirements

### Hosting Environment
- Scalable web application hosting
- Database hosting with backup strategies
- Static asset delivery (images, CSS, JS)
- SSL certificates and security

### Email Delivery
- Reliable transactional email service
- Handle high volume email sending
- Bounce and unsubscribe management
- Email template management

### Monitoring & Logging
- Application performance monitoring
- Error tracking and alerting
- Scraping job monitoring
- Database performance metrics

### Backup & Recovery
- Automated database backups
- Code repository backup
- Disaster recovery procedures
- Data retention policies

### Scaling Considerations
- Handle increased traffic and data volume
- Database optimisation for large datasets
- Caching strategies for performance
- Load balancing for high availability

## Decisions Log

**Hosting Architecture**: Local development server + web hosting deployment
- Price scraping: Python cron on local server
- Database: MariaDB on local server for processing
- Static site generation: Local build process
- Deployment: Push generated site to web hosting
- Separates heavy processing from public hosting

**Prototype Architecture**: Raspberry Pi + static hosting
- All processing on Raspberry Pi (scraping, data storage, site generation)
- No database needed on web hosting for prototype
- Simple file-based data storage initially
- Cron job pushes static files to web server
- Scale up to proper architecture later

**Deployment Method**: rsync over SSH
- Direct rsync from Pi to web hosting
- Cleaner than GitHub webhook hack
- Immediate deployment after site generation
- Simple authentication via SSH keys

**Email/Notification Service**: TBD - considering alternatives like WhatsApp

**Frontend Architecture**: Static site generated periodically
- HTML/CSS/JS static files
- Rebuild entire site when prices update
- No server-side processing needed
- Maximum simplicity and speed

**Static Site Generation**: Python + Jinja2 templates
- Same language as scraping scripts
- Simple template-based HTML generation
- No additional tools or dependencies needed

## Implementation Details

### Raspberry Pi Setup
**Hardware Requirements:**
- Raspberry Pi 4 (4GB+ RAM recommended)
- 64GB+ SD card (Class 10)
- Reliable power supply
- Ethernet connection (preferred over WiFi for stability)

**Software Stack:**
- Raspberry Pi OS (64-bit)
- Python 3.9+
- MariaDB 10.6+
- Cron for scheduling

### Directory Structure (Pi)
```
/home/pi/power-tracker/
├── venv/                 # Python virtual environment
├── data/
│   ├── products/         # JSON product files
│   └── prices/           # Price history exports
├── scrapers/            # Web scraping scripts
├── templates/           # Jinja2 templates
├── static/              # Generated static site
├── logs/                # Scraping logs (5 types)
└── deploy/              # rsync deployment scripts
```

### Cron Schedule
```bash
# Hourly scraping (24/7)
0 * * * * /home/pi/power-tracker/venv/bin/python /home/pi/power-tracker/scrape.py

# Site regeneration after scraping
15 * * * * /home/pi/power-tracker/venv/bin/python /home/pi/power-tracker/generate.py

# Deployment to web hosting
30 * * * * /home/pi/power-tracker/deploy.sh

# Daily log cleanup
0 2 * * * /home/pi/power-tracker/cleanup_logs.py
```

### rsync Deployment Command
```bash
rsync -avz --delete /home/pi/power-tracker/static/ user@domain.com:/path/to/web/directory/
```

### Logging Infrastructure
**5 Log Types Implemented:**
- `power_tracker.log` - Main application (10MB rotating, 5 backups)
- `scraping.log` - Detailed scraping activity (10MB, 10 backups)
- `site_generation.log` - Static site builds (5MB, 3 backups)  
- `deployment.log` - rsync operations (5MB, 3 backups)
- `errors.log` - Error-only quick reference (5MB, 5 backups)
- `daily_summary.log` - Daily stats (30 days retention)

### Monitoring Commands Available
```bash
# Full status overview
./monitor.py

# Quick one-line status
./quick_status.py

# Recent scraping activity
./monitor.py --scrapes 6

# View specific logs
./monitor.py --logs scraping --lines 50
```

### Database Schema (MariaDB)
**Tables Created:**
- `price_history` - All price data with timestamps
- `email_subscriptions` - User alerts (future use)  
- `scrape_log` - Success/failure tracking per scrape
- `latest_prices` - View for current prices per retailer
- `price_comparison` - View for min/max/avg across retailers

### Security Considerations
- SSH key authentication for deployment
- MariaDB with dedicated user/password
- Log files with appropriate permissions
- No secrets stored in code (environment variables)

## Scaling Path

### Phase 2 (Growth)
- Migrate Pi database to cloud MariaDB
- Keep Pi for scraping, deploy database to cloud
- Add multiple product categories
- Implement proper backup strategies

### Phase 3 (Scale)
- Multiple scraping instances
- Load balancing for high traffic
- CDN for static assets
- Professional monitoring (Datadog, etc.)

## Resolved Questions

~~Cloud provider selection~~ → Not needed for MVP, existing web hosting sufficient
~~Cost optimisation~~ → Minimal costs: Pi hardware + existing hosting  
~~GDPR compliance~~ → Email collection only, simple privacy policy sufficient
~~Development vs production~~ → Single Pi environment, git for version control