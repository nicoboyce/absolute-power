# Recommendation Engine - Detailed Specification

## Engine Overview
**Purpose**: Transform user requirements into 3-5 perfectly matched product recommendations
**Input**: Use case selection + requirement form data
**Output**: Personalised product recommendations with clear reasoning

## Recommendation Logic Matrix

### Emergency Home Backup Logic Tree

#### Short Outages (2-8 hours)
```
User Input: Duration ≤ 8 hours, Medical priority = true
├─ Budget Conscious (£200-500)
│  └─ Recommend: Jackery Explorer 500 v2 (£449)
│     Reasoning: "Medical device safe, 8-hour runtime, UPS switching"
│
├─ Balanced Choice (£500-800)  
│  └─ Recommend: Anker SOLIX C800 (£599)
│     Reasoning: "Perfect for medical equipment, silent operation"
│
└─ Premium/Future-proof (£800+)
   └─ Recommend: EcoFlow DELTA 2 (£899)
      Reasoning: "Powers fridge + medical devices for 12+ hours"

User Input: Duration ≤ 8 hours, Communication priority = true
├─ Budget: Bluetti EB3A (£209)
├─ Balanced: Jackery Explorer 500 v2 (£449)  
└─ Premium: Anker SOLIX C800 (£599)
```

#### Extended Outages (12-48 hours)
```
User Input: Duration > 12 hours, Any priority
├─ Budget Conscious (£600-1000)
│  └─ Recommend: Jackery Explorer 1000 v2 (£799)
│     Reasoning: "24-hour essential power, expandable with solar"
│
├─ Comprehensive (£1000-1500)
│  └─ Recommend: Bluetti AC70 (£649) 
│     Reasoning: "Powers fridge for 36 hours, fast AC charging"
│
└─ Maximum Backup (£1500+)
   └─ Recommend: Anker SOLIX F2000 (£1699)
      Reasoning: "2+ days complete home backup power"
```

### Camping & Outdoors Logic Tree

#### Weekend Trips (1-3 days)
```
User Equipment: Portable fridge priority = true
├─ Ultra-Portable: Jackery Explorer 240 v2 (£199)
│  Reasoning: "Weighs 3kg, perfect for car camping, powers fridge 12hrs"
│
├─ Best Balance: Anker SOLIX C800 (£599)
│  Reasoning: "Powers 40L fridge for 2 full days, solar ready"
│
└─ Premium Choice: Jackery Explorer 1000 Plus (£799)
   Reasoning: "Solar charging, powers everything, modular design"

User Equipment: Basic devices only (phones, lights)
├─ Ultra-Light: Jackery Explorer 100 Plus (£99)
├─ Weekend Warrior: Jackery Explorer 300 Plus (£229)
└─ Future-Proof: Anker SOLIX C800 (£599)
```

#### Extended Camping (4-7 days)
```
User Duration: 4+ days, Solar compatible needed
├─ Solar-Ready: EcoFlow DELTA 2 (£899)
│  Reasoning: "Fast solar charging, handles all camping equipment"
│
├─ High Capacity: Bluetti AC200L (£1299)  
│  Reasoning: "Week-long power independence, massive capacity"
│
└─ Modular System: Anker SOLIX F2000 (£1699)
   Reasoning: "Add batteries and panels as needed, ultimate flexibility"
```

### Work Flexibility Logic Tree

#### Mobile Office (4-8 hours daily)
```
User Equipment: Laptop + Monitor setup
├─ Budget: Anker SOLIX C800 (£599)
│  Reasoning: "Powers laptop + monitor for full work day"
│
├─ Professional: EcoFlow DELTA 2 (£899)
│  Reasoning: "UPS function, powers multiple monitors, printer"
│
└─ Studio Setup: Anker SOLIX F2000 (£1699)
   Reasoning: "Powers full studio: computers, lights, equipment"

User Equipment: Power tools + workspace
├─ Contractor: Bluetti AC200L (£1299)
├─ Workshop: EcoFlow DELTA Pro 3 (£2499)
└─ Professional Site: Anker SOLIX F3800 (£3699)
```

### Off-Grid Living Logic Tree

