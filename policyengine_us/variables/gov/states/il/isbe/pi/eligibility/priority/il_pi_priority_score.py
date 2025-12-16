from policyengine_us.model_api import *


class il_pi_priority_score(Variable):
    value_type = int
    entity = Person
    label = "Weighted priority score for Illinois PI eligibility"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=3",
    )
    defined_for = "il_pi_demographic_eligible"

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        household = person.household

        # Highest priority factors (50 pts each)
        # Factor 1: Homeless
        is_homeless = household("is_homeless", period)
        # Factor 2: Foster care
        is_in_foster_care = person("is_in_foster_care", period)
        # Factor 3: Early Intervention or developmental delay
        is_enrolled_ei = person("is_enrolled_in_early_intervention", period)
        has_developmental_delay = person("has_developmental_delay", period)
        # Factor 4: Deep poverty (≤50% FPL)
        is_deep_poverty = person("il_pi_is_deep_poverty", period)
        # Factor 5: Non-English speaking home
        is_non_english_home = household("is_non_english_speaking_home", period)

        highest_priority = [
            is_homeless,
            is_in_foster_care,
            is_enrolled_ei,
            has_developmental_delay,
            is_deep_poverty,
            is_non_english_home,
        ]

        # Other priority factors (25 pts each)
        # Factor 6: Low income (≤100% FPL)
        is_low_income = person("il_pi_is_low_income", period)
        # Factor 7: Parent didn't complete high school
        parent_low_education = person(
            "parent_has_less_than_high_school_education", period
        )
        # Factor 8: Child/parent born outside US
        born_outside_us = person("is_born_outside_us", period)
        is_immigrant_family = spm_unit.any(born_outside_us)
        # Factor 10: Active Duty Military family
        is_military = person("is_military", period)
        is_military_family = spm_unit.any(is_military)
        # Factor 11: Parent is currently age 21 or younger
        is_young_parent_family = person("il_pi_is_young_parent_family", period)
        # Factor 13: History of abuse/neglect (protective services)
        needs_protective_services = person(
            "receives_or_needs_protective_services", period
        )
        # Categorical benefits (income verification proxy)
        receives_benefits = person(
            "il_pi_receives_categorical_benefits", period
        )

        other_priority = [
            is_low_income,
            parent_low_education,
            is_immigrant_family,
            is_military_family,
            is_young_parent_family,
            needs_protective_services,
            receives_benefits,
        ]

        # Lower priority factors (10 pts each)
        # Factor 33: Teen parent at birth of first child
        was_teen = person("was_teen_parent_at_first_birth", period)
        is_teen_parent_family = spm_unit.any(was_teen)
        # Factor 36: Experiencing poverty (≤200% FPL)
        is_poverty = person("il_pi_is_poverty", period)

        lower_priority = [
            is_teen_parent_family,
            is_poverty,
        ]

        # Calculate weighted score
        highest_score = sum([f.astype(int) for f in highest_priority]) * 50
        other_score = sum([f.astype(int) for f in other_priority]) * 25
        lower_score = sum([f.astype(int) for f in lower_priority]) * 10

        return highest_score + other_score + lower_score
