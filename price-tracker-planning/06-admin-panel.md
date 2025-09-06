# Admin Panel

## Requirements

### Product Management
- Add/edit/delete products
- Bulk import from CSV or API
- Manage product categories and attributes
- Handle product variations and duplicates

### Retailer Management
- Add new retailers and scraping targets
- Configure scraping rules per retailer
- Monitor scraper health and success rates
- Update affiliate links and commission rates

### System Monitoring
- View scraping status and recent failures
- Monitor email delivery rates
- Track system performance metrics
- Alert logs and error reporting

### Revenue Tracking
- Affiliate click and conversion reports
- Revenue breakdown by retailer/product
- Performance analytics and trends

## Decisions Log

**Admin Interface**: Mixed approach - CLI scripts + direct file editing
- Python CLI scripts for bulk operations (adding products, retailers)
- Direct JSON file editing for tweaks and configuration
- Claude Code assistance for updates and maintenance
- No web interface needed for MVP

## Implementation Details

### CLI Scripts Available

**Product Management:**
```bash
# Add new product
python add_product.py --brand "EcoFlow" --model "Delta Pro 3" --capacity "4096Wh" --chemistry "LiFePO4"

# Update product specs
python update_product.py --id "ecoflow-delta-pro-3" --weight "51.5kg"

# Bulk import from CSV
python import_products.py --csv products.csv --category power-stations

# Validate all products
python validate_products.py
```

**Retailer Management:**
```bash
# Add new retailer
python add_retailer.py --name "EcoFlow UK" --url "https://uk.ecoflow.com" --commission "5%"

# Update retailer URLs for all products
python update_retailer_urls.py --retailer ecoflow --pattern "old-url" --replace "new-url"

# Test retailer scraping
python test_scraper.py --retailer ecoflow --product ecoflow-delta-pro-3
```

**System Monitoring (Enhanced):**
```bash
# Full system status
./monitor.py

# Detailed scraping report
./monitor.py --scrapes 24 --detailed

# Generate weekly report
python generate_report.py --weekly

# Check for failed scrapes
python check_failures.py --last 24h
```

### File-Based Configuration

**Direct editing for quick changes:**
```bash
# Edit product specs
vim data/products/power-stations/ecoflow-delta-pro-3.json

# Update retailer config
vim config/retailers.json

# Modify scraping schedule
crontab -e
```

### Claude Code Integration
```bash
# Generate product JSON from specs
echo "Brand: EcoFlow, Model: Delta Pro 3, Capacity: 4096Wh..." | claude_generate_product.py

# Analyze pricing trends
claud_analyze_prices.py --product ecoflow-delta-pro-3 --days 30

# Bulk update from manufacturer specs
claud_bulk_update.py --source manufacturer_specs.pdf
```

### Revenue Tracking Scripts
```bash
# Affiliate performance report
python affiliate_report.py --month 2025-01

# Product performance analysis
python product_analysis.py --top-performers 10

# Revenue projection
python revenue_forecast.py --based-on last-3-months
```

### Backup & Maintenance
```bash
# Backup all data
python backup_data.py --destination /backup/$(date +%Y%m%d)

# Clean old price data (optional)
python cleanup_prices.py --older-than 1year --dry-run

# Rebuild all static pages
python rebuild_site.py --full
```

### Error Handling & Alerts
```bash
# Check for scraping issues
python health_check.py --alert-email admin@domain.com

# Fix common data issues
python fix_data_issues.py --auto-fix duplicates,missing-specs

# Validate affiliate links
python check_affiliate_links.py --test-all
```

## Resolved Questions

**Authentication**: Not needed for CLI-based admin (Pi access control sufficient)

**Bulk Operations**: CSV import scripts + validation pipeline handles efficiently

**Real-time Status**: monitor.py provides comprehensive real-time system status

**Product Addition Workflow**: 
1. CLI script creates JSON template
2. Manual spec completion/validation
3. Claude Code assistance for complex products
4. Automated deployment after validation