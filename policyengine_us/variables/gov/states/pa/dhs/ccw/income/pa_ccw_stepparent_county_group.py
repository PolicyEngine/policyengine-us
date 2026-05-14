from policyengine_us.model_api import *


class pa_ccw_stepparent_county_group(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    default_value = 1
    label = "Pennsylvania CCW stepparent deduction county group"
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=76"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.pa.dhs.ccw.stepparent_deduction

        is_group_2 = np.isin(county, p.county_group_2)
        is_group_3 = np.isin(county, p.county_group_3)
        is_group_4 = np.isin(county, p.county_group_4)

        return select(
            [is_group_4, is_group_3, is_group_2],
            [4, 3, 2],
            default=1,
        )
