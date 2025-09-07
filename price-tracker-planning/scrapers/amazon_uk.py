#!/usr/bin/env python3

"""
Amazon UK scraper for power stations
Handles dynamic pricing on Amazon UK product pages
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

class AmazonUKScraper(BaseScraper):
    """Scraper for Amazon UK power station products"""
    
    def __init__(self):
        super().__init__('amazon_uk', 'https://www.amazon.co.uk')
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_price(self, soup):
        """Extract price from Amazon UK product page"""
        price_selectors = [
            # Main price
            '.a-price-whole',
            '.a-offscreen',  # Often contains the actual price
            '.a-price .a-offscreen',
            '[data-testid="price"] .a-price .a-offscreen',
            
            # Deal prices
            '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '.a-price-symbol + .a-price-whole',
            
            # Alternative selectors
            '#priceblock_dealprice',
            '#corePrice_feature_div .a-price .a-offscreen',
            '.a-price-range .a-price .a-offscreen',
            
            # Backup selectors
            '[class*="price"] [class*="whole"]',
            '.pricing-summary .a-price .a-offscreen'
        ]
        
        for selector in price_selectors:
            try:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    
                    # Clean up price text
                    # Remove currency symbols and clean
                    price_text = re.sub(r'[£$€¥₹]', '', price_text)
                    price_text = re.sub(r'[,\s]', '', price_text)
                    
                    # Extract price using regex
                    price_match = re.search(r'(\d+\.?\d*)', price_text)
                    if price_match:
                        price = float(price_match.group(1))
                        if 10 <= price <= 50000:  # Reasonable price range for power stations
                            self.logger.info(f"Extracted price from {selector}: £{price}")
                            return price
                        
            except (ValueError, AttributeError) as e:
                self.logger.debug(f"Failed to extract price from {selector}: {e}")
                continue
        
        # Try alternative method: look for any price-like patterns in the page
        price_pattern = r'£\s?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        price_matches = re.findall(price_pattern, soup.get_text())
        
        for match in price_matches:
            try:
                price = float(match.replace(',', ''))
                if 10 <= price <= 50000:
                    self.logger.info(f"Pattern match price: £{price}")
                    return price
            except ValueError:
                continue
        
        return None
    
    def check_availability(self, soup):
        """Check if product is available on Amazon UK"""
        # Amazon availability indicators
        availability_indicators = {
            'in_stock': [
                'in stock',
                'available',
                'add to basket',
                'add to cart',
                'buy now',
                'choose options'
            ],
            'out_of_stock': [
                'out of stock',
                'unavailable',
                'currently unavailable',
                'temporarily out of stock',
                'see all buying options'
            ]
        }
        
        page_text = soup.get_text().lower()
        
        # Check for out of stock indicators first
        for indicator in availability_indicators['out_of_stock']:
            if indicator in page_text:
                self.logger.info(f"Out of stock indicator found: {indicator}")
                return False
        
        # Check for in stock indicators
        for indicator in availability_indicators['in_stock']:
            if indicator in page_text:
                self.logger.info(f"In stock indicator found: {indicator}")
                return True
        
        # Check specific Amazon elements
        availability_selectors = [
            '#availability span',
            '#availability .a-declarative',
            '[data-feature-name="availability"] span',
            '.a-button-text',  # Add to Cart/Buy Now buttons
        ]
        
        for selector in availability_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text().lower().strip()
                if any(indicator in text for indicator in availability_indicators['in_stock']):
                    return True
                elif any(indicator in text for indicator in availability_indicators['out_of_stock']):
                    return False
        
        # Default to in stock if we can't determine (Amazon usually shows availability clearly)
        self.logger.info("Availability unclear - defaulting to in stock")
        return True
    
    def scrape_product(self, product_id, url):
        """Scrape a single product from Amazon UK"""
        try:
            # Add small delay to be respectful
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
            
            # Log successful extraction
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
    """Test the Amazon UK scraper"""
    scraper = AmazonUKScraper()
    
    # Test with a known power station URL
    test_url = "https://www.amazon.co.uk/dp/B0B8Y8N5C6"  # EcoFlow DELTA 2
    result = scraper.scrape_product("test-product", test_url)
    
    print(f"Test result: {result}")

if __name__ == "__main__":
    main()