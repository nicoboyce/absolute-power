"""
EcoFlow UK scraper for portable power stations

Scrapes prices and availability directly from uk.ecoflow.com
Handles their dynamic pricing structure and promotional elements

MAINTENANCE NOTES:
- EcoFlow often has promotional banners with fixed prices (e.g. £700 off promotions)
- These banners can interfere with price extraction if not filtered properly
- Product pages use dynamic pricing that may require JavaScript for full loading
- Always test scraper changes against multiple products to ensure no false positives

LAST UPDATED: 2025-09-07
KNOWN ISSUES: Promotional banners containing £700 can be mistaken for product prices
"""

import re
from scrapers.base import BaseScraper, clean_price_string

class EcoFlowScraper(BaseScraper):
    def __init__(self):
        super().__init__('ecoflow_uk', 'https://uk.ecoflow.com')
    
    def extract_price(self, soup):
        """
        Extract price from EcoFlow UK product page
        
        CRITICAL: EcoFlow pages often contain promotional banners with prices like £700
        that are NOT the product price. This method must carefully select only the
        actual product price, not promotional content.
        
        Args:
            soup (BeautifulSoup): Parsed HTML of the product page
            
        Returns:
            float: Product price in GBP, or None if not found
            
        Common Issues:
        - Promotional banners: "50% off RAPID 5000 mAh on orders over £700"
        - These create false £700 matches that appear on every page
        - Must prioritise product-specific price selectors over generic patterns
        """
        # PRIMARY: EcoFlow specific product price selectors
        # These are the most reliable and product-specific elements
        primary_selectors = [
            '.product-price .price-item--regular',  # Main product price
            '.price__current .price-item',         # Current price display
            '.product-form__price .price',         # Product form price
            '[data-testid="product-price"]',      # Test ID for product price
            '.variant-price .money',               # Variant pricing
        ]
        
        # SECONDARY: Generic price selectors (less reliable)
        secondary_selectors = [
            '.price__current',
            '.product-price .price',
            '[data-testid="price"]',
            '.price-box .price',
            '.money'
        ]
        
        # Try primary selectors first (most reliable for actual product price)
        for selector in primary_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                self.logger.debug(f"Found primary price element ({selector}): {price_text}")
                
                # Extract numeric price
                price_match = re.search(r'£?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = clean_price_string(price_str)
                    if price and price != 700:  # Explicitly reject £700 (promotional banner price)
                        self.logger.info(f"Extracted product price from {selector}: £{price}")
                        return price
                    elif price == 700:
                        self.logger.warning(f"Rejected £700 from {selector} - likely promotional banner")
        
        # Try secondary selectors if primary ones fail
        for selector in secondary_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                self.logger.debug(f"Found secondary price element ({selector}): {price_text}")
                
                # Extract numeric price
                price_match = re.search(r'£?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = clean_price_string(price_str)
                    if price and price != 700 and 100 <= price <= 5000:  # Stricter range for secondary
                        self.logger.info(f"Extracted price from secondary {selector}: £{price}")
                        return price
                    elif price == 700:
                        self.logger.warning(f"Rejected £700 from {selector} - likely promotional banner")
        
        # LAST RESORT: Pattern matching (high risk of false positives)
        # Only use if no structured price elements found
        self.logger.debug("No structured price found, trying pattern matching...")
        
        price_pattern = re.compile(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)')
        price_matches = price_pattern.findall(str(soup))
        
        # Filter out known promotional prices and collect candidates
        candidates = []
        for match in price_matches:
            price = clean_price_string(match.replace(',', ''))
            if price and price != 700 and 100 <= price <= 5000:  # Exclude £700 promotional price
                candidates.append(price)
        
        if candidates:
            # If multiple candidates, prefer the one that appears most product-like
            # (typically the highest price in a reasonable range)
            chosen_price = max(candidates) if len(candidates) > 1 else candidates[0]
            self.logger.info(f"Pattern match price (from {len(candidates)} candidates): £{chosen_price}")
            return chosen_price
        
        self.logger.warning("No valid price found - all matches were likely promotional content")
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