# SPM scope and ordinary housing income

The country model separates Supplemental Poverty Measure (SPM) outputs from
ordinary income for records outside a dataset's declared measurement universe.
It preserves included units' existing housing cap and canonical calculator
amounts. Dataset construction must supply the measurement universe and any
required outside housing valuation.

## Source decisions

Supply `spm_unit_spm_universe_status` for every SPM unit and year:

| Value | Measurement behavior |
| --- | --- |
| `INCLUDED` | Compute canonical amounts and poverty indicators. |
| `OUTSIDE` | Return missing SPM amounts, resources and poverty indicators; do not call the threshold provider for the unit. |
| `UNRESOLVED` | Raise `SPM_UNIVERSE_REQUIRED` when scope-dependent outputs are requested. |

Dataset simulations default to `UNRESOLVED`. A household situation defaults to
`INCLUDED`. The model never infers scope from missing tenure, age, county or a
zero-adult measurement composition. A dataset must resolve scope for each year;
an earlier year's declaration does not supply a later year's declaration.
Automatic dataset extension drops these annual source declarations from its
generated future-year tables; explicitly supplied multi-year tables retain them.

Source universes differ. Census's ACS research excludes all group quarters
because the public ACS does not identify the required subtypes. CPS-based SPM
includes some noninstitutional group quarters. A dataset release must identify
its source universe and validate household/member linkage before declaring
units outside. See [Census's ACS SPM research, pages 6–7](https://www.census.gov/content/dam/Census/library/working-papers/2020/demo/SEHSD-WP2020-09.pdf#page=6)
and [Census group-quarters guidance](https://www.census.gov/topics/income-poverty/guidance/group-quarters.html).

## Housing in ordinary income

`spm_unit_ordinary_housing_subsidy` supplies household benefits, CBO means-tested
transfers and California CPUC income. The corresponding contributed household
benefit overrides use the same output. SPM resources continue to use
`spm_unit_capped_housing_subsidy`.

| Unit | Ordinary housing value |
| --- | --- |
| Included | Existing capped SPM housing value, including supported policy overrides. |
| Outside with finite, nonnegative assistance equal to zero | Zero. |
| Outside with positive assistance | Explicit `spm_unit_ordinary_housing_subsidy_reported`, between zero and assistance. |

The reported input defaults to `-1`, a missing-value sentinel. Its year-local
formula and the dataset-extension exclusion prevent uprating or carry-forward
from manufacturing a new year's report. The model ignores this report for included units. A missing or
invalid required report raises `SPM_ORDINARY_HOUSING_VALUE_REQUIRED`. Invalid
assistance raises `SPM_HOUSING_ASSISTANCE_INVALID`. Core rejects explicit NaN
inputs before these formulas execute; computed invalid values reach these
typed checks.

A release supplying an outside value must retain its unit identifier, year,
allocation and valuation source. Numeric bounds do not establish that evidence.
Likewise, accepting the country's computed/input assistance of zero does not
certify observed nonreceipt; the release still must validate its source inputs.

Census first values housing assistance using market rent less tenant payment,
then caps the amount added to SPM resources at shelter need less tenant payment.
See the [SPM technical documentation, page 14](https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14).
That definition does not establish a housing valuation outside the SPM universe
or authorize changing CBO and CPUC conventions. This bridge preserves included
valuations and requires an explicit outside valuation.

## Nullable indicators and aggregation

The following outputs now use floating-point `0`, `1` and `NaN`:
`spm_unit_is_in_spm_poverty`, `spm_unit_is_in_deep_spm_poverty`, `in_poverty`,
`in_deep_poverty` and `person_in_poverty`. `NaN` identifies an outside record.
Included records with invalid resources or thresholds raise
`SPM_MEASUREMENT_INVALID`.
The indicators retain stock-quantity semantics: a monthly request returns the
annual classification without dividing a positive indicator by twelve.

Use `calculate(..., map_to="person")` and MicroSeries `count`, `sum` and `mean`
for person-weighted summaries. Keep outside records in full-population coverage
counts and exclude their missing indicators from the eligible denominator.
An empty eligible denominator yields a missing rate; serialize it as JSON
`null`. Do not cast these indicators to `bool`, negate them with `~`, or use
them directly as Boolean selection masks. Compare an observed indicator with
`1` when selecting poor units and separately retain its missingness mask.

Dataset inputs and `set_input` cannot override formula-owned measurement
outputs or the computed ordinary housing bridge. Preserve observed poverty
reports under separate report-only names.

The country consumer audit found only direct alias projections in production
Python; usage documentation uses MicroSeries means. The historical Utah
notebook divides one poverty mean by another and requires an explicit empty or
zero-baseline check before reuse. Wrapper serialization and summary consumers
require the companion nullable-summary change.

## Qualification limits

Synthetic tests exercise mixed included/outside records, canonical-provider
selection, included parity, missing outcomes, housing consumers, year-local
reports and contributed reforms. They do not certify a native population build,
outside housing source values or a complete managed-wrapper run.

Tiny country dataset fixtures also invoke dataset-dependent Medicaid allocation:
the model distributes statewide spending across the fixture's weighted enrolled
cost indices. Thus their absolute Medicaid totals do not represent household
estimates. Housing-component tests explicitly isolate Medicaid and CHIP where
needed to avoid float32 cancellation in CBO totals. This limitation reproduces
on the unchanged country base and requires representative population validation
before interpreting fiscal totals.
