https://aetnao365.sharepoint.com/:x:/r/sites/InteroperabilityPrj/Transparency/_layouts/15/Doc.aspx?sourcedoc=%7B52FB16D5-374A-4490-85DE-1C1F0EA150BA%7D&file=CostAPI_Requirements%20Document.xlsx&action=default&mobileredirect=true&isSPOFile=1&ovuser=fabb61b8-3afe-4e75-b934-a47f782b8cd7%2CShyen.Vakharia%40aetna.com&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI1MC8yNTA2MTIxNjQyNCIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3DConnect your OneDrive account- Excel with response contract details

Request Field

Source

Source Field

Formula (if applicable)

Notes

Megan/TiC Notes

Service object

Cost API Request (from AH, etc)

Service object

N/A

The whole service entity is the same.  

 

CostEstimateResponseInfo:providerInfo

Cost API Request (from AH, etc)

providerInfo

N/A

The whole providerInfo entity is the same, including TIN/PIN, network participation

 

coverage:isServiceCovered

Benefits API response

benefitcoverage:isservicecovered

N/A

 

 

coverage:maxCoverageAmount

Benefits API response

benefitcoverage:maxCoverageAmount

N/A

Optional field. Leave empty if we don’t receive it in the benefit api response

 

coverage:costShareCopay

Benefits API Response

coverages:costShareCopay

N/A

The CE logic needs to determine which benefit to pick

 

coverage:costShareCoinsurance

Benefits API Response

coverages:costShareCoinsurance

N/A

The CE logic needs to determine which benefit to pick

 

cost:inNetworkCost/

cost:outOfNetworkCost

provider rates logic (from Spanner)

Spanner

 

 

Row 36, row 37, row 39 in the excel (look at column B for the appropriate nomenclature)

INN:This is the provider rate value that is used to calculation the members out of pocket cost share

ONN: This is the out of network rate value that is used to calculation the members out of pocket cost share

cost:inNetworkCostType

provider rates logic (from Spanner)

Spanner

N/A

 

Can be ‘amount’ or ‘percent’

healthClaimLine:amountCopay

Calculator logic

Need to determine logic response object

calc_copay

 

 

healthClaimLine:Coinsurance

Calculator logic

Need to determine logic response object

calc_coins

 

 

healthClaimLine:amountResponsibility

Calculator logic

 

member_pays

Blank if rate is % (if percentResponsibility exists)

 

healthClaimLine:percentResponsibility

Calculator logic

 

= member_pays = cost:inNetworkCost/ cost:outOfNetworkCost WHEN cost:inNetworkCostType = 'percent'



 

When we get a percent as the service amount from provider rate logic, we cant run calculation. So we return the rate (received as a % ) as is



healthClaimLine:amountpayable

Calculator logic

Need to determine logic response object

insurance_pays

Blank if rate is % (if percentResponsibility exists)

Insurance_pay = InNetwork_cost - member_pay

accumulator:code

Accumulator api response

accumulator array → “code”

N/A

Indicates the type of accumulator. code = deductible, limit, oopmax, etc.

DONE

accumulator:level

Accumulator api response

accumulator array → “level”

N/A

 

DONE

accumulator:limitValue

Accumulator api response

accumulator array → “limitValue”

N/A

 

DONE

accumulator:limitType

Accumulator api response

accumulator array → “limitType”

N/A

 

optional. Only available when accumulator:code='limit'
DONE

accumulator:calculatedValue

Accumulator api response

accumulator array → “calculatedValue”

N/A

= remaining value of accums at the start of calculation

DONE

accumulatorCalculation:remainingValue

Calculator logic

Need to determine logic response object

rem_OOPMAXF, rem_OOPMAXI, rem_DF, rem_DI, rem_limit_val

= remaining value of accums after calculation

DONE

accumulatorCalculation:appliedValue

Calculator logic

Need to determine logic response object

= calculatedValue (from accums api response) - accumulatorCalculation:remainingValue

 

DONE

accumulatorCalculation:appliedValueType

Calculator logic

Need to determine logic response object

 

Assuming this = “accumulator:limitType”



= amount or counter

DONE

Questions:

For the accumulators, do we need to return the accumExCode? And similarly, do we need to return any of the relatedAccumulators fields mentioned in the benefit api response?

Do we need to return the benefit code for benefit type that our service chose?

I don’t see maxCoverageAmount attribute 

@Vakharia, Shyen  How do we perform calculations when the rate is given as a percentage? cc: @Berns, Ryan T  

@Vakharia, Shyen: As per Benefit API response documentation, we will receive multiple coverage for that benefit. Do we have any business rule how to pick coverage?

@Vakharia, ShyenIf rate is in percentage , do we need to populate below attributes in cost API response?. cc: @Berns, Ryan T @Paladugu, Kiran K 

@Vakharia, Shyen  Do we have any update on below ? cc: @Berns, Ryan T 

"accumulators": [
          {
            "accumulator": {
              "code": "OOP Max",
              "level": "Individual",
              "limitValue": 3000.0,
              "calculatedValue": 3000.0
            },
            "accumulatorCalculation": {
              "remainingValue": 3000.0,
              "appliedValue": 0.0
            }
          },
          {
            "accumulator": {
              "code": "OOP Max",
              "level": "Family",
              "limitValue": 9000.0,
              "calculatedValue": 9000.0
            },
            "accumulatorCalculation": {
              "remainingValue": 9000.0,
              "appliedValue": 0.0
            }
          }
        ]
