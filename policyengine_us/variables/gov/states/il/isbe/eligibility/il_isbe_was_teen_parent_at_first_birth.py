from policyengine_us.model_api import *


class il_isbe_was_teen_parent_at_first_birth(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Parent was a teen at birth of first child"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf"
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        age = person("age", period.this_year)
        is_child = person("is_child", period.this_year)

        # Find oldest child using get_rank (rank 0 = oldest when using -age)
        is_oldest_child = person.get_rank(spm_unit, -age, is_child) == 0

        # Get ages
        head_age = spm_unit.max(age * person("is_tax_unit_head", period))
        oldest_child_age = spm_unit.max(age * is_oldest_child)

        # Calculate parent's age at first birth
        age_at_first_birth = head_age - oldest_child_age

        # Check if parent was under threshold age at birth and has children
        p = parameters(period).gov.states.il.isbe.age_threshold
        has_children = spm_unit.any(is_child)
        return has_children & (age_at_first_birth < p.teen_parent)
