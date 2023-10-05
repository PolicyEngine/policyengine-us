from policyengine_us.model_api import *


class ca_child_care_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Child Care Age Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.eligibility
        persons = spm_unit.members
        is_child = persons("is_child", period)
        age = persons("age", period)
        is_disabled = persons("is_disabled", period)
        child_disabled_under_18 = (
            (is_child) & (age <= p.disabled_age_threshold) & (is_disabled)
        )
        child_under_13 = (is_child) & (age <= p.age_threshold)

        return spm_unit.any(child_under_13 | child_disabled_under_18)
