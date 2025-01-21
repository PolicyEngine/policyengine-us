from policyengine_us.model_api import *


class nc_scca_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child age eligibility for North Carolina Subsidized Child Care Assistance (SCCA) program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.scca
        # child < 13 or disabled child < 17 to be eligible
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_age_limit, p.age_limit)
        age_eligible = person("age", period.this_year) < age_limit
    
        return age_eligible
