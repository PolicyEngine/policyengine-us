# Resources

[SSA reported $5.293 billion in SSI expenditures in February 2023](https://www.ssa.gov/policy/docs/quickfacts/stat_snapshot/#table3).
Adjust `pass_rate.yaml` to match this for SSI in 2023 ($5.293 billion * 12 = $63.5 billion).

Check with this code:
```python
from policyengine_us import Microsimulation
Microsimulation().calc("ssi", map_to="person", period=2023).sum() / 1e9
```
