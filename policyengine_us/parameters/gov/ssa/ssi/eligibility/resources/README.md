# Resources

SSI countable resources are now calculated from imputed liquid assets
(bank accounts, stocks, bonds) rather than using a random pass rate.

The assets are imputed from SIPP in policyengine-us-data and flow through
to the SSI resource test via `ssi_countable_resources`.

Check SSI expenditures with:
```python
from policyengine_us import Microsimulation
Microsimulation().calc("ssi", map_to="person", period=2023).sum() / 1e9
```

[SSA reported $5.293 billion in SSI expenditures in February 2023](https://www.ssa.gov/policy/docs/quickfacts/stat_snapshot/#table3).
Annual target: $5.293 billion * 12 = $63.5 billion.
