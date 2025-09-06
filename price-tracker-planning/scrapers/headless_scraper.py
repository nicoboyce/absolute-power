"""
Headless browser scraper for JavaScript-heavy sites
Uses Playwright for reliable scraping of dynamic content
"""

import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time
import random
from scrapers.base import BaseScraper, clean_price_string

class HeadlessScraper(BaseScraper):
    """Base class for headless browser scraping using Playwright"""
    
    def __init__(self, retailer_name, base_url):
        super().__init__(retailer_name, base_url)
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-extensions',
            ]
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            java_script_enabled=True,
            ignore_https_errors=True
        )
        
        # Set realistic headers
        await self.context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.page = await self.context.new_page()
        
    async def close_browser(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def get_page_content(self, url, wait_for_selector=None, wait_time=3):
        """
        Fetch page content with JavaScript rendering
        
        Args:
            url: URL to fetch
            wait_for_selector: CSS selector to wait for (optional)
            wait_time: Time to wait for page load (seconds)
        """
        try:
            # Random delay before request
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navigate to page
            response = await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response.status != 200:
                self.logger.error(f"HTTP {response.status} for {url}")
                return None
                
            # Wait for specific content if specified
            if wait_for_selector:
                try:
                    await self.page.wait_for_selector(wait_for_selector, timeout=10000)
                except:
                    self.logger.warning(f"Selector {wait_for_selector} not found on {url}")
            else:
                # Generic wait for page stability
                await asyncio.sleep(wait_time)
                
            # Get page content
            content = await self.page.content()
            self.logger.info(f"Successfully fetched: {url}")
            
            return BeautifulSoup(content, 'html.parser')
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    async def scrape_product_async(self, product_id, url, price_selector=None, stock_selector=None):
        """Async version of scrape_product for headless browser"""
        if not self.browser:
            await self.init_browser()
            
        soup = await self.get_page_content(url)
        if not soup:
            self.log_scrape_result(product_id, 'error', 'Failed to fetch page')
            return None
            
        try:
            # Extract price using provided selector or class method
            if price_selector:
                price_elem = soup.select_one(price_selector)
                price = clean_price_string(price_elem.text if price_elem else None)
            else:
                price = self.extract_price(soup)
                
            # Extract availability
            if stock_selector:
                stock_elem = soup.select_one(stock_selector)
                in_stock = self.parse_stock_status(stock_elem.text if stock_elem else '')
            else:
                in_stock = self.extract_availability(soup)
                
            if price is None:
                self.log_scrape_result(product_id, 'not_found', 'Price not found')
                return None
                
            result = {
                'product_id': product_id,
                'retailer': self.retailer_name,
                'price': float(price),
                'in_stock': in_stock,
                'url': url
            }
            
            # Save to database
            self.save_price(result)
            self.log_scrape_result(product_id, 'success')
            
            self.logger.info(f"Scraped {product_id}: £{price} ({'in stock' if in_stock else 'out of stock'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping {product_id}: {e}")
            self.log_scrape_result(product_id, 'error', str(e))
            return None
            
    def parse_stock_status(self, text):
        """Parse stock status from text"""
        text = text.lower()
        if any(phrase in text for phrase in ['in stock', 'available', 'add to cart', 'buy now']):
            return True
        elif any(phrase in text for phrase in ['out of stock', 'unavailable', 'sold out']):
            return False
        else:
            return True  # Default to in stock if unclear
            
    def scrape_product(self, product_id, url):
        """Sync wrapper for async scrape method"""
        return asyncio.run(self.scrape_product_async(product_id, url))

class EcoFlowHeadlessScraper(HeadlessScraper):
    """EcoFlow scraper using headless browser"""
    
    def __init__(self):
        super().__init__('ecoflow_uk_headless', 'https://uk.ecoflow.com')
        
    def extract_price(self, soup):
        """Extract price from EcoFlow product page"""
        # Multiple selectors to try
        selectors = [
            '.price-current',
            '.product-price',
            '[data-price]',
            '.price',
            '.current-price'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                self.logger.info(f"Found price with selector {selector}: {elem.text}")
                return clean_price_string(elem.text)
                
        # Pattern matching fallback
        import re
        text = soup.get_text()
        price_match = re.search(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        if price_match:
            price = price_match.group(1).replace(',', '')
            self.logger.info(f"Pattern match price: £{price}")
            return float(price)
            
        return None
        
    def extract_availability(self, soup):
        """Extract availability from EcoFlow product page"""
        # Check for stock indicators
        stock_indicators = soup.find_all(text=True)
        stock_text = ' '.join(stock_indicators).lower()
        
        if any(phrase in stock_text for phrase in ['add to cart', 'buy now', 'in stock']):
            return True
        elif any(phrase in stock_text for phrase in ['out of stock', 'sold out', 'unavailable']):
            return False
        else:
            self.logger.info("Availability unclear - defaulting to in stock")
            return True

class BluettiHeadlessScraper(HeadlessScraper):
    """Bluetti scraper using headless browser"""
    
    def __init__(self):
        super().__init__('bluetti_uk_headless', 'https://bluettipower.co.uk')
        
    def extract_price(self, soup):
        """Extract price from Bluetti product page"""
        selectors = [
            '.price',
            '.product-price',
            '.current-price',
            '[class*="price"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return clean_price_string(elem.text)
                
        # Pattern matching
        import re
        text = soup.get_text()
        price_match = re.search(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        if price_match:
            return float(price_match.group(1).replace(',', ''))
            
        return None
        
    def extract_availability(self, soup):
        """Extract availability from Bluetti product page"""
        return self.parse_stock_status(soup.get_text())

# Usage example for running all headless scrapers
async def run_headless_scrapers():
    """Run all headless scrapers concurrently"""
    scrapers = [
        EcoFlowHeadlessScraper(),
        BluettiHeadlessScraper()
    ]
    
    # Initialize all browsers
    for scraper in scrapers:
        await scraper.init_browser()
        
    try:
        # Run scraping tasks
        tasks = []
        for scraper in scrapers:
            # Add your product URLs here
            tasks.append(scraper.scrape_product_async('test-product', scraper.base_url))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
        
    finally:
        # Clean up
        for scraper in scrapers:
            await scraper.close_browser()

if __name__ == '__main__':
    asyncio.run(run_headless_scrapers())