#### Van Life / Mobile Living
```
User Duration: 3-7 days between charges
├─ Van Life Starter: EcoFlow DELTA 2 (£899)
│  Reasoning: "Perfect van life companion, car charging, compact"
│
├─ Extended Living: Bluetti AC200MAX (£1899)
│  Reasoning: "Multi-day independence, expandable, reliable"
│
└─ Full Off-Grid: Anker SOLIX F3800 (£3699)
   Reasoning: "Powers everything: fridge, lights, electronics, tools"
```

## Recommendation Presentation Format

### Dynamic Section Header
```
[USER_CASE_SELECTED] + "Your Recommended [CONTEXT] Solutions"

Examples:
- "Your Recommended Home Backup Solutions"  
- "Your Recommended Portable Power Stations"
- "Your Recommended Mobile Office Power"
- "Your Recommended Off-Grid Power Systems"
```

### Individual Recommendation Card Layout
```
┌─────────────────────────────────────────────┐
│ [RECOMMENDED BADGE] - Only for top pick     │
│                                             │
│ [Product Image - 300x200px]                 │
│                                             │
│ Product Name (24px, bold)                   │
│ "Why This One" Tagline (18px, blue)         │
│ £Price (28px, green, bold)                  │
│                                             │
│ ─────────────────────────────────────────── │
│ ✓ Benefit 1 specific to their use case     │
│ ✓ Benefit 2 specific to their use case     │  
│ ✓ Benefit 3 specific to their use case     │
│ ─────────────────────────────────────────── │
│                                             │
│ [View Full Details] [Add to Compare List]   │
└─────────────────────────────────────────────┘
```

### Dynamic "Why This One" Taglines

**Emergency Backup Context**:
- "Medical equipment certified"
- "Silent operation guaranteed"  
- "Instant UPS switching"
- "Hospital-grade reliability"
- "Extended runtime leader"

**Camping Context**:
- "Weighs only 3.1kg"
- "Solar charging champion"
- "Rugged outdoor design"
- "Powers fridge 2+ days"
- "Waterproof connections"

**Work Context**:
- "All-day laptop power"
- "UPS function included"
- "Professional grade build"
- "Multiple device support"
- "Quiet operation certified"

**Off-Grid Context**:
- "Ultimate capacity leader"
- "Modular expansion ready"
- "Multi-day independence"
- "Heavy-duty applications"
- "Complete system solution"

## Benefit Statement Generation

### Dynamic Benefit Calculation
```javascript
function generateBenefits(product, userCase, userRequirements) {
  const benefits = [];
  
  // Runtime calculation based on user's priority devices
  if (userCase === 'emergency_backup') {
    if (userRequirements.priorities.includes('medical')) {
      benefits.push(`Powers CPAP machine for ${calculateRuntime(product.capacity, 40)}hrs`);
    }
    if (userRequirements.priorities.includes('communication')) {
      benefits.push(`Charges ${Math.floor(product.capacity / 10)} phones during outage`);
    }
  }
  
  // Weight consideration for portable use cases
  if (userCase === 'camping_outdoor') {
    if (product.weight < 5) {
      benefits.push(`Ultralight at ${product.weight}kg (easy to carry)`);
    }
    benefits.push(`Powers portable fridge for ${calculateRuntime(product.capacity, 60)}hrs`);
  }
  
  return benefits.slice(0, 3); // Maximum 3 benefits per card
}
```

### Use Case Specific Benefits

**Emergency Backup Benefits**:
```javascript
const emergencyBenefits = {
  medical: [
    "Medical device compatible (clean sine wave)",
    "UPS function - instant switching (<10ms)",
    "Silent operation (won't disturb patients)",
    "Hospital-grade power quality"
  ],
  communication: [
    "Keeps phones charged for days",
    "Powers WiFi router for internet", 
    "Radio and emergency communications",
    "LED torch built-in"
  ],
  food_preservation: [
    "Keeps fridge running ${hours} hours",
    "Freezer contents stay frozen",
    "Save hundreds in spoiled food",
    "Temperature monitoring capability"
  ]
}
```

## Comparison Table Generation

### Automatic Comparison Setup
```
User selects Emergency Backup + Medical Priority:

                    Budget Pick    Best Value    Premium
                    Jackery 500v2  Anker C800    EcoFlow Δ2
────────────────────────────────────────────────────────
Your Runtime        
CPAP Machine        12 hours      19 hours      25 hours
Phone Charging      51 charges    76 charges    102 charges
Fridge Power        8 hours       12 hours      17 hours

Key Features
Medical Compatible  ✅             ✅            ✅
UPS Function        ❌             ✅            ✅
Solar Expandable    ❌             ✅            ✅
Weight             6.2kg          10.5kg        12.0kg
Price              £449           £599          £899
────────────────────────────────────────────────────────
Best For           Short outages  Most versatile Extended backup
```

