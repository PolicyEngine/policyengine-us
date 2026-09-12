# Microsimulation

The `Microsimulation` class is the primary tool for population-level policy analysis in PolicyEngine US. It combines representative survey microdata with PolicyEngine's tax-benefit model to estimate how policies affect the entire US population.

## Getting started

```python
from policyengine_us import Microsimulation

# Create a microsimulation with the default dataset
sim = Microsimulation()

# Calculate a variable for the default year (2024)
household_net_income = sim.calc("household_net_income")

# The result is a weighted MicroSeries
print(f"Total household net income: ${household_net_income.sum():,.0f}")
print(f"Mean household net income: ${household_net_income.mean():,.0f}")
```

## Methods: `calc()` vs `calculate()`

The `Microsimulation` class provides two methods for computing variables:

### `calc()` / `calculate()`

These methods are aliases - `calc` is shorthand for `calculate`. Both return a `MicroSeries` object that includes survey weights, enabling proper population-level statistics.

```python
# These are equivalent
income = sim.calc("household_net_income")
income = sim.calculate("household_net_income")

# MicroSeries supports weighted aggregations
income.sum()      # Total across population (using weights)
income.mean()     # Weighted mean
income.median()   # Weighted median
income.gini()     # Gini coefficient
```

### Key parameters

- `variable_name` (str): The variable to calculate
- `period` (int or str): The time period (e.g., `2024` or `"2024"`)
- `map_to` (str): Entity to map results to (see below)
- `use_weights` (bool): If `False`, returns raw unweighted array

```python
# Calculate SNAP benefits for 2024
snap = sim.calc("snap", period=2024)

# Get unweighted array
snap_raw = sim.calc("snap", period=2024, use_weights=False)
```

## Entity mapping with `map_to`

PolicyEngine US models multiple entity levels: `person`, `tax_unit`, `spm_unit`, `family`, and `household`. The `map_to` parameter transforms results between these levels.

### Mapping from groups to persons

When mapping a group-level variable (like `household_net_income`) to persons, each person receives their group's value:

```python
# Get household income at person level (each person gets their household's value)
person_hh_income = sim.calc("household_net_income", map_to="person")

# Useful for person-weighted analysis
print(f"Average income per person: ${person_hh_income.mean():,.0f}")
```

### Mapping from persons to groups

When mapping a person-level variable to groups, values are summed by default:

```python
# Sum employment income to household level
hh_earnings = sim.calc("employment_income", map_to="household")
```

### Common use cases

```python
# Calculate poverty at person level for person-weighted statistics
person_poverty = sim.calc("in_poverty", map_to="person")
poverty_rate = person_poverty.mean()

# Map tax credits to see household-level impact
hh_eitc = sim.calc("eitc", map_to="household")
```

## Available datasets

### The default build

The default is the certified Populace build, pinned by build id and hosted as a
HuggingFace *dataset* repository:

```python
# Default: the certified Populace build named in DEFAULT_DATASET.
sim = Microsimulation()
```

### Supplying another population

A population file has to satisfy the SPM input contract: it supplies primitive
inputs, including observed `county_fips` codes as five-digit strings and
source-backed `is_spm_independent_minor_role` values, and it must not store
formula-owned SPM outputs such as `spm_unit_spm_threshold`. Any observed Census
measurement is retained under a separate report-only name.

The legacy files under `hf://policyengine/policyengine-us-data/` predate that
contract, so resource and poverty outputs are not available over them:

- `cps_2023.h5` stores `spm_unit_spm_threshold`, so the loader rejects it.
- `enhanced_cps_2024.h5` loads and computes tax variables, but carries no SPM
  independence roles, so SPM units consisting of one 15-to-17-year-old classify
  no measurement adult and every resource output over the file fails closed.

A household simulation that has no county input can select an SPM area
explicitly instead:

```python
sim = Microsimulation(dataset=..., spm={"geography_kind": "national"})
```

### Filtering by geography

The microdata includes geographic identifiers that can be used for state-level analysis:

```python
# Calculate for all households, then filter to a specific state
sim = Microsimulation()
in_california = sim.calc("CA")  # Boolean for California residents
ca_benefits = sim.calc("household_benefits")[in_california]
print(f"California total benefits: ${ca_benefits.sum():,.0f}")
```

