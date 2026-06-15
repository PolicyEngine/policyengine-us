from policyengine_us.model_api import *


class ma_dese_csfp_county_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Massachusetts DESE CSFP county eligible"
    defined_for = StateCode.MA
    reference = (
        "https://www.doe.mass.edu/cnp/food_dist.html",
        "https://www.gbfb.org/what-we-do/our-programs/commodity-supplemental-food-program/",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.ma.dese.csfp
        return np.isin(county, p.counties)
