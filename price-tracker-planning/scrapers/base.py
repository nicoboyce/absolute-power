"""
Base scraper class and utilities
"""

import requests
import time
import random
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
try:
    import mariadb
    HAS_MARIADB = True
except ImportError:
    HAS_MARIADB = False
    print("MariaDB not available - running in test mode")
from config import USER_AGENTS, REQUEST_DELAY, TIMEOUT, DB_CONFIG

class BaseScraper:
    def __init__(self, retailer_name, base_url):
        self.retailer_name = retailer_name
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(f'scraper.{retailer_name}')
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_page(self, url):
        """Fetch a web page with error handling and rate limiting"""
        try:
            # Rate limiting
            time.sleep(REQUEST_DELAY + random.uniform(0, 1))
            
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            self.logger.info(f"Successfully fetched: {url}")
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_price(self, soup):
        """Extract price from page - override in subclasses"""
        raise NotImplementedError("Subclasses must implement extract_price")
    
    def extract_availability(self, soup):
        """Extract availability from page - override in subclasses"""
        raise NotImplementedError("Subclasses must implement extract_availability")
    
    def scrape_product(self, product_id, url):
        """Scrape a single product"""
        soup = self.get_page(url)
        if not soup:
            self.log_scrape_result(product_id, 'error', 'Failed to fetch page')
            return None
        
        try:
            price = self.extract_price(soup)
            in_stock = self.extract_availability(soup)
            
            if price is None:
                self.log_scrape_result(product_id, 'not_found', 'Price not found')
                return None
            
            result = {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': float(price),
                'in_stock': in_stock,
                'url': url
            }
            
            # Save to database
            self.save_price(result)
            self.log_scrape_result(product_id, 'success')
            
            self.logger.info(f"Scraped {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping {product_id}: {e}")
            self.log_scrape_result(product_id, 'error', str(e))
            return None
    
    def save_price(self, price_data):
        """Save price data to JSON and optionally database"""
        import json
        from pathlib import Path
        from datetime import datetime
        
        # Save to JSON file
        prices_dir = Path(__file__).parent.parent / "data" / "prices"
        prices_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with today's date
        today = datetime.now().strftime("%Y-%m-%d")
        prices_file = prices_dir / f"prices_{today}.json"
        
        # Load existing data or create new
        if prices_file.exists():
            with open(prices_file, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Add new price data
        product_id = price_data['product_id']
        if product_id not in data:
            data[product_id] = []
        
        data[product_id].append({
            'retailer': price_data['retailer'],
            'price': price_data['price'],
            'in_stock': price_data['in_stock'],
            'scraped_at': datetime.now().isoformat(),
            'url': price_data['url']
        })
        
        # Save back to file
        with open(prices_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Saved price to JSON: {price_data['product_id']} @ {price_data['retailer']}")
        
        # Also try database if available
        if not HAS_MARIADB:
            return
            
        try:
            conn = mariadb.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO price_history (product_id, retailer, price, in_stock, url)
                VALUES (?, ?, ?, ?, ?)
            """, (
                price_data['product_id'],
                price_data['retailer'], 
                price_data['price'],
                price_data['in_stock'],
                price_data['url']
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except mariadb.Error as e:
            self.logger.error(f"Database error: {e}")
    
    def log_scrape_result(self, product_id, status, error_message=None):
        """Log scraping result to database or console for testing"""
        if not HAS_MARIADB:
            self.logger.info(f"TEST MODE: Scrape result - {product_id}: {status} {error_message or ''}")
            return
            
        try:
            conn = mariadb.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scrape_log (retailer, product_id, status, error_message)
                VALUES (?, ?, ?, ?)
            """, (self.retailer_name, product_id, status, error_message))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except mariadb.Error as e:
            self.logger.error(f"Failed to log scrape result: {e}")

def clean_price_string(price_str):
    """Clean price string and convert to float"""
    if not price_str:
        return None
    
    # Remove currency symbols, commas, spaces
    cleaned = price_str.replace('£', '').replace(',', '').replace(' ', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None