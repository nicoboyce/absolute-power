#!/usr/bin/env python3
"""
Simple test to verify Selenium is working
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys

def test_selenium():
    """Test basic Selenium functionality"""
    print("Testing Selenium with Chromium...")
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-features=VizDisplayCompositor')
    
    service = Service('/usr/bin/chromedriver')
    
    try:
        print("Initializing driver...")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        print("Loading example.com...")
        driver.get('https://example.com')
        
        print(f"Page title: {driver.title}")
        print("✅ Selenium is working!")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_selenium()
    sys.exit(0 if success else 1)