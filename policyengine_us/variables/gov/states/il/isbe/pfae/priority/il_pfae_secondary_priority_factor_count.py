from policyengine_us.model_api import *


class il_pfae_secondary_priority_factor_count(Variable):
    value_type = int
    entity = Person
    label = "Number of secondary priority factors for Illinois PFAE"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        household = person.household

        # Factor 5: Income <= 100% FPL
        is_low_income = person("il_pfae_is_low_income", period)

        # Factor 6: Parent didn't complete high school (Household-level variable)
        parent_low_education = household(
            "parent_has_less_than_high_school_education", period
        )

        # Factor 7: Teen parent at birth of first child
        # Parent was under 20 when first child was born
        was_teen_parent = spm_unit(
            "il_isbe_was_teen_parent_at_first_birth", period
        )

        # Factor 8: Child or parent born outside US
        born_outside_us = person("is_born_outside_us", period)
        is_immigrant_family = spm_unit.any(born_outside_us)

        # Factor 9: Non-English speaking home (Household-level variable)
        is_non_english_home = household("is_non_english_speaking_home", period)

        # Factor 10: Active Duty Military family
        is_active_duty_military = person("military_basic_pay", period) > 0
        is_military_family = spm_unit.any(is_active_duty_military)

        # Factor 11: Developmental delay (without IEP)
        has_developmental_delay = person("has_developmental_delay", period)
        has_iep = person("has_individualized_education_program", period)
        delay_without_iep = has_developmental_delay & ~has_iep

        # Factor 12: No prior formal early learning
        no_prior_learning = person(
            "has_no_prior_formal_early_learning", period
        )

        factors = [
            is_low_income,
            parent_low_education,
            was_teen_parent,
            is_immigrant_family,
            is_non_english_home,
            is_military_family,
            delay_without_iep,
            no_prior_learning,
        ]

        return sum([f.astype(int) for f in factors])
