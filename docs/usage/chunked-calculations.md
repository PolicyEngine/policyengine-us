# Household-chunked calculations

`policyengine_us.tools.calculate_chunked.calculate_chunked` calculates numeric
variables over a disjoint partition of households, releasing each simulation
before constructing the next. The source dataset and result arrays remain in
memory; the helper bounds simulation working memory by chunk size, rather than
promising a fixed RSS limit.

```python
from policyengine_us import Microsimulation
from policyengine_us.tools.calculate_chunked import calculate_chunked

result = calculate_chunked(
    lambda dataset: Microsimulation(dataset=dataset, dataset_end_year=2026),
    ["tob_revenue_oasdi", "tob_revenue_medicare_hi", "tob_revenue_total"],
    2026,
    4,
    dataset=Microsimulation.default_dataset,
)
tax_units = result.entities["tax_unit"]
print(result.weighted_sums)
```

The factory owns reforms and simulation options. It must return a fresh
PolicyEngine-US Microsimulation with the supplied population and row order.
The explicit `dataset=` keyword supplies the source without first constructing
a full-population simulation. Supported sources are `USSingleYearDataset`,
`USMultiYearDataset`, and local or Hugging Face entity-table HDFStore files.
Legacy variable-array and flat-file datasets must first be converted to the US
entity-table schema. All six entity tables and person membership links are
required. Input data is not modified.

Each output DataFrame contains `<entity>_id`, `weight`, and requested variable
columns, with exactly the source entity order. `weight` is the weight used by
`Microsimulation.get_weights`, projected from household weights; native input
entity weight columns are preserved in the chunk datasets. Weighted sums are
calculated from the assembled source-order arrays, avoiding changes in reduction
order. A requested variable can itself be an entity weight variable.

## Exact partition invariants

Every household gets exactly one label. Each person inherits their household's
label; every tax unit, SPM unit, family and marital unit must have members in
exactly one household and inherits that label. Entity IDs must be unique,
nonmissing, fully referenced and unmodified. Boolean selection preserves the
source entity order, and results are written back to their original row
positions. These facts prove disjointness, complete coverage, and whole groups.
They also preserve each household's calculation inputs and weights. All source
years are retained, with identical structural IDs and links across years.
Optional `household_chunks` provides arbitrary integer labels in
`[0, n_chunks)`; otherwise consecutive household partitions are balanced. Empty
partitions are skipped, including when chunks outnumber households.

Exact calculation additionally requires every dependency to be local to a
household. The current model has two Medicaid state reductions,
`medicaid_slcsp_state_average_cost_index` and `medicaid_slcsp_state_denominator`.
The helper rejects these at calculation time, including indirect dependencies
and branches. Known Medicaid claiming-tax-unit links crossing households are
also rejected. The model audit found no other population ranking, quantile or
stochastic formula reductions. Custom reform formulas remain the caller's
responsibility: cross-household reductions, order-dependent random draws and
other global dependencies are unsupported. These are calculation restrictions,
not an assumption that every model variable can be chunked.

The tests compare a full 32-household, five-state fixture with one, two, three
and seven chunks, plus random household assignments. They compare every entity
value and weighted sum, check source order and unchanged input frames, and use
weak references to check simulation release. The fixture includes households
with multiple tax and SPM units and Social Security recipients. Independent
pre-change TOB branch calculations protect the statutory signed allocation.

## TOB working memory

Counterfactual income tax without Social Security and under pre-1993 inclusion
is cached in parent variable holders. A direct TOB calculation prepares those
holders in separate outer calculations: current Core retains popped branches
in active calculation frames, so the frames must finish before collection.
Each temporary branch clones the system, clears non-input arrays, computes and
copies only income tax, and is removed and collected before the next direct
counterfactual. A TOB dependency nested inside another formula can retain its
branch identities until that outer formula returns. OASDI remains old-law tax minus no-inclusion
tax, total remains current tax minus no-inclusion tax, and HI remains the signed
residual. No per-unit floor is introduced.

The hub will add measured full-dataset peak memory and timing after running its
memory probe. Small-fixture exactness establishes correctness, not a measured
full-population RSS reduction.
