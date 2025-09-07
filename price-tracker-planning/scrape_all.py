#!/usr/bin/env python3
"""
Main scraping orchestrator - runs hourly via cron on Raspberry Pi

This script coordinates all retailer scrapers to gather pricing data across
the entire product catalogue. It's the heart of the price tracking system.

DEPLOYMENT NOTES:
- Runs every hour via cron job on Raspberry Pi
- Results are saved to JSON files in data/prices/
- After scraping, generate.py rebuilds the static site
- Logs are written to logs/ directory for monitoring

ARCHITECTURE:
1. Load all product JSON files from data/products/power-stations/
2. Initialize all available scrapers (5 active retailers)
3. For each product, scrape all configured retailers
4. Save results to daily JSON files
5. Log comprehensive statistics for monitoring

ACTIVE SCRAPERS (as of 2025-09-07):
- Jackery UK: Direct manufacturer scraping
- Anker UK: Direct manufacturer scraping  
- Currys: UK electronics retailer
- Amazon UK: Major e-commerce platform
- Bluetti UK: Direct manufacturer scraping
- EcoFlow UK: Direct manufacturer scraping (with promotional price filtering)

MAINTENANCE:
- Check scrape success rates regularly (should be >80%)
- Monitor for new anti-scraping measures
- Add new retailers by creating scraper classes and adding here
- Update product JSON files to add new retailer URLs

TROUBLESHOOTING:
- Low success rates: Check if sites changed HTML structure
- 403/429 errors: Sites may have blocked our IP - adjust headers/delays
- No prices found: Sites may have implemented JavaScript-only pricing

LAST UPDATED: 2025-09-07
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from logging_config import setup_logging
from scrapers.ecoflow import EcoFlowScraper
from scrapers.jackery import JackeryScraper  
from scrapers.anker import AnkerScraper
from scrapers.currys import CurrysScraper
from scrapers.amazon_uk import AmazonUKScraper
from scrapers.bluetti_uk import BluettiUKScraper
from scrapers.argos import ArgosScraper
from scrapers.ebay_official import EbayOfficialScraper
from scrapers.goalzero_uk import GoalZeroUKScraper
from scrapers.outdoorsupply import OutdoorSupplyScraper

# Import headless scrapers with fallback
try:
    from scrapers.headless_scraper import EcoFlowHeadlessScraper, BluettiHeadlessScraper
    # Note: On Raspberry Pi, Selenium/Chromium may have issues in headless mode
    # Falling back to standard scrapers if needed
    HEADLESS_AVAILABLE = True
    logging.info("Headless scrapers available (may not work on ARM)")
except ImportError as e:
    HEADLESS_AVAILABLE = False
    logging.warning(f"Headless scrapers disabled: {e}")

def load_products():
    """Load all product JSON files"""
    products = []
    products_dir = Path(__file__).parent / "data" / "products" / "power-stations"
    
    for json_file in products_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                product = json.load(f)
                products.append(product)
        except Exception as e:
            logging.error(f"Failed to load {json_file}: {e}")
    
    return products

def scrape_all_retailers():
    """Main scraping orchestrator"""
    logger = logging.getLogger(__name__)
    
    # Initialize scrapers - mix of standard and headless
    scrapers = {
        'jackery_uk': JackeryScraper(),
        'anker_uk': AnkerScraper(),
        'currys': CurrysScraper(),
        'amazon_uk': AmazonUKScraper(),
        'bluetti_uk': BluettiUKScraper(),
        'argos': ArgosScraper(),
        'ebay_official': EbayOfficialScraper(),
        'goalzero_uk': GoalZeroUKScraper(),
        'outdoorsupply': OutdoorSupplyScraper()
    }
    
    # Add headless scrapers if available (for JS-heavy sites)
    if HEADLESS_AVAILABLE:
        scrapers.update({
            'ecoflow_uk': EcoFlowHeadlessScraper(),
            'bluetti_uk': BluettiHeadlessScraper()
        })
        logger.info("Headless browser scrapers enabled")
    else:
        # Fallback to standard scraper for EcoFlow
        scrapers['ecoflow_uk'] = EcoFlowScraper()
        logger.warning("Using standard scrapers - some sites may fail")
    
    products = load_products()
    total_scrapes = 0
    successful_scrapes = 0
    
    logger.info(f"Starting scrape run: {len(products)} products, {len(scrapers)} retailers")
    
    for product in products:
        product_id = product['id']
        
        for retailer_key, scraper in scrapers.items():
            if retailer_key in product.get('retailers', {}):
                retailer_data = product['retailers'][retailer_key]
                url = retailer_data.get('url')
                
                if url:
                    logger.info(f"Scraping {product_id} from {retailer_key}")
                    total_scrapes += 1
                    
                    try:
                        # Check if it's a headless scraper and run async
                        if hasattr(scraper, 'scrape_product_async'):
                            import asyncio
                            result = asyncio.run(scraper.scrape_product_async(product_id, url))
                        else:
                            result = scraper.scrape_product(product_id, url)
                            
                        if result:
                            successful_scrapes += 1
                            logger.info(f"✓ {product_id} @ {retailer_key}: £{result['price']}")
                        else:
                            logger.warning(f"✗ {product_id} @ {retailer_key}: No result")
                            
                    except Exception as e:
                        logger.error(f"✗ {product_id} @ {retailer_key}: {str(e)}")
    
    # Log summary
    success_rate = (successful_scrapes / total_scrapes * 100) if total_scrapes > 0 else 0
    logger.info(f"Scrape completed: {successful_scrapes}/{total_scrapes} successful ({success_rate:.1f}%)")
    
    # Log to summary for monitoring
    summary_logger = logging.getLogger('summary')
    summary_logger.info(f"Scrape completed: {successful_scrapes}/{total_scrapes} successful, {len(products)} products")
    
    return successful_scrapes, total_scrapes

if __name__ == '__main__':
    setup_logging()
    scrape_all_retailers()