from policyengine_us.model_api import *


class il_pi_other_priority_score(Variable):
    value_type = int
    entity = Person
    label = "Illinois PI other priority score (25 pts factors)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
    )
    defined_for = "il_pi_demographic_eligible"

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        household = person.household

        # Other priority factors (25 pts each):
        # Factor 6: Low income (<=100% FPL)
        is_low_income = person("il_pi_is_low_income", period)
        # Factor 7: Parent didn't complete high school (Household-level variable)
        parent_low_education = household(
            "parent_has_less_than_high_school_education", period
        )
        # Factor 8: Child/parent born outside US
        born_outside_us = person("is_born_outside_us", period)
        is_immigrant_family = spm_unit.any(born_outside_us)
        # Factor 10: Active Duty Military family
        is_active_duty_military = person("military_basic_pay", period) > 0
        is_military_family = spm_unit.any(is_active_duty_military)
        # Factor 11: Parent is currently age 21 or younger
        is_young_parent_family = spm_unit(
            "il_pi_is_young_parent_family", period
        )
        # Factor 18: Member of household has developmental delay or disability
        has_developmental_delay = spm_unit(
            "il_pi_has_developmental_delay", period
        )
        # Factor 28: Geriatric pregnancy (pregnant woman age 40+)
        has_geriatric_pregnancy = spm_unit(
            "il_pi_has_geriatric_pregnancy", period
        )

        other_priority_factors = [
            is_low_income,
            parent_low_education,
            is_immigrant_family,
            is_military_family,
            is_young_parent_family,
            has_developmental_delay,
            has_geriatric_pregnancy,
        ]

        return sum([f.astype(int) for f in other_priority_factors]) * 25
