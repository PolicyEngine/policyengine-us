from policyengine_us.model_api import *


class il_pi_highest_priority(Variable):
    value_type = bool
    entity = Person
    label = "Has a highest priority factor for Illinois PI"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/prevention-initiative-manual.pdf"
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Highest priority factors: foster care, homeless, deep poverty,
        # Early Intervention, developmental delay, non-English home.
        is_homeless = person.household("is_homeless", period)
        is_in_foster_care = person("is_in_foster_care", period)
        is_deep_poverty = person("il_pi_is_deep_poverty", period)
        is_enrolled_ei = person("is_enrolled_in_early_intervention", period)
        has_developmental_delay = person("has_developmental_delay", period)
        is_non_english_home = person.household(
            "is_non_english_speaking_home", period
        )

        return (
            is_homeless
            | is_in_foster_care
            | is_deep_poverty
            | is_enrolled_ei
            | has_developmental_delay
            | is_non_english_home
        )
