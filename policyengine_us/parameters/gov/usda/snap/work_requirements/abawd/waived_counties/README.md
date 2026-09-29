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
letter text says 18 reservations, but its Table 2 lists 14), New Mexico's
FY2026 reservation areas (Laguna Pueblo, San Felipe, Taos Pueblo, and Tesuque
Pueblo; FNS response of October 23, 2025, page 4, Table 2), Delaware's FY2025
waiver for the city of Wilmington (inside New Castle County, which is not
waived), and New York's FY2026 approval, which covers two reservation areas
only.

List entries must be exact `County` enum names, because
`is_in_snap_abawd_waived_area` matches them against `county_str`. A misspelled
name never matches and raises no error. New Mexico's Dona Ana County must be
written in `nm.yaml` with the precomposed N-tilde (U+00D1) that the enum uses
(`DO`, then U+00D1, then `A_ANA_COUNTY_NM`), even though the FNS letter prints
"Dona Ana County". The ASCII spelling `DONA_ANA_COUNTY_NM` would silently
never match. This README spells the name in ASCII only, because core reads
READMEs without specifying an encoding.

Two county-grain approximations remain:

- Pennsylvania includes all of Butler and Cumberland counties even though the
  approval excludes Cranberry Township and Hampden Township, respectively.
- Household records without county information use `county_str`'s existing
  first-county-in-state fallback. The fallback biases population results in
  states whose waivers cover only some counties:
  - Delaware falls back to Kent County, which is waived. Residents of New
    Castle County outside Wilmington (about 50 percent of the state) are
    therefore treated as waived from 2024-10 through 2025-09 and, with
    `hr1_waiver_criteria.in_effect` false, after enactment as well. Delaware
    waiver coverage and the estimated P.L. 119-21 waiver effect are
    overstated.
  - New Mexico falls back to Bernalillo County, which is not waived.
    Residents of the 29 waived counties (about 57 percent of the state) are
    therefore treated as unwaived. New Mexico waiver coverage is understated,
    and the estimated P.L. 119-21 waiver effect is about zero.
  - New York falls back to Albany County, which is waived under the FY2025
    waiver covering 61 of 62 counties. Only Saratoga County (about 1.2
    percent of the state) is misclassified.
  - Alaska falls back to the Aleutians East Borough, which is waived. The
    Municipality of Anchorage (about 40 percent of the state, 2020 Census)
    is therefore treated as waived, the same direction as Delaware.

  Supplying `county` or `county_fips` removes the bias.

The July 2025 Minnesota and North Dakota entries replace, rather than extend,
their earlier county lists. Minnesota changes from 15 to 17 counties, and
North Dakota changes from three counties to Rolette County only.

## Pre-P.L. 119-21 waiver geography

`gov.usda.snap.work_requirements.abawd.hr1_waiver_criteria.in_effect` is true
from 2025-07-04, when P.L. 119-21 section 10102(b) removed the "lack of
sufficient jobs" waiver criterion. When a reform sets it to false,
`is_in_snap_abawd_waived_area` treats an area as waived if the current dated
lists in this folder or `waived_states` waive it, or if those lists waived it
on 2025-07-03, the last day before enactment. Months that start on or before
2025-07-03 read only the current lists, which are the pre-enactment geography,
so they are unchanged; later months keep the 2025-07-03 geography
indefinitely. The switch freezes geography and evaluates no waiver criterion.
There is no separate frozen copy of these lists: a correction to any list in
effect on 2025-07-03 flows into the counterfactual automatically. The
counterfactual's limits are listed once, in the header of
`hr1_waiver_criteria/in_effect.yaml`.
