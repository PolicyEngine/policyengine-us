from policyengine_us.model_api import *

# Last day before P.L. 119-21 (approved July 4, 2025) struck the 7 U.S.C.
# 2015(o)(4)(A)(ii) "lack of sufficient jobs" waiver criterion. With
# hr1_waiver_criteria.in_effect false, the waiver lists in effect on this day
# stay waived. Core parameters cannot hold dates, so the instant lives here.
PRE_HR1_WAIVER_SNAPSHOT = "2025-07-03"


def in_listed_abawd_waiver_area(p, state_code, county):
    # p is gov.usda.snap.work_requirements.abawd at some instant. Sub-state
    # waivers match the County enum name; statewide waivers match state_code.
    in_waived_county = np.zeros_like(state_code, dtype=bool)
    for state in p.waived_counties._children:
        in_waived_county |= (state_code == state.upper()) & np.isin(
            county,
            p.waived_counties[state],
        )
    return in_waived_county | np.isin(state_code, p.waived_states)


class is_in_snap_abawd_waived_area(Variable):
    value_type = bool
    entity = Person
    label = "Lives in an area with a waived SNAP ABAWD time limit"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_4",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title7/pdf/USCODE-2023-title7-chap51-sec2015.pdf#page=10",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=12",
        "https://www.law.cornell.edu/cfr/text/7/273.24#f",
        "https://www.fns.usda.gov/sites/default/files/resource-files/ak-abawd-response-fy2025.pdf#page=4",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-79.pdf#page=6",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2026/26-15.pdf#page=6",
        "https://www.usda.gov/sites/default/files/guidance-documents/fna.obbb-time-limit-waivers-reinstatement.pdf#page=2",
    )
    documentation = (
        "Whether the person lives in an area where the USDA Food and "
        "Nutrition Service has waived the SNAP ABAWD time limit under "
        "7 U.S.C. 2015(o)(4) and 7 CFR 273.24(f). Sub-state waivers are "
        "matched on the County enum name via county_str (which derives "
        "from county_fips when a FIPS code is provided, so either input "
        "form matches); statewide waivers are matched on state_code. A "
        "household with no county information falls back to the first "
        "county alphabetically in its state: Alaska's Aleutians East "
        "Borough, New York's Albany County, and Delaware's Kent County are "
        "waived, while New Mexico's Bernalillo County is not. See the "
        "waived_counties state parameters for the waiver provenance and "
        "this fallback's implications. P.L. 119-21 section 10102(b) struck "
        "the lack-of-sufficient-jobs waiver criterion on enactment "
        "(2025-07-04). When "
        "gov.usda.snap.work_requirements.abawd.hr1_waiver_criteria.in_effect "
        "is false, the person is also treated as waived if their area is on "
        "the waiver lists in effect on the earlier of the period start and "
        "2025-07-03, the last day before enactment. Months before 2025-07-04 "
        "therefore keep the actual waiver geography, and later months add "
        "the 2025-07-03 geography, assuming every waiver in effect that day "
        "was renewed indefinitely."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        county = person.household("county_str", period.this_year)
        state_code = person.household("state_code_str", period.this_year)
        in_waived_area = in_listed_abawd_waiver_area(p, state_code, county)
        if p.hr1_waiver_criteria.in_effect:
            return in_waived_area
        # Pre-P.L. 119-21 criteria: areas waived on the snapshot day stay
        # waived, in union with the current lists. Before that day the dated
        # lists already are the pre-enactment geography, so read them at the
        # earlier of the period start and the snapshot; pre-enactment months
        # then match current law exactly.
        snapshot = min(str(period.start), PRE_HR1_WAIVER_SNAPSHOT)
        p_pre = parameters(snapshot).gov.usda.snap.work_requirements.abawd
        return in_waived_area | in_listed_abawd_waiver_area(p_pre, state_code, county)
