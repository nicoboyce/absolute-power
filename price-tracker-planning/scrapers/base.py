"""
Base scraper class for all retailer scrapers

This module provides the foundation for all price scraping operations.
Any developer maintaining or extending scrapers should read this carefully.

ARCHITECTURE OVERVIEW:
- All scrapers inherit from BaseScraper
- Each scraper implements extract_price() and extract_availability()  
- Results are standardised through create_result()
- Price data is saved to JSON files (date-based)
- Comprehensive logging for debugging and monitoring

MAINTENANCE GUIDELINES:
- Always test scrapers on multiple products before deployment
- Be aware of anti-scraping measures (rate limiting, bot detection)
- Use respectful delays between requests (1-2 seconds minimum)
- Handle errors gracefully and log detailed information
- Validate price ranges to avoid false positives from promotional content

ADDING NEW SCRAPERS:
1. Inherit from BaseScraper
2. Implement extract_price(soup) method
3. Implement extract_availability(soup) method
4. Add appropriate headers for the target site
5. Test thoroughly with representative products
6. Add to scrape_all.py

COMMON ISSUES:
- Promotional banners can contain misleading prices
- Out-of-stock text may appear for product bundles, not base products
- Dynamic pricing may require JavaScript rendering
- Rate limiting can cause 403/429 errors

LAST UPDATED: 2025-09-07
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
    """
    Base class for all retailer scrapers
    
    Provides common functionality for:
    - HTTP session management with appropriate headers
    - Rate limiting and respectful crawling
    - Standardised result formatting
    - JSON and database persistence
    - Comprehensive error handling and logging
    
    SUBCLASS REQUIREMENTS:
    - Must implement extract_price(soup) -> float|None
    - Must implement extract_availability(soup) -> bool
    - Should set appropriate headers for target site
    """
    
    def __init__(self, retailer_name, base_url):
        """
        Initialize scraper with retailer-specific settings
        
        Args:
            retailer_name (str): Unique identifier for this retailer (e.g. 'jackery_uk')
            base_url (str): Base URL for the retailer's website
        """
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
        """
        Fetch a web page with comprehensive error handling and rate limiting
        
        Features:
        - Automatic rate limiting (REQUEST_DELAY + random jitter)
        - Proper timeout handling
        - HTTP status code validation
        - BeautifulSoup parsing with HTML5 parser
        
        Args:
            url (str): Full URL to fetch
            
        Returns:
            BeautifulSoup|None: Parsed HTML soup or None if failed
        """
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
        """
        Extract product price from parsed HTML
        
        CRITICAL IMPLEMENTATION NOTES:
        - Must handle promotional prices and banners (common source of false positives)
        - Should validate price ranges appropriate for power stations (£100-£5000)
        - Must return None if no valid price found (do not guess or return 0)
        - Should prioritise product-specific selectors over generic ones
        - Must handle comma separators in prices (e.g. "1,299.00")
        
        Args:
            soup (BeautifulSoup): Parsed HTML of product page
            
        Returns:
            float|None: Price in GBP or None if not found
            
        Example Implementation:
        ```python
        def extract_price(self, soup):
            price_elem = soup.select_one('.product-price')
            if price_elem:
                price_text = price_elem.get_text()
                return clean_price_string(price_text)
            return None
        ```
        """
        raise NotImplementedError("Subclasses must implement extract_price")
    
    def extract_availability(self, soup):
        """
        Extract product availability from parsed HTML
        
        CRITICAL IMPLEMENTATION NOTES:
        - Prioritise "Add to cart" buttons as strongest in-stock signal
        - Be wary of out-of-stock text in product bundles or promotions
        - Check for disabled buttons or form elements
        - Default to True (in stock) when unclear - most sites show prices only for available items
        - Watch for variant-specific availability (like Bluetti's panel combinations)
        
        Args:
            soup (BeautifulSoup): Parsed HTML of product page
            
        Returns:
            bool: True if in stock, False if out of stock
            
        Example Implementation:
        ```python
        def extract_availability(self, soup):
            # Check for add to cart button
            if soup.select_one('button[name="add"]'):
                return True
            # Check for out of stock text
            if 'out of stock' in soup.get_text().lower():
                return False
            return True  # Default to available
        ```
        """
        raise NotImplementedError("Subclasses must implement extract_availability")
    
    def scrape_product(self, product_id, url):
        """
        Scrape a single product's price and availability
        
        This is the main entry point for scraping operations. It handles:
        - Page fetching with error handling
        - Price and availability extraction
        - Result validation and formatting
        - Data persistence (JSON + optional database)
        - Comprehensive logging
        
        Args:
            product_id (str): Unique product identifier from JSON files
            url (str): Full URL to the product page
            
        Returns:
            dict|None: Scraping result with price, availability, and metadata
                      Returns None if scraping failed
                      
        Result Format:
        ```python
        {
            'product_id': 'jackery-explorer-1000',
            'retailer': 'jackery_uk',
            'price': 799.0,
            'in_stock': True,
            'url': 'https://uk.jackery.com/products/...'
        }
        ```
        """
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
    
    def create_result(self, product_id, price, in_stock, status, url=None):
        """Create a standardized scraping result dictionary"""
        if price is not None and in_stock is not None and status == "success":
            # Save successful price data
            price_data = {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': price,
                'in_stock': in_stock,
                'url': url
            }
            self.save_price(price_data)
            self.log_scrape_result(product_id, "success")
            
            return {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': price,
                'in_stock': in_stock,
                'status': 'success',
                'url': url
            }
        else:
            # Log failed scrape
            self.log_scrape_result(product_id, "failed", status)
            return {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': None,
                'in_stock': None,
                'status': 'failed',
                'error': status,
                'url': url
            }
    
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
    """
    Clean and parse price string to float
    
    Handles common price formatting:
    - Currency symbols (£, $, etc.)
    - Thousands separators (commas)
    - Whitespace and other formatting
    - Invalid/empty strings
    
    Args:
        price_str (str): Raw price string (e.g. "£1,299.00", "999.99")
        
    Returns:
        float|None: Numeric price or None if invalid
        
    Examples:
        >>> clean_price_string("£1,299.00")
        1299.0
        >>> clean_price_string("invalid")
        None
    """
    if not price_str:
        return None
    
    # Remove currency symbols, commas, spaces
    cleaned = price_str.replace('£', '').replace(',', '').replace(' ', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None
    if not price_str:
        return None
    
    # Remove currency symbols, commas, spaces
    cleaned = price_str.replace('£', '').replace(',', '').replace(' ', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None