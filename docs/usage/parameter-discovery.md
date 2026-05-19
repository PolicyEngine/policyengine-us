# Finding parameters

PolicyEngine US contains over 1,000 parameters representing tax rates, benefit amounts, income thresholds, and other policy values. This guide explains how to discover and understand these parameters when creating reforms.

## Parameter tree structure

Parameters are organized hierarchically under `policyengine_us/parameters/gov/`. The directory path maps directly to the parameter path you use in code.

### Federal agencies

| Directory | Agency | Examples |
|-----------|--------|----------|
| `gov/irs/` | Internal Revenue Service | Income tax brackets, deductions, credits (CTC, EITC, CDCC) |
| `gov/hhs/` | Health and Human Services | Federal poverty guidelines, Medicaid, TANF, CHIP |
| `gov/usda/` | Dept. of Agriculture | SNAP (food stamps), school meals, WIC |
| `gov/ssa/` | Social Security Administration | SSI, Social Security |
| `gov/hud/` | Housing and Urban Development | Section 8, housing assistance |
| `gov/ed/` | Dept. of Education | Pell grants, student aid |
| `gov/dol/` | Dept. of Labor | Unemployment insurance |
| `gov/fcc/` | Federal Communications Commission | Lifeline, ACP |
| `gov/doe/` | Dept. of Energy | Energy assistance programs |
| `gov/aca/` | Affordable Care Act | Premium tax credits, marketplace |

### IRS parameters (federal taxes)

The IRS section is the most detailed, covering the federal income tax code:

```
gov/irs/
├── income/           # Tax brackets and rates
│   └── bracket.yaml  # Marginal rates by filing status
├── deductions/       # Above and below-the-line deductions
│   ├── standard/     # Standard deduction amounts
│   └── itemized/     # SALT, mortgage interest, charitable
├── credits/          # Tax credits
│   ├── ctc/          # Child Tax Credit
│   ├── eitc/         # Earned Income Tax Credit
│   ├── cdcc/         # Child and Dependent Care Credit
│   └── ...
├── capital_gains/    # Long-term capital gains rates
├── payroll/          # Social Security and Medicare taxes
└── ald/              # Above-the-line deductions
```

### State parameters

State-specific parameters follow a consistent structure:

```
gov/states/{state_code}/
├── tax/
│   └── income/
│       ├── rates.yaml      # State income tax rates
│       ├── credits/        # State tax credits
│       └── deductions/     # State deductions
└── {agency}/               # State benefit programs
```

For example, California parameters are at `gov/states/ca/`, New York at `gov/states/ny/`.

## Searching for parameters

### Using grep to find parameters

Search for parameters by keyword:

```bash
# Find SALT-related parameters
grep -r "salt" policyengine_us/parameters/gov/irs/ --include="*.yaml"

# Find all EITC parameters
grep -r "eitc" policyengine_us/parameters/gov/ --include="*.yaml" -l

# Find parameters mentioning a specific dollar amount
grep -r "15_000" policyengine_us/parameters/ --include="*.yaml"
```

### Browsing the directory structure

List parameters in a specific area:

```bash
# See all CTC-related parameters
ls policyengine_us/parameters/gov/irs/credits/ctc/

# See all California parameters
ls -R policyengine_us/parameters/gov/states/ca/

# Find all parameter files for a program
find policyengine_us/parameters/gov/irs/credits/eitc -name "*.yaml"
```

### Converting paths to parameter names

The file path becomes the parameter path by:
1. Removing the `policyengine_us/parameters/` prefix
2. Removing the `.yaml` extension
3. Replacing `/` with `.`

Example:
- File: `policyengine_us/parameters/gov/irs/deductions/standard/amount.yaml`
- Parameter: `gov.irs.deductions.standard.amount`

## Reading YAML parameter files

### Simple parameters

A basic parameter file with values over time:

```yaml
description: Federal deduction from AGI if not itemizing.

SINGLE:
  2018-01-01: 12_000
  2019-01-01: 12_200
  2024-01-01: 14_600
JOINT:
  2018-01-01: 24_000
  2024-01-01: 29_200
# ... other filing statuses

metadata:
  unit: currency-USD
  period: year
  label: Standard deduction
```

### Filing status variants

Many IRS parameters vary by filing status. The five statuses are:
- `SINGLE` - Unmarried individuals
- `JOINT` - Married filing jointly
- `SEPARATE` - Married filing separately
- `HEAD_OF_HOUSEHOLD` - Unmarried with dependents
- `SURVIVING_SPOUSE` - Qualifying surviving spouse

### Bracket syntax

Tax brackets and phase-outs use a bracket structure:

```yaml
brackets:
  - threshold:
      values:
        2018-01-01: 0
    amount:
      values:
        2018-01-01: 2_000
  - threshold:
      values:
        2018-01-01: 17
    amount:
      values:
        2018-01-01: 0
```

This defines an amount of $2,000 when the threshold variable is 0-16, and $0 when 17+.

### Date format

All dates use ISO format: `YYYY-MM-DD`. The value applies from that date until the next specified date.

```yaml
# $12,000 from 2018-01-01 through 2018-12-31
# $12,200 from 2019-01-01 through 2019-12-31
SINGLE:
  2018-01-01: 12_000
  2019-01-01: 12_200
```

### Metadata fields

Common metadata fields you'll encounter:

| Field | Description |
|-------|-------------|
| `unit` | Value type: `currency-USD`, `/1` (percentage), `year`, etc. |
| `period` | Time period: `year`, `month`, `eternity` |
| `label` | Human-readable name |
| `reference` | Legal citations with title and href |
| `breakdown` | Categories the parameter varies by |
| `uprating` | Inflation adjustment parameter |

## Common parameter patterns

### Federal poverty guidelines

HHS poverty guidelines are at `gov/hhs/fpg.yaml` and vary by household size and state group:

```yaml
first_person:
  CONTIGUOUS_US:
    2024-01-01: 15_060
  AK:
    2024-01-01: 18_810
  HI:
    2024-01-01: 17_310
additional_person:
  CONTIGUOUS_US:
    2024-01-01: 5_380
```

### State-specific overrides

Some programs have federal defaults with state-specific values:

```yaml
# Federal default in gov/program/threshold.yaml
threshold:
  2024-01-01: 100

# State override in gov/states/ca/program/threshold.yaml
threshold:
  2024-01-01: 150  # California has higher threshold
```

### Indexed parameters

Parameters with inflation adjustment include uprating metadata:

```yaml
values:
  2024-01-01: 14_600
metadata:
  uprating:
    parameter: gov.irs.uprating
    rounding:
      type: downwards
      interval: 50
```

## Using parameters in reforms

Once you find a parameter, use it in a reform:

```python
from policyengine_us import Simulation

# Create reform modifying the standard deduction
reform = {
    "gov.irs.deductions.standard.amount.SINGLE": {
        "2024-01-01": 20_000
    }
}

sim = Simulation(
    situation=household,
    reform=reform
)
```

## Additional resources

- [OpenFisca parameter documentation](https://openfisca.org/doc/coding-the-legislation/legislation_parameters.html)
- [PolicyEngine reform examples](https://policyengine.org/us/research)
