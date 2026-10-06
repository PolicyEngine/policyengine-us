from policyengine_us.model_api import *


class ca_tanf_region1(Variable):
    value_type = bool
    entity = Household
    label = "In a CalWORKs region 1 county"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/calworks/composition/minimum-basic-standard-of-adequate-care.html"

    def formula(household, period, parameters):
        county = household("county_str", period)
        region1_counties = parameters(
            period
        ).gov.states.ca.cdss.tanf.cash.region1_counties
        return np.isin(county, region1_counties)
