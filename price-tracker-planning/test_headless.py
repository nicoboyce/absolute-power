#!/usr/bin/env python3
"""
Test script for headless browser functionality
Tests both standard and headless scrapers
"""

import logging
from scrapers.headless_scraper import EcoFlowHeadlessScraper

def test_headless_scraper():
    """Test the headless scraper functionality"""
    logging.basicConfig(level=logging.INFO)
    
    scraper = EcoFlowHeadlessScraper()
    
    try:
        # Initialize browser
        scraper.init_browser()
        
        # Test fetching EcoFlow homepage
        soup = scraper.get_page_content('https://uk.ecoflow.com/')
        
        if soup:
            print("✅ Successfully loaded EcoFlow homepage with headless browser")
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Look for price elements
            price_elements = soup.find_all(text=lambda t: t and '£' in str(t))
            if price_elements:
                print(f"Found {len(price_elements)} price elements on homepage")
                for i, elem in enumerate(price_elements[:3]):  # Show first 3
                    print(f"  {i+1}. {elem.strip()}")
            else:
                print("No price elements found on homepage")
        else:
            print("❌ Failed to load EcoFlow homepage")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close_browser()
        print("Browser closed")

if __name__ == '__main__':
    print("Testing headless browser scraper...")
    test_headless_scraper()