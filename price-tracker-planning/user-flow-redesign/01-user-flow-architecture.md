# User Flow Architecture Plan

## Overview
Complete redesign of the power station price tracker to transform from a "price comparison tool" into a "power backup advisor" that guides users from problem identification through to email signup.

## Current Problems
- **Backwards flow**: Leads with solution (price tracking) before establishing problem
- **Cognitive overload**: 30 products displayed immediately without context
- **No user qualification**: Users must self-select from overwhelming options
- **Weak value proposition**: "Compare prices" vs "Never lose power again"
- **Premature email capture**: Asking for signup before demonstrating value

## New Flow Strategy

### 1. PROBLEM-FIRST APPROACH
- Lead with real problems: power cuts, camping, medical needs
- Emotional hooks before technical features
- Social proof through use cases, not statistics

### 2. GUIDED QUALIFICATION
- Self-selection through clear use case categories
- Progressive data capture based on needs
- Maximum 5 curated recommendations per path

### 3. VALUE-DRIVEN CONVERSION
- "Track your shortlist" vs generic email signup
- Product-specific value propositions
- Social proof at decision moments

## User Journey Stages

```
AWARENESS → QUALIFICATION → RECOMMENDATION → DECISION → CONVERSION
    ↓            ↓              ↓             ↓           ↓
 Hero Hook → Use Case → Curated Choice → Confidence → Email Signup
```

### Stage 1: Awareness (Hero Section)
**Goal**: Hook visitors with relatable problems
- Problem-focused headlines
- Emotional scenarios (medical, family, work)
- Clear value proposition
- Low-commitment CTA

### Stage 2: Qualification (Use Case Selector)  
**Goal**: Self-segment users by needs
- 4 clear use case categories
- Progressive data capture
- Visual card-based selection
- Personalisation foundation

### Stage 3: Recommendation (Curated Choices)
**Goal**: Present perfect matches, not options
- Maximum 5 recommendations
- Clear reasoning for each choice
- Benefit-focused specifications
- Comparison tools for finalists

### Stage 4: Decision Support (Confidence Building)
**Goal**: Address objections and build trust
- Real user testimonials
- Expert validation
- Technical education
- Risk reversal offers

### Stage 5: Conversion (Email Capture)
**Goal**: Low-friction, value-first signup
- Pre-populated with user's interests
- Clear value exchange
- Contextual incentives
- Progressive onboarding

## Key Architectural Changes

### FROM: Generic Product Listing
**Old**: 30 products, complex filters, technical specs
**New**: Personalised recommendations, benefit-focused, guided choice

### FROM: Feature-Led Marketing
**Old**: "Price tracking", "30 products", "5 retailers"
**New**: "Never powerless", "Perfect for your needs", "Real user success"

### FROM: Self-Service Discovery
**Old**: Users figure out what they need
**New**: Site helps users understand their requirements

### FROM: Conversion Through Comparison
**Old**: Compare everything, choose cheapest
**New**: Find perfect match, track best deals

## Success Metrics

### Primary KPI
- **Email signup conversion rate**: Target 15%+ (vs current ~3%)

### Supporting Metrics
- Use case selection rate: >60%
- Recommendation engagement: >80% view 2+ products
- Time to conversion: <5 minutes average
- Email confirmation rate: >90%

### User Experience Metrics
- Task completion rate: >85%
- User satisfaction score: >4.5/5
- Recommendation accuracy: >90% user agreement

## Implementation Priority

1. **Phase 1**: Hero section + Use case selector (Week 1-2)
2. **Phase 2**: Recommendation engine + Product matching (Week 3-4)  
3. **Phase 3**: Confidence building + Social proof (Week 5)
4. **Phase 4**: Email capture + Onboarding (Week 6)
5. **Phase 5**: A/B testing + Optimisation (Ongoing)

## Measurement Framework

### Conversion Funnel Tracking
```
Landing → Use Case → Recommendations → Email → Confirmation
  100%      60%         45%          15%      13%
```

### A/B Testing Plan
- Hero headlines (3 variants)
- Use case presentations (visual vs text)
- Recommendation count (3 vs 4 vs 5)
- CTA button text and placement
- Social proof types and positioning

This architecture transforms the user experience from overwhelming product browsing to guided problem-solving, dramatically improving conversion potential while building a higher-quality email list of engaged prospects.