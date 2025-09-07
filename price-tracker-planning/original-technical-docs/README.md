# Original Technical Documentation

## Overview

Documentation for the current technical implementation of the power station price tracking system. These documents describe the existing working system including scraping, data storage, alerts, and affiliate tracking.

## System Architecture

Current implementation built with:
- **Python**: Web scraping and backend processing
- **PostgreSQL**: Product and price data storage
- **Static HTML/CSS/JS**: Frontend presentation
- **Raspberry Pi**: Deployment target
- **Automated scraping**: Scheduled price updates

## Documentation Structure

### 1. **[01-data-structure.md](01-data-structure.md)**
Database schema and data models for the current system.

**Contents**:
- Product database structure
- Price history tracking
- Retailer information storage
- Data relationships and constraints

### 2. **[02-price-scraping.md](02-price-scraping.md)**
Web scraping implementation for price collection.

**Contents**:
- Scraper architecture and design
- Retailer-specific implementations
- Error handling and validation
- Scheduling and automation

### 3. **[03-price-alerts.md](03-price-alerts.md)**
Alert system for price notifications.

**Contents**:
- Email alert system
- Threshold management
- User subscription handling
- Delivery mechanisms

### 4. **[04-affiliate-system.md](04-affiliate-system.md)**
Revenue tracking and affiliate integration.

**Contents**:
- Affiliate link management
- Revenue attribution
- Commission tracking
- Reporting systems

### 5. **[05-frontend.md](05-frontend.md)**
Current UI implementation and static site generation.

**Contents**:
- HTML template system
- CSS styling approach
- JavaScript functionality
- Static site generation process

### 6. **[06-admin-panel.md](06-admin-panel.md)**
Administrative interface specifications.

**Contents**:
- Product management interface
- Scraper monitoring tools
- Data validation systems
- System health monitoring

### 7. **[07-infrastructure.md](07-infrastructure.md)**
Deployment and hosting configuration.

**Contents**:
- Raspberry Pi setup
- Automated deployment
- System monitoring
- Backup and recovery

## Current System Status

### Working Components
- ✅ Web scraping for major UK retailers
- ✅ Price history tracking and storage
- ✅ Static website generation
- ✅ Automated deployment to Pi
- ✅ Basic email alert system

### Known Limitations
- ⚠️ Low conversion rate (~3%)
- ⚠️ No user qualification system
- ⚠️ Limited personalisation
- ⚠️ Basic analytics tracking
- ⚠️ No A/B testing capability

## Maintenance Notes

This system is currently production-ready and serving users. Any changes should:

1. **Maintain backwards compatibility** with existing data
2. **Preserve scraping functionality** that currently works
3. **Keep deployment process** intact for Pi hosting
4. **Maintain existing affiliate links** for revenue
5. **Preserve email alert functionality** for current users

## Integration with New Design

The user flow redesign (see `../user-flow-redesign/`) builds upon this foundation by:

- **Keeping existing scraping system** for price data
- **Enhancing database schema** for user qualification
- **Adding personalisation layer** on top of current data
- **Maintaining Pi deployment** with enhanced frontend
- **Preserving affiliate tracking** with improved attribution

These documents serve as the technical foundation for understanding what currently works and what needs enhancement in the redesigned user experience.