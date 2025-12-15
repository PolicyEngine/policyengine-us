from policyengine_us.model_api import *


class il_pi_risk_factor_count(Variable):
    value_type = int
    entity = Person
    label = "Number of risk factors for Illinois PI eligibility"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/prevention-initiative-manual.pdf"
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Highest priority factors (each also counts as a risk factor)
        is_homeless = person.household("is_homeless", period)
        is_in_foster_care = person("is_in_foster_care", period)
        is_deep_poverty = person("il_pi_is_deep_poverty", period)
        is_enrolled_ei = person("is_enrolled_in_early_intervention", period)
        has_developmental_delay = person("has_developmental_delay", period)
        is_non_english_home = person.household(
            "is_non_english_speaking_home", period
        )

        # Standard risk factors
        is_low_income = person("il_pi_is_low_income", period)
        receives_benefits = person(
            "il_pi_receives_categorical_benefits", period
        )
        parent_low_education = person(
            "parent_has_less_than_high_school_education", period
        )
        needs_protective_services = person(
            "receives_or_needs_protective_services", period
        )

        factors = [
            is_homeless,
            is_in_foster_care,
            is_deep_poverty,
            is_enrolled_ei,
            has_developmental_delay,
            is_non_english_home,
            is_low_income,
            receives_benefits,
            parent_low_education,
            needs_protective_services,
        ]

        return sum([f.astype(int) for f in factors])
