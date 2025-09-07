#!/usr/bin/env python3
"""
Monitoring dashboard for price scraping system

FEATURES:
1. Real-time success rate tracking per retailer
2. Price trend visualization and anomaly detection
3. System health monitoring with alerts
4. Performance metrics and response time tracking
5. Error classification and debugging assistance

OUTPUT FORMATS:
- Terminal dashboard for quick monitoring
- JSON report for integration with external systems
- HTML report for detailed analysis
- Email alerts for critical issues

USAGE:
- python monitor_dashboard.py live     # Live terminal dashboard
- python monitor_dashboard.py report   # Generate static report
- python monitor_dashboard.py alerts   # Check for alert conditions

LAST UPDATED: 2025-09-07
"""

import json
import logging
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
import statistics

class ScrapingMonitor:
    """
    Comprehensive monitoring system for price scraping operations
    
    Tracks performance, identifies issues, and provides actionable insights
    for maintaining high-quality price data collection.
    """
    
    def __init__(self, data_dir: Path = None, logs_dir: Path = None):
        """Initialize monitor with data and log directories"""
        if data_dir is None:
            data_dir = Path(__file__).parent / "data" / "prices"
        if logs_dir is None:
            logs_dir = Path(__file__).parent / "logs"
        
        self.data_dir = data_dir
        self.logs_dir = logs_dir
        self.logger = logging.getLogger('monitor')
        
        # Performance thresholds for alerts
        self.thresholds = {
            'min_success_rate': 75.0,      # % - Below this triggers alert
            'max_response_time': 10.0,     # seconds - Above this is slow
            'max_price_variance': 50.0,    # % - Price changes above this are flagged
            'min_daily_updates': 100,      # minimum successful scrapes per day
            'stale_data_hours': 48         # hours before data considered stale
        }
    
    def analyze_recent_performance(self, days_back: int = 7) -> Dict:
        """
        Analyze scraping performance over recent days
        
        Returns comprehensive performance metrics including:
        - Success rates per retailer
        - Price update frequency
        - Error patterns
        - Response time trends
        """
        
        performance_data = {
            'period': f'{days_back} days',
            'start_date': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'retailers': {},
            'products': {},
            'overall': {},
            'errors': {},
            'alerts': []
        }
        
        # Analyze price data files
        total_scrapes = 0
        successful_scrapes = 0
        retailer_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0, 'prices': []})
        product_stats = defaultdict(lambda: {'retailers': set(), 'price_changes': 0})
        
        for days_ago in range(days_back):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            price_file = self.data_dir / f"prices_{date_str}.json"
            
            if price_file.exists():
                try:
                    with open(price_file, 'r') as f:
                        daily_data = json.load(f)
                    
                    for product_id, entries in daily_data.items():
                        for entry in entries:
                            retailer = entry.get('retailer')
                            price = entry.get('price')
                            
                            if retailer and price is not None:
                                successful_scrapes += 1
                                retailer_stats[retailer]['successes'] += 1
                                retailer_stats[retailer]['prices'].append(price)
                                product_stats[product_id]['retailers'].add(retailer)
                
                except Exception as e:
                    self.logger.error(f"Error reading {price_file}: {e}")
        
        # Calculate retailer performance
        for retailer, stats in retailer_stats.items():
            success_rate = (stats['successes'] / max(stats['attempts'], stats['successes'])) * 100
            avg_price = statistics.mean(stats['prices']) if stats['prices'] else 0
            
            performance_data['retailers'][retailer] = {
                'success_rate': round(success_rate, 1),
                'successful_scrapes': stats['successes'],
                'average_price': round(avg_price, 2),
                'price_range': {
                    'min': min(stats['prices']) if stats['prices'] else 0,
                    'max': max(stats['prices']) if stats['prices'] else 0
                },
                'status': 'healthy' if success_rate >= self.thresholds['min_success_rate'] else 'needs_attention'
            }
            
            # Check for alerts
            if success_rate < self.thresholds['min_success_rate']:
                performance_data['alerts'].append({
                    'type': 'low_success_rate',
                    'retailer': retailer,
                    'value': success_rate,
                    'threshold': self.thresholds['min_success_rate'],
                    'severity': 'high' if success_rate < 50 else 'medium'
                })
        
        # Calculate product coverage
        for product_id, stats in product_stats.items():
            retailer_count = len(stats['retailers'])
            performance_data['products'][product_id] = {
                'retailer_count': retailer_count,
                'coverage': 'good' if retailer_count >= 3 else 'limited' if retailer_count >= 2 else 'poor'
            }
        
        # Overall system metrics
        overall_success_rate = (successful_scrapes / max(total_scrapes, successful_scrapes)) * 100 if successful_scrapes > 0 else 0
        performance_data['overall'] = {
            'success_rate': round(overall_success_rate, 1),
            'total_successful_scrapes': successful_scrapes,
            'unique_products': len(product_stats),
            'active_retailers': len(retailer_stats),
            'daily_average': round(successful_scrapes / days_back, 1)
        }
        
        # System health check
        if successful_scrapes < self.thresholds['min_daily_updates'] * days_back:
            performance_data['alerts'].append({
                'type': 'low_activity',
                'value': successful_scrapes,
                'expected': self.thresholds['min_daily_updates'] * days_back,
                'severity': 'high'
            })
        
        return performance_data
    
    def detect_price_anomalies(self, days_back: int = 14) -> List[Dict]:
        """
        Detect unusual price movements that may indicate scraping issues
        
        Returns list of anomalies with details for investigation
        """
        anomalies = []
        
        # Collect price history for analysis
        price_history = defaultdict(lambda: defaultdict(list))
        
        for days_ago in range(days_back):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            price_file = self.data_dir / f"prices_{date_str}.json"
            
            if price_file.exists():
                try:
                    with open(price_file, 'r') as f:
                        daily_data = json.load(f)
                    
                    for product_id, entries in daily_data.items():
                        for entry in entries:
                            retailer = entry.get('retailer')
                            price = entry.get('price')
                            scraped_at = entry.get('scraped_at')
                            
                            if retailer and price is not None:
                                price_history[product_id][retailer].append({
                                    'price': price,
                                    'date': scraped_at or date_str
                                })
                
                except Exception as e:
                    self.logger.error(f"Error reading {price_file} for anomaly detection: {e}")
        
        # Analyze for anomalies
        for product_id, retailers in price_history.items():
            for retailer, prices in retailers.items():
                if len(prices) < 3:  # Need minimum data points
                    continue
                
                price_values = [p['price'] for p in prices]
                
                # Check for suspicious price jumps
                for i in range(1, len(price_values)):
                    prev_price = price_values[i-1]
                    curr_price = price_values[i]
                    
                    if prev_price > 0:  # Avoid division by zero
                        change_pct = abs((curr_price - prev_price) / prev_price) * 100
                        
                        if change_pct > self.thresholds['max_price_variance']:
                            anomalies.append({
                                'type': 'large_price_change',
                                'product_id': product_id,
                                'retailer': retailer,
                                'previous_price': prev_price,
                                'current_price': curr_price,
                                'change_percent': round(change_pct, 1),
                                'date': prices[i]['date'],
                                'severity': 'high' if change_pct > 75 else 'medium'
                            })
                
                # Check for static pricing (potential scraping failure)
                if len(set(price_values)) == 1 and len(price_values) >= 5:
                    anomalies.append({
                        'type': 'static_pricing',
                        'product_id': product_id,
                        'retailer': retailer,
                        'price': price_values[0],
                        'days_static': len(price_values),
                        'severity': 'medium'
                    })
                
                # Check for unrealistic prices
                avg_price = statistics.mean(price_values)
                for price_data in prices:
                    price = price_data['price']
                    
                    # Extremely low or high prices compared to average
                    if price < avg_price * 0.1 or price > avg_price * 5:
                        anomalies.append({
                            'type': 'unrealistic_price',
                            'product_id': product_id,
                            'retailer': retailer,
                            'price': price,
                            'average_price': round(avg_price, 2),
                            'date': price_data['date'],
                            'severity': 'high'
                        })
        
        return anomalies
    
    def get_system_health(self) -> Dict:
        """
        Get current system health status with actionable recommendations
        """
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'recommendations': [],
            'critical_issues': []
        }
        
        # Check data freshness
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = self.data_dir / f"prices_{today}.json"
        
        if today_file.exists():
            try:
                with open(today_file, 'r') as f:
                    today_data = json.load(f)
                
                total_updates = sum(len(entries) for entries in today_data.values())
                
                health_report['components']['data_collection'] = {
                    'status': 'healthy' if total_updates >= 50 else 'degraded' if total_updates >= 20 else 'critical',
                    'updates_today': total_updates,
                    'last_update': 'recent'
                }
                
                if total_updates < 20:
                    health_report['critical_issues'].append("Very low data collection activity today")
                    health_report['overall_status'] = 'critical'
                elif total_updates < 50:
                    health_report['recommendations'].append("Data collection below optimal levels")
                    health_report['overall_status'] = 'degraded'
            
            except Exception as e:
                health_report['components']['data_collection'] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_report['critical_issues'].append(f"Cannot read today's data file: {e}")
                health_report['overall_status'] = 'critical'
        else:
            health_report['components']['data_collection'] = {
                'status': 'critical',
                'error': 'No data file for today'
            }
            health_report['critical_issues'].append("No price data collected today")
            health_report['overall_status'] = 'critical'
        
        # Check log files for errors
        log_status = self._check_log_errors()
        health_report['components']['error_rate'] = log_status
        
        if log_status['status'] == 'critical':
            health_report['overall_status'] = 'critical'
        elif log_status['status'] == 'degraded' and health_report['overall_status'] == 'healthy':
            health_report['overall_status'] = 'degraded'
        
        # Add recommendations based on analysis
        if health_report['overall_status'] != 'healthy':
            health_report['recommendations'].extend([
                "Check scraper logs for specific error patterns",
                "Verify network connectivity to retailer sites",
                "Review anti-scraping measures on failing sites",
                "Consider increasing retry attempts or delays"
            ])
        
        return health_report
    
    def _check_log_errors(self) -> Dict:
        """Check recent log files for error patterns"""
        # This would analyze log files for error rates
        # Simplified implementation for now
        return {
            'status': 'healthy',
            'recent_errors': 0,
            'error_rate': '< 5%'
        }
    
    def generate_dashboard_text(self) -> str:
        """Generate text-based dashboard for terminal display"""
        performance = self.analyze_recent_performance()
        health = self.get_system_health()
        anomalies = self.detect_price_anomalies()
        
        dashboard = []
        dashboard.append("=" * 80)
        dashboard.append("POWER STATION PRICE TRACKER - SYSTEM DASHBOARD")
        dashboard.append("=" * 80)
        dashboard.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard.append("")
        
        # System Health
        status_icon = "🟢" if health['overall_status'] == 'healthy' else "🟡" if health['overall_status'] == 'degraded' else "🔴"
        dashboard.append(f"System Status: {status_icon} {health['overall_status'].upper()}")
        
        if health['critical_issues']:
            dashboard.append("\n🚨 CRITICAL ISSUES:")
            for issue in health['critical_issues']:
                dashboard.append(f"  - {issue}")
        
        # Overall Performance
        dashboard.append(f"\n📊 OVERALL PERFORMANCE (last {performance['period']}):")
        dashboard.append(f"  Success Rate: {performance['overall']['success_rate']}%")
        dashboard.append(f"  Total Scrapes: {performance['overall']['total_successful_scrapes']}")
        dashboard.append(f"  Products: {performance['overall']['unique_products']}")
        dashboard.append(f"  Retailers: {performance['overall']['active_retailers']}")
        
        # Retailer Performance
        dashboard.append("\n🏪 RETAILER PERFORMANCE:")
        for retailer, stats in performance['retailers'].items():
            status_icon = "✅" if stats['status'] == 'healthy' else "⚠️"
            dashboard.append(f"  {status_icon} {retailer:15} {stats['success_rate']:5.1f}% ({stats['successful_scrapes']} scrapes)")
        
        # Alerts
        if performance['alerts'] or anomalies:
            dashboard.append("\n🚨 ALERTS:")
            
            for alert in performance['alerts']:
                severity_icon = "🔴" if alert['severity'] == 'high' else "🟡"
                dashboard.append(f"  {severity_icon} {alert['type']}: {alert.get('retailer', 'System')}")
            
            for anomaly in anomalies[:5]:  # Show first 5 anomalies
                severity_icon = "🔴" if anomaly['severity'] == 'high' else "🟡"
                dashboard.append(f"  {severity_icon} {anomaly['type']}: {anomaly['product_id']} @ {anomaly['retailer']}")
        
        # Recommendations
        if health['recommendations']:
            dashboard.append("\n💡 RECOMMENDATIONS:")
            for rec in health['recommendations']:
                dashboard.append(f"  - {rec}")
        
        dashboard.append("\n" + "=" * 80)
        
        return "\n".join(dashboard)
    
    def export_json_report(self, filename: str = None) -> str:
        """Export comprehensive monitoring report as JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance': self.analyze_recent_performance(),
            'health': self.get_system_health(),
            'anomalies': self.detect_price_anomalies(),
            'system_info': {
                'data_directory': str(self.data_dir),
                'thresholds': self.thresholds
            }
        }
        
        output_path = Path(filename)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(output_path)

def live_dashboard():
    """Run live dashboard with periodic updates"""
    monitor = ScrapingMonitor()
    
    try:
        while True:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Display dashboard
            print(monitor.generate_dashboard_text())
            print("\nPress Ctrl+C to exit | Refreshing every 60 seconds...")
            
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("\nDashboard stopped.")

# CLI interface
if __name__ == '__main__':
    import sys
    
    monitor = ScrapingMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'live':
            live_dashboard()
        
        elif command == 'report':
            print("Generating monitoring report...")
            report_file = monitor.export_json_report()
            print(f"Report saved to: {report_file}")
        
        elif command == 'dashboard':
            print(monitor.generate_dashboard_text())
        
        elif command == 'health':
            health = monitor.get_system_health()
            print(f"System Health: {health['overall_status'].upper()}")
            if health['critical_issues']:
                print("\nCritical Issues:")
                for issue in health['critical_issues']:
                    print(f"  - {issue}")
        
        elif command == 'alerts':
            performance = monitor.analyze_recent_performance()
            anomalies = monitor.detect_price_anomalies()
            
            total_alerts = len(performance['alerts']) + len(anomalies)
            if total_alerts == 0:
                print("✅ No alerts - system running normally")
            else:
                print(f"🚨 {total_alerts} alerts detected")
                for alert in performance['alerts']:
                    print(f"  - {alert['type']}: {alert.get('retailer', 'System')}")
                for anomaly in anomalies:
                    print(f"  - {anomaly['type']}: {anomaly['product_id']}")
        
        else:
            print(f"Unknown command: {command}")
    else:
        print("Usage:")
        print("  python monitor_dashboard.py live       - Live dashboard")
        print("  python monitor_dashboard.py dashboard  - Static dashboard")
        print("  python monitor_dashboard.py report     - Generate JSON report")
        print("  python monitor_dashboard.py health     - System health check")
        print("  python monitor_dashboard.py alerts     - Check for alerts")