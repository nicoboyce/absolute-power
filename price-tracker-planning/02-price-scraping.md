# Price Scraping System

## Requirements

### Core Scraping
- Extract product prices from retailer websites
- Handle different website structures and layouts
- Robust error handling and retry logic
- Rate limiting to avoid being blocked
- User agent rotation and proxy support

### Scheduling
- Regular price updates (hourly/daily based on product)
- Prioritise popular products for more frequent updates
- Handle failed scrapes with exponential backoff
- Queue management for large product catalogues

### Data Processing
- Clean and normalise scraped price data
- Handle different price formats and currencies
- Detect and flag suspicious price changes
- Store raw scraping data for debugging

### Monitoring
- Track scraping success rates per retailer
- Alert when scrapers break or fail consistently
- Monitor for website structure changes

## Decisions Log

**Scraping Technology**: BeautifulSoup + requests
- Lightweight for Raspberry Pi prototype
- Good for most retailer websites
- Upgrade to Selenium/Playwright if needed later

**Retailer Priority**: Start with easier targets first
- Avoid Amazon initially (requires API approval + sales)  
- Focus on retailers with simpler anti-bot measures
- Add Amazon via API once Associates program generates revenue

**UK Power Station Retailers**: Initial prototype targets
- Currys (major electronics, reasonable scraping)
- Argos (wide availability, simpler structure)  
- Anker UK (direct manufacturer, affiliate program)

**Scraping Schedule**: Hourly cron job
- Every hour, 24/7 for testing flexibility
- No technical constraints on Pi
- Catches flash sales and daily deals
- Allows testing at any hour
- Can scale back later if needed

## Implementation Details

### Scraper Architecture
```python
# Base scraper class (scrapers/base.py)
class BaseScraper:
    - Rate limiting (2+ second delays)
    - User agent rotation
    - Session management
    - Error handling & retries
    - Database integration
    - Comprehensive logging
```

### Retailer-Specific Scrapers
```bash
scrapers/
├── base.py              # Abstract base class
├── ecoflow.py          # EcoFlow UK direct
├── jackery.py          # Jackery UK direct  
├── bluetti.py          # Bluetti UK direct
└── currys.py           # Currys template (needs work)
```

### Scraping Schedule (Cron)
```bash
# Every hour - scrape all active products
0 * * * * /home/pi/power-tracker/venv/bin/python /home/pi/power-tracker/scrape_all.py

# Every 6 hours - full system check
0 */6 * * * /home/pi/power-tracker/health_check.py

# Daily - cleanup and reporting
0 2 * * * /home/pi/power-tracker/daily_maintenance.py
```

### Error Handling Strategy
```python
# Retry logic with exponential backoff
# Fallback to cached data if all retailers fail
# Alert system for sustained failures
# Automatic scraper disable after repeated failures
```

### Performance Monitoring
```python
# Track success rates per retailer
# Monitor response times
# Alert on unusual price changes
# Log detailed performance metrics
```

**Development Status**: Framework complete, manufacturer affiliate programs prioritized
- Apply to Jackery UK (8% commission) - PRIORITY
- Apply to EcoFlow via Awin (5% commission)
- Apply to Bluetti direct (5-10% commission)
- Build manufacturer-direct scrapers first (better margins)
- Currys/Argos secondary (lower margins, more blocking)

## Questions to Resolve

- How to handle dynamic content (JavaScript-rendered prices)?
- Legal considerations for web scraping?
- How to detect when retailer websites change structure?
- Handling of regional pricing and availability?