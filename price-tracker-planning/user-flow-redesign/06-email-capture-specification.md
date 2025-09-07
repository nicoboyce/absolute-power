# Email Capture System - Detailed Specification  

## Section Overview
**Purpose**: Convert engaged users to email subscribers through value-first, contextual signup
**Position**: After confidence building, as sticky element + dedicated section
**Success Metric**: >15% email signup rate (vs current ~3%)

## Dual Implementation Strategy

### 1. Sticky Bottom Bar (Always Visible)
```
┌─────────────────────────────────────────────────────────────────┐
│ 💡 Track prices on your shortlist • Save £127 avg per person   │
│ [Your Products: Anker C800, Jackery 1000] [Email] [Get Alerts] │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Dedicated Signup Section
```
┌─────────────────────────────────────────────────────────────────┐
│                    VALUE REINFORCEMENT                          │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐   │
│  │  Your Potential │  │           Signup Form              │   │
│  │    Savings      │  │                                     │   │
│  │                 │  │  Email: [________________]         │   │
│  │  Products: 2    │  │                                     │   │
│  │  Value: £1,398  │  │  Track These Products:              │   │
│  │  Avg Drop: 18%  │  │  ☑️ Anker SOLIX C800 (£599)       │   │
│  │  You Save: £251 │  │  ☑️ Jackery 1000 v2 (£799)        │   │
│  │                 │  │  ☐ Add EcoFlow DELTA 2             │   │
│  │  Recent Deals:  │  │                                     │   │
│  │  💰 Anker: -14% │  │  Alert Preferences:                │   │
│  │  ⚡ Jackery:-11%│  │  ☑️ Price drops 10%+               │   │
│  │                 │  │  ☐ New product launches            │   │
│  └─────────────────┘  │                                     │   │
│                       │  [START TRACKING PRICES] 🔔        │   │
│                       │                                     │   │
│                       │  Free • Unsubscribe anytime        │   │
│                       └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Dynamic Value Proposition Generation

### Personalised Headlines by User Journey
```javascript
const valuePropositions = {
  emergency_backup: {
    headline: "Track Your Emergency Backup Shortlist",
    subheadline: "Get notified when critical home backup power goes on sale",
    urgency: "Don't wait for the next power cut to overpay"
  },
  camping_outdoor: {
    headline: "Track Your Camping Power Shortlist", 
    subheadline: "Save money on portable power for your adventures",
    urgency: "Camping season deals happen fast - don't miss out"
  },
  work_mobile: {
    headline: "Track Your Mobile Office Power List",
    subheadline: "Professional power solutions at the best prices",
    urgency: "Business equipment deals are time-sensitive"
  },
  off_grid: {
    headline: "Track Your Off-Grid Power System",
    subheadline: "High-capacity systems deserve high-value deals",
    urgency: "Premium power station deals are rare - catch them"
  }
};
```

### Dynamic Savings Calculation
```javascript
function calculatePotentialSavings(userProducts) {
  const totalValue = userProducts.reduce((sum, product) => sum + product.currentPrice, 0);
  const historicalSavings = userProducts.map(product => 
    Math.max(...product.priceHistory) - Math.min(...product.priceHistory)
  );
  const avgSavingsRate = historicalSavings.reduce((sum, saving) => sum + saving, 0) / totalValue;
  
  return {
    totalValue,
    potentialSaving: Math.round(totalValue * avgSavingsRate),
    avgSavingsRate: Math.round(avgSavingsRate * 100)
  };
}
```

## Sticky Bottom Bar Implementation

### Dynamic Content Based on User Behaviour
```javascript
class StickyEmailBar {
  constructor() {
    this.userProducts = []; // Products user has viewed/compared
    this.visible = false;
    this.trigger = 'viewed_recommendations'; // When to show
  }
  
  updateContent() {
    if (this.userProducts.length === 0) {
      this.content = "💡 Track power station deals • 2,400+ users saving money";
    } else {
      const savings = calculatePotentialSavings(this.userProducts);
      this.content = `💡 Track your ${this.userProducts.length} products • Save £${savings.potentialSaving} on average`;
    }
  }
  
  show() {
    this.visible = true;
    this.element.classList.add('slide-up');
  }
}
```

### Trigger Conditions
```javascript
const stickyBarTriggers = {
  immediate: false,
  scroll_depth: 60, // Show after 60% page scroll
  product_views: 2,  // Show after viewing 2+ products
  comparison_started: true, // Show when user compares products
  time_threshold: 120000, // Show after 2 minutes on site
  exit_intent: true // Show on exit intent (desktop)
};
```

## Main Signup Form Design

