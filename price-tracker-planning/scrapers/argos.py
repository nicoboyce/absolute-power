"""
Argos UK scraper for Jackery power stations

IMPLEMENTATION NOTES:
- Argos has strong anti-scraping measures (403 errors common)
- May require headless browser approach
- Uses dynamic content loading for pricing
- Strong rate limiting and bot detection

STRATEGY:
1. Use realistic headers and user agents
2. Implement delays and retry logic  
3. Handle 403 errors gracefully
4. Fallback to search-based price discovery if needed

PRODUCTS CONFIRMED ON ARGOS:
- Jackery Explorer series power stations
- Same-day delivery available (£3.95)
- Competitive pricing vs other retailers

LAST UPDATED: 2025-09-07
"""

import time
import random
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, clean_price_string

class ArgosScraper(BaseScraper):
    """
    Argos UK scraper with enhanced anti-detection measures
    
    Argos has implemented strong bot detection, so this scraper:
    - Uses realistic browser headers
    - Implements longer delays between requests
    - Handles 403 errors with exponential backoff
    - May require headless browser fallback
    """
    
    def __init__(self):
        super().__init__('argos', 'https://www.argos.co.uk')
        
        # Enhanced headers to appear more like real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def get_page(self, url, max_retries=3):
        """
        Enhanced page fetching with anti-bot detection handling
        
        Argos-specific improvements:
        - Longer delays (3-6 seconds)
        - Exponential backoff on 403 errors
        - Session persistence
        - Realistic browsing patterns
        """
        for attempt in range(max_retries):
            try:
                # Longer delay for Argos (they're strict about rate limiting)
                delay = random.uniform(3, 6) + (attempt * 2)  # Exponential backoff
                time.sleep(delay)
                
                self.logger.info(f"Fetching Argos page (attempt {attempt + 1}/{max_retries}): {url}")
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 403:
                    self.logger.warning(f"403 Forbidden from Argos (attempt {attempt + 1}). Retrying with longer delay...")
                    continue
                    
                response.raise_for_status()
                
                self.logger.info(f"Successfully fetched Argos page: {url}")
                return BeautifulSoup(response.content, 'html.parser')
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"All attempts failed for Argos URL: {url}")
                    return None
                    
        return None
    
    def extract_price(self, soup):
        """
        Extract price from Argos product page
        
        Argos price selectors (common patterns):
        - .Price__Container price spans
        - .price-current, .price-display classes
        - data-test-id attributes for price elements
        - JSON-LD structured data
        
        NOTE: Argos may load prices via JavaScript, requiring headless browser
        """
        price_selectors = [
            # Primary price selectors
            '[data-test-id="price-current"]',
            '.price-current',
            '.Price__Container .price',
            '.pdp-price .price',
            
            # Alternative selectors
            '.price-display',
            '.product-price',
            '[data-price]',
            
            # Fallback selectors
            '.price',
            '[class*="price"]',
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                price = clean_price_string(price_text)
                
                if price and 50 <= price <= 5000:  # Reasonable range for power stations
                    self.logger.info(f"Found Argos price with selector '{selector}': £{price}")
                    return price
        
        # Try JSON-LD structured data (common on e-commerce sites)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                
                # Handle both single product and array of products
                products = data if isinstance(data, list) else [data]
                
                for product in products:
                    if product.get('@type') in ['Product', 'ProductOffer']:
                        offers = product.get('offers', {})
                        if offers.get('price'):
                            price = float(offers['price'])
                            if 50 <= price <= 5000:
                                self.logger.info(f"Found Argos price in JSON-LD: £{price}")
                                return price
                                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                continue
        
        self.logger.warning("No price found on Argos page")
        return None
    
    def extract_availability(self, soup):
        """
        Extract availability from Argos product page
        
        Argos availability patterns:
        - "Add to basket" button presence
        - Stock status text ("In stock", "Limited stock", "Out of stock")
        - Delivery availability ("Same day delivery available")
        - Store stock indicators
        """
        
        # Check for add to basket button (strongest stock indicator)
        add_to_basket_selectors = [
            '[data-test-id="add-to-basket"]',
            'button[class*="add-to-basket"]',
            'button[class*="add-to-trolley"]',
            '.add-to-basket',
            '.basket-add',
        ]
        
        for selector in add_to_basket_selectors:
            button = soup.select_one(selector)
            if button and not button.get('disabled'):
                self.logger.info("Found active 'Add to basket' button - product in stock")
                return True
        
        # Check stock status text
        stock_indicators = [
            '[data-test-id="stock-status"]',
            '.stock-status',
            '.availability',
            '.pdp-availability',
        ]
        
        for selector in stock_indicators:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                if any(phrase in text for phrase in ['in stock', 'available', 'limited stock']):
                    self.logger.info(f"Found positive stock indicator: {text}")
                    return True
                if any(phrase in text for phrase in ['out of stock', 'unavailable', 'sold out']):
                    self.logger.info(f"Found negative stock indicator: {text}")
                    return False
        
        # Check for delivery options (Argos-specific)
        delivery_selectors = [
            '.delivery-options',
            '[data-test-id="delivery"]',
            '.same-day-delivery',
        ]
        
        for selector in delivery_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                if 'same day' in text or 'delivery available' in text:
                    self.logger.info("Found delivery options - product likely in stock")
                    return True
        
        # Default to True if we can't determine (most products with prices are available)
        self.logger.info("Could not determine stock status - defaulting to available")
        return True
    
    def scrape_product(self, product_id, url):
        """
        Enhanced scrape with Argos-specific error handling
        
        Handles common Argos issues:
        - 403 Forbidden responses
        - JavaScript-rendered content
        - Rate limiting
        """
        self.logger.info(f"Starting Argos scrape for {product_id}: {url}")
        
        soup = self.get_page(url)
        if not soup:
            # If standard scraping fails, log the attempt for potential headless retry
            self.logger.error(f"Argos scraping failed for {product_id} - may need headless browser")
            return None
        
        try:
            price = self.extract_price(soup)
            in_stock = self.extract_availability(soup)
            
            if price is None:
                self.logger.warning(f"No price found for {product_id} on Argos")
                return None
            
            result = {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': float(price),
                'in_stock': in_stock,
                'url': url
            }
            
            # Save to database/JSON
            self.save_price(result)
            
            self.logger.info(f"Successfully scraped Argos {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping Argos {product_id}: {e}")
            return None

# Test function for development
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '..')
    from logging_config import setup_logging
    
    setup_logging()
    scraper = ArgosScraper()
    
    # Test with a known Argos Jackery product
    test_url = "https://www.argos.co.uk/product/1874143/jackery-explorer-1000-plus-portable-power-station"
    result = scraper.scrape_product("jackery-explorer-1000-plus", test_url)
    
    if result:
        print(f"SUCCESS: {result}")
    else:
        print("FAILED: Could not scrape product")