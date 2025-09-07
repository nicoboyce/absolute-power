# Conversion Tracking & Analytics Strategy

## Overview
Comprehensive analytics framework to measure, optimise, and scale the new user flow from first visit through to email signup and beyond.

## Conversion Funnel Definition

### Primary Conversion Path (5 Stages)
```
Stage 1: AWARENESS (Landing & Interest)
├─ Page view from traffic source
├─ Hero section engagement (>30s time)
├─ Scroll depth >50% (reaches use case selector)
└─ Success Metric: 70% scroll-through rate

Stage 2: QUALIFICATION (Use Case Selection)  
├─ Use case card interaction (hover/click)
├─ Use case selection (card clicked)
├─ Requirements form started
└─ Success Metric: 60% card selection rate

Stage 3: CONSIDERATION (Product Evaluation)
├─ Requirements form completed
├─ Product recommendations viewed
├─ 2+ products compared or detailed view
└─ Success Metric: 80% form completion rate

Stage 4: INTENT (Email Capture Initiated)
├─ Email address entered in form
├─ Product tracking preferences selected
├─ Submit button clicked
└─ Success Metric: 15% email signup rate

Stage 5: CONVERSION (Confirmed Subscription)
├─ Email subscription confirmed
├─ Welcome email opened
├─ First week engagement tracked
└─ Success Metric: 90% confirmation rate
```

## Analytics Implementation

### Event Tracking Schema
```javascript
const analyticsEvents = {
  // Page and section views
  page_view: {
    required: ['page_url', 'referrer', 'user_session'],
    optional: ['utm_source', 'utm_medium', 'utm_campaign']
  },
  
  section_view: {
    required: ['section_name', 'scroll_depth'],
    optional: ['time_to_reach', 'viewport_size']
  },
  
  // Hero section interactions
  hero_cta_click: {
    required: ['button_text', 'position'],
    optional: ['scroll_depth', 'time_on_page']
  },
  
  hero_animation_engagement: {
    required: ['watch_time', 'completion_rate'],
    optional: ['interactions', 'pause_count']
  },
  
  // Use case qualification
  use_case_card_hover: {
    required: ['card_id', 'hover_duration'],
    optional: ['cards_previously_hovered']
  },
  
  use_case_selected: {
    required: ['use_case', 'time_to_select'],
    optional: ['cards_considered', 'hesitation_count']
  },
  
  requirements_form_started: {
    required: ['use_case', 'form_fields_count'],
    optional: ['pre_populated_data']
  },
  
  requirements_form_completed: {
    required: ['use_case', 'form_data', 'completion_time'],
    optional: ['field_completion_order', 'validation_errors']
  },
  
  // Product recommendations
  recommendations_generated: {
    required: ['use_case', 'product_count', 'generation_time'],
    optional: ['requirements_hash', 'cache_hit']
  },
  
  product_card_viewed: {
    required: ['product_id', 'position_in_list'],
    optional: ['view_duration', 'scroll_depth']
  },
  
  product_comparison_started: {
    required: ['product_ids', 'comparison_type'],
    optional: ['source_section']
  },
  
  // Confidence building interactions
  calculator_used: {
    required: ['devices_selected', 'runtime_calculated'],
    optional: ['capacity_recommended', 'use_case_context']
  },
  
  testimonial_viewed: {
    required: ['testimonial_id', 'view_duration'],
    optional: ['carousel_position', 'interaction_type']
  },
  
  faq_expanded: {
    required: ['question_id', 'category'],
    optional: ['scroll_depth', 'search_query']
  },
  
  // Email capture
  email_form_started: {
    required: ['form_location', 'products_selected'],
    optional: ['sticky_bar_visible', 'previous_attempts']
  },
  
  email_validation_error: {
    required: ['error_type', 'email_domain'],
    optional: ['suggestion_shown', 'correction_applied']
  },
  
  email_signup_attempted: {
    required: ['products_count', 'preferences_selected'],
    optional: ['form_completion_time', 'validation_errors']
  },
  
  email_signup_success: {
    required: ['user_id', 'products_tracked', 'use_case'],
    optional: ['signup_source', 'incentive_claimed']
  }
};
```