### Two-Column Desktop Layout
```
Left Column (40%):              Right Column (60%):
├─ Savings Calculator           ├─ Email Input Field
├─ Recent Deals Examples        ├─ Product Selection (pre-populated)
├─ Social Proof Counter         ├─ Alert Preferences
├─ Community Savings Stats      ├─ Primary CTA Button
└─ Trust Indicators             └─ Privacy Assurance
```

### Form Field Specifications

#### Email Input
```html
<div class="email-field">
  <label for="email">Email Address</label>
  <input 
    type="email" 
    id="email" 
    name="email"
    placeholder="your@email.com"
    required
    autocomplete="email"
    class="form-input"
  />
  <div class="validation-message" id="email-validation"></div>
</div>
```

**Validation Logic**:
```javascript
function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValid = regex.test(email);
  const domain = email.split('@')[1];
  
  // Additional checks
  const isDisposableEmail = checkDisposableEmailList(domain);
  const isTypo = checkCommonTypos(domain); // gmail.co.uk -> gmail.com
  
  return { isValid, isDisposableEmail, isTypo, suggestion: getTypoSuggestion(domain) };
}
```

#### Product Selection (Pre-populated)
```html
<div class="product-selection">
  <label>Products to Track</label>
  <div class="product-checkboxes">
    <!-- Dynamically populated based on user behaviour -->
    <label class="product-checkbox">
      <input type="checkbox" value="anker-c800" checked />
      <span class="checkmark"></span>
      Anker SOLIX C800 (£599)
      <span class="price-change">-14% last month</span>
    </label>
  </div>
  <button type="button" class="add-more-products">Add more products</button>
</div>
```

#### Alert Preferences
```html
<div class="alert-preferences">
  <label>Alert Preferences</label>
  <div class="preference-checkboxes">
    <label>
      <input type="checkbox" value="price_drops" checked />
      Price drops by 10% or more
    </label>
    <label>
      <input type="checkbox" value="special_offers" checked />
      Special offers & seasonal deals
    </label>
    <label>
      <input type="checkbox" value="new_products" />
      New product launches & reviews
    </label>
    <label>
      <input type="checkbox" value="educational" />
      Power station guides & tips
    </label>
  </div>
</div>
```

## Incentive Strategy

### Immediate Value Delivery
```javascript
const signupIncentives = {
  immediate: [
    "Power Station Buyer's Guide (24-page PDF)",
    "Capacity Calculator Spreadsheet", 
    "Emergency Preparedness Checklist",
    "Access to exclusive discount codes"
  ],
  
  tiered_by_products: {
    single_product: ["Buyer's guide", "Price alerts"],
    two_products: ["Guide", "Calculator", "First-time discount"],
    three_plus: ["Everything", "Phone support priority", "Early sale access"]
  },
  
  use_case_specific: {
    emergency_backup: "Emergency Power Planning Kit",
    camping_outdoor: "Camping Power Setup Guide", 
    work_mobile: "Mobile Office Power Guide",
    off_grid: "Off-Grid System Design Templates"
  }
};
```

### Exclusive Offers
```javascript
const exclusiveOffers = {
  first_time_signup: {
    discount: "£50 off your first purchase over £500",
    code: "WELCOME50",
    expiry: "14 days"
  },
  
  multiple_products: {
    discount: "5% extra off when 3+ tracked products go on sale",
    code: "TRACKER5",
    conditions: "Applies automatically"
  },
  
  seasonal: {
    winter: "Emergency preparedness bundle discount",
    summer: "Camping power combo deals",
    black_friday: "Exclusive early access to BF deals"
  }
};
```

## Social Proof Integration

### Live Counters (Real-time Updates)
```javascript
class SocialProofCounter {
  constructor() {
    this.subscribers = 2400; // Base count
    this.recentSignups = this.getRecentSignupCount();
    this.totalSavings = this.calculateCommunitySavings();
  }
  
  updateDisplay() {
    document.getElementById('subscriber-count').textContent = 
      `${this.subscribers.toLocaleString()} people tracking deals`;
    
    document.getElementById('recent-activity').textContent = 
      `+${this.recentSignups} joined in the last hour`;
      
    document.getElementById('community-savings').textContent = 
      `£${this.totalSavings.toLocaleString()} saved by our community last month`;
  }
  
  // Update every 30 seconds with realistic increments
  startLiveUpdates() {
    setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance of increment
        this.subscribers += Math.floor(Math.random() * 3) + 1;
        this.updateDisplay();
      }
    }, 30000);
  }
}
```

