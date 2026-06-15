from policyengine_us.model_api import *


class KYCCAPRateRegion(Enum):
    REGION_1 = "Region 1"
    REGION_2 = "Region 2"
    REGION_3 = "Region 3"
    REGION_4 = "Region 4"
    REGION_5 = "Region 5"
    REGION_6 = "Region 6"
    REGION_7 = "Region 7"
    REGION_8 = "Region 8"
    REGION_9 = "Region 9"
    REGION_10 = "Region 10"


class ky_ccap_rate_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = KYCCAPRateRegion
    default_value = KYCCAPRateRegion.REGION_1
    definition_period = MONTH
    label = "Kentucky CCAP rate region"
    defined_for = StateCode.KY
    reference = "https://www.chfs.ky.gov/agencies/dcbs/dcc/Documents/dcc300kymaxpaymentchart.pdf#page=1"

    def formula(household, period, parameters):
        # DCC-300 publishes a daily rate chart for all 120 counties. The 24-value
        # rate vector (4 provider types x 3 age groups x 2 day lengths) takes only
        # 10 distinct signatures, so counties are grouped into 10 rate regions.
        county = household("county_str", period)
        p = parameters(period).gov.states.ky.dcbs.ccap.regions
        regions = KYCCAPRateRegion
        return select(
            [
                np.isin(county, p.region_2),
                np.isin(county, p.region_3),
                np.isin(county, p.region_4),
                np.isin(county, p.region_5),
                np.isin(county, p.region_6),
                np.isin(county, p.region_7),
                np.isin(county, p.region_8),
                np.isin(county, p.region_9),
                np.isin(county, p.region_10),
            ],
            [
                regions.REGION_2,
                regions.REGION_3,
                regions.REGION_4,
                regions.REGION_5,
                regions.REGION_6,
                regions.REGION_7,
                regions.REGION_8,
                regions.REGION_9,
                regions.REGION_10,
            ],
            default=regions.REGION_1,
        )
