# Use Case Selector - Detailed Specification

## Section Overview
**Purpose**: Qualify users by primary need and capture requirements data
**Position**: Immediately after hero section
**Success Metric**: >60% card selection rate, >80% form completion

## Section Header Design

### Layout
```
┌─────────────────────────────────────────────────────────┐
│                    Section Header                       │
│                                                         │
│              "What Do You Need Power For?"              │
│                                                         │
│     "Different situations need different power          │
│     solutions. Tell us your main use case and we'll     │
│     show you exactly what you need."                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Typography**:
- Main heading (H2): 36px desktop, 28px mobile, weight: 700
- Supporting text: 18px, weight: 400, max-width: 600px, centred
- Background: Light grey (#f8f9fa) for section separation
- Vertical padding: 80px desktop, 60px mobile

## Card Grid Layout

### Desktop Grid (1024px+)
```
┌─────────────────────────────────────────────────────────┐
│  [Emergency Backup]    [Camping & Outdoors]           │
│        Card 1               Card 2                      │
│                                                         │
│   [Work Flexibility]    [Off-Grid Living]             │
│        Card 3               Card 4                      │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout (< 768px)
```
┌─────────────────────┐
│  [Emergency Backup] │
│       Card 1        │
├─────────────────────┤
│ [Camping & Outdoors]│
│       Card 2        │
├─────────────────────┤
│  [Work Flexibility] │
│       Card 3        │
├─────────────────────┤
│  [Off-Grid Living]  │
│       Card 4        │
└─────────────────────┘
```

**Grid Specifications**:
- Card dimensions: 280px width × 320px height
- Gap between cards: 24px
- Cards centre-aligned in container
- Equal height maintained across row

## Individual Card Specifications

### Card 1: Emergency Home Backup
```
┌─────────────────────────────────────────────┐
│ 🏠 (48px icon, centred)                     │
│                                             │
│         Emergency Home Backup               │
│     Power cuts, medical devices,            │
│        essential appliances                 │
│                                             │
│ ✓ CPAP machines & medical equipment         │
│ ✓ Keep fridge running during outages        │
│ ✓ Charge phones during storms               │
│ ✓ Home office backup power                  │
│ ✓ Elderly care & accessibility devices      │
│                                             │
│ Duration: 4-48 hours backup power           │
│ Budget: £400-£1,500                         │
│                                             │
│ [Hidden form reveals on click]              │
└─────────────────────────────────────────────┘
```

**Hidden Form Fields** (slides down when card selected):
```
How long are your typical power cuts?
[●────────────────────────●] 2hrs ──── 48hrs

What's your priority? (checkboxes)
☐ Medical equipment  ☐ Food preservation  
☐ Communication     ☐ Work from home
```

### Card 2: Camping & Outdoors
```
┌─────────────────────────────────────────────┐
│ ⛺ (48px icon, centred)                     │
│                                             │
│           Camping & Outdoors                │
│    Weekends away, festivals,                │
│          garden parties                     │
│                                             │
│ ✓ Portable fridges & cool boxes             │
│ ✓ Lights & phone charging                   │
│ ✓ Camping equipment power                   │
│ ✓ Festival & outdoor events                 │
│ ✓ Garden parties & BBQs                     │
│                                             │
│ Duration: 1-7 days portable power           │
│ Budget: £200-£800                           │
│                                             │
│ [Hidden form reveals on click]              │
└─────────────────────────────────────────────┘
```

**Hidden Form Fields**:
```
How many days away typically?
[●────────────────────────●] 1 day ──── 7 days

What needs power? (checkboxes)
☐ Portable fridge  ☐ Lighting  
☐ Device charging  ☐ Power tools
```

### Card 3: Work Flexibility
```
┌─────────────────────────────────────────────┐
│ 💻 (48px icon, centred)                     │
│                                             │
│            Work Anywhere                    │
│    Mobile office, garden studio,            │
│          remote work                        │
│                                             │
│ ✓ Laptop & monitor power all day            │
│ ✓ Garden office without mains power         │
│ ✓ Mobile workshop power tools               │
│ ✓ Photography & video equipment             │
│ ✓ Pop-up shops & market stalls              │
│                                             │
│ Duration: 8-16 hours work power             │
│ Budget: £500-£2,000                         │
│                                             │
│ [Hidden form reveals on click]              │
└─────────────────────────────────────────────┘
```

**Hidden Form Fields**:
```
How many hours work per day?
[●────────────────────────●] 4hrs ──── 16hrs

What equipment? (checkboxes)
☐ Laptop only    ☐ Laptop + Monitor  
☐ Power tools    ☐ Lighting equipment
```

### Card 4: Off-Grid Living
```
┌─────────────────────────────────────────────┐
│ 🚐 (48px icon, centred)                     │
│                                             │
│           Off-Grid Living                   │
│     Van life, boats, remote                 │
│           properties                        │
│                                             │
│ ✓ Van life & motorhome power                │
│ ✓ Boat & marine applications                │
│ ✓ Remote cabin electricity                  │
│ ✓ Off-grid workshops                        │
│ ✓ Backup for solar systems                  │
│                                             │
│ Duration: Multi-day self-sufficiency        │
│ Budget: £1,000-£5,000+                      │
│                                             │
│ [Hidden form reveals on click]              │
└─────────────────────────────────────────────┘
```

**Hidden Form Fields**:
```
How many days between charges?
[●────────────────────────●] 2 days ──── 14 days

Power requirements? (checkboxes)
☐ Basic devices      ☐ Small appliances  
☐ High power tools   ☐ Everything possible
```

