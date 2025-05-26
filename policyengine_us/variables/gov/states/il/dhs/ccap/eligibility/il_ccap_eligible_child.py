from policyengine_us.model_api import *


class il_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Illinois Child Care Assistance Program (CCAP)"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=104995"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.age_threshold
        age = person("monthly_age", period)
        is_child = age < p.child
        is_dependent = person("is_tax_unit_dependent", period)
        is_special_needs_child = person("il_ccap_special_needs_child", period)
        immigration_status_eligible = person(
            "il_ccap_immigration_status_eligible_person", period
        )
        eligible_child = is_child | is_special_needs_child
        return immigration_status_eligible & eligible_child & is_dependent
