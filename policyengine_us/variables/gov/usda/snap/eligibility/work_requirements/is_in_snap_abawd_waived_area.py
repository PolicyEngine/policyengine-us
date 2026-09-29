from policyengine_us.model_api import *

# Last day before P.L. 119-21 (approved July 4, 2025) struck the 7 U.S.C.
# 2015(o)(4)(A)(ii) "lack of sufficient jobs" waiver criterion. With
# hr1_waiver_criteria.in_effect false, the waiver lists in effect on this day
# stay waived. Core parameters cannot hold dates, so the instant lives here;
# test_snap_abawd_waived_counties.py checks that it is one day before the
# switch's first true value. It is not the "2025-06-01" pre-HR1 instant that
# is_snap_abawd_exempt uses for the age and exemption rules, because the
# waiver lists differ between the two dates: the Minnesota and North Dakota
# replacement waivers took effect 2025-07-01, and the Hawaii, Massachusetts,
# and Virginia waivers ended 2025-06-30.
PRE_HR1_WAIVER_SNAPSHOT = "2025-07-03"


def in_listed_abawd_waiver_area(p, state_code, county):
    # p is gov.usda.snap.work_requirements.abawd at some instant. Sub-state
    # waivers match the County enum name; statewide waivers match state_code.
    in_waived_county = np.zeros_like(state_code, dtype=bool)
    for state in p.waived_counties:
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
        "waived, while New Mexico's Bernalillo County is not. For records "
        "without county information this biases population results: "
        "residents of Delaware's New Castle County outside Wilmington (about "
        "half the state) and of Alaska's Anchorage (about 40 percent) are "
        "treated as waived, overstating coverage and the P.L. 119-21 waiver "
        "effect, while residents of New Mexico's 29 waived counties (about "
        "57 percent) are treated as unwaived, understating coverage and "
        "leaving an estimated waiver effect of about zero; in New York only "
        "Saratoga County (about 1.2 percent) is misclassified. See the "
        "waived_counties README for details. "
        "P.L. 119-21 section 10102(b) struck the lack-of-sufficient-jobs "
        "waiver criterion on enactment (2025-07-04). When "
        "gov.usda.snap.work_requirements.abawd.hr1_waiver_criteria.in_effect "
        "is false, the person is also treated as waived if their area was "
        "on the waiver lists in effect on 2025-07-03, the last day before "
        "enactment. This freezes that day's waiver geography rather than "
        "evaluating any waiver criterion. Months starting on or before "
        "2025-07-03 therefore keep the actual waiver geography, and later "
        "months add the 2025-07-03 geography, assuming every waiver in "
        "effect that day was renewed indefinitely."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        county = person.household("county_str", period.this_year)
        state_code = person.household("state_code_str", period.this_year)
        in_waived_area = in_listed_abawd_waiver_area(p, state_code, county)
        # Through the snapshot day, the dated lists already are the
        # pre-enactment geography, so both switch values give current law.
        if (
            p.hr1_waiver_criteria.in_effect
            or str(period.start) <= PRE_HR1_WAIVER_SNAPSHOT
        ):
            return in_waived_area
        # Pre-P.L. 119-21 geography: areas waived on the snapshot day stay
        # waived, in union with the current lists.
        p_pre = parameters(
            PRE_HR1_WAIVER_SNAPSHOT
        ).gov.usda.snap.work_requirements.abawd
        return in_waived_area | in_listed_abawd_waiver_area(p_pre, state_code, county)
