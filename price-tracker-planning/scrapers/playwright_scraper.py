"""
Enhanced headless scraper using Playwright for better reliability

ADVANTAGES OVER SELENIUM:
- Better performance and reliability
- Faster startup and execution  
- Better handling of modern JavaScript frameworks
- More robust on ARM/Raspberry Pi systems
- Less resource intensive
- Better error handling and recovery

IMPLEMENTATION:
- Drop-in replacement for Selenium-based scrapers
- Improved anti-detection measures
- Better retry logic and error handling
- ARM-compatible browser binaries
- Stealth mode for harder-to-scrape sites

LAST UPDATED: 2025-09-07
"""

import asyncio
import logging
import random
import time
from pathlib import Path
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, clean_price_string

class PlaywrightScraper:
    """
    Enhanced headless scraper using Playwright for JavaScript-heavy sites
    
    Better reliability than Selenium, especially for ARM systems and 
    sites with sophisticated anti-bot measures.
    """
    
    def __init__(self, retailer_name: str, base_url: str):
        self.retailer_name = retailer_name
        self.base_url = base_url
        self.logger = logging.getLogger(f'scraper.{retailer_name}')
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Import price validator for data quality
        try:
            from price_validator import validate_scraped_price
            self.price_validator = validate_scraped_price
            self.validation_enabled = True
        except ImportError:
            self.logger.warning("Price validation system not available")
            self.price_validator = None
            self.validation_enabled = False
    
    async def init_browser(self, headless: bool = True, slow_mo: int = 100):
        """
        Initialize Playwright browser with optimized settings
        
        Args:
            headless: Run in headless mode
            slow_mo: Delay between actions in milliseconds (helps avoid detection)
        """
        try:
            playwright = await async_playwright().start()
            
            # Use Chromium for best compatibility
            self.browser = await playwright.chromium.launch(
                headless=headless,
                slow_mo=slow_mo,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-extensions',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--metrics-recording-only',
                    '--mute-audio',
                    '--no-first-run',
                    '--safebrowsing-disable-auto-update',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI,VizDisplayCompositor',
                ]
            )
            
            # Create new page with realistic settings
            self.page = await self.browser.new_page()
            
            # Set realistic user agent and viewport
            await self.page.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            await self.page.set_viewport_size({'width': 1920, 'height': 1080})
            
            # Set extra headers to appear more human
            await self.page.set_extra_http_headers({
                'Accept-Language': 'en-GB,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            self.logger.info("Playwright browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright browser: {e}")
            raise
    
    async def close_browser(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            self.logger.info("Playwright browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing Playwright browser: {e}")
    
    async def get_page_content(self, url: str, wait_for_selector: str = None, 
                             wait_timeout: int = 10000, additional_wait: int = 2) -> Optional[BeautifulSoup]:
        """
        Navigate to page and get content with JavaScript execution
        
        Args:
            url: URL to navigate to
            wait_for_selector: CSS selector to wait for before proceeding
            wait_timeout: Max time to wait for selector (milliseconds) 
            additional_wait: Additional wait time after selector found (seconds)
        """
        try:
            # Random delay before navigation
            await asyncio.sleep(random.uniform(1, 3))
            
            self.logger.info(f"Navigating to: {url}")
            
            # Navigate with timeout
            response = await self.page.goto(url, timeout=30000, wait_until='networkidle')
            
            if response.status >= 400:
                self.logger.warning(f"HTTP {response.status} response from {url}")
                return None
            
            # Wait for specific content if specified
            if wait_for_selector:
                try:
                    await self.page.wait_for_selector(wait_for_selector, timeout=wait_timeout)
                    self.logger.info(f"Found selector: {wait_for_selector}")
                except Exception as e:
                    self.logger.warning(f"Selector {wait_for_selector} not found: {e}")
            
            # Additional wait for dynamic content
            if additional_wait > 0:
                await asyncio.sleep(additional_wait)
            
            # Get page content
            content = await self.page.content()
            self.logger.info(f"Successfully retrieved content from {url}")
            
            return BeautifulSoup(content, 'html.parser')
            
        except Exception as e:
            self.logger.error(f"Error getting page content from {url}: {e}")
            return None
    
    async def extract_text_by_selector(self, selector: str) -> Optional[str]:
        """Extract text from page using CSS selector"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else None
            return None
        except Exception as e:
            self.logger.error(f"Error extracting text with selector {selector}: {e}")
            return None
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot for debugging purposes"""
        if not filename:
            timestamp = int(time.time())
            filename = f"debug_screenshot_{timestamp}.png"
        
        try:
            screenshot_path = Path("logs") / filename
            screenshot_path.parent.mkdir(exist_ok=True)
            
            await self.page.screenshot(path=str(screenshot_path))
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return ""

class EnhancedEcoFlowScraper(PlaywrightScraper):
    """
    Enhanced EcoFlow scraper using Playwright for better JS handling
    
    EcoFlow uses heavy JavaScript for pricing and dynamic content.
    This scraper handles those challenges with better reliability.
    """
    
    def __init__(self):
        super().__init__('ecoflow_uk_enhanced', 'https://uk.ecoflow.com')
    
    async def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extract price from EcoFlow page with fallback strategies
        """
        # Primary selectors for EcoFlow pricing
        price_selectors = [
            '.price-now',
            '.current-price', 
            '.product-price .price',
            '[data-price]',
            '.price-current',
            '.sale-price'
        ]
        
        # Try direct CSS selection first
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                
                # Skip promotional content that caused £700 false positives
                if any(word in price_text.lower() for word in ['off', 'save', 'discount', 'orders over']):
                    continue
                
                price = clean_price_string(price_text)
                if price and 100 <= price <= 5000:
                    self.logger.info(f"Found EcoFlow price with selector '{selector}': £{price}")
                    return price
        
        # Fallback: Try extracting price directly from JavaScript if page content available
        if hasattr(self, 'page') and self.page:
            try:
                # Look for price in JavaScript variables
                js_price = await self.page.evaluate('''
                    () => {
                        // Common price variable names in EcoFlow's JS
                        if (window.productPrice) return window.productPrice;
                        if (window.currentPrice) return window.currentPrice;
                        if (window.price) return window.price;
                        
                        // Look for price data attributes
                        const priceElement = document.querySelector('[data-price]');
                        if (priceElement) return priceElement.dataset.price;
                        
                        return null;
                    }
                ''')
                
                if js_price:
                    price = float(js_price)
                    if 100 <= price <= 5000:
                        self.logger.info(f"Found EcoFlow price via JavaScript: £{price}")
                        return price
            except Exception as e:
                self.logger.debug(f"JavaScript price extraction failed: {e}")
        
        # Pattern matching as last resort
        import re
        page_text = soup.get_text()
        
        # Look for £XXX.XX or £X,XXX.XX patterns, excluding promotional text
        price_patterns = [
            r'£(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*GBP',
        ]
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, page_text)
            for match in matches:
                # Check context around the match to avoid promotional content
                start = max(0, match.start() - 50)
                end = min(len(page_text), match.end() + 50)
                context = page_text[start:end].lower()
                
                # Skip if in promotional context
                if any(word in context for word in ['off orders', 'save', 'discount', 'from']):
                    continue
                
                try:
                    price_str = match.group(1).replace(',', '')
                    price = float(price_str)
                    if 100 <= price <= 5000:
                        self.logger.info(f"Found EcoFlow price via pattern matching: £{price}")
                        return price
                except ValueError:
                    continue
        
        self.logger.warning("No valid price found on EcoFlow page")
        return None
    
    def extract_availability(self, soup: BeautifulSoup) -> bool:
        """Extract availability from EcoFlow page"""
        
        # Check for add to cart buttons
        cart_selectors = [
            '.add-to-cart:not([disabled])',
            '.btn-add-cart:not([disabled])',
            '.purchase-btn:not([disabled])',
            'button[data-action="add-to-cart"]:not([disabled])'
        ]
        
        for selector in cart_selectors:
            if soup.select_one(selector):
                self.logger.info("Found active add to cart button - product available")
                return True
        
        # Check stock status text
        page_text = soup.get_text().lower()
        
        # Positive indicators
        if any(phrase in page_text for phrase in ['add to cart', 'buy now', 'in stock', 'available']):
            return True
        
        # Negative indicators
        if any(phrase in page_text for phrase in ['out of stock', 'sold out', 'unavailable']):
            return False
        
        # Default to available if we have pricing
        return True
    
    async def scrape_product_async(self, product_id: str, url: str) -> Optional[Dict]:
        """
        Async product scraping with enhanced error handling
        """
        self.logger.info(f"Starting enhanced EcoFlow scrape for {product_id}: {url}")
        
        try:
            if not self.browser:
                await self.init_browser()
            
            # Get page content with wait for price elements
            soup = await self.get_page_content(url, wait_for_selector='.price, .product-price', additional_wait=3)
            
            if not soup:
                self.logger.error(f"Could not retrieve page content for {product_id}")
                return None
            
            # Extract price and availability
            price = await self.extract_price(soup)
            in_stock = self.extract_availability(soup)
            
            if price is None:
                self.logger.warning(f"No price found for EcoFlow {product_id}")
                return None
            
            # Validate price if validator available
            if self.validation_enabled and self.price_validator:
                is_valid, reason = self.price_validator(product_id, self.retailer_name, price)
                if not is_valid:
                    self.logger.warning(f"Price validation failed for {product_id}: {reason}")
                    return None
            
            result = {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': float(price),
                'in_stock': in_stock,
                'url': url,
                'scraped_at': time.time()
            }
            
            self.logger.info(f"Successfully scraped EcoFlow {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping EcoFlow {product_id}: {e}")
            return None
        
        finally:
            # Don't close browser here - reuse for efficiency
            pass

# Test and usage example
async def test_enhanced_scraper():
    """Test the enhanced scraper with a real product"""
    scraper = EnhancedEcoFlowScraper()
    
    try:
        await scraper.init_browser(headless=True)
        
        # Test with actual EcoFlow product URL
        test_url = "https://uk.ecoflow.com/products/river-3"
        result = await scraper.scrape_product_async("ecoflow-river-3", test_url)
        
        if result:
            print(f"SUCCESS: {result}")
        else:
            print("FAILED: Could not scrape product")
            
    finally:
        await scraper.close_browser()

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    asyncio.run(test_enhanced_scraper())