### Attribution Tracking
```javascript
class AttributionManager {
  constructor() {
    this.firstTouchKey = 'first_touch_attribution';
    this.lastTouchKey = 'last_touch_attribution';
    this.sessionKey = 'session_attribution';
  }
  
  captureFirstTouch() {
    // Only capture if not already set
    if (localStorage.getItem(this.firstTouchKey)) return;
    
    const attribution = {
      timestamp: Date.now(),
      url: window.location.href,
      referrer: document.referrer,
      utm_source: this.getUrlParameter('utm_source'),
      utm_medium: this.getUrlParameter('utm_medium'),
      utm_campaign: this.getUrlParameter('utm_campaign'),
      utm_content: this.getUrlParameter('utm_content'),
      gclid: this.getUrlParameter('gclid'), // Google Ads
      fbclid: this.getUrlParameter('fbclid'), // Facebook Ads
      user_agent: navigator.userAgent,
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      device_type: this.detectDeviceType()
    };
    
    localStorage.setItem(this.firstTouchKey, JSON.stringify(attribution));
  }
  
  captureLastTouch() {
    const attribution = {
      timestamp: Date.now(),
      url: window.location.href,
      referrer: document.referrer,
      session_id: this.getSessionId()
    };
    
    sessionStorage.setItem(this.lastTouchKey, JSON.stringify(attribution));
  }
  
  getFullAttribution() {
    const firstTouch = JSON.parse(localStorage.getItem(this.firstTouchKey) || '{}');
    const lastTouch = JSON.parse(sessionStorage.getItem(this.lastTouchKey) || '{}');
    
    return {
      first_touch: firstTouch,
      last_touch: lastTouch,
      session_count: this.getSessionCount(),
      days_since_first_visit: this.getDaysSinceFirstVisit(),
      total_page_views: this.getTotalPageViews()
    };
  }
  
  getSessionCount() {
    const count = localStorage.getItem('session_count') || '0';
    return parseInt(count, 10);
  }
  
  incrementSessionCount() {
    const currentCount = this.getSessionCount();
    localStorage.setItem('session_count', (currentCount + 1).toString());
  }
  
  getDaysSinceFirstVisit() {
    const firstTouch = JSON.parse(localStorage.getItem(this.firstTouchKey) || '{}');
    if (!firstTouch.timestamp) return 0;
    
    return Math.floor((Date.now() - firstTouch.timestamp) / (1000 * 60 * 60 * 24));
  }
}
```

### A/B Testing Framework
```javascript
class ABTestManager {
  constructor() {
    this.tests = new Map();
    this.userBucket = this.getUserBucket();
    this.assignmentKey = 'ab_test_assignments';
  }
  
  defineTest(testName, config) {
    this.tests.set(testName, {
      name: testName,
      variants: config.variants,
      trafficSplit: config.trafficSplit || this.evenSplit(config.variants.length),
      successMetric: config.successMetric,
      isActive: config.isActive !== false,
      minSampleSize: config.minSampleSize || 1000,
      maxDuration: config.maxDuration || 30, // days
      startDate: config.startDate || new Date()
    });
  }
  
  getVariant(testName) {
    const test = this.tests.get(testName);
    if (!test || !test.isActive) return test?.variants[0]; // Return control
    
    // Check for existing assignment
    const assignments = JSON.parse(localStorage.getItem(this.assignmentKey) || '{}');
    if (assignments[testName]) {
      return assignments[testName];
    }
    
    // Assign variant based on user bucket
    const variant = this.assignVariant(test);
    assignments[testName] = variant;
    localStorage.setItem(this.assignmentKey, JSON.stringify(assignments));
    
    // Track assignment
    analytics.track('ab_test_assigned', {
      test_name: testName,
      variant: variant,
      user_bucket: this.userBucket
    });
    
    return variant;
  }
  
  assignVariant(test) {
    let cumulativeWeight = 0;
    const random = this.userBucket; // Use consistent bucket
    
    for (let i = 0; i < test.variants.length; i++) {
      cumulativeWeight += test.trafficSplit[i];
      if (random <= cumulativeWeight) {
        return test.variants[i];
      }
    }
    
    return test.variants[0]; // Fallback to control
  }
  
  trackConversion(testName, conversionEvent) {
    const variant = this.getVariant(testName);
    if (!variant) return;
    
    analytics.track('ab_test_conversion', {
      test_name: testName,
      variant: variant,
      conversion_event: conversionEvent,
      user_bucket: this.userBucket
    });
  }
  
  getUserBucket() {
    // Generate consistent bucket (0-99) based on session/user ID
    const sessionId = this.getSessionId();
    const hash = this.simpleHash(sessionId);
    return hash % 100;
  }
  
  simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }
}
```

