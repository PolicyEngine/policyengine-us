from policyengine_us.model_api import *


class WAWCCCRegion(Enum):
    REGION_1 = "Region 1"
    SPOKANE = "Spokane"
    REGION_2 = "Region 2"
    REGION_3 = "Region 3"
    REGION_4 = "Region 4"
    REGION_5 = "Region 5"
    REGION_6 = "Region 6"


class wa_wccc_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = WAWCCCRegion
    default_value = WAWCCCRegion.REGION_2
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC base geographic region"
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0205",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.wa.dcyf.wccc.region
        return select(
            [
                np.isin(county, p.region_1_counties),
                np.isin(county, p.spokane_counties),
                np.isin(county, p.region_2_counties),
                np.isin(county, p.region_3_counties),
                np.isin(county, p.region_4_counties),
                np.isin(county, p.region_5_counties),
                np.isin(county, p.region_6_counties),
            ],
            [
                WAWCCCRegion.REGION_1,
                WAWCCCRegion.SPOKANE,
                WAWCCCRegion.REGION_2,
                WAWCCCRegion.REGION_3,
                WAWCCCRegion.REGION_4,
                WAWCCCRegion.REGION_5,
                WAWCCCRegion.REGION_6,
            ],
            default=WAWCCCRegion.REGION_2,
        )
