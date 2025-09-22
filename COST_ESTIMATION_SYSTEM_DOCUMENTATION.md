# Cost Estimation Service - Comprehensive System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Rates System](#rates-system)
3. [Benefits System](#benefits-system)
4. [Accumulators System](#accumulators-system)
5. [Data Flow and Processing](#data-flow-and-processing)
6. [Cost Calculation Logic](#cost-calculation-logic)
7. [Examples and Use Cases](#examples-and-use-cases)
8. [API Integration](#api-integration)

---

## System Overview

The Cost Estimation Service is a comprehensive healthcare cost calculation system that determines how much a member will pay for a specific medical service. It integrates three core components:

- **Rates**: Negotiated pricing between insurance and providers
- **Benefits**: Coverage rules and cost-sharing requirements
- **Accumulators**: Tracking mechanisms for annual limits and spending

### Key Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rates API     │    │  Benefits API   │    │Accumulators API │
│                 │    │                 │    │                 │
│ • Negotiated    │    │ • Coverage      │    │ • Deductible    │
│   Rates         │    │   Rules         │    │ • OOPMAX        │
│ • Payment       │    │ • Cost Sharing  │    │ • Limits        │
│   Methods       │    │ • Network       │    │ • Progress      │
│                 │    │   Categories    │    │   Tracking      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Cost Estimation │
                    │     Service     │
                    │                 │
                    │ • Rate Lookup   │
                    │ • Benefit       │
                    │   Matching      │
                    │ • Accumulator   │
                    │   Processing    │
                    │ • Cost          │
                    │   Calculation   │
                    └─────────────────┘
```

---

## Rates System

### Definition
Rates represent the **negotiated pricing** between insurance companies and healthcare providers for specific services.

### Rate Types

#### 1. Amount-Based Rates
- **Definition**: Fixed dollar amount for a service
- **Example**: $150 for a doctor visit
- **Payment Method**: "AMT" (Amount)

#### 2. Percentage-Based Rates
- **Definition**: Percentage of billed charges
- **Example**: 80% of billed charges
- **Payment Method**: "PCT" (Percentage)

### Rate Lookup Process

#### Input Criteria
```json
{
  "membershipId": "5~265646860+10+725+20250101+799047+BA+42",
  "serviceCode": "99213",
  "serviceType": "CPT4",
  "providerInfo": {
    "serviceLocation": "0003543634",
    "providerType": "PCP",
    "speciality": {"code": "207Q00000X"},
    "providerNetworks": {"networkID": "00387"}
  },
  "zipCode": "12345",
  "benefitProductType": "Medical"
}
```

#### Rate Selection Hierarchy
1. **Provider-Specific Rate**: Exact provider match
2. **Specialty-Based Rate**: Provider specialty match
3. **Provider Type Rate**: General provider type
4. **Default Rate**: Fallback rate

#### Database Queries
The system uses multiple SQL queries to find the best rate:

```sql
-- Provider-specific rate
SELECT rate, paymentMethod, rateType 
FROM negotiated_rates 
WHERE providerId = ? AND serviceCode = ? AND networkId = ?

-- Specialty-based rate
SELECT rate, paymentMethod, rateType 
FROM negotiated_rates 
WHERE specialtyCode = ? AND serviceCode = ? AND networkId = ?

-- Provider type rate
SELECT rate, paymentMethod, rateType 
FROM negotiated_rates 
WHERE providerType = ? AND serviceCode = ? AND networkId = ?

-- Default rate
SELECT rate, paymentMethod, rateType 
FROM default_rates 
WHERE serviceCode = ? AND networkId = ?
```

### Rate Response Structure
```json
{
  "paymentMethod": "AMT",
  "rate": 150.0,
  "rateType": "AMOUNT",
  "isRateFound": true,
  "isProviderInfoFound": true
}
```

### Examples

#### Example 1: Fixed Amount Rate
```json
{
  "serviceCode": "99213",
  "description": "Office visit",
  "rate": 150.0,
  "rateType": "AMOUNT",
  "paymentMethod": "AMT"
}
```
**Interpretation**: This service costs exactly $150.

#### Example 2: Percentage Rate
```json
{
  "serviceCode": "99214",
  "description": "Extended office visit",
  "rate": 80.0,
  "rateType": "PERCENTAGE",
  "paymentMethod": "PCT"
}
```
**Interpretation**: Insurance pays 80% of billed charges.

---

## Benefits System

### Definition
Benefits define the **coverage rules** and **cost-sharing requirements** for specific services under a member's insurance plan.

### Benefit Structure

#### Core Benefit Information
```json
{
  "benefitName": "MEDICAL ANCILLARY",
  "benefitCode": 1,
  "isInitialBenefit": "Y",
  "benefitTier": {
    "benefitTierName": "Standard"
  },
  "networkCategory": "InNetwork",
  "prerequisites": [
    {
      "type": "precert",
      "isRequired": "N"
    }
  ]
}
```

#### Coverage Rules
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
    "copayCountToDeductibleIndicator": "N",
    "copayContinueWhenDeductibleMetIndicator": "Y",
    "copayContinueWhenOutOfPocketMaxMetIndicator": "N",
    "isDeductibleBeforeCopay": "Y",
    "isServiceCovered": "Y"
  }
}
```

### Coverage Rule Definitions

#### Cost Sharing Rules
- **costShareCopay**: Fixed amount member pays per service
- **costShareCoinsurance**: Percentage member pays after deductible

#### Out-of-Pocket Rules
- **copayAppliesOutOfPocket**: Whether copay counts toward OOPMAX
- **coinsAppliesOutOfPocket**: Whether coinsurance counts toward OOPMAX
- **deductibleAppliesOutOfPocket**: Whether deductible counts toward OOPMAX

#### Deductible Rules
- **copayCountToDeductibleIndicator**: Whether copay counts toward deductible
- **isDeductibleBeforeCopay**: Whether deductible must be met before copay applies

#### Continuation Rules
- **copayContinueWhenDeductibleMetIndicator**: Whether copay continues after deductible met
- **copayContinueWhenOutOfPocketMaxMetIndicator**: Whether copay continues after OOPMAX met

### Benefit Selection Process

#### 1. Network Category Matching
```python
def match_network_category(benefit, is_out_of_network):
    if benefit.networkCategory == "InNetwork" and not is_out_of_network:
        return True
    elif benefit.networkCategory == "OutofNetwork" and is_out_of_network:
        return True
    return False
```

#### 2. Provider Tier Matching
```python
def match_provider_tier(benefit, provider_tier):
    # Match based on provider network participation tier
    return benefit.providerTier == provider_tier
```

#### 3. Service Code Matching
```python
def match_service_code(benefit, service_code):
    for service_info in benefit.serviceInfo:
        for service_code_info in service_info.serviceCodeInfo:
            if service_code_info.code == service_code:
                return True
    return False
```

### Benefit Response Structure
```json
{
  "serviceInfo": [
    {
      "serviceCodeInfo": [
        {
          "code": "99213",
          "type": "CPT4",
          "modifier": {}
        }
      ],
      "placeOfService": [
        {
          "code": "11"
        }
      ],
      "providerType": [
        {
          "code": "PCP"
        }
      ],
      "providerSpecialty": [
        {
          "code": "207Q00000X"
        }
      ],
      "benefit": [
        {
          "benefitName": "MEDICAL ANCILLARY",
          "benefitCode": 1,
          "coverage": {
            "costShareCopay": 100.0,
            "costShareCoinsurance": 20.0,
            "isServiceCovered": "Y"
          }
        }
      ]
    }
  ]
}
```

---

## Accumulators System

### Definition
Accumulators are **tracking mechanisms** that monitor member spending toward annual benefit limits during a coverage period.

### Accumulator Types

#### 1. Deductible Accumulator
**Purpose**: Tracks spending toward annual deductible

```json
{
  "code": "Deductible",
  "level": "Individual",
  "limitValue": 500.0,
  "currentValue": 200.0,
  "calculatedValue": 300.0,
  "frequency": "Calendar Year",
  "effectivePeriod": {
    "datetimeBegin": "2025-01-01",
    "datetimeEnd": "2025-12-31"
  }
}
```

**Fields Explanation**:
- **limitValue**: Total deductible amount ($500)
- **currentValue**: Amount used so far ($200)
- **calculatedValue**: Remaining amount ($300)

#### 2. Out-of-Pocket Maximum (OOPMAX) Accumulator
**Purpose**: Tracks total out-of-pocket spending

```json
{
  "code": "OOPMAX",
  "level": "Family",
  "limitValue": 9000.0,
  "currentValue": 8500.0,
  "calculatedValue": 500.0,
  "frequency": "Calendar Year"
}
```

#### 3. Limit Accumulator
**Purpose**: Tracks usage limits (visits, dollar limits)

```json
{
  "code": "Limit",
  "level": "Individual",
  "limitValue": 20.0,
  "currentValue": 15.0,
  "calculatedValue": 5.0,
  "limitType": "Counter",
  "frequency": "Calendar Year"
}
```

### Accumulator Levels

#### Individual Level
- Tracks spending for a single person
- Example: Individual deductible of $500

#### Family Level
- Tracks spending for entire family
- Example: Family deductible of $1,500
- **Precedence**: Family limits take precedence over individual limits

### Accumulator Matching Process

#### 1. Benefit-Accumulator Matching
```python
def match_accumulators(benefit, accumulator_response):
    matched_accumulators = []
    
    for related_accumulator in benefit.coverage.relatedAccumulators:
        for accumulator in accumulator_response.accumulators:
            if accumulator.matches(related_accumulator):
                matched_accumulators.append(accumulator)
    
    return matched_accumulators
```

#### 2. Matching Criteria
```python
def matches(self, other):
    return (
        other.code == self.code and
        other.level == self.level and
        other.accumExCode == self.accumExCode and
        other.deductibleCode == self.deductibleCode
    )
```

### Accumulator Response Structure
```json
{
  "readAccumulatorsResponse": {
    "memberships": {
      "dependents": [
        {
          "membershipIdentifier": {
            "idValue": "5~265646860+10+725+20250101+799047+BA+42"
          },
          "accumulators": [
            {
              "level": "Individual",
              "code": "Deductible",
              "limitValue": 500.0,
              "currentValue": 0.0,
              "calculatedValue": 500.0,
              "frequency": "Calendar Year",
              "effectivePeriod": {
                "datetimeBegin": "2025-01-01",
                "datetimeEnd": "2025-12-31"
              }
            }
          ]
        }
      ]
    }
  }
}
```

---

## Data Flow and Processing

### 1. Request Processing
```
Cost Estimation Request
         │
         ▼
┌─────────────────┐
│ Parse Request   │
│ • Service Info  │
│ • Provider Info │
│ • Member Info   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Extract Data    │
│ • Service Code  │
│ • Provider ID   │
│ • Network Info  │
└─────────────────┘
```

### 2. API Calls
```
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rate Lookup   │    │  Benefit Query  │    │Accumulator Query│
│                 │    │                 │    │                 │
│ • Provider      │    │ • Coverage      │    │ • Deductible    │
│   Specific      │    │   Rules         │    │ • OOPMAX        │
│ • Specialty     │    │ • Cost Sharing  │    │ • Limits        │
│   Based         │    │ • Network       │    │ • Progress      │
│ • Default       │    │   Category      │    │   Tracking      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3. Data Integration
```
         │
         ▼
┌─────────────────┐
│ Benefit-Accumulator │
│ Matcher Service     │
│                     │
│ • Match Benefits    │
│ • Match Accumulators│
│ • Create Selected   │
│   Benefits          │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Calculation     │
│ Service         │
│                 │
│ • Process Each  │
│   Benefit       │
│ • Calculate     │
│   Member Pay    │
│ • Apply Rules   │
└─────────────────┘
```

### 4. Handler Chain Processing
```
         │
         ▼
┌─────────────────┐
│ Service Coverage│
│ Handler         │
│ • Check if      │
│   covered       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Benefit         │
│ Limitation      │
│ Handler         │
│ • Check limits  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ OOPMAX Handler  │
│ • Check OOPMAX  │
│   status        │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Deductible      │
│ Handler         │
│ • Apply         │
│   deductible    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Cost Share      │
│ Handler         │
│ • Apply copay   │
│ • Apply         │
│   coinsurance   │
└─────────────────┘
```

---

## Cost Calculation Logic

### Calculation Flow

#### 1. Service Amount Determination
```python
def get_service_amount(rate, rate_type, billed_amount):
    if rate_type == "AMOUNT":
        return rate
    elif rate_type == "PERCENTAGE":
        return (rate / 100) * billed_amount
    else:
        return billed_amount
```

#### 2. Deductible Application
```python
def apply_deductible(service_amount, deductible_remaining):
    if deductible_remaining > 0:
        deductible_applied = min(service_amount, deductible_remaining)
        remaining_service = service_amount - deductible_applied
        return deductible_applied, remaining_service
    return 0, service_amount
```

#### 3. Copay Application
```python
def apply_copay(service_amount, copay_amount, deductible_met):
    if deductible_met and copay_amount > 0:
        return min(copay_amount, service_amount)
    return 0
```

#### 4. Coinsurance Application
```python
def apply_coinsurance(service_amount, coinsurance_percentage):
    if coinsurance_percentage > 0:
        return (coinsurance_percentage / 100) * service_amount
    return 0
```

### OOPMAX Logic

#### Family OOPMAX Precedence
```python
def check_oopmax_status(individual_oopmax, family_oopmax):
    # Family OOPMAX takes precedence
    if family_oopmax.calculatedValue == 0:
        return "FAMILY_MET"
    elif individual_oopmax.calculatedValue == 0:
        return "INDIVIDUAL_MET"
    else:
        return "NOT_MET"
```

#### Copay Continuation Logic
```python
def should_continue_copay(oopmax_status, copay_continue_indicator):
    if oopmax_status == "FAMILY_MET" or oopmax_status == "INDIVIDUAL_MET":
        return copay_continue_indicator == "Y"
    return True
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

## Examples and Use Cases

### Example 1: Normal Cost Sharing (Deductible Not Met)

#### Input Data
```json
{
  "service": {
    "code": "99213",
    "description": "Office visit"
  },
  "rate": {
    "rate": 300.0,
    "rateType": "AMOUNT"
  },
  "benefit": {
    "costShareCopay": 25.0,
    "costShareCoinsurance": 20.0,
    "isDeductibleBeforeCopay": "Y"
  },
  "accumulators": {
    "deductible": {
      "limitValue": 500.0,
      "calculatedValue": 500.0
    },
    "oopmax": {
      "limitValue": 3000.0,
      "calculatedValue": 3000.0
    }
  }
}
```

#### Calculation Process
1. **Service Amount**: $300 (from rate)
2. **Deductible Check**: $500 remaining, apply $300
3. **Copay**: $0 (deductible not met)
4. **Coinsurance**: $0 (deductible not met)
5. **Member Pays**: $300
6. **Insurance Pays**: $0

#### Result
```json
{
  "healthClaimLine": {
    "amountCopay": 0.0,
    "amountCoinsurance": 0.0,
    "amountResponsibility": 300.0,
    "amountpayable": 0.0
  }
}
```

### Example 2: Deductible Met, Normal Cost Sharing

#### Input Data
```json
{
  "service": {
    "code": "99213",
    "description": "Office visit"
  },
  "rate": {
    "rate": 300.0,
    "rateType": "AMOUNT"
  },
  "benefit": {
    "costShareCopay": 25.0,
    "costShareCoinsurance": 20.0,
    "isDeductibleBeforeCopay": "Y"
  },
  "accumulators": {
    "deductible": {
      "limitValue": 500.0,
      "calculatedValue": 0.0
    },
    "oopmax": {
      "limitValue": 3000.0,
      "calculatedValue": 2500.0
    }
  }
}
```

#### Calculation Process
1. **Service Amount**: $300
2. **Deductible Check**: $0 remaining, no deductible applied
3. **Copay**: $25 (deductible met)
4. **Coinsurance**: $55 (20% of $275 remaining)
5. **Member Pays**: $80
6. **Insurance Pays**: $220

#### Result
```json
{
  "healthClaimLine": {
    "amountCopay": 25.0,
    "amountCoinsurance": 55.0,
    "amountResponsibility": 80.0,
    "amountpayable": 220.0
  }
}
```

### Example 3: OOPMAX Met, No Cost Sharing

#### Input Data
```json
{
  "service": {
    "code": "99213",
    "description": "Office visit"
  },
  "rate": {
    "rate": 300.0,
    "rateType": "AMOUNT"
  },
  "benefit": {
    "costShareCopay": 25.0,
    "costShareCoinsurance": 20.0,
    "copayContinueWhenOutOfPocketMaxMetIndicator": "N"
  },
  "accumulators": {
    "oopmax": {
      "level": "Family",
      "limitValue": 3000.0,
      "calculatedValue": 0.0
    }
  }
}
```

#### Calculation Process
1. **Service Amount**: $300
2. **OOPMAX Check**: Family OOPMAX met ($0 remaining)
3. **Copay**: $0 (OOPMAX met, indicator = "N")
4. **Coinsurance**: $0 (OOPMAX met)
5. **Member Pays**: $0
6. **Insurance Pays**: $300

#### Result
```json
{
  "healthClaimLine": {
    "amountCopay": 0.0,
    "amountCoinsurance": 0.0,
    "amountResponsibility": 0.0,
    "amountpayable": 300.0
  }
}
```

### Example 4: OOPMAX Met, Copay Continues

#### Input Data
```json
{
  "service": {
    "code": "99213",
    "description": "Office visit"
  },
  "rate": {
    "rate": 300.0,
    "rateType": "AMOUNT"
  },
  "benefit": {
    "costShareCopay": 25.0,
    "costShareCoinsurance": 20.0,
    "copayContinueWhenOutOfPocketMaxMetIndicator": "Y"
  },
  "accumulators": {
    "oopmax": {
      "level": "Family",
      "limitValue": 3000.0,
      "calculatedValue": 0.0
    }
  }
}
```

#### Calculation Process
1. **Service Amount**: $300
2. **OOPMAX Check**: Family OOPMAX met ($0 remaining)
3. **Copay**: $25 (OOPMAX met, but indicator = "Y")
4. **Coinsurance**: $0 (OOPMAX met)
5. **Member Pays**: $25
6. **Insurance Pays**: $275

#### Result
```json
{
  "healthClaimLine": {
    "amountCopay": 25.0,
    "amountCoinsurance": 0.0,
    "amountResponsibility": 25.0,
    "amountpayable": 275.0
  }
}
```

---

## API Integration

### Request Structure
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
    "supportingService": {
      "code": "",
      "type": ""
    },
    "modifier": {
      "modifierCode": ""
    },
    "diagnosisCode": "",
    "placeOfService": {
      "code": "11"
    }
  },
  "providerInfo": [
    {
      "serviceLocation": "0003543634",
      "providerType": "PCP",
      "speciality": {
        "code": "207Q00000X"
      },
      "taxIdentificationNumber": "",
      "taxIdQualifier": "",
      "providerNetworks": {
        "networkID": "00387"
      },
      "providerIdentificationNumber": "0006170130",
      "nationalProviderId": "",
      "providerNetworkParticipation": {
        "providerTier": ""
      }
    }
  ]
}
```

### Response Structure
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
          "speciality": {
            "code": "207Q00000X"
          }
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

### Error Handling

#### Common Error Scenarios
1. **Rate Not Found**: No negotiated rate for service/provider combination
2. **Benefit Not Found**: No matching benefit for service/provider
3. **Accumulator Not Found**: No accumulator data for member
4. **Invalid Service Code**: Service code not recognized
5. **Provider Not Found**: Provider information not found

#### Error Response Structure
```json
{
  "error": {
    "code": "RATE_NOT_FOUND",
    "message": "No negotiated rate found for service 99213 with provider 0006170130",
    "details": {
      "serviceCode": "99213",
      "providerId": "0006170130",
      "networkId": "00387"
    }
  }
}
```

---

## Best Practices

### 1. Data Validation
- Always validate input parameters
- Check for required fields
- Validate service codes and provider IDs

### 2. Error Handling
- Implement comprehensive error handling
- Provide meaningful error messages
- Log errors for debugging

### 3. Performance Optimization
- Use caching for frequently accessed data
- Implement circuit breakers for external APIs
- Use connection pooling for database access

### 4. Testing
- Test all cost calculation scenarios
- Validate accumulator logic
- Test error conditions

### 5. Monitoring
- Monitor API response times
- Track error rates
- Monitor accumulator calculations

---

## Conclusion

The Cost Estimation Service is a complex system that integrates rates, benefits, and accumulators to provide accurate cost estimates for healthcare services. Understanding how these components work together is essential for:

- **Developers**: Building and maintaining the system
- **Business Users**: Understanding cost calculation logic
- **Support Teams**: Troubleshooting issues
- **QA Teams**: Testing system functionality

This documentation provides a comprehensive overview of the system architecture, data flow, and calculation logic, enabling effective development, testing, and maintenance of the cost estimation service.