### User Segmentation Strategy
```javascript
class UserSegmentation {
  constructor() {
    this.segments = new Map();
  }
  
  defineSegments() {
    // Behavioral segments
    this.segments.set('engagement_level', {
      quick_exit: (user) => user.timeOnSite < 30000, // <30 seconds
      browser: (user) => user.timeOnSite >= 30000 && user.timeOnSite < 120000,
      researcher: (user) => user.timeOnSite >= 120000 && user.interactions > 5,
      converter: (user) => user.hasSignedUp
    });
    
    // Use case segments
    this.segments.set('use_case', {
      emergency_focused: (user) => user.selectedUseCase === 'emergency_backup',
      outdoor_enthusiast: (user) => user.selectedUseCase === 'camping_outdoor',
      professional_user: (user) => user.selectedUseCase === 'work_mobile',
      off_grid_lifestyle: (user) => user.selectedUseCase === 'off_grid'
    });
    
    // Value segments
    this.segments.set('price_sensitivity', {
      budget_conscious: (user) => this.getMaxViewedPrice(user) < 500,
      mid_market: (user) => this.getMaxViewedPrice(user) >= 500 && this.getMaxViewedPrice(user) < 1500,
      premium_buyer: (user) => this.getMaxViewedPrice(user) >= 1500
    });
    
    // Traffic source segments
    this.segments.set('acquisition', {
      organic_search: (user) => user.trafficSource === 'organic',
      paid_search: (user) => user.trafficSource === 'cpc',
      social_media: (user) => user.trafficSource === 'social',
      direct_navigation: (user) => user.trafficSource === 'direct',
      referral: (user) => user.trafficSource === 'referral'
    });
  }
  
  classifyUser(userData) {
    const classification = {};
    
    this.segments.forEach((rules, segmentName) => {
      Object.keys(rules).forEach(ruleName => {
        if (rules[ruleName](userData)) {
          classification[segmentName] = ruleName;
        }
      });
    });
    
    return classification;
  }
  
  trackSegmentPerformance() {
    // Calculate conversion rates by segment
    const segmentStats = {};
    
    this.segments.forEach((rules, segmentName) => {
      segmentStats[segmentName] = {};
      
      Object.keys(rules).forEach(ruleName => {
        // This would query actual user data
        segmentStats[segmentName][ruleName] = {
          totalUsers: 0,
          conversions: 0,
          conversionRate: 0,
          avgTimeToConversion: 0,
          avgOrderValue: 0
        };
      });
    });
    
    return segmentStats;
  }
}
```

## Revenue Attribution Model