## Card Visual Design Specifications

### Default State (Unselected)
```css
.use-case-card {
  background: white;
  border: 2px solid #e3e3e3;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.use-case-card:hover {
  transform: translateY(-4px);
  border-color: #3498db;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
```

### Selected State
```css
.use-case-card.selected {
  border-color: #3498db;
  background: #f8f9ff;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(52,152,219,0.2);
}

.use-case-card.selected::after {
  content: "✓";
  position: absolute;
  top: 16px;
  right: 16px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}
```

### Typography Within Cards
- Card title: 20px, weight: 700, colour: #2c3e50
- Subtitle: 16px, weight: 400, colour: #7f8c8d
- Checklist items: 14px, weight: 400, colour: #2c3e50
- Duration/Budget: 14px, weight: 600, colour: #3498db

## Interactive Behaviour

### Card Selection Flow
1. **Initial State**: All cards visible, none selected
2. **Hover State**: Card lifts, border colour changes
3. **Click/Tap**: Card selects, form slides down
4. **Form Display**: Previous selection deselects, new form shows
5. **Form Completion**: "Show My Options" button appears

### Progressive Form Enhancement

**Basic (No JavaScript)**:
- Cards link to separate pages with forms
- Form submission via POST request
- Server-side processing and redirect

**Enhanced (JavaScript Enabled)**:
- Smooth card selection animations
- Inline form reveal/hide
- Real-time validation
- AJAX form submission
- Smooth scroll to next section

### Form Validation Rules

**Emergency Backup**:
- Duration: 2-48 hours (slider validation)
- Priority: At least 1 checkbox required
- Auto-suggestion based on duration

**Camping & Outdoors**:
- Days: 1-7 days (slider validation)
- Equipment: At least 1 checkbox required
- Portable weight consideration hints

**Work Flexibility**:
- Hours: 4-16 hours (slider validation)
- Equipment: Minimum laptop selected
- Power draw calculations

**Off-Grid Living**:
- Days: 2-14 days (slider validation)
- Requirements: At least 1 checkbox required
- Capacity scaling recommendations

## Alternative "Unsure" Option

### Additional Card/Link
**Position**: Below main 4 cards, centred
**Text**: `"I'm not sure what I need - help me calculate →"`

**Destination**: Power calculator tool
```
┌─────────────────────────────────────────────┐
│               Power Calculator               │
│                                             │
│    What devices do you want to power?       │
│                                             │
│    [Device Library with Power Consumption]  │
│    ☐ Laptop (50W) - 16 hours               │
│    ☐ Phone (10W) - 80 full charges         │
│    ☐ LED TV (100W) - 8 hours               │
│    ☐ Portable Fridge (60W) - 24 hours      │
│                                             │
│    Total estimated need: 1,200Wh           │
│    Recommended category: Emergency Backup   │
│                                             │
│    [Show My Recommendations]                │
└─────────────────────────────────────────────┘
```

## Data Collection Strategy

### Explicit Data Captured
```javascript
const userRequirements = {
  useCase: 'emergency_backup' | 'camping_outdoor' | 'work_mobile' | 'off_grid',
  duration: number, // hours or days depending on use case
  budget: string, // budget range selected
  priorities: Array<string>, // checkbox selections
  timestamp: Date,
  sessionId: string
};
```

### Implicit Data Tracked
```javascript
const behaviorData = {
  timeToSelect: number, // milliseconds from page load
  cardsHovered: Array<string>, // which cards user considered
  formAbandonmentPoint: string | null, // where they stopped
  returnVisit: boolean, // repeat visitor
  mobileDevice: boolean,
  trafficSource: string
};
```

## Personalisation Opportunities

### Dynamic Content Based on Traffic Source
- **Google "power cut" search**: Emphasise emergency backup card
- **Camping blog referral**: Highlight camping card with special styling
- **LinkedIn traffic**: Promote work flexibility use case
- **Van life forums**: Feature off-grid living prominently

### Seasonal Adjustments
- **Winter months**: Emergency backup messaging stronger
- **Summer season**: Camping and outdoor emphasis
- **Storm warnings**: Emergency preparedness urgency
- **Holiday periods**: Travel and camping focus

### Geographic Personalisation
- **Rural postcodes**: Off-grid and emergency focus
- **Urban areas**: Work flexibility and convenience
- **Coastal regions**: Marine and outdoor applications
- **Scotland/Wales**: Remote property and off-grid

## Success Metrics & Analytics

### Primary Conversion Metrics
- **Card selection rate**: Target >60%
- **Form completion rate**: Target >80% (of card clickers)
- **Time to selection**: Target <90 seconds
- **Progression rate**: Target >90% continue to recommendations

### Engagement Analytics
```javascript
// Track detailed user interactions
analytics.track('use_case_interaction', {
  card_hovered: cardId,
  time_hovering: milliseconds,
  cards_compared: arrayOfCardIds,
  selection_made: boolean,
  form_completion_rate: percentage
});
```

### A/B Testing Elements
- **Card presentation**: Visual vs text-heavy
- **Icon choices**: Emoji vs SVG vs photos
- **Form complexity**: Simple vs detailed capture
- **Card order**: Priority arrangement testing
- **Copy variations**: Benefit vs feature focus

This use case selector transforms overwhelming choice into guided self-selection, capturing valuable user intent data while maintaining high engagement and progression rates.