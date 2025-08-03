# PolicyEngine US

[![codecov](https://codecov.io/gh/PolicyEngine/policyengine-us/branch/master/graph/badge.svg?token=BLoCjCf5Qr)](https://codecov.io/gh/PolicyEngine/policyengine-us)
[![PyPI version](https://badge.fury.io/py/policyengine-us.svg)](https://badge.fury.io/py/policyengine-us)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

PolicyEngine US is a microsimulation model of the US state and federal tax and benefit system.

## Installation

To install, run `pip install policyengine-us`.

## Usage

### Quick Start

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

### ⚠️ Important: Time-Specific Inputs

When calculating for specific years, you **must** use the time-specific format:

```python
# ❌ Wrong for year-specific calculations
"age": 30

# ✅ Correct for year-specific calculations  
"age": {"2025": 30}
```

Example:
```python
sim = Simulation(
    situation={
        "people": {
            "person": {
                "age": {"2025": 30},
                "employment_income": {"2025": 50_000},
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
```

## Documentation

For detailed documentation, including:
- Complete usage guide
- Examples for families, state-specific programs, and multi-year calculations
- Full list of available variables and entities
- Troubleshooting guide

Visit **[policyengine.github.io/policyengine-us](https://policyengine.github.io/policyengine-us/)**

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