### Lifetime Value Tracking
```javascript
class RevenueAttribution {
  async trackPurchase(purchaseData) {
    const {
      userId,
      email,
      productId,
      retailer,
      purchasePrice,
      commission,
      orderDate
    } = purchaseData;
    
    // Find user's attribution data
    const user = await User.findOne({ email });
    if (!user) return; // Can't attribute
    
    const attribution = user.signupAttribution;
    const timeToConversion = new Date(orderDate) - new Date(user.createdAt);
    
    // Record attributed revenue
    await AttributedRevenue.create({
      user_id: userId,
      product_id: productId,
      retailer,
      purchase_price: purchasePrice,
      commission_earned: commission,
      time_to_conversion: timeToConversion,
      attribution_source: attribution.utm_source,
      attribution_medium: attribution.utm_medium,
      attribution_campaign: attribution.utm_campaign,
      first_touch_date: new Date(attribution.timestamp),
      order_date: orderDate
    });
    
    // Update user LTV
    await this.updateUserLTV(userId, commission);
    
    // Track cohort performance
    await this.updateCohortStats(user.createdAt, commission);
  }
  
  async calculateCohortLTV(cohortMonth, timeframe = 12) {
    // Monthly cohort analysis
    const cohortStart = new Date(cohortMonth);
    const cohortEnd = new Date(cohortStart.getFullYear(), cohortStart.getMonth() + 1, 0);
    
    const cohortUsers = await User.find({
      createdAt: { $gte: cohortStart, $lte: cohortEnd }
    });
    
    const cohortRevenue = await AttributedRevenue.aggregate([
      {
        $match: {
          user_id: { $in: cohortUsers.map(u => u.id) },
          order_date: {
            $gte: cohortStart,
            $lte: new Date(cohortStart.getFullYear(), cohortStart.getMonth() + timeframe, 0)
          }
        }
      },
      {
        $group: {
          _id: null,
          totalRevenue: { $sum: '$commission_earned' },
          totalOrders: { $sum: 1 },
          uniqueUsers: { $addToSet: '$user_id' }
        }
      }
    ]);
    
    const stats = cohortRevenue[0] || {};
    
    return {
      cohortMonth,
      cohortSize: cohortUsers.length,
      totalRevenue: stats.totalRevenue || 0,
      totalOrders: stats.totalOrders || 0,
      convertedUsers: stats.uniqueUsers?.length || 0,
      conversionRate: (stats.uniqueUsers?.length || 0) / cohortUsers.length,
      revenuePerUser: (stats.totalRevenue || 0) / cohortUsers.length,
      avgOrderValue: (stats.totalRevenue || 0) / (stats.totalOrders || 1)
    };
  }
  
  async calculateChannelROI() {
    const channelStats = await AttributedRevenue.aggregate([
      {
        $group: {
          _id: {
            source: '$attribution_source',
            medium: '$attribution_medium'
          },
          revenue: { $sum: '$commission_earned' },
          orders: { $sum: 1 },
          users: { $addToSet: '$user_id' }
        }
      }
    ]);
    
    // Add cost data (from advertising platforms)
    const channelROI = channelStats.map(channel => ({
      source: channel._id.source,
      medium: channel._id.medium,
      revenue: channel.revenue,
      orders: channel.orders,
      users: channel.users.length,
      // cost: getCostData(channel._id.source, channel._id.medium),
      // roi: (channel.revenue - cost) / cost
    }));
    
    return channelROI;
  }
}
```

## Real-Time Dashboard Requirements

### Key Performance Indicators
```javascript
const dashboardMetrics = {
  // Acquisition metrics
  acquisition: {
    total_visits: 'COUNT(DISTINCT session_id) FROM analytics_events WHERE event_name = "page_view"',
    unique_visitors: 'COUNT(DISTINCT user_fingerprint)',
    traffic_sources: 'GROUP BY utm_source, utm_medium',
    bounce_rate: '(single_page_sessions / total_sessions) * 100',
    avg_session_duration: 'AVG(session_duration)'
  },
  
  // Engagement metrics
  engagement: {
    use_case_selection_rate: '(use_case_selected / page_views) * 100',
    form_completion_rate: '(forms_completed / forms_started) * 100',
    product_interaction_rate: '(product_views / recommendation_views) * 100',
    scroll_depth_avg: 'AVG(max_scroll_depth)',
    time_to_qualification: 'AVG(time_to_use_case_selection)'
  },
  
  // Conversion metrics
  conversion: {
    email_signup_rate: '(email_signups / page_views) * 100',
    form_abandonment_rate: '(forms_started - forms_completed) / forms_started * 100',
    confirmation_rate: '(confirmed_emails / signup_attempts) * 100',
    segmented_conversion_rates: 'GROUP BY use_case, traffic_source'
  },
  
  // Revenue metrics (when available)
  revenue: {
    attributed_revenue: 'SUM(commission_earned)',
    revenue_per_subscriber: 'attributed_revenue / total_subscribers',
    customer_lifetime_value: 'AVG(user_ltv)',
    payback_period: 'acquisition_cost / monthly_revenue_per_user',
    channel_roi: '(revenue - cost) / cost * 100'
  }
};
```

