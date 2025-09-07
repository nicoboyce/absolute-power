# Technical Implementation Guide

## Overview
Complete technical specification for transforming the current price tracker into a conversion-optimised user flow with personalised recommendations and email capture.

## Frontend Architecture

### Technology Stack
```
Base Technologies:
├─ HTML5 with semantic structure
├─ CSS3 with custom properties (CSS variables)
├─ Vanilla JavaScript (ES6+) for core functionality
├─ Progressive Web App capabilities
└─ Mobile-first responsive design

Performance Requirements:
├─ First Contentful Paint: <1.5s
├─ Largest Contentful Paint: <2.5s  
├─ Cumulative Layout Shift: <0.1
├─ Time to Interactive: <3.0s
└─ Mobile PageSpeed Score: >90
```

### Core JavaScript Classes

#### 1. Hero Animation Controller
```javascript
class HeroAnimationController {
  constructor(container) {
    this.container = container;
    this.sequences = ['power-cut', 'solution', 'relief'];
    this.currentSequence = 0;
    this.isPlaying = true;
    this.duration = 8000; // 8 seconds total
    this.loops = 3; // Auto-pause after 3 loops
    this.currentLoop = 0;
  }
  
  init() {
    this.loadSequences();
    this.setupControls();
    this.startAnimation();
    this.trackEngagement();
  }
  
  startAnimation() {
    if (!this.isPlaying || this.currentLoop >= this.loops) return;
    
    const sequence = this.sequences[this.currentSequence];
    this.playSequence(sequence);
    
    setTimeout(() => {
      this.currentSequence = (this.currentSequence + 1) % this.sequences.length;
      if (this.currentSequence === 0) this.currentLoop++;
      this.startAnimation();
    }, this.duration / this.sequences.length);
  }
  
  playSequence(sequenceName) {
    this.container.className = `hero-animation ${sequenceName}`;
    analytics.track('hero_animation_view', { sequence: sequenceName });
  }
  
  pause() {
    this.isPlaying = false;
    analytics.track('hero_animation_paused');
  }
  
  trackEngagement() {
    // Track how long users watch animation
    const startTime = Date.now();
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting && entry.target === this.container) {
          const watchTime = Date.now() - startTime;
          analytics.track('hero_animation_engagement', { watchTime });
        }
      });
    });
    observer.observe(this.container);
  }
}
```

#### 2. Use Case Selector
```javascript
class UseCaseSelector {
  constructor() {
    this.cards = document.querySelectorAll('.use-case-card');
    this.selectedCase = null;
    this.formData = {};
    this.progressIndicator = document.querySelector('.progress-indicator');
  }
  
  init() {
    this.attachEventListeners();
    this.trackCardViews();
  }
  
  attachEventListeners() {
    this.cards.forEach(card => {
      card.addEventListener('click', (e) => this.selectCard(e.currentTarget));
      card.addEventListener('mouseenter', (e) => this.trackHover(e.currentTarget));
    });
  }
  
  selectCard(cardElement) {
    const caseId = cardElement.dataset.useCase;
    
    // Visual state management
    this.cards.forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');
    
    // Show form
    this.showDetailsForm(caseId);
    
    // Track selection
    analytics.track('use_case_selected', {
      case: caseId,
      timeToSelect: Date.now() - this.pageLoadTime
    });
    
    this.selectedCase = caseId;
  }
  
  showDetailsForm(caseId) {
    const existingForm = document.querySelector('.use-case-form');
    if (existingForm) existingForm.remove();
    
    const formHTML = this.generateFormHTML(caseId);
    const cardElement = document.querySelector(`[data-use-case="${caseId}"]`);
    cardElement.insertAdjacentHTML('afterend', formHTML);
    
    this.attachFormListeners();
    this.smoothScrollToForm();
  }
  
  generateFormHTML(caseId) {
    const formConfig = this.getFormConfig(caseId);
    
    return `
      <div class="use-case-form" data-case="${caseId}">
        <h3>Tell us more about your ${formConfig.title} needs:</h3>
        ${formConfig.fields.map(field => this.renderField(field)).join('')}
        <button class="show-recommendations-btn" disabled>
          Show My Recommendations
        </button>
      </div>
    `;
  }
  
  getFormConfig(caseId) {
    const configs = {
      emergency_backup: {
        title: "emergency backup",
        fields: [
          {
            type: "slider",
            name: "duration",
            label: "How long are your typical power cuts?",
            min: 2,
            max: 48,
            unit: "hours"
          },
          {
            type: "checkbox-group",
            name: "priorities",
            label: "What's your priority?",
            options: [
              { value: "medical", label: "Medical equipment" },
              { value: "food", label: "Food preservation" },
              { value: "communication", label: "Communication" },
              { value: "work", label: "Work from home" }
            ]
          }
        ]
      },
      // ... other use cases
    };
    return configs[caseId];
  }
  
  validateForm() {
    const form = document.querySelector('.use-case-form');
    const requiredFields = form.querySelectorAll('[required]');
    const isValid = Array.from(requiredFields).every(field => {
      return field.type === 'checkbox' ? 
        form.querySelector(`input[name="${field.name}"]:checked`) : 
        field.value.trim() !== '';
    });
    
    document.querySelector('.show-recommendations-btn').disabled = !isValid;
    return isValid;
  }
}
```

