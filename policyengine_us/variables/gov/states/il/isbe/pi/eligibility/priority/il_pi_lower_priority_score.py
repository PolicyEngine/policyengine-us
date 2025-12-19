from policyengine_us.model_api import *


class il_pi_lower_priority_score(Variable):
    value_type = int
    entity = Person
    label = "Illinois PI lower priority score (10 pts factors)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=3",
    )
    defined_for = "il_pi_demographic_eligible"

    def formula(person, period, parameters):
        household = person.household
        spm_unit = person.spm_unit

        # Lower priority factors (10 pts each):
        # Factor 33: Teen parent at birth of first child (SPMUnit-level variable)
        # Parent was under 20 when first child was born
        is_teen_parent_family = spm_unit(
            "il_isbe_was_teen_parent_at_first_birth", period
        )
        # Factor 35: Parent/Caregiver is single parent
        is_parent = spm_unit.members("is_tax_unit_head_or_spouse", period)
        is_single_parent = spm_unit.sum(is_parent) == 1
        # Factor 36: Experiencing poverty (<=200% FPL)
        is_poverty = person("il_pi_is_poverty", period)

        lower_priority_factors = [
            is_teen_parent_family,
            is_single_parent,
            is_poverty,
        ]

        return sum([f.astype(int) for f in lower_priority_factors]) * 10
