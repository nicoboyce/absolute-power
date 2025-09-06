"""
EcoFlow UK scraper
Direct manufacturer scraping
"""

import re
from scrapers.base import BaseScraper, clean_price_string

class EcoFlowScraper(BaseScraper):
    def __init__(self):
        super().__init__('ecoflow_uk', 'https://uk.ecoflow.com')
    
    def extract_price(self, soup):
        """Extract price from EcoFlow UK product page"""
        # EcoFlow specific selectors - update after testing
        price_selectors = [
            '.price__current',
            '.product-price .price',
            '[data-testid="price"]',
            '.price-box .price',
            '.money'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                self.logger.debug(f"Found price element: {price_text}")
                
                # Extract numeric price
                price_match = re.search(r'£?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = clean_price_string(price_str)
                    if price:
                        self.logger.info(f"Extracted price: £{price}")
                        return price
        
        # Fallback: search entire page for price patterns
        price_pattern = re.compile(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)')
        price_matches = price_pattern.findall(str(soup))
        
        for match in price_matches:
            price = clean_price_string(match.replace(',', ''))
            if price and 500 <= price <= 5000:  # Reasonable range for power stations
                self.logger.info(f"Pattern match price: £{price}")
                return price
        
        self.logger.warning("No price found")
        return None
    
    def extract_availability(self, soup):
        """Extract availability from EcoFlow UK page"""
        # Check for out of stock indicators
        out_of_stock_selectors = [
            '.sold-out',
            '.out-of-stock',
            '.unavailable'
        ]
        
        for selector in out_of_stock_selectors:
            if soup.select_one(selector):
                self.logger.info("Product out of stock")
                return False
        
        # Check for in stock indicators
        in_stock_selectors = [
            '.add-to-cart',
            '.buy-now',
            '.in-stock',
            'button[data-testid="add-to-cart"]'
        ]
        
        for selector in in_stock_selectors:
            element = soup.select_one(selector)
            if element and not element.get('disabled'):
                self.logger.info("Product in stock")
                return True
        
        # Default to in stock if unclear
        self.logger.info("Availability unclear - defaulting to in stock")
        return True