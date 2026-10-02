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
only. Other omitted sub-county parts include:

- FY2024 waivers keyed at their mid-2024 implementation dates: Minnesota's
  10 reservation areas and North Dakota's Turtle Mountain reservation area
  (both from 2024-07-01).
- FY2024 waivers keyed at 2024-11-01: Michigan's Oak Park city, New Jersey's
  Trenton city, and Oregon's eight reservation areas.
- FY2025 waivers: Alaska's Eklutna ANVSA, Arizona's 16 reservation areas,
  Michigan's three cities and 10 reservation areas, Minnesota's nine
  reservation areas, North Dakota's Turtle Mountain reservation area,
  Oregon's seven reservation areas, South Dakota's six reservation areas,
  and Washington's one reservation area.
- FY2026 waivers: Arizona's six reservation areas; Michigan's six cities
  (Bay City, Detroit, Eastpointe, Flint, Jackson, and Saginaw) and eight
  reservation areas; Minnesota's four reservation areas; New Jersey's
  Camden city; and Nevada's 12 reservation areas and colonies. The New
  York, Oregon, and Wisconsin FY2026 approvals cover reservation areas
  only, so they add no county.

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
  - Michigan falls back to Alcona County, which is waived under the FY2024,
    FY2025, and FY2026 lists, so a Michigan household without county
    information is treated as waived from 2024-11 through 2026-10.
    Coverage is overstated, most of all from 2026-03 through 2026-10, when
    the FY2026 waiver covers 15 of 83 counties.
  - Kentucky (Adair County), New Jersey (Atlantic County), Oregon (Baker
    County), and Washington (Adams County) fall back to counties waived
    under their FY2024 and FY2025 lists but outside any FY2026 list, so
    such households are treated as waived through each state's FY2025
    expiration and as unwaived afterward.
  - Arizona (Apache County), Minnesota (Aitkin County), and Nevada (Carson
    City) fall back to counties outside their FY2026 lists (Yuma,
    Clearwater, and Mineral counties, respectively), as New Mexico's
    Bernalillo County is outside its FY2026 Luna County list.

  Supplying `county` or `county_fips` removes the bias.

The July 2025 Minnesota and North Dakota entries replace, rather than extend,
their earlier county lists. Minnesota changes from 15 to 17 counties, and
North Dakota changes from three counties to Rolette County only.

## Dating conventions

These rules apply to the county lists in this folder; each rule notes
where `waived_states` differs.

- Modeling start. Waivers that ended before 2024-11-01, the waiver
  parameters' modeling start date, are not modeled (for example, Arizona's
  FY2024 waiver, which ended 2024-09-30). The FY2024 Kentucky, Michigan,
  New Jersey, Oregon, and Washington county waivers, which took effect
  between 2023-12-01 and 2024-03-01 and were still running on 2024-11-01,
  are keyed at 2024-11-01, as `waived_states` does for the DC, NY, and NM
  FY2024 waivers; the comment above each list gives the actual
  implementation date. County approvals that took effect from mid-2024 on
  are keyed at their implementation dates. `waived_states` does not follow
  that last rule: Nevada's statewide waiver, in effect from 2024-07-01, is
  keyed at 2024-11-01 there. Months before 2024-11 are therefore
  incomplete.
- Overlapping approvals. A dated list is the union of every county approval
  for that state in effect that month. When a new approval takes effect
  while an older, reinstated approval in the same file is still running and
  the new area is inside the old list, no key is added at the new
  approval's start; the list switches when the old approval ends, and a
  comment says so. Michigan's FY2026 waiver (from 2025-11-01) sits inside
  its FY2025 list through 2026-02-28, and Minnesota's FY2026 Clearwater
  County waiver (from 2025-12-01) sits inside its FY2025 list through
  2026-06-30. A statewide waiver in `waived_states` does not count as an
  older approval here, so `ca.yaml` is keyed at its counties' 2025-11-01
  implementation date even though the reinstated California statewide
  waiver ran through 2026-01-31.

## Alaska

From 2025-11-01 through 2026-10-31 two FNS approvals cover Alaska:

- a 7 U.S.C. 2015(o)(4) area waiver for 20 boroughs and census areas under
  the noncontiguous-State criterion (unemployment at least 1.5 times the
  national rate; FNS response, October 23, 2025); and
- a 7 U.S.C. 2015(o)(7) good-faith exemption, which the Alaska Division of
  Public Assistance describes as covering every borough and census area
  except the Municipality of Anchorage.

`ak.yaml` keeps all 29 non-Anchorage areas for that period and marks the
nine that only the good-faith exemption covers. The same approval supplies
the retained pre-HR1 exceptions in the `good_faith_exemption` parameters
(for example, the 56-to-64 age band).

Limitation: FNS has posted no approval document for Alaska's good-faith
exemption, so the geographic scope rests on the Alaska Division of Public
Assistance FAQ. The nine marked entries follow that FAQ (all areas except
Anchorage), although FNS Q&A #1
(June 11, 2026, question 17) describes (o)(7) exemptions as applying to
individuals rather than to areas. If FNS terminates the exemption early
(7 U.S.C. 2015(o)(7)(D)(ii)), remove the nine marked entries from that
date.

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
