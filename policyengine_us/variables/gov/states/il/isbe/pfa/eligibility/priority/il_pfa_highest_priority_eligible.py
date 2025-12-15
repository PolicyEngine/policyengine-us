from policyengine_us.model_api import *


class il_pfa_highest_priority_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child has a highest priority factor for Illinois PFA"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Highest priority factors: homeless, foster care, IEP,
        # deep poverty (<= 50% FPL), non-English home, developmental delay.
        is_homeless = person.household("is_homeless", period)
        is_in_foster_care = person("is_in_foster_care", period)
        has_iep = person("has_iep", period)
        is_deep_poverty = person("il_pfa_is_deep_poverty", period)
        is_non_english_home = person.household(
            "is_non_english_speaking_home", period
        )
        has_developmental_delay = person("has_developmental_delay", period)

        return (
            is_homeless
            | is_in_foster_care
            | has_iep
            | is_deep_poverty
            | is_non_english_home
            | has_developmental_delay
        )
