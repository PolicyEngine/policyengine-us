from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_tier import (
    SchoolMealTier,
)


class school_meal_breakfast_tier(Variable):
    value_type = Enum
    label = "School breakfast tier"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "School meal tier for breakfast. It starts from school_meal_tier, the "
        "tier for both meals, and gives the FREE tier to all students in "
        "states with universal free breakfast and to reduced-price students "
        "in states that cover only the reduced-price breakfast copay."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1773#e_1_A",
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/HTML/2011-2012/SL2011-342.html",
        "https://gc.nh.gov/rsa/html/XV/189/189-11-a.htm",
        "https://mgaleg.maryland.gov/2026RS/Statute_Web/ged/7-602.pdf#page=2",
        # PDF pages 1005-1006
        "https://www.lbb.texas.gov/Documents/GAA/General_Appropriations_Act_2024_2025.pdf#page=1005",
        "https://lawfilesext.leg.wa.gov/biennium/2021-22/Pdf/Bills/Session%20Laws/Senate/5092-S.SL.pdf#page=997",
    )

    def formula(spm_unit, period, parameters):
        # The tier for both meals already includes state coverage of both
        # meals, so only breakfast-specific state policies apply here.
        tier = spm_unit("school_meal_tier", period)
        universal_free_breakfast = spm_unit(
            "state_has_universal_free_school_breakfast", period
        )
        state = spm_unit.household("state_code_str", period)
        p = parameters(period).gov.usda.school_meals
        state_covers_reduced_copay = p.state_covers_reduced_price_copay_breakfast_only[
            state
        ].astype(bool)
        reduced = tier == tier.possible_values.REDUCED
        return select(
            [
                (tier == tier.possible_values.FREE)
                | universal_free_breakfast
                | (reduced & state_covers_reduced_copay),
                reduced,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED],
            default=SchoolMealTier.PAID,
        )
