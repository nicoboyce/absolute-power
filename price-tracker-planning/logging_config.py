"""
Logging configuration for power tracker
Provides comprehensive logging for monitoring Pi operations
"""

import logging
import logging.handlers
from pathlib import Path
from config import LOGS_DIR

def setup_logging():
    """Configure logging with rotating files and console output"""
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Main application log (rotating)
    main_log_file = LOGS_DIR / 'power_tracker.log'
    main_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    main_handler.setLevel(logging.INFO)
    main_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main_handler.setFormatter(main_formatter)
    root_logger.addHandler(main_handler)
    
    # Scraping-specific log (rotating)
    scrape_log_file = LOGS_DIR / 'scraping.log'
    scrape_handler = logging.handlers.RotatingFileHandler(
        scrape_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    scrape_handler.setLevel(logging.DEBUG)
    scrape_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    scrape_handler.setFormatter(scrape_formatter)
    
    # Add scrape handler only to scraper loggers
    scraper_logger = logging.getLogger('scraper')
    scraper_logger.addHandler(scrape_handler)
    scraper_logger.setLevel(logging.DEBUG)
    
    # Site generation log
    site_log_file = LOGS_DIR / 'site_generation.log'
    site_handler = logging.handlers.RotatingFileHandler(
        site_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    site_handler.setLevel(logging.INFO)
    site_handler.setFormatter(main_formatter)
    
    site_logger = logging.getLogger('site_gen')
    site_logger.addHandler(site_handler)
    site_logger.setLevel(logging.INFO)
    
    # Deployment log
    deploy_log_file = LOGS_DIR / 'deployment.log'
    deploy_handler = logging.handlers.RotatingFileHandler(
        deploy_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    deploy_handler.setLevel(logging.INFO)
    deploy_handler.setFormatter(main_formatter)
    
    deploy_logger = logging.getLogger('deploy')
    deploy_logger.addHandler(deploy_handler)
    deploy_logger.setLevel(logging.INFO)
    
    # Error-only log for quick problem identification
    error_log_file = LOGS_DIR / 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(main_formatter)
    root_logger.addHandler(error_handler)
    
    # Daily summary log for monitoring
    summary_log_file = LOGS_DIR / 'daily_summary.log'
    summary_handler = logging.handlers.TimedRotatingFileHandler(
        summary_log_file,
        when='midnight',
        backupCount=30  # Keep 30 days
    )
    summary_handler.setLevel(logging.INFO)
    summary_formatter = logging.Formatter(
        '%(asctime)s - SUMMARY - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    summary_handler.setFormatter(summary_formatter)
    
    summary_logger = logging.getLogger('summary')
    summary_logger.addHandler(summary_handler)
    summary_logger.setLevel(logging.INFO)
    summary_logger.propagate = False  # Don't propagate to root logger
    
    logging.info("Logging system initialized")
    return root_logger

def log_scrape_summary(successful_scrapes, failed_scrapes, total_products):
    """Log daily scraping summary"""
    summary_logger = logging.getLogger('summary')
    summary_logger.info(f"Scrape completed: {successful_scrapes}/{total_products} successful, {failed_scrapes} failed")

def log_deployment_summary(files_uploaded, errors):
    """Log deployment summary"""
    summary_logger = logging.getLogger('summary')
    if errors:
        summary_logger.error(f"Deployment completed with errors: {files_uploaded} files uploaded, {len(errors)} errors")
    else:
        summary_logger.info(f"Deployment successful: {files_uploaded} files uploaded")

def log_site_generation_summary(pages_generated, total_products):
    """Log site generation summary"""
    summary_logger = logging.getLogger('summary')
    summary_logger.info(f"Site generated: {pages_generated} pages for {total_products} products")

# Function to easily tail logs for monitoring
def get_recent_logs(log_name='power_tracker', lines=50):
    """Get recent log entries for monitoring"""
    log_file = LOGS_DIR / f'{log_name}.log'
    if log_file.exists():
        with open(log_file, 'r') as f:
            return f.readlines()[-lines:]
    return []