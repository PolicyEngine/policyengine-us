# Parameter Label Metadata Improvements

## Motivation

PolicyEngine parameters require human-readable labels for two critical purposes:

1. **API v2 Database Seeding**: In an effort to improve trust for front end users, API v2 alpha aims to ensure that all parameters have defined labels.

2. **Front-end Display**: The PolicyEngine web interface displays parameter names to users when they modify policy assumptions. Without proper labels, users see cryptic paths like `gov.irs.income.amt.exemption.amount.SINGLE` instead of meaningful descriptions like "AMT exemption amount (Single)".

## Problem Analysis

An analysis of policyengine-us identified several categories of parameters that lack proper labels:

| Category | Parents | Params | Issue |
|----------|---------|--------|-------|
| Breakdowns without parent label | 12 | 445 | Has `breakdown` metadata but no `label` |
| Brackets without scale label | 8 | 68 | ParameterScale lacks `label` in metadata |
| Pseudo-breakdowns | 61 | 799 | Looks like breakdown but missing `breakdown` metadata |
| Breakdowns with `range()` dimensions | ~80 | ~5,000 | Has `breakdown` but dimensions lack semantic meaning |

This PR provides example fixes for each category to establish patterns for future work.

## Changes

### 1. Breakdown Without Parent Label

**File:** `gov/states/wi/tax/income/deductions/standard/max.yaml`

**Problem:** This parameter has `breakdown: [filing_status]` metadata but no `label`, so child parameters like `max.SINGLE` cannot generate labels.

**Fix:** Added `label: Wisconsin standard deduction maximum`

**Before:**
```yaml
metadata:
  breakdown:
    - filing_status
  period: year
```

**After:**
```yaml
metadata:
  label: Wisconsin standard deduction maximum
  breakdown:
    - filing_status
  period: year
```

**Result:** Parameters like `gov.states.wi.tax.income.deductions.standard.max.SINGLE` can now generate label "Wisconsin standard deduction maximum (Single)".

---

### 2. Bracket Scale Without Label

**File:** `gov/irs/credits/education/american_opportunity_credit/amount.yaml`

**Problem:** This ParameterScale has bracket children like `amount[0].threshold` and `amount[1].rate`, but the scale lacks a `label`, so bracket parameters cannot generate labels.

**Fix:** Added `label: American Opportunity Credit amount schedule`

**Before:**
```yaml
metadata:
  type: marginal_rate
  rate_unit: /1
  threshold_unit: currency-USD
```

**After:**
```yaml
metadata:
  label: American Opportunity Credit amount schedule
  type: marginal_rate
  rate_unit: /1
  threshold_unit: currency-USD
```

**Result:** Parameters like `gov.irs.credits.education.american_opportunity_credit.amount[0].threshold` can now generate label "American Opportunity Credit amount schedule (bracket 1 threshold)".

---

### 3. Pseudo-Breakdown (Missing `breakdown` Metadata)

**File:** `gov/irs/income/amt/exemption/amount.yaml`

**Problem:** This parameter has filing status children (SINGLE, JOINT, etc.) but lacks `breakdown` metadata, so the system doesn't recognise it as a breakdown parameter.

**Fix:** Added both `breakdown: [filing_status]` and `label: AMT exemption amount`

**Before:**
```yaml
metadata:
  unit: currency-USD
  period: year
  propagate_metadata_to_children: true
```

**After:**
```yaml
metadata:
  label: AMT exemption amount
  breakdown:
    - filing_status
  unit: currency-USD
  period: year
  propagate_metadata_to_children: true
```

**Result:** Parameters like `gov.irs.income.amt.exemption.amount.SINGLE` can now generate label "AMT exemption amount (Single)".

---

### 4. Breakdown with `range()` Dimensions (New `breakdown_labels` Field)

**File:** `gov/irs/deductions/itemized/salt_and_real_estate/state_sales_tax_table/tax.yaml`

**Problem:** This parameter has breakdown dimensions `[state_code, range(1,7), range(1,20)]`. While `state_code` can be looked up to get "California" from "CA", the `range()` dimensions have no semantic meaning - "1" and "5" are just indices with no human-readable interpretation.

**Fix:** Added new `breakdown_labels` metadata field to provide semantic labels for each dimension.

**Before:**
```yaml
metadata:
  breakdown:
  - state_code
  - range(1,7)
  - range(1,20)
  label: Optional state sales tax table
```

**After:**
```yaml
metadata:
  breakdown:
  - state_code
  - range(1,7)
  - range(1,20)
  breakdown_labels:
  - State
  - Exemptions
  - Income bracket
  label: Optional state sales tax table
```

**Note:** This change adds the metadata, but requires a corresponding update to `policyengine.py` to read and use `breakdown_labels` when generating labels. Once implemented, parameters like `gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table.tax.CA.1.5` could generate label "Optional state sales tax table (California, 1 exemption, income bracket 5)".

---

## Summary of Patterns

| Category | Fix Required |
|----------|--------------|
| Breakdown without label | Add `label:` to parent metadata |
| Bracket without label | Add `label:` to ParameterScale metadata |
| Pseudo-breakdown | Add `breakdown:` and `label:` to parent metadata |
| Breakdown with `range()` | Add `breakdown_labels:` to parent metadata (requires policyengine.py update) |

## Next Steps

1. **policyengine.py**: Update `_generate_breakdown_label()` to:
   - Traverse up the parameter tree to find breakdown ancestors (not just immediate parent)
   - Support the new `breakdown_labels` metadata field
   - Handle nested breakdowns properly

2. **policyengine-us**: Apply these patterns to remaining parameters:
   - 11 more breakdown parents without labels
   - 7 more scales without labels
   - 60 more pseudo-breakdown parents
   - ~79 more breakdown parents with `range()` dimensions
