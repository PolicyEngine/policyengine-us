from policyengine_us.model_api import *


class il_pi_is_young_parent_family(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Young parent family for Illinois PI (Factor 11)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # Factor 11 (25 pts): Parent is currently age 21 years or younger.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.age_threshold
        age = spm_unit.members("age", period)
        is_parent = spm_unit.members("is_parent", period)
        is_young = age <= p.young_parent
        # Eligible if any parent is 21 or younger.
        return spm_unit.any(is_parent & is_young)
