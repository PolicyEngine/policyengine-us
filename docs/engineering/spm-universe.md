# SPM measurement scope

The country model separates Supplemental Poverty Measure (SPM) outputs from
ordinary income for records outside a dataset's declared measurement universe.
Dataset construction must supply the measurement universe.

## Source decisions

Supply `spm_unit_spm_universe_status` for every SPM unit and year:

| Value | Measurement behavior |
| --- | --- |
| `INCLUDED` | Compute canonical amounts and poverty indicators. |
| `OUTSIDE` | Return missing SPM amounts, resources and poverty indicators; do not call the threshold provider for the unit. |
| `UNRESOLVED` | Raise `SPM_UNIVERSE_REQUIRED` when scope-dependent outputs are requested. |

Store the declaration on the SPM-unit table, for every year, as either the
member name (`"INCLUDED"`, `"OUTSIDE"`, `"UNRESOLVED"`) or the member index
(`0`, `1`, `2`); both encodings resolve the same scope. Any other stored value
raises `SPM_UNIVERSE_REQUIRED`: a name the enum does not define is rejected on
load, and an index the enum does not define fails closed at measurement rather
than removing the unit from the universe.

Dataset simulations default to `UNRESOLVED`. A household situation defaults to
`INCLUDED`. The model never infers scope from missing tenure, age, county or a
zero-adult measurement composition. A dataset must resolve scope for each year;
an earlier year's declaration does not supply a later year's declaration.
Automatic dataset extension drops these annual source declarations from its
generated future-year tables; explicitly supplied multi-year tables retain them.

Scope is a source-owned input with a household fallback, so it is listed in
`DATASET_SOURCE_INPUTS` rather than rejected. Setting it invalidates dependent
cached results, because every scope-dependent measurement and summary is
downstream of it.

Source universes differ. Census's ACS research excludes all group quarters
because the public ACS does not identify the required subtypes. CPS-based SPM
includes some noninstitutional group quarters. A dataset release must identify
its source universe and validate household/member linkage before declaring
units outside. See [Census's ACS SPM research, pages 6–7](https://www.census.gov/content/dam/Census/library/working-papers/2020/demo/SEHSD-WP2020-09.pdf#page=6)
and [Census group-quarters guidance](https://www.census.gov/topics/income-poverty/guidance/group-quarters.html).

## Housing in ordinary income

Ordinary income aggregates - general household benefits, CBO means-tested
transfers, California CPUC countable income and the contributed household
benefit overrides - add the modelled `housing_assistance` award, not the
Census SPM's capped housing valuation. That separation is independent of SPM
scope: `housing_assistance` is a program amount the model computes for every
unit, so these aggregates never consult the measurement universe and never
require a scope declaration.

SPM resources keep the capped valuation through
`spm_unit_capped_housing_subsidy`, which caps the SPM-unit-allocated award at
shelter need less the allocated tenant payment. That variable is scoped:
included units receive the capped value, outside units receive `NaN`. Included
allocated assistance must be finite and nonnegative; otherwise the formula
raises `SPM_HOUSING_ASSISTANCE_INVALID`.

Census first values housing assistance using market rent less tenant payment,
then caps the amount added to SPM resources at shelter need less tenant payment.
See the [SPM technical documentation, page 14](https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14).
That definition does not establish a housing valuation outside the SPM universe
or authorize changing CBO and CPUC conventions; those aggregates use the actual
award instead.

## Nullable indicators, distribution outputs and aggregation

The following outputs now use floating-point `0`, `1` and `NaN`:
`spm_unit_is_in_spm_poverty`, `spm_unit_is_in_deep_spm_poverty`, `in_poverty`,
`in_deep_poverty` and `person_in_poverty`. `NaN` identifies an outside record.
Included records with invalid resources or thresholds raise
`SPM_MEASUREMENT_INVALID`.
The indicators retain stock-quantity semantics: a monthly request returns the
annual classification without dividing a positive indicator by twelve.

`spm_unit_oecd_equiv_net_income` and `spm_unit_income_decile` inherit the same
universe. Equivalised income is `NaN` outside the universe, and decile ranks
are computed over the included units alone, so an outside record cannot move
another record's rank. Both are float stock quantities and both reject
non-finite included inputs with `SPM_MEASUREMENT_INVALID`.

Use `calculate(..., map_to="person")` and MicroSeries `count`, `sum` and `mean`
for person-weighted summaries. Keep outside records in full-population coverage
counts and exclude their missing indicators from the eligible denominator.
An empty eligible denominator yields a missing rate; serialize it as JSON
`null`. Do not cast these indicators to `bool`, negate them with `~`, or use
them directly as Boolean selection masks. Compare an observed indicator with
`1` when selecting poor units and separately retain its missingness mask.

Dataset inputs and `set_input` cannot override formula-owned measurement
outputs. Preserve observed poverty reports under separate report-only names.

The country consumer audit found only direct alias projections in production
Python; usage documentation uses MicroSeries means. The historical Utah
notebook divides one poverty mean by another and requires an explicit empty or
zero-baseline check before reuse. Wrapper serialization and summary consumers
require the companion nullable-summary change.

## Qualification limits

Synthetic tests exercise mixed included/outside records, canonical-provider
selection, included parity, missing outcomes, decile ranking, housing
consumers and contributed reforms. They do not certify a native population
build or a complete managed-wrapper run.

Tiny country dataset fixtures also invoke dataset-dependent Medicaid allocation:
the model distributes statewide spending across the fixture's weighted enrolled
cost indices. Thus their absolute Medicaid totals do not represent household
estimates. This limitation reproduces on the unchanged country base and
requires representative population validation before interpreting fiscal
totals.
