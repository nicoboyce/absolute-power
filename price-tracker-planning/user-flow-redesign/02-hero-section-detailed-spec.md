# Hero Section - Detailed Specification

## Section Overview
**Purpose**: Hook visitors with relatable problems and guide them toward solution discovery
**Position**: Top of homepage, first thing users see
**Success Metric**: >60% scroll to use case selector

## Layout Structure

### Desktop Layout (1200px+ width)
```
┌─────────────────────────────────────────────────────────┐
│ [Nav Overlay - Transparent]                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  CONTENT (60%)                    VISUAL (40%)         │
│  ┌─────────────────────┐        ┌─────────────────┐     │
│  │ Headline            │        │                 │     │
│  │ Subheadline         │        │   Animation     │     │
│  │ Social Proof        │        │   Sequence      │     │
│  │ Primary CTA         │        │                 │     │
│  │ Secondary CTA       │        │                 │     │
│  │ Trust Indicators    │        │                 │     │
│  └─────────────────────┘        └─────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout (< 768px width)
```
┌─────────────────────────────────┐
│ [Minimal Nav]                   │
├─────────────────────────────────┤
│                                 │
│     Visual Element              │
│     ┌─────────────────┐         │
│     │   Animation     │         │
│     │   Sequence      │         │
│     └─────────────────┘         │
│                                 │
│     Headline                    │
│     Subheadline                 │
│     Social Proof                │
│                                 │
│     Primary CTA (Full Width)    │
│     Secondary CTA               │
│                                 │
│     Trust Indicators            │
│                                 │
└─────────────────────────────────┘
```

## Content Hierarchy

### Primary Headline (H1)
**Default Version**:
```
"Power Cuts Don't Have To Leave You Powerless"
```

**A/B Testing Variants**:
```
Variant A: "Never Be Caught Without Power Again"
Variant B: "When The Grid Fails, You Don't Have To"  
Variant C: "Keep Your Life Running When The Lights Go Out"
```

**Typography**:
- Desktop: 48px, font-weight: 700, line-height: 1.2
- Mobile: 32px, font-weight: 700, line-height: 1.3
- Colour: Dark navy (#2c3e50)
- Font: System font stack for performance

### Supporting Subheadline
**Content**:
```
"From medical devices during outages to laptops while camping - 
portable power stations keep your essential devices running when traditional power fails."
```

**Emotional Hook Variants** (for different segments):
```
Medical Focus: "CPAP machines, oxygen concentrators, medication fridges - 
               never worry about power cuts affecting critical care."

Family Focus: "Keep phones charged during storms, power kids' devices on camping trips, 
              maintain comfort when the grid goes down."

Professional: "Never miss a deadline due to power cuts. Work from anywhere, 
              maintain productivity during outages."
```

**Typography**:
- Desktop: 24px, font-weight: 400, line-height: 1.4
- Mobile: 18px, font-weight: 400, line-height: 1.5
- Colour: Medium grey (#7f8c8d)
- Max-width: 600px

### Social Proof Statistics Bar
**Content Focus**: Real-world context, not technical specs
```
┌─────────────────────────────────────────────────────────┐
│ 💡 2.1M UK homes lost power in winter 2024             │
│ ⏰ Average outage: 4.2 hours (enough to drain devices)  │
│ 🌩️ Most outages during storms (when you need power most)│
└─────────────────────────────────────────────────────────┘
```

**Visual Design**:
- Light background bar with subtle border
- Icons for visual interest
- Small font (14px) but readable
- Horizontal scroll on mobile if needed

## Visual Element Specification

### Hero Animation Sequence
**Concept**: Problem → Solution → Relief (8-second loop)

**Scene 1** (3 seconds): "The Problem"
- Dark house silhouette
- Devices with red "low battery" indicators
- Phone screen showing "2% battery"
- Laptop closing/going dark
- Family looking concerned

**Scene 2** (2 seconds): "The Solution"  
- Power station appears (slide in from right)
- Cables connecting to devices
- LED indicators showing "charging"
- Gentle blue glow effect

**Scene 3** (3 seconds): "The Relief"
- Devices back online (green indicators)
- Phone showing "100% charged"
- Laptop screen bright
- Family relaxed and smiling

**Technical Implementation**:
- SVG animation with CSS keyframes
- Fallback static image for slow connections
- Pause/play controls for accessibility
- Auto-pause after 3 loops to reduce distraction

### Alternative Static Visual
**Split-screen Before/After**:
- Left: Dark house, worried family, dead devices
- Right: Same scene with power station, everyone comfortable
- Clear visual contrast between problem and solution

## Call-to-Action Design

### Primary CTA Button
**Default Text**: `"Find My Power Solution"`

**A/B Testing Variants**:
```
Variant A: "Get My Backup Plan"
Variant B: "Calculate My Power Needs"  
Variant C: "Match Me With The Right Power Station"
```

**Visual Design**:
```css
.primary-cta {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
  font-size: 18px;
  font-weight: 600;
  padding: 16px 32px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.3);
}

