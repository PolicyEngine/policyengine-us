# Social Security benefit levers

The benefit lever interface separates reported annual benefits from public
benefit outputs. Stable public formulas combine a selected reported source with
independent across-the-board and supplied payable-share factors, and one joint
payment-year COLA factor. All factors are one by default. A stored-data preflight
checks the scoring artifact's identity and columns before population scoring.

The engine contract does not certify API or application field exposure.
Calculated benefit source modes are reserved for subsequent implementations.
No package-specific values are part of this interface.

## Input and override contract

The public components are `social_security_retirement`,
`social_security_disability`, `social_security_survivors`, and
`social_security_dependents`. Their `_reported` twins are pure annual Person
inputs, including zero, with the original effective per-capita SOI/CBO
uprating. Public formulas have no variable-level uprating. Dataset extension
still uprates original column names before constructor migration.

Initial ingress through either PE-US constructor, dataset loading, or Core's
`SimulationBuilder` (including YAML) migrates a legacy public input to its
reported twin separately for each supplied period. The public formula then
applies the levers in the stored year as well as later years. When both names
are supplied in the same period, the reported amount remains the source and
the public input remains a final override.

A public `set_input` after construction is a final override for its own period.
It also seeds or refreshes the reported twin for that period unless the caller
explicitly supplied that twin. Automatically migrated or seeded twins follow
later public writes, preserving main's uprating and earlier-year lookbacks;
calculated or uprated caches do not block seeding. An explicitly supplied
reported input, including zero, retains precedence. Aggregate `social_security`
inputs remain final overrides.
Clones and branches retain these rules. Later public writes replace their
runtime input-name list privately, preserving overrides in legacy extraction
without changing a parent or sibling clone. Migrated inputs extract as twins;
later overrides extract alongside their twins and retain precedence on reload.
A private provenance envelope preserves the distinction between automatic and
explicit sources through legacy extraction and complete snapshots, including
subsequent public writes after reload. Builders consume this metadata before
validating ordinary situation inputs.

This compatibility layer requires Core 3.33.1 or later for recorded-input,
storage-origin and replay APIs. The lockfile uses Core 3.33.2.

Each component has a `_source` selector with default `reported`. Reserved
options `supplied_aime`, `supplied_pia`, `supplied_ratio_survivor`, and `history`
fail explicitly until their calculation routes are implemented. Selection never
depends on whether an amount is positive. The selected `_base` and the
`_pia_ratio_factor` (currently one) are separate from reported inputs. Future
calculated routes must bypass population PIA and COLA factors, apply the other
factors once, and perform their earnings test on the resulting payable amount.

`policyengine_us.tools.social_security_inputs.export_source_inputs(simulation)`
exports all recorded pure-input periods and entity memberships as `sources`,
with supplied formula-variable values in a separate `overrides` payload. Cached
calculations are excluded. `reload_source_inputs(payload, ...)` restores sources
before final overrides. Core's legacy `extract_person` retains every recorded
input period for the four benefit components and their reported twins, excluding
formula caches. This keeps later overrides final on reload and preserves their
source histories and future uprating. Other variables keep Core's usual first
known period. Neither interface settles the separate API/application metadata
and field-exposure contract.

Annual benefit inputs retain Core's period normalization. For example, supplying
`social_security_retirement: {"2024-07": 500}` through a PE-US constructor stores
500 under the rolling annual period `year:2024-07`, then migrates that exact
stored period to `_reported`. A July monthly output still follows Core's normal
calendar-year amount divided by twelve; it is not a new monthly entitlement
schedule. The complete source snapshot preserves the rolling annual key.

PE-US wrappers also preserve an exact supplied multi-year annual total, such as
`year:2024:2`. They apply a benefit multiplier only when it is identical in every
calendar year covered by that total. Differing annual multipliers require
separately supplied annual source amounts, because the total provides no annual
allocation for nonzero rows. Zero rows remain zero. An exact supplied `_base`
amount takes precedence over `_reported`, and base neutralization or abolition
still applies; base overrides for only part of a multi-year source require
annual source amounts. Explicit public multi-year inputs remain final overrides,
and neutralization still takes precedence. Raw Core `SimulationBuilder` and YAML
should supply canonical annual `_reported` periods for lever calculations; the
additional exact multi-year reported-source adapter belongs to PE-US wrappers.
A weighted `Microsimulation` request also needs an explicit weight for that exact
multi-year period, matching Core.

## Parameters and composition

All lever parameters live under `gov.contrib.ssa.benefit_levers`:

