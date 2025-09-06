# Data Structure & Database

## Requirements

### Product Schema
- Flexible structure to handle any product category
- Basic product information (name, brand, model)
- Category-specific attributes as flexible data
- Unique identifiers and slugs
- Timestamps for creation/updates

### Retailer Management
- Store retailer information
- Handle retailer-specific product URLs
- Track retailer reliability and scraping success rates

### Price History
- Store all historical price data
- Track price changes over time
- Associate prices with specific retailers and timestamps
- Handle currency and regional pricing

### User Email Tracking
- Store email subscriptions
- Link users to specific products they're tracking
- Handle unsubscribe tokens
- Track notification history

## Decisions Log

**Email Collection**: Simple file-based system
- HTML form writes to CSV/text file
- Python script reads file for processing
- No backend database needed for MVP

**Product Data Storage**: Mixed approach
- MariaDB for price history and time-series data
- JSON files for product information and specifications
- Best of both worlds: scalable pricing data + simple product management

**Product Identification**: Amazon ASIN + fuzzy matching
- Use Amazon ASIN as primary product identifier
- Fuzzy match other retailers by name/brand
- Amazon has most comprehensive product data
- Other retailers mapped to ASIN where possible

**Power Station JSON Schema**: Comprehensive spec tracking
```json
{
  "id": "ecoflow-delta-pro-3",
  "name": "EcoFlow DELTA Pro 3", 
  "brand": "EcoFlow",
  "model": "DELTA Pro 3",
  "category": "power-station",
  "specs": {
    "capacity": "4096Wh",
    "ac_output": {
      "outlets": 5,
      "continuous": "4000W",
      "surge": "8000W",
      "x_boost": "6000W"
    },
    "chemistry": "LFP",
    "inputs": {
      "solar": {
        "max_power": "2600W",
        "hpv_range": "30-150V/15A (1600W max)",
        "lpv_range": "11-60V/20A (1000W max)"
      },
      "ac_charging": "2900W (200-240V~12.5A)",
      "car_charging": ["12V 8A max", "48V 20A max"]
    },
    "outputs": {
      "ac": "5 outlets, 4000W max (8000W surge)", 
      "usb_a": "2x (5V 2.4A / 9V 2A / 12V 1.5A, 18W max)",
      "usb_c": "2x (5/9/12/15/20V 5A, 100W max)",
      "dc12v": "12.6V/30A 378W total (DC5521×1 5A max, Anderson×1 30A max)"
    },
    "connectivity": ["Wi-Fi 2.4GHz", "Bluetooth", "CAN"],
    "features": ["X-Boost", "expandable", "supports 2x extra batteries"],
    "dimensions": "693×341×410mm",
    "weight": "51.5kg",
    "performance": {
      "cycle_life": "4000 cycles to 80%",
      "operating_temp": {
        "discharge": "-10°C to 45°C", 
        "charge": "0°C to 45°C"
      },
      "charging_times": {
        "ac": "1.7 hrs",
        "car": "12 hrs", 
        "solar_100w": {"1_panel": "15 hrs", "2_panels": "8 hrs"},
        "solar_200w": {"1_panel": "7.5 hrs", "2_panels": "3.8 hrs"}
      }
    },
    "warranty": "3+2 years"
  },
  "retailers": {
    "currys": {"url": "...", "affiliate_url": "..."},
    "argos": {"url": "...", "affiliate_url": "..."}
  }
}

## Implementation Details

### File Structure
```
/home/pi/power-tracker/data/products/
├── power-stations/
│   ├── ecoflow-delta-pro-3.json
│   ├── jackery-explorer-1000-v2.json
│   └── anker-solix-c800x.json
└── categories.json  # Category metadata
```

### MariaDB Schema Implementation
```sql
-- Price history with indexes for performance
CREATE TABLE price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    retailer VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    in_stock BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url TEXT,
    
    INDEX idx_product_retailer (product_id, retailer),
    INDEX idx_scraped_at (scraped_at),
    INDEX idx_product_time (product_id, scraped_at)
);