.primary-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4);
  background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
}
```

**Mobile Adaptations**:
- Full width button (minus 20px margin each side)
- Larger touch target (minimum 44px height)
- Increased padding for thumb-friendly interaction

### Secondary CTA
**Text**: `"Just browsing? See all power stations →"`
**Style**: Text link, smaller, positioned below primary button
**Destination**: Current full product grid (for researchers)
**Purpose**: Provide escape route for users not ready for guided flow

## Trust Indicators

### Subtle Trust Signals (Bottom of Section)
**Content**:
```
✅ Free UK delivery on orders over £200
🛡️ Price match guarantee  
⭐ Real reviews from 2,400+ buyers
📞 30-day return policy
```

**Design Requirements**:
- Subtle visual treatment (small text, light grey)
- Horizontal layout desktop, 2x2 grid mobile
- Icons for visual scanning
- Links to relevant policy pages

### UK-Specific Elements
- British pound currency symbols
- "UK delivery" messaging
- Phone number format: "0800 xxx xxxx"
- Company registration references if applicable

## Interactive Elements

### Scroll Indicator
**Purpose**: Encourage users to continue down the page
**Implementation**: Subtle animated arrow or "scroll to explore" text
**Positioning**: Bottom centre of hero section
**Behaviour**: Fades out as user starts scrolling

### Navigation Overlay
**Style**: Transparent background with logo and minimal menu
**Sticky Behaviour**: Becomes solid white with shadow on scroll
**Mobile**: Hamburger menu with full-screen overlay

## Performance Requirements

### Loading Optimisation
- Hero content visible within 1.5 seconds
- Animation loads progressively (static first, then animated)
- Critical CSS inlined for above-the-fold content
- Fonts preloaded for typography performance

### Accessibility Standards
- WCAG 2.1 AA compliance
- Proper heading hierarchy (H1 for main headline)
- Alt text for all visual elements
- Keyboard navigation support
- High contrast ratio (4.5:1 minimum)

## Analytics Tracking

### Engagement Metrics
```javascript
// Track hero section performance
trackHeroEngagement({
  time_to_scroll: Date.now() - pageLoadTime,
  button_clicks: ['primary_cta', 'secondary_cta'],
  animation_interactions: ['pause', 'replay'],
  variant_shown: abTest.getVariant('hero_headline')
});
```

### A/B Testing Events
- Headline variant shown
- CTA button text variant
- Animation vs static image test
- Primary vs secondary CTA click rates

## Responsive Breakpoints

### Large Desktop (1400px+)
- Wider max-width container
- Larger typography scale
- More generous white space

### Standard Desktop (1024px - 1399px)
- Standard layout as specified above
- Optimised for most users

### Tablet Portrait (768px - 1023px)
- Stacked layout with visual on top
- Reduced font sizes
- Adjusted spacing

### Mobile (< 768px)
- Single column layout
- Full-width CTA button
- Simplified animation
- Touch-optimised spacing

This hero section specification creates a problem-focused, emotionally engaging entry point that guides users naturally toward the qualification stage while building trust and managing cognitive load.