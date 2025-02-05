from policyengine_us.model_api import *


class nc_scca_market_rate(Variable):
    value_type = int
    entity = Person
    label = "Child age eligibility for North Carolina Subsidized Child Care Assistance (SCCA) program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca

        county = person.household("county_str", period)

        age_group = person("nc_scca_age_group", period)

        rate_table = p.childcare_market_rates

        market_rate = rate_table[county][age_group]

        return market_rate