Each state has a corresponding boolean variable using its two-letter abbreviation (e.g., `CA`, `NY`, `TX`).

## Subsampling for faster development

For development and testing, use `subsample()` to work with a smaller representative sample:

```python
sim = Microsimulation()
sim.subsample(1_000)  # Sample 1,000 households

# Or use a fraction
sim.subsample(frac=0.1)  # 10% of households

# Results are still weighted to represent the full population
total = sim.calc("household_net_income").sum()
```

The `subsample()` method:
- Samples households (keeping all people within sampled households)
- Adjusts weights to maintain population totals
- Accepts a `seed` parameter for reproducibility

## Winners and losers analysis

A common use case is comparing baseline policy to a reform:

```python
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform

# Define a reform (example: double the EITC)
reform = Reform.from_dict(
    {"gov.irs.credits.eitc.max[0].amount": {"2024-01-01.2100-12-31": 1246}},
    country_id="us",
)

# Create baseline and reformed simulations
baseline = Microsimulation()
reformed = Microsimulation(reform=reform)

# Calculate net income change at person level for proper population weighting
baseline_income = baseline.calc("household_net_income", map_to="person")
reformed_income = reformed.calc("household_net_income", map_to="person")

gain = reformed_income - baseline_income

# Analyze winners and losers
winners = gain > 1  # Gained more than $1
losers = gain < -1  # Lost more than $1
no_change = ~winners & ~losers

print(f"Winners: {winners.mean():.1%}")
print(f"Losers: {losers.mean():.1%}")
print(f"No change: {no_change.mean():.1%}")

# Total cost/benefit
print(f"Net cost: ${gain.sum():,.0f}")

# Average gain among winners
print(f"Average gain for winners: ${gain[winners].mean():,.0f}")
```

## Weight sanity checks

When running microsimulations, verify that weights produce sensible population totals:

```python
sim = Microsimulation()

# Check population
person_weight = sim.calc("person_weight", map_to="person")
print(f"Total population: {person_weight.sum():,.0f}")

# Check household count
household_weight = sim.calc("household_weight")
print(f"Total households: {household_weight.sum():,.0f}")

# Verify key aggregates against published statistics
total_earnings = sim.calc("employment_income").sum()
print(f"Total employment income: ${total_earnings / 1e12:.2f}T")

total_snap = sim.calc("snap").sum()
print(f"Total SNAP benefits: ${total_snap / 1e9:.1f}B")
```

Compare these totals against official statistics to validate your analysis:
- US population: ~330 million
- US households: ~130 million
- SNAP expenditure: ~$110 billion annually

## Performance tips

1. **Subsample during development**: Use `sim.subsample(1_000)` while iterating
2. **Avoid redundant calculations**: Store results in variables rather than recalculating
3. **Use appropriate entities**: Calculate at the natural entity level when possible

```python
# Good: Calculate at natural entity level, then map if needed
snap = sim.calc("snap")  # spm_unit level
snap_per_person = sim.calc("snap", map_to="person")

# Slower: Unnecessarily mapping multiple times
```

## Complete example

```python
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform
import pandas as pd

# Create simulations
baseline = Microsimulation()
baseline.subsample(10_000, seed=123)  # For faster iteration

# Define a reform
reform = Reform.from_dict(
    {
        "gov.contrib.ubi_center.basic_income.amount": {
            "2024-01-01.2100-12-31": 1000
        },
        "gov.contrib.ubi_center.basic_income.phase_out.rate": {
            "2024-01-01.2100-12-31": 0.1
        },
    },
    country_id="us",
)
reformed = Microsimulation(reform=reform)
reformed.subsample(10_000, seed=123)

# Calculate impacts
baseline_income = baseline.calc("household_net_income", map_to="person")
reformed_income = reformed.calc("household_net_income", map_to="person")
change = reformed_income - baseline_income

# Distributional analysis by income decile
decile = baseline.calc("household_income_decile", map_to="person")

results = []
for d in range(1, 11):
    in_decile = decile == d
    avg_change = change[in_decile].mean()
    results.append({"Decile": d, "Average change": avg_change})

df = pd.DataFrame(results)
print(df)
```
