# SNAP ABAWD waived counties

Each YAML file contains one state's county-level USDA FNS ABAWD time-limit
waivers. Keeping state timelines separate avoids repeating every active
county's name whenever one state starts, changes, or ends a waiver.

The parameters intentionally model only counties and county-equivalents.
Sub-county waivers are omitted because treating them as whole counties would
overstate eligibility. This excludes Connecticut's, Maine's, New Hampshire's,
and Rhode Island's town-level waivers; Montana's reservation-only waiver; and
reservation, city, or civil-subdivision areas included in several other state
approvals. Among the latter are New Mexico's FY2025 reservation areas (the
letter text says 18 reservations, but its Table 2 lists 14), Delaware's FY2025
waiver for the city of Wilmington (inside New Castle County, which is not
waived), and New York's FY2026 approval, which covers two reservation areas
only.

List entries must be exact `County` enum names, because
`is_in_snap_abawd_waived_area` matches them against `county_str`. A misspelled
name never matches and raises no error. New Mexico's Doña Ana County must be
written as the UTF-8 literal `DOÑA_ANA_COUNTY_NM`, with the precomposed `Ñ`
(U+00D1) that the enum uses, even though the FNS letter prints "Dona Ana
County". `DONA_ANA_COUNTY_NM` would silently never match.

Two county-grain approximations remain:

- Pennsylvania includes all of Butler and Cumberland counties even though the
  approval excludes Cranberry Township and Hampden Township, respectively.
- Household records without county information use `county_str`'s existing
  first-county-in-state fallback. In Alaska, that fallback is the waived
  Aleutians East Borough. In New York, it is Albany County, which is waived
  under the FY2025 waiver covering 61 of 62 counties. In Delaware, it is Kent
  County, which is waived even though the most populous county, New Castle,
  is not. In New Mexico, it is Bernalillo County, which is not waived.

The July 2025 Minnesota and North Dakota entries replace, rather than extend,
their earlier county lists. Minnesota changes from 15 to 17 counties, and
North Dakota changes from three counties to Rolette County only.

## Pre-P.L. 119-21 waiver geography

`gov.usda.snap.work_requirements.abawd.hr1_waiver_criteria.in_effect` is true
from 2025-07-04, when P.L. 119-21 section 10102(b) removed the "lack of
sufficient jobs" waiver criterion. When a reform sets it to false,
`is_in_snap_abawd_waived_area` treats an area as waived if the current dated
lists in this folder or `waived_states` waive it, or if those lists waived it
on 2025-07-03, the last day before enactment. The lists are read at the
earlier of the period start and 2025-07-03, so months before 2025-07-04 are
unchanged and later months keep the 2025-07-03 geography indefinitely. There
is no separate frozen copy of these lists: a correction to any list in effect
on 2025-07-03 flows into the counterfactual automatically.
