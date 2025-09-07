#!/usr/bin/env python3

"""
Bluetti UK scraper for power stations

Scrapes bluettipower.co.uk for Bluetti portable power station pricing and availability.
Bluetti operates on Shopify platform with standard e-commerce patterns.

MAINTENANCE NOTES:
- Bluetti uses standard Shopify pricing structure
- Product bundles may show different availability than base products
- Watch for variant-specific out-of-stock messages (e.g. solar panel combos)
- Site has good structured data - prioritise CSS selectors over text search

KNOWN ISSUES:
- Some product variants (bundles with accessories) may be out of stock
  while base product remains available - prioritise add-to-cart button detection

LAST UPDATED: 2025-09-07
TEST PRODUCTS: 
- EB3A: https://bluettipower.co.uk/products/bluetti-eb3a-portable-power-station
- Elite 200 v2: https://bluettipower.co.uk/products/elite-200-v2-portable-power-station
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

class BluettiUKScraper(BaseScraper):
    """
    Scraper for Bluetti UK power station products
    
    Handles Shopify-based e-commerce structure with:
    - Standard Shopify price selectors
    - Add-to-cart button detection for availability
    - Comprehensive error handling for network issues
    - Respectful rate limiting (1 second delays)
    
    Target Site: bluettipower.co.uk (Shopify platform)
    """
    
    def __init__(self):
        super().__init__('bluetti_uk', 'https://bluettipower.co.uk')
        # Add specific headers for Bluetti
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
        })
    
    def extract_price(self, soup):
        """
        Extract price from Bluetti UK product page
        
        Shopify typically structures prices in:
        - .price or .product-price elements
        - .price-item--regular for sale prices
        - .money for currency formatting
        
        Validates price range (£10-£20000) suitable for power station market.
        
        Args:
            soup (BeautifulSoup): Parsed product page HTML
            
        Returns:
            float|None: Product price in GBP or None if not found
        """
        price_selectors = [
            # Main price selectors
            '.price',
            '.product-price',
            '[class*="price"]',
            '.money',
            '.amount',
            
            # Shopify common selectors
            '.price__current .price-item--regular',
            '.price-item--regular',
            '.price__regular .price-item',
            '.price-list .price-item',
            
            # Specific to Bluetti structure
            '.product-form__price',
            '.price-wrapper .price',
            '.variant-price',
            
            # Backup text-based search
            '[data-price]',
        ]
        
        for selector in price_selectors:
            try:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    
                    # Extract price from text
                    price_match = re.search(r'£\s?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        price = float(price_str)
                        if 10 <= price <= 20000:  # Reasonable range for power stations
                            self.logger.info(f"Extracted price from {selector}: £{price}")
                            return price
                        
            except (ValueError, AttributeError) as e:
                self.logger.debug(f"Failed to extract price from {selector}: {e}")
                continue
        
        # Fallback: search for price patterns in page text
        price_patterns = [
            r'£\s?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:Price|Cost|RRP)[\s:]+£\s?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        page_text = soup.get_text()
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                try:
                    price = float(match.replace(',', ''))
                    if 10 <= price <= 20000:
                        self.logger.info(f"Pattern match price: £{price}")
                        return price
                except ValueError:
                    continue
        
        return None
    
    def extract_availability(self, soup):
        """
        Check if product is available on Bluetti UK
        
        CRITICAL: Bluetti pages may contain "out of stock" text in promotional content
        or other products that should NOT affect the current product's availability.
        Must prioritize actual product elements over general page text.
        
        Args:
            soup (BeautifulSoup): Parsed HTML of the product page
            
        Returns:
            bool: True if in stock, False if out of stock
            
        Priority order:
        1. Add to cart button (highest priority - indicates in stock)
        2. Specific out-of-stock indicators on the product
        3. General availability text (lowest priority)
        """
        # HIGHEST PRIORITY: Check for add to cart button (definitive in-stock indicator)
        add_to_cart_selectors = [
            'button[data-testid="add-to-cart"]',
            '.add-to-cart-button',
            'input[type="submit"][value*="cart"]',
            'button[name="add"]',
            '.btn-addToCart',
            '.product-form__cart button',
            '.shopify-payment-button',
            'form[action*="cart/add"] button[type="submit"]'
        ]
        
        for selector in add_to_cart_selectors:
            button = soup.select_one(selector)
            if button and not button.get('disabled'):
                self.logger.info(f"Found active add-to-cart button ({selector}) - product is in stock")
                return True
        
        # MEDIUM PRIORITY: Check for explicit out-of-stock indicators in product area
        product_area_selectors = [
            '.product-form',
            '.product-info', 
            '.product-details',
            '.product-options',
            '.inventory'
        ]
        
        for area_selector in product_area_selectors:
            product_area = soup.select_one(area_selector)
            if product_area:
                area_text = product_area.get_text().lower()
                out_of_stock_phrases = [
                    'out of stock',
                    'sold out',
                    'unavailable',
                    'notify when available',
                    'temporarily unavailable'
                ]
                
                for phrase in out_of_stock_phrases:
                    if phrase in area_text:
                        self.logger.info(f"Out of stock indicator '{phrase}' found in {area_selector}")
                        return False
        
        # LOW PRIORITY: Check entire page text (high risk of false positives)
        page_text = soup.get_text().lower()
        
        # But first, check for strong in-stock indicators
        strong_in_stock = [
            'add to cart',
            'add to basket', 
            'buy now',
            'purchase now',
            'order now'
        ]
        
        for indicator in strong_in_stock:
            if indicator in page_text:
                self.logger.info(f"Strong in-stock indicator found: '{indicator}'")
                return True
        
        # Check for product-specific out of stock (be more specific to avoid false positives)
        specific_out_of_stock = [
            'this product is out of stock',
            'this item is currently out of stock',
            'product unavailable'
        ]
        
        for indicator in specific_out_of_stock:
            if indicator in page_text:
                self.logger.info(f"Specific out-of-stock indicator: '{indicator}'")
                return False
        
        # DEFAULT: If we found pricing but no clear availability indicators, assume in stock
        # (Most e-commerce sites don't show prices for out-of-stock items)
        self.logger.info("No definitive availability indicators found - assuming in stock")
        return True
    
    def scrape_product(self, product_id, url):
        """Scrape a single product from Bluetti UK"""
        try:
            # Add delay to be respectful
            time.sleep(1)
            
            self.logger.info(f"Scraping {product_id} from {url}")
            
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract price
            price = self.extract_price(soup)
            if price is None:
                self.logger.warning("No price found")
                return self.create_result(product_id, None, None, "Price not found")
            
            # Check availability
            in_stock = self.extract_availability(soup)
            
            # Log result
            stock_status = "in stock" if in_stock else "out of stock"
            self.logger.info(f"Scraped {product_id}: £{price} ({stock_status})")
            
            return self.create_result(product_id, price, in_stock, "success", url)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {product_id}: {e}")
            return self.create_result(product_id, None, None, f"Request failed: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {product_id}: {e}")
            return self.create_result(product_id, None, None, f"Scraping error: {e}")

def main():
    """Test the Bluetti UK scraper"""
    scraper = BluettiUKScraper()
    
    # Test with a known Bluetti URL
    test_url = "https://bluettipower.co.uk/products/elite-30-v2-portable-power-station"
    result = scraper.scrape_product("test-product", test_url)
    
    print(f"Test result: {result}")

if __name__ == "__main__":
    main()