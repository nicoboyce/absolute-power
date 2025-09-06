#!/usr/bin/env python3
"""
Quick status check - one-liner system health
Perfect for checking from anywhere
"""

import mariadb
from datetime import datetime, timedelta
from config import DB_CONFIG

def quick_check():
    """One-line status summary"""
    try:
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Last hour's scraping activity
        since = datetime.now() - timedelta(hours=1)
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success
            FROM scrape_log 
            WHERE scraped_at >= ?
        """, (since,))
        
        total, success = cursor.fetchone()
        
        # Latest prices
        cursor.execute("SELECT COUNT(*) FROM price_history WHERE scraped_at >= ?", (since,))
        new_prices = cursor.fetchone()[0]
        
        # System health
        if total == 0:
            status = "🟡 IDLE"
        elif success == total and total > 0:
            status = "🟢 HEALTHY"
        elif success > total * 0.8:
            status = "🟡 PARTIAL"
        else:
            status = "🔴 ISSUES"
        
        print(f"{status} | Last hour: {success}/{total} scrapes, {new_prices} prices | {datetime.now():%H:%M:%S}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"🔴 ERROR | Database connection failed: {e} | {datetime.now():%H:%M:%S}")

if __name__ == '__main__':
    quick_check()