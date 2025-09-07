#!/usr/bin/env python3

"""
Bluetti UK scraper for power stations
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

class BluettiUKScraper(BaseScraper):
    """Scraper for Bluetti UK power station products"""
    
    def __init__(self):
        super().__init__('bluetti_uk', 'https://bluettipower.co.uk')
        # Add specific headers for Bluetti
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
        })
    
    def extract_price(self, soup):
        """Extract price from Bluetti UK product page"""
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
    
    def check_availability(self, soup):
        """Check if product is available on Bluetti UK"""
        availability_indicators = {
            'in_stock': [
                'add to cart',
                'add to basket',
                'buy now',
                'in stock',
                'available',
                'order now',
                'purchase'
            ],
            'out_of_stock': [
                'out of stock',
                'sold out',
                'unavailable',
                'pre-order',
                'notify when available',
                'back in stock'
            ]
        }
        
        page_text = soup.get_text().lower()
        
        # Check for out of stock first
        for indicator in availability_indicators['out_of_stock']:
            if indicator in page_text:
                self.logger.info(f"Out of stock indicator: {indicator}")
                return False
        
        # Check for in stock indicators
        for indicator in availability_indicators['in_stock']:
            if indicator in page_text:
                self.logger.info(f"In stock indicator: {indicator}")
                return True
        
        # Check button elements
        buttons = soup.find_all(['button', 'input', 'a'], class_=re.compile(r'add|cart|buy', re.I))
        for button in buttons:
            button_text = button.get_text().lower().strip()
            if any(indicator in button_text for indicator in availability_indicators['in_stock']):
                return True
            if any(indicator in button_text for indicator in availability_indicators['out_of_stock']):
                return False
        
        # Default to in stock if unclear
        self.logger.info("Availability unclear - defaulting to in stock")
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
            in_stock = self.check_availability(soup)
            
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