### Winner Detection Logic
```javascript
function detectWinners(products, userPriorities) {
  const categories = {
    capacity: products.sort((a, b) => b.capacity - a.capacity)[0],
    value: products.sort((a, b) => (a.price/a.capacity) - (b.price/b.capacity))[0],
    portability: products.sort((a, b) => a.weight - b.weight)[0],
    features: products.sort((a, b) => b.featureScore - a.featureScore)[0]
  };
  
  // Highlight winners with 🏆 emoji
  return categories;
}
```

## Social Proof Integration

### Real User Stories by Use Case
```javascript
const userStories = {
  emergency_backup: [
    {
      name: "Mark from Edinburgh",
      story: "Used this during the February 2024 storm: 'Kept our baby's bottle warmer and phones charged for 2 days. Absolute lifesaver with a newborn.'",
      product: "anker_solix_c800",
      verified: true
    }
  ],
  camping_outdoor: [
    {
      name: "Sarah from Cornwall", 
      story: "Takes this camping monthly: 'Powers our portable fridge, lights, and charges all devices. Still going strong after 18 months.'",
      product: "jackery_1000_plus",
      verified: true
    }
  ]
}
```

## Recommendation Algorithm Scoring

### Multi-Factor Scoring System
```javascript
function calculateRecommendationScore(product, userRequirements) {
  let score = 0;
  
  // Capacity match (40% of score)
  const capacityMatch = Math.min(product.capacity / userRequirements.targetCapacity, 1);
  score += capacityMatch * 40;
  
  // Budget fit (30% of score)  
  const budgetFit = userRequirements.maxBudget >= product.price ? 30 : 0;
  score += budgetFit;
  
  // Feature match (20% of score)
  const featureMatch = calculateFeatureMatch(product, userRequirements);
  score += featureMatch * 20;
  
  // Brand reliability (10% of score)
  score += product.brandScore * 10;
  
  return score;
}
```

### Feature Matching Logic
```javascript
function calculateFeatureMatch(product, requirements) {
  const matches = [];
  
  if (requirements.needsSolar && product.solarCapable) matches.push(1);
  if (requirements.needsUPS && product.hasUPS) matches.push(1);
  if (requirements.priorityWeight && product.weight < 10) matches.push(1);
  if (requirements.medicalUse && product.medicalGrade) matches.push(1);
  
  return matches.length / 4; // Normalised score
}
```

## Fallback Recommendations

### No Perfect Match Scenario
```javascript
if (perfectMatches.length === 0) {
  return {
    message: "We found great options that almost match your needs:",
    recommendations: closeMatches,
    tradeoffExplanations: [
      "Slightly over budget but excellent long-term value",
      "Meets 90% of requirements with bonus features",
      "Consider this if budget allows - significant upgrade"
    ]
  };
}
```

### Budget Constraints Handling
```javascript
if (userBudget < lowestRecommendedPrice) {
  return {
    message: "Great news! We found options in your budget:",
    recommendations: budgetOptions,
    upgradeOptions: [
      {
        product: nextLevelUp,
        additionalCost: priceDifference,
        additionalBenefits: extraFeatures
      }
    ]
  };
}
```

## Performance & Caching Strategy

### Recommendation Caching
```javascript
// Cache recommendations by use case + requirements hash
const cacheKey = `recommendations_${useCase}_${hash(requirements)}`;
const cachedResult = redis.get(cacheKey);

if (cachedResult && !isStale(cachedResult)) {
  return cachedResult;
}

const freshRecommendations = generateRecommendations(useCase, requirements);
redis.setex(cacheKey, 3600, freshRecommendations); // 1 hour cache
```

### Real-time Price Integration
- Recommendations show current best prices
- Out-of-stock products automatically excluded
- Price changes trigger recommendation recalculation
- Deal alerts integrated with recommendation engine

This recommendation engine transforms generic product browsing into personalised solution matching, dramatically improving user satisfaction and conversion rates while building trust through relevant, reasoned suggestions.