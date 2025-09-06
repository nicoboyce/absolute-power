"""
Jackery UK scraper
Direct manufacturer scraping  
"""

import re
from scrapers.base import BaseScraper, clean_price_string

class JackeryScraper(BaseScraper):
    def __init__(self):
        super().__init__('jackery_uk', 'https://uk.jackery.com')
    
    def extract_price(self, soup):
        """Extract price from Jackery UK product page"""
        # Jackery specific selectors
        price_selectors = [
            '.price .money',
            '.product-price',
            '.current-price',
            '[data-price]',
            '.price-item'
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
        
        # Fallback pattern search
        price_pattern = re.compile(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)')
        price_matches = price_pattern.findall(str(soup))
        
        for match in price_matches:
            price = clean_price_string(match.replace(',', ''))
            if price and 500 <= price <= 5000:  # Power station price range
                self.logger.info(f"Pattern match price: £{price}")
                return price
        
        self.logger.warning("No price found")
        return None
    
    def extract_availability(self, soup):
        """Extract availability from Jackery UK page"""
        # Out of stock patterns
        out_of_stock_text = [
            'out of stock',
            'sold out', 
            'unavailable',
            'notify when available'
        ]
        
        page_text = soup.get_text().lower()
        for text in out_of_stock_text:
            if text in page_text:
                self.logger.info("Product out of stock")
                return False
        
        # Look for add to cart button
        add_to_cart = soup.select_one('button[name="add"], .add-to-cart, .buy-now')
        if add_to_cart and not add_to_cart.get('disabled'):
            self.logger.info("Product in stock")  
            return True
        
        # Default assumption
        self.logger.info("Availability unclear - defaulting to in stock")
        return True