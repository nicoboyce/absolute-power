"""
Outdoor Supply UK scraper for Goal Zero and outdoor power products

RETAILER PROFILE:
- Specialist outdoor and camping equipment retailer
- Stocks Goal Zero power stations and solar panels
- Fast delivery and outdoor focus
- Competitive pricing for outdoor gear
- Clean, modern e-commerce site

TARGET PRODUCTS:
- Goal Zero Yeti series power stations
- Solar panels and accessories
- Outdoor/camping power solutions
- Emergency preparedness equipment

SCRAPING STRATEGY:
- Standard e-commerce structure
- Clear pricing and stock indicators
- Product pages with good metadata
- Respectful scraping with appropriate delays

LAST UPDATED: 2025-09-07
"""

import logging
from bs4 import BeautifulSoup
from base import BaseScraper, clean_price_string

class OutdoorSupplyScraper(BaseScraper):
    """
    Outdoor Supply UK scraper for Goal Zero and outdoor power products
    
    Specialist outdoor retailer with competitive pricing and good availability
    for Goal Zero products that may be hard to find elsewhere in the UK.
    """
    
    def __init__(self):
        super().__init__('outdoorsupply', 'https://www.outdoorsupply.co.uk')
        
        # Standard UK e-commerce headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
    
    def extract_price(self, soup):
        """
        Extract price from Outdoor Supply UK product page
        
        Standard UK e-commerce pricing patterns:
        - Clear £ pricing display
        - May have sale prices vs regular prices
        - VAT inclusive pricing
        - Bundle deals and promotions
        """
        
        price_selectors = [
            # Common e-commerce price selectors
            '.price .current',
            '.product-price .price',
            '.current-price',
            '.sale-price',
            '.special-price',
            
            # Product page specific
            '.product-info-main .price',
            '.price-box .price',
            '.regular-price',
            
            # Data attributes
            '[data-price]',
            '[data-price-amount]',
            
            # Generic fallbacks
            '.price',
            '.money',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                
                # Skip shipping, tax, and promotional text
                if any(word in price_text.lower() for word in ['shipping', 'tax', 'from', 'starting at']):
                    continue
                
                price = clean_price_string(price_text)
                
                # Outdoor equipment price range validation
                if price and 100 <= price <= 5000:
                    self.logger.info(f"Found Outdoor Supply price with selector '{selector}': £{price}")
                    return price
        
        # Check meta tags for price info
        price_meta = soup.find('meta', attrs={'property': 'product:price:amount'})
        if price_meta and price_meta.get('content'):
            try:
                price = float(price_meta['content'])
                if 100 <= price <= 5000:
                    self.logger.info(f"Found Outdoor Supply price in meta tags: £{price}")
                    return price
            except ValueError:
                pass
        
        # Try structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                try:
                    import json
                    data = json.loads(script.string)
                    
                    if isinstance(data, list):
                        data = data[0]
                    
                    if data.get('@type') == 'Product':
                        offers = data.get('offers', {})
                        if isinstance(offers, list):
                            offers = offers[0]
                        
                        if offers.get('price'):
                            price = float(offers['price'])
                            if 100 <= price <= 5000:
                                self.logger.info(f"Found Outdoor Supply price in JSON-LD: £{price}")
                                return price
                
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        
        self.logger.warning("No price found on Outdoor Supply page")
        return None
    
    def extract_availability(self, soup):
        """
        Extract availability from Outdoor Supply UK product page
        
        Standard e-commerce availability patterns:
        - Add to cart/basket buttons
        - Stock level indicators
        - Delivery availability
        - Out of stock messages
        """
        
        # Check for add to cart/basket buttons
        add_to_cart_selectors = [
            '.add-to-cart',
            '.add-to-basket',
            '.btn-cart',
            'button[type="submit"][name*="add"]',
            '.product-add-form button',
            '[data-role="add-to-cart"]'
        ]
        
        for selector in add_to_cart_selectors:
            button = soup.select_one(selector)
            if button and not button.get('disabled'):
                button_text = button.get_text().lower()
                
                if any(phrase in button_text for phrase in ['add to cart', 'add to basket', 'buy now']):
                    if 'out of stock' not in button_text:
                        self.logger.info("Found active add to cart button - product available")
                        return True
        
        # Check stock status indicators
        stock_selectors = [
            '.stock-status',
            '.availability',
            '.product-availability',
            '.stock-info',
            '[data-stock]'
        ]
        
        for selector in stock_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                
                # Positive indicators
                if any(phrase in text for phrase in ['in stock', 'available', 'ready to dispatch']):
                    self.logger.info(f"Found positive stock indicator: {text}")
                    return True
                
                # Negative indicators
                if any(phrase in text for phrase in ['out of stock', 'unavailable', 'sold out']):
                    self.logger.info(f"Found negative stock indicator: {text}")
                    return False
        
        # Check delivery information (often indicates stock)
        delivery_selectors = [
            '.delivery-info',
            '.shipping-info',
            '.dispatch-info'
        ]
        
        for selector in delivery_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                if any(phrase in text for phrase in ['fast delivery', 'next day', 'in stock']):
                    self.logger.info(f"Found delivery info suggesting availability: {text}")
                    return True
        
        # Check for sold out page indicators
        page_text = soup.get_text().lower()
        if any(phrase in page_text for phrase in ['currently out of stock', 'temporarily unavailable']):
            self.logger.info("Found out of stock indicator in page text")
            return False
        
        # Default to available (most outdoor retailers only show prices for available items)
        self.logger.info("Could not determine Outdoor Supply stock status - defaulting to available")
        return True
    
    def scrape_product(self, product_id, url):
        """
        Outdoor Supply specific scraping implementation
        """
        self.logger.info(f"Starting Outdoor Supply scrape for {product_id}: {url}")
        
        soup = self.get_page(url)
        if not soup:
            self.logger.error(f"Outdoor Supply scraping failed for {product_id} - couldn't fetch page")
            return None
        
        try:
            price = self.extract_price(soup)
            in_stock = self.extract_availability(soup)
            
            if price is None:
                self.logger.warning(f"No price found for {product_id} on Outdoor Supply")
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
            
            self.logger.info(f"Successfully scraped Outdoor Supply {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping Outdoor Supply {product_id}: {e}")
            return None

# Test function for development
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '..')
    from logging_config import setup_logging
    
    setup_logging()
    scraper = OutdoorSupplyScraper()
    
    # Test with a Goal Zero product from Outdoor Supply
    test_url = "https://www.outdoorsupply.co.uk/goal-zero-yeti-500x-portable-power-station"
    result = scraper.scrape_product("goalzero-yeti-500x", test_url)
    
    if result:
        print(f"SUCCESS: {result}")
    else:
        print("FAILED: Could not scrape Outdoor Supply product")