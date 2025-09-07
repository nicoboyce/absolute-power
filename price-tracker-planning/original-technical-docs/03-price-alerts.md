# Price Tracking & Alerts

## Requirements

### Price Analysis
- Compare current prices against historical data
- Identify significant price drops (percentage or absolute)
- Calculate price trends and patterns
- Handle temporary price spikes vs genuine drops

### Alert Generation
- Generate email notifications for price drops
- Customisable alert thresholds per user/product
- Batch notifications to avoid spam
- Include relevant product information and links

### Email Management
- HTML email templates with product images
- Unsubscribe links and preference management
- Track email delivery and open rates
- Handle bounces and invalid email addresses

### Alert Logic
- Prevent duplicate alerts for same price drop
- Cooldown periods between alerts
- Different alert types (instant, daily digest, weekly summary)

## Decisions Log

*No decisions made yet - awaiting technology selection*

## Implementation Details

### Email Collection (Simple)
```html
<!-- Minimal signup form -->
<form class="price-alert-form">
    <input type="email" placeholder="your@email.com" required>
    <input type="hidden" name="product" value="ecoflow-delta-pro-3">
    <input type="number" name="threshold" placeholder="Alert me when under £___">
    <button type="submit">Get Price Alerts</button>
</form>
```

### File-Based Storage (MVP)
```csv
# price_alerts.csv
email,product_id,threshold,date_added,active
user@email.com,ecoflow-delta-pro-3,3500,2025-01-15,true
user2@email.com,jackery-explorer-1000-v2,800,2025-01-16,true
```

### Alert Processing Logic
```python
# check_alerts.py (runs after each scrape)
def process_price_alerts():
    alerts = load_active_alerts()
    latest_prices = get_latest_prices()
    
    for alert in alerts:
        current_price = latest_prices.get(alert['product_id'])
        if current_price and current_price <= alert['threshold']:
            send_price_alert(alert, current_price)
            log_alert_sent(alert['email'], alert['product_id'])
```

### Email Template (Simple)
```html
<!-- Basic HTML email -->
<h2>Price Alert: {{product_name}}</h2>
<p>Great news! The price has dropped to <strong>£{{current_price}}</strong></p>
<p>Your alert threshold: £{{threshold}}</p>

<!-- Retailer links with affiliate codes -->
<div class="retailer-links">
    <a href="{{ecoflow_link}}">EcoFlow UK - £{{ecoflow_price}} <span class="affiliate">AD</span></a>
    <a href="{{jackery_link}}">Jackery UK - £{{jackery_price}} <span class="affiliate">AD</span></a>
</div>

<p><small><a href="{{unsubscribe_link}}">Unsubscribe</a></small></p>
```

### Notification Alternatives (Future)
```python
# WhatsApp integration (when ready)
def send_whatsapp_alert(phone, product, price):
    message = f"Price Alert: {product} now £{price}"
    whatsapp_api.send_message(phone, message)

# Discord/Telegram webhooks
def send_discord_alert(webhook_url, product, price):
    payload = {
        "content": f"@here Price drop: {product} - £{price}",
        "embeds": [product_embed]
    }
    requests.post(webhook_url, json=payload)
```

### Alert Frequency Management
```python
# Prevent spam - cooldown periods
COOLDOWN_HOURS = 24

def should_send_alert(email, product_id):
    last_sent = get_last_alert_time(email, product_id)
    if last_sent and (now() - last_sent) < COOLDOWN_HOURS:
        return False
    return True
```

### Unsubscribe System
```python
# Generate unsubscribe tokens
def generate_unsubscribe_link(email, product_id):
    token = hashlib.sha256(f"{email}:{product_id}:{SECRET}".encode()).hexdigest()[:16]
    return f"https://domain.com/unsubscribe?token={token}"

# Handle unsubscribe requests (simple)
def handle_unsubscribe(token):
    # Validate token and mark alert as inactive
    update_alert_status(token, active=False)
```

## Questions to Resolve

- What constitutes a "significant" price drop?
- How to handle flash sales vs permanent price reductions?
- Email delivery frequency to avoid overwhelming users?
- Integration with affiliate links in email content?