# SNAP ABAWD waived counties

Each YAML file contains one state's county-level USDA FNS ABAWD time-limit
waivers. Keeping state timelines separate avoids repeating every active
county's name whenever one state starts, changes, or ends a waiver.

The parameters intentionally model only counties and county-equivalents.
Sub-county waivers are omitted because treating them as whole counties would
overstate eligibility. This excludes Connecticut's, Maine's, New Hampshire's,
and Rhode Island's town-level waivers; Montana's reservation-only waiver; and
reservation, city, or civil-subdivision areas included in several other state
approvals.

Two county-grain approximations remain:

- Pennsylvania includes all of Butler and Cumberland counties even though the
  approval excludes Cranberry Township and Hampden Township, respectively.
- Household records without county information use `county_str`'s existing
  first-county-in-state fallback. In Alaska, that fallback is the waived
  Aleutians East Borough.

The July 2025 Minnesota and North Dakota entries replace, rather than extend,
their earlier county lists. Minnesota changes from 15 to 17 counties, and
North Dakota changes from three counties to Rolette County only.
