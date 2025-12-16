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
        spm_unit = person.spm_unit

        # Lower priority factors (10 pts each):
        # Factor 33: Teen parent at birth of first child
        was_teen = person("was_teen_parent_at_first_birth", period)
        is_teen_parent_family = spm_unit.any(was_teen)
        # Factor 36: Experiencing poverty (<=200% FPL)
        is_poverty = person("il_pi_is_poverty", period)

        lower_priority_factors = [
            is_teen_parent_family,
            is_poverty,
        ]

        return sum([f.astype(int) for f in lower_priority_factors]) * 10