#### 3. Recommendation Engine
```javascript
class RecommendationEngine {
  constructor(productDatabase) {
    this.products = productDatabase;
    this.userProfile = {};
    this.recommendations = [];
  }
  
  generateRecommendations(useCase, requirements) {
    // Filter products by use case compatibility
    const compatibleProducts = this.products.filter(product => 
      this.isCompatibleWithUseCase(product, useCase)
    );
    
    // Score products based on requirements
    const scoredProducts = compatibleProducts.map(product => ({
      ...product,
      score: this.calculateScore(product, requirements),
      reasoning: this.generateReasoning(product, useCase, requirements)
    }));
    
    // Sort by score and return top 5
    const topProducts = scoredProducts
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);
    
    // Assign recommendation tiers
    return this.assignTiers(topProducts, requirements);
  }
  
  calculateScore(product, requirements) {
    let score = 0;
    
    // Capacity match (40% weight)
    const capacityScore = this.calculateCapacityScore(product, requirements);
    score += capacityScore * 0.4;
    
    // Budget fit (30% weight)
    const budgetScore = this.calculateBudgetScore(product, requirements);
    score += budgetScore * 0.3;
    
    // Feature match (20% weight)  
    const featureScore = this.calculateFeatureScore(product, requirements);
    score += featureScore * 0.2;
    
    // Brand reliability (10% weight)
    score += product.brandScore * 0.1;
    
    return Math.min(score, 100); // Cap at 100
  }
  
  calculateCapacityScore(product, requirements) {
    const targetCapacity = this.calculateTargetCapacity(requirements);
    const ratio = product.capacity / targetCapacity;
    
    if (ratio >= 0.8 && ratio <= 1.2) return 100; // Perfect range
    if (ratio >= 0.6 && ratio <= 1.5) return 80;  // Good range
    if (ratio >= 0.4 && ratio <= 2.0) return 60;  // Acceptable
    return 30; // Poor fit
  }
  
  generateReasoning(product, useCase, requirements) {
    const reasons = [];
    
    // Add capacity reasoning
    const runtime = this.calculateRuntime(product, requirements.priorityDevices);
    reasons.push(`Powers your devices for ${runtime} hours`);
    
    // Add use-case specific benefits
    const useCaseBenefits = this.getUseCaseBenefits(product, useCase);
    reasons.push(...useCaseBenefits.slice(0, 2));
    
    return reasons;
  }
  
  assignTiers(products, requirements) {
    if (products.length === 0) return [];
    
    const budget = requirements.budget || 'mid';
    const tiers = {
      budget: products[products.length - 1], // Lowest price, good score
      recommended: products[0], // Highest score overall
      premium: products.find(p => p.price > requirements.budgetMax) || products[0]
    };
    
    return [
      { ...tiers.recommended, tier: 'recommended' },
      { ...tiers.budget, tier: 'budget' },
      { ...tiers.premium, tier: 'premium' }
    ].filter((item, index, arr) => 
      arr.findIndex(i => i.id === item.id) === index // Remove duplicates
    );
  }
}
```

