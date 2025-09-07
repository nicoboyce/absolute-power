"""
Headless browser scraper for JavaScript-heavy sites
Uses Selenium for reliable scraping of dynamic content
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from scrapers.base import BaseScraper, clean_price_string

class HeadlessScraper(BaseScraper):
    """Base class for headless browser scraping using Selenium"""
    
    def __init__(self, retailer_name, base_url):
        super().__init__(retailer_name, base_url)
        self.driver = None
        
    def init_browser(self):
        """Initialize Selenium browser"""
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # ARM-specific options for Raspberry Pi
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Try multiple possible chromedriver locations
        possible_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver', 
            '/opt/chrome/chromedriver',
            'chromedriver'  # In PATH
        ]
        
        chromedriver_path = None
        for path in possible_paths:
            if Path(path).exists() or path == 'chromedriver':
                chromedriver_path = path
                break
        
        if not chromedriver_path:
            self.logger.error("No chromedriver found in standard locations")
            raise FileNotFoundError("chromedriver not found")
        
        service = Service(chromedriver_path)
        
        try:
            self.logger.info(f"Initializing Chrome driver with path: {chromedriver_path}")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            self.logger.info("Browser initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser with {chromedriver_path}: {e}")
            # Try fallback approach
            try:
                self.logger.info("Attempting fallback browser initialization...")
                options.add_argument('--remote-debugging-port=9222')
                self.driver = webdriver.Chrome(options=options)  # Let Selenium find driver
                self.driver.set_page_load_timeout(30)
                self.driver.implicitly_wait(10)
                self.logger.info("Fallback browser initialization successful")
            except Exception as e2:
                self.logger.error(f"Fallback also failed: {e2}")
                raise
        
    def close_browser(self):
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
            
    def get_page_content(self, url, wait_for_selector=None, wait_time=3, max_retries=3):
        """
        Fetch page content with JavaScript rendering and retry logic
        
        Args:
            url: URL to fetch
            wait_for_selector: CSS selector to wait for (optional)
            wait_time: Time to wait for page load (seconds)
            max_retries: Maximum retry attempts
        """
        for attempt in range(max_retries):
            try:
                # Random delay before request
                time.sleep(random.uniform(2, 5))
                
                self.logger.info(f"Navigating to {url} (attempt {attempt + 1}/{max_retries})")
                
                # Navigate to page with timeout handling
                self.driver.get(url)
                
                # Wait for page to be ready
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # Wait for specific content if specified
                if wait_for_selector:
                    try:
                        wait = WebDriverWait(self.driver, 15)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector)))
                        self.logger.info(f"Found selector: {wait_for_selector}")
                    except Exception as e:
                        self.logger.warning(f"Selector {wait_for_selector} not found on {url}: {e}")
                        # Continue anyway - selector might not always be present
                
                # Additional wait for dynamic content
                time.sleep(wait_time)
                
                # Scroll to trigger any lazy loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                # Get page content
                content = self.driver.page_source
                self.logger.info(f"Successfully fetched: {url}")
                
                return BeautifulSoup(content, 'html.parser')
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {5 * (attempt + 1)} seconds...")
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"All {max_retries} attempts failed for {url}")
                    return None
        
        return None

    def scrape_product(self, product_id, url, price_selector=None, stock_selector=None):
        """Scrape product using headless browser"""
        if not self.driver:
            self.init_browser()
            
        soup = self.get_page_content(url, wait_for_selector=price_selector)
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

# Usage example for running headless scrapers
def run_headless_scrapers():
    """Run headless scrapers sequentially"""
    scrapers = [
        EcoFlowHeadlessScraper(),
        BluettiHeadlessScraper()
    ]
    
    results = []
    for scraper in scrapers:
        try:
            scraper.init_browser()
            # Add your product URLs here
            result = scraper.scrape_product('test-product', scraper.base_url)
            results.append(result)
        except Exception as e:
            logging.error(f"Error with {scraper.retailer_name}: {e}")
            results.append(None)
        finally:
            scraper.close_browser()
    
    return results

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_headless_scrapers()