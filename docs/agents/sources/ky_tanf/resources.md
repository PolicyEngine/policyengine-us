# Kentucky TANF (K-TAP) Resource Limits

## Source
- **Regulation**: 921 KAR 2:016 - Standards of need and amount for KTAP
- **Section**: Section 3 - Resource Limitations
- **URL**: https://apps.legislature.ky.gov/law/kar/titles/921/002/016/

## Resource Limit

Per 921 KAR 2:016 Section 3(2):

| Resource Type | Maximum Amount |
|---------------|----------------|
| Liquid Assets | $10,000        |

The total amount of resources reserved by a benefit group shall not be in excess of $10,000 in liquid assets.

## Excluded Resources

The following resources are excluded from the $10,000 limit per 921 KAR 2:016 Section 3:

1. **Retirement Accounts**
   - Individual Retirement Accounts (IRAs)
   - Other qualified retirement accounts

2. **Burial and Final Expense Resources**
   - Burial funds
   - Burial spaces

3. **Education Savings**
   - 529 college savings accounts (Qualified Tuition Programs)

4. **ABLE Accounts**
   - Achieving a Better Life Experience (ABLE) accounts

5. **Individual Development Accounts (IDAs)**
   - Up to $15,000 when matched
   - Must be used for qualified purposes (homeownership, education, business)

6. **Government Compensation**
   - Various government compensation payments
   - Certain one-time payments

7. **Joint Account Treatment**
   - Joint account ownership is divided among owners
   - Only the proportional share attributable to the benefit group member is counted

## Historical Comparison

| Time Period | Resource Limit |
|-------------|----------------|
| Pre-2023    | $2,000         |
| Post-2023   | $10,000        |

The 2023 update raised the resource limit from $2,000 to $10,000, a significant change especially beneficial for:
- Older kinship caregivers who may have retirement savings
- Families trying to build emergency funds
- Grandparents raising grandchildren

## Implementation Notes

### For Simplified Implementation

Resource eligibility testing may be implemented as:

```python
# Simplified resource test
countable_resources = total_liquid_assets - excluded_resources
is_resource_eligible = countable_resources <= 10_000
```

### Excluded Resources to Track
For a more complete implementation, track:
- IRA balances (exclude)
- 529 account balances (exclude)
- ABLE account balances (exclude)
- Burial funds (exclude)

### Policy Rationale

The increase from $2,000 to $10,000 was part of the 2023 KTAP modernization effort. The previous $2,000 limit:
- Had not been updated since 1995
- Prevented families from building emergency savings
- Was particularly harmful to older kinship caregivers relying on retirement savings

The new $10,000 limit allows families to:
- Maintain modest emergency funds
- Keep retirement savings without penalty
- Better prepare for unexpected expenses
