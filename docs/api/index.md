# PolicyEngine US API Reference

## Overview

PolicyEngine US provides a comprehensive Python API for tax and benefit calculations. This reference documents the main classes, methods, and patterns for programmatic access.

## Installation

```bash
pip install policyengine-us
```

## Core Classes

### Simulation

The primary interface for running calculations.

```python
from policyengine_us import Simulation

simulation = Simulation(
    situation=dict,      # Household data
    reform=dict,         # Optional policy changes
    trace=bool,          # Enable calculation tracing
)
```

#### Key Methods

##### `calculate(variable_name, period)`
Calculate a variable value for a given period.

**Parameters:**
- `variable_name` (str): Name of variable to calculate
- `period` (str or int): Time period (e.g., 2024, "2024-01", "2024-Q1")

**Returns:**
- numpy.ndarray: Calculated values for all entities

**Example:**
```python
# Annual calculation
snap_benefit = simulation.calculate("snap", 2024)

# Monthly calculation  
monthly_snap = simulation.calculate("snap", "2024-01")
```

##### `trace_computation(variable_name, period)`
Get detailed calculation trace for debugging.

**Returns:**
- dict: Nested structure showing all intermediate calculations

### Microsimulation

For population-level analysis using survey microdata.

```python
from policyengine_us import Microsimulation

microsim = Microsimulation(
    reform=dict,           # Optional policy changes
    dataset="cps_2024",    # Survey dataset
)
```

#### Key Methods

##### `calculate(variable_name, period, map_to=None)`
Calculate variable for entire population.

**Parameters:**
- `variable_name` (str): Variable to calculate
- `period` (str or int): Time period
- `map_to` (str): Optional entity aggregation

**Returns:**
- pandas.Series or MicroSeries: Population values with weights

##### `calculate_dataframe(variables, period)`
Calculate multiple variables efficiently.

**Parameters:**
- `variables` (list): Variable names
- `period` (str or int): Time period

**Returns:**
- pandas.DataFrame: All requested variables

## Entity System

PolicyEngine uses four entity types:

### People
Individual persons with attributes:
- Demographics: `age`, `is_disabled`, `is_blind`
- Income: `employment_income`, `self_employment_income`
- Relationships: `is_tax_unit_dependent`, `is_spouse`

### Tax Units
Groups filing taxes together:
- `tax_unit_head`, `tax_unit_spouse`, `tax_unit_dependents`
- Used for: Income tax, EITC, CTC calculations

### SPM Units
Supplemental Poverty Measure units:
- Family groups sharing resources
- Used for: SNAP, poverty measurement

### Households
Physical residence units:
- Geographic: `state_name`, `county_name`, `zip_code`
- Housing: `housing_cost`, `housing_type`
- Used for: Housing assistance, utility programs

## Variable System

### Variable Types

#### Input Variables
Set directly in the situation:
```python
situation = {
    "people": {
        "person1": {
            "age": 30,
            "employment_income": 50_000,
        }
    }
}
```

#### Formula Variables
Calculated from other variables:
```python
# In variable definition
def formula(person, period, parameters):
    employment = person("employment_income", period)
    self_employment = person("self_employment_income", period)
    return employment + self_employment
```

#### Parameter Variables
Values from legislation:
```python
def formula(person, period, parameters):
    p = parameters(period).gov.irs.deductions
    return p.standard.single
```

### Time Periods

Variables can have different `definition_period`:
- `YEAR`: Annual values (income, deductions)
- `MONTH`: Monthly values (SNAP, housing)
- `ETERNITY`: Unchanging (disability status)

## Reform System

### Creating Reforms

Modify parameters or variables:

```python
def reform(parameters):
    # Change Child Tax Credit amount
    ctc = parameters.gov.irs.credits.ctc.amount
    ctc.update(value=3_000, period="2024-01-01")
    return parameters

simulation = Simulation(
    situation=situation,
    reform=reform,
)
```

### Reform Types

#### Parameter Reform
```python
def double_eitc(parameters):
    eitc = parameters.gov.irs.credits.eitc
    for param in eitc.maximum.children:
        param.update(
            value=param.values_list[-1].value * 2,
            period="2024-01-01"
        )
    return parameters
```

#### Structural Reform
```python
from policyengine_core.model_api import *

class universal_basic_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    
    def formula(person, period, parameters):
        return 12_000  # $1,000/month

reform = Reform()
reform.add_variable(universal_basic_income)
```