### Recent Activity Feed
```javascript
const recentActivity = [
  "Sarah from Bristol saved £89 on Anker SOLIX C800",
  "Mike from Edinburgh joined 12 minutes ago", 
  "Deal alert: Jackery 1000 v2 now £799 (was £899)",
  "Emma from Cardiff tracking 3 power stations"
];

// Rotate through activity every 10 seconds
function showActivityFeed() {
  let index = 0;
  setInterval(() => {
    document.getElementById('activity-feed').textContent = recentActivity[index];
    index = (index + 1) % recentActivity.length;
  }, 10000);
}
```

## CTA Button Optimisation

### Button Text A/B Testing
```javascript
const ctaVariants = {
  control: "START TRACKING PRICES 🔔",
  urgency: "GET DEAL ALERTS NOW ⚡",
  value: "SAVE MONEY ON POWER STATIONS 💰", 
  personal: "TRACK MY SHORTLIST 📋",
  community: "JOIN 2,400+ SMART BUYERS 👥"
};
```

### Button Design Specifications
```css
.primary-signup-cta {
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  font-size: 18px;
  font-weight: 700;
  padding: 16px 32px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  width: 100%;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.primary-signup-cta:hover {
  background: linear-gradient(135deg, #229954 0%, #27ae60 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
}

.primary-signup-cta:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
}
```

## Privacy & Trust Assurance

### GDPR Compliance Elements
```html
<div class="privacy-assurance">
  <p class="trust-indicators">
    ✅ Free forever • ✅ Unsubscribe anytime • ✅ UK GDPR compliant
  </p>
  <p class="privacy-link">
    We respect your privacy. Read our 
    <a href="/privacy-policy">Privacy Policy</a>
  </p>
  <p class="data-usage">
    We'll only email you about price drops and power station deals. 
    No spam, no selling your data.
  </p>
</div>
```

### Data Security Messaging
```javascript
const trustMessages = [
  "🔒 Your email is encrypted and secure",
  "🇬🇧 Data stored in UK servers only", 
  "❌ Never shared with third parties",
  "📧 Average 2 emails per week maximum",
  "⚡ Instant unsubscribe with one click"
];
```

## Mobile Optimisation

### Mobile-First Form Design
```css
@media (max-width: 768px) {
  .signup-form {
    padding: 16px;
    margin: 0 auto;
  }
  
  .form-input {
    font-size: 16px; /* Prevents zoom on iOS */
    padding: 12px;
    border-radius: 4px;
  }
  
  .primary-signup-cta {
    padding: 16px 24px;
    font-size: 16px;
    margin-top: 16px;
  }
  
  .product-checkboxes {
    max-height: 200px;
    overflow-y: auto;
  }
}
```

### Touch-Optimised Interactions
- Minimum 44px touch targets
- Proper input types for mobile keyboards
- Swipe-friendly product selection
- Auto-scroll to form after CTA click

## Email Onboarding Sequence

### Immediate Confirmation Email
```javascript
const confirmationEmail = {
  subject: "You're now tracking {{product_count}} power stations ⚡",
  
  content: `
    Hi there!
    
    Great news - you're now tracking {{product_list}} for price drops.
    
    Here's what happens next:
    • We monitor prices 24/7 across all major UK retailers
    • You'll get instant alerts when prices drop by 10% or more
    • Expected next deal: {{estimated_deal_timeframe}}
    
    As promised, here are your exclusive resources:
    📋 Power Station Buyer's Guide (attached)
    🧮 Capacity Calculator Spreadsheet (attached)
    💰 £50 welcome discount code: WELCOME50
    
    Questions? Just reply to this email.
    
    Happy power hunting!
    The Power Station Team
  `,
  
  attachments: ["buyers-guide.pdf", "calculator.xlsx"]
};
```

### Email Sequence Strategy (First 30 Days)
```javascript
const emailSequence = [
  {
    day: 0,
    type: "confirmation",
    subject: "You're now tracking power stations ⚡",
    purpose: "Confirm subscription, deliver promised resources"
  },
  {
    day: 3,
    type: "education",
    subject: "Quick question about your power needs", 
    purpose: "Gather additional data, provide personalised tips"
  },
  {
    day: 7,
    type: "value",
    subject: "Your first price update + exclusive offer",
    purpose: "Show system working, offer exclusive discount"
  },
  {
    day: 14,
    type: "social_proof",
    subject: "How Sarah saved £127 on her camping setup",
    purpose: "Social proof, success story, engagement"
  },
  {
    day: 30,
    type: "feedback",
    subject: "How are we doing? (30-second survey)",
    purpose: "Feedback collection, engagement measurement"
  }
];
```

This email capture system transforms passive browsing into active engagement through personalised value delivery, creating a high-quality subscriber base of genuinely interested prospects.