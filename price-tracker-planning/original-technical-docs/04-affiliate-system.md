# Affiliate System

## Requirements

### Link Management
- Store affiliate URLs for each retailer
- Dynamic link generation with tracking parameters
- Handle different affiliate program structures
- Fallback to direct links when affiliate unavailable

### Revenue Tracking
- Track clicks from site to retailers
- Monitor conversion rates and commissions
- Generate revenue reports by retailer/product
- Handle different commission structures

### Link Insertion
- Automatically replace product URLs with affiliate links
- Maintain link integrity and user experience
- Handle mobile vs desktop link differences
- Cache affiliate links for performance

### Compliance
- Proper affiliate disclosure statements
- Handle different regional affiliate requirements
- Track and report for tax purposes

## Decisions Log

*No decisions made yet - awaiting technology selection*

## Implementation Details

### Affiliate Link Management
```python
# retailers.json configuration
{
    "ecoflow": {
        "name": "EcoFlow UK",
        "affiliate_program": "direct",
        "commission_rate": "5%",
        "link_format": "https://uk.ecoflow.com/products/{product_slug}?ref=AFFILIATE_ID",
        "tracking_enabled": true
    },
    "jackery": {
        "affiliate_program": "direct",
        "commission_rate": "8%",
        "link_format": "https://uk.jackery.com/{product_path}?utm_source=affiliate&utm_campaign=CAMPAIGN_ID"
    }
}
```

### Dynamic Link Generation
```python
def generate_affiliate_link(retailer, product_id, base_url):
    """Generate affiliate link with tracking parameters"""
    config = load_retailer_config(retailer)
    
    # Add tracking parameters
    tracking_params = {
        'utm_source': 'price_tracker',
        'utm_medium': 'affiliate',
        'utm_campaign': f'power_stations_{product_id}',
        'ref': config['affiliate_id']
    }
    
    return append_tracking_params(base_url, tracking_params)
```

### Revenue Tracking System
```python
# Click tracking (client-side)
<script>
function trackClick(retailer, product, price) {
    // Send tracking event
    fetch('/track', {
        method: 'POST',
        body: JSON.stringify({
            retailer: retailer,
            product: product,
            price: price,
            timestamp: Date.now()
        })
    });
}
</script>

# Server-side logging
click_log.csv:
timestamp,product_id,retailer,price_shown,user_ip_hash
```

### Commission Calculation
```python
# Revenue projections
def calculate_potential_revenue(clicks, conversion_rate, avg_order_value, commission_rate):
    conversions = clicks * conversion_rate
    revenue = conversions * avg_order_value * commission_rate
    return revenue

# Example for EcoFlow:
# 100 clicks/month × 2% conversion × £2000 AOV × 5% commission = £200/month
```

### Compliance Implementation
```html
<!-- Affiliate disclosure -->
<div class="affiliate-disclosure">
    <p>This site contains affiliate links. We may earn a commission when you make a purchase through these links at no additional cost to you.</p>
</div>

<!-- Per-link disclosure -->
<a href="affiliate_link" class="affiliate-link" title="Affiliate Link">
    EcoFlow UK - £3,999 
    <span class="affiliate-badge">AD</span>
</a>
```

## Questions to Resolve

- Which affiliate networks to prioritise?
- How to handle affiliate link expiration?
- Backup strategies when affiliate programs change?
- Integration with email notifications?