## Common Patterns

### Household Simulation
```python
# Family with children
situation = {
    "people": {
        "parent": {"age": 35, "employment_income": 40_000},
        "child1": {"age": 10},
        "child2": {"age": 5},
    },
    "tax_units": {
        "unit": {"members": ["parent", "child1", "child2"]}
    },
    "households": {
        "household": {
            "members": ["parent", "child1", "child2"],
            "state_name": "CA",
        }
    }
}
```

### Multi-Year Analysis
```python
results = {}
for year in range(2020, 2030):
    value = simulation.calculate("household_net_income", year)
    results[year] = value[0]
```

### State Comparison
```python
states = ["CA", "TX", "NY", "FL"]
state_taxes = {}

for state in states:
    sim = Simulation(
        situation={
            "people": {"p": {"employment_income": 100_000}},
            "households": {"h": {"members": ["p"], "state_name": state}}
        }
    )
    state_taxes[state] = sim.calculate("state_income_tax", 2024)[0]
```

### Marginal Tax Rate
```python
base_income = 50_000
delta = 1_000

base_sim = Simulation(situation_with_income(base_income))
high_sim = Simulation(situation_with_income(base_income + delta))

base_net = base_sim.calculate("household_net_income", 2024)[0]
high_net = high_sim.calculate("household_net_income", 2024)[0]

marginal_rate = 1 - (high_net - base_net) / delta
```

## Advanced Features

### Custom Variables
```python
from policyengine_core.model_api import *

class my_benefit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "My custom benefit"
    
    def formula(person, period, parameters):
        income = person("adjusted_gross_income", period)
        return where(income < 30_000, 1_000, 0)
```

### Parameter Files
Create YAML parameter files:
```yaml
description: Maximum benefit amount
values:
  2024-01-01: 1_000
  2025-01-01: 1_100
metadata:
  unit: currency-USD
  reference:
    - title: "My Reform Act"
      href: "https://example.com"
```

### Debugging

Enable trace mode:
```python
sim = Simulation(situation=situation, trace=True)
result = sim.calculate("snap", 2024)
trace = sim.trace_computation("snap", 2024)

# Pretty print trace
import json
print(json.dumps(trace, indent=2))
```

## Performance Tips

### Batch Calculations
```python
# Inefficient
for var in variables:
    results[var] = sim.calculate(var, 2024)

# Efficient  
df = microsim.calculate_dataframe(variables, 2024)
```

### Caching
Results are automatically cached within a simulation:
```python
# First call computes
snap1 = sim.calculate("snap", 2024)

# Second call returns cached value
snap2 = sim.calculate("snap", 2024)
```

### Memory Management
For large microsimulations:
```python
# Process in chunks
chunk_size = 10_000
for i in range(0, len(dataset), chunk_size):
    chunk = dataset[i:i+chunk_size]
    process_chunk(chunk)
```

## Error Handling

Common exceptions:
- `VariableNotFound`: Variable name doesn't exist
- `PeriodMismatch`: Wrong period format for variable
- `EntityMismatch`: Variable calculated for wrong entity

```python
try:
    result = sim.calculate("invalid_variable", 2024)
except VariableNotFound:
    print("Variable does not exist")
```

## Integration Examples

### Web API
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    sim = Simulation(situation=data["situation"])
    result = sim.calculate(data["variable"], data["period"])
    return jsonify({"result": result.tolist()})
```

### Pandas Integration
```python
import pandas as pd

# Create scenarios DataFrame
scenarios = pd.DataFrame({
    "income": [20_000, 50_000, 100_000],
    "children": [0, 2, 3],
})

# Calculate for each scenario
results = []
for _, row in scenarios.iterrows():
    sim = create_simulation(row)
    results.append({
        "income": row["income"],
        "children": row["children"],
        "eitc": sim.calculate("eitc", 2024)[0],
        "ctc": sim.calculate("ctc", 2024)[0],
    })

results_df = pd.DataFrame(results)
```

## See Also

- [Policy Reference](../policy/index) - Program rules and eligibility
- [Examples](../examples/index) - Jupyter notebooks with use cases
- [GitHub Repository](https://github.com/PolicyEngine/policyengine-us) - Source code
- [Web Interface](https://policyengine.org/us) - Interactive calculator