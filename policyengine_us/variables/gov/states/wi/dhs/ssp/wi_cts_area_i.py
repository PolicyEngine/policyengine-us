from policyengine_us.model_api import *


class wi_cts_area_i(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS uses Area I income limits"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=63"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        county = person.household("county", period.this_year).decode_to_str()
        return np.isin(county, p.area_i_counties) | person.household(
            "wi_cts_tribal_area_i", period
        )
