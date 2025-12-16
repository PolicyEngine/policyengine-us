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
        # Secondary priority selection factors (25 points each):
        # 5. Family income at or below 100% FPL
        # 6. Primary caregiver did not complete high school / No GED
        # 7. Teen parent at birth of first child (not modeled)
        # 8. Child/parent born outside US (not modeled)
        # 9. Parent speaks language other than English at home
        # 10. Active Duty Military family
        # 11. Developmental delays (without IEP referral)
        # 12. Child has not previously participated in formal early learning (not modeled)
        # Factor 5: Income <= 100% FPL
        is_low_income = person("il_pfae_is_low_income", period)

        # Factor 6: Parent didn't complete high school
        parent_low_education = person(
            "parent_has_less_than_high_school_education", period
        )

        # Factor 9: Non-English speaking home
        is_non_english_home = person.household(
            "is_non_english_speaking_home", period
        )

        # Factor 10: Active Duty Military family
        # Check if any household member is active military
        is_military_family = person.household("is_military", period).any()

        # Factor 11: Developmental delay (without IEP)
        has_developmental_delay = person("has_developmental_delay", period)
        has_iep = person("has_iep", period)
        # Only count if has delay but no IEP (IEP is a 50-pt factor)
        delay_without_iep = has_developmental_delay & ~has_iep

        factors = [
            is_low_income,
            parent_low_education,
            is_non_english_home,
            is_military_family,
            delay_without_iep,
        ]

        return sum([f.astype(int) for f in factors])
