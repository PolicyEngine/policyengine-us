# SNAP work requirements coverage

This document records which SNAP work-requirement rules are modeled in
PolicyEngine US, which are partially modeled, and which are pending, on a
rule-by-rule and state-by-state basis. It covers general work registration
(7 CFR 273.7), the Able-Bodied Adult Without Dependents (ABAWD) time limit
(7 CFR 273.24), and the HR1/OBBBA changes (P.L. 119-21, Section 10102(a),
effective 2025-07-04).

Maintenance: this document and the accompanying coverage tests
(`policyengine_us/tests/policy/baseline/gov/usda/snap/eligibility/work_requirements/state_coverage.yaml`)
must be updated as the child issues of
[#8820](https://github.com/PolicyEngine/policyengine-us/issues/8820)
([#8821](https://github.com/PolicyEngine/policyengine-us/issues/8821)–[#8824](https://github.com/PolicyEngine/policyengine-us/issues/8824))
land.

## Rule-by-rule coverage

| Rule | Status | Notes |
| --- | --- | --- |
| General work registration age exemptions (under 16, 60 and older) — 7 CFR 273.7(b)(1)(i) | Modeled | `meets_snap_general_work_requirements` |
| General work registration 30-hour weekly work threshold — 7 CFR 273.7(b)(1)(vii) | Modeled | `gov.usda.snap.work_requirements.general.weekly_hours_threshold` |
| General exemptions: disability, care of child under 6, care of incapacitated person — 7 CFR 273.7(b)(1)(ii), (iv) | Modeled | Shared between general and ABAWD checks |
| Non-age work registration exemptions: student enrollment, unemployment compensation receipt — 7 CFR 273.7(b)(1)(v), (viii) | Modeled | `is_snap_work_registration_exempt_non_age` |
| Non-age work registration exemptions: TANF-complying, drug or alcohol treatment participants, unemployment compensation applicants not yet receiving — 7 CFR 273.7(b)(1)(iii), (v), (vi) | Pending | [#8824](https://github.com/PolicyEngine/policyengine-us/issues/8824); requires additional input variables |
| ABAWD 20-hour weekly work threshold — 7 CFR 273.24(a)(1)(i) | Modeled | `meets_snap_abawd_work_requirements` |
| ABAWD age exemption brackets, including the HR1 change of the upper bound from 55 to 65 — 7 U.S.C. 2015(o)(3)(A) | Modeled | `gov.usda.snap.work_requirements.abawd.age_threshold.exempted` |
| ABAWD dependent-child age threshold, including the HR1 change from 18 to 14 — 7 U.S.C. 2015(o)(3)(C) | Modeled | `gov.usda.snap.work_requirements.abawd.age_threshold.dependent` |
| Removal of pre-HR1 homeless and veteran ABAWD exemptions | Modeled | Applied where HR1 is in effect via `is_snap_abawd_hr1_in_effect` |
| Pregnancy exemption — 7 U.S.C. 2015(o)(3)(E) | Modeled | Uses the `is_pregnant` input variable |
| Indian, Urban Indian, and California Indian ABAWD exemption — 7 U.S.C. 2015(o)(3)(F)-(G) | Partially modeled | `is_snap_abawd_indian_exempt` is consumed by the ABAWD formula but is an input variable with no formula; it defaults to false unless supplied |
| Qualifying work-program participation or hours counting toward the ABAWD requirement | Pending | [#8823](https://github.com/PolicyEngine/policyengine-us/issues/8823); only employment hours (`weekly_hours_worked_before_lsr`) are counted |

## State-by-state HR1 ABAWD effective dates

`is_snap_abawd_hr1_in_effect` determines whether the HR1 ABAWD changes apply
to a person, based on their state.

| State(s) | Model behavior | Actual policy | Status |
| --- | --- | --- | --- |
| All states except CA, HI, AK | HR1 in effect from 2025-07-04 (`gov.usda.snap.work_requirements.abawd.in_effect`) | Federal effective date 2025-07-04 | Modeled |
| CA | HR1 in effect from 2026-06-01 (`gov.states.ca.cdss.snap.work_requirements.abawd.hr1_in_effect`, per ACL 25-93) | Delayed implementation to 2026-06-01 | Modeled |
| HI, AK | HR1 applied at the federal 2025-07-04 date | Delayed implementation to 2025-11-01 | Pending [#8821](https://github.com/PolicyEngine/policyengine-us/issues/8821); the `gov.usda.snap.work_requirements.abawd.exempt_states` parameter exists but is not consumed by any formula |
| AK boroughs with high-unemployment waivers | No sub-state waiver geography | Borough-level ABAWD waivers | Pending [#8822](https://github.com/PolicyEngine/policyengine-us/issues/8822) |

## Data-dependent input limitations

Several exemption paths depend on input variables that standard survey
microdata do not carry, so household-level results are only as precise as the
supplied inputs:

- `weekly_hours_worked_before_lsr`: hours worked; drives both the 30-hour
  general and 20-hour ABAWD thresholds.
- `is_snap_abawd_indian_exempt`: no survey source; defaults to false.
- `is_pregnant`: no survey source; defaults to false.
- `is_incapable_of_self_care`: care-of-incapacitated-person exemption.
- `is_homeless` and `is_veteran`: pre-HR1 ABAWD exemptions.
- `is_snap_higher_ed_student` and `unemployment_compensation`: non-age work
  registration exemptions.

Population-level data parity is tracked separately in
[PolicyEngine/populace#248](https://github.com/PolicyEngine/populace/issues/248).
