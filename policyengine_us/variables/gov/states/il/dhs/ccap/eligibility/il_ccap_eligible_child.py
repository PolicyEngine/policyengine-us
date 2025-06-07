from policyengine_us.model_api import *


class il_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Illinois Child Care Assistance Program (CCAP)"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=104995"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.age_limit
        age = person("monthly_age", period)
        is_disabled = person("is_disabled", period)
        age_limit = where(is_disabled, p.special_needs_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_status_eligible = person(
            "il_ccap_immigration_status_eligible_person", period
        )

        return age_eligible & is_dependent & immigration_status_eligible
