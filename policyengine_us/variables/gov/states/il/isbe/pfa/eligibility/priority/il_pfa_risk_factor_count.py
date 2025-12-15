from policyengine_us.model_api import *


class il_pfa_risk_factor_count(Variable):
    value_type = int
    entity = Person
    label = "Number of risk factors for Illinois PFA eligibility"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Highest priority factors (each also counts as a risk factor)
        is_homeless = person.household("is_homeless", period)
        is_in_foster_care = person("is_in_foster_care", period)
        has_iep = person("has_iep", period)
        is_deep_poverty = person("il_pfa_is_deep_poverty", period)
        is_non_english_home = person.household(
            "is_non_english_speaking_home", period
        )
        has_developmental_delay = person("has_developmental_delay", period)

        # Standard risk factors
        is_low_income = person("il_pfa_is_low_income", period)
        receives_benefits = person(
            "il_pfa_receives_categorical_benefits", period
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
            has_iep,
            is_deep_poverty,
            is_non_english_home,
            has_developmental_delay,
            is_low_income,
            receives_benefits,
            parent_low_education,
            needs_protective_services,
        ]

        return sum([f.astype(int) for f in factors])
