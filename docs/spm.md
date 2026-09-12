# Supplemental Poverty Measure

The country model uses the installed `spm-calculator` artifact for all five SPM
measurement amounts. It does not extrapolate thresholds with country CPI or income
parameters. Each supported year and scenario comes from the verified artifact.
The installed 1.0.0 artifact covers 2022 through 2035; unavailable years fail.
Taxes, benefits, resources and the housing-assistance cap
remain country-model formulas. General household benefits and CBO transfer
aggregates count actual `housing_assistance`; only SPM resources count
`spm_unit_capped_housing_subsidy`. The cap uses the canonical housing amount before
the final model storage conversion.

## Housing allocation and its assumptions

The country sums modeled `housing_assistance` within each household, then
allocates the total to SPM units in proportion to their member counts. Each
unit's cap applies after this allocation. This follows the subsidy proration in
[Census's technical documentation, page 14](https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14).
The allocated amount is an SPM resource valuation; general benefits still count
the original program awards. Multiple actual awards supplied in a household
are summed, not discarded.

The associated Microcosm producer uses independently reported household
public-housing or reduced-rent status, with these declared assumptions:

- **A1, assisted family:** the householder's SPM unit represents the assisted
  program family when the survey cannot identify its membership. This does not
  imply that housing law permits only one assisted family per household.
- **A2, timing:** interview-time housing receipt represents full-year receipt
  for the income year; it is not an observed twelve-month payment history.
- **A3, program coverage:** public housing and reported reduced rent are modeled
  through the existing HUD-family calculation, although reduced rent may include
  programs outside HUD.
- **A4, tenant contribution:** for SPM valuation, sum `hud_ttp` only for units
  with positive modeled housing assistance, then allocate that sum using the
  same member shares. This preserves the contribution associated with actual
  awards and excludes nonrecipients' hypothetical tenant payments. Census
  describes a household contribution but does not specify this multi-unit
  allocation; A4 is a consistency assumption, not verified Census parity.

The model retains its existing HUD program-family approximation, including
family income and utility treatment. These allocation variables do not alter
HUD eligibility, payments or utility allowances. Zero-award households need no
SPM geography for their zero housing resource. In assisted households, every
SPM unit receiving an allocated share needs a valid county and adult composition.

## Measurement configuration

`Simulation`, `Microsimulation` and `CountryTaxBenefitSystem` accept a serializable
`spm` mapping. Its fields are `forecast_content_sha256`, `scenario`,
`geography_kind`, `geography_id`, `county_vintage` and `as_of`. The hash, when given,
must match the installed artifact. The default scenario is the artifact's declared
default; the default county vintage is `"2020"`.

County geography is the default for both household and population calculations.
A local household must supply a valid `county_fips`. State alone does not identify
an SPM area. Missing counties raise `SPM_GEOGRAPHY_REQUIRED`; invalid or unavailable
counties raise `SPM_GEOGRAPHY_UNAVAILABLE`. There is no first-county, congressional
district or national fallback in SPM measurement.

These geography errors occur only when calculating an SPM measurement or a
dependent SPM resource, such as the housing-assistance cap for units allocated
housing assistance; units with no allocation are capped at zero without consulting the
measurement. A state-only tax request can still run. SPM reads the input-only `county_fips` variable and ignores any
county inferred or cached by other tax or benefit formulas. Geography and
composition errors are `SPMInputError` instances with `code` and `to_dict()`.

California CARE income excludes housing subsidies under
[CPUC Decision 14-08-030, Section 6.2](https://liob.cpuc.ca.gov/wp-content/uploads/sites/14/2020/12/ACF22B3.pdf#page=75)
and [Ordering Paragraph 40(3)](https://liob.cpuc.ca.gov/wp-content/uploads/sites/14/2020/12/ACF22B3.pdf#page=124).
[PG&E's June 2026 reply brief](https://docs.cpuc.ca.gov/PublishedDocs/Efile/G000/M608/K305/608305628.PDF#page=10)
confirms that its CARE/FERA income determination excludes housing subsidies,
despite contrary wording in its application. The shared CARE/FERA parameter
records the decision's effective date, August 14, 2014. Annual calculations
select the list at January 1, so calendar 2014 retains the earlier modeled
inclusion and calendar 2015 first applies the exclusion. Before that transition,
the model retains housing-subsidy inclusion using actual assistance; this update
does not validate the earlier income rule's historical policy basis. CARE/FERA
income never consults the SPM housing cap. The SPM resource calculation retains
its housing cap.

A caller can consciously select national measurement:

```python
simulation = Simulation(situation=household, spm={"geography_kind": "national"})
```

Or select one artifact area with `{"geography_kind": "metro", "geography_id":
"<area-id>"}`. A public application should display the national/local choice and
pass it explicitly; it should return structured validation errors when requested
local inputs are missing. This selection affects SPM measurement, not the
geography inputs used by other benefit programs.

`geography_id` applies only to a fixed metro selection; county mode uses each
household's observed `county_fips`. `as_of` is an ISO calendar date constraining
the artifact's information date. Configuration accepts no external forecast path
or consumer-side extrapolation policy.

`simulation.spm_config` returns fully resolved JSON-compatible settings, including
the artifact content hash. `simulation.spm_provenance()` returns detached runtime,
year, scenario and geography receipts. Each simulation has private receipt state;
policy-reform baselines retain the same measurement selection. Starting a new
simulation from a supplied system preserves its reform variables and starts fresh
receipts. Cloning a calculated simulation retains receipts for cached values and
detaches future receipts. Branches sharing policy parameters also have separate
SPM receipt state.

SPM adult counts use supplied age and a source-backed independence role. Explicit
household head/spouse primitives support household scenarios; the model never
guesses those roles from age ordering. A person counts as an SPM adult at age 18,
or at age 15 or above with `is_spm_independent_minor_role`. That role defaults to
the input-only `is_household_head | is_household_spouse` and can be supplied from
source data. A unit with no classified adult raises
`SPM_COMPOSITION_REQUIRED`. Generic age-based adult/child counts and benefit
eligibility are unchanged. The dataset loader rejects stored formula-owned SPM
outputs; observed source results should use report-only column names. It does not
delete or silently recalculate over supplied derived inputs.

`Microsimulation()` defaults to the immutable dataset URI
`hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-spm-20260909`.
This dataset supplies observed county inputs and source-backed independence roles.
The canonical country release must wait until that exact tag and its certified
bytes exist and pass independent readback. The unpublished candidate embeds the
same URI; local candidate checks do not establish production default availability.

The published country wheel requires exactly `spm-calculator==1.0.0`; it contains
no Git or local-path dependency. For coordinated development before registry
resolution is available, install the local calculator wheel into an isolated
environment and run tests with `uv run --no-sync`. Refresh the registry lockfile
when the calculator release is available to the resolver.
