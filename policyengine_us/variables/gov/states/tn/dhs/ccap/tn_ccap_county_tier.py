from policyengine_us.model_api import *


class TNCCAPCountyTier(Enum):
    TOP_TIER = "Top Tier"
    LOWER_TIER = "Lower Tier"


class tn_ccap_county_tier(Variable):
    value_type = Enum
    entity = Household
    possible_values = TNCCAPCountyTier
    default_value = TNCCAPCountyTier.LOWER_TIER
    definition_period = MONTH
    label = "Tennessee CCAP county reimbursement tier"
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf",
        "https://www.tn.gov/content/dam/tn/human-services/documents/Current%20state%20rate%20and%20QRIS%20bonus%20table.pdf",
    )

    def formula(household, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.county_tier
        county = household("county_str", period.this_year)
        is_top_tier = np.isin(county, p.top_tier_counties)
        return where(
            is_top_tier,
            TNCCAPCountyTier.TOP_TIER,
            TNCCAPCountyTier.LOWER_TIER,
        )
