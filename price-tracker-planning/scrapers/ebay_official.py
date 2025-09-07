"""
eBay Official Store scraper for manufacturer-backed listings

FOCUS: Bluetti UK Official eBay store - manufacturer pricing with eBay convenience
Store URL: https://www.ebay.co.uk/str/bluettiukofficial

ADVANTAGES OF EBAY OFFICIAL STORES:
- Manufacturer-backed pricing and warranties
- Often competitive pricing to match direct sales
- eBay buyer protection on top of manufacturer warranty
- Sometimes exclusive eBay promotions and bundles
- Good availability tracking (eBay stock management)

SCRAPING CONSIDERATIONS:
- eBay has sophisticated anti-bot measures
- Product URLs can be complex with tracking parameters
- Pricing may include shipping costs in total
- eBay frequently updates page structure
- May require headless browser for JavaScript content

IMPLEMENTATION STRATEGY:
1. Focus on official manufacturer stores only
2. Handle eBay's dynamic pricing and bidding structure
3. Extract "Buy It Now" prices (not auction prices)
4. Careful shipping cost handling
5. Robust error handling for eBay's anti-scraping

LAST UPDATED: 2025-09-07
"""

import re
import time
import random
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, clean_price_string
from urllib.parse import parse_qs, urlparse

class EbayOfficialScraper(BaseScraper):
    """
    eBay official store scraper for manufacturer listings
    
    Designed specifically for official manufacturer stores like Bluetti UK,
    focusing on "Buy It Now" fixed prices rather than auction listings.
    """
    
    def __init__(self):
        super().__init__('ebay_official', 'https://www.ebay.co.uk')
        
        # eBay-specific headers to avoid bot detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1'
        })
    
    def get_page(self, url, max_retries=3):
        """
        eBay-specific page fetching with enhanced anti-detection
        
        eBay has strict rate limiting and sophisticated bot detection.
        This method includes longer delays and realistic browsing patterns.
        """
        for attempt in range(max_retries):
            try:
                # Longer delays for eBay (they track request patterns)
                delay = random.uniform(4, 8) + (attempt * 2)
                time.sleep(delay)
                
                self.logger.info(f"Fetching eBay page (attempt {attempt + 1}/{max_retries}): {url}")
                
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 429:  # Too Many Requests
                    self.logger.warning(f"Rate limited by eBay (attempt {attempt + 1}). Waiting longer...")
                    time.sleep(30)  # Long wait for rate limiting
                    continue
                
                if response.status_code == 403:
                    self.logger.warning(f"403 Forbidden from eBay (attempt {attempt + 1}). May be blocked...")
                    continue
                
                response.raise_for_status()
                
                self.logger.info(f"Successfully fetched eBay page: {url}")
                return BeautifulSoup(response.content, 'html.parser')
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for eBay URL {url}: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"All attempts failed for eBay URL: {url}")
                    return None
        
        return None
    
    def extract_price(self, soup):
        """
        Extract Buy It Now price from eBay listing
        
        eBay price structure:
        - Buy It Now prices (fixed price, what we want)
        - Auction prices (current bid, ignore these)
        - Shipping costs (may be separate or included)
        - Multi-variant pricing (different options)
        
        Priority: Buy It Now > Fixed Price > Best Offer listings
        """
        
        # Primary eBay price selectors (Buy It Now / Fixed Price)
        price_selectors = [
            # New eBay UI selectors (2024+)
            '[data-testid="x-price-primary"] .notranslate',
            '.notranslate[data-testid*="price"]',
            
            # Classic eBay price selectors
            '#prcIsum', # Main price element
            '.u-flL .notranslate', # Buy It Now price
            '.vi-price .notranslate', # Item price display
            
            # Alternative selectors
            '[data-test-id="price"]',
            '.it-prc', # Item price
            '.vi-prc', # View item price
            
            # Fallback selectors
            '.price .notranslate',
            '.prcVwItm .notranslate',
            '.bin-price .notranslate'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                
                # Skip if this looks like shipping cost
                if 'shipping' in price_text.lower() or 'postage' in price_text.lower():
                    continue
                
                # Skip if this looks like a bid/offer prompt
                if any(word in price_text.lower() for word in ['bid', 'offer', 'starting']):
                    continue
                
                price = clean_price_string(price_text)
                
                # eBay price validation (power stations range)
                if price and 50 <= price <= 6000:
                    self.logger.info(f"Found eBay price with selector '{selector}': £{price}")
                    return price
        
        # Try JSON-LD structured data (eBay often uses this)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                try:
                    import json
                    data = json.loads(script.string)
                    
                    # Handle arrays of structured data
                    if isinstance(data, list):
                        data = data[0]  # Take first item
                    
                    if data.get('@type') == 'Product':
                        offers = data.get('offers', {})
                        if offers.get('price'):
                            price = float(offers['price'])
                            if 50 <= price <= 6000:
                                self.logger.info(f"Found eBay price in JSON-LD: £{price}")
                                return price
                
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        
        # Try meta tags (eBay sometimes uses these for SEO)
        meta_price = soup.find('meta', attrs={'property': 'product:price:amount'})
        if meta_price and meta_price.get('content'):
            try:
                price = float(meta_price['content'])
                if 50 <= price <= 6000:
                    self.logger.info(f"Found eBay price in meta tags: £{price}")
                    return price
            except ValueError:
                pass
        
        self.logger.warning("No valid price found on eBay page")
        return None
    
    def extract_availability(self, soup):
        """
        Extract availability from eBay listing
        
        eBay availability patterns:
        - "Buy It Now" button (available for fixed price purchase)
        - Quantity available indicators
        - "Out of stock" messages
        - Auction ended indicators
        """
        
        # Check for Buy It Now button (strongest stock indicator)
        buy_it_now_selectors = [
            '#binBtn_btn',  # Classic Buy It Now button
            '[data-test-id="buy-it-now"]',
            '.vi-bin-btn',  # View item Buy It Now
            '.buyItNow',
            '[data-testid*="buy-now"]'
        ]
        
        for selector in buy_it_now_selectors:
            button = soup.select_one(selector)
            if button and not button.get('disabled'):
                # Check if button text indicates availability
                button_text = button.get_text().lower()
                if 'buy it now' in button_text or 'buy now' in button_text:
                    self.logger.info("Found active 'Buy It Now' button - item available")
                    return True
        
        # Check quantity available
        quantity_selectors = [
            '#qtySubTxt',  # Quantity available text
            '.vi-qnt-avail',  # View item quantity available
            '[data-test-id="quantity"]'
        ]
        
        for selector in quantity_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                if 'available' in text and not 'not available' in text:
                    self.logger.info(f"Found quantity indicator: {text}")
                    return True
                if 'out of stock' in text or 'sold out' in text:
                    self.logger.info(f"Found out of stock indicator: {text}")
                    return False
        
        # Check for general availability messages
        availability_selectors = [
            '.vi-availability',  # View item availability
            '.availability',
            '[data-test-id="availability"]'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().lower()
                if any(phrase in text for phrase in ['in stock', 'available', 'ready to ship']):
                    self.logger.info(f"Found positive availability indicator: {text}")
                    return True
                if any(phrase in text for phrase in ['out of stock', 'unavailable', 'sold out', 'ended']):
                    self.logger.info(f"Found negative availability indicator: {text}")
                    return False
        
        # Check if listing has ended (auction format)
        if soup.select_one('.ended') or 'listing has ended' in soup.get_text().lower():
            self.logger.info("eBay listing has ended - not available")
            return False
        
        # Default to available if we found a price (Buy It Now listings with prices are usually available)
        self.logger.info("Could not determine eBay availability - defaulting to available")
        return True
    
    def _extract_shipping_cost(self, soup):
        """
        Extract shipping cost if shown separately
        
        eBay often shows shipping costs separately from item price.
        This can be important for total cost comparison.
        """
        shipping_selectors = [
            '#fshippingCost',  # Free shipping cost element
            '.vi-acc-oth-shp .notranslate',  # View item shipping cost
            '[data-test-id="shipping-cost"]',
            '.ship-cost'
        ]
        
        for selector in shipping_selectors:
            element = soup.select_one(selector)
            if element:
                shipping_text = element.get_text().strip()
                if 'free' in shipping_text.lower():
                    return 0.0
                
                shipping_cost = clean_price_string(shipping_text)
                if shipping_cost and shipping_cost < 100:  # Reasonable shipping cost
                    return shipping_cost
        
        return None
    
    def scrape_product(self, product_id, url):
        """
        Enhanced eBay scraping with shipping cost handling
        """
        self.logger.info(f"Starting eBay scrape for {product_id}: {url}")
        
        soup = self.get_page(url)
        if not soup:
            self.logger.error(f"eBay scraping failed for {product_id} - couldn't fetch page")
            return None
        
        try:
            price = self.extract_price(soup)
            in_stock = self.extract_availability(soup)
            
            if price is None:
                self.logger.warning(f"No price found for {product_id} on eBay")
                return None
            
            # Check for shipping costs
            shipping_cost = self._extract_shipping_cost(soup)
            if shipping_cost is not None and shipping_cost > 0:
                self.logger.info(f"eBay shipping cost for {product_id}: £{shipping_cost}")
                # For now, we'll track item price only. Shipping can be added to metadata if needed.
                # total_price = price + shipping_cost
            
            result = {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': float(price),
                'in_stock': in_stock,
                'url': url
            }
            
            # Add shipping info to metadata if available
            if shipping_cost is not None:
                result['metadata'] = {'shipping_cost': shipping_cost}
            
            # Save to database/JSON
            self.save_price(result)
            
            self.logger.info(f"Successfully scraped eBay {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping eBay {product_id}: {e}")
            return None

# Test function for development
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '..')
    from logging_config import setup_logging
    
    setup_logging()
    scraper = EbayOfficialScraper()
    
    # Test with a Bluetti eBay official store product
    # Note: Replace with actual Bluetti eBay listing URL
    test_url = "https://www.ebay.co.uk/itm/123456789"  # Example URL structure
    result = scraper.scrape_product("bluetti-eb3a", test_url)
    
    if result:
        print(f"SUCCESS: {result}")
    else:
        print("FAILED: Could not scrape eBay product")