from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible person for the Massachusetts EAEDC dependent care deduction"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.age_threshold
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        meets_age_limit = age < p.dependent
        return is_dependent & meets_age_limit
