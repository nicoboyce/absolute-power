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
    """Load all product JSON files with enhanced data processing"""
    products = []
    products_dir = Path(__file__).parent / "data" / "products" / "power-stations"
    
    for json_file in products_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                product = json.load(f)
                
                # Enhance product data for template
                product = enhance_product_data(product)
                products.append(product)
        except Exception as e:
            logging.error(f"Failed to load {json_file}: {e}")
    
    return products

def enhance_product_data(product):
    """Enhance product data with calculated fields"""
    try:
        # Extract capacity as number for sorting/filtering
        capacity_str = product.get('specs', {}).get('capacity', '0Wh')
        capacity_digits = ''.join(filter(str.isdigit, str(capacity_str)))
        capacity_wh = int(capacity_digits) if capacity_digits else 0
        product['capacity_wh'] = capacity_wh
        
        # Extract weight as number
        weight_str = product.get('specs', {}).get('weight', '0kg')
        weight_digits = ''.join(filter(lambda x: x.isdigit() or x == '.', str(weight_str)))
        weight_kg = float(weight_digits) if weight_digits else 0
        product['weight'] = weight_kg
        
        # Extract AC output watts - handle nested structure
        ac_output = product.get('specs', {}).get('ac_output', {})
        if isinstance(ac_output, dict):
            continuous_power = ac_output.get('continuous', '0W')
            ac_digits = ''.join(filter(str.isdigit, str(continuous_power)))
            ac_output_watts = int(ac_digits) if ac_digits else 0
        else:
            ac_digits = ''.join(filter(str.isdigit, str(ac_output)))
            ac_output_watts = int(ac_digits) if ac_digits else 0
        product['ac_output_watts'] = ac_output_watts
        
        # Extract solar input watts - check multiple possible locations
        solar_input_watts = None
        
        # Check direct solar_input field
        solar_input = product.get('specs', {}).get('solar_input')
        if solar_input and str(solar_input).strip():
            solar_digits = ''.join(filter(str.isdigit, str(solar_input)))
            solar_input_watts = int(solar_digits) if solar_digits else None
        
        # Check in performance/charging_times
        if not solar_input_watts:
            performance = product.get('specs', {}).get('performance', {})
            charging_times = performance.get('charging_times', {})
            solar_info = charging_times.get('solar', '')
            if solar_info and str(solar_info).strip():
                solar_digits = ''.join(filter(str.isdigit, str(solar_info)))
                solar_input_watts = int(solar_digits) if solar_digits else None
        
        product['solar_input_watts'] = solar_input_watts
        
        # Extract battery type - check multiple possible field names
        battery_type = (product.get('specs', {}).get('battery_type') or 
                       product.get('specs', {}).get('chemistry') or 
                       'Li-ion')
        product['battery_type'] = battery_type
        
        # Extract cycle life
        cycle_life = None
        
        # Check direct cycle_life field
        cycle_life_direct = product.get('specs', {}).get('cycle_life')
        if cycle_life_direct and str(cycle_life_direct).strip():
            cycle_digits = ''.join(filter(str.isdigit, str(cycle_life_direct)))
            cycle_life = int(cycle_digits) if cycle_digits else None
        
        # Check in performance section
        if not cycle_life:
            performance = product.get('specs', {}).get('performance', {})
            cycle_life_perf = performance.get('cycle_life', '')
            if cycle_life_perf and str(cycle_life_perf).strip():
                cycle_digits = ''.join(filter(str.isdigit, str(cycle_life_perf)))
                cycle_life = int(cycle_digits) if cycle_digits else None
        
        product['cycle_life'] = cycle_life
        
        # Extract USB ports (simplified for now)
        usb_ports = product.get('specs', {}).get('usb_ports', [])
        if isinstance(usb_ports, str):
            usb_digits = ''.join(filter(str.isdigit, usb_ports))
            usb_count = int(usb_digits) if usb_digits else 2  # Default to 2
            usb_ports = [{'type': 'USB-A', 'count': usb_count}]
        elif not isinstance(usb_ports, list):
            # Default to 2 USB ports for most power stations
            usb_ports = [{'type': 'USB-A', 'count': 2}]
        product['usb_ports'] = usb_ports
        
        # Add brand extraction
        brand_name = product.get('brand', '').lower() or product.get('name', '').split()[0].lower()
        product['brand'] = brand_name or 'unknown'
        
        # Create slug for URLs
        product['slug'] = product.get('id', '').replace('_', '-')
        
        return product
        
    except Exception as e:
        # If any processing fails, return the original product with safe defaults
        logging.warning(f"Failed to enhance product data for {product.get('name', 'unknown')}: {e}")
        product['capacity_wh'] = 0
        product['weight'] = 0
        product['ac_output_watts'] = 0
        product['solar_input_watts'] = None
        product['battery_type'] = 'Li-ion'
        product['cycle_life'] = None
        product['usb_ports'] = [{'type': 'USB-A', 'count': 2}]
        product['brand'] = product.get('brand', '').lower() or 'unknown'
        product['slug'] = product.get('id', '').replace('_', '-')
        return product

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

def process_products_with_prices(products, prices):
    """Process products with pricing data"""
    processed_products = []
    
    for product in products:
        product_id = product.get('id')
        product_prices = prices.get(product_id, [])
        
        # Add price information to product
        product['prices'] = product_prices
        
        # Calculate min price and best deal info
        if product_prices:
            in_stock_prices = [p for p in product_prices if p.get('in_stock', True) and p.get('price')]
            if in_stock_prices:
                min_price = min(in_stock_prices, key=lambda x: x['price'])['price']
                product['min_price'] = min_price
                
                # Calculate value per Wh
                if product['capacity_wh'] > 0:
                    product['value_per_wh'] = product['capacity_wh'] / min_price
                
                # Mock discount calculation for demo
                product['discount_percentage'] = None
                if min_price < 1000:  # Mock condition
                    original_price = min_price * 1.2
                    discount = ((original_price - min_price) / original_price) * 100
                    if discount > 5:
                        product['discount_percentage'] = int(discount)
        
        processed_products.append(product)
    
    # Sort by best value (capacity per pound)
    processed_products.sort(key=lambda x: x.get('value_per_wh', 0), reverse=True)
    
    return processed_products

def generate_site():
    """Main site generation function"""
    logger = logging.getLogger(__name__)
    logger.info("Starting site generation")
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    # Load data
    products = load_products()
    prices = get_latest_prices()
    
    # Process products with pricing data
    processed_products = process_products_with_prices(products, prices)
    
    # Ensure static directory exists
    STATIC_DIR.mkdir(exist_ok=True)
    (STATIC_DIR / "products").mkdir(exist_ok=True)
    
    # Try enhanced template first, fallback to original
    try:
        homepage_template = env.get_template('enhanced_homepage.html')
        logger.info("Using enhanced homepage template")
    except:
        homepage_template = env.get_template('homepage.html')
        logger.info("Using original homepage template")
    
    # Generate homepage
    homepage_html = homepage_template.render(
        products=processed_products,
        site_name=SITE_NAME,
        site_url=SITE_URL,
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
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