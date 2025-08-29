# Texas LIHEAP Test Suite

Comprehensive integration tests for the Texas Low Income Home Energy Assistance Program (LIHEAP), administered by the Texas Department of Housing and Community Affairs (TDHCA).

## Test Files

### Unit Tests
- `tx_liheap_income.yaml` - Tests household income calculation from various sources
- `tx_liheap_income_eligible.yaml` - Tests income eligibility at 150% Federal Poverty Level
- `tx_liheap_categorical_eligible.yaml` - Tests categorical eligibility through SNAP/TANF/SSI
- `tx_liheap_priority_group.yaml` - Tests priority group determination (elderly, disabled, young children)
- `tx_liheap_eligible.yaml` - Tests overall eligibility combining income and categorical paths
- `tx_liheap_regular_benefit.yaml` - Tests regular benefit amount calculations
- `tx_liheap.yaml` - Tests final benefit determination

### Integration Tests
- `integration.yaml` - Comprehensive scenarios testing complete benefit calculation flows

## Test Coverage

### Income Limits (2025)
Tests verify correct application of 150% FPL thresholds:
- 1 person: $23,475/year ($1,956/month)
- 2 persons: $31,725/year ($2,644/month)
- 3 persons: $39,975/year ($3,331/month)
- 4 persons: $48,225/year ($4,019/month)
- 5 persons: $56,475/year ($4,706/month)
- 6 persons: $64,725/year ($5,394/month)
- 7 persons: $72,975/year ($6,081/month)
- 8 persons: $81,225/year ($6,769/month)

### Priority Groups
Tests verify identification of:
- Elderly households (age 60+)
- Disabled individuals
- Households with children under 6

### Benefit Amounts
Tests validate benefit calculations within documented ranges:
- Regular assistance: $200 - $1,000 base (up to $12,300 total)
- Adjustments for household size using SMI percentages
- Priority group bonuses
- Income-based scaling

### Categorical Eligibility
Tests verify automatic eligibility for recipients of:
- SNAP (Supplemental Nutrition Assistance Program)
- TANF (Temporary Assistance for Needy Families)
- SSI (Supplemental Security Income)

## Edge Cases Tested
- Income exactly at threshold (eligible)
- Income one dollar over threshold (ineligible)
- Zero income households
- Mixed income sources
- Multiple priority factors
- Large households (8+ members)
- Categorical eligibility overriding income limits

## Data Sources
All test values based on official documentation from:
- TDHCA LIHEAP program guidance
- Federal poverty guidelines (2025)
- 45 CFR 96.85 (SMI adjustment factors)
- Texas LIHEAP State Plan 2025

## Running Tests
```bash
# Run all LIHEAP tests
pytest policyengine_us/tests/policy/baseline/gov/states/tx/tdhca/liheap/

# Run specific test file
policyengine-core test policyengine_us/tests/policy/baseline/gov/states/tx/tdhca/liheap/integration.yaml -c policyengine_us

# Run with verbose output
pytest policyengine_us/tests/policy/baseline/gov/states/tx/tdhca/liheap/ -v
```