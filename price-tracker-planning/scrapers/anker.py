"""
Anker UK scraper
Direct manufacturer scraping
"""

import re
from scrapers.base import BaseScraper, clean_price_string

class AnkerScraper(BaseScraper):
    def __init__(self):
        super().__init__('anker_uk', 'https://www.anker.com/uk')
    
    def extract_price(self, soup):
        """Extract price from Anker UK product page"""
        # Anker specific selectors
        price_selectors = [
            '.price-current',
            '.product-price .price',
            '.money',
            '[data-price-amount]',
            '.price .amount'
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
            if price and 500 <= price <= 5000:  # Power station range
                self.logger.info(f"Pattern match price: £{price}")
                return price
        
        self.logger.warning("No price found")
        return None
    
    def extract_availability(self, soup):
        """Extract availability from Anker UK page"""
        # Check for out of stock indicators
        unavailable_selectors = [
            '.out-of-stock',
            '.sold-out',
            '.unavailable'
        ]
        
        for selector in unavailable_selectors:
            if soup.select_one(selector):
                self.logger.info("Product out of stock")
                return False
        
        # Check page text for availability  
        page_text = soup.get_text().lower()
        if any(phrase in page_text for phrase in ['out of stock', 'sold out', 'unavailable']):
            self.logger.info("Product out of stock (text)")
            return False
        
        # Look for purchase options
        purchase_elements = soup.select('.add-to-cart, .buy-now, button[data-add-to-cart]')
        if purchase_elements:
            for elem in purchase_elements:
                if not elem.get('disabled') and 'disabled' not in elem.get('class', []):
                    self.logger.info("Product in stock")
                    return True
        
        # Default to available
        self.logger.info("Availability unclear - defaulting to in stock")
        return True