| Parameter | Default | Meaning |
| --- | --- | --- |
| `across_the_board.start_year` | 9999 | First affected payment year |
| `across_the_board.rate` | 0 | Proportional change, finite and at least -1 |
| `payable.share` | 1 | Externally supplied annual share in [0,1] |
| `payable.oasi_only` | false | OASI-only rather than combined OASDI |
| `cola.start_year` | 9999 | First affected January payment year |
| `cola.effective_year` | 0 | Optional first affected COLA effective year |
| `cola.effective_month` | 12 | Effective month when effective year is supplied |
| `cola.end_year` | 0 | Last affected payment year, or no end |
| `cola.pp_change` | 0 | Addition to the annual proportional COLA rate |
| `cola.alternative_rate` | -1 | Supplied pinned alternative annual rate; -1 selects baseline |
| `cola.withholding_enabled` | false | Enable component payment-year withholding terms |

A positive `effective_year` takes precedence over `start_year`: December 2028
means the first affected check is January 2029. Parameter values can vary by
payment year. Example modeling assumptions are CPI-E `pp_change = 0.0015`
(+0.15 percentage points), or chained CPI `pp_change = -0.0030`
(-0.30 percentage points), with an explicitly selected start. These are examples,
not observed index series or package presets. An alternative-rate path must be
pinned and recorded by its supplier; it is not generated from a household.

For each exposed payment event, statutory baseline rate c and configured
addition delta give adjusted rate max(0,c+delta), without a second rounding of
the policy addition. The joint multiplier is `(1+adjusted)/(1+c)` unless that
event is withheld, in which case it is `1/(1+c)`. Each component's
`_cola_withheld` term defaults false; a subsequent means-test implementation
supplies the rules. Switching a policy off later preserves its earlier effect
on the benefit level. Public reported-route benefits multiply this joint factor,
the PIA ratio factor, the across-the-board factor, and the payable factor once.

The payable supplier specifies an annual path beginning in the depletion year
and supplies a blended share for a depletion year beginning partway through the
year. The engine does not predict depletion, share paths, or within-year fund
cash flow. In OASI-only mode, disability is unaffected; a positive dependent
benefit requires an explicit `social_security_dependents_fund` of `oasi` or `di`.
Mixed or unidentified dependent streams require an external allocation/blended
scenario; the engine does not assign the entire stream to OASI silently.

## COLA history and exposure

Historical statutory events are under `gov.ssa.cola_history` through December
2025 (January 2026 payment), including June/July events before 1983, zero-rate
years and the corrected December 1999 2.5% rate. The current main January 2027
SSA schedule already includes the actual Q3 2026 index. Starting with that
schedule entry, rate construction uses `gov.ssa.uprating`, comparing with the Q3
index associated with the last effective nonzero COLA. Decimal half-up rounding
to 0.1 percentage point preserves the high-water base over zero-COLA years.
`cola_events(system.parameters, through_year)` in
`tools.social_security_benefit_levers` exports the exact baseline schedule for a
scoring receipt. Freeze this schedule together with the reform parameters.

Historical PIA COLA rounding is implemented separately by
`tools.ssa_cola_history.apply_cola_to_pia`: round upward to a dime before June
1982 and downward thereafter; unknown rule codes fail explicitly. Reported-route
ratios validate exposed rules but do not reconstruct a rounded individual PIA
from an annual recipient amount. Initial-PIA computations/inverses before the
1983 benchmark remain outside this implementation. Bend-point history is now
available back to 1979 for future services.

Per-component optional inputs are `_first_cola_year`/`_first_cola_month`,
`_worker_eligibility_year`, `_worker_id`, and
`_entitlement_year`/`_entitlement_month`. A first-COLA date takes precedence.
A worker link follows an explicit component basis on the linked worker, falling
back to the shared authoritative `social_security_worker_computation_year`.
A supplied recipient basis is preserved; conflicting positive bases or invalid
links fail. No disability or deceased-worker computation basis is inferred from
a linked worker's retirement age.

Absent identified dates, own retirement uses age-62 eligibility (even if claiming
later); older survivors use an age-60 recipient proxy. Positive disability,
child/caregiver dependents and young survivors use a pre-start exposure proxy.
These proxies are assumptions, not observed histories. Supply current-year
entitlement/first-COLA dates as the lower-exposure sensitivity; compare adjacent
retirement eligibility years for integer-age birthday uncertainty and age-50
survivor or linked-record alternatives where relevant. Report these sensitivity
envelopes separately from identified results. Without worker/share information,
auxiliary PIA inversion remains unidentified.

Each projected cross-section infers eligibility anew from `year - age + 62`.
It does not carry cohorts or income histories across static population rows.
A supplied retirement entitlement/claim date does not erase pre-claim COLAs.
Pre-1983 retirement eligibility can expose a July payment in its eligibility
year; modern retirement eligibility first exposes January of the next year.

Run the stored-data preflight described in
[the scoring-data guide](usage/social-security-scoring-preflight.md) before
population lever scoring. Its receipt records the artifact, bytes hash, stored
year, full stored columns, source mapping and projection convention.

For a supplied alternative-index level path, convert its pinned levels (including
an explicit pre-start anchor) with `projected_cola_rates`, then supply the
resulting payment-year rates under `cola.alternative_rate`. Record the source,
anchor, level path and generated rate path with the scoring receipt.
