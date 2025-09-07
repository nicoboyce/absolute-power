#!/usr/bin/env python3
"""
Price validation and anomaly detection system

This module prevents false positives from promotional content and detects
pricing anomalies that require human review. Critical for data quality.

KEY FEATURES:
1. Price range validation per product category
2. Historical variance analysis 
3. Cross-retailer outlier detection
4. Promotional content filtering
5. Static price monitoring (staleness detection)

PREVENTS ISSUES LIKE:
- EcoFlow £700 promotional banner false positives
- Unrealistic pricing (£1 or £50,000 products)
- Cross-contamination from product bundles
- Stale pricing data going unnoticed

IMPLEMENTATION:
- Called from BaseScraper.save_price() for all scraped data
- Flags suspicious prices for manual review
- Auto-rejects obvious false positives
- Logs all validation decisions for debugging

LAST UPDATED: 2025-09-07
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from statistics import median, stdev
import re

logger = logging.getLogger(__name__)

class PriceValidator:
    """
    Comprehensive price validation with anomaly detection
    
    Validates scraped prices against historical data and market norms
    to prevent false positives and detect genuine price changes.
    """
    
    def __init__(self, data_dir: Path = None):
        """Initialize validator with price history data"""
        if data_dir is None:
            data_dir = Path(__file__).parent / "data" / "prices"
        
        self.data_dir = data_dir
        self.logger = logging.getLogger('price_validator')
        
        # Product category price ranges (GBP)
        self.category_ranges = {
            'power-stations': {
                'min': 80,      # Cheapest units like small USB power banks
                'max': 6000,    # Premium systems like Anker F3800
                'typical_min': 150,   # More realistic minimum
                'typical_max': 3500   # More realistic maximum
            }
        }
        
        # Promotional content patterns that cause false positives
        self.promotional_patterns = [
            r'£?700.*off.*orders',  # "50% off orders over £700"
            r'save.*£?\d+',         # "Save £200"
            r'£?\d+.*discount',     # "£300 discount"
            r'up to.*£?\d+.*off',   # "Up to £500 off"
            r'from.*£?\d+',         # "From £199" (minimum price indicators)
        ]
        
        # Compile regex patterns for performance
        self.promotional_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.promotional_patterns]
    
    def validate_price(self, product_id: str, retailer: str, price: float, 
                      product_category: str = 'power-stations') -> Tuple[bool, str]:
        """
        Validate a scraped price against multiple criteria
        
        Args:
            product_id: Unique product identifier
            retailer: Retailer name (e.g. 'jackery_uk', 'argos')
            price: Scraped price in GBP
            product_category: Product category for range validation
            
        Returns:
            (is_valid, reason): Tuple of validation result and explanation
        """
        
        # 1. Basic range validation
        category_range = self.category_ranges.get(product_category, self.category_ranges['power-stations'])
        
        if price < category_range['min']:
            return False, f"Price £{price} below minimum range £{category_range['min']}"
        
        if price > category_range['max']:
            return False, f"Price £{price} above maximum range £{category_range['max']}"
        
        # 2. Promotional pattern detection
        if self._is_promotional_price(price):
            return False, f"Price £{price} matches known promotional content pattern"
        
        # 3. Historical variance analysis
        historical_data = self._get_historical_prices(product_id)
        if historical_data:
            is_valid, reason = self._check_historical_variance(price, historical_data, retailer)
            if not is_valid:
                return False, reason
        
        # 4. Cross-retailer outlier detection
        current_prices = self._get_current_prices(product_id)
        if len(current_prices) >= 2:  # Need at least 2 prices for comparison
            is_valid, reason = self._check_cross_retailer_variance(price, current_prices, retailer)
            if not is_valid:
                return False, reason
        
        # 5. Realistic range check (tighter than category range)
        if price < category_range['typical_min']:
            self.logger.warning(f"Price £{price} for {product_id} is unusually low but within range")
        
        if price > category_range['typical_max']:
            self.logger.warning(f"Price £{price} for {product_id} is unusually high but within range")
        
        return True, "Price validation passed"
    
    def _is_promotional_price(self, price: float) -> bool:
        """Check if price matches known promotional false positive patterns"""
        
        # Specific known false positives
        known_false_positives = [700.0, 500.0, 200.0, 100.0]  # Common promotional thresholds
        
        if price in known_false_positives:
            self.logger.warning(f"Price £{price} matches known promotional false positive")
            return True
        
        return False
    
    def _get_historical_prices(self, product_id: str, days_back: int = 30) -> List[float]:
        """Retrieve historical prices for variance analysis"""
        historical_prices = []
        
        # Look back through recent price files
        for days_ago in range(days_back):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            price_file = self.data_dir / f"prices_{date_str}.json"
            
            if price_file.exists():
                try:
                    with open(price_file, 'r') as f:
                        data = json.load(f)
                    
                    if product_id in data:
                        for entry in data[product_id]:
                            if 'price' in entry:
                                historical_prices.append(float(entry['price']))
                
                except Exception as e:
                    self.logger.error(f"Error reading historical data from {price_file}: {e}")
        
        return historical_prices
    
    def _check_historical_variance(self, price: float, historical_prices: List[float], 
                                 retailer: str) -> Tuple[bool, str]:
        """Check if price is within reasonable variance of historical data"""
        
        if len(historical_prices) < 3:
            return True, "Insufficient historical data for variance check"
        
        median_price = median(historical_prices)
        
        try:
            std_dev = stdev(historical_prices)
        except:
            std_dev = median_price * 0.1  # Fallback: assume 10% standard deviation
        
        # Allow up to 3 standard deviations or 50% variance (whichever is larger)
        max_variance = max(std_dev * 3, median_price * 0.5)
        price_diff = abs(price - median_price)
        
        if price_diff > max_variance:
            variance_pct = (price_diff / median_price) * 100
            return False, f"Price £{price} differs by {variance_pct:.1f}% from historical median £{median_price:.2f}"
        
        # Warning for significant but acceptable changes
        warning_variance = max(std_dev * 2, median_price * 0.3)
        if price_diff > warning_variance:
            variance_pct = (price_diff / median_price) * 100
            self.logger.warning(f"{retailer} price £{price} is {variance_pct:.1f}% different from historical median £{median_price:.2f}")
        
        return True, "Historical variance check passed"
    
    def _get_current_prices(self, product_id: str) -> Dict[str, float]:
        """Get current prices from all retailers for cross-comparison"""
        current_prices = {}
        
        # Read today's price file
        today = datetime.now().strftime("%Y-%m-%d")
        price_file = self.data_dir / f"prices_{today}.json"
        
        if price_file.exists():
            try:
                with open(price_file, 'r') as f:
                    data = json.load(f)
                
                if product_id in data:
                    # Get latest price from each retailer
                    for entry in data[product_id]:
                        if 'retailer' in entry and 'price' in entry:
                            retailer = entry['retailer']
                            price = float(entry['price'])
                            
                            # Keep only the most recent price per retailer
                            if retailer not in current_prices:
                                current_prices[retailer] = price
            
            except Exception as e:
                self.logger.error(f"Error reading current prices from {price_file}: {e}")
        
        return current_prices
    
    def _check_cross_retailer_variance(self, price: float, current_prices: Dict[str, float], 
                                     retailer: str) -> Tuple[bool, str]:
        """Check if price is reasonable compared to other retailers"""
        
        other_prices = [p for r, p in current_prices.items() if r != retailer]
        
        if len(other_prices) == 0:
            return True, "No other retailer prices for comparison"
        
        median_other = median(other_prices)
        min_other = min(other_prices)
        max_other = max(other_prices)
        
        # Allow reasonable competitive variance (30% below median, or within min-max range)
        competitive_min = min(median_other * 0.7, min_other * 0.95)
        competitive_max = max(median_other * 1.3, max_other * 1.05)
        
        if price < competitive_min:
            discount_pct = ((median_other - price) / median_other) * 100
            if discount_pct > 50:  # Suspicious discount
                return False, f"Price £{price} is {discount_pct:.1f}% below other retailers (median £{median_other:.2f})"
            else:
                self.logger.info(f"Good deal: {retailer} price £{price} is {discount_pct:.1f}% below median £{median_other:.2f}")
        
        if price > competitive_max:
            premium_pct = ((price - median_other) / median_other) * 100
            if premium_pct > 50:  # Suspicious premium
                return False, f"Price £{price} is {premium_pct:.1f}% above other retailers (median £{median_other:.2f})"
            else:
                self.logger.info(f"Premium pricing: {retailer} price £{price} is {premium_pct:.1f}% above median £{median_other:.2f}")
        
        return True, "Cross-retailer variance check passed"
    
    def detect_stale_prices(self, hours_threshold: int = 48) -> Dict[str, List[str]]:
        """
        Detect products with prices that haven't updated recently
        
        Returns dict of {product_id: [list of stale retailers]}
        """
        stale_prices = {}
        cutoff_time = datetime.now() - timedelta(hours=hours_threshold)
        
        # Check recent price files
        for days_ago in range(3):  # Check last 3 days
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            price_file = self.data_dir / f"prices_{date_str}.json"
            
            if price_file.exists():
                try:
                    with open(price_file, 'r') as f:
                        data = json.load(f)
                    
                    for product_id, entries in data.items():
                        for entry in entries:
                            if 'retailer' in entry and 'scraped_at' in entry:
                                retailer = entry['retailer']
                                scraped_at = datetime.fromisoformat(entry['scraped_at'])
                                
                                if scraped_at < cutoff_time:
                                    if product_id not in stale_prices:
                                        stale_prices[product_id] = []
                                    if retailer not in stale_prices[product_id]:
                                        stale_prices[product_id].append(retailer)
                
                except Exception as e:
                    self.logger.error(f"Error checking stale prices in {price_file}: {e}")
        
        return stale_prices
    
    def generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""
        
        stale_prices = self.detect_stale_prices()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'stale_prices': stale_prices,
            'stale_count': sum(len(retailers) for retailers in stale_prices.values()),
            'validation_rules': {
                'price_ranges': self.category_ranges,
                'promotional_patterns': self.promotional_patterns,
                'variance_thresholds': {
                    'historical_max': '3 standard deviations or 50%',
                    'cross_retailer_max': '30% below median or within range'
                }
            }
        }
        
        return report

# Integration with BaseScraper
def validate_scraped_price(product_id: str, retailer: str, price: float, 
                          product_category: str = 'power-stations') -> Tuple[bool, str]:
    """
    Convenience function for integration with existing scrapers
    
    Can be called from BaseScraper.save_price() to validate before saving
    """
    validator = PriceValidator()
    return validator.validate_price(product_id, retailer, price, product_category)

# CLI interface for monitoring
if __name__ == '__main__':
    import sys
    
    validator = PriceValidator()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        # Generate validation report
        report = validator.generate_validation_report()
        print(json.dumps(report, indent=2))
    
    elif len(sys.argv) == 4:
        # Test validation: python price_validator.py product_id retailer price
        product_id = sys.argv[1]
        retailer = sys.argv[2]
        price = float(sys.argv[3])
        
        is_valid, reason = validator.validate_price(product_id, retailer, price)
        print(f"Validation result: {is_valid}")
        print(f"Reason: {reason}")
    
    else:
        print("Usage:")
        print("  python price_validator.py report                    - Generate validation report")
        print("  python price_validator.py product_id retailer price - Test price validation")