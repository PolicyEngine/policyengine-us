from policyengine_us.model_api import *


class is_in_snap_abawd_waived_area(Variable):
    value_type = bool
    entity = Person
    label = "Lives in an area with a waived SNAP ABAWD time limit"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_4",
        "https://www.law.cornell.edu/cfr/text/7/273.24#f",
        "https://www.fna.usda.gov/sites/default/files/resource-files/ak-abawd-response-fy2025.pdf",
    )
    documentation = (
        "Whether the person lives in an area where the USDA Food and "
        "Nutrition Service has waived the SNAP ABAWD time limit under "
        "7 U.S.C. 2015(o)(4) and 7 CFR 273.24(f). Waived areas are "
        "identified by county FIPS code. When a dataset does not include "
        "county geography, county_fips defaults to an empty string and "
        "this variable returns False, so no area waiver applies."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        county_fips = person.household("county_fips", period.this_year)
        return np.isin(county_fips, p.waived_county_fips)
