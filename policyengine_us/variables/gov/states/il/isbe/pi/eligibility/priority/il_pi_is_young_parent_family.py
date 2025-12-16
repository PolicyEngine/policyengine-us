from policyengine_us.model_api import *


class il_pi_is_young_parent_family(Variable):
    value_type = bool
    entity = Person
    label = "Young parent family for Illinois PI (Factor 11, 25 points)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Factor 11 (25 pts): Parent is currently age 21 years or younger.
        # All parents in the family must be age 21 or younger.
        age = person("age", period)
        is_parent = person("is_parent", period)
        is_young_parent = is_parent & (age <= 21)
        is_old_parent = is_parent & (age > 21)
        spm_unit = person.spm_unit
        has_young_parent = spm_unit.any(is_young_parent)
        has_old_parent = spm_unit.any(is_old_parent)
        # Only eligible if there's at least one young parent and no old parents.
        return has_young_parent & ~has_old_parent