#### 4. Email Capture System
```javascript
class EmailCaptureSystem {
  constructor() {
    this.stickyBar = document.querySelector('.sticky-email-bar');
    this.mainForm = document.querySelector('.email-signup-form');
    this.userProducts = JSON.parse(localStorage.getItem('userProducts') || '[]');
    this.isVisible = false;
  }
  
  init() {
    this.setupStickyBar();
    this.setupMainForm();
    this.trackUserProducts();
    this.setupExitIntent();
  }
  
  setupStickyBar() {
    // Show sticky bar based on user engagement
    const triggers = {
      scrollDepth: 60, // Show after 60% scroll
      productViews: 2,  // Show after viewing 2+ products
      timeThreshold: 120000 // Show after 2 minutes
    };
    
    let scrollTriggered = false;
    let timeTriggered = false;
    
    // Scroll trigger
    window.addEventListener('scroll', () => {
      if (scrollTriggered) return;
      
      const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      if (scrollPercent >= triggers.scrollDepth) {
        this.showStickyBar();
        scrollTriggered = true;
      }
    });
    
    // Time trigger
    setTimeout(() => {
      if (!this.isVisible && this.userProducts.length > 0) {
        this.showStickyBar();
        timeTriggered = true;
      }
    }, triggers.timeThreshold);
  }
  
  showStickyBar() {
    if (this.isVisible) return;
    
    this.updateStickyBarContent();
    this.stickyBar.classList.add('show');
    this.isVisible = true;
    
    analytics.track('sticky_bar_shown', {
      trigger: this.determineTrigger(),
      productsCount: this.userProducts.length
    });
  }
  
  updateStickyBarContent() {
    const content = this.stickyBar.querySelector('.content');
    
    if (this.userProducts.length === 0) {
      content.innerHTML = "💡 Track power station deals • 2,400+ users saving money";
    } else {
      const savings = this.calculatePotentialSavings();
      content.innerHTML = `💡 Track your ${this.userProducts.length} products • Save £${savings} average`;
    }
  }
  
  setupMainForm() {
    const form = this.mainForm;
    const emailInput = form.querySelector('input[type="email"]');
    const submitButton = form.querySelector('.submit-button');
    
    // Real-time validation
    emailInput.addEventListener('input', (e) => {
      this.validateEmail(e.target.value);
    });
    
    // Form submission
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.submitForm(new FormData(form));
    });
    
    // Pre-populate with user's products
    this.prePopulateForm();
  }
  
  validateEmail(email) {
    const validation = this.performEmailValidation(email);
    const input = document.querySelector('input[type="email"]');
    const message = document.querySelector('.validation-message');
    
    input.classList.remove('valid', 'invalid', 'warning');
    
    if (!validation.isValid && email.length > 0) {
      input.classList.add('invalid');
      message.textContent = 'Please enter a valid email address';
    } else if (validation.isTypo) {
      input.classList.add('warning');
      message.innerHTML = `Did you mean <button type="button" class="suggestion">${validation.suggestion}</button>?`;
    } else if (validation.isDisposable) {
      input.classList.add('warning');
      message.textContent = 'Temporary emails won\'t receive our alerts';
    } else if (email.length > 0) {
      input.classList.add('valid');
      message.textContent = '';
    }
    
    return validation.isValid && !validation.isDisposable;
  }
  
  async submitForm(formData) {
    const submitButton = document.querySelector('.submit-button');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.textContent = 'Setting up alerts...';
    submitButton.disabled = true;
    
    try {
      const response = await fetch('/api/email-signup', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      if (response.ok) {
        this.showSuccessState();
        analytics.track('email_signup_success', {
          productsTracked: formData.getAll('products').length,
          userCase: localStorage.getItem('selectedUseCase')
        });
      } else {
        throw new Error('Signup failed');
      }
    } catch (error) {
      this.showErrorState(error.message);
      analytics.track('email_signup_error', { error: error.message });
    } finally {
      submitButton.textContent = originalText;
      submitButton.disabled = false;
    }
  }
  
  showSuccessState() {
    const form = this.mainForm;
    form.innerHTML = `
      <div class="success-message">
        <div class="success-icon">✅</div>
        <h3>You're all set!</h3>
        <p>Check your email for your buyer's guide and welcome discount.</p>
        <p>We'll notify you the moment any of your tracked products go on sale.</p>
      </div>
    `;
  }
}
```

