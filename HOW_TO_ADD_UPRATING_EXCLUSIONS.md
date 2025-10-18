# How to Add Uprating Detection Exclusions

## Quick Guide

To exclude a parameter file from uprating detection, edit **one file**:

### File to Edit
`policyengine_us/tools/uprating_config.py`

### Example

```python
EXCLUSIONS = [
    'gov/bls/cpi',                # Exclude entire directory
    'gov/hhs/uprating.yaml',      # Exclude specific file
    'gov/ssa/nawi.yaml',          # Another specific file
    'calibration/',               # Exclude all calibration data
]
```

## When to Add Exclusions

Add a parameter to exclusions when it is:

✅ **Uprating source data** (like CPI indices, wage indices)
✅ **Already an uprating file** (like `benchmark_premium_uprating.yaml`)
✅ **Calibration data** (not policy parameters)
✅ **Historical data series** (not parameters that change policy)

❌ **Don't exclude** if it's a policy parameter that should have `uprating:` metadata

## Example: Excluding a File

**Before:**
```
Found 415 parameters in 42 files with annual updates but missing uprating metadata.

  • gov/aca/benchmark_premium_uprating.yaml
    Years: 2014-2025 (12 years), avg growth: 4.72%/year
```

**Edit config:**
```python
EXCLUSIONS = [
    # ... existing exclusions ...
    'gov/aca/benchmark_premium_uprating.yaml',  # Add this line
]
```

**After:**
```
Found 414 parameters in 41 files with annual updates but missing uprating metadata.

  (gov/aca/benchmark_premium_uprating.yaml no longer appears)
```

## Example: Excluding All Calibration Data

If you want to exclude all calibration files at once:

```python
EXCLUSIONS = [
    'gov/bls/cpi',
    'gov/hhs/uprating.yaml',
    'gov/ssa/nawi.yaml',
    'calibration/',  # ← Uncomment this line
]
```

This would reduce findings from **414 parameters in 41 files** to a smaller set.

## Growth Rate Configuration

You can also adjust the growth rate thresholds in the same file:

```python
MIN_GROWTH_RATE = 0.0   # 0% - values should not decrease
MAX_GROWTH_RATE = 0.10  # 10% - filter out large policy changes
```

- Lower `MAX_GROWTH_RATE` (e.g., 0.05) to catch only very inflation-like changes
- Raise `MAX_GROWTH_RATE` (e.g., 0.15) to include some policy phase-ins

## Testing Your Changes

After editing the config:

```bash
# Run the command-line tool
python policyengine_us/tools/detect_missing_uprating.py

# Run the test
pytest policyengine_us/tests/code_health/uprating_metadata.py

# Both should show the same results
```

## Single Source of Truth

✅ **One config file** controls both:
- The test (`policyengine_us/tests/code_health/uprating_metadata.py`)
- The command-line script (`policyengine_us/tools/detect_missing_uprating.py`)

No need to update multiple locations!
