# Supplemental Poverty Measure

The country model uses the installed `spm-calculator` artifact for all five SPM
measurement amounts. It does not extrapolate thresholds with country CPI or income
parameters. Each supported year and scenario comes from the verified artifact.
The installed 1.0.0 artifact covers 2022 through 2035; unavailable years fail.
Taxes, benefits, resources and the housing-assistance cap
remain country-model formulas. The cap uses the canonical housing amount before
the final model storage conversion.

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
dependent resource, such as the housing-assistance cap for units with housing
assistance; units with none are capped at zero without consulting the
measurement. A state-only tax request can still run. SPM reads the input-only `county_fips` variable and ignores any
county inferred or cached by other tax or benefit formulas. Geography and
composition errors are `SPMInputError` instances with `code` and `to_dict()`.

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
no Git or local-path dependency. The committed `uv.lock` resolves that release
from PyPI, so `uv sync --locked --extra dev` installs the calculator with every
other dependency and needs no local wheel.
