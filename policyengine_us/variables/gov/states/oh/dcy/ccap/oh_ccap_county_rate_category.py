from policyengine_us.model_api import *


class OHCCAPCountyRateCategory(Enum):
    CATEGORY_1 = "Category 1"
    CATEGORY_2 = "Category 2"
    CATEGORY_3 = "Category 3"


class oh_ccap_county_rate_category(Variable):
    value_type = Enum
    entity = Household
    possible_values = OHCCAPCountyRateCategory
    # Non-Ohio households fall through to Category 2; downstream consumers are
    # masked by defined_for, but the load-bearing default is needed because
    # vectorized formula execution does not short-circuit on defined_for.
    default_value = OHCCAPCountyRateCategory.CATEGORY_2
    definition_period = YEAR
    label = "Ohio CCAP county reimbursement rate category"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/assets/laws/administrative-code/pdfs/5180/6/1/5180$6-1-10_PH_FF_N_APP1_20251020_1028.pdf#page=1"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.oh.dcy.ccap.geography
        is_category_1 = np.isin(county, p.category_1_counties)
        is_category_2 = np.isin(county, p.category_2_counties)
        is_category_3 = np.isin(county, p.category_3_counties)
        # Category 2 is also the default for any non-Ohio county.
        return select(
            [is_category_1, is_category_2, is_category_3],
            [
                OHCCAPCountyRateCategory.CATEGORY_1,
                OHCCAPCountyRateCategory.CATEGORY_2,
                OHCCAPCountyRateCategory.CATEGORY_3,
            ],
            default=OHCCAPCountyRateCategory.CATEGORY_2,
        )