### Real-Time Alerting System
```javascript
class AlertingSystem {
  constructor() {
    this.thresholds = {
      conversion_rate_drop: {
        threshold: -20, // 20% decrease
        timeframe: '24h',
        comparison: 'previous_period'
      },
      traffic_spike: {
        threshold: 200, // 200% increase
        timeframe: '1h',
        comparison: 'rolling_average'
      },
      error_rate_increase: {
        threshold: 50, // 50% increase
        timeframe: '15m',
        comparison: 'baseline'
      },
      email_delivery_failure: {
        threshold: 5, // 5% failure rate
        timeframe: '30m',
        comparison: 'absolute'
      }
    };
  }
  
  async checkThresholds() {
    for (const [alertName, config] of Object.entries(this.thresholds)) {
      const currentValue = await this.getCurrentMetric(alertName, config.timeframe);
      const comparison = await this.getComparisonValue(alertName, config);
      
      const changePercent = ((currentValue - comparison) / comparison) * 100;
      
      if (Math.abs(changePercent) >= Math.abs(config.threshold)) {
        await this.triggerAlert(alertName, {
          currentValue,
          comparison,
          changePercent,
          threshold: config.threshold
        });
      }
    }
  }
  
  async triggerAlert(alertName, data) {
    const alert = {
      name: alertName,
      severity: this.getSeverity(data.changePercent),
      timestamp: new Date(),
      data
    };
    
    // Send to appropriate channels
    switch (alert.severity) {
      case 'critical':
        await this.sendSlackAlert(alert);
        await this.sendEmailAlert(alert);
        break;
      case 'warning':
        await this.sendSlackAlert(alert);
        break;
      case 'info':
        await this.logAlert(alert);
        break;
    }
  }
}
```

## Privacy-Compliant Implementation

### GDPR Compliance Framework
```javascript
class ConsentManager {
  constructor() {
    this.consentTypes = {
      necessary: { required: true, description: 'Essential site functionality' },
      analytics: { required: false, description: 'Site usage analytics' },
      marketing: { required: false, description: 'Marketing and advertising' }
    };
  }
  
  initializeTracking() {
    const consent = this.getStoredConsent();
    
    // Always allow necessary tracking
    this.enableNecessaryTracking();
    
    if (consent.analytics) {
      this.enableAnalyticsTracking();
    }
    
    if (consent.marketing) {
      this.enableMarketingTracking();
    }
    
    // Show consent banner if no consent given
    if (!this.hasConsentDecision()) {
      this.showConsentBanner();
    }
  }
  
  enableAnalyticsTracking() {
    // Initialize analytics with anonymized data
    analytics.init({
      anonymize_ip: true,
      respect_dnt: true,
      cookie_expiry: 90, // days
      data_retention: 24 // months
    });
  }
  
  handleConsentUpdate(newConsent) {
    const previousConsent = this.getStoredConsent();
    
    // Handle withdrawal of consent
    if (previousConsent.analytics && !newConsent.analytics) {
      this.deleteAnalyticsCookies();
      analytics.disable();
    }
    
    if (previousConsent.marketing && !newConsent.marketing) {
      this.deleteMarketingCookies();
      this.removeMarketingPixels();
    }
    
    // Store new consent
    localStorage.setItem('user_consent', JSON.stringify({
      ...newConsent,
      timestamp: Date.now(),
      version: '1.0'
    }));
  }
  
  anonymizeUserData() {
    return {
      user_session: this.hashString(this.getSessionId()),
      user_fingerprint: this.hashString(this.getUserFingerprint()),
      ip_address: null, // Remove IP
      user_agent: this.truncateUserAgent(navigator.userAgent)
    };
  }
}
```

This comprehensive analytics and tracking strategy ensures complete visibility into user behavior while respecting privacy regulations and providing actionable insights for continuous optimisation.