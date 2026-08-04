from policyengine_us.model_api import *


class is_in_snap_abawd_waived_area(Variable):
    value_type = bool
    entity = Person
    label = "Lives in an area with a waived SNAP ABAWD time limit"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_4",
        "https://www.law.cornell.edu/cfr/text/7/273.24#f",
        "https://www.fns.usda.gov/sites/default/files/resource-files/ak-abawd-response-fy2025.pdf#page=4",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-79.pdf#page=6",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2026/26-15.pdf#page=6",
    )
    documentation = (
        "Whether the person lives in an area where the USDA Food and "
        "Nutrition Service has waived the SNAP ABAWD time limit under "
        "7 U.S.C. 2015(o)(4) and 7 CFR 273.24(f). Sub-state waivers are "
        "matched on the County enum name via county_str (which derives "
        "from county_fips when a FIPS code is provided, so either input "
        "form matches); statewide waivers are matched on state_code. A "
        "household with no county information falls back to the first "
        "county alphabetically in its state, which for Alaska is the "
        "waived Aleutians East Borough — see waived_counties.yaml for "
        "the waiver provenance and this fallback's implications."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        county = person.household("county_str", period.this_year)
        state_code = person.household("state_code_str", period.this_year)
        in_waived_county = np.isin(county, p.waived_counties)
        in_waived_state = np.isin(state_code, p.waived_states)
        return in_waived_county | in_waived_state
