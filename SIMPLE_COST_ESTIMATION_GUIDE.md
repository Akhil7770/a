# Cost Estimation Service - Simple Guide with Easy Examples

## Table of Contents
1. [What is Cost Estimation?](#what-is-cost-estimation)
2. [The Three Main Parts](#the-three-main-parts)
3. [Rates - How Much Things Cost](#rates---how-much-things-cost)
4. [Benefits - What Your Insurance Covers](#benefits---what-your-insurance-covers)
5. [Accumulators - How Much You've Spent This Year](#accumulators---how-much-youve-spent-this-year)
6. [How It All Works Together](#how-it-all-works-together)
7. [Real Examples Step by Step](#real-examples-step-by-step)

---

## What is Cost Estimation?

**Simple Definition**: Cost estimation tells you how much YOU will pay for a doctor visit, and how much your INSURANCE will pay.

**Real Example**:
- You go to the doctor
- The visit costs $200
- Cost estimation tells you: "You pay $50, insurance pays $150"

---

## The Three Main Parts

Think of cost estimation like a recipe with 3 ingredients:

### 1. 🏥 **Rates** = "How much does this cost?"
- Like a price tag on a product
- Example: Doctor visit = $200

### 2. 📋 **Benefits** = "What does my insurance cover?"
- Like your insurance policy rules
- Example: "You pay $25 copay, insurance pays the rest"

### 3. 📊 **Accumulators** = "How much have I spent this year?"
- Like a running total of your spending
- Example: "You've spent $1,200 out of your $2,000 limit"

---

## Rates - How Much Things Cost

### What is a Rate?
A rate is the **price** for a medical service.

### Types of Rates

#### 1. **Fixed Amount Rate** (Like a fixed price)
**Example**: 
- Service: Doctor visit
- Rate: $150
- Meaning: This visit costs exactly $150

```json
{
  "service": "Doctor visit",
  "rate": 150.00,
  "type": "Fixed amount"
}
```

#### 2. **Percentage Rate** (Like a discount)
**Example**:
- Service: Surgery
- Rate: 80%
- Meaning: Insurance pays 80% of the bill

```json
{
  "service": "Surgery", 
  "rate": 80.00,
  "type": "Percentage"
}
```

### How Rates are Found

The system looks for rates in this order:

1. **Your specific doctor** → "Dr. Smith charges $150"
2. **Your doctor's specialty** → "All cardiologists charge $200"
3. **Your doctor's type** → "All specialists charge $180"
4. **Default rate** → "All doctors charge $160"

**Real Example**:
```
Looking for rate for Dr. Smith (cardiologist):
1. Check Dr. Smith specifically → Found! $150
2. Stop looking, use $150
```

---

## Benefits - What Your Insurance Covers

### What are Benefits?
Benefits are the **rules** that tell you what your insurance will pay for.

### Main Benefit Rules

#### 1. **Copay** = Fixed amount you pay
**Example**:
- Rule: "You pay $25 for doctor visits"
- Meaning: Every time you see a doctor, you pay $25

#### 2. **Coinsurance** = Percentage you pay
**Example**:
- Rule: "You pay 20% of the cost"
- Meaning: If visit costs $100, you pay $20

#### 3. **Deductible** = Amount you pay before insurance helps
**Example**:
- Rule: "You pay first $500 of medical costs each year"
- Meaning: You pay everything until you've spent $500

### Benefit Rules Explained

#### **copayAppliesOutOfPocket** = "Does copay count toward your yearly limit?"
- **"Y"** = Yes, copay counts toward your $2,000 yearly limit
- **"N"** = No, copay doesn't count toward your yearly limit

**Example**:
```
Your copay: $25
Your yearly limit: $2,000
If copayAppliesOutOfPocket = "Y":
- You pay $25
- Your remaining yearly limit becomes $1,975
```

#### **copayContinueWhenOutOfPocketMaxMetIndicator** = "Do you still pay copay after reaching yearly limit?"
- **"Y"** = Yes, you still pay copay even after reaching limit
- **"N"** = No, you stop paying copay after reaching limit

**Example**:
```
Your yearly limit: $2,000
You've spent: $2,000 (limit reached)
Your copay: $25

If copayContinueWhenOutOfPocketMaxMetIndicator = "N":
- You pay $0 (no more copay)
- Insurance pays everything

If copayContinueWhenOutOfPocketMaxMetIndicator = "Y":
- You still pay $25
- Insurance pays the rest
```

#### **isDeductibleBeforeCopay** = "Do you pay deductible before copay?"
- **"Y"** = Yes, pay deductible first, then copay
- **"N"** = No, pay copay even if deductible not met

**Example**:
```
Deductible: $500 (not met yet)
Copay: $25
Visit cost: $200

If isDeductibleBeforeCopay = "Y":
- You pay $200 (goes toward deductible)
- No copay yet

If isDeductibleBeforeCopay = "N":
- You pay $25 copay
- You pay $175 toward deductible
```

### Complete Benefit Example

```json
{
  "benefitName": "Medical Coverage",
  "coverage": {
    "costShareCopay": 25.0,                    // You pay $25 copay
    "costShareCoinsurance": 20.0,              // You pay 20% coinsurance
    "copayAppliesOutOfPocket": "Y",            // Copay counts toward yearly limit
    "copayContinueWhenOutOfPocketMaxMetIndicator": "N", // No copay after limit reached
    "isDeductibleBeforeCopay": "Y"             // Pay deductible before copay
  }
}
```

---

## Accumulators - How Much You've Spent This Year

### What are Accumulators?
Accumulators are like **running totals** that track how much you've spent toward different limits.

### Types of Accumulators

#### 1. **Deductible Accumulator**
**What it tracks**: How much you've paid toward your deductible

**Example**:
```
Your deductible: $500
You've paid so far: $200
Remaining: $300
```

```json
{
  "code": "Deductible",
  "level": "Individual",
  "limitValue": 500.0,        // Your deductible limit
  "currentValue": 200.0,      // How much you've paid
  "calculatedValue": 300.0    // How much is left
}
```

#### 2. **Out-of-Pocket Maximum (OOPMAX) Accumulator**
**What it tracks**: Your total yearly spending limit

**Example**:
```
Your yearly limit: $2,000
You've spent so far: $1,500
Remaining: $500
```

```json
{
  "code": "OOPMAX",
  "level": "Family",
  "limitValue": 2000.0,       // Your yearly limit
  "currentValue": 1500.0,     // How much you've spent
  "calculatedValue": 500.0    // How much is left
}
```

#### 3. **Limit Accumulator**
**What it tracks**: Usage limits (like number of visits)

**Example**:
```
Physical therapy limit: 20 visits per year
You've used: 15 visits
Remaining: 5 visits
```

```json
{
  "code": "Limit",
  "level": "Individual", 
  "limitValue": 20.0,         // Visit limit
  "currentValue": 15.0,       // Visits used
  "calculatedValue": 5.0      // Visits remaining
}
```

### Individual vs Family Levels

#### **Individual Level**
- Tracks spending for **one person**
- Example: Your personal deductible of $500

#### **Family Level**
- Tracks spending for **your entire family**
- Example: Family deductible of $1,500
- **Important**: Family limits are checked first!

**Example**:
```
Individual deductible: $500 (you've paid $300)
Family deductible: $1,500 (you've paid $1,200)

The system uses FAMILY deductible because it's higher priority.
You still need to pay $300 more to meet family deductible.
```

---

## How It All Works Together

### Step-by-Step Process

#### Step 1: Get the Price (Rate)
```
Service: Doctor visit
Rate: $200
```

#### Step 2: Check Your Benefits
```
Your copay: $25
Your coinsurance: 20%
Your deductible: $500 (not met yet)
```

#### Step 3: Check Your Spending (Accumulators)
```
Deductible remaining: $500
Yearly limit remaining: $1,500
```

#### Step 4: Calculate What You Pay
```
Visit cost: $200
Deductible not met, so:
- You pay: $200 (goes toward deductible)
- Insurance pays: $0
```

### The Calculation Rules

#### Rule 1: Check Deductible First
```
If deductible not met:
- You pay everything (up to deductible amount)
- No copay or coinsurance yet
```

#### Rule 2: After Deductible Met
```
If deductible is met:
- You pay copay: $25
- You pay coinsurance: 20% of remaining cost
- Insurance pays the rest
```

#### Rule 3: Check Yearly Limit (OOPMAX)
```
If yearly limit reached:
- You pay $0 (if copay stops after limit)
- OR you still pay copay (if copay continues after limit)
- Insurance pays everything else
```

---

## Real Examples Step by Step

### Example 1: First Doctor Visit of the Year

#### Your Situation:
- **Deductible**: $500 (not met)
- **Copay**: $25
- **Coinsurance**: 20%
- **Yearly limit**: $2,000

#### Doctor Visit:
- **Cost**: $200

#### What Happens:
```
Step 1: Check deductible
- Deductible remaining: $500
- Visit cost: $200
- You pay: $200 (goes toward deductible)
- Insurance pays: $0

Step 2: Update accumulators
- Deductible remaining: $300 (was $500, now $300)
- Yearly spending: $200 (was $0, now $200)
```

#### Result:
```
You pay: $200
Insurance pays: $0
Deductible remaining: $300
```

### Example 2: Second Doctor Visit (Deductible Still Not Met)

#### Your Situation:
- **Deductible**: $300 remaining
- **Copay**: $25
- **Coinsurance**: 20%

#### Doctor Visit:
- **Cost**: $400

#### What Happens:
```
Step 1: Check deductible
- Deductible remaining: $300
- Visit cost: $400
- You pay: $300 (meets deductible)
- Remaining visit cost: $100

Step 2: Apply copay and coinsurance
- Copay: $25
- Coinsurance: 20% of $75 = $15
- You pay total: $300 + $25 + $15 = $340
- Insurance pays: $60
```

#### Result:
```
You pay: $340
Insurance pays: $60
Deductible: MET! (now $0 remaining)
```

### Example 3: Third Doctor Visit (Deductible Met)

#### Your Situation:
- **Deductible**: MET ($0 remaining)
- **Copay**: $25
- **Coinsurance**: 20%
- **Yearly spending**: $540

#### Doctor Visit:
- **Cost**: $200

#### What Happens:
```
Step 1: Deductible is met, so apply copay and coinsurance
- Copay: $25
- Remaining cost: $175
- Coinsurance: 20% of $175 = $35
- You pay total: $25 + $35 = $60
- Insurance pays: $140
```

#### Result:
```
You pay: $60
Insurance pays: $140
Yearly spending: $600 (was $540, now $600)
```

### Example 4: You've Reached Your Yearly Limit

#### Your Situation:
- **Yearly limit**: $2,000 (REACHED!)
- **Copay**: $25
- **Rule**: No copay after yearly limit reached

#### Doctor Visit:
- **Cost**: $300

#### What Happens:
```
Step 1: Check yearly limit
- Yearly limit: REACHED ($2,000)
- Rule: No copay after limit reached

Step 2: Apply the rule
- You pay: $0
- Insurance pays: $300
```

#### Result:
```
You pay: $0
Insurance pays: $300
Yearly limit: Still reached
```

### Example 5: Copay Continues After Yearly Limit

#### Your Situation:
- **Yearly limit**: $2,000 (REACHED!)
- **Copay**: $25
- **Rule**: Copay continues after yearly limit reached

#### Doctor Visit:
- **Cost**: $300

#### What Happens:
```
Step 1: Check yearly limit
- Yearly limit: REACHED ($2,000)
- Rule: Copay continues after limit reached

Step 2: Apply the rule
- You pay: $25 (copay only)
- Insurance pays: $275
```

#### Result:
```
You pay: $25
Insurance pays: $275
Yearly limit: Still reached
```

---

## Simple Summary

### The Three Questions the System Asks:

1. **"How much does this cost?"** (Rate)
   - Answer: $200

2. **"What are the rules?"** (Benefits)
   - Answer: You pay $25 copay + 20% coinsurance

3. **"How much have you spent this year?"** (Accumulators)
   - Answer: You've spent $1,500 of your $2,000 limit

### The Final Calculation:
```
Cost: $200
Rules: $25 copay + 20% coinsurance
Your spending: $1,500 of $2,000 limit

Result: You pay $65, insurance pays $135
```

### Key Points to Remember:

1. **Deductible comes first** - You pay everything until deductible is met
2. **Family limits are checked before individual limits**
3. **Yearly limits can stop all payments** (depending on rules)
4. **Copay can continue or stop** after yearly limit (depending on rules)

This system ensures you never pay more than your insurance plan allows, and helps you understand exactly what you'll owe before you get the bill!