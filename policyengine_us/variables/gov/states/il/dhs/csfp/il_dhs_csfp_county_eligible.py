from policyengine_us.model_api import *


class il_dhs_csfp_county_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Illinois DHS CSFP county eligible"
    defined_for = StateCode.IL
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=31874",
        "https://web.archive.org/web/20260320212109/https://www.dhs.state.il.us/page.aspx?item=31874",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.il.dhs.csfp
        return np.isin(county, p.counties)
