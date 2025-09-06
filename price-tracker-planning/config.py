"""
Configuration settings for the power tracker application
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data directories
PRODUCTS_DIR = BASE_DIR / "data" / "products"
PRICES_DIR = BASE_DIR / "data" / "prices"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"

# Database settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tracker',
    'password': os.getenv('DB_PASSWORD', 'your_password_here'),
    'database': 'power_tracker'
}

# Scraping settings
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

REQUEST_DELAY = 2  # seconds between requests
TIMEOUT = 10  # request timeout in seconds

# Deployment settings
REMOTE_HOST = 'your-domain.com'
REMOTE_USER = 'username'
REMOTE_PATH = '/path/to/web/directory'
SSH_KEY_PATH = '~/.ssh/id_rsa'

# Site settings
SITE_NAME = "Power Station Price Tracker"
SITE_URL = "https://your-domain.com"
SITE_DESCRIPTION = "Track prices for portable power stations across UK retailers"

# Retailers configuration
RETAILERS = {
    'currys': {
        'name': 'Currys',
        'base_url': 'https://www.currys.co.uk',
        'affiliate_tag': 'your_currys_affiliate_id'
    },
    'argos': {
        'name': 'Argos', 
        'base_url': 'https://www.argos.co.uk',
        'affiliate_tag': 'your_argos_affiliate_id'
    },
    'anker': {
        'name': 'Anker UK',
        'base_url': 'https://www.anker.com/uk',
        'affiliate_tag': 'your_anker_affiliate_id'
    }
}