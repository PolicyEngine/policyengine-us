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

        # Factor 6: Parent didn't complete high school
        parent_low_education = person(
            "parent_has_less_than_high_school_education", period
        )

        # Factor 7: Teen parent at birth of first child
        was_teen = person("was_teen_parent_at_first_birth", period)
        parent_was_teen = spm_unit.any(was_teen)

        # Factor 8: Child or parent born outside US
        born_outside_us = person("is_born_outside_us", period)
        is_immigrant_family = spm_unit.any(born_outside_us)

        # Factor 9: Non-English speaking home (Household-level variable)
        is_non_english_home = household("is_non_english_speaking_home", period)

        # Factor 10: Active Duty Military family
        is_military = person("is_military", period)
        is_military_family = spm_unit.any(is_military)

        # Factor 11: Developmental delay (without IEP)
        has_developmental_delay = person("has_developmental_delay", period)
        has_iep = person("has_iep", period)
        delay_without_iep = has_developmental_delay & ~has_iep

        # Factor 12: No prior formal early learning
        has_prior_learning = person("has_prior_formal_early_learning", period)
        no_prior_learning = ~has_prior_learning

        factors = [
            is_low_income,
            parent_low_education,
            parent_was_teen,
            is_immigrant_family,
            is_non_english_home,
            is_military_family,
            delay_without_iep,
            no_prior_learning,
        ]

        return sum([f.astype(int) for f in factors])
