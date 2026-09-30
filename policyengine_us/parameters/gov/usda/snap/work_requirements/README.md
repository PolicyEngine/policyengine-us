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
| General work registration exemption for working 30 hours weekly or earning the federal minimum wage times 30 hours — 7 U.S.C. 2015(d)(2)(E); 7 CFR 273.7(b)(1)(vii) | Modeled | `is_snap_work_registration_exempt_employed`; usual weekly hours are averaged over weeks worked (`snap_work_requirement_weekly_hours`) and annual earnings over 52 weeks (`snap_work_requirement_weekly_earnings`), compared with `gov.usda.snap.work_requirements.general.weekly_hours_threshold` and that threshold times `gov.dol.minimum_wage`; setting `gov.simulation.snap_work_tests_average_over_year` to false switches to usual hours and earnings per week worked |
| General exemptions: disability, care of child under 6, care of incapacitated person — 7 CFR 273.7(b)(1)(ii), (iv) | Modeled | Shared between general and ABAWD checks |
| Non-age work registration exemptions: student enrollment, unemployment compensation receipt — 7 CFR 273.7(b)(1)(v), (viii) | Modeled | `is_snap_work_registration_exempt_non_age`; unemployment compensation exempts only in its months of receipt (`is_receiving_unemployment_compensation`), allocated from `weeks_unemployed` as one block per year with a start month hashed from a supplied `person_id` (datasets or explicit inputs) or otherwise from the person's position in the household, so every axis copy of a household matches; or all 12 months when weeks unemployed are not reported |
| Non-age work registration exemptions: TANF-complying, drug or alcohol treatment participants, unemployment compensation applicants not yet receiving — 7 CFR 273.7(b)(1)(iii), (v), (vi) | Partially modeled | `is_snap_work_registration_exempt_non_age` consumes the input variables `is_complying_with_tanf_work_requirements` (gated on TANF enrollment), `is_in_substance_use_treatment_program` and `has_applied_for_unemployment_compensation`; they default to false unless supplied, and no Populace US stage produces them (data parity is tracked in [PolicyEngine/populace#248](https://github.com/PolicyEngine/populace/issues/248)) |
| ABAWD work requirement of 20 hours a week averaged monthly, defined as 80 hours a month — 7 CFR 273.24(a)(1)(i) | Modeled | `meets_snap_abawd_work_requirements` compares average weekly hours (worked plus work program) times 52 / 12 with `gov.usda.snap.work_requirements.abawd.monthly_hours_threshold`; hours worked are averaged over weeks worked (`snap_work_requirement_weekly_hours`) |
| ABAWD age exemption brackets, including the HR1 change of the upper bound from 55 to 65 — 7 U.S.C. 2015(o)(3)(A) | Modeled | `gov.usda.snap.work_requirements.abawd.age_threshold.exempted` |
| ABAWD dependent-child age threshold, including the HR1 change from 18 to 14 — 7 U.S.C. 2015(o)(3)(C) | Modeled | `gov.usda.snap.work_requirements.abawd.age_threshold.dependent` |
| Removal of pre-HR1 homeless and veteran ABAWD exemptions | Modeled | Applied where HR1 is in effect via `is_snap_abawd_hr1_in_effect` |
| Pregnancy exemption — 7 U.S.C. 2015(o)(3)(E) | Modeled | Uses the `is_pregnant` input variable |
| Indian, Urban Indian, and California Indian ABAWD exemption — 7 U.S.C. 2015(o)(3)(F)-(G) | Partially modeled | `is_snap_abawd_indian_exempt` is consumed by the ABAWD formula but is an input variable with no formula; it defaults to false unless supplied |
| Qualifying work-program participation or hours counting toward the ABAWD requirement — 7 CFR 273.24(a)(1)(ii)-(iv) | Partially modeled | `weekly_snap_work_program_hours` and `is_snap_workfare_participant` are consumed by `meets_snap_abawd_work_requirements` but are input variables that default to zero or false unless supplied; Populace US releases list them as documented absent inputs because the CPS ASEC has no work-program item ([PolicyEngine/populace#249](https://github.com/PolicyEngine/populace/issues/249), closed) |

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

- `weekly_hours_worked_before_lsr`: usual weekly hours in the weeks worked;
  drives both the 30-hour general and 20-hour ABAWD thresholds through
  `snap_work_requirement_weekly_hours`.
- `weeks_worked`: weeks worked in the year; averages usual hours over the
  year. When it is 0 (not reported), usual hours are used unchanged.
- `employment_income_before_lsr`, `self_employment_income_before_lsr` and
  `sstb_self_employment_income_before_lsr`: drive the 30-hour exemption's
  earnings equivalent.
- `is_snap_abawd_indian_exempt`: no survey source; defaults to false.
- `is_pregnant`: no survey source; defaults to false.
- `is_incapable_of_self_care`: care-of-incapacitated-person exemption.
- `is_homeless` and `is_veteran`: pre-HR1 ABAWD exemptions.
- `is_snap_higher_ed_student` and `unemployment_compensation`: non-age work
  registration exemptions.
- `weeks_unemployed`: weeks spent looking for work; sets the months of
  unemployment compensation receipt. When it is 0 (not reported, as on
  ACS-based rows), any receipt exempts the person in all 12 months.

Population-level data parity is tracked separately in
[PolicyEngine/populace#248](https://github.com/PolicyEngine/populace/issues/248).