-- View for latest prices (performance optimized)
CREATE VIEW latest_prices AS
SELECT 
    product_id,
    retailer,
    price,
    currency,
    in_stock,
    scraped_at,
    url,
    RANK() OVER (PARTITION BY product_id, retailer ORDER BY scraped_at DESC) as rn
FROM price_history
WHERE rn = 1;
```

### Email Collection System
```html
<!-- Simple HTML form -->
<form action="mailto:alerts@domain.com" method="post" enctype="text/plain">
    <input type="email" name="email" required>
    <input type="hidden" name="product_id" value="ecoflow-delta-pro-3">
    <input type="hidden" name="price_threshold" value="">
    <button type="submit">Get Price Alerts</button>
</form>
```

### Product JSON Validation Schema
```python
# JSON Schema validation
POWER_STATION_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "brand", "model", "category", "specs"],
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z0-9-]+$"},
        "name": {"type": "string"},
        "brand": {"type": "string"},
        "model": {"type": "string"},
        "category": {"type": "string", "enum": ["power-station"]},
        "specs": {
            "type": "object",
            "required": ["capacity", "chemistry", "weight"],
            "properties": {
                "capacity": {"type": "string", "pattern": "\\d+Wh$"},
                "chemistry": {"type": "string", "enum": ["LiFePO4", "LFP", "Li-ion"]},
                "weight": {"type": "string", "pattern": "\\d+(\\.\\d+)?kg$"}
            }
        },
        "retailers": {
            "type": "object",
            "patternProperties": {
                "^[a-z_]+$": {
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "format": "uri"},
                        "affiliate_url": {"type": "string", "format": "uri"}
                    }
                }
            }
        }
    }
}
```

### Data Management Scripts
**add_product.py** - CLI tool for adding new products:
```python
# Usage: python add_product.py --brand EcoFlow --model "Delta Pro 3" --capacity 4096Wh
```

**update_retailers.py** - Bulk retailer URL updates:
```python
# Updates all products with new retailer URLs
# Usage: python update_retailers.py --retailer currys --base-url "https://currys.co.uk"
```

**validate_products.py** - Data integrity checking:
```python
# Validates all JSON files against schema
# Checks for duplicate IDs, missing required fields
```

### Product ID Generation Rules
```python
def generate_product_id(brand, model):
    """Generate consistent product IDs"""
    # Convert to lowercase, remove special chars, join with hyphens
    brand_clean = re.sub(r'[^a-z0-9]', '', brand.lower())
    model_clean = re.sub(r'[^a-z0-9]', '-', model.lower())
    return f"{brand_clean}-{model_clean}"

# Examples:
# "EcoFlow DELTA Pro 3" → "ecoflow-delta-pro-3"
# "Anker SOLIX C800X Plus" → "anker-solix-c800x-plus"
```

### Multi-Category Schema Support
```python
# categories.json
{
    "power-stations": {
        "name": "Power Stations",
        "schema_version": "1.0",
        "required_specs": ["capacity", "chemistry", "weight"],
        "optional_specs": ["outputs", "inputs", "features"],
        "url_slug": "power-stations"
    }
}
```

### Retailer Configuration
```python
# retailers.json
{
    "ecoflow": {
        "name": "EcoFlow UK",
        "base_url": "https://uk.ecoflow.com",
        "affiliate_program": "direct",
        "commission_rate": "5%",
        "scraping_enabled": true,
        "selectors": {
            "price": ".price-current",
            "availability": ".stock-status"
        }
    }
}
```

## Resolved Implementation Questions

**Product Variations Handling**: 
- Each significant variation gets its own JSON file
- Use model suffixes: `jackery-explorer-1000-v2.json`
- Colour/minor variations noted in `features` array

**Currency Handling**: 
- GBP only for UK prototype
- Price stored as DECIMAL(10,2) for accuracy
- Currency field ready for future expansion

**Data Retention**: 
- Price history: Keep all data (storage cheap, analysis valuable)
- Log files: 30-day rotation for daily summaries
- Email subscriptions: Keep until unsubscribe

**Product Matching**: 
- Manual curation for prototype (quality over automation)
- Fuzzy matching as fallback for new retailers
- Amazon ASIN as canonical identifier where available