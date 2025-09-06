# Price Tracker Project Planning

Multi-category price comparison platform following the PCPartPicker model.

## Project Overview

Template-based system for tracking prices across different product categories. Core focus on essential business features: price tracking, notifications, and affiliate revenue.

## Phase Structure

### Essential Phase (MVP)
- Product database with basic info
- Price scraping from 2-3 retailers
- Price history storage
- Basic price comparison page
- Email price alerts
- Affiliate link insertion
- Simple admin panel

### Future Phases
- Advanced filtering/search
- User accounts and wishlists
- Historical price charts
- Mobile app
- API for third parties
- Social features
- Advanced analytics

## Implementation Components (Build Order)

1. [Infrastructure](./07-infrastructure.md) - *Set up hosting, database, basic services*
2. [Data Structure & Database](./01-data-structure.md) - *Core data models and relationships*
3. [Admin Panel](./06-admin-panel.md) - *Product/retailer management interface*
4. [Price Scraping System](./02-price-scraping.md) - *Data collection backbone*
5. [Frontend Interface](./05-frontend.md) - *Public-facing comparison pages*
6. [Affiliate System](./04-affiliate-system.md) - *Revenue generation*
7. [Price Tracking & Alerts](./03-price-alerts.md) - *User value and retention*

## Status

**Planning Complete** - All major technology decisions made:
- Raspberry Pi + static hosting architecture
- Python + BeautifulSoup scraping  
- JSON files for products, MariaDB for prices
- Python + Jinja2 for site generation
- Comprehensive logging and monitoring setup

**Next Phase**: Development implementation on Raspberry Pi

## Additional Documentation

- [Setup Commands](./setup-commands.md) - Pi installation steps
- [Database Schema](./database.sql) - MariaDB table structure
- [Affiliate Programs Research](./affiliate-programs-research.md) - Power station programs
- [All Niche Affiliate Programs](./all-niche-affiliate-programs.md) - Complete research across all categories
- [Future Categories](./future-categories.md) - Multi-domain expansion plan