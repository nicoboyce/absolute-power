"""
Goal Zero UK scraper for outdoor-focused power stations

BRAND POSITIONING:
Goal Zero focuses on outdoor, camping, and emergency preparedness markets.
Their products are often premium-priced but built for rugged outdoor use.

UK AVAILABILITY:
- Limited direct UK presence compared to other brands
- Primary sales through outdoor/camping specialty retailers
- Premium pricing reflects outdoor/emergency positioning
- Strong brand in van life and camping communities

SCRAPING CONSIDERATIONS:
- Clean, simple website structure (outdoor brand aesthetic)
- Standard e-commerce patterns (Shopify-based)
- Price information usually clearly displayed
- Stock levels may be limited due to specialist nature
- UK site may have different pricing than US

IMPLEMENTATION STRATEGY:
1. Focus on direct Goal Zero UK site first
2. Handle Shopify-based structure
3. Extract clear pricing and availability
4. Validate against outdoor/camping price ranges
5. Handle potential stock limitations gracefully

LAST UPDATED: 2025-09-07
"""

import re
import logging
from bs4 import BeautifulSoup
from base import BaseScraper, clean_price_string

class GoalZeroUKScraper(BaseScraper):
    """
    Goal Zero UK scraper for outdoor power station market
    
    Goal Zero specializes in outdoor and emergency power solutions,
    with premium pricing and rugged design focus.
    """
    
    def __init__(self):
        super().__init__('goalzero_uk', 'https://www.goalzero.co.uk')
        
        # Goal Zero UK specific headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_price(self, soup):
        """
        Extract price from Goal Zero UK product page
        
        Goal Zero typically uses clean Shopify-based pricing:
        - Main product price clearly displayed
        - May have multiple variants with different pricing
        - Currency clearly marked as £ for UK site
        - Bundle pricing for power station + solar panel combinations
        """
        
        # Goal Zero UK price selectors (Shopify-based)
        price_selectors = [
            # Shopify standard selectors
            '.price .price-item--regular',
            '.price-item--sale',
            '.product-single__prices .money',
            '.product__price .money',
            
            # Goal Zero specific selectors
            '.product-form__price .money',
            '.price-current',
            '.current-price',
            
            # Generic e-commerce selectors
            '.product-price',
            '.price',
            '[data-price]',
            
            # Variant pricing
            '.variant-price',
            '.selected-variant-price'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                
                # Skip variant labels and shipping info
                if any(word in price_text.lower() for word in ['from', 'starting', 'shipping', 'tax']):
                    continue
                
                price = clean_price_string(price_text)
                
                # Goal Zero price range validation (outdoor premium brand)
                if price and 150 <= price <= 4000:
                    self.logger.info(f"Found Goal Zero UK price with selector '{selector}': £{price}")
                    return price
        
        # Try structured data (Shopify often includes this)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                try:
                    import json
                    data = json.loads(script.string)
                    
                    # Handle arrays and single objects
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product':
                                data = item
                                break
                    
                    if data.get('@type') == 'Product':
                        offers = data.get('offers', {})
                        if isinstance(offers, list):
                            offers = offers[0]  # Take first offer
                        
                        if offers.get('price'):
                            price = float(offers['price'])
                            if 150 <= price <= 4000:
                                self.logger.info(f"Found Goal Zero UK price in JSON-LD: £{price}")
                                return price
                
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        
        # Try Shopify product JSON (common pattern)
        product_json_scripts = soup.find_all('script', string=re.compile(r'product.*price'))
        for script in product_json_scripts:
            if script.string:
                try:
                    # Extract price from product JSON
                    price_matches = re.findall(r'"price"[:\s]*(\d+)', script.string)
                    for match in price_matches:
                        price = float(match) / 100  # Shopify stores prices in cents
                        if 150 <= price <= 4000:
                            self.logger.info(f"Found Goal Zero UK price in product JSON: £{price}")
                            return price
                except (ValueError, TypeError):
                    continue
        
        self.logger.warning("No price found on Goal Zero UK page")
        return None
    
    def extract_availability(self, soup):
        """
        Extract availability from Goal Zero UK product page
        
        Goal Zero availability patterns:
        - "Add to Cart" button for available products
        - "Sold Out" or "Out of Stock" messages
        - Inventory level indicators
        - Pre-order status for new products
        """
        
        # Check for Add to Cart button (primary availability indicator)
        add_to_cart_selectors = [
            # Shopify standard selectors
            'form[action*="add"] button[type="submit"]',
            '.btn-product-add',
            '.product-form__cart-submit',
            
            # Goal Zero specific
            '.add-to-cart',
            '.product-add',
            '[name="add"]',
            
            # Generic selectors
            'button[class*="add"]',
            'input[value*="Add"]'
        ]
        
        for selector in add_to_cart_selectors:
            button = soup.select_one(selector)
            if button and not button.get('disabled'):
                button_text = button.get_text().lower()
                
                # Check button text indicates availability
                if any(phrase in button_text for phrase in ['add to cart', 'add to bag', 'buy now']):
                    if 'out of stock' not in button_text and 'sold out' not in button_text:
                        self.logger.info(f"Found active add to cart button - product available")
                        return True
        
        # Check for explicit stock status messages
        stock_selectors = [
            '.stock-status',
            '.product-availability',
            '.inventory-status',
            '[data-stock]'
        ]
        
        for selector in stock_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                
                # Positive stock indicators
                if any(phrase in text for phrase in ['in stock', 'available', 'ready to ship']):
                    self.logger.info(f"Found positive stock indicator: {text}")
                    return True
                
                # Negative stock indicators
                if any(phrase in text for phrase in ['out of stock', 'sold out', 'unavailable']):
                    self.logger.info(f"Found negative stock indicator: {text}")
                    return False
        
        # Check for sold out classes or disabled states
        if soup.select_one('.sold-out') or soup.select_one('.out-of-stock'):
            self.logger.info("Found sold out class indicator")
            return False
        
        # Check page text for stock indicators
        page_text = soup.get_text().lower()
        
        # Strong negative indicators
        if any(phrase in page_text for phrase in ['currently out of stock', 'temporarily unavailable', 'sold out']):
            self.logger.info("Found stock out indicator in page text")
            return False
        
        # Check for pre-order status
        if 'pre-order' in page_text or 'coming soon' in page_text:
            self.logger.info("Product appears to be pre-order/coming soon")
            return False
        
        # Default to available if we have pricing (Goal Zero typically only shows prices for available items)
        self.logger.info("Could not determine Goal Zero stock status - defaulting to available")
        return True
    
    def scrape_product(self, product_id, url):
        """
        Goal Zero specific scraping with outdoor brand considerations
        
        Goal Zero has clean, straightforward product pages.
        Main challenges are limited UK availability and premium pricing.
        """
        self.logger.info(f"Starting Goal Zero UK scrape for {product_id}: {url}")
        
        soup = self.get_page(url)
        if not soup:
            self.logger.error(f"Goal Zero UK scraping failed for {product_id} - couldn't fetch page")
            return None
        
        try:
            price = self.extract_price(soup)
            in_stock = self.extract_availability(soup)
            
            if price is None:
                self.logger.warning(f"No price found for {product_id} on Goal Zero UK")
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
            
            self.logger.info(f"Successfully scraped Goal Zero UK {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping Goal Zero UK {product_id}: {e}")
            return None

# Test function for development
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '..')
    from logging_config import setup_logging
    
    setup_logging()
    scraper = GoalZeroUKScraper()
    
    # Test with a Goal Zero UK product
    test_url = "https://www.goalzero.co.uk/products/yeti-500x-portable-power-station"
    result = scraper.scrape_product("goalzero-yeti-500x", test_url)
    
    if result:
        print(f"SUCCESS: {result}")
    else:
        print("FAILED: Could not scrape Goal Zero UK product")