### Progressive Enhancement Strategy

#### Base Experience (No JavaScript)
```html
<!-- Fallback form that submits via POST -->
<form action="/signup" method="POST" class="email-signup-form">
  <div class="form-group">
    <label for="email">Email Address</label>
    <input type="email" name="email" required>
  </div>
  
  <div class="form-group">
    <label>Products to track:</label>
    <input type="hidden" name="products" value="anker-c800,jackery-1000">
    <p>Anker SOLIX C800, Jackery Explorer 1000 v2</p>
  </div>
  
  <button type="submit">Start Tracking Prices</button>
</form>
```

#### Enhanced Experience (JavaScript Enabled)
```javascript
// Progressive enhancement loader
class ProgressiveEnhancement {
  init() {
    // Test for required features
    if (this.hasRequiredFeatures()) {
      this.loadEnhancedFeatures();
    } else {
      this.fallbackToBasicExperience();
    }
  }
  
  hasRequiredFeatures() {
    return (
      'fetch' in window &&
      'Promise' in window &&
      'localStorage' in window &&
      'IntersectionObserver' in window
    );
  }
  
  loadEnhancedFeatures() {
    // Initialize enhanced components
    new HeroAnimationController(document.querySelector('.hero-animation')).init();
    new UseCaseSelector().init();
    new EmailCaptureSystem().init();
    
    // Load analytics
    this.initAnalytics();
  }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new ProgressiveEnhancement().init();
});
```

## Backend Implementation

### Database Schema
```sql
-- Products table
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  brand VARCHAR(100) NOT NULL,
  model VARCHAR(100),
  capacity_wh INTEGER NOT NULL,
  ac_output_w INTEGER,
  weight_kg DECIMAL(4,2),
  battery_type VARCHAR(50),
  solar_input_w INTEGER,
  cycle_life INTEGER,
  features JSONB, -- Flexible feature storage
  use_cases TEXT[], -- Array of compatible use cases
  brand_score INTEGER DEFAULT 50, -- Reliability score
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Price tracking
CREATE TABLE price_history (
  id SERIAL PRIMARY KEY,
  product_id INTEGER REFERENCES products(id),
  retailer VARCHAR(100) NOT NULL,
  price DECIMAL(8,2) NOT NULL,
  currency CHAR(3) DEFAULT 'GBP',
  url TEXT,
  in_stock BOOLEAN DEFAULT true,
  recorded_at TIMESTAMP DEFAULT NOW(),
  
  INDEX idx_product_retailer (product_id, retailer),
  INDEX idx_recorded_at (recorded_at)
);

-- Users and tracking
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT false,
  use_case VARCHAR(50),
  requirements JSONB,
  preferences JSONB,
  signup_source VARCHAR(100), -- Attribution tracking
  created_at TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP DEFAULT NOW(),
  unsubscribed BOOLEAN DEFAULT false
);

-- Price alerts
CREATE TABLE price_alerts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  product_id INTEGER REFERENCES products(id),
  threshold_type VARCHAR(20) DEFAULT 'percentage', -- percentage or absolute
  threshold_value DECIMAL(5,2), -- 10.00 for 10% or 50.00 for £50
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  last_triggered TIMESTAMP,
  
  UNIQUE(user_id, product_id)
);

-- Analytics events
CREATE TABLE analytics_events (
  id SERIAL PRIMARY KEY,
  user_session VARCHAR(100), -- Anonymous session tracking
  event_name VARCHAR(100) NOT NULL,
  event_properties JSONB,
  user_agent TEXT,
  ip_address INET,
  referrer TEXT,
  page_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  
  INDEX idx_event_name (event_name),
  INDEX idx_created_at (created_at),
  INDEX idx_user_session (user_session)
);
```

### API Endpoints

