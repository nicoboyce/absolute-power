# Setup Commands for Raspberry Pi

## System Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install MariaDB
sudo apt install mariadb-server mariadb-client -y
sudo mysql_secure_installation

# Install Python dependencies
sudo apt install python3-pip python3-venv -y
```

## Project Setup
```bash
# Create project directory
mkdir -p /home/pi/power-tracker
cd /home/pi/power-tracker

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install requests beautifulsoup4 jinja2 mariadb

# Create directory structure
mkdir -p {data/products,data/prices,scrapers,templates,static,logs}
```

## Directory Structure
```
/home/pi/power-tracker/
├── venv/                 # Python virtual environment
├── data/
│   ├── products/         # JSON product files
│   └── prices/           # Price history exports
├── scrapers/            # Web scraping scripts
├── templates/           # Jinja2 templates
├── static/              # Generated static site
├── logs/                # Scraping logs
├── config.py            # Configuration
├── scrape.py            # Main scraping script
├── generate.py          # Site generation script
├── deploy.py            # Deployment script
└── requirements.txt     # Python dependencies
```

## MariaDB Setup
```sql
-- Create database and user
CREATE DATABASE power_tracker;
CREATE USER 'tracker'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON power_tracker.* TO 'tracker'@'localhost';
FLUSH PRIVILEGES;
```