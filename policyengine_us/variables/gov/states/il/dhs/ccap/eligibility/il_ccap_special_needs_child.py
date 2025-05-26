from policyengine_us.model_api import *


class il_ccap_special_needs_child(Variable):
    value_type = bool
    entity = Person
    label = (
        "Special needs child for Illinois Child Care Assistance Program (CCAP)"
    )
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=104995"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.age_threshold
        age = person("monthly_age", period)
        # There a section for the disability requirement
        is_disabled = person("is_disabled", period)
        is_child = age < p.special_needs_child
        return is_child & is_disabled
