from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_tier import (
    SchoolMealTier,
)


class school_meal_lunch_tier(Variable):
    value_type = Enum
    label = "School lunch tier"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "School meal tier for lunch. It starts from school_meal_tier, the tier "
        "for both meals, and gives the FREE tier to reduced-price students in "
        "states that cover only the reduced-price lunch copay."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1758#b_1_A",
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://le.utah.gov/xcode/Title53F/Chapter2/C53F-2-S423_2025070120250507.html",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=28A.235.160",
    )

    def formula(spm_unit, period, parameters):
        # The tier for both meals already includes state coverage of both
        # meals, so only lunch-specific state policies apply here.
        tier = spm_unit("school_meal_tier", period)
        state = spm_unit.household("state_code_str", period)
        p = parameters(period).gov.usda.school_meals
        state_covers_reduced_copay = p.state_covers_reduced_price_copay_lunch_only[
            state
        ].astype(bool)
        reduced = tier == tier.possible_values.REDUCED
        return select(
            [
                (tier == tier.possible_values.FREE)
                | (reduced & state_covers_reduced_copay),
                reduced,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED],
            default=SchoolMealTier.PAID,
        )
