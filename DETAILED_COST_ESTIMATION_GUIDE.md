# Cost Estimation Service - Complete Detailed Guide

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Request Processing](#request-processing)
3. [Rates System - Complete Details](#rates-system---complete-details)
4. [Benefits System - Complete Details](#benefits-system---complete-details)
5. [Accumulators System - Complete Details](#accumulators-system---complete-details)
6. [Handler Chain Processing](#handler-chain-processing)
7. [Cost Calculation Logic](#cost-calculation-logic)
8. [Response Generation](#response-generation)

---

## System Architecture

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                    Cost Estimation Service                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Rate Lookup │  │Benefit Match│  │Accumulator  │        │
│  │   Service   │  │   Service   │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Calculation Service (Handler Chain)           │ │
│  │  Service → Benefit → OOPMAX → Deductible → Cost Share  │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Response Builder Service                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Processing

### Input Request Structure
```json
{
  "membershipId": "5~265646860+10+725+20250101+799047+BA+42",
  "zipCode": "12345",
  "benefitProductType": "Medical",
  "languageCode": "11",
  "service": {
    "code": "99213",
    "type": "CPT4", 
    "description": "Office visit",
    "supportingService": {"code": "", "type": ""},
    "modifier": {"modifierCode": ""},
    "diagnosisCode": "",
    "placeOfService": {"code": "11"}
  },
  "providerInfo": [
    {
      "serviceLocation": "0003543634",
      "providerType": "PCP",
      "speciality": {"code": "207Q00000X"},
      "taxIdentificationNumber": "",
      "taxIdQualifier": "",
      "providerNetworks": {"networkID": "00387"},
      "providerIdentificationNumber": "0006170130",
      "nationalProviderId": "",
      "providerNetworkParticipation": {"providerTier": ""}
    }
  ]
}
```

### Field Definitions

#### Service Information
- **code**: Medical service code (CPT, HCPCS, etc.)
- **type**: Code type (CPT4, HCPCS, etc.)
- **description**: Human-readable service description
- **supportingService**: Additional service codes if applicable
- **modifier**: Service modifiers that affect billing
- **diagnosisCode**: ICD-10 diagnosis code
- **placeOfService**: Where service is performed (office, hospital, etc.)

#### Provider Information
- **serviceLocation**: Provider's service location ID
- **providerType**: Type of provider (PCP, Specialist, etc.)
- **speciality**: Provider's medical specialty code
- **taxIdentificationNumber**: Provider's tax ID
- **providerNetworks**: Network the provider belongs to
- **providerIdentificationNumber**: Unique provider identifier
- **nationalProviderId**: National provider identifier
- **providerNetworkParticipation**: Provider's network tier

---

## Rates System - Complete Details

### Rate Types and Payment Methods

#### 1. Amount-Based Rates (AMT)
```json
{
  "paymentMethod": "AMT",
  "rate": 150.00,
  "rateType": "AMOUNT",
  "isRateFound": true,
  "isProviderInfoFound": true
}
```

**Details**:
- **paymentMethod**: "AMT" = Amount-based payment
- **rate**: Fixed dollar amount for the service
- **rateType**: "AMOUNT" = Fixed amount rate
- **isRateFound**: Whether a rate was found in database
- **isProviderInfoFound**: Whether provider information was found

#### 2. Percentage-Based Rates (PCT)
```json
{
  "paymentMethod": "PCT", 
  "rate": 80.00,
  "rateType": "PERCENTAGE",
  "isRateFound": true,
  "isProviderInfoFound": true
}
```

**Details**:
- **paymentMethod**: "PCT" = Percentage-based payment
- **rate**: Percentage of billed charges (80% = 80%)
- **rateType**: "PERCENTAGE" = Percentage rate
- **isRateFound**: Whether a rate was found in database
- **isProviderInfoFound**: Whether provider information was found

### Rate Lookup Hierarchy

#### 1. Provider-Specific Rate
```sql
SELECT rate, paymentMethod, rateType 
FROM negotiated_rates 
WHERE providerId = '0006170130' 
  AND serviceCode = '99213' 
  AND networkId = '00387'
```

#### 2. Specialty-Based Rate
```sql
SELECT rate, paymentMethod, rateType 
FROM negotiated_rates 
WHERE specialtyCode = '207Q00000X' 
  AND serviceCode = '99213' 
  AND networkId = '00387'
```

#### 3. Provider Type Rate
```sql
SELECT rate, paymentMethod, rateType 
FROM negotiated_rates 
WHERE providerType = 'PCP' 
  AND serviceCode = '99213' 
  AND networkId = '00387'
```

#### 4. Default Rate
```sql
SELECT rate, paymentMethod, rateType 
FROM default_rates 
WHERE serviceCode = '99213' 
  AND networkId = '00387'
```

### Rate Calculation Logic
```python
def calculate_service_amount(rate, rate_type, billed_amount):
    if rate_type == "AMOUNT":
        return rate  # Use fixed amount
    elif rate_type == "PERCENTAGE":
        return (rate / 100) * billed_amount  # Calculate percentage
    else:
        return billed_amount  # Use billed amount as fallback
```

---

## Benefits System - Complete Details

### Benefit Structure

#### Core Benefit Information
```json
{
  "benefitName": "MEDICAL ANCILLARY",
  "benefitCode": 1,
  "isInitialBenefit": "Y",
  "benefitTier": {"benefitTierName": "Standard"},
  "networkCategory": "InNetwork",
  "prerequisites": [
    {
      "type": "precert",
      "isRequired": "N"
    }
  ],
  "benefitProvider": "",
  "serviceProvider": [{"providerDesignation": ""}]
}
```

**Field Definitions**:
- **benefitName**: Name of the benefit plan
- **benefitCode**: Unique identifier for the benefit
- **isInitialBenefit**: "Y" = Primary benefit, "N" = Secondary benefit
- **benefitTier**: Tier level of the benefit (Standard, Premium, etc.)
- **networkCategory**: "InNetwork" or "OutofNetwork"
- **prerequisites**: Required pre-authorizations or certifications
- **benefitProvider**: Provider of the benefit
- **serviceProvider**: Service provider designations

### Coverage Rules - Complete Definitions

#### Cost Sharing Rules
```json
{
  "coverage": {
    "sequenceNumber": 1,
    "benefitDescription": "MEDICAL ANCILLARY",
    "costShareCopay": 100.0,
    "costShareCoinsurance": 20.0,
    "copayAppliesOutOfPocket": "Y",
    "coinsAppliesOutOfPocket": "Y", 
    "deductibleAppliesOutOfPocket": "Y",
    "deductibleAppliesOutOfPocketOtherIndicator": "N",
    "copayCountToDeductibleIndicator": "N",
    "copayContinueWhenDeductibleMetIndicator": "Y",
    "copayContinueWhenOutOfPocketMaxMetIndicator": "N",
    "coinsuranceToOutOfPocketOtherIndicator": "N",
    "copayToOutofPocketOtherIndicator": "N",
    "isDeductibleBeforeCopay": "Y",
    "benefitLimitation": "",
    "isServiceCovered": "Y"
  }
}
```

#### Detailed Field Explanations

##### Cost Sharing Fields
- **costShareCopay**: Fixed dollar amount member pays per service
- **costShareCoinsurance**: Percentage member pays after deductible (20.0 = 20%)

##### Out-of-Pocket Application Fields
- **copayAppliesOutOfPocket**: "Y" = Copay counts toward OOPMAX, "N" = Does not count
- **coinsAppliesOutOfPocket**: "Y" = Coinsurance counts toward OOPMAX, "N" = Does not count
- **deductibleAppliesOutOfPocket**: "Y" = Deductible counts toward OOPMAX, "N" = Does not count

##### Deductible Rules
- **copayCountToDeductibleIndicator**: "Y" = Copay counts toward deductible, "N" = Does not count
- **isDeductibleBeforeCopay**: "Y" = Deductible must be met before copay applies, "N" = Copay applies regardless

##### Continuation Rules
- **copayContinueWhenDeductibleMetIndicator**: "Y" = Copay continues after deductible met, "N" = Copay stops
- **copayContinueWhenOutOfPocketMaxMetIndicator**: "Y" = Copay continues after OOPMAX met, "N" = Copay stops

##### Other Fields
- **deductibleAppliesOutOfPocketOtherIndicator**: "Y" = Deductible applies to "other" OOP bucket, "N" = Does not apply
- **coinsuranceToOutOfPocketOtherIndicator**: "Y" = Coinsurance applies to "other" OOP bucket, "N" = Does not apply
- **copayToOutofPocketOtherIndicator**: "Y" = Copay applies to "other" OOP bucket, "N" = Does not apply

### Benefit Matching Process

#### 1. Network Category Matching
```python
def match_network_category(benefit, is_out_of_network):
    if benefit.networkCategory == "InNetwork" and not is_out_of_network:
        return True
    elif benefit.networkCategory == "OutofNetwork" and is_out_of_network:
        return True
    return False
```

#### 2. Service Code Matching
```python
def match_service_code(benefit, service_code):
    for service_info in benefit.serviceInfo:
        for service_code_info in service_info.serviceCodeInfo:
            if service_code_info.code == service_code:
                return True
    return False
```

#### 3. Provider Type Matching
```python
def match_provider_type(benefit, provider_type):
    for service_info in benefit.serviceInfo:
        for provider_type_item in service_info.providerType:
            if provider_type_item.code == provider_type:
                return True
    return False
```

#### 4. Provider Specialty Matching
```python
def match_provider_specialty(benefit, specialty_code):
    for service_info in benefit.serviceInfo:
        for specialty_item in service_info.providerSpecialty:
            if specialty_item.code == specialty_code:
                return True
    return False
```

---

## Accumulators System - Complete Details

### Accumulator Types

#### 1. Deductible Accumulator
```json
{
  "level": "Individual",
  "code": "Deductible",
  "frequency": "Calendar Year",
  "relationshipToSubscriber": "W",
  "suffix": "799047",
  "benefitProductType": "Medical",
  "description": "Deductible",
  "currentValue": 200.0,
  "limitValue": 500.0,
  "calculatedValue": 300.0,
  "effectivePeriod": {
    "datetimeBegin": "2025-01-01",
    "datetimeEnd": "2025-12-31"
  },
  "savingsLevel": "In Network",
  "networkIndicator": "InNetwork",
  "networkIndicatorCode": "I",
  "accumExCode": "L02"
}
```

**Field Definitions**:
- **level**: "Individual" or "Family"
- **code**: Accumulator type ("Deductible", "OOPMAX", "Limit")
- **frequency**: Accumulation period ("Calendar Year", "Plan Year")
- **relationshipToSubscriber**: Relationship to primary subscriber ("W" = Self)
- **suffix**: Member suffix identifier
- **benefitProductType**: Type of benefit ("Medical", "Pharmacy", etc.)
- **description**: Human-readable description
- **currentValue**: Amount used/spent so far
- **limitValue**: Total limit amount
- **calculatedValue**: Remaining amount (limitValue - currentValue)
- **effectivePeriod**: Time period for accumulation
- **savingsLevel**: Network level ("In Network", "Out of Network")
- **networkIndicator**: Network status
- **networkIndicatorCode**: Network code ("I" = In-Network, "O" = Out-of-Network)
- **accumExCode**: Accumulator exclusion code

#### 2. OOPMAX Accumulator
```json
{
  "level": "Family",
  "code": "OOPMAX",
  "frequency": "Calendar Year",
  "relationshipToSubscriber": "W",
  "suffix": "799047",
  "benefitProductType": "Medical",
  "description": "OOPMAX",
  "currentValue": 1500.0,
  "limitValue": 2000.0,
  "calculatedValue": 500.0,
  "effectivePeriod": {
    "datetimeBegin": "2025-01-01",
    "datetimeEnd": "2025-12-31"
  },
  "savingsLevel": "In Network",
  "networkIndicator": "InNetwork",
  "networkIndicatorCode": "I",
  "accumExCode": "L04"
}
```

#### 3. Limit Accumulator
```json
{
  "level": "Individual",
  "code": "Limit",
  "frequency": "Calendar Year",
  "relationshipToSubscriber": "W",
  "suffix": "799047",
  "benefitProductType": "Medical",
  "description": "Physical Therapy Visits",
  "currentValue": 15.0,
  "limitValue": 20.0,
  "calculatedValue": 5.0,
  "limitType": "Counter",
  "effectivePeriod": {
    "datetimeBegin": "2025-01-01",
    "datetimeEnd": "2025-12-31"
  },
  "savingsLevel": "In Network",
  "networkIndicator": "InNetwork",
  "networkIndicatorCode": "I",
  "accumExCode": "L05"
}
```

**Additional Fields for Limits**:
- **limitType**: "Counter" = Visit-based limit, "Dollar" = Dollar-based limit

### Accumulator Matching Logic

#### Matching Criteria
```python
def matches(self, other):
    return (
        other.code == self.code and
        other.level == self.level and
        (other.accumExCode == self.accumExCode or 
         (other.accumExCode == "" and self.accumExCode is None)) and
        (other.deductibleCode == self.deductibleCode or
         (other.deductibleCode == "" and self.deductibleCode is None))
    )
```

#### Family vs Individual Precedence
```python
def get_effective_oopmax(individual_oopmax, family_oopmax):
    # Family OOPMAX takes precedence
    if family_oopmax is not None:
        return family_oopmax
    elif individual_oopmax is not None:
        return individual_oopmax
    else:
        return None
```

---

## Handler Chain Processing

### Handler Chain Order
```
ServiceCoverageHandler → BenefitLimitationHandler → OOPMaxHandler → DeductibleHandler → CostShareCoPayHandler
```

### 1. Service Coverage Handler
```python
def process(self, context: InsuranceContext) -> InsuranceContext:
    if not context.is_service_covered:
        context.member_pays = context.service_amount
        context.calculation_complete = True
        context.error_code = "SERVICE_NOT_COVERED"
        return context
    
    return context  # Continue to next handler
```

**Purpose**: Check if the service is covered under the benefit plan.

### 2. Benefit Limitation Handler
```python
def process(self, context: InsuranceContext) -> InsuranceContext:
    if "limit" not in context.accum_code:
        return context  # No limits, continue
    
    if context.limit_calculated == 0:
        context.calculation_complete = True  # Limit reached, stop
        return context
    
    if context.limit_type == "dollar":
        if context.service_amount > context.limit_calculated:
            return self._apply_partial_limit(context)
        else:
            return self._apply_within_limit(context)
    
    elif context.limit_type == "counter":
        return self._apply_limitation(context)
```

**Purpose**: Check if benefit limits (visits, dollar amounts) have been reached.

### 3. OOPMAX Handler
```python
def process(self, context: InsuranceContext) -> InsuranceContext:
    if "oopmax" not in context.accum_code:
        return self._deductible_handler.handle(context)
    
    if (context.oopmax_family_calculated == 0 or 
        context.oopmax_individual_calculated == 0):
        return self._oopmax_copay_handler.handle(context)
    
    return self._deductible_handler.handle(context)
```

**Purpose**: Check if out-of-pocket maximum has been reached.

### 4. Deductible Handler
```python
def process(self, context: InsuranceContext) -> InsuranceContext:
    if "deductible" not in context.accum_code:
        return self._cost_share_co_pay_handler.handle(context)
    
    if (context.deductible_family_calculated == 0 or 
        context.deductible_individual_calculated == 0):
        return self._deductible_cost_share_co_pay_handler.handle(context)
    
    if not context.is_deductible_before_copay:
        if context.cost_share_copay > 0:
            return self._deductible_co_pay_handler.handle(context)
        else:
            return self._deductible_oopmax_handler.handle(context)
    else:
        return self._deductible_oopmax_handler.handle(context)
```

**Purpose**: Apply deductible logic and determine next step.

### 5. Cost Share CoPay Handler
```python
def process(self, context: InsuranceContext) -> InsuranceContext:
    if (context.cost_share_copay > 0 and 
        context.cost_share_copay > context.service_amount):
        if context.service_amount < min_oopmax:
            return self._apply_member_pays_service_amount(context)
        else:
            return self._apply_member_pays_oopmax_difference(context)
    else:
        if (context.cost_share_copay < context.oopmax_individual_calculated and
            context.cost_share_copay < context.oopmax_family_calculated):
            context = self._apply_member_pays_cost_share_copay(context)
            return self._deductible_co_insurance_handler.handle(context)
        else:
            return self._apply_member_pays_oopmax_difference(context)
```

**Purpose**: Apply copay and coinsurance logic.

---

## Cost Calculation Logic

### Service Amount Calculation
```python
def calculate_service_amount(rate, rate_type, billed_amount):
    if rate_type == "AMOUNT":
        return rate
    elif rate_type == "PERCENTAGE":
        return (rate / 100) * billed_amount
    else:
        return billed_amount
```

### Deductible Application
```python
def apply_deductible(service_amount, deductible_remaining):
    if deductible_remaining > 0:
        deductible_applied = min(service_amount, deductible_remaining)
        remaining_service = service_amount - deductible_applied
        return deductible_applied, remaining_service
    return 0, service_amount
```

### Copay Application
```python
def apply_copay(service_amount, copay_amount, deductible_met, oopmax_met, continue_after_oopmax):
    if deductible_met and copay_amount > 0:
        if oopmax_met and not continue_after_oopmax:
            return 0  # No copay after OOPMAX
        else:
            return min(copay_amount, service_amount)
    return 0
```

### Coinsurance Application
```python
def apply_coinsurance(service_amount, coinsurance_percentage, oopmax_met):
    if oopmax_met:
        return 0  # No coinsurance after OOPMAX
    elif coinsurance_percentage > 0:
        return (coinsurance_percentage / 100) * service_amount
    return 0
```

### Final Cost Calculation
```python
def calculate_final_cost(service_amount, deductible_applied, copay_applied, coinsurance_applied):
    member_responsibility = deductible_applied + copay_applied + coinsurance_applied
    insurance_payable = service_amount - member_responsibility
    
    return {
        "amountCopay": copay_applied,
        "amountCoinsurance": coinsurance_applied,
        "amountResponsibility": member_responsibility,
        "amountpayable": insurance_payable
    }
```

---

## Response Generation

### Final Response Structure
```json
{
  "costEstimateResponse": {
    "service": {
      "code": "99213",
      "type": "CPT4",
      "description": "Office visit"
    },
    "costEstimateResponseInfo": [
      {
        "providerInfo": {
          "serviceLocation": "0003543634",
          "providerType": "PCP",
          "speciality": {"code": "207Q00000X"}
        },
        "coverage": {
          "isServiceCovered": "Y",
          "maxCoverageAmount": "",
          "costShareCopay": 100.0,
          "costShareCoinsurance": 20
        },
        "cost": {
          "inNetworkCosts": 900.0,
          "outOfNetworkCosts": 0.0,
          "inNetworkCostsType": "AMOUNT"
        },
        "healthClaimLine": {
          "amountCopay": 100.0,
          "amountCoinsurance": 60.0,
          "amountResponsibility": 660.0,
          "percentResponsibility": 0.0,
          "amountpayable": 240.0
        },
        "accumulators": [
          {
            "accumulator": {
              "code": "Deductible",
              "level": "Individual",
              "limitValue": 500.0,
              "calculatedValue": 500.0
            },
            "accumulatorCalculation": {
              "remainingValue": 500.0,
              "appliedValue": 0.0
            }
          }
        ]
      }
    ]
  }
}
```

### Response Field Definitions

#### Service Information
- **code**: Service code from request
- **type**: Service type from request
- **description**: Service description from request

#### Provider Information
- **serviceLocation**: Provider location from request
- **providerType**: Provider type from request
- **speciality**: Provider specialty from request

#### Coverage Information
- **isServiceCovered**: Whether service is covered ("Y" or "N")
- **maxCoverageAmount**: Maximum coverage amount (if applicable)
- **costShareCopay**: Copay amount from benefit
- **costShareCoinsurance**: Coinsurance percentage from benefit

#### Cost Information
- **inNetworkCosts**: In-network cost amount
- **outOfNetworkCosts**: Out-of-network cost amount
- **inNetworkCostsType**: Cost type ("AMOUNT" or "PERCENTAGE")

#### Health Claim Line
- **amountCopay**: Actual copay amount member pays
- **amountCoinsurance**: Actual coinsurance amount member pays
- **amountResponsibility**: Total amount member is responsible for
- **percentResponsibility**: Percentage of total cost member pays
- **amountpayable**: Amount insurance will pay

#### Accumulators
- **accumulator**: Accumulator information
- **accumulatorCalculation**: Calculation details for the accumulator

This comprehensive guide covers every aspect of the cost estimation system, from input processing to final response generation, with detailed explanations of each component and field.