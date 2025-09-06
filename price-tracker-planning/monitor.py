#!/usr/bin/env python3
"""
Monitoring script for power tracker
Provides easy status checking and log viewing
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
import mariadb
from config import DB_CONFIG, LOGS_DIR
from logging_config import get_recent_logs

def get_db_connection():
    """Get database connection"""
    try:
        return mariadb.connect(**DB_CONFIG)
    except mariadb.Error as e:
        print(f"Database connection failed: {e}")
        return None

def show_recent_scrapes(hours=24):
    """Show recent scraping activity"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    
    # Get recent scrape summary
    cursor.execute("""
        SELECT retailer, 
               COUNT(*) as total_scrapes,
               SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
               SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
               MAX(scraped_at) as last_scrape
        FROM scrape_log 
        WHERE scraped_at >= ?
        GROUP BY retailer
        ORDER BY last_scrape DESC
    """, (since,))
    
    results = cursor.fetchall()
    
    print(f"\n📊 Scraping Activity (Last {hours} hours)")
    print("=" * 60)
    
    if not results:
        print("No recent scraping activity found")
        return
    
    for retailer, total, successful, errors, last_scrape in results:
        success_rate = (successful / total * 100) if total > 0 else 0
        status_emoji = "✅" if success_rate > 80 else "⚠️" if success_rate > 50 else "❌"
        
        print(f"{status_emoji} {retailer}:")
        print(f"   Total: {total}, Success: {successful}, Errors: {errors}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Last Scrape: {last_scrape}")
        print()
    
    cursor.close()
    conn.close()

def show_price_updates(hours=24):
    """Show recent price updates"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    
    cursor.execute("""
        SELECT product_id, retailer, price, scraped_at
        FROM price_history 
        WHERE scraped_at >= ?
        ORDER BY scraped_at DESC
        LIMIT 20
    """, (since,))
    
    results = cursor.fetchall()
    
    print(f"\n💰 Recent Price Updates (Last {hours} hours)")
    print("=" * 60)
    
    if not results:
        print("No recent price updates found")
        return
    
    for product_id, retailer, price, scraped_at in results:
        print(f"£{price:.2f} - {product_id} @ {retailer} ({scraped_at})")
    
    cursor.close()
    conn.close()

def show_system_status():
    """Show overall system status"""
    print("\n🖥️  System Status")
    print("=" * 60)
    
    # Check if processes are running
    import subprocess
    
    try:
        # Check cron status
        result = subprocess.run(['systemctl', 'is-active', 'cron'], 
                              capture_output=True, text=True)
        cron_status = "✅ Running" if result.returncode == 0 else "❌ Stopped"
        print(f"Cron Service: {cron_status}")
    except:
        print("Cron Service: ❓ Unknown")
    
    # Check database
    conn = get_db_connection()
    if conn:
        print("Database: ✅ Connected")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM price_history")
        total_prices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT product_id) FROM price_history")
        unique_products = cursor.fetchone()[0]
        
        print(f"Total Price Records: {total_prices:,}")
        print(f"Products Tracked: {unique_products}")
        
        cursor.close()
        conn.close()
    else:
        print("Database: ❌ Connection Failed")
    
    # Check log files
    log_files = ['power_tracker.log', 'scraping.log', 'errors.log']
    print("\nLog Files:")
    
    for log_file in log_files:
        log_path = LOGS_DIR / log_file
        if log_path.exists():
            size_mb = log_path.stat().st_size / (1024*1024)
            modified = datetime.fromtimestamp(log_path.stat().st_mtime)
            print(f"  {log_file}: ✅ {size_mb:.1f}MB (modified: {modified:%Y-%m-%d %H:%M})")
        else:
            print(f"  {log_file}: ❌ Not found")

def show_recent_errors(lines=10):
    """Show recent errors"""
    print(f"\n🚨 Recent Errors (Last {lines} lines)")
    print("=" * 60)
    
    error_logs = get_recent_logs('errors', lines)
    if not error_logs:
        print("✅ No recent errors found")
        return
    
    for line in error_logs[-lines:]:
        print(line.rstrip())

def show_logs(log_name='power_tracker', lines=20):
    """Show recent log entries"""
    print(f"\n📝 Recent {log_name} logs (Last {lines} lines)")
    print("=" * 60)
    
    logs = get_recent_logs(log_name, lines)
    if not logs:
        print(f"No logs found for {log_name}")
        return
    
    for line in logs[-lines:]:
        print(line.rstrip())

def main():
    parser = argparse.ArgumentParser(description='Power Tracker Monitoring')
    parser.add_argument('--scrapes', type=int, default=24, 
                       help='Show scraping activity for last N hours')
    parser.add_argument('--prices', type=int, default=24,
                       help='Show price updates for last N hours')
    parser.add_argument('--errors', type=int, default=10,
                       help='Show last N error log entries')
    parser.add_argument('--logs', choices=['power_tracker', 'scraping', 'deployment', 'site_generation'],
                       help='Show recent logs for specified component')
    parser.add_argument('--lines', type=int, default=20,
                       help='Number of log lines to show')
    parser.add_argument('--status', action='store_true',
                       help='Show system status')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # Show default overview
        show_system_status()
        show_recent_scrapes(args.scrapes)
        show_price_updates(args.prices)
        show_recent_errors(args.errors)
    else:
        if args.status:
            show_system_status()
        if args.scrapes:
            show_recent_scrapes(args.scrapes)
        if args.prices:
            show_price_updates(args.prices)
        if args.errors:
            show_recent_errors(args.errors)
        if args.logs:
            show_logs(args.logs, args.lines)

if __name__ == '__main__':
    main()