#### Product Recommendations API
```javascript
// POST /api/recommendations
app.post('/api/recommendations', async (req, res) => {
  const { useCase, requirements } = req.body;
  
  try {
    // Validate input
    const validation = validateRecommendationRequest(useCase, requirements);
    if (!validation.isValid) {
      return res.status(400).json({ error: validation.message });
    }
    
    // Generate recommendations
    const recommendations = await recommendationEngine.generate(useCase, requirements);
    
    // Track the request
    await analytics.track(req.sessionId, 'recommendations_requested', {
      useCase,
      requirementsHash: hashObject(requirements),
      recommendationCount: recommendations.length
    });
    
    res.json({
      success: true,
      recommendations,
      metadata: {
        generated_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 3600000).toISOString() // 1 hour
      }
    });
    
  } catch (error) {
    console.error('Recommendation error:', error);
    res.status(500).json({ error: 'Failed to generate recommendations' });
  }
});
```

#### Email Signup API
```javascript
// POST /api/email-signup
app.post('/api/email-signup', async (req, res) => {
  const { email, products, preferences, useCase, requirements } = req.body;
  
  try {
    // Validate email
    const emailValidation = await validateEmail(email);
    if (!emailValidation.isValid) {
      return res.status(400).json({ 
        error: 'Invalid email address',
        suggestion: emailValidation.suggestion 
      });
    }
    
    // Check for existing user
    let user = await User.findOne({ email });
    if (user && !user.unsubscribed) {
      return res.status(409).json({ 
        error: 'Email already subscribed',
        message: 'This email is already tracking products. Check your inbox for existing alerts.'
      });
    }
    
    // Create or update user
    user = await User.upsert({
      email,
      use_case: useCase,
      requirements,
      preferences,
      signup_source: req.get('Referer') || 'direct',
      email_verified: false,
      unsubscribed: false
    });
    
    // Set up price alerts
    const alertPromises = products.map(productId => 
      PriceAlert.upsert({
        user_id: user.id,
        product_id: productId,
        threshold_type: 'percentage',
        threshold_value: preferences.priceDropThreshold || 10.0,
        is_active: true
      })
    );
    
    await Promise.all(alertPromises);
    
    // Send welcome email
    await emailService.sendWelcomeEmail(user, products);
    
    // Track successful signup
    await analytics.track(req.sessionId, 'email_signup_success', {
      useCase,
      productsCount: products.length,
      hasRequirements: !!requirements
    });
    
    res.json({
      success: true,
      message: 'Successfully signed up for price alerts',
      user_id: user.id,
      alerts_count: products.length
    });
    
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({ error: 'Failed to process signup' });
  }
});
```

### Performance Optimisation

#### Caching Strategy
```javascript
const Redis = require('redis');
const redis = Redis.createClient();

// Cache recommendations
async function getCachedRecommendations(useCase, requirements) {
  const cacheKey = `rec:${useCase}:${hashObject(requirements)}`;
  const cached = await redis.get(cacheKey);
  
  if (cached) {
    const data = JSON.parse(cached);
    if (Date.now() - data.generated < 3600000) { // 1 hour TTL
      return data.recommendations;
    }
  }
  
  return null;
}

async function cacheRecommendations(useCase, requirements, recommendations) {
  const cacheKey = `rec:${useCase}:${hashObject(requirements)}`;
  const data = {
    recommendations,
    generated: Date.now()
  };
  
  await redis.setex(cacheKey, 3600, JSON.stringify(data)); // 1 hour expiry
}
```

#### Database Optimisation
```sql
-- Essential indexes for performance
CREATE INDEX idx_products_use_case ON products USING GIN (use_cases);
CREATE INDEX idx_products_capacity ON products (capacity_wh);
CREATE INDEX idx_price_history_product_recent ON price_history (product_id, recorded_at DESC);
CREATE INDEX idx_price_alerts_active ON price_alerts (is_active, user_id) WHERE is_active = true;

-- Materialized view for current prices
CREATE MATERIALIZED VIEW current_prices AS
SELECT DISTINCT ON (product_id, retailer)
  product_id,
  retailer,
  price,
  in_stock,
  recorded_at
FROM price_history
ORDER BY product_id, retailer, recorded_at DESC;

-- Refresh materialized view every 15 minutes
CREATE OR REPLACE FUNCTION refresh_current_prices()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY current_prices;
END;
$$ LANGUAGE plpgsql;
```

This technical implementation provides a robust foundation for the new user flow while maintaining excellent performance and user experience across all devices and connection speeds.