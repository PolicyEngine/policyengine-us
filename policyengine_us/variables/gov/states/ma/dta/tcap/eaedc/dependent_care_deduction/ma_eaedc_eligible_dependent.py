from policyengine_us.model_api import *


class ma_eaedc_eligible_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Eligible dependent for the Massachusetts EAEDC dependent care deduction"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-200"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.age_threshold
        dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)
        age_eligible = age < p.dependent
        is_related_to_head_or_spouse = person(
            "is_tafdc_related_to_head_or_spouse", period
        )
        return dependent & age_eligible & ~is_related_to_head_or_spouse
