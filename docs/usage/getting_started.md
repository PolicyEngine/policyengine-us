# Getting Started

This guide helps you get started with PolicyEngine US for microsimulation analysis.

## Installation

```bash
pip install policyengine-us
```

## Basic Usage

The simplest simulation involves creating a single person household:

```python
from policyengine_us import Simulation

# Create a simulation
sim = Simulation(
    situation={
        "people": {
            "person": {
                "age": 30,
                "employment_income": 50_000,
            }
        },
        "households": {
            "household": {
                "members": ["person"],
                "state_name": "CA",
            }
        }
    }
)

# Calculate values
income_tax = sim.calculate("income_tax")
snap_benefits = sim.calculate("snap")
```

## Time-Specific Inputs

When calculating values for specific years (past or future), you must use the time-specific input format.

### ⚠️ Critical Difference

**Simple format** (only for current year):
```python
"age": 30,
"employment_income": 50_000,
```

**Time-specific format** (required for specific years):
```python
"age": {"2025": 30},
"employment_income": {"2025": 50_000},
```

### Example: Calculating 2025 Benefits

```python
sim = Simulation(
    situation={
        "people": {
            "person": {
                "age": {"2025": 30},
                "employment_income": {"2025": 50_000},
                "pre_subsidy_rent": {"2025": 24_000},
            }
        },
        "households": {
            "household": {
                "members": ["person"],
                "state_name": {"2025": "CA"},
            }
        }
    }
)

# Calculate for 2025
snap_2025 = sim.calculate("snap", 2025)

# Calculate for specific month
snap_jan_2025 = sim.calculate("snap", "2025-01")
```

## Entity Structure

PolicyEngine US models four types of entities:

1. **People**: Individual persons
2. **Tax Units**: Groups that file taxes together
3. **SPM Units**: Supplemental Poverty Measure units (for poverty calculations)
4. **Households**: Physical households

### Family Example

```python
sim = Simulation(
    situation={
        "people": {
            "parent": {
                "age": {"2025": 35},
                "employment_income": {"2025": 60_000},
            },
            "child": {
                "age": {"2025": 10},
            }
        },
        "tax_units": {
            "tax_unit": {
                "members": ["parent", "child"],
            }
        },
        "spm_units": {
            "spm_unit": {
                "members": ["parent", "child"],
            }
        },
        "households": {
            "household": {
                "members": ["parent", "child"],
                "state_name": {"2025": "NY"},
            }
        }
    }
)
```

## Common Pitfalls

1. **Using simple format for specific years**: This will give incorrect results
2. **Missing entities**: Always include all required entity types
3. **Forgetting state_name**: Required for state-specific calculations
4. **Wrong variable names**: Variable names are case-sensitive

## Next Steps

- Explore specific benefit programs in the documentation
- See the [examples](../examples) directory for more complex scenarios
- Check state-specific documentation for your state