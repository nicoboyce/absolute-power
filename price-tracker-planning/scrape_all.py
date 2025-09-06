#!/usr/bin/env python3
"""
Main scraping script - runs hourly via cron
Scrapes all active products from all enabled retailers
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
    
    # Initialize scrapers
    scrapers = {
        'ecoflow_uk': EcoFlowScraper(),
        'jackery_uk': JackeryScraper(),
        'anker_uk': AnkerScraper()
    }
    
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