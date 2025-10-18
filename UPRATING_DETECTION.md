# Uprating Metadata Detection

This repository includes automated detection for parameters that should have uprating metadata but don't.

## The Problem

Parameters that are manually updated every year with inflation-like growth should have automated `uprating:` metadata. Without it:
- Values are hard-coded and must be manually updated each year
- Risk of forgetting to update (stale values)
- No clear indication the value should be inflation-adjusted

## The Solution

### Automated Test

A test runs on every CI build:

```bash
pytest policyengine_us/tests/code_health/uprating_metadata.py
```

This test **will fail** if it finds parameters with:
- ✅ 3+ consecutive years of updates
- ✅ Growth rates between 0-10% (inflation-like)
- ❌ Missing `uprating:` metadata

### Command-Line Tool

You can also run the detection manually:

```bash
python policyengine_us/tools/detect_missing_uprating.py
```

This produces a detailed report showing:
- Which files have parameters needing uprating
- Year ranges for each parameter
- Average growth rates
- Number of parameters per file

## What Gets Detected

### ✅ Flagged (Needs Uprating)
```yaml
# gov/irs/capital_gains/brackets.yaml
thresholds:
  1:
    SINGLE:
      values:
        2013-01-01: 36_250
        2014-01-01: 36_900
        2015-01-01: 37_450
        # ... manually updated every year (1.64% avg growth)
        2025-01-01: 48_350
```
**Why:** Consistent ~1-2% annual growth over 13 years = inflation adjustment

### ❌ Not Flagged (Policy Change)
```yaml
# gov/states/nj/tax/income/exclusions/retirement/max_amount.yaml
SINGLE:
  2017-01-01: 30_000
  2018-01-01: 45_000  # 50% jump
  2019-01-01: 60_000  # 33% jump
  2020-01-01: 75_000  # 25% jump
```
**Why:** Large jumps (>10%) indicate policy phase-in, not inflation

### ❌ Not Flagged (Excluded)
```yaml
# gov/bls/cpi/c_cpi_u.yaml - CPI index itself
# gov/hhs/uprating.yaml - Uprating factors
# gov/ssa/nawi.yaml - National Average Wage Index
```
**Why:** These ARE the uprating sources, not parameters to be uprated

## How to Fix

When the test fails, you have two options:

### Option 1: Add Uprating Metadata

```yaml
description: Capital gains tax bracket thresholds
metadata:
  unit: currency-USD
  uprating: gov.bls.cpi.c_cpi_u  # ← Add this
  reference:
    - title: IRC §1(j)(5)(B)
      href: https://...
```

### Option 2: Exclude from Detection

If the parameter is actually uprating source data (not a parameter that needs uprating), add it to the **single config file**:

**Edit:** `policyengine_us/tools/uprating_config.py`

```python
EXCLUSIONS = [
    'gov/bls/cpi',
    'gov/hhs/uprating.yaml',
    'gov/ssa/nawi.yaml',
    'gov/aca/benchmark_premium_uprating.yaml',  # ← Add your exclusion here
]
```

Changes to this config file apply to **both** the test and the command-line script automatically.

## Current Status

As of the last run:
- **415 parameters** in **42 files** need review
- Top priorities (10+ years of manual updates):
  - `gov/irs/capital_gains/brackets.yaml` (13 years)
  - `gov/aca/benchmark_premium_uprating.yaml` (12 years)
  - `gov/states/nj/tax/income/credits/eitc/match.yaml` (12 years)

See `missing_uprating_final.txt` for the full report.

## Technical Details

The detection algorithm:
1. Scans all parameter YAML files
2. Identifies date-keyed time series (e.g., `2023-01-01: value`)
3. Checks for 3+ consecutive years with different values
4. Calculates year-over-year growth rates
5. Flags parameters with 0-10% growth lacking `uprating:` metadata
6. Excludes known uprating source files

**Growth Rate Threshold:** 0-10% filters out deliberate policy changes while catching inflation adjustments.
