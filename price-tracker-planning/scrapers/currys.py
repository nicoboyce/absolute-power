"""
Currys scraper for power stations
"""

import re
from scrapers.base import BaseScraper, clean_price_string

class CurrysScraper(BaseScraper):
    def __init__(self):
        super().__init__('currys', 'https://www.currys.co.uk')
        
        # Add additional headers to avoid blocking
        self.session.headers.update({
            'Referer': 'https://www.currys.co.uk/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
    
    def extract_price(self, soup):
        """Extract price from Currys product page"""
        # Common selectors to try (update after manual inspection)
        price_selectors = [
            '.price',
            '.current-price',
            '[data-testid="price"]',
            '.price-current',
            '.pdp-price',
            '.product-price'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                self.logger.debug(f"Found price element with selector '{selector}': {price_text}")
                
                # Extract numeric price from text
                price_match = re.search(r'£?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = clean_price_string(price_str)
                    if price:
                        self.logger.info(f"Extracted price: £{price}")
                        return price
        
        # Fallback: look for any text containing £ and numbers
        price_pattern = re.compile(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)')
        price_matches = price_pattern.findall(str(soup))
        
        if price_matches:
            # Take the first reasonable price (avoid very small prices like delivery)
            for match in price_matches:
                price = clean_price_string(match.replace(',', ''))
                if price and price > 50:  # Reasonable minimum for power stations
                    self.logger.info(f"Extracted price from pattern match: £{price}")
                    return price
        
        self.logger.warning("Could not extract price from page")
        return None
    
    def extract_availability(self, soup):
        """Extract availability from Currys product page"""
        # Common availability indicators
        availability_selectors = [
            '.availability',
            '.stock-status',
            '[data-testid="availability"]',
            '.product-availability',
            '.stock-level'
        ]
        
        # Look for availability text
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True).lower()
                self.logger.debug(f"Found availability element with selector '{selector}': {text}")
                
                # Check for out of stock indicators
                out_of_stock_phrases = [
                    'out of stock',
                    'unavailable',
                    'not available',
                    'sold out',
                    'temporarily unavailable'
                ]
                
                for phrase in out_of_stock_phrases:
                    if phrase in text:
                        self.logger.info("Product out of stock")
                        return False
                
                # Check for in stock indicators
                in_stock_phrases = [
                    'in stock',
                    'available',
                    'add to basket',
                    'buy now'
                ]
                
                for phrase in in_stock_phrases:
                    if phrase in text:
                        self.logger.info("Product in stock")
                        return True
        
        # Check for add to basket button as availability indicator
        basket_button = soup.select_one('button[data-testid="add-to-basket"], .add-to-basket, .buy-button')
        if basket_button and not basket_button.get('disabled'):
            self.logger.info("Add to basket button found - product likely in stock")
            return True
        
        # Default to True if we can't determine availability
        self.logger.warning("Could not determine availability - defaulting to in stock")
        return True
    
    def get_product_name(self, soup):
        """Extract product name for verification"""
        name_selectors = [
            'h1',
            '.product-title',
            '.pdp-product-name',
            '[data-testid="product-title"]'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if name:
                    return name
        
        return "Unknown Product"

# Test function for manual verification
def test_currys_scraper():
    """Test the Currys scraper with a known URL"""
    scraper = CurrysScraper()
    
    # Test URL - replace with actual product URL
    test_url = "https://www.currys.co.uk/products/anker-solix-c800x-plus-768-wh-portable-power-station-10260796.html"
    
    print(f"Testing Currys scraper with URL: {test_url}")
    
    soup = scraper.get_page(test_url)
    if soup:
        price = scraper.extract_price(soup)
        availability = scraper.extract_availability(soup)
        name = scraper.get_product_name(soup)
        
        print(f"Product: {name}")
        print(f"Price: £{price}" if price else "Price: Not found")
        print(f"Available: {'Yes' if availability else 'No'}")
        
        # Show some page content for debugging
        print(f"\nPage title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for any price-like text
        import re
        price_pattern = re.compile(r'£\d+')
        price_matches = price_pattern.findall(soup.get_text())[:10]  # First 10 matches
        print(f"Price-like text found: {price_matches}")
    else:
        print("Failed to fetch page - check if site is blocking requests")

if __name__ == '__main__':
    test_scraper()