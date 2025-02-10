from policyengine_us.model_api import *


class nc_scca_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child age eligibility for North Carolina Subsidized Child Care Assistance (SCCA) program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca
        disabled_age_limit = p.disabled_age_limit
        school_age_limit = p.school_age_limit

        is_disabled = person("is_disabled", period.this_year)
        age = person("age", period)

        # Apply disabled_age_limit only if child is under 18 and disabled
        age_limit = where((age < disabled_age_limit) & is_disabled, disabled_age_limit, school_age_limit)

        print(f"age_limit: {age_limit}, age: {age}, is_disabled: {is_disabled}")

        age_eligible = age < age_limit
    
        return age_eligible & person("is_tax_unit_dependent", period)