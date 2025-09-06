#!/usr/bin/env python3
"""
Static site generation script
Builds HTML pages from product data and price history
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
try:
    import mariadb
    HAS_MARIADB = True
except ImportError:
    HAS_MARIADB = False
    print("MariaDB not available - generating with mock data")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DB_CONFIG, STATIC_DIR, TEMPLATES_DIR, SITE_NAME, SITE_URL
from logging_config import setup_logging
import logging

def get_db_connection():
    """Get database connection"""
    if not HAS_MARIADB:
        return None
        
    try:
        return mariadb.connect(**DB_CONFIG)
    except mariadb.Error as e:
        logging.error(f"Database connection failed: {e}")
        return None

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

def get_latest_prices():
    """Get latest prices from JSON files"""
    prices_dir = Path(__file__).parent / "data" / "prices"
    
    # If no prices directory, return empty
    if not prices_dir.exists():
        logging.warning("No prices directory found")
        return {}
    
    # Find the most recent prices file
    price_files = sorted(prices_dir.glob("prices_*.json"), reverse=True)
    
    if not price_files:
        logging.warning("No price files found")
        # Return some mock data for testing
        return {
            'ecoflow-delta-2': [
                {
                    'retailer': 'ecoflow_uk',
                    'price': 899.00,
                    'in_stock': True,
                    'scraped_at': datetime.now().isoformat(),
                    'url': 'https://uk.ecoflow.com/products/delta-2-portable-power-station'
                }
            ]
        }
    
    # Load the most recent prices file
    latest_file = price_files[0]
    logging.info(f"Loading prices from {latest_file.name}")
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Format the data for templates
        prices = {}
        for product_id, product_prices in data.items():
            if product_id not in prices:
                prices[product_id] = []
            
            # Get the latest price for each retailer
            retailers_seen = set()
            for price_data in reversed(product_prices):  # Most recent first
                retailer = price_data['retailer']
                if retailer not in retailers_seen:
                    retailers_seen.add(retailer)
                    prices[product_id].append({
                        'retailer': retailer,
                        'price': price_data['price'],
                        'in_stock': price_data['in_stock'],
                        'scraped_at': price_data['scraped_at'],
                        'url': price_data['url']
                    })
            
            # Sort by price
            prices[product_id].sort(key=lambda x: x['price'] if x['price'] else float('inf'))
        
        return prices
        
    except Exception as e:
        logging.error(f"Failed to load prices from {latest_file}: {e}")
        return {}
    
    # Fallback to database if JSON fails and database is available
    if HAS_MARIADB:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT product_id, retailer, price, in_stock, scraped_at, url
                    FROM latest_prices
                    ORDER BY product_id, price ASC
                """)
                
                prices = {}
                for row in cursor.fetchall():
                    product_id, retailer, price, in_stock, scraped_at, url = row
                    
                    if product_id not in prices:
                        prices[product_id] = []
                    
                    prices[product_id].append({
                        'retailer': retailer,
                        'price': float(price),
                        'in_stock': bool(in_stock),
                        'scraped_at': scraped_at,
                        'url': url
                    })
                
                cursor.close()
                conn.close()
                return prices
                
            except mariadb.Error as e:
                logging.error(f"Failed to fetch prices from database: {e}")
    
    return {}

def generate_site():
    """Main site generation function"""
    logger = logging.getLogger(__name__)
    logger.info("Starting site generation")
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    # Load data
    products = load_products()
    prices = get_latest_prices()
    
    # Ensure static directory exists
    STATIC_DIR.mkdir(exist_ok=True)
    (STATIC_DIR / "products").mkdir(exist_ok=True)
    
    # Generate homepage
    homepage_template = env.get_template('homepage.html')
    homepage_html = homepage_template.render(
        products=products,
        prices=prices,
        site_name=SITE_NAME,
        site_url=SITE_URL,
        generated_at=datetime.now()
    )
    
    with open(STATIC_DIR / "index.html", 'w') as f:
        f.write(homepage_html)
    
    logger.info("Generated homepage")
    
    pages_generated = 1  # Homepage
    
    # Generate test page with modern design
    try:
        test_template = env.get_template('test.html')
        
        # Find best deal for hero section
        hero_deal = None
        best_value = 0
        for product in products:
            product_prices = prices.get(product['id'], [])
            if product_prices:
                # Calculate value per Wh for best deal detection
                capacity_wh = int(product['specs']['capacity'].replace('Wh', '').replace(',', ''))
                lowest_price = min([p['price'] for p in product_prices if p['in_stock']], default=None)
                if lowest_price and capacity_wh > 0:
                    value_per_wh = capacity_wh / lowest_price
                    if value_per_wh > best_value:
                        best_value = value_per_wh
                        # Simulate savings for demo
                        original_price = lowest_price * 1.5  # Mock original price
                        hero_deal = {
                            'id': product['id'],
                            'name': product['name'],
                            'current_price': lowest_price,
                            'original_price': original_price,
                            'savings': original_price - lowest_price,
                            'discount_percent': int(((original_price - lowest_price) / original_price) * 100)
                        }
        
        test_html = test_template.render(
            products=products,
            prices=prices,
            hero_deal=hero_deal,
            site_name=SITE_NAME,
            site_url=SITE_URL,
            generated_at=datetime.now()
        )
        
        with open(STATIC_DIR / "test.html", 'w') as f:
            f.write(test_html)
        
        logger.info("Generated test page")
        pages_generated += 1
        
    except Exception as e:
        logger.error(f"Failed to generate test page: {e}")
    
    # Generate individual product pages
    product_template = env.get_template('product.html')
    
    for product in products:
        product_id = product['id']
        product_prices = prices.get(product_id, [])
        
        # Find lowest price
        lowest_price = None
        if product_prices:
            in_stock_prices = [p for p in product_prices if p['in_stock']]
            if in_stock_prices:
                lowest_price = min(in_stock_prices, key=lambda x: x['price'])
        
        product_html = product_template.render(
            product=product,
            prices=product_prices,
            lowest_price=lowest_price,
            site_name=SITE_NAME,
            site_url=SITE_URL,
            generated_at=datetime.now()
        )
        
        product_file = STATIC_DIR / "products" / f"{product_id}.html"
        with open(product_file, 'w') as f:
            f.write(product_html)
        
        pages_generated += 1
        logger.info(f"Generated page for {product_id}")
    
    logger.info(f"Site generation completed: {pages_generated} pages for {len(products)} products")
    
    # Log to summary
    summary_logger = logging.getLogger('summary')
    summary_logger.info(f"Site generated: {pages_generated} pages for {len(products)} products")
    
    return pages_generated

if __name__ == '__main__':
    setup_logging()
    generate_site()