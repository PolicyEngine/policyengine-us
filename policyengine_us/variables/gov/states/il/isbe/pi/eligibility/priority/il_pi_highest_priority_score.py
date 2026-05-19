from policyengine_us.model_api import *


class il_pi_highest_priority_score(Variable):
    value_type = int
    entity = Person
    label = "Illinois PI highest priority score (50 pts factors)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
    )
    defined_for = "il_pi_demographic_eligible"

    def formula(person, period, parameters):
        household = person.household

        # Highest priority factors (50 pts each):
        # Factor 1: Homeless (McKinney-Vento)
        is_homeless = household("is_homeless", period)
        # Factor 2: Youth in Care (foster care, child welfare)
        is_in_foster_care = person("is_in_foster_care", period)
        # Factor 3: Developmental delay
        has_developmental_delay = person("has_developmental_delay", period)
        # Factor 4: Deep poverty (<=50% FPL) and/or receiving TANF
        is_deep_poverty = person("il_pi_is_deep_poverty", period)
        # Factor 5: Non-English speaking home
        is_non_english_home = household("is_non_english_speaking_home", period)

        highest_priority_factors = [
            is_homeless,
            is_in_foster_care,
            has_developmental_delay,
            is_deep_poverty,
            is_non_english_home,
        ]

        return sum([f.astype(int) for f in highest_priority_factors]) * 50
