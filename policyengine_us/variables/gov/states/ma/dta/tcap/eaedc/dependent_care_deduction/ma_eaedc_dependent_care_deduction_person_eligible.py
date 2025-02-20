from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction_person_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts EAEDC dependent care deduction per person eligible"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.deductions.dependent_care
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        meets_age_limit = age < p.dependent_age_threshold
        return is_dependent & meets_age_limit
