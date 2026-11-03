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
`USMultiYearDataset`, local or Hugging Face entity-table HDFStore files, and
local or Hugging Face variable-centric `.h5` files: top-level groups named for
variables, each holding one array per period (`<variable>/<period>`), as
population projection files store them and as `Microsimulation(dataset=path)`
loads them through Core. Flat files are not supported. All six entity ID
arrays and person membership links are required. Input data is not modified.

For entity tables the factory receives a dataset object of the source's type.
For a variable-centric file it receives a `str` path to a temporary `.h5` file
in the same layout, with the source file's name, every stored period and each
array's dtype, fixed-width byte strings included, so the factory can call
`Microsimulation(dataset=path)`. The source arrays stay on disk and are read
again for each chunk. Each array is assigned to the entity of its variable in
the country system; arrays whose length differs from that entity's count are
rejected, and names that match no country-system variable are left out, as
Core's loader ignores them. The helper raises when the factory's system (a
reform, say) defines a name it left out, since Core would load that name in an
unchunked simulation. Membership role arrays (`person_<group>_role`), which Core also
reads, are kept with the people. Entity IDs and memberships must be identical
in every stored period. Only one chunk file exists at once; it is deleted after
its chunk, also when the factory or a calculation fails.

Each output DataFrame contains `<entity>_id`, `weight`, and requested variable
columns, with exactly the source entity order. `weight` is the weight used by
`Microsimulation.get_weights`, projected from household weights; native input
entity weight columns are preserved in the chunk datasets. Weighted sums are
calculated from the assembled source-order arrays, avoiding changes in reduction
order. A requested variable can itself be an entity weight variable. The name
`weight` is reserved for the output weight column.

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
household. The current model has four formulas that reduce across every unit
in the simulation: the Medicaid state reductions
`medicaid_slcsp_state_average_cost_index` and `medicaid_slcsp_state_denominator`,
and the rankers `household_income_decile` and `spm_unit_income_decile`, which
call `MicroSeries.decile_rank` and would rank within the chunk. The helper
rejects these at calculation time, including indirect dependencies such as
`income_decile`, branches and reform baselines. The check runs in Core's
period-consistency hook, just before a formula would run, so it adds no frames
to a dependency chain; a chunked chain reaches the recursion limit when the
whole-file chain does. A guarded variable with a stored value returns that
value, because no formula reduces across the chunk. Known Medicaid
claiming-tax-unit links crossing households are also rejected. The SSI spouse
pairing also tests whether the whole simulation holds a single marital unit, so
a chunk with exactly one marital unit can differ from the whole file; such
chunks are rejected. Custom reform formulas remain the caller's responsibility:
cross-household reductions, order-dependent random draws and other global
dependencies are unsupported. These are calculation restrictions, not an
assumption that every model variable can be chunked.

The tests compare a full 32-household, five-state fixture with one, two, three
and seven chunks, plus random household assignments. They compare every entity
value and weighted sum, check source order and unchanged input frames, and use
weak references to check simulation release. The fixture includes households
with multiple tax and SPM units and Social Security recipients. The same
households written as a variable-centric file are compared with an unchunked
`Microsimulation` on that file for one, two, three and seven chunks and under a
parameter reform, and with the entity-table route. Real simulations check the
guard on direct, dependency, branch, baseline and cross-period routes, and a
frame-depth test checks that guarding adds at most three frames to the deepest
stack. Independent pre-change TOB branch calculations protect the statutory
signed allocation.

## TOB working memory

The TOB outputs difference `income_tax_chapter_1`, chapter 1 liability after
nonrefundable and before refundable credits, which leaves out the chapter 2A
net investment income tax. Counterfactual chapter 1 tax without Social
Security, and under bounded pre-1993 inclusion, is cached in parent variable
holders. The bound is the lesser of the pre-1993 section 86 amount and actual
inclusion, read in the outer simulation before either counterfactual branch
exists. A direct TOB calculation prepares those holders in separate outer
calculations, old-law first: current Core retains popped branches in active
calculation frames, so the frames must finish before collection. Each temporary
branch clones the system, clears non-input arrays, computes and copies only
chapter 1 tax, and is removed and collected before the next direct
counterfactual. A TOB dependency nested inside another formula can retain its
branch identities until that outer formula returns. OASDI remains bounded
old-law tax minus no-inclusion tax, total remains current chapter 1 tax minus
no-inclusion tax, and HI remains the signed residual. No per-unit floor is
introduced. See [OASDI modeled liabilities and benefits](social-security-oasdi-accounting.md)
for the accounting these outputs feed.

The PR records measured full-dataset peak memory and timing; small-fixture
exactness establishes correctness, not